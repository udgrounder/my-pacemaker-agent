#!/usr/bin/env python3
"""Source-only release, deployment, rollback, and issue collection tools."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import shlex
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
        if path.name not in IGNORED_RUNTIME_NAMES and path.is_file()
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


def release_id(assets: dict[str, str]) -> str:
    payload = json.dumps(assets, sort_keys=True, separators=(",", ":")).encode()
    return "mpa-" + hashlib.sha256(payload).hexdigest()[:16]


def require_safe_ref(value: str, field: str) -> str:
    if not SAFE_REF.fullmatch(value):
        raise ValueError(f"{field} must be lowercase safe text")
    return value


def sync_runtime(_: argparse.Namespace) -> None:
    replace_tree(RUNTIME_SOURCE, RUNTIME_DIST)
    print(f"synced runtime: {RUNTIME_SOURCE} -> {RUNTIME_DIST}")


def run_validation(command: list[str]) -> dict:
    if not command:
        raise ValueError("validation-command is required")
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    record = {"command": command, "exit_code": result.returncode,
              "stdout": result.stdout[-4000:], "stderr": result.stderr[-4000:], "executed_at": now()}
    if result.returncode:
        raise ValueError(f"validation command failed: {record}")
    return record


def prepare_release(args: argparse.Namespace) -> None:
    validation_command = args.validation_command
    validation = run_validation(shlex.split(validation_command) if isinstance(validation_command, str) else validation_command)
    metadata = {field: getattr(args, field) for field in RELEASE_METADATA}
    if any(not value.strip() for value in metadata.values()):
        raise ValueError("release metadata fields must not be empty")
    assets = asset_map(RUNTIME_DIST)
    ident = release_id(assets)
    manifest_path = MANIFESTS / f"{ident}.json"
    package_path = PACKAGES / ident
    if manifest_path.exists() != package_path.exists():
        raise ValueError("release manifest and package must either both exist or both be absent")
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("assets") != assets or asset_map(package_path) != assets:
            raise ValueError("existing release ID does not match its immutable package")
    else:
        package_path.parent.mkdir(parents=True, exist_ok=True)
        staging = package_path.with_name(f".{package_path.name}.new-{uuid.uuid4().hex[:8]}")
        try:
            shutil.copytree(RUNTIME_DIST, staging, ignore=runtime_ignore)
            if asset_map(staging) != assets:
                raise ValueError("release package asset map changed while preparing")
            staging.replace(package_path)
        finally:
            if staging.exists():
                shutil.rmtree(staging)
        manifest = {
            "release_id": ident,
            "created_at": now(),
            "asset_root": "dist/.mpa-workspace",
            "package": relative_to_root(package_path),
            "assets": assets,
            "source_git": scoped_git(),
            "metadata": metadata,
        }
        write_json(manifest_path, manifest)
    receipt = {
        "release_id": ident,
        "manifest": relative_to_root(manifest_path),
        "created_at": now(),
        "verified_by": args.verified_by,
        "validation": validation,
    }
    write_json(RELEASE_RECEIPTS / f"{ident}-{receipt_suffix()}.json", receipt)
    print(ident)


def load_manifest(value: str) -> tuple[Path, dict]:
    path = Path(value)
    if not path.is_absolute():
        path = ROOT / path
    path = path.resolve()
    if MANIFESTS.resolve() not in path.parents:
        raise ValueError("manifest must be inside workspace/releases/manifests")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not data.get("release_id") or not isinstance(data.get("assets"), dict):
        raise ValueError("invalid release manifest")
    if data.get("package") != relative_to_root(PACKAGES / data["release_id"]):
        raise ValueError("manifest package path is invalid")
    if not isinstance(data.get("metadata"), dict) or any(not data["metadata"].get(field) for field in RELEASE_METADATA):
        raise ValueError("manifest release metadata is incomplete")
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
    for manifest_path in sorted(MANIFESTS.glob("*.json")):
        try:
            _, manifest = load_manifest(str(manifest_path))
            release_package(manifest)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            invalid.append(f"{manifest_path.name}: {error}")
    if invalid:
        raise ValueError("invalid release artifacts: " + "; ".join(invalid))
    print(f"release audit passed: {len(list(MANIFESTS.glob('*.json')))} manifest(s)")


def verify_target(target: Path, expected: dict[str, str]) -> None:
    if asset_map(target) != expected:
        raise ValueError("target runtime asset map does not match release manifest")


def deployment_dry_run(args: argparse.Namespace) -> None:
    target_ref = require_safe_ref(args.target_ref, "target-ref")
    manifest_path, manifest = load_manifest(args.manifest)
    release_package(manifest)
    root = Path(args.target).resolve()
    target = root / ".mpa-workspace"
    if not target.is_dir():
        raise ValueError("target .mpa-workspace is missing; use install.py for first installation")
    result = {"release_id": manifest["release_id"], "manifest": relative_to_root(manifest_path),
              "target": str(root), "target_ref": target_ref, "current_assets": asset_map(target),
              "release_assets": manifest["assets"], "created_at": now()}
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
    dry_run = (ROOT / args.dry_run).resolve()
    if DEPLOYMENT_RECEIPTS.resolve() not in dry_run.parents or not dry_run.is_file():
        raise ValueError("deploy requires a recorded deployment dry-run")
    dry_run_data = json.loads(dry_run.read_text(encoding="utf-8"))
    if dry_run_data.get("release_id") != manifest["release_id"] or dry_run_data.get("target") != str(root) or dry_run_data.get("target_ref") != target_ref:
        raise ValueError("dry-run does not match deployment inputs")
    backup = root / ".mpa-backups" / f"{manifest['release_id']}-{receipt_suffix()}"
    backup.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(target, backup)
    replacement = target.with_name(f".mpa-workspace.new-{uuid.uuid4().hex[:8]}")
    previous = target.with_name(f".mpa-workspace.previous-{uuid.uuid4().hex[:8]}")
    try:
        shutil.copytree(package, replacement, ignore=runtime_ignore)
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
        if previous.exists():
            shutil.rmtree(previous)
    finally:
        if replacement.exists():
            shutil.rmtree(replacement)
        if previous.exists() and target.exists():
            shutil.rmtree(previous)
    receipt = {
        "release_id": manifest["release_id"],
        "manifest": relative_to_root(manifest_path),
        "target": str(root),
        "backup": str(backup.relative_to(root)),
        "applied_at": now(),
        "verified_by": args.verified_by,
        "approved_by": args.approved_by, "approval_ref": args.approval_ref,
        "rollback_owner": args.rollback_owner, "dry_run": relative_to_root(dry_run),
    }
    write_json(DEPLOYMENT_RECEIPTS / target_ref / f"deploy-{manifest['release_id']}-{receipt_suffix()}.json", receipt)
    write_json(target / "history" / "releases" / f"{manifest['release_id']}.json", receipt)
    print(receipt["backup"])


def rollback(args: argparse.Namespace) -> None:
    target_ref = require_safe_ref(args.target_ref, "target-ref")
    root = Path(args.target).resolve()
    backups_root = (root / ".mpa-backups").resolve()
    backup = (root / args.backup).resolve()
    if backups_root not in backup.parents or not backup.is_dir():
        raise ValueError("backup must be inside target .mpa-backups")
    target = root / ".mpa-workspace"
    replacement = target.with_name(f".mpa-workspace.rollback-{uuid.uuid4().hex[:8]}")
    try:
        shutil.copytree(backup, replacement)
        if target.exists():
            shutil.rmtree(target)
        replacement.replace(target)
    finally:
        if replacement.exists():
            shutil.rmtree(replacement)
    receipt = {"target": str(root), "backup": str(backup.relative_to(root)), "rolled_back_at": now()}
    write_json(DEPLOYMENT_RECEIPTS / target_ref / f"rollback-{receipt_suffix()}.json", receipt)
    print("rolled back")


def issue_text(title: str, summary: str, kind: str) -> str:
    return ("---\n" + json.dumps({"type": "issue", "status": "open", "kind": kind,
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
    text = issue_text(args.title, args.summary, args.kind)
    check_issue_text(text)
    (folder / ident).write_text(text, encoding="utf-8")
    print(ident)


def collect_issue(args: argparse.Namespace) -> None:
    project_ref = require_safe_ref(args.project_ref, "project-ref")
    source = Path(args.project).resolve() / "workspace" / "issues" / args.issue
    if not source.is_file():
        raise ValueError("specified issue does not exist")
    text = source.read_text(encoding="utf-8")
    check_issue_text(text)
    destination = ISSUES / "inbox" / project_ref / source.name
    archived = list((ISSUES / "archived").rglob(source.name)) if (ISSUES / "archived").exists() else []
    if destination.exists() or archived:
        raise ValueError("issue already exists in inbox or archive")
    destination.parent.mkdir(parents=True, exist_ok=True)
    source.replace(destination)
    print(destination.relative_to(ROOT))


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
    return metadata, body


def write_issue(path: Path, metadata: dict, body: str) -> None:
    path.write_text("---\n" + json.dumps(metadata, ensure_ascii=False, indent=2) + "\n---\n" + body,
                    encoding="utf-8")


def issue_receipt(kind: str, issue: str, value: dict) -> None:
    write_json(ISSUE_RECEIPTS / kind / f"{receipt_suffix()}.json", {"issue": issue, "at": now(), **value})


def review_issue(args: argparse.Namespace) -> None:
    path, issue = inbox_issue(args.issue)
    read_issue(path)
    issue_receipt("reviews", issue, {"reviewed_by": args.reviewed_by, "decision": args.decision})
    print(issue)


def triage_issue(args: argparse.Namespace) -> None:
    path, issue = inbox_issue(args.issue)
    accepted = any(json.loads(item.read_text(encoding="utf-8")).get("issue") == issue and
                   json.loads(item.read_text(encoding="utf-8")).get("decision") == "accepted"
                   for item in (ISSUE_RECEIPTS / "reviews").glob("*.json"))
    if not accepted:
        raise ValueError("an accepted review receipt is required before triage")
    metadata, body = read_issue(path)
    metadata.update({"status": "triaged", "classification": args.classification, "triaged_at": now()})
    write_issue(path, metadata, body)
    issue_receipt("triages", issue, {"classification": args.classification, "triaged_by": args.triaged_by})
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
    metadata.update({"status": "resolved", "resolved_at": now(), "task": args.task,
                     "release": args.release, "deployment": relative_to_root(deployment),
                     "verification": args.verification})
    write_issue(path, metadata, body)
    issue_receipt("resolutions", issue, {"resolved_by": args.resolved_by, "release": args.release,
                                           "deployment": relative_to_root(deployment), "verification": args.verification})
    print(issue)


def archive_issue(args: argparse.Namespace) -> None:
    path, issue = inbox_issue(args.issue)
    metadata, _ = read_issue(path)
    if metadata.get("status") != "resolved" or not all(metadata.get(key) for key in ("release", "deployment", "verification")):
        raise ValueError("only resolved issues with release, deployment, and verification evidence may be archived")
    project_ref = issue.split("/", 1)[0]
    destination = ISSUES / "archived" / dt.datetime.now(dt.timezone.utc).strftime("%Y/%m") / project_ref / path.name
    if destination.exists():
        raise ValueError("archive destination already exists")
    destination.parent.mkdir(parents=True, exist_ok=True)
    path.replace(destination)
    issue_receipt("archives", issue, {"archive": str(destination.relative_to(ROOT)), "archived_by": args.archived_by})
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
    roll.add_argument("--target", required=True); roll.add_argument("--backup", required=True); roll.add_argument("--target-ref", required=True)
    roll.set_defaults(func=rollback)
    create = commands.add_parser("issue-create"); create.add_argument("--project", required=True); create.add_argument("--title", required=True); create.add_argument("--summary", required=True); create.add_argument("--kind", default="observation"); create.set_defaults(func=create_issue)
    collect = commands.add_parser("issue-collect"); collect.add_argument("--project", required=True); collect.add_argument("--project-ref", required=True); collect.add_argument("--issue", required=True); collect.set_defaults(func=collect_issue)
    review = commands.add_parser("issue-review"); review.add_argument("--issue", required=True); review.add_argument("--reviewed-by", required=True); review.add_argument("--decision", choices=("accepted", "rejected"), required=True); review.set_defaults(func=review_issue)
    triage = commands.add_parser("issue-triage"); triage.add_argument("--issue", required=True); triage.add_argument("--classification", required=True); triage.add_argument("--triaged-by", required=True); triage.set_defaults(func=triage_issue)
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
