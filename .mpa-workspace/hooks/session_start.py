#!/usr/bin/env python3
"""
session_start.py — 세션 시작 루틴 주입 (SessionStart)

매 세션 시작 시 진행 중 태스크 목록과 핵심 라우팅 규칙을 컨텍스트에 주입한다.
agent 가 agent_rules.md 를 "안 읽는" 경우를 없애기 위한 기계적 보장 — 차단은 하지 않는다.

사용법: session_start.py --agent {claude|codex|gemini}
입력  : stdin 으로 hook JSON (사용하지 않아도 무방)
"""

import argparse
import json
import os
import sys


def read_cwd_from_stdin():
    """hook 입력 JSON 의 cwd 를 우선 사용하고, 없으면 os.getcwd() 로 폴백한다."""
    try:
        raw = sys.stdin.read()
        if raw.strip():
            data = json.loads(raw)
            if isinstance(data, dict) and data.get("cwd"):
                return data["cwd"]
    except Exception:
        pass
    return os.getcwd()


def read_status(plan_path):
    try:
        with open(plan_path, encoding="utf-8") as f:
            for line in f:
                if "상태" in line and (":" in line or "：" in line):
                    return line.strip().lstrip("#").strip()
    except Exception:
        pass
    return "상태 미상"


def active_tasks(cwd):
    if not os.path.isdir(os.path.join(cwd, "workspace")):
        return None  # workspace 자체가 없음
    base = os.path.join(cwd, "workspace", "tasks", "active")
    if not os.path.isdir(base):
        return []  # active 디렉터리가 아직 없음 = 진행 중 태스크 없음
    rows = []
    for name in sorted(os.listdir(base)):
        task_dir = os.path.join(base, name)
        if not os.path.isdir(task_dir):
            continue
        plan = os.path.join(task_dir, "plan.md")
        approved = os.path.exists(os.path.join(task_dir, ".approved"))
        status = read_status(plan) if os.path.exists(plan) else "plan.md 없음"
        mark = "✅승인" if approved else "⏳미승인"
        rows.append(f"  - {name} — {status} [{mark}]")
    return rows


def build_message(cwd):
    rows = active_tasks(cwd)
    mode = os.environ.get("MPA_GATE", "block").strip().lower()

    lines = ["[my-pacemaker-agent] 세션 시작 루틴"]

    if rows is None:
        lines.append("workspace/ 가 없습니다 — 프로젝트 초기화(Layer 0)가 필요합니다.")
        return "\n".join(lines)

    if rows:
        lines.append("진행 중인 태스크:")
        lines.extend(rows)
        lines.append("→ 이어서 진행할지, 새 작업을 시작할지 사용자에게 확인하세요.")
    else:
        lines.append("진행 중인 태스크 없음.")

    lines.append(
        "요청을 받으면 .mpa-workspace/core/agent_rules.md 의 라우팅 표로 유형을 판단하고 "
        "해당 inject 파일을 로드해 작업하세요."
    )
    lines.append(
        f"코드 수정 게이트: MPA_GATE={mode}. 승인된 plan(.approved 마커) 없이 소스를 "
        "수정하면 차단/경고됩니다 — 구현 전 plan 승인과 마커 생성을 잊지 마세요."
    )
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", default="claude")
    args = ap.parse_args()

    cwd = read_cwd_from_stdin()
    message = build_message(cwd)

    out = {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": message}}
    print(json.dumps(out, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
