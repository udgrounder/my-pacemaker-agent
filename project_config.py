#!/usr/bin/env python3
"""Installation-local project configuration initializer and audit.

The file managed here is deliberately outside ``.mpa-workspace``.  Runtime
releases may replace the latter, but must never replace this installation's
project identity or local path metadata.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import tempfile
from pathlib import Path


CONFIG_RELATIVE = ".mpa-project/config.yaml"
CONFIG_SCHEMA_VERSION = 1
REQUIRED_PROJECT_FIELDS = ("name", "root_path", "initialized_at")
FIELD_LABELS = {
    "name": "project name",
    "root_path": "absolute project root path",
    "initialized_at": "initialization timestamp",
}
TOP_LEVEL_SCHEMA = re.compile(r"^schema_version:\s*(\d+)\s*(?:#.*)?$")
TOP_LEVEL_SCHEMA_KEY = re.compile(r"^schema_version\s*:")
TOP_LEVEL_KEY = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*:")
PROJECT_FIELD = re.compile(r"^  ([A-Za-z_][A-Za-z0-9_-]*):(?:\s|$)")


def config_path(project_root: Path) -> Path:
    return project_root.resolve() / CONFIG_RELATIVE


def _quoted(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def _default_values(project_root: Path) -> dict[str, str]:
    root = project_root.resolve()
    timestamp = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return {
        "name": root.name or "project",
        "root_path": str(root),
        "initialized_at": timestamp,
    }


def _read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines(keepends=True)


def _schema_version(lines: list[str]) -> tuple[int | None, bool]:
    for line in lines:
        stripped = line.rstrip("\r\n")
        match = TOP_LEVEL_SCHEMA.fullmatch(stripped)
        if match:
            return int(match.group(1)), True
        if TOP_LEVEL_SCHEMA_KEY.match(stripped):
            return None, True
        if stripped and not stripped.lstrip().startswith("#") and TOP_LEVEL_KEY.match(stripped):
            # schema_version is required at the top level, but a later key
            # means it is absent rather than accidentally nested.
            continue
    return None, False


def _project_field_lines(lines: list[str]) -> tuple[int | None, int | None, dict[str, int]]:
    project_start = None
    project_end = None
    fields: dict[str, int] = {}
    for index, line in enumerate(lines):
        stripped = line.rstrip("\r\n")
        if stripped == "project:":
            if project_start is None:
                project_start = index
            continue
        if project_start is None:
            continue
        if stripped and not stripped.startswith((" ", "\t", "#")):
            project_end = index
            break
        match = PROJECT_FIELD.match(stripped)
        if match and match.group(1) not in fields:
            fields[match.group(1)] = index
    if project_start is not None and project_end is None:
        project_end = len(lines)
    return project_start, project_end, fields


def _known_values(lines: list[str]) -> dict[str, str]:
    _, _, fields = _project_field_lines(lines)
    values: dict[str, str] = {}
    for field, index in fields.items():
        line = lines[index].rstrip("\r\n")
        _, raw = line.split(":", 1)
        value = raw.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            try:
                value = json.loads(value) if value[0] == '"' else value[1:-1]
            except json.JSONDecodeError:
                value = value[1:-1]
        values[field] = value
    return values


def _semantic_checksum(lines: list[str]) -> str:
    """Hash stable non-path project identity, never the absolute root path."""
    values = _known_values(lines)
    payload = {
        "schema_version": CONFIG_SCHEMA_VERSION,
        "project": {field: values.get(field, "") for field in ("name", "initialized_at")},
    }
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _insert_missing(lines: list[str], project_root: Path) -> tuple[list[str], list[str]]:
    values = _default_values(project_root)
    missing: list[str] = []
    schema, schema_present = _schema_version(lines)
    if schema_present and schema is None:
        return lines, ["invalid schema_version"]
    if schema is not None and schema > CONFIG_SCHEMA_VERSION:
        return lines, [f"unsupported future schema_version: {schema}"]
    if schema is not None and schema != CONFIG_SCHEMA_VERSION:
        return lines, [f"unsupported schema_version: {schema}"]

    result = list(lines)
    if not schema_present:
        result.insert(0, f"schema_version: {CONFIG_SCHEMA_VERSION}\n")
        missing.append("schema_version")

    project_start, project_end, fields = _project_field_lines(result)
    additions = [
        f"  {field}: {_quoted(values[field])}\n"
        for field in REQUIRED_PROJECT_FIELDS
        if field not in fields
    ]
    missing.extend(REQUIRED_PROJECT_FIELDS[index] for index, field in enumerate(REQUIRED_PROJECT_FIELDS) if field not in fields)
    if project_start is None:
        if result and not result[-1].endswith("\n"):
            result[-1] += "\n"
        if result and result[-1].strip():
            result.append("\n")
        result.extend(["project:\n", *additions])
    elif additions:
        assert project_end is not None
        result[project_end:project_end] = additions
    return result, missing


def inspect_project_config(project_root: Path) -> dict[str, object]:
    """Return a non-mutating plan for config initialization or additive update."""
    root = project_root.resolve()
    path = config_path(root)
    if not path.exists():
        return {
            "path": CONFIG_RELATIVE,
            "status": "create",
            "add": ["schema_version", *REQUIRED_PROJECT_FIELDS],
            "warnings": [],
        }
    try:
        lines = _read_lines(path)
    except OSError as error:
        return {"path": CONFIG_RELATIVE, "status": "warning", "add": [], "warnings": [str(error)]}
    schema, schema_present = _schema_version(lines)
    if schema_present and schema is None:
        return {
            "path": CONFIG_RELATIVE,
            "status": "warning",
            "add": [],
            "warnings": ["invalid schema_version"],
        }
    if schema_present and schema != CONFIG_SCHEMA_VERSION:
        return {
            "path": CONFIG_RELATIVE,
            "status": "warning",
            "add": [],
            "warnings": [f"unsupported schema_version: {schema}"],
        }
    _, _, fields = _project_field_lines(lines)
    add = ([] if schema_present else ["schema_version"]) + [
        field for field in REQUIRED_PROJECT_FIELDS if field not in fields
    ]
    return {
        "path": CONFIG_RELATIVE,
        "status": "update" if add else "unchanged",
        "add": add,
        "warnings": [],
        "semantic_checksum": _semantic_checksum(lines),
    }


def _atomic_write(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        stream.writelines(lines)
        stream.flush()
    try:
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def ensure_project_config(project_root: Path, *, write: bool = True) -> dict[str, object]:
    """Create or add missing config fields while preserving existing content."""
    root = project_root.resolve()
    path = config_path(root)
    plan = inspect_project_config(root)
    if not write or plan["status"] in {"unchanged", "warning"}:
        return plan
    if not path.exists():
        values = _default_values(root)
        lines = [
            f"schema_version: {CONFIG_SCHEMA_VERSION}\n",
            "project:\n",
            f"  name: {_quoted(values['name'])}\n",
            f"  root_path: {_quoted(values['root_path'])}\n",
            f"  initialized_at: {_quoted(values['initialized_at'])}\n",
        ]
        _atomic_write(path, lines)
        return {**plan, "status": "created", "semantic_checksum": _semantic_checksum(lines)}
    original = _read_lines(path)
    updated, added = _insert_missing(original, root)
    if not added:
        return {**plan, "status": "unchanged"}
    _atomic_write(path, updated)
    return {
        **plan,
        "status": "updated",
        "add": added,
        "semantic_checksum": _semantic_checksum(updated),
    }


def audit_project_config(project_root: Path) -> dict[str, object]:
    """Audit local config without changing it; findings are warning-level."""
    root = project_root.resolve()
    path = config_path(root)
    result = inspect_project_config(root)
    findings = list(result.get("warnings", []))
    if path.is_file():
        lines = _read_lines(path)
        values = _known_values(lines)
        if values.get("root_path", "").startswith("/") and str(root) != values["root_path"].strip('"\''):
            findings.append("project root differs from configured root_path")
        for field in REQUIRED_PROJECT_FIELDS:
            if field in values and not values[field].strip():
                findings.append(f"project.{field} is empty (preserved)")
        text = path.read_text(encoding="utf-8")
        if re.search(r"(?i)(api[_-]?key|secret|password|token)\s*:", text):
            findings.append("credential-like field found (preserved)")
        result["semantic_checksum"] = _semantic_checksum(lines)
    result["findings"] = findings
    result["status"] = "warning" if findings else result["status"]
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="MPA installation-local project config tools")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("ensure", "audit"):
        sub = subparsers.add_parser(name)
        sub.add_argument("--project", required=True)
        sub.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = Path(args.project).resolve()
    result = ensure_project_config(root) if args.command == "ensure" else audit_project_config(root)
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
