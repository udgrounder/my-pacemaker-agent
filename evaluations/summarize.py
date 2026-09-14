#!/usr/bin/env python3
"""Validate and summarize local MPA effectiveness study records."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from statistics import median
from typing import Any, Dict, Iterable, List, Optional, Tuple


SCENARIOS = {
    "wording_edit", "configuration_edit", "bug_fix", "multi_step_feature", "session_resume", "intent_change",
}
CONDITIONS = {"mpa", "baseline"}
STATUSES = {"completed", "failed", "stopped"}
QUALITIES = {"accepted", "rejected", "unverified"}
EVENT_KINDS = {
    "user_intervention", "duplicate_intent_request", "blocking_wait", "correction", "defect", "rework",
}
NECESSITIES = {"necessary", "unnecessary", "unknown"}
MANIFEST_FIELDS = (
    "model", "model_version", "settings_ref", "tool_permissions", "source_ref", "request_ref", "time_limit_seconds",
)
UTC_TIMESTAMP_PATTERN = r"^(?:(?:(?:000[1-9]|00[1-9][0-9]|0[1-9][0-9]{2}|[1-9][0-9]{3})-(?:(?:01|03|05|07|08|10|12)-(?:0[1-9]|[12][0-9]|3[01])|(?:04|06|09|11)-(?:0[1-9]|[12][0-9]|30)|02-(?:0[1-9]|1[0-9]|2[0-8])))|(?:(?:[0-9]{2}(?:0[48]|[2468][048]|[13579][26])|(?:0[48]|[2468][048]|[13579][26])00)-02-29))T(?:[01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\.[0-9]+)?Z$"
UTC_TIMESTAMP_RE = re.compile(UTC_TIMESTAMP_PATTERN)
RUN_FIELDS = (
    "run_id", "scenario_id", "condition", "pair_id", "status", "quality", "started_at", "ended_at",
    "active_seconds", "user_wait_seconds", "token_count", "stop_reason", "resume_requested_at",
    "first_acceptance_action_at", "condition_manifest", "events",
)


class StudyValidationError(ValueError):
    pass


def _timestamp(value: Any, label: str) -> datetime:
    if not isinstance(value, str):
        raise StudyValidationError(f"{label} must be an ISO-8601 string")
    if not UTC_TIMESTAMP_RE.fullmatch(value):
        raise StudyValidationError(f"{label} must be a UTC ISO-8601 timestamp ending in Z")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise StudyValidationError(f"{label} is not ISO-8601") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise StudyValidationError(f"{label} must be a UTC ISO-8601 timestamp ending in Z")
    return parsed


def _optional_timestamp(value: Any, label: str) -> Optional[datetime]:
    if value is None:
        return None
    return _timestamp(value, label)


def _optional_nonnegative_int(value: Any, label: str) -> None:
    if value is not None and (isinstance(value, bool) or not isinstance(value, int) or value < 0):
        raise StudyValidationError(f"{label} must be a non-negative integer or null")


def _require_string(value: Any, label: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise StudyValidationError(f"{label} must be a non-empty string")


def validate_study(data: Any) -> Dict[str, Any]:
    if not isinstance(data, dict) or set(data) != {"schema_version", "study_id", "runs"}:
        raise StudyValidationError("study must contain only schema_version, study_id, and runs")
    if data["schema_version"] != 1:
        raise StudyValidationError("schema_version must be 1")
    _require_string(data["study_id"], "study_id")
    if not isinstance(data["runs"], list):
        raise StudyValidationError("runs must be an array")

    identifiers = set()
    paired: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for index, run in enumerate(data["runs"]):
        label = f"runs[{index}]"
        if not isinstance(run, dict):
            raise StudyValidationError(f"{label} must be an object")
        for field in RUN_FIELDS:
            if field not in run:
                raise StudyValidationError(f"{label}.{field} is required")
        if set(run) != set(RUN_FIELDS):
            raise StudyValidationError(f"{label} has invalid fields")
        _require_string(run["run_id"], f"{label}.run_id")
        if run["run_id"] in identifiers:
            raise StudyValidationError(f"duplicate run_id: {run['run_id']}")
        identifiers.add(run["run_id"])
        if run["scenario_id"] not in SCENARIOS:
            raise StudyValidationError(f"{label}.scenario_id is unknown")
        if run["condition"] not in CONDITIONS or run["status"] not in STATUSES or run["quality"] not in QUALITIES:
            raise StudyValidationError(f"{label} has an invalid condition, status, or quality")
        if run["pair_id"] is not None:
            _require_string(run["pair_id"], f"{label}.pair_id")
        if run["stop_reason"] is not None:
            _require_string(run["stop_reason"], f"{label}.stop_reason")
        if run["status"] == "stopped" and run["stop_reason"] is None:
            raise StudyValidationError(f"{label}.stop_reason is required for stopped runs")
        if run["status"] != "stopped" and run["stop_reason"] is not None:
            raise StudyValidationError(f"{label}.stop_reason is allowed only for stopped runs")
        started = _timestamp(run["started_at"], f"{label}.started_at")
        ended = _timestamp(run["ended_at"], f"{label}.ended_at")
        if ended < started:
            raise StudyValidationError(f"{label} has an end before its start")
        resume_requested = _optional_timestamp(run["resume_requested_at"], f"{label}.resume_requested_at")
        first_action = _optional_timestamp(run["first_acceptance_action_at"], f"{label}.first_acceptance_action_at")
        if run["scenario_id"] == "session_resume" and (resume_requested is None or first_action is None):
            raise StudyValidationError(f"{label} requires resume timestamps for session_resume")
        if run["scenario_id"] != "session_resume" and (resume_requested is not None or first_action is not None):
            raise StudyValidationError(f"{label} has resume timestamps outside session_resume")
        if resume_requested is not None and (resume_requested < started or resume_requested > ended):
            raise StudyValidationError(f"{label}.resume_requested_at is outside the run interval")
        if first_action is not None and (first_action < started or first_action > ended):
            raise StudyValidationError(f"{label}.first_acceptance_action_at is outside the run interval")
        if resume_requested is not None and first_action is not None and first_action < resume_requested:
            raise StudyValidationError(f"{label} has first acceptance action before resume request")
        for field in ("active_seconds", "user_wait_seconds", "token_count"):
            _optional_nonnegative_int(run.get(field), f"{label}.{field}")
        manifest = run["condition_manifest"]
        if not isinstance(manifest, dict) or set(manifest) != set(MANIFEST_FIELDS):
            raise StudyValidationError(f"{label}.condition_manifest has invalid fields")
        for field in MANIFEST_FIELDS[:-1]:
            _require_string(manifest[field], f"{label}.condition_manifest.{field}")
        _optional_nonnegative_int(manifest["time_limit_seconds"], f"{label}.condition_manifest.time_limit_seconds")
        if not isinstance(run["events"], list):
            raise StudyValidationError(f"{label}.events must be an array")
        for event_index, event in enumerate(run["events"]):
            if not isinstance(event, dict) or set(event) != {"kind", "at", "necessity"}:
                raise StudyValidationError(f"{label}.events[{event_index}] has invalid fields")
            if event["kind"] not in EVENT_KINDS or event["necessity"] not in NECESSITIES:
                raise StudyValidationError(f"{label}.events[{event_index}] has invalid values")
            at = _timestamp(event["at"], f"{label}.events[{event_index}].at")
            if at < started or at > ended:
                raise StudyValidationError(f"{label}.events[{event_index}] is outside the run interval")
        pair_id = run["pair_id"]
        if pair_id is not None:
            paired[pair_id].append(run)

    for pair_id, runs in paired.items():
        if len(runs) != 2 or {run["condition"] for run in runs} != CONDITIONS:
            raise StudyValidationError(f"pair_id {pair_id} must contain one mpa and one baseline run")
        first, second = runs
        if first["scenario_id"] != second["scenario_id"] or first["condition_manifest"] != second["condition_manifest"]:
            raise StudyValidationError(f"pair_id {pair_id} does not share scenario and condition manifest")
    return data


def _summary(values: Iterable[Optional[int]]) -> Dict[str, Optional[float]]:
    usable = [value for value in values if value is not None]
    if not usable:
        return {"count": 0, "median": None, "min": None, "max": None}
    return {"count": len(usable), "median": median(usable), "min": min(usable), "max": max(usable)}


def _event_summary(runs: Iterable[Dict[str, Any]]) -> Dict[str, Dict[str, int]]:
    events = [event for run in runs for event in run["events"]]
    return {
        "by_kind": dict(Counter(event["kind"] for event in events)),
        "by_necessity": dict(Counter(event["necessity"] for event in events)),
    }


def summarize(data: Dict[str, Any]) -> Dict[str, Any]:
    validate_study(data)
    by_condition: Dict[str, List[Dict[str, Any]]] = {condition: [] for condition in sorted(CONDITIONS)}
    pairs: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for run in data["runs"]:
        by_condition[run["condition"]].append(run)
        if run.get("pair_id") is not None:
            pairs[run["pair_id"]].append(run)

    conditions = {}
    for condition, runs in by_condition.items():
        successes = [run for run in runs if run["status"] == "completed" and run["quality"] == "accepted"]
        scenario_events = {
            scenario: _event_summary(run for run in runs if run["scenario_id"] == scenario)
            for scenario in sorted(SCENARIOS)
        }
        conditions[condition] = {
            "runs": len(runs), "successes": len(successes), "success_rate": len(successes) / len(runs) if runs else None,
            "status_counts": dict(Counter(run["status"] for run in runs)),
            "quality_counts": dict(Counter(run["quality"] for run in runs)),
            "active_seconds": _summary(run.get("active_seconds") for run in runs),
            "user_wait_seconds": _summary(run.get("user_wait_seconds") for run in runs),
            "token_count": _summary(run.get("token_count") for run in runs),
            "resume_seconds": _summary(
                int((_timestamp(run["first_acceptance_action_at"], "first_acceptance_action_at") - _timestamp(run["resume_requested_at"], "resume_requested_at")).total_seconds())
                if run["resume_requested_at"] is not None and run["first_acceptance_action_at"] is not None else None
                for run in runs
            ),
            "missing": {field: sum(run.get(field) is None for run in runs) for field in ("active_seconds", "user_wait_seconds", "token_count")},
            "events": _event_summary(runs),
            "scenario_events": scenario_events,
        }

    paired_active_deltas = []
    for pair in pairs.values():
        baseline = next(run for run in pair if run["condition"] == "baseline")
        mpa = next(run for run in pair if run["condition"] == "mpa")
        successful = all(run["status"] == "completed" and run["quality"] == "accepted" for run in pair)
        if successful and baseline.get("active_seconds") is not None and mpa.get("active_seconds") is not None:
            paired_active_deltas.append(mpa["active_seconds"] - baseline["active_seconds"])
    return {
        "schema_version": 1, "study_id": data["study_id"], "total_runs": len(data["runs"]),
        "conditions": conditions,
        "paired_successful_active_seconds_delta": _summary(paired_active_deltas),
        "interpretation": "Descriptive local measurement only; no causal or statistical effect claim.",
    }


def render_markdown(report: Dict[str, Any]) -> str:
    lines = [f"# MPA 효과 측정 요약: {report['study_id']}", "", report["interpretation"], "", "| 조건 | run | 성공 | 성공률 | active 중앙값 | user wait 중앙값 | token 중앙값 | 재개 중앙값 | active 누락 |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for condition in ("baseline", "mpa"):
        value = report["conditions"][condition]
        lines.append("| {condition} | {runs} | {successes} | {rate} | {active} | {wait} | {token} | {resume} | {missing} |".format(
            condition=condition, runs=value["runs"], successes=value["successes"],
            rate="n/a" if value["success_rate"] is None else f"{value['success_rate']:.2f}",
            active=value["active_seconds"]["median"] if value["active_seconds"]["median"] is not None else "n/a",
            wait=value["user_wait_seconds"]["median"] if value["user_wait_seconds"]["median"] is not None else "n/a",
            token=value["token_count"]["median"] if value["token_count"]["median"] is not None else "n/a",
            resume=value["resume_seconds"]["median"] if value["resume_seconds"]["median"] is not None else "n/a",
            missing=value["missing"]["active_seconds"],
        ))
    lines.extend(["", "## 사용자 개입·재작업 사건", ""])
    for condition in ("baseline", "mpa"):
        lines.extend([f"### {condition}", "", "| scenario | 사건 종류별 수 | 필요성 분류별 수 |", "|---|---|---|"])
        for scenario in sorted(SCENARIOS):
            events = report["conditions"][condition]["scenario_events"][scenario]
            kinds = ", ".join(f"{kind}: {count}" for kind, count in sorted(events["by_kind"].items())) or "없음"
            necessities = ", ".join(f"{kind}: {count}" for kind, count in sorted(events["by_necessity"].items())) or "없음"
            lines.append(f"| {scenario} | {kinds} | {necessities} |")
        lines.append("")
    paired = report["paired_successful_active_seconds_delta"]
    lines.extend(["", "## 성공 쌍 active time 차이 (mpa - baseline)", "", f"유효 쌍: {paired['count']}; 중앙값: {paired['median'] if paired['median'] is not None else 'n/a'}초"])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--json-out", required=True, type=Path)
    parser.add_argument("--markdown-out", required=True, type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.input.read_text(encoding="utf-8"))
        report = summarize(data)
        args.json_out.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        args.markdown_out.write_text(render_markdown(report), encoding="utf-8")
    except (OSError, json.JSONDecodeError, StudyValidationError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
