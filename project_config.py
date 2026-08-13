#!/usr/bin/env python3
"""Installation-local project configuration initializer and audit.

The file managed here is deliberately outside ``.mpa-workspace``. Runtime
releases may replace the latter and may apply explicitly declared additive
``runtime.*`` defaults, but must never replace this installation's project
identity or user-owned local values.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
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
MAPPING_LINE = re.compile(r"^(?P<indent> *)(?P<key>[A-Za-z_][A-Za-z0-9_-]*):(?:\s*(?P<value>.*))?(?:\r?\n)?$")
MIGRATION_KEY = re.compile(r"^runtime(?:\.[A-Za-z_][A-Za-z0-9_-]*)+$")
MIGRATION_SECRET = re.compile(r"(?i)(api[_-]?key|secret|password|token)\s*[:=]")
MIGRATION_ABSOLUTE_PATH = re.compile(r"(?<![\w.-])/(?:Users|home|var|private|tmp|etc)/")
PROJECT_REFERENCE = re.compile(r"^\$\{project\.(name|root_path|initialized_at)\}$")
MIGRATION_SECRET_KEY = re.compile(r"(?i)(api[_-]?key|secret|password|token)")


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
    if path.is_symlink():
        return {"status": "warning", "schema_version": normalized["schema_version"], "add": [],
                "skipped": [], "warnings": ["config.yaml symlink is not supported for migration"]}
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


def _migration_scalar(value: object) -> str:
    """Serialize one safe JSON scalar as a YAML scalar."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, str):
        return _quoted(value)
    raise ValueError("runtime config migration values must be scalar")


def _resolve_project_reference(value: object, lines: list[str]) -> object:
    if not isinstance(value, str):
        return value
    reference = PROJECT_REFERENCE.fullmatch(value)
    if not reference:
        return value
    known = _known_values(lines)
    return known.get(reference.group(1), value)


def validate_runtime_config_migration(migration: object) -> dict[str, object] | None:
    """Validate release-provided, additive-only Runtime config defaults.

    The migration is deliberately limited to ``runtime.*`` paths.  This keeps
    project identity and user-owned config fields outside the release's write
    authority while still allowing a Runtime release to introduce defaults.
    """
    if migration is None:
        return None
    if not isinstance(migration, dict):
        raise ValueError("runtime config migration must be an object")
    schema_version = migration.get("schema_version")
    additions = migration.get("additive_defaults")
    if not isinstance(schema_version, int) or isinstance(schema_version, bool) or schema_version < 1:
        raise ValueError("runtime config migration schema_version must be a positive integer")
    if not isinstance(additions, dict):
        raise ValueError("runtime config migration additive_defaults must be an object")
    normalized: dict[str, object] = {}
    for path, value in additions.items():
        if not isinstance(path, str) or not MIGRATION_KEY.fullmatch(path):
            raise ValueError("runtime config migration paths must use runtime.<name>[.<name>...]")
        if MIGRATION_SECRET_KEY.search(path):
            raise ValueError(f"runtime config migration cannot declare credential-like key: {path}")
        if isinstance(value, (dict, list, tuple, set)):
            raise ValueError(f"runtime config migration value must be scalar: {path}")
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError(f"runtime config migration value must be finite: {path}")
        if isinstance(value, str) and (MIGRATION_SECRET.search(value) or MIGRATION_ABSOLUTE_PATH.search(value)):
            raise ValueError(f"runtime config migration contains sensitive/path-like value: {path}")
        _migration_scalar(value)
        normalized[path] = value
    return {"schema_version": schema_version, "additive_defaults": normalized}


def _mapping_paths(lines: list[str]) -> dict[str, tuple[int, int, bool]]:
    """Return YAML mapping paths for the intentionally small config format."""
    stack: list[tuple[int, str]] = []
    result: dict[str, tuple[int, int, bool]] = {}
    for index, line in enumerate(lines):
        raw = line.rstrip("\r\n")
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        match = MAPPING_LINE.fullmatch(raw)
        if not match:
            continue
        indent = len(match.group("indent"))
        while stack and stack[-1][0] >= indent:
            stack.pop()
        key = match.group("key")
        path = ".".join([item[1] for item in stack] + [key])
        value = match.group("value")
        result[path] = (index, indent, bool(value and not value.startswith("#")))
        stack.append((indent, key))
    return result


def _section_end(lines: list[str], start: int, indent: int) -> int:
    for index in range(start + 1, len(lines)):
        raw = lines[index].rstrip("\r\n")
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        current_indent = len(raw) - len(raw.lstrip(" "))
        if current_indent <= indent:
            return index
    return len(lines)


def _insert_runtime_path(lines: list[str], path: str, value: object) -> list[str]:
    """Insert one missing scalar path while preserving existing lines."""
    parts = path.split(".")
    mappings = _mapping_paths(lines)
    for prefix, (_, _, has_value) in mappings.items():
        if path.startswith(prefix + ".") and prefix == ".".join(parts[:len(prefix.split("."))]):
            # A scalar where a mapping parent is required is ambiguous and
            # should be surfaced instead of producing malformed YAML.
            if has_value and len(prefix.split(".")) < len(parts):
                raise ValueError(f"runtime config migration conflicts with scalar path: {prefix}")
    if path in mappings:
        return lines

    # Insert below the deepest existing mapping parent.  This avoids creating
    # a duplicate top-level ``runtime`` block when only a nested key is new.
    for depth in range(len(parts) - 1, 0, -1):
        parent_path = ".".join(parts[:depth])
        parent = mappings.get(parent_path)
        if parent is None:
            continue
        parent_index, parent_indent, parent_has_value = parent
        if parent_has_value:
            raise ValueError(f"runtime config migration conflicts with scalar path: {parent_path}")
        insertion = _section_end(lines, parent_index, parent_indent)
        additions = []
        for offset, part in enumerate(parts[depth:-1]):
            additions.append(" " * (parent_indent + 2 * (offset + 1)) + f"{part}:\n")
        additions.append(" " * (parent_indent + 2 * (len(parts) - depth)) + f"{parts[-1]}: {_migration_scalar(value)}\n")
        return lines[:insertion] + additions + lines[insertion:]

    # Build missing mapping parents at the end of the document.  Existing
    # paths are handled above, so this creates a single unambiguous subtree.
    result = list(lines)
    if result and not result[-1].endswith("\n"):
        result[-1] += "\n"
    if result and result[-1].strip():
        result.append("\n")
    for depth, part in enumerate(parts[:-1]):
        result.append("  " * depth + f"{part}:\n")
    result.append("  " * (len(parts) - 1) + f"{parts[-1]}: {_migration_scalar(value)}\n")
    return result


def preview_runtime_config_migration(project_root: Path, migration: object) -> dict[str, object]:
    """Return an additive migration plan without modifying the project."""
    normalized = validate_runtime_config_migration(migration)
    if normalized is None:
        return {"status": "none", "schema_version": None, "add": [], "skipped": []}
    root = project_root.resolve()
    path = config_path(root)
    if path.is_symlink():
        raise ValueError("runtime config migration does not follow config.yaml symlinks")
    if not path.exists():
        base = [
            f"schema_version: {CONFIG_SCHEMA_VERSION}\n",
            "project:\n",
            f"  name: {_quoted(_default_values(root)['name'])}\n",
            f"  root_path: {_quoted(_default_values(root)['root_path'])}\n",
            f"  initialized_at: {_quoted(_default_values(root)['initialized_at'])}\n",
        ]
    else:
        base = _read_lines(path)
    schema, schema_present = _schema_version(base)
    if schema_present and schema != CONFIG_SCHEMA_VERSION:
        return {"status": "warning", "schema_version": normalized["schema_version"], "add": [],
                "skipped": [], "warnings": ["unsupported schema_version"]}
    mappings = _mapping_paths(base)
    additions = normalized["additive_defaults"]
    add = [key for key in additions if key not in mappings]
    skipped = [key for key in additions if key in mappings]
    return {"status": "update" if add else "unchanged", "schema_version": normalized["schema_version"],
            "add": add, "skipped": skipped, "warnings": []}


def apply_runtime_config_migration(project_root: Path, migration: object, *, write: bool = True) -> dict[str, object]:
    """Apply only missing ``runtime.*`` values; never overwrite existing values."""
    normalized = validate_runtime_config_migration(migration)
    if normalized is None:
        return {"status": "none", "schema_version": None, "add": [], "skipped": []}
    root = project_root.resolve()
    path = config_path(root)
    if path.is_symlink():
        raise ValueError("runtime config migration does not follow config.yaml symlinks")
    if not path.exists():
        ensure_project_config(root, write=write)
    original = _read_lines(path)
    schema, schema_present = _schema_version(original)
    if schema_present and schema != CONFIG_SCHEMA_VERSION:
        raise ValueError("runtime config migration requires a supported schema_version")
    result = list(original)
    added: list[str] = []
    skipped: list[str] = []
    for key, value in normalized["additive_defaults"].items():
        before = _mapping_paths(result)
        if key in before:
            skipped.append(key)
            continue
        result = _insert_runtime_path(result, key, _resolve_project_reference(value, result))
        added.append(key)
    if write and result != original:
        _atomic_write(path, result)
    return {"status": "updated" if added else "unchanged", "schema_version": normalized["schema_version"],
            "add": added, "skipped": skipped, "semantic_checksum": _semantic_checksum(result)}


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
