#!/usr/bin/env python3
"""Validate the experimental inspect-only MPA Runtime reference contract."""

import argparse
import json
import re
import sys
from pathlib import Path


EXIT_VERSION = 20
EXIT_SCHEMA = 21
EXIT_REFERENCE = 22
EXIT_DRIFT = 23
PROFILE = "mpa-toml-v1"
CONTRACT_FILE = Path("contracts/agent_reference.toml")
KEY = re.compile(r"^[a-z][a-z0-9_]*$")
SCALAR = re.compile(r"^(?:0|[1-9][0-9]*)$")
ANCHOR = re.compile(r"^[a-z][a-z0-9-]*$")
MARKER = re.compile(r"<!-- mpa-contract:([a-z][a-z0-9_.]*)=([^\n]*) -->")
LIFECYCLE_BASELINES = {
    "major": {
        "state_ids": ["designing", "design_complete", "implementing", "verifying", "testing", "review_complete", "completion_approved", "done"],
        "labels_ko": ["설계 중", "설계 완료", "구현 중", "검증 중", "테스트 중", "검토 완료", "완료 승인", "done"],
        "transitions": ["designing>design_complete", "design_complete>implementing", "implementing>verifying", "verifying>testing", "testing>review_complete", "review_complete>completion_approved", "completion_approved>done"],
    },
    "minor": {
        "state_ids": ["drafting", "implementing", "completion_approved", "done"],
        "labels_ko": ["작성 중", "구현 중", "완료 승인", "done"],
        "transitions": ["drafting>implementing", "implementing>completion_approved", "completion_approved>done"],
    },
}
REFERENCE_BASELINES = {
    "entry.agent_rules": ("markdown_file", "core/agent_rules.md", "agent-behavior-rules"),
    "entry.user_burden_minimization": ("markdown_section", "core/agent_rules.md", "user-burden-minimization"),
    "entry.agent_rules_detail": ("markdown_file", "core/agent_rules_detail.md", "agent-rules-detail"),
}
PATH_BASELINES = {
    "tasks_root": "workspace/tasks",
    "docs_root": "docs",
}


class ContractError(Exception):
    def __init__(self, code, message, field_id="contract", path="contracts/agent_reference.toml"):
        super().__init__(message)
        self.code = code
        self.field_id = field_id
        self.path = path


def _parse_string(value, line):
    if "\\/" in value:
        raise ContractError(EXIT_SCHEMA, f"non-TOML escape at line {line}")
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as error:
        raise ContractError(EXIT_SCHEMA, f"invalid quoted string at line {line}") from error
    if not isinstance(parsed, str) or "\n" in parsed or "\r" in parsed or any(0xD800 <= ord(char) <= 0xDFFF for char in parsed):
        raise ContractError(EXIT_SCHEMA, f"invalid string at line {line}")
    return parsed


def _parse_value(value, line):
    if value.startswith('"'):
        return _parse_string(value, line)
    if SCALAR.fullmatch(value):
        return int(value)
    if value.startswith("[") and value.endswith("]"):
        if "\\/" in value:
            raise ContractError(EXIT_SCHEMA, f"non-TOML escape at line {line}")
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as error:
            raise ContractError(EXIT_SCHEMA, f"invalid string array at line {line}") from error
        if not isinstance(parsed, list) or not all(isinstance(item, str) and "\n" not in item and "\r" not in item for item in parsed):
            raise ContractError(EXIT_SCHEMA, f"array must contain strings at line {line}")
        return parsed
    raise ContractError(EXIT_SCHEMA, f"unsupported value at line {line}")


def parse_profile(text):
    if text.startswith("\ufeff"):
        raise ContractError(EXIT_SCHEMA, "UTF-8 BOM is not allowed")
    result = {"contract": {}, "paths": {}, "lifecycle": [], "references": []}
    current = None
    seen_single = set()
    for number, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "#" in line:
            raise ContractError(EXIT_SCHEMA, f"inline comments are not allowed at line {number}")
        array_match = re.fullmatch(r"\[\[([a-z][a-z0-9_]*)\]\]", line)
        table_match = re.fullmatch(r"\[([a-z][a-z0-9_]*)\]", line)
        if array_match:
            name = array_match.group(1)
            if name not in {"lifecycle", "references"}:
                raise ContractError(EXIT_SCHEMA, f"unsupported array table at line {number}")
            current = {}
            result[name].append(current)
            continue
        if table_match:
            name = table_match.group(1)
            if name not in {"contract", "paths"} or name in seen_single:
                raise ContractError(EXIT_SCHEMA, f"unsupported or duplicate table at line {number}")
            current = result[name]
            seen_single.add(name)
            continue
        if current is None:
            raise ContractError(EXIT_SCHEMA, f"value before table at line {number}")
        match = re.fullmatch(r"([a-z][a-z0-9_]*)\s*=\s*(.+)", line)
        if not match:
            raise ContractError(EXIT_SCHEMA, f"invalid key at line {number}")
        key, raw_value = match.groups()
        if key in current:
            raise ContractError(EXIT_SCHEMA, f"duplicate key at line {number}")
        current[key] = _parse_value(raw_value, number)
    if seen_single != {"contract", "paths"}:
        raise ContractError(EXIT_SCHEMA, "contract and paths tables are required")
    return result


def _ensure_exact(table, expected, field_id):
    actual = set(table)
    if actual != expected:
        missing = sorted(expected - actual)
        unknown = sorted(actual - expected)
        detail = "missing keys: " + ", ".join(missing) if missing else "unknown keys: " + ", ".join(unknown)
        raise ContractError(EXIT_SCHEMA, detail, field_id)


def _relative(value, field_id):
    if not isinstance(value, str):
        raise ContractError(EXIT_SCHEMA, "path must be a string", field_id)
    path = Path(value)
    if not value or path.is_absolute() or ".." in path.parts:
        raise ContractError(EXIT_REFERENCE, "path must stay relative", field_id, value)
    return path


def _safe_runtime_file(runtime_root, relative, field_id):
    relative = _relative(str(relative), field_id)
    candidate = runtime_root / relative
    try:
        candidate.resolve().relative_to(runtime_root.resolve())
    except ValueError as error:
        raise ContractError(EXIT_REFERENCE, "path escapes Runtime root", field_id, relative.as_posix()) from error
    current = runtime_root
    if current.is_symlink():
        raise ContractError(EXIT_REFERENCE, "Runtime root cannot be a symlink", field_id, str(runtime_root))
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ContractError(EXIT_REFERENCE, "symlink references are not allowed", field_id, relative.as_posix())
    if not candidate.is_file():
        raise ContractError(EXIT_REFERENCE, "referenced file is missing", field_id, relative.as_posix())
    return candidate


def _markers(path):
    try:
        matches = MARKER.findall(path.read_text(encoding="utf-8"))
    except (UnicodeError, OSError) as error:
        raise ContractError(EXIT_REFERENCE, "cannot read Markdown owner", path=str(path)) from error
    markers = {}
    for field_id, value in matches:
        if field_id in markers:
            raise ContractError(EXIT_DRIFT, "duplicate Markdown binding marker", field_id, str(path))
        markers[field_id] = value
    return markers


def _lifecycle_binding(item):
    pairs = ";".join(f"{state}|{label}" for state, label in zip(item["state_ids"], item["labels_ko"]))
    return f"{pairs};transitions={'|'.join(item['transitions'])}"


def validate(runtime_root):
    runtime_root = Path(runtime_root)
    if runtime_root.is_symlink() or not runtime_root.is_dir():
        raise ContractError(EXIT_REFERENCE, "Runtime root is missing or a symlink", path=str(runtime_root))
    contract_path = _safe_runtime_file(runtime_root, CONTRACT_FILE, "contract")
    try:
        data = parse_profile(contract_path.read_text(encoding="utf-8"))
    except (UnicodeError, OSError) as error:
        raise ContractError(EXIT_SCHEMA, "cannot read contract", path=str(contract_path)) from error
    contract = data["contract"]
    _ensure_exact(contract, {"protocol", "contract_version", "profile", "maturity", "usage", "authority", "discovery_path"}, "contract")
    if contract["protocol"] != "mpa-agent-reference" or contract["contract_version"] != 1:
        raise ContractError(EXIT_VERSION, "unsupported protocol or contract version")
    if contract["profile"] != PROFILE or contract["maturity"] != "experimental" or contract["usage"] != "inspect-only" or contract["authority"] != "not-invokable":
        raise ContractError(EXIT_SCHEMA, "invalid V1 contract metadata")
    if contract["discovery_path"] != ".mpa/runtime/contracts/agent_reference.toml":
        raise ContractError(EXIT_SCHEMA, "invalid discovery path")

    paths = data["paths"]
    _ensure_exact(paths, set(PATH_BASELINES), "paths")
    rules = _safe_runtime_file(runtime_root, "core/agent_rules.md", "entry.agent_rules")
    bindings = _markers(rules)
    for key, value in paths.items():
        _relative(value, f"paths.{key}")
        field_id = f"paths.{key}"
        if value != PATH_BASELINES[key]:
            raise ContractError(EXIT_VERSION, "path change requires a new contract version", field_id)
        if bindings.get(field_id) != value:
            raise ContractError(EXIT_DRIFT, "path binding differs from contract", field_id, "core/agent_rules.md")

    lifecycle_keys = {"field_id", "track", "owner_path", "owner_anchor", "usage", "authority", "state_ids", "labels_ko", "transitions"}
    if {item.get("track") for item in data["lifecycle"]} != {"major", "minor"} or len(data["lifecycle"]) != 2:
        raise ContractError(EXIT_SCHEMA, "exactly major and minor lifecycle tables are required", "lifecycle")
    for item in data["lifecycle"]:
        _ensure_exact(item, lifecycle_keys, item.get("field_id", "lifecycle"))
        field_id = item["field_id"]
        if not isinstance(field_id, str) or not isinstance(item["track"], str) or field_id != f"lifecycle.{item['track']}" or item["usage"] != "inspect-only" or item["authority"] != "not-invokable":
            raise ContractError(EXIT_SCHEMA, "invalid lifecycle identity or usage", field_id)
        if not all(isinstance(item[key], list) and all(isinstance(value, str) for value in item[key]) for key in ("state_ids", "labels_ko", "transitions")):
            raise ContractError(EXIT_SCHEMA, "invalid lifecycle value type", field_id)
        if len(item["state_ids"]) != len(item["labels_ko"]) or not item["state_ids"] or len(set(item["state_ids"])) != len(item["state_ids"]):
            raise ContractError(EXIT_SCHEMA, "invalid lifecycle state mapping", field_id)
        if not all(re.fullmatch(r"[a-z][a-z0-9_]*", state) for state in item["state_ids"]):
            raise ContractError(EXIT_SCHEMA, "invalid lifecycle state id", field_id)
        if {key: item[key] for key in ("state_ids", "labels_ko", "transitions")} != LIFECYCLE_BASELINES[item["track"]]:
            raise ContractError(EXIT_VERSION, "lifecycle change requires a new contract version", field_id)
        owner = _safe_runtime_file(runtime_root, item["owner_path"], field_id)
        if not ANCHOR.fullmatch(item["owner_anchor"]):
            raise ContractError(EXIT_REFERENCE, "invalid lifecycle owner anchor", field_id, item["owner_path"])
        if f'<a id="' + item["owner_anchor"] + '"></a>' not in owner.read_text(encoding="utf-8"):
            raise ContractError(EXIT_REFERENCE, "lifecycle owner anchor is missing", field_id, item["owner_path"])
        if _markers(owner).get(field_id) != _lifecycle_binding(item):
            raise ContractError(EXIT_DRIFT, "lifecycle binding differs from contract", field_id, item["owner_path"])

    reference_keys = {"field_id", "owner_kind", "owner_path", "owner_anchor", "usage", "authority"}
    if not data["references"]:
        raise ContractError(EXIT_SCHEMA, "at least one reference is required", "references")
    known_ids = set()
    for item in data["references"]:
        _ensure_exact(item, reference_keys, item.get("field_id", "references"))
        field_id = item["field_id"]
        if not isinstance(field_id, str) or field_id in known_ids or item["usage"] != "inspect-only" or item["authority"] != "not-invokable" or item["owner_kind"] not in {"markdown_file", "markdown_section"}:
            raise ContractError(EXIT_SCHEMA, "invalid reference identity, kind, or usage", field_id)
        known_ids.add(field_id)
        owner = _safe_runtime_file(runtime_root, item["owner_path"], field_id)
        if owner.suffix != ".md" or not ANCHOR.fullmatch(item["owner_anchor"]):
            raise ContractError(EXIT_REFERENCE, "invalid Markdown reference", field_id, item["owner_path"])
        if f'<a id="' + item["owner_anchor"] + '"></a>' not in owner.read_text(encoding="utf-8"):
            raise ContractError(EXIT_REFERENCE, "reference anchor is missing", field_id, item["owner_path"])
        if REFERENCE_BASELINES.get(field_id) != (item["owner_kind"], item["owner_path"], item["owner_anchor"]):
            raise ContractError(EXIT_VERSION, "reference change requires a new contract version", field_id)
    if known_ids != set(REFERENCE_BASELINES):
        raise ContractError(EXIT_VERSION, "reference set change requires a new contract version", "references")
    return {"contract_version": 1, "profile": PROFILE, "references": len(data["references"])}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate an MPA inspect-only reference contract.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--runtime-root", type=Path, help="Runtime directory to validate")
    group.add_argument("--project-root", type=Path, help="Installed project root used for contract discovery")
    args = parser.parse_args(argv)
    runtime_root = args.runtime_root or ((args.project_root / ".mpa/runtime") if args.project_root else Path(__file__).resolve().parents[1])
    try:
        report = validate(runtime_root)
    except ContractError as error:
        print(json.dumps({"code": error.code, "field_id": error.field_id, "path": error.path, "message": str(error)}, ensure_ascii=False))
        return error.code
    except (UnicodeError, OSError, TypeError, ValueError) as error:
        print(json.dumps({"code": EXIT_SCHEMA, "field_id": "contract", "path": str(runtime_root), "message": f"invalid contract input: {error}"}, ensure_ascii=False))
        return EXIT_SCHEMA
    print(json.dumps({"code": 0, "runtime_root": str(Path(runtime_root)), **report}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
