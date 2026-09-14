"""Pure issue metadata parsing and machine-path normalization helpers."""

from __future__ import annotations

import json
import re
from collections.abc import Container
from pathlib import Path
from typing import Pattern


def parse_issue_candidate(
    text: str,
    *,
    type_marker_pattern: Pattern[str],
    methodology_type_marker: str,
    methodology_kind: str,
) -> tuple[str | None, dict | None, str]:
    """Classify raw issue metadata without normalizing or rewriting its body."""
    marker_values = {value.strip() for value in type_marker_pattern.findall(text)}
    if len(marker_values) > 1:
        raise ValueError("issue type markers conflict")
    marker = next(iter(marker_values), None)

    if not text.startswith("---\n"):
        if marker == methodology_type_marker:
            return methodology_kind, None, text
        if marker is None:
            return None, None, text
        return "project_asset", None, text

    try:
        raw_metadata, body = text[4:].split("\n---\n", 1)
        metadata = json.loads(raw_metadata)
    except (ValueError, json.JSONDecodeError) as error:
        raise ValueError("issue metadata is invalid") from error
    if not isinstance(metadata, dict) or metadata.get("type") != "issue":
        raise ValueError("issue metadata is invalid")
    kind = metadata.get("kind")
    if kind is not None and (not isinstance(kind, str) or not kind.strip()):
        raise ValueError("issue kind is invalid")
    kind = kind.strip() if isinstance(kind, str) else None
    if marker is not None:
        marker_is_methodology = marker == methodology_type_marker
        if marker_is_methodology != (kind == methodology_kind):
            raise ValueError("issue metadata and type marker conflict")
    return kind, metadata, body


def candidate_metadata_is_complete(metadata: dict | None) -> bool:
    if metadata is None:
        return True
    required = (
        "status", "canonical_key", "canonical_issue_key", "occurrence", "area",
        "observed_release", "collection_purpose", "source_issue_id", "workspace_issue_id",
    )
    return metadata.get("status") == "open" and all(
        isinstance(metadata.get(field), str) and metadata[field].strip()
        for field in required
    )


def normalize_machine_paths(
    text: str,
    project_root: Path,
    *,
    machine_absolute_path: Pattern[str],
) -> str:
    """Replace machine paths while preserving project-relative reproduction detail."""
    project_roots = {
        project_root.absolute().as_posix().rstrip("/"),
        project_root.resolve().as_posix().rstrip("/"),
    }
    for root in tuple(project_roots):
        if root.startswith("/private/var/"):
            project_roots.add(root.removeprefix("/private"))
        elif root.startswith("/var/"):
            project_roots.add(f"/private{root}")

    def replace(match: re.Match[str]) -> str:
        token = match.group(0)
        suffix = ""
        while token and token[-1] in ".,;:!?":
            suffix = token[-1] + suffix
            token = token[:-1]
        matching_root = next(
            (root for root in sorted(project_roots, key=len, reverse=True)
             if token == root or token.startswith(f"{root}/")),
            None,
        )
        if matching_root is not None:
            return f"<project-root>{token[len(matching_root):]}{suffix}"
        parts = [part for part in token.split("/") if part]
        safe_tail = parts[-2:] if len(parts) > 1 else parts
        replacement = "<redacted-path>"
        if safe_tail:
            replacement += "/" + "/".join(safe_tail)
        return replacement + suffix

    return machine_absolute_path.sub(replace, text)


def normalize_identity_paths(
    text: str,
    *,
    normalized_machine_path: Pattern[str],
    machine_absolute_path: Pattern[str],
    identity_path_anchors: Container[str],
) -> str:
    """Remove machine roots while retaining stable path detail for identity."""
    def stable_path(parts: list[str]) -> str:
        anchor = next(
            (index for index, part in enumerate(parts) if part in identity_path_anchors),
            None,
        )
        safe_parts = parts[anchor:] if anchor is not None else parts[-2:]
        return "<machine-path>" + ("/" + "/".join(safe_parts) if safe_parts else "")

    def replace_absolute(match: re.Match[str]) -> str:
        token = match.group(0)
        suffix = ""
        while token and token[-1] in ".,;:!?":
            suffix = token[-1] + suffix
            token = token[:-1]
        return stable_path([part for part in token.split("/") if part]) + suffix

    def replace_placeholder(match: re.Match[str]) -> str:
        token = match.group(0)
        prefix_end = token.find(">") + 1
        parts = [part for part in token[prefix_end:].split("/") if part]
        return stable_path(parts)

    return normalized_machine_path.sub(
        replace_placeholder, machine_absolute_path.sub(replace_absolute, text))


def metadata_identity(metadata: dict) -> dict[str, str]:
    return {
        key: str(metadata[key])
        for key in ("source_issue_id", "workspace_issue_id", "canonical_issue_key")
        if metadata.get(key)
    }
