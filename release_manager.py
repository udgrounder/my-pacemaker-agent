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
import stat
import subprocess
import sys
import tempfile
import uuid
import zipfile
from contextlib import contextmanager
from pathlib import Path

import project_config


ROOT = Path(__file__).resolve().parent
RUNTIME_SOURCE = ROOT / ".mpa/runtime"
RUNTIME_DIST = ROOT / "dist" / ".mpa/runtime"
RUNTIME_DIR = ".mpa/runtime"
LEGACY_RUNTIME_DIR = ".mpa-workspace"
INTERMEDIATE_RUNTIME_DIR = ".mpa-runtime"
LEGACY_CONFIG_RELATIVE = ".mpa-project/config.yaml"
INTERMEDIATE_CONFIG_RELATIVE = ".mpa-config/config.yaml"
LEGACY_RUNTIME_CONFIG = ".mpa-workspace/config.toml"
WORKSPACE = ROOT / "workspace"
RELEASES = WORKSPACE / "releases"
LEGACY_RELEASES = RELEASES / "legacy"
LEGACY_ACTIVE_MANIFESTS = RELEASES / "manifests"
LEGACY_ACTIVE_PACKAGES = RELEASES / "packages"
LEGACY_ACTIVE_RECEIPTS = WORKSPACE / "receipts" / "releases"
# Compatibility aliases are kept for integrations that import these constants;
# active releases are now discovered only under RELEASES/<release-id>/ bundles.
MANIFESTS = RELEASES
PACKAGES = RELEASES
RELEASE_RECEIPTS = RELEASES
DEPLOYMENT_RECEIPTS = WORKSPACE / "receipts" / "deployments"
ISSUES = WORKSPACE / "issues"
SAFE_REF = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
SECRET = re.compile(r"(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*\S+")
ABSOLUTE_PATH = re.compile(r"(?<![\w.-])/(?:Users|home|var|private|tmp|etc)/")
IGNORED_RUNTIME_NAMES = {"__pycache__", ".DS_Store", "history"}
RELEASE_METADATA = ("compatibility", "breaking_change", "migration", "rollback_condition", "release_note")
RELEASE_SCHEMA_VERSION = 4
VALIDATION_TIMEOUT_SECONDS = 120
RUNTIME_BACKUP_RETENTION = 3
DOCS_INDEX_TEMPLATE = "# 문서 색인\n\n> 이 파일은 agent가 문서 산출물의 위치와 요약을 관리합니다. 일반 문서 내용은 프로젝트 사용자가 소유합니다.\n\n"
RELEASE_BUNDLE_SCHEMA_VERSION = 1
BACKUP_MARKER = "backup-metadata.json"
LOCK_FILE = ".mpa-deploy.lock"
RUNTIME_BACKUP_ROOT = "runtime"
RUNTIME_CONFIG_BACKUP_ROOT = "runtime-config"


def resolve_runtime(root: Path) -> tuple[Path, bool]:
    """Return the installed Runtime and whether it still uses the legacy path."""
    runtime = root / RUNTIME_DIR
    if runtime.is_dir():
        return runtime, False
    legacy = root / LEGACY_RUNTIME_DIR
    if legacy.is_dir():
        return legacy, True
    intermediate = root / INTERMEDIATE_RUNTIME_DIR
    if intermediate.is_dir():
        return intermediate, True
    raise ValueError("target .mpa/runtime is missing; use install.py for first installation")


def migrate_legacy_project_config(root: Path) -> bool:
    """Seed the new config location without replacing an existing config."""
    destination = project_config.config_path(root)
    source = root / INTERMEDIATE_CONFIG_RELATIVE
    if not source.is_file():
        source = root / LEGACY_CONFIG_RELATIVE
    if destination.exists() or not source.is_file():
        return False
    destination.parent.mkdir(parents=True, exist_ok=True)
    content = source.read_text(encoding="utf-8").replace(LEGACY_RUNTIME_DIR, RUNTIME_DIR)
    temporary = destination.with_name(f".{destination.name}.migrate-{uuid.uuid4().hex[:8]}")
    try:
        temporary.write_text(content, encoding="utf-8")
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)
    return True


def migrate_legacy_runtime_config(root: Path, legacy_runtime: Path) -> bool:
    """Preserve the legacy per-project TOML beside the new project config."""
    source = root / ".mpa-config/config.toml"
    if not source.is_file():
        source = legacy_runtime / "config.toml"
    destination = root / ".mpa/config" / "config.toml"
    if destination.exists() or not source.is_file():
        return False
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return True


def migrate_agent_runtime_references(root: Path) -> list[str]:
    """Update only managed agent files that explicitly reference the legacy Runtime."""
    candidates = ("AGENTS.md", "CLAUDE.md", "GEMINI.md", ".claude/settings.json",
                  ".codex/hooks.json", ".agents/rules/mpa_pacemaker.md",
                  ".codex/agents/mpa_pacemaker.toml")
    updated = []
    for relative in candidates:
        path = root / relative
        if not path.is_file():
            continue
        content = path.read_text(encoding="utf-8")
        if LEGACY_RUNTIME_DIR not in content and INTERMEDIATE_RUNTIME_DIR not in content:
            continue
        temporary = path.with_name(f".{path.name}.mpa-path-{uuid.uuid4().hex[:8]}")
        try:
            temporary.write_text(content.replace(LEGACY_RUNTIME_DIR, RUNTIME_DIR).replace(INTERMEDIATE_RUNTIME_DIR, RUNTIME_DIR), encoding="utf-8")
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)
        updated.append(relative)
    return updated


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


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


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
    temporary = path.with_name(f".{path.name}.tmp-{uuid.uuid4().hex[:8]}")
    try:
        with temporary.open("w", encoding="utf-8") as stream:
            stream.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def _runtime_config_migration(value: object) -> dict[str, object] | None:
    return project_config.validate_runtime_config_migration(value)


def _runtime_config_checksum(root: Path) -> str | None:
    path = project_config.config_path(root)
    return sha(path) if path.is_file() else None


def _runtime_config_summary(root: Path, migration: object) -> dict[str, object]:
    normalized = _runtime_config_migration(migration)
    preview = project_config.preview_runtime_config_migration(root, normalized)
    return {
        "schema_version": preview.get("schema_version"),
        "add": preview.get("add", []),
        "skipped": preview.get("skipped", []),
        "status": preview.get("status"),
        "config_checksum": _runtime_config_checksum(root),
    }


def _safe_relative(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError as error:
        raise ValueError(f"path escapes release root: {path}") from error


def _bundle_paths(release_id: str) -> dict[str, Path]:
    require_safe_ref(release_id, "release-id")
    bundle = RELEASES / release_id
    return {
        "bundle": bundle,
        "package": bundle / f"package_{release_id}.zip",
        "manifest": bundle / f"manifest_{release_id}.json",
        "note": bundle / f"note_{release_id}.md",
        "receipt": bundle / f"release-receipt_{release_id}.json",
    }


def _zip_runtime(source: Path, destination: Path) -> None:
    """Write a deterministic, symlink-free Runtime archive."""
    assert_safe_runtime_tree(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(source.rglob("*")):
            relative = path.relative_to(source)
            if any(part in IGNORED_RUNTIME_NAMES for part in relative.parts):
                continue
            if path.is_dir():
                continue
            info = zipfile.ZipInfo(relative.as_posix(), date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (path.stat().st_mode & 0o777) << 16
            archive.writestr(info, path.read_bytes())


def _zip_entries(archive_path: Path) -> list[str]:
    try:
        with zipfile.ZipFile(archive_path) as archive:
            return archive.namelist()
    except (OSError, zipfile.BadZipFile) as error:
        raise ValueError(f"release package is not a valid ZIP: {archive_path.name}") from error


def _validate_zip_member(name: str) -> None:
    path = Path(name)
    if not name or path.is_absolute() or ".." in path.parts:
        raise ValueError(f"release package contains an unsafe path: {name}")


def _archive_current_release(archive_path: Path) -> str:
    try:
        with zipfile.ZipFile(archive_path) as archive:
            info = archive.getinfo(".mpa-version")
            for line in archive.read(info).decode("utf-8").splitlines():
                if line.startswith("current_release:"):
                    return line.split(":", 1)[1].strip()
    except (KeyError, UnicodeDecodeError, OSError, zipfile.BadZipFile) as error:
        raise ValueError("release package .mpa-version is invalid") from error
    raise ValueError("release package current_release is missing")


def _extract_runtime(archive_path: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=False)
    names: set[str] = set()
    try:
        with zipfile.ZipFile(archive_path) as archive:
            for info in archive.infolist():
                _validate_zip_member(info.filename)
                if info.filename in names:
                    raise ValueError(f"release package contains a duplicate path: {info.filename}")
                names.add(info.filename)
                mode = (info.external_attr >> 16) & 0xFFFF
                if stat.S_IFMT(mode) == stat.S_IFLNK:
                    raise ValueError(f"release package contains a symlink: {info.filename}")
                target = (destination / info.filename).resolve()
                if destination.resolve() not in target.parents and target != destination.resolve():
                    raise ValueError(f"release package path escapes staging: {info.filename}")
                if info.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(info) as source, target.open("wb") as output:
                    shutil.copyfileobj(source, output)
                permissions = (info.external_attr >> 16) & 0o777
                if permissions:
                    target.chmod(permissions)
    except (OSError, ValueError, zipfile.BadZipFile) as error:
        shutil.rmtree(destination, ignore_errors=True)
        raise ValueError("release package extraction failed") from error


def _release_bundle_dirs() -> list[Path]:
    if not RELEASES.is_dir():
        return []
    return sorted(path for path in RELEASES.iterdir()
                  if path.is_dir() and SAFE_REF.fullmatch(path.name)
                  and path.name not in {"legacy", "manifests", "packages"})


@contextmanager
def target_lock(root: Path):
    """Prevent concurrent deploy/rollback for one target without a hard gate elsewhere."""
    lock_path = root / LOCK_FILE
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    stream = lock_path.open("a+", encoding="utf-8")
    try:
        try:
            import fcntl
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except ImportError:
            pass
        except BlockingIOError as error:
            raise ValueError("target already has a deploy or rollback in progress") from error
        yield
    finally:
        try:
            import fcntl
            fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
        except ImportError:
            pass
        stream.close()


def _remove_created_project_paths(root: Path, created: list[str]) -> None:
    for relative in sorted(created, key=lambda value: value.count("/"), reverse=True):
        path = root / relative.rstrip("/")
        if path.is_file():
            path.unlink()
        elif path.is_dir() and not any(path.iterdir()):
            path.rmdir()


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
    paths = [".mpa/runtime", "dist/.mpa/runtime", "release_manager.py", "install.py"]
    try:
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True,
                              capture_output=True, check=True).stdout.strip()
        diff = subprocess.run(["git", "diff", "--name-status", "--", *paths], cwd=ROOT,
                              text=True, capture_output=True, check=True).stdout.splitlines()
        return {"status": "available", "head": head, "scoped_diff": diff}
    except (OSError, subprocess.CalledProcessError):
        return {"status": "unavailable"}


def current_release(root: Path) -> str:
    version_file = root / ".mpa-version"
    if not version_file.is_file():
        raise ValueError("Runtime .mpa-version is missing")
    content = version_file.read_text(encoding="utf-8")
    match = re.search(r"^current_release:\s*(.+?)\s*$", content, re.MULTILINE)
    if match:
        return match.group(1)
    match = re.search(r"^current_version:\s*(.+?)\s*$", content, re.MULTILINE)
    if not match:
        raise ValueError("Runtime current_release is missing")
    # Upgrade keeps the pre-schema-4 value only as an historical origin marker.
    return "legacy-" + re.sub(r"[^a-z0-9._-]+", "-", match.group(1).lower()).strip("-")


def new_release_id() -> str:
    """Return the sole user-visible release key: UTC timestamp plus random suffix."""
    return f"{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"


def set_current_release(root: Path, ident: str) -> None:
    require_safe_ref(ident, "release-id")
    version_file = root / ".mpa-version"
    version_file.parent.mkdir(parents=True, exist_ok=True)
    version_file.write_text(f"current_release: {ident}\n", encoding="utf-8")


def restore_release_version(version_file: Path, original: str | None) -> None:
    if original is None:
        version_file.unlink(missing_ok=True)
    else:
        version_file.write_text(original, encoding="utf-8")
    sync_runtime(argparse.Namespace())


def migrate_legacy_active_releases() -> None:
    """Move pre-bundle active artifacts out of the new release inventory."""
    date_root = dt.datetime.now().strftime("%Y%m%d")
    legacy_root = LEGACY_RELEASES / "migrated" / date_root
    legacy_receipts = WORKSPACE / "receipts" / "legacy" / "migrations" / date_root
    legacy_ids = set()
    records: dict[str, dict[str, list[str] | str]] = {}
    for path in LEGACY_ACTIVE_MANIFESTS.glob("*.json") if LEGACY_ACTIVE_MANIFESTS.exists() else []:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {}
        raw_ident = str(data.get("release_id") or path.stem)
        ident = raw_ident if SAFE_REF.fullmatch(raw_ident) else f"legacy-{sha_bytes(raw_ident.encode())[:12]}"
        legacy_ids.add(ident)
        destination = legacy_root / ident
        destination.mkdir(parents=True, exist_ok=True)
        path.replace(destination / path.name)
        records[ident] = {"source_paths": [relative_to_root(path)],
                          "destination_root": relative_to_root(destination)}
    for ident in legacy_ids:
        package = LEGACY_ACTIVE_PACKAGES / ident
        if package.exists():
            destination = legacy_root / ident
            destination.mkdir(parents=True, exist_ok=True)
            package.replace(destination / package.name)
            records.setdefault(ident, {"source_paths": [], "destination_root": relative_to_root(destination)})
            records[ident]["source_paths"].append(relative_to_root(package))
    for path in LEGACY_ACTIVE_RECEIPTS.glob("*.json") if LEGACY_ACTIVE_RECEIPTS.exists() else []:
        try:
            raw_receipt_id = str(json.loads(path.read_text(encoding="utf-8")).get("release_id") or "")
            receipt_id = raw_receipt_id if SAFE_REF.fullmatch(raw_receipt_id) else f"legacy-{sha_bytes(raw_receipt_id.encode())[:12]}"
            if receipt_id in legacy_ids:
                legacy_receipts.mkdir(parents=True, exist_ok=True)
                path.replace(legacy_receipts / path.name)
                records.setdefault(receipt_id, {"source_paths": [], "destination_root": relative_to_root(legacy_root / receipt_id)})
                records[receipt_id]["source_paths"].append(relative_to_root(path))
        except json.JSONDecodeError:
            continue
    for ident, record in records.items():
        write_json(legacy_receipts / f"{ident}-bundle-migration-{receipt_suffix()}.json", {
            "schema_version": 1,
            "kind": "release_layout_migration",
            "release_id": ident,
            "reason": "pre-bundle active manifest/package/receipt moved out of active inventory",
            "source_paths": record["source_paths"],
            "destination_root": record["destination_root"],
            "migrated_at": now(),
            "verified_by": "release-manager",
        })


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


def load_runtime_config_migration(value: object) -> dict[str, object] | None:
    """Load optional release-local Runtime defaults from a JSON file."""
    if value in (None, ""):
        return None
    path = Path(str(value))
    if not path.is_absolute():
        path = ROOT / path
    try:
        migration = json.loads(path.read_text(encoding="utf-8"))
    except OSError as error:
        raise ValueError(f"runtime config migration file cannot be read: {path}") from error
    except json.JSONDecodeError as error:
        raise ValueError("runtime config migration file is not valid JSON") from error
    return _runtime_config_migration(migration)


def prepare_release(args: argparse.Namespace) -> None:
    if isinstance(args.validation_command, list):  # direct API use in tests/integrations
        validation_command = args.validation_command
    else:
        try:
            validation_command = json.loads(args.validation_command)
        except (TypeError, json.JSONDecodeError) as error:
            raise ValueError("validation-command must be an argv JSON array") from error
    metadata = {field: getattr(args, field) for field in RELEASE_METADATA}
    if any(not value.strip() for value in metadata.values()):
        raise ValueError("release metadata fields must not be empty")
    runtime_config = load_runtime_config_migration(getattr(args, "runtime_config_json", None))
    migrate_legacy_active_releases()
    version_file = RUNTIME_SOURCE / ".mpa-version"
    original_version = version_file.read_text(encoding="utf-8") if version_file.exists() else None
    ident = new_release_id()
    try:
        set_current_release(RUNTIME_SOURCE, ident)
        sync_runtime(argparse.Namespace())
        validation = run_validation(validation_command)
    except Exception:
        restore_release_version(version_file, original_version)
        raise
    assets = asset_map(RUNTIME_DIST)
    if current_release(RUNTIME_DIST) != ident:
        raise ValueError("Runtime release ID does not match prepared release")
    paths = _bundle_paths(ident)
    if paths["bundle"].exists():
        raise ValueError("generated release ID already exists")
    staging = RELEASES / f".{ident}.new-{uuid.uuid4().hex[:8]}"
    final_paths = _bundle_paths(ident)
    staged_paths = {
        key: staging / path.name for key, path in final_paths.items() if key != "bundle"
    }
    package_checksum = None
    asset_checksum = hashlib.sha256(json.dumps(assets, sort_keys=True).encode()).hexdigest()
    runtime_config_checksum = (hashlib.sha256(json.dumps(runtime_config, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
                               if runtime_config is not None else None)
    try:
        staging.mkdir(parents=True, exist_ok=False)
        _zip_runtime(RUNTIME_DIST, staged_paths["package"])
        package_checksum = sha(staged_paths["package"])
        note = (
            f"# Release {ident}\n\n"
            f"- release_id: `{ident}`\n"
            f"- verified_by: {args.verified_by}\n"
            f"- created_at: {now()}\n"
            f"- package: `package_{ident}.zip`\n\n"
            "## Release metadata\n\n"
            + "\n".join(f"- {field}: {metadata[field]}" for field in RELEASE_METADATA)
            + "\n\n## Validation\n\n"
            + f"- command: `{json.dumps(validation['command'], ensure_ascii=False)}`\n"
            + f"- exit_code: `{validation['exit_code']}`\n"
        )
        if runtime_config is not None:
            note += ("\n## Runtime config migration\n\n"
                     f"- schema_version: `{runtime_config['schema_version']}`\n"
                     f"- additive keys: `{json.dumps(sorted(runtime_config['additive_defaults']), ensure_ascii=False)}`\n"
                     "- existing project/user values are preserved; rollback restores the pre-deploy config snapshot.\n")
        staged_paths["note"].write_text(note, encoding="utf-8")
        final_manifest = final_paths["manifest"]
        final_receipt = final_paths["receipt"]
        final_package = final_paths["package"]
        final_note = final_paths["note"]
        receipt = {
            "schema_version": RELEASE_SCHEMA_VERSION,
            "bundle_schema_version": RELEASE_BUNDLE_SCHEMA_VERSION,
            "release_id": ident,
            "manifest": relative_to_root(final_manifest),
            "package": relative_to_root(final_package),
            "note": relative_to_root(final_note),
            "created_at": now(),
            "verified_by": args.verified_by,
            "package_checksum": package_checksum,
            "asset_checksum": asset_checksum,
            "validation": validation,
        }
        if runtime_config is not None:
            receipt["runtime_config"] = {
                "schema_version": runtime_config["schema_version"],
                "migration_checksum": runtime_config_checksum,
            }
        write_json(staged_paths["receipt"], receipt)
        manifest = {
            "schema_version": RELEASE_SCHEMA_VERSION,
            "bundle_schema_version": RELEASE_BUNDLE_SCHEMA_VERSION,
            "release_id": ident,
            "created_at": now(),
            "asset_root": "dist/.mpa/runtime",
            "package": relative_to_root(final_package),
            "note": relative_to_root(final_note),
            "assets": assets,
            "asset_checksum": asset_checksum,
            "package_checksum": package_checksum,
            "source_snapshot": {"allowlist": sorted(assets), "asset_checksum": asset_checksum, "validation": validation, "metadata": metadata},
            "source_git": scoped_git(),
            "metadata": metadata,
            "validation": validation,
            "release_receipt": relative_to_root(final_receipt),
        }
        if runtime_config is not None:
            manifest["runtime_config"] = runtime_config
        write_json(staged_paths["manifest"], manifest)
        staging.replace(final_paths["bundle"])
    except Exception:
        if staging.exists():
            shutil.rmtree(staging)
        restore_release_version(version_file, original_version)
        raise
    print(ident)


def load_manifest(value: str) -> tuple[Path, dict]:
    path = Path(value)
    if not path.is_absolute():
        path = ROOT / path
    path = path.resolve()
    if RELEASES.resolve() not in path.parents or path.parent.parent != RELEASES.resolve():
        raise ValueError("manifest must be inside workspace/releases/<release-id>")
    data = json.loads(path.read_text(encoding="utf-8"))
    release_id = data.get("release_id")
    if (data.get("schema_version") != RELEASE_SCHEMA_VERSION or
            data.get("bundle_schema_version") != RELEASE_BUNDLE_SCHEMA_VERSION or
            not isinstance(release_id, str) or not SAFE_REF.fullmatch(release_id) or
            path.parent.name != release_id or path.name != f"manifest_{release_id}.json" or
            not isinstance(data.get("assets"), dict)):
        raise ValueError("invalid release manifest")
    paths = _bundle_paths(release_id)
    if data.get("package") != relative_to_root(paths["package"]):
        raise ValueError("manifest package path is invalid")
    if data.get("note") != relative_to_root(paths["note"]):
        raise ValueError("manifest note path is invalid")
    if data.get("release_receipt") != relative_to_root(paths["receipt"]):
        raise ValueError("manifest release receipt path is invalid")
    if not isinstance(data.get("metadata"), dict) or any(not data["metadata"].get(field) for field in RELEASE_METADATA):
        raise ValueError("manifest release metadata is incomplete")
    if not isinstance(data.get("validation"), dict) or data["validation"].get("exit_code") != 0:
        raise ValueError("manifest validation result is invalid")
    receipt = paths["receipt"].resolve()
    if not receipt.is_file():
        raise ValueError("manifest release receipt is missing")
    receipt_data = json.loads(receipt.read_text(encoding="utf-8"))
    runtime_config = data.get("runtime_config")
    if runtime_config is not None:
        runtime_config = _runtime_config_migration(runtime_config)
        expected_runtime_receipt = {
            "schema_version": runtime_config["schema_version"],
            "migration_checksum": hashlib.sha256(json.dumps(runtime_config, ensure_ascii=False, sort_keys=True).encode()).hexdigest(),
        }
    else:
        expected_runtime_receipt = None
    if (receipt_data.get("schema_version") != RELEASE_SCHEMA_VERSION or
            receipt_data.get("bundle_schema_version") != RELEASE_BUNDLE_SCHEMA_VERSION or
            receipt_data.get("release_id") != data["release_id"] or
            receipt_data.get("manifest") != relative_to_root(path) or
            receipt_data.get("package") != data["package"] or
            receipt_data.get("note") != data["note"] or
            receipt_data.get("validation") != data["validation"] or
            receipt_data.get("package_checksum") != data.get("package_checksum") or
            receipt_data.get("asset_checksum") != data.get("asset_checksum") or
            receipt_data.get("runtime_config") != expected_runtime_receipt):
        raise ValueError("manifest release receipt does not match")
    return path, data


def release_package(manifest: dict) -> Path:
    paths = _bundle_paths(manifest["release_id"])
    package = paths["package"].resolve()
    if not package.is_file():
        raise ValueError("immutable release package is missing")
    if manifest.get("package_checksum") != sha(package):
        raise ValueError("immutable release package checksum does not match manifest")
    if _archive_current_release(package) != manifest["release_id"]:
        raise ValueError("immutable release package has a different current_release")
    return package


def audit_releases(_: argparse.Namespace) -> None:
    invalid = []
    if LEGACY_ACTIVE_MANIFESTS.exists() and any(LEGACY_ACTIVE_MANIFESTS.glob("*.json")):
        invalid.append("legacy active manifests require migration")
    if LEGACY_ACTIVE_PACKAGES.exists() and any(LEGACY_ACTIVE_PACKAGES.iterdir()):
        invalid.append("legacy active packages require migration")
    bundles = {path.name for path in _release_bundle_dirs()}
    for bundle in sorted(_release_bundle_dirs()):
        release_id = bundle.name
        paths = _bundle_paths(release_id)
        expected = {path.name for key, path in paths.items() if key != "bundle"}
        actual = {path.name for path in bundle.iterdir() if path.is_file()}
        if actual != expected:
            invalid.append(f"{release_id}: bundle file inventory mismatch")
        try:
            _, manifest = load_manifest(str(paths["manifest"]))
            package = release_package(manifest)
            with tempfile.TemporaryDirectory(prefix=f"audit-{release_id}-") as directory:
                extracted = Path(directory) / "runtime"
                _extract_runtime(package, extracted)
                if asset_map(extracted) != manifest["assets"]:
                    raise ValueError("decompressed Runtime asset map does not match manifest")
        except (OSError, ValueError, json.JSONDecodeError) as error:
            invalid.append(f"{release_id}: {error}")
    if invalid:
        raise ValueError("invalid release artifacts: " + "; ".join(invalid))
    print(f"release audit passed: {len(bundles)} release bundle(s)")


def verify_target(target: Path, expected: dict[str, str]) -> None:
    if asset_map(target) != expected:
        raise ValueError("target runtime asset map does not match release manifest")


def ensure_required_project_directories(root: Path) -> list[str]:
    """Create only missing empty user-owned roots required by install/update rules."""
    created = []
    required = ("workspace", "workspace/issues", "docs")
    for name in required:
        path = root / name
        if path.exists() and not path.is_dir():
            raise ValueError(f"required project path is not a directory: {name}")
    docs_index = root / "docs" / "INDEX.md"
    if docs_index.exists() and not docs_index.is_file():
        raise ValueError("required project path is not a file: docs/INDEX.md")
    for name in required:
        path = root / name
        if not path.exists():
            path.mkdir(parents=True)
            created.append(name + "/")
    if not docs_index.exists():
        temporary = docs_index.with_name(f".{docs_index.name}.new-{uuid.uuid4().hex[:8]}")
        try:
            temporary.write_text(DOCS_INDEX_TEMPLATE, encoding="utf-8")
            temporary.replace(docs_index)
        finally:
            temporary.unlink(missing_ok=True)
        created.append("docs/INDEX.md")
    return created


def prune_runtime_backups(root: Path, keep: int = RUNTIME_BACKUP_RETENTION) -> list[str]:
    """Retain only marked successful Runtime backups; leave unknown dirs untouched."""
    backups = root / ".mpa/backups"
    if not backups.is_dir():
        return []
    candidates = []
    for path in backups.iterdir():
        if not path.is_dir():
            continue
        marker = path / BACKUP_MARKER
        if not marker.is_file():
            continue
        try:
            metadata = json.loads(marker.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if metadata.get("kind") != "runtime_backup" or metadata.get("status") != "successful":
            continue
        candidates.append(path)
    candidates.sort(key=lambda path: path.stat().st_mtime_ns, reverse=True)
    removed = []
    for path in candidates[keep:]:
        shutil.rmtree(path)
        removed.append(path.name)
    return removed


def _backup_runtime_path(path: Path) -> Path:
    """Resolve the Runtime tree in a current or legacy backup."""
    nested = path / RUNTIME_BACKUP_ROOT / ".mpa/runtime"
    return nested if nested.is_dir() else path


def _backup_config_path(path: Path) -> Path:
    return path / RUNTIME_CONFIG_BACKUP_ROOT / "config.yaml"


def _capture_config(root: Path) -> tuple[bool, bytes | None]:
    path = project_config.config_path(root)
    return path.is_file(), path.read_bytes() if path.is_file() else None


def _restore_config_state(root: Path, state: tuple[bool, bytes | None]) -> None:
    existed, content = state
    path = project_config.config_path(root)
    if existed and content is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(f".{path.name}.restore-{uuid.uuid4().hex[:8]}")
        try:
            temporary.write_bytes(content)
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)
    elif path.exists():
        path.unlink()


def _backup_runtime(root: Path, target: Path, backup: Path, include_config: bool) -> dict[str, object]:
    runtime_destination = backup / RUNTIME_BACKUP_ROOT / ".mpa/runtime"
    runtime_destination.parent.mkdir(parents=True, exist_ok=False)
    shutil.copytree(target, runtime_destination)
    config_path = project_config.config_path(root)
    config_existed = config_path.is_file()
    config_destination = _backup_config_path(backup)
    if include_config and config_existed:
        config_destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(config_path, config_destination)
    return {"included": include_config, "existed": config_existed,
            "checksum": sha(config_path) if include_config and config_existed else None}


def _restore_config_from_backup(root: Path, backup: Path, metadata: dict[str, object]) -> None:
    snapshot = metadata.get("config_snapshot") or {}
    if not snapshot.get("included"):
        return
    path = project_config.config_path(root)
    if snapshot.get("existed"):
        source = _backup_config_path(backup)
        if not source.is_file() or (snapshot.get("checksum") and sha(source) != snapshot.get("checksum")):
            raise ValueError("backup Runtime config snapshot is missing or invalid")
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(f".{path.name}.rollback-{uuid.uuid4().hex[:8]}")
        try:
            shutil.copy2(source, temporary)
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)
    elif path.exists():
        path.unlink()


def _write_backup_marker(path: Path, release_id: str, assets: dict[str, str], config_snapshot: dict[str, object] | None = None) -> None:
    backup_assets = asset_map(path)
    backup_assets.pop(BACKUP_MARKER, None)
    write_json(path / BACKUP_MARKER, {
        "schema_version": 2,
        "kind": "runtime_backup",
        "status": "successful",
        "release_id": release_id,
        "asset_checksum": hashlib.sha256(json.dumps(backup_assets, sort_keys=True).encode()).hexdigest(),
        "release_asset_checksum": hashlib.sha256(json.dumps(assets, sort_keys=True).encode()).hexdigest(),
        "runtime_backup": "runtime/.mpa/runtime",
        "config_snapshot": config_snapshot or {"included": False, "existed": False, "checksum": None},
        "created_at": now(),
    })


def _validate_backup(path: Path, release_id: str) -> dict:
    marker = path / BACKUP_MARKER
    if not marker.is_file():
        raise ValueError("backup is not a managed Runtime backup")
    try:
        metadata = json.loads(marker.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError("backup metadata is invalid") from error
    if metadata.get("kind") != "runtime_backup" or metadata.get("status") != "successful" or metadata.get("release_id") != release_id:
        raise ValueError("backup metadata does not match release")
    assets = asset_map(path)
    assets.pop(BACKUP_MARKER, None)
    checksum = hashlib.sha256(json.dumps(assets, sort_keys=True).encode()).hexdigest()
    if metadata.get("asset_checksum") != checksum:
        raise ValueError("backup asset checksum does not match metadata")
    runtime_path = _backup_runtime_path(path)
    if not runtime_path.is_dir():
        raise ValueError("backup Runtime tree is missing")
    if metadata.get("schema_version", 1) >= 2 and metadata.get("runtime_backup") != "runtime/.mpa/runtime":
        raise ValueError("backup Runtime path metadata is invalid")
    return metadata


def update_issue_inventory(root: Path) -> list[dict[str, str]]:
    folder = root / "workspace" / "issues"
    if not folder.is_dir():
        return []
    return [{"path": path.name, "checksum": sha(path)} for path in sorted(folder.glob("*.md"))]


def project_fingerprint(root: Path) -> str:
    return sha_bytes(str(root.resolve()).encode("utf-8"))[:16]


def _issue_identity(path: Path) -> dict[str, str]:
    metadata, _ = read_issue(path)
    return {
        key: str(metadata[key])
        for key in ("source_issue_id", "workspace_issue_id", "canonical_issue_key")
        if metadata.get(key)
    }


def _existing_issue_identity_matches(identity: dict[str, str]) -> list[str]:
    matches: list[str] = []
    for path in list((ISSUES / "inbox").rglob("*.md")) if (ISSUES / "inbox").exists() else []:
        try:
            values = _issue_identity(path)
        except (OSError, ValueError, json.JSONDecodeError):
            continue
        if any(values.get(key) == value for key, value in identity.items()):
            matches.append(str(path.relative_to(ROOT)))
    for path in list((ISSUES / "archived").rglob("*.md")) if (ISSUES / "archived").exists() else []:
        try:
            values = _issue_identity(path)
        except (OSError, ValueError, json.JSONDecodeError):
            continue
        if any(values.get(key) == value for key, value in identity.items()):
            matches.append(str(path.relative_to(ROOT)))
    return matches


def _rollback_issue_moves(moved: list[tuple[Path, Path]]) -> None:
    for source, destination in reversed(moved):
        if destination.exists() and not source.exists():
            move_issue_atomically(destination, source)


def confirm_issue_move(source: Path, destination: Path) -> None:
    """Confirm that an issue move completed without retaining a second receipt."""
    if destination.is_file() and not source.exists():
        return
    if destination.is_file() and source.exists():
        raise OSError("issue move verification failed: source reappeared; preserved both files for reconciliation")
    raise OSError("issue move verification failed")


def delete_issue_source(source: Path) -> None:
    source.unlink()


def transfer_issue_after_verification(source: Path, destination: Path) -> None:
    """Create and confirm the destination before deleting the collection source."""
    temporary = destination.with_name(f".{destination.name}.new-{uuid.uuid4().hex[:8]}")
    destination_created = False
    source_deleted = False
    try:
        with source.open("rb") as input_file, temporary.open("xb") as output_file:
            shutil.copyfileobj(input_file, output_file)
            output_file.flush()
            os.fsync(output_file.fileno())
        os.link(temporary, destination)
        destination_created = True
        temporary.unlink()
        if not destination.is_file():
            raise OSError("issue destination verification failed")
        delete_issue_source(source)
        source_deleted = True
        confirm_issue_move(source, destination)
    except Exception:
        if not source_deleted and source.exists() and destination_created and destination.exists():
            destination.unlink()
        raise
    finally:
        if temporary.exists():
            temporary.unlink()


def collect_update_issues_transaction(root: Path, project_ref: str,
                                      expected: list[dict[str, str]]) -> tuple[list[str], list[tuple[Path, Path]]]:
    """Collect a verified update batch and return rollback handles for the caller."""
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
        identity_matches = _existing_issue_identity_matches(_issue_identity(source))
        if destination.exists() or archived or identity_matches:
            raise ValueError("update issue already exists in inbox or archive")
        destinations.append((source, destination))
    moved: list[tuple[Path, Path]] = []
    try:
        for source, destination in destinations:
            destination.parent.mkdir(parents=True, exist_ok=True)
            transfer_issue_after_verification(source, destination)
            moved.append((source, destination))
    except Exception:
        _rollback_issue_moves(moved)
        raise
    return [str(destination.relative_to(ROOT)) for _, destination in moved], moved


def collect_update_issues(root: Path, project_ref: str, expected: list[dict[str, str]]) -> list[str]:
    collected, _ = collect_update_issues_transaction(root, project_ref, expected)
    return collected


def deployment_dry_run(args: argparse.Namespace) -> None:
    target_ref = require_safe_ref(args.target_ref, "target-ref")
    manifest_path, manifest = load_manifest(args.manifest)
    release_package(manifest)
    root = Path(args.target).resolve()
    target, legacy_runtime = resolve_runtime(root)
    created_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    result = {"release_id": manifest["release_id"],
              "from_release": current_release(target), "to_release": manifest["release_id"], "manifest": relative_to_root(manifest_path),
              "release_receipt": manifest["release_receipt"],
              "target": str(root), "target_ref": target_ref, "current_assets": asset_map(target),
              "release_assets": manifest["assets"], "history": target_history(target), "issue_inventory": update_issue_inventory(root),
              "runtime_config": _runtime_config_summary(root, manifest.get("runtime_config")),
              "path_migration": {"from": LEGACY_RUNTIME_DIR if legacy_runtime else RUNTIME_DIR,
                                 "to": RUNTIME_DIR, "required": legacy_runtime},
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
    target, legacy_runtime = resolve_runtime(root)
    original_target = target
    destination = root / RUNTIME_DIR
    dry_run = (ROOT / args.dry_run).resolve()
    if DEPLOYMENT_RECEIPTS.resolve() not in dry_run.parents or not dry_run.is_file():
        raise ValueError("deploy requires a recorded deployment dry-run")
    with target_lock(root):
        dry_run_data = json.loads(dry_run.read_text(encoding="utf-8"))
        if (dry_run_data.get("release_id") != manifest["release_id"] or dry_run_data.get("to_release") != manifest["release_id"] or
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
                dry_run_data.get("from_release") != current_release(target)):
            raise ValueError("target changed after dry-run")
        if dry_run_data.get("issue_inventory") != update_issue_inventory(root):
            raise ValueError("project issues changed after dry-run")
        runtime_config = manifest.get("runtime_config")
        dry_runtime_config = dry_run_data.get("runtime_config", {})
        if runtime_config is not None and dry_runtime_config.get("config_checksum") != _runtime_config_checksum(root):
            raise ValueError("Runtime project config changed after dry-run")
        if runtime_config is not None:
            _runtime_config_migration(runtime_config)
        if not all(str(getattr(args, field, "")).strip() for field in ("approved_by", "approval_ref", "rollback_owner")):
            raise ValueError("approved-by, approval-ref, and rollback-owner are required")
        if target_history(target).get(manifest["release_id"], {}).get("status") == "applied":
            raise ValueError("target history already contains this release ID")
        from_release = current_release(target)
        backup = root / ".mpa/backups" / f"{manifest['release_id']}-{receipt_suffix()}"
        replacement = None
        previous = None
        created_paths: list[str] = []
        moved_issues: list[tuple[Path, Path]] = []
        deployment_receipt: Path | None = None
        history_path: Path | None = None
        config_snapshot: dict[str, object] = {"included": False, "existed": False, "checksum": None}
        migrated_legacy_toml = False
        migrated_legacy_config = False
        migrated_agent_files: list[str] = []
        with tempfile.TemporaryDirectory(prefix=f"deploy-{manifest['release_id']}-") as directory:
            extracted = Path(directory) / "runtime"
            try:
                created_paths = ensure_required_project_directories(root)
                backup.parent.mkdir(parents=True, exist_ok=True)
                config_snapshot = _backup_runtime(root, target, backup, runtime_config is not None)
                migrated_legacy_toml = legacy_runtime and migrate_legacy_runtime_config(root, target)
                replacement = destination.parent / f".runtime.new-{uuid.uuid4().hex[:8]}"
                previous = target.with_name(f"{target.name}.previous-{uuid.uuid4().hex[:8]}")
                _extract_runtime(package, extracted)
                shutil.copytree(extracted, replacement)
                history = target / "history"
                if history.exists():
                    shutil.copytree(history, replacement / "history")
                verify_target(replacement, manifest["assets"])
                target.replace(previous)
                try:
                    replacement.replace(destination)
                    target = destination
                    verify_target(target, manifest["assets"])
                except Exception:
                    if target.exists():
                        shutil.rmtree(target)
                    if previous.exists():
                        previous.replace(root / (LEGACY_RUNTIME_DIR if legacy_runtime else RUNTIME_DIR))
                    raise
                migrated_legacy_config = migrate_legacy_project_config(root)
                migrated_agent_files = migrate_agent_runtime_references(root) if legacy_runtime else []
                config_migration = {"status": "none", "add": [], "skipped": []}
                if runtime_config is not None:
                    config_migration = project_config.apply_runtime_config_migration(root, runtime_config)
                collected, moved_issues = collect_update_issues_transaction(
                    root, target_ref, dry_run_data["issue_inventory"])
                receipt = {
                    "status": "applied", "release_id": manifest["release_id"],
                    "from_release": from_release, "to_release": manifest["release_id"],
                    "manifest": relative_to_root(manifest_path),
                    "target_ref": target_ref, "target_fingerprint": project_fingerprint(root),
                    "backup": str(backup.relative_to(root)), "applied_at": now(), "verified_by": args.verified_by,
                    "approved_by": args.approved_by, "approval_ref": args.approval_ref,
                    "rollback_owner": args.rollback_owner, "dry_run": relative_to_root(dry_run),
                    "assets": manifest["assets"], "verification": {"asset_map": "matched", "verified_at": now()},
                    "runtime_config": {"migration": config_migration, "config_backup": config_snapshot},
                    "path_migration": {"from": LEGACY_RUNTIME_DIR if legacy_runtime else RUNTIME_DIR,
                                       "to": RUNTIME_DIR, "legacy_config_migrated": migrated_legacy_config,
                                       "legacy_toml_migrated": migrated_legacy_toml,
                                       "agent_files_migrated": migrated_agent_files},
                    "collected_issues": collected,
                    "issue_collection": {"status": "collected" if collected else "no-op", "count": len(collected)},
                }
                deployment_receipt = DEPLOYMENT_RECEIPTS / target_ref / f"deploy-{manifest['release_id']}-{receipt_suffix()}.json"
                history_path = target / "history" / "releases" / f"{manifest['release_id']}.json"
                write_json(deployment_receipt, receipt)
                write_json(history_path, receipt)
                _write_backup_marker(backup, manifest["release_id"], manifest["assets"], config_snapshot)
                if previous and previous.exists():
                    shutil.rmtree(previous)
                try:
                    removed_backups = prune_runtime_backups(root)
                    if removed_backups:
                        print(f"pruned runtime backups: {', '.join(removed_backups)}", file=sys.stderr)
                except OSError as error:
                    print(f"warning: runtime backup retention deferred: {error}", file=sys.stderr)
            except Exception as error:
                _rollback_issue_moves(moved_issues)
                if previous and previous.exists():
                    if target.exists():
                        shutil.rmtree(target)
                    previous.replace(original_target)
                try:
                    _restore_config_from_backup(root, backup, {"config_snapshot": config_snapshot})
                except Exception:
                    pass
                if replacement and replacement.exists():
                    shutil.rmtree(replacement)
                if deployment_receipt and deployment_receipt.exists():
                    deployment_receipt.unlink()
                if history_path and history_path.exists():
                    history_path.unlink()
                _remove_created_project_paths(root, created_paths)
                failure = {"status": "failed", "release_id": manifest["release_id"], "from_release": from_release,
                           "to_release": manifest["release_id"], "manifest": relative_to_root(manifest_path),
                           "target_ref": target_ref, "target_fingerprint": project_fingerprint(root),
                           "backup": str(backup.relative_to(root)) if backup.exists() else None,
                           "failed_at": now(), "error": str(error), "dry_run": relative_to_root(dry_run),
                           "recovery": {"runtime_restored": not previous or target.is_dir(), "issues_restored": not moved_issues}}
                try:
                    write_json(DEPLOYMENT_RECEIPTS / target_ref / f"deploy-failed-{manifest['release_id']}-{receipt_suffix()}.json", failure)
                except OSError:
                    pass
                if target.is_dir():
                    try:
                        write_json(target / "history" / "releases" / f"{manifest['release_id']}.json", failure)
                    except OSError:
                        pass
                raise
        print(json.dumps({"backup": str(backup.relative_to(root)), "issue_collection": receipt["issue_collection"]}, ensure_ascii=False))


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
    with target_lock(root):
        previous = None
        target = root / ".mpa/runtime"
        from_release = None
        created_paths: list[str] = []
        receipt_path: Path | None = None
        history_path: Path | None = None
        release_id = None
        config_before: tuple[bool, bytes | None] = (False, None)
        try:
            backups_root = (root / ".mpa/backups").resolve()
            backup = (root / args.backup).resolve()
            if backups_root not in backup.parents or not backup.is_dir():
                raise ValueError("backup must be inside target .mpa/backups")
            if not target.is_dir():
                raise ValueError("target .mpa/runtime is missing")
            release_id = require_safe_ref(args.release_id, "release-id")
            if release_id not in target_history(target):
                raise ValueError("target history does not contain the release to roll back")
            _validate_backup(backup, release_id)
            from_release = current_release(target)
            created_paths = ensure_required_project_directories(root)
            config_before = _capture_config(root)
            replacement = target.parent / f".runtime.rollback-{uuid.uuid4().hex[:8]}"
            previous = target.parent / f".runtime.rollback-previous-{uuid.uuid4().hex[:8]}"
            try:
                shutil.copytree(_backup_runtime_path(backup), replacement)
                target.replace(previous)
                try:
                    replacement.replace(target)
                    metadata = json.loads((backup / BACKUP_MARKER).read_text(encoding="utf-8"))
                    _restore_config_from_backup(root, backup, metadata)
                except Exception:
                    if previous.exists() and not target.exists():
                        previous.replace(target)
                    _restore_config_state(root, config_before)
                    raise
            finally:
                if replacement.exists():
                    shutil.rmtree(replacement)
            receipt = {"status": "rolled_back", "release_id": release_id,
                       "from_release": from_release, "to_release": current_release(root / ".mpa/runtime"),
                       "target_ref": target_ref, "target_fingerprint": project_fingerprint(root),
                       "backup": str(backup.relative_to(root)), "rolled_back_at": now(),
                       "approved_by": args.approved_by, "approval_ref": args.approval_ref,
                       "rollback_owner": args.rollback_owner, "verified_by": args.verified_by,
                       "verification": {"asset_map": asset_map(root / ".mpa/runtime"), "verified_at": now()}}
            receipt_path = DEPLOYMENT_RECEIPTS / target_ref / f"rollback-{receipt_suffix()}.json"
            history_path = root / ".mpa/runtime" / "history" / "releases" / f"{release_id}.json"
            write_json(receipt_path, receipt)
            write_json(history_path, receipt)
        except Exception as error:
            if previous and previous.exists():
                if target.exists():
                    shutil.rmtree(target)
                previous.replace(target)
            try:
                _restore_config_state(root, config_before)
            except Exception:
                pass
            if receipt_path and receipt_path.exists():
                receipt_path.unlink()
            if history_path and history_path.exists():
                history_path.unlink()
            _remove_created_project_paths(root, created_paths)
            try:
                write_json(DEPLOYMENT_RECEIPTS / target_ref / f"rollback-failed-{receipt_suffix()}.json",
                           {"status": "failed", "release_id": release_id, "target_ref": target_ref,
                            "target_fingerprint": project_fingerprint(root), "backup": args.backup,
                            "failed_at": now(), "error": str(error),
                            "recovery": {"runtime_restored": not previous or target.is_dir()}})
            except OSError:
                pass
            raise
        if previous and previous.exists():
            shutil.rmtree(previous)
        print(json.dumps({"status": "rolled_back", "release_id": release_id,
                          "backup": str(backup.relative_to(root))}, ensure_ascii=False))


def issue_text(title: str, summary: str, kind: str, *, key: str = "legacy-issue", occurrence: str = "first_observed",
               area: str = "unspecified", observed_release: str = "unknown",
               collection_purpose: str = "review", source_issue_id: str | None = None,
               workspace_issue_id: str | None = None) -> str:
    return ("---\n" + json.dumps({"type": "issue", "status": "open", "kind": kind,
            "canonical_key": key, "canonical_issue_key": key,
            "occurrence": occurrence, "area": area,
            "observed_release": observed_release, "collection_purpose": collection_purpose,
            "source_issue_id": source_issue_id or "unknown",
            "workspace_issue_id": workspace_issue_id or f"workspace-issue-{uuid.uuid4().hex}",
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
                      collection_purpose=getattr(args, "collection_purpose", "review"),
                      source_issue_id=Path(ident).stem)
    check_issue_text(text)
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
    identity_matches = _existing_issue_identity_matches(_issue_identity(source))
    if destination.exists() or archived or identity_matches:
        raise ValueError("issue already exists in inbox or archive")
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        transfer_issue_after_verification(source, destination)
    except Exception:
        _rollback_issue_moves([(source, destination)])
        raise
    similar = [str(path.relative_to(ROOT)) for path in (ISSUES / "archived").rglob(f"*{source.stem}*")]
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


def task_plan_reference(value: str) -> str:
    candidate = (ROOT / value).resolve()
    active_tasks_root = (WORKSPACE / "tasks" / "active").resolve()
    if (active_tasks_root not in candidate.parents or candidate.name != "plan.md" or
            not candidate.is_file()):
        raise ValueError("accepted issue requires an existing active workspace task plan")
    return str(candidate.relative_to(ROOT.resolve()))


def archive_issue(args: argparse.Namespace) -> None:
    """Archive a user-decided issue, preserving the decision in the issue itself."""
    if args.decision not in ("accepted", "rejected"):
        raise ValueError("decision must be accepted or rejected")
    if not args.decided_by.strip() or not args.reason.strip():
        raise ValueError("decided-by and reason are required")
    path, issue = inbox_issue(args.issue)
    metadata, body = read_issue(path)
    if metadata.get("status") != "open":
        raise ValueError("only open inbox issues may be archived by decision")
    task = None
    if args.decision == "accepted":
        if not args.task:
            raise ValueError("accepted issue requires a task plan")
        task = task_plan_reference(args.task)
    elif args.task:
        raise ValueError("rejected issue must not link a task")
    project_ref = issue.split("/", 1)[0]
    destination = ISSUES / "archived" / dt.datetime.now(dt.timezone.utc).strftime("%Y/%m") / project_ref / path.name
    if destination.exists():
        raise ValueError("archive destination already exists")
    decided_at = now()
    metadata.update({"status": "archived", "decision": args.decision,
                     "decided_by": args.decided_by, "decided_at": decided_at,
                     "decision_reason": args.reason, "follow_up_task": task})
    result = ("\n\n## 처리 결과\n\n"
              f"- 사용자 결정: `{args.decision}`\n"
              f"- 판단자: {args.decided_by}\n"
              f"- 판단 근거: {args.reason}\n")
    if task:
        result += f"- 연결 작업: `{task}`\n"
    original = path.read_text(encoding="utf-8")
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        write_issue(path, metadata, body.rstrip() + result)
        move_issue_atomically(path, destination)
    except Exception:
        if destination.exists():
            move_issue_atomically(destination, path)
        path.write_text(original, encoding="utf-8")
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
    release.add_argument("--runtime-config-json", help="optional additive runtime.* defaults JSON file")
    release.add_argument("--validation-command", required=True, help="argv JSON array; executed without a shell")
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
    archive = commands.add_parser("issue-archive"); archive.add_argument("--issue", required=True)
    archive.add_argument("--decision", choices=("accepted", "rejected"), required=True)
    archive.add_argument("--decided-by", required=True); archive.add_argument("--reason", required=True)
    archive.add_argument("--task", help="required for accepted issues; existing workspace task plan path")
    archive.set_defaults(func=archive_issue)
    args = parser.parse_args()
    try:
        args.func(args)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
