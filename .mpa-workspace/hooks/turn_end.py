#!/usr/bin/env python3
"""
turn_end.py — 종료 시 갱신 리마인드 (Stop / AfterAgent)

진행 중 태스크가 있을 때, changelog.md / memory 갱신을 가볍게 상기시킨다.
차단하지 않는다 (응답 종료를 막지 않는다). 진행 중 태스크가 없으면 아무것도 하지 않는다.

노이즈가 거슬리면 settings 에서 이 hook 만 제거하면 된다.

사용법: turn_end.py --agent {claude|codex|gemini}
입력  : stdin 으로 hook JSON
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


def has_active_task(cwd):
    base = os.path.join(cwd, "workspace", "tasks", "active")
    if not os.path.isdir(base):
        return False
    for name in os.listdir(base):
        if os.path.isdir(os.path.join(base, name)):
            return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", default="claude")
    args = ap.parse_args()

    cwd = read_cwd_from_stdin()
    if not has_active_task(cwd):
        sys.exit(0)

    message = (
        "[my-pacemaker-agent] 진행 중 태스크가 있습니다. 코드를 변경했다면 "
        "해당 태스크의 changelog.md 와 관련 memory(roles/shared)를 갱신했는지 확인하세요."
    )
    event = "AfterAgent" if args.agent == "gemini" else "Stop"
    out = {"hookSpecificOutput": {"hookEventName": event, "additionalContext": message}}
    print(json.dumps(out, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
