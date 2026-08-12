#!/usr/bin/env python3
"""Source-only release, deployment, rollback, and issue collection tools."""

from __future__ import annotations

import argparse
import datetime as dt
import errno
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RUNTIME_SOURCE = ROOT / ".mpa-workspace"
RUNTIME_DIST = ROOT / "dist" / ".mpa-workspace"
WORKSPACE = ROOT / "workspace"
MANIFESTS = WORKSPACE / "releases" / "manifests"
PACKAGES = WORKSPACE / "releases" / "packages"
RELEASE_RECEIPTS = WORKSPACE / "receipts" / "releases"
DEPLOYMENT_RECEIPTS = WORKSPACE / "receipts" / "deployments"
ISSUE_RECEIPTS = WORKSPACE / "receipts" / "issues"
ISSUES = WORKSPACE / "issues"
SAFE_REF = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
SECRET = re.compile(r"(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*\S+")
ABSOLUTE_PATH = re.compile(r"(?<![\w.-])/(?:Users|home|var|private|tmp|etc)/")
IGNORED_RUNTIME_NAMES = {"__pycache__", ".DS_Store", "history"}
RELEASE_METADATA = ("compatibility", "breaking_change", "migration", "rollback_condition", "release_note")
RELEASE_SCHEMA_VERSION = 3
VALIDATION_TIMEOUT_SECONDS = 120
DOCS_INDEX_TEMPLATE = "# 문서 색인\n\n> 이 파일은 agent가 문서 산출물의 위치와 요약을 관리합니다. 일반 문서 내용은 프로젝트 사용자가 소유합니다.\n\n"


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def receipt_suffix() -> str:
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{stamp}-{uuid.uuid4().hex[:8]}"


def relative_to_root(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT.resolve()))


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def assert_safe_runtime_tree(root: Path) -> None:
    if not root.is_dir():
        raise ValueError(f"Runtime directory is missing: {root}")
    for path in root.rglob("*"):
        if path.name in IGNORED_RUNTIME_NAMES:
            continue
        if path.is_symlink():
            raise ValueError(f"Runtime must not contain symlinks: {path}")
        if not path.is_dir() and not path.is_file():
            raise ValueError(f"Runtime contains an unsupported file type: {path}")


def asset_map(root: Path) -> dict[str, str]:
    assert_safe_runtime_tree(root)
    return {
        path.relative_to(root).as_posix(): sha(path)
        for path in sorted(root.rglob("*"))
        if path.is_file() and not any(part in IGNORED_RUNTIME_NAMES for part in path.relative_to(root).parts)
    }


def runtime_ignore(_: str, names: list[str]) -> set[str]:
    return {name for name in names if name in IGNORED_RUNTIME_NAMES}


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def replace_tree(source: Path, destination: Path) -> None:
    """Copy a validated tree to a sibling staging path and replace destination safely."""
    assert_safe_runtime_tree(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    token = uuid.uuid4().hex[:8]
    staging = destination.with_name(f".{destination.name}.new-{token}")
    previous = destination.with_name(f".{destination.name}.previous-{token}")
    try:
        shutil.copytree(source, staging, ignore=runtime_ignore)
        if destination.exists():
            destination.replace(previous)
        try:
            staging.replace(destination)
        except Exception:
            if previous.exists() and not destination.exists():
                previous.replace(destination)
            raise
        if previous.exists():
            shutil.rmtree(previous)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
        if previous.exists() and destination.exists():
            shutil.rmtree(previous)


def scoped_git() -> dict:
    paths = [".mpa-workspace", "dist/.mpa-workspace", "release_manager.py", "install.py"]
    try:
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True,
                              capture_output=True, check=True).stdout.strip()
        diff = subprocess.run(["git", "diff", "--name-status", "--", *paths], cwd=ROOT,
                              text=True, capture_output=True, check=True).stdout.splitlines()
        return {"status": "available", "head": head, "scoped_diff": diff}
    except (OSError, subprocess.CalledProcessError):
        return {"status": "unavailable"}


def runtime_version(root: Path) -> str:
    version_file = root / ".mpa-version"
    if not version_file.is_file():
        raise ValueError("Runtime .mpa-version is missing")
    match = re.search(r"^current_version:\s*(.+?)\s*$", version_file.read_text(encoding="utf-8"), re.MULTILINE)
    if not match:
        raise ValueError("Runtime current_version is missing")
    return match.group(1)


def release_id(version: str, assets: dict[str, str]) -> str:
    payload = json.dumps(assets, sort_keys=True, separators=(",", ":")).encode()
    version_tag = re.sub(r"[^a-zA-Z0-9]+", "-", version).strip("-").lower()
    return f"mpa-{version_tag}-{hashlib.sha256(payload).hexdigest()[:12]}"


def migrate_legacy_active_releases() -> None:
    """Keep old hash-only artifacts out of the active versioned release inventory."""
    legacy_root = WORKSPACE / "releases" / "legacy" / "migrated" / dt.datetime.now().strftime("%Y%m%d")
    legacy_receipts = WORKSPACE / "receipts" / "legacy" / "migrations" / dt.datetime.now().strftime("%Y%m%d")
    legacy_ids = set()
    for path in MANIFESTS.glob("*.json") if MANIFESTS.exists() else []:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {}
        if data.get("schema_version") != RELEASE_SCHEMA_VERSION:
            legacy_ids.add(path.stem)
            legacy_root.mkdir(parents=True, exist_ok=True)
            path.replace(legacy_root / path.name)
    for ident in legacy_ids:
        package = PACKAGES / ident
        if package.exists():
            legacy_root.mkdir(parents=True, exist_ok=True)
            package.replace(legacy_root / package.name)
    for path in RELEASE_RECEIPTS.glob("*.json") if RELEASE_RECEIPTS.exists() else []:
        try:
            if json.loads(path.read_text(encoding="utf-8")).get("release_id") in legacy_ids:
                legacy_receipts.mkdir(parents=True, exist_ok=True)
                path.replace(legacy_receipts / path.name)
        except json.JSONDecodeError:
            continue


def require_safe_ref(value: str, field: str) -> str:
    if not SAFE_REF.fullmatch(value):
        raise ValueError(f"{field} must be lowercase safe text")
    return value


def sync_runtime(_: argparse.Namespace) -> None:
    replace_tree(RUNTIME_SOURCE, RUNTIME_DIST)
    print(f"synced runtime: {RUNTIME_SOURCE} -> {RUNTIME_DIST}")


def run_validation(command: list[str]) -> dict:
    if not isinstance(command, list) or not command or not all(isinstance(arg, str) and arg for arg in command):
        raise ValueError("validation-command is required")
    try:
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True,
                                timeout=VALIDATION_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired as error:
        raise ValueError(f"validation command timed out after {VALIDATION_TIMEOUT_SECONDS}s") from error
    record = {"command": command, "exit_code": result.returncode,
              "stdout": result.stdout[-4000:], "stderr": result.stderr[-4000:], "executed_at": now()}
    if result.returncode:
        raise ValueError(f"validation command failed: {record}")
    return record


def prepare_release(args: argparse.Namespace) -> None:
    if isinstance(args.validation_command, list):  # direct API use in tests/integrations
        validation_command = args.validation_command
    else:
        try:
            validation_command = json.loads(args.validation_command)
        except (TypeError, json.JSONDecodeError) as error:
            raise ValueError("validation-command must be an argv JSON array") from error
    migrate_legacy_active_releases()
    validation = run_validation(validation_command)
    metadata = {field: getattr(args, field) for field in RELEASE_METADATA}
    if any(not value.strip() for value in metadata.values()):
        raise ValueError("release metadata fields must not be empty")
    assets = asset_map(RUNTIME_DIST)
    version = runtime_version(RUNTIME_DIST)
    ident = release_id(version, assets)
    for existing_path in MANIFESTS.glob("*.json") if MANIFESTS.exists() else []:
        existing = json.loads(existing_path.read_text(encoding="utf-8"))
        if existing.get("runtime_version") == version and existing.get("assets") != assets:
            raise ValueError("runtime_version already has a different immutable package")
    manifest_path = MANIFESTS / f"{ident}.json"
    package_path = PACKAGES / ident
    if manifest_path.exists() != package_path.exists():
        raise ValueError("release manifest and package must either both exist or both be absent")
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("assets") != assets or asset_map(package_path) != assets:
            raise ValueError("existing release ID does not match its immutable package")
        write_json(RELEASE_RECEIPTS / f"{ident}-{receipt_suffix()}.json", {
            "schema_version": RELEASE_SCHEMA_VERSION, "release_id": ident, "runtime_version": version,
            "manifest": relative_to_root(manifest_path), "created_at": now(),
            "verified_by": args.verified_by, "validation": validation,
        })
    else:
        package_path.parent.mkdir(parents=True, exist_ok=True)
        staging = package_path.with_name(f".{package_path.name}.new-{uuid.uuid4().hex[:8]}")
        receipt_path = RELEASE_RECEIPTS / f"{ident}-{receipt_suffix()}.json"
        try:
            shutil.copytree(RUNTIME_DIST, staging, ignore=runtime_ignore)
            if asset_map(staging) != assets:
                raise ValueError("release package asset map changed while preparing")
            staging.replace(package_path)
            receipt = {
                "schema_version": RELEASE_SCHEMA_VERSION,
                "release_id": ident, "runtime_version": version,
                "manifest": relative_to_root(manifest_path),
                "created_at": now(),
                "verified_by": args.verified_by,
                "validation": validation,
            }
            write_json(receipt_path, receipt)
            manifest = {
                "schema_version": RELEASE_SCHEMA_VERSION,
                "release_id": ident, "runtime_version": version,
                "created_at": now(),
                "asset_root": "dist/.mpa-workspace",
                "package": relative_to_root(package_path),
                "assets": assets,
                "asset_checksum": hashlib.sha256(json.dumps(assets, sort_keys=True).encode()).hexdigest(),
                "source_snapshot": {"allowlist": sorted(assets), "asset_checksum": hashlib.sha256(json.dumps(assets, sort_keys=True).encode()).hexdigest(), "validation": validation, "metadata": metadata},
                "source_git": scoped_git(),
                "metadata": metadata,
                "validation": validation,
                "release_receipt": relative_to_root(receipt_path),
            }
            write_json(manifest_path, manifest)
        except Exception:
            if receipt_path.exists():
                receipt_path.unlink()
            if package_path.exists():
                shutil.rmtree(package_path)
            raise
        finally:
            if staging.exists():
                shutil.rmtree(staging)
    print(ident)


def load_manifest(value: str) -> tuple[Path, dict]:
    path = Path(value)
    if not path.is_absolute():
        path = ROOT / path
    path = path.resolve()
    if MANIFESTS.resolve() not in path.parents:
        raise ValueError("manifest must be inside workspace/releases/manifests")
    data = json.loads(path.read_text(encoding="utf-8"))
    if (data.get("schema_version") != RELEASE_SCHEMA_VERSION or not data.get("release_id") or
            not data.get("runtime_version") or not isinstance(data.get("assets"), dict)):
        raise ValueError("invalid release manifest")
    if data.get("package") != relative_to_root(PACKAGES / data["release_id"]):
        raise ValueError("manifest package path is invalid")
    if not isinstance(data.get("metadata"), dict) or any(not data["metadata"].get(field) for field in RELEASE_METADATA):
        raise ValueError("manifest release metadata is incomplete")
    if not isinstance(data.get("validation"), dict) or data["validation"].get("exit_code") != 0:
        raise ValueError("manifest validation result is invalid")
    receipt = (ROOT / data.get("release_receipt", "")).resolve()
    if RELEASE_RECEIPTS.resolve() not in receipt.parents or not receipt.is_file():
        raise ValueError("manifest release receipt is missing")
    receipt_data = json.loads(receipt.read_text(encoding="utf-8"))
    if (receipt_data.get("schema_version") != RELEASE_SCHEMA_VERSION or
            receipt_data.get("release_id") != data["release_id"] or receipt_data.get("runtime_version") != data["runtime_version"] or
            receipt_data.get("manifest") != relative_to_root(path) or
            receipt_data.get("validation") != data["validation"]):
        raise ValueError("manifest release receipt does not match")
    return path, data


def release_package(manifest: dict) -> Path:
    package = (PACKAGES / manifest["release_id"]).resolve()
    if PACKAGES.resolve() not in package.parents or not package.is_dir():
        raise ValueError("immutable release package is missing")
    if asset_map(package) != manifest["assets"]:
        raise ValueError("immutable release package does not match manifest")
    return package


def audit_releases(_: argparse.Namespace) -> None:
    invalid = []
    manifests = {path.stem for path in MANIFESTS.glob("*.json")}
    packages = {path.name for path in PACKAGES.iterdir() if path.is_dir()} if PACKAGES.exists() else set()
    receipt_ids = set()
    for path in RELEASE_RECEIPTS.glob("*.json") if RELEASE_RECEIPTS.exists() else []:
        try:
            receipt_ids.add(json.loads(path.read_text(encoding="utf-8")).get("release_id"))
        except json.JSONDecodeError:
            invalid.append(f"{path.name}: invalid release receipt JSON")
    if manifests != packages:
        invalid.append("active manifest/package inventory does not match")
    if any(release not in manifests for release in receipt_ids if release):
        invalid.append("active release receipt has no manifest")
    for manifest_path in sorted(MANIFESTS.glob("*.json")):
        try:
            _, manifest = load_manifest(str(manifest_path))
            release_package(manifest)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            invalid.append(f"{manifest_path.name}: {error}")
    if invalid:
        raise ValueError("invalid release artifacts: " + "; ".join(invalid))
    print(f"release audit passed: {len(manifests)} manifest(s)")


def verify_target(target: Path, expected: dict[str, str]) -> None:
    if asset_map(target) != expected:
        raise ValueError("target runtime asset map does not match release manifest")


def ensure_required_project_directories(root: Path) -> list[str]:
    """Create only missing empty user-owned roots required by install/update rules."""
    created = []
    for name in ("workspace", "workspace/issues", "docs"):
        path = root / name
        if not path.exists():
            path.mkdir(parents=True)
            created.append(name + "/")
        elif not path.is_dir():
            raise ValueError(f"required project path is not a directory: {name}")
    docs_index = root / "docs" / "INDEX.md"
    if not docs_index.exists():
        docs_index.write_text(DOCS_INDEX_TEMPLATE, encoding="utf-8")
        created.append("docs/INDEX.md")
    return created


def update_issue_inventory(root: Path) -> list[dict[str, str]]:
    folder = root / "workspace" / "issues"
    if not folder.is_dir():
        return []
    return [{"path": path.name, "checksum": sha(path)} for path in sorted(folder.glob("*.md"))]


def collect_update_issues(root: Path, project_ref: str, expected: list[dict[str, str]]) -> list[str]:
    """Collect a verified update batch; restore every source if its receipt cannot be written."""
    if update_issue_inventory(root) != expected:
        raise ValueError("project issues changed after dry-run")
    project_issues = root / "workspace" / "issues"
    destinations: list[tuple[Path, Path]] = []
    for item in expected:
        source = project_issues / item["path"]
        text = source.read_text(encoding="utf-8")
        check_issue_text(text)
        read_issue(source)
        destination = ISSUES / "inbox" / project_ref / source.name
        archived = list((ISSUES / "archived").rglob(source.name)) if (ISSUES / "archived").exists() else []
        if destination.exists() or archived:
            raise ValueError("update issue already exists in inbox or archive")
        destinations.append((source, destination))
    moved: list[tuple[Path, Path]] = []
    try:
        for source, destination in destinations:
            destination.parent.mkdir(parents=True, exist_ok=True)
            move_issue_atomically(source, destination)
            moved.append((source, destination))
        receipt_path = ISSUE_RECEIPTS / "update-collections" / f"{receipt_suffix()}.json"
        write_json(receipt_path, {"project": str(root), "project_ref": project_ref,
                                  "issues": [str(destination.relative_to(ROOT)) for _, destination in moved], "at": now()})
    except Exception:
        for source, destination in reversed(moved):
            if destination.exists() and not source.exists():
                move_issue_atomically(destination, source)
        raise
    return [str(destination.relative_to(ROOT)) for _, destination in moved]


def deployment_dry_run(args: argparse.Namespace) -> None:
    target_ref = require_safe_ref(args.target_ref, "target-ref")
    manifest_path, manifest = load_manifest(args.manifest)
    release_package(manifest)
    root = Path(args.target).resolve()
    target = root / ".mpa-workspace"
    if not target.is_dir():
        raise ValueError("target .mpa-workspace is missing; use install.py for first installation")
    created_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    result = {"release_id": manifest["release_id"], "runtime_version": manifest["runtime_version"],
              "from_version": runtime_version(target), "to_version": manifest["runtime_version"], "manifest": relative_to_root(manifest_path),
              "release_receipt": manifest["release_receipt"],
              "target": str(root), "target_ref": target_ref, "current_assets": asset_map(target),
              "release_assets": manifest["assets"], "history": target_history(target), "issue_inventory": update_issue_inventory(root),
              "created_at": created_at.isoformat(),
              "expires_at": (created_at + dt.timedelta(minutes=30)).isoformat()}
    path = DEPLOYMENT_RECEIPTS / target_ref / f"dry-run-{manifest['release_id']}-{receipt_suffix()}.json"
    write_json(path, result)
    print(relative_to_root(path))


def deploy(args: argparse.Namespace) -> None:
    target_ref = require_safe_ref(args.target_ref, "target-ref")
    manifest_path, manifest = load_manifest(args.manifest)
    package = release_package(manifest)
    root = Path(args.target).resolve()
    target = root / ".mpa-workspace"
    if not target.is_dir():
        raise ValueError("target .mpa-workspace is missing; use install.py for first installation")
    ensure_required_project_directories(root)
    dry_run = (ROOT / args.dry_run).resolve()
    if DEPLOYMENT_RECEIPTS.resolve() not in dry_run.parents or not dry_run.is_file():
        raise ValueError("deploy requires a recorded deployment dry-run")
    dry_run_data = json.loads(dry_run.read_text(encoding="utf-8"))
    if (dry_run_data.get("release_id") != manifest["release_id"] or dry_run_data.get("to_version") != manifest["runtime_version"] or
            dry_run_data.get("target") != str(root) or dry_run_data.get("target_ref") != target_ref):
        raise ValueError("dry-run does not match deployment inputs")
    if dry_run_data.get("release_receipt") != manifest.get("release_receipt"):
        raise ValueError("dry-run release receipt does not match manifest")
    try:
        expires_at = dt.datetime.fromisoformat(dry_run_data["expires_at"])
    except (KeyError, ValueError) as error:
        raise ValueError("dry-run expiry is invalid") from error
    if dt.datetime.now(dt.timezone.utc) > expires_at:
        raise ValueError("dry-run has expired")
    if (dry_run_data.get("current_assets") != asset_map(target) or dry_run_data.get("history") != target_history(target) or
            dry_run_data.get("from_version") != runtime_version(target)):
        raise ValueError("target changed after dry-run")
    if dry_run_data.get("issue_inventory") != update_issue_inventory(root):
        raise ValueError("project issues changed after dry-run")
    if not all(str(getattr(args, field, "")).strip() for field in ("approved_by", "approval_ref", "rollback_owner")):
        raise ValueError("approved-by, approval-ref, and rollback-owner are required")
    if target_history(target).get(manifest["release_id"], {}).get("status") == "applied":
        raise ValueError("target history already contains this release ID")
    if any(record.get("to_version") == manifest["runtime_version"] for record in target_history(target).values()):
        raise ValueError("target history already contains this runtime_version")
    from_version = runtime_version(target)
    backup = root / ".mpa-backups" / f"{manifest['release_id']}-{receipt_suffix()}"
    replacement = None
    previous = None
    try:
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(target, backup)
        replacement = target.with_name(f".mpa-workspace.new-{uuid.uuid4().hex[:8]}")
        previous = target.with_name(f".mpa-workspace.previous-{uuid.uuid4().hex[:8]}")
        try:
            shutil.copytree(package, replacement, ignore=runtime_ignore)
            history = target / "history"
            if history.exists():
                shutil.copytree(history, replacement / "history")
            verify_target(replacement, manifest["assets"])
            target.replace(previous)
            try:
                replacement.replace(target)
                verify_target(target, manifest["assets"])
            except Exception:
                if target.exists():
                    shutil.rmtree(target)
                if previous.exists():
                    previous.replace(target)
                raise
        finally:
            if replacement and replacement.exists():
                shutil.rmtree(replacement)
        collected = collect_update_issues(root, target_ref, dry_run_data["issue_inventory"])
        receipt = {
            "status": "applied", "release_id": manifest["release_id"],
            "from_version": from_version, "to_version": manifest["runtime_version"],
            "manifest": relative_to_root(manifest_path), "target": str(root),
            "backup": str(backup.relative_to(root)), "applied_at": now(), "verified_by": args.verified_by,
            "approved_by": args.approved_by, "approval_ref": args.approval_ref,
            "rollback_owner": args.rollback_owner, "dry_run": relative_to_root(dry_run),
            "assets": manifest["assets"], "verification": {"asset_map": "matched", "verified_at": now()},
            "collected_issues": collected,
        }
        write_json(DEPLOYMENT_RECEIPTS / target_ref / f"deploy-{manifest['release_id']}-{receipt_suffix()}.json", receipt)
        write_json(target / "history" / "releases" / f"{manifest['release_id']}.json", receipt)
        if previous and previous.exists():
            shutil.rmtree(previous)
    except Exception as error:
        if previous and previous.exists():
            if target.exists():
                shutil.rmtree(target)
            previous.replace(target)
        failure = {"status": "failed", "release_id": manifest["release_id"], "manifest": relative_to_root(manifest_path),
                   "target": str(root), "backup": str(backup.relative_to(root)) if backup.exists() else None,
                   "failed_at": now(), "error": str(error), "dry_run": relative_to_root(dry_run)}
        write_json(DEPLOYMENT_RECEIPTS / target_ref / f"deploy-failed-{manifest['release_id']}-{receipt_suffix()}.json", failure)
        if target.is_dir():
            write_json(target / "history" / "releases" / f"{manifest['release_id']}.json", failure)
        raise
    print(receipt["backup"])


def target_history(target: Path) -> dict[str, dict]:
    """Read deployment history before applying; malformed history is a hard stop."""
    folder = target / "history" / "releases"
    if not folder.exists():
        return {}
    result = {}
    for path in sorted(folder.glob("*.json")):
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            raise ValueError(f"target history is invalid: {path.name}") from error
        release = value.get("release_id")
        if not release or release in result:
            raise ValueError("target history has an invalid or duplicate release ID")
        result[release] = value
    return result


def rollback(args: argparse.Namespace) -> None:
    target_ref = require_safe_ref(args.target_ref, "target-ref")
    root = Path(args.target).resolve()
    ensure_required_project_directories(root)
    previous = None
    target = root / ".mpa-workspace"
    try:
        backups_root = (root / ".mpa-backups").resolve()
        backup = (root / args.backup).resolve()
        if backups_root not in backup.parents or not backup.is_dir():
            raise ValueError("backup must be inside target .mpa-backups")
        if not target.is_dir():
            raise ValueError("target .mpa-workspace is missing")
        release_id = require_safe_ref(args.release_id, "release-id")
        if release_id not in target_history(target):
            raise ValueError("target history does not contain the release to roll back")
        replacement = target.with_name(f".mpa-workspace.rollback-{uuid.uuid4().hex[:8]}")
        previous = target.with_name(f".mpa-workspace.rollback-previous-{uuid.uuid4().hex[:8]}")
        try:
            shutil.copytree(backup, replacement)
            target.replace(previous)
            try:
                replacement.replace(target)
            except Exception:
                if previous.exists() and not target.exists():
                    previous.replace(target)
                raise
        finally:
            if replacement.exists():
                shutil.rmtree(replacement)
    except Exception as error:
        if previous and previous.exists():
            if target.exists():
                shutil.rmtree(target)
            previous.replace(target)
        write_json(DEPLOYMENT_RECEIPTS / target_ref / f"rollback-failed-{receipt_suffix()}.json",
                   {"target": str(root), "backup": args.backup, "failed_at": now(), "error": str(error)})
        raise
    try:
        receipt = {"status": "rolled_back", "release_id": release_id, "target": str(root),
                   "from_version": runtime_version(previous), "to_version": runtime_version(root / ".mpa-workspace"),
                   "backup": str(backup.relative_to(root)), "rolled_back_at": now(),
                   "approved_by": args.approved_by, "approval_ref": args.approval_ref,
                   "rollback_owner": args.rollback_owner, "verified_by": args.verified_by,
                   "verification": {"asset_map": asset_map(root / ".mpa-workspace"), "verified_at": now()}}
        write_json(DEPLOYMENT_RECEIPTS / target_ref / f"rollback-{receipt_suffix()}.json", receipt)
        write_json(root / ".mpa-workspace" / "history" / "releases" / f"{release_id}.json", receipt)
    except Exception as error:
        if previous and previous.exists():
            if target.exists():
                shutil.rmtree(target)
            previous.replace(target)
        write_json(DEPLOYMENT_RECEIPTS / target_ref / f"rollback-failed-{receipt_suffix()}.json",
                   {"target": str(root), "backup": args.backup, "failed_at": now(), "error": str(error)})
        raise
    if previous and previous.exists():
        shutil.rmtree(previous)
    print("rolled back")


def issue_text(title: str, summary: str, kind: str, *, key: str = "legacy-issue", occurrence: str = "first_observed",
               area: str = "unspecified", observed_release: str = "unknown",
               collection_purpose: str = "review") -> str:
    return ("---\n" + json.dumps({"type": "issue", "status": "open", "kind": kind,
            "canonical_key": key, "occurrence": occurrence, "area": area,
            "observed_release": observed_release, "collection_purpose": collection_purpose,
            "created_at": now()}, ensure_ascii=False, indent=2) + "\n---\n\n"
            f"# {title}\n\n{summary}\n")


def check_issue_text(text: str) -> None:
    if SECRET.search(text) or ABSOLUTE_PATH.search(text):
        raise ValueError("issue contains a credential-like value or machine absolute path")


def create_issue(args: argparse.Namespace) -> None:
    project = Path(args.project).resolve()
    folder = project / "workspace" / "issues"
    folder.mkdir(parents=True, exist_ok=True)
    ident = f"issue-{dt.datetime.now().strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}.md"
    key = getattr(args, "key", None) or f"issue-{uuid.uuid4().hex[:12]}"
    require_safe_ref(key, "key")
    text = issue_text(args.title, args.summary, args.kind, key=key,
                      occurrence=getattr(args, "occurrence", "first_observed"),
                      area=getattr(args, "area", "unspecified"),
                      observed_release=getattr(args, "observed_release", "unknown"),
                      collection_purpose=getattr(args, "collection_purpose", "review"))
    (folder / ident).write_text(text, encoding="utf-8")
    print(ident)


def collect_issue(args: argparse.Namespace) -> None:
    project_ref = require_safe_ref(args.project_ref, "project-ref")
    project_issues = (Path(args.project).resolve() / "workspace" / "issues").resolve()
    source = (project_issues / args.issue).resolve()
    if project_issues not in source.parents or source.suffix != ".md" or not source.is_file():
        raise ValueError("specified issue does not exist")
    text = source.read_text(encoding="utf-8")
    check_issue_text(text)
    read_issue(source)
    destination = ISSUES / "inbox" / project_ref / source.name
    archived = list((ISSUES / "archived").rglob(source.name)) if (ISSUES / "archived").exists() else []
    if destination.exists() or archived:
        raise ValueError("issue already exists in inbox or archive")
    destination.parent.mkdir(parents=True, exist_ok=True)
    move_issue_atomically(source, destination)
    similar = [str(path.relative_to(ROOT)) for path in (ISSUES / "archived").rglob(f"*{source.stem}*")]
    try:
        issue_receipt("collections", f"{project_ref}/{source.name}", {"project": str(Path(args.project).resolve()), "similar_archives": similar})
    except Exception:
        move_issue_atomically(destination, source)
        raise
    print(json.dumps({"issue": str(destination.relative_to(ROOT)), "similar_archives": similar}, ensure_ascii=False))


def move_issue_atomically(source: Path, destination: Path) -> None:
    """Rename locally; use a fsync'd temporary destination across filesystems."""
    try:
        source.replace(destination)
        return
    except OSError as error:
        if error.errno != errno.EXDEV:
            raise
    temporary = destination.with_name(f".{destination.name}.new-{uuid.uuid4().hex[:8]}")
    try:
        with source.open("rb") as input_file, temporary.open("xb") as output_file:
            shutil.copyfileobj(input_file, output_file)
            output_file.flush()
            os.fsync(output_file.fileno())
        temporary.replace(destination)
        try:
            source.unlink()
        except Exception:
            destination.unlink(missing_ok=True)
            raise
    finally:
        if temporary.exists():
            temporary.unlink()


def inbox_issue(value: str) -> tuple[Path, str]:
    inbox = (ISSUES / "inbox").resolve()
    path = (ISSUES / "inbox" / value).resolve()
    if inbox not in path.parents or path.suffix != ".md" or not path.is_file():
        raise ValueError("issue must name an existing inbox markdown file")
    relative = path.relative_to(inbox)
    if len(relative.parts) != 2 or not SAFE_REF.fullmatch(relative.parts[0]):
        raise ValueError("issue must be <project-ref>/<filename>.md")
    return path, relative.as_posix()


def read_issue(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("issue metadata is missing")
    try:
        raw, body = text[4:].split("\n---\n", 1)
        metadata = json.loads(raw)
    except (ValueError, json.JSONDecodeError) as error:
        raise ValueError("issue metadata is invalid") from error
    if metadata.get("type") != "issue":
        raise ValueError("not an issue record")
    required = ("canonical_key", "occurrence", "area", "observed_release", "collection_purpose")
    if any(not metadata.get(field) for field in required):
        raise ValueError("issue canonical metadata is incomplete")
    return metadata, body


def write_issue(path: Path, metadata: dict, body: str) -> None:
    path.write_text("---\n" + json.dumps(metadata, ensure_ascii=False, indent=2) + "\n---\n" + body,
                    encoding="utf-8")


def issue_receipt(kind: str, issue: str, value: dict) -> None:
    write_json(ISSUE_RECEIPTS / kind / f"{receipt_suffix()}.json", {"issue": issue, "at": now(), **value})


def review_issue(args: argparse.Namespace) -> None:
    path, issue = inbox_issue(args.issue)
    metadata, body = read_issue(path)
    original = path.read_text(encoding="utf-8")
    metadata.update({"review_status": args.decision, "reviewed_at": now(),
                     "approved_by": args.reviewed_by, "approval_ref": args.approval_ref})
    try:
        write_issue(path, metadata, body)
        issue_receipt("reviews", issue, {"reviewed_by": args.reviewed_by,
                      "approved_by": args.reviewed_by, "approval_ref": args.approval_ref,
                      "decision": args.decision})
    except Exception:
        path.write_text(original, encoding="utf-8")
        raise
    print(issue)


def triage_issue(args: argparse.Namespace) -> None:
    path, issue = inbox_issue(args.issue)
    metadata, body = read_issue(path)
    if metadata.get("review_status") != "accepted" or not metadata.get("approval_ref"):
        raise ValueError("an accepted review receipt is required before triage")
    original = path.read_text(encoding="utf-8")
    metadata.update({"status": args.status, "classification": args.classification, "triaged_at": now(),
                     "reproduction": args.reproduction, "impact": args.impact, "priority": args.priority,
                     "relationship": args.relationship, "follow_up_task": args.follow_up_task})
    try:
        write_issue(path, metadata, body)
        issue_receipt("triages", issue, {"classification": args.classification, "triaged_by": args.triaged_by,
                                          "status": args.status, "reproduction": args.reproduction,
                                          "impact": args.impact, "priority": args.priority,
                                          "relationship": args.relationship, "follow_up_task": args.follow_up_task})
    except Exception:
        path.write_text(original, encoding="utf-8")
        raise
    print(issue)


def resolve_issue(args: argparse.Namespace) -> None:
    path, issue = inbox_issue(args.issue)
    metadata, body = read_issue(path)
    if metadata.get("status") != "triaged":
        raise ValueError("issue must be triaged before resolution")
    manifest = (MANIFESTS / f"{args.release}.json").resolve()
    deployment = (ROOT / args.deployment).resolve()
    if not manifest.is_file() or DEPLOYMENT_RECEIPTS.resolve() not in deployment.parents or not deployment.is_file():
        raise ValueError("resolution requires an existing release manifest and deployment receipt")
    deployment_data = json.loads(deployment.read_text(encoding="utf-8"))
    if deployment_data.get("release_id") != args.release:
        raise ValueError("deployment receipt must belong to the resolved release")
    original = path.read_text(encoding="utf-8")
    metadata.update({"status": "resolved", "resolved_at": now(), "task": args.task,
                     "release": args.release, "deployment": relative_to_root(deployment),
                     "verification": args.verification})
    try:
        write_issue(path, metadata, body)
        issue_receipt("resolutions", issue, {"resolved_by": args.resolved_by, "release": args.release,
                                               "deployment": relative_to_root(deployment), "verification": args.verification})
    except Exception:
        path.write_text(original, encoding="utf-8")
        raise
    print(issue)


def archive_issue(args: argparse.Namespace) -> None:
    path, issue = inbox_issue(args.issue)
    metadata, _ = read_issue(path)
    if metadata.get("status") != "resolved" or not all(metadata.get(key) for key in ("release", "deployment", "verification")):
        raise ValueError("only resolved issues with release, deployment, and verification evidence may be archived")
    manifest = MANIFESTS / f"{metadata['release']}.json"
    deployment = (ROOT / metadata["deployment"]).resolve()
    if not manifest.is_file() or DEPLOYMENT_RECEIPTS.resolve() not in deployment.parents or not deployment.is_file():
        raise ValueError("archive evidence no longer exists")
    if json.loads(deployment.read_text(encoding="utf-8")).get("release_id") != metadata["release"]:
        raise ValueError("archive deployment evidence does not match release")
    project_ref = issue.split("/", 1)[0]
    destination = ISSUES / "archived" / dt.datetime.now(dt.timezone.utc).strftime("%Y/%m") / project_ref / path.name
    if destination.exists():
        raise ValueError("archive destination already exists")
    destination.parent.mkdir(parents=True, exist_ok=True)
    move_issue_atomically(path, destination)
    try:
        issue_receipt("archives", issue, {"archive": str(destination.relative_to(ROOT)), "archived_by": args.archived_by})
    except Exception:
        move_issue_atomically(destination, path)
        raise
    print(destination.relative_to(ROOT))


def main() -> int:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("sync-runtime").set_defaults(func=sync_runtime)
    commands.add_parser("release-audit").set_defaults(func=audit_releases)
    release = commands.add_parser("prepare-release")
    release.add_argument("--verified-by", required=True)
    release.add_argument("--compatibility", required=True); release.add_argument("--breaking-change", required=True)
    release.add_argument("--migration", required=True); release.add_argument("--rollback-condition", required=True)
    release.add_argument("--release-note", required=True)
    release.add_argument("--validation-command", required=True, help="shell-like command text; executed without a shell")
    release.set_defaults(func=prepare_release)
    deploy_parser = commands.add_parser("deploy")
    deploy_parser.add_argument("--manifest", required=True); deploy_parser.add_argument("--target", required=True)
    deploy_parser.add_argument("--target-ref", required=True); deploy_parser.add_argument("--verified-by", required=True)
    deploy_parser.add_argument("--dry-run", required=True); deploy_parser.add_argument("--approved-by", required=True)
    deploy_parser.add_argument("--approval-ref", required=True); deploy_parser.add_argument("--rollback-owner", required=True)
    deploy_parser.set_defaults(func=deploy)
    dry_run = commands.add_parser("deployment-dry-run")
    dry_run.add_argument("--manifest", required=True); dry_run.add_argument("--target", required=True); dry_run.add_argument("--target-ref", required=True)
    dry_run.set_defaults(func=deployment_dry_run)
    roll = commands.add_parser("rollback")
    roll.add_argument("--target", required=True); roll.add_argument("--backup", required=True); roll.add_argument("--target-ref", required=True); roll.add_argument("--release-id", required=True)
    roll.add_argument("--verified-by", required=True); roll.add_argument("--approved-by", required=True); roll.add_argument("--approval-ref", required=True); roll.add_argument("--rollback-owner", required=True)
    roll.set_defaults(func=rollback)
    create = commands.add_parser("issue-create"); create.add_argument("--project", required=True); create.add_argument("--title", required=True); create.add_argument("--summary", required=True); create.add_argument("--kind", default="observation"); create.add_argument("--key"); create.add_argument("--occurrence", default="first_observed"); create.add_argument("--area", default="unspecified"); create.add_argument("--observed-release", default="unknown"); create.add_argument("--collection-purpose", default="review"); create.set_defaults(func=create_issue)
    collect = commands.add_parser("issue-collect"); collect.add_argument("--project", required=True); collect.add_argument("--project-ref", required=True); collect.add_argument("--issue", required=True); collect.set_defaults(func=collect_issue)
    review = commands.add_parser("issue-review"); review.add_argument("--issue", required=True); review.add_argument("--reviewed-by", required=True); review.add_argument("--approval-ref", required=True); review.add_argument("--decision", choices=("accepted", "rejected"), required=True); review.set_defaults(func=review_issue)
    triage = commands.add_parser("issue-triage"); triage.add_argument("--issue", required=True); triage.add_argument("--classification", required=True); triage.add_argument("--triaged-by", required=True)
    triage.add_argument("--status", choices=("triaged", "needs_information", "undetermined"), default="triaged")
    triage.add_argument("--reproduction", required=True); triage.add_argument("--impact", required=True); triage.add_argument("--priority", choices=("low", "medium", "high", "critical"), required=True)
    triage.add_argument("--relationship", choices=("recurrence", "regression", "duplicate", "related", "new", "undetermined"), required=True); triage.add_argument("--follow-up-task", default="none")
    triage.set_defaults(func=triage_issue)
    resolve = commands.add_parser("issue-resolve"); resolve.add_argument("--issue", required=True); resolve.add_argument("--task", required=True); resolve.add_argument("--release", required=True); resolve.add_argument("--deployment", required=True); resolve.add_argument("--verification", required=True); resolve.add_argument("--resolved-by", required=True); resolve.set_defaults(func=resolve_issue)
    archive = commands.add_parser("issue-archive"); archive.add_argument("--issue", required=True); archive.add_argument("--archived-by", required=True); archive.set_defaults(func=archive_issue)
    args = parser.parse_args()
    try:
        args.func(args)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
