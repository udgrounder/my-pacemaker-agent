#!/usr/bin/env python3
"""
code_gate.py — 코드 수정 게이트 (PreToolUse / BeforeTool)

승인된 plan(.approved 마커) 없이 프로젝트 소스코드를 수정하려 하면 차단한다.
plan.md / changelog / memory / docs / 설정 파일 작성은 절대 차단하지 않는다.

동작 강도는 환경변수 MPA_GATE 로 조절한다:
  - block (기본) : 마커 없으면 소스 수정 차단 (exit 2)
  - warn         : 차단하지 않고 경고만 주입
  - off          : 게이트 비활성

승인 마커: workspace/tasks/active/<task>/.approved
  사용자가 plan 을 승인하면 agent 가 생성한다. 사용자가 직접 만들거나 지워도 된다.

  .approved 파일 내용 (선택):
    비어 있으면 → 모든 소스 경로 허용 (기존 동작 유지)
    경로를 명시하면 → 해당 접두사 경로만 허용, 범위 이탈 시 경고 주입
    예)
      # 허용 경로 (접두사 매칭)
      src/features/auth/
      tests/auth/

사용법: code_gate.py --agent {claude|codex|gemini}
입력  : stdin 으로 hook JSON
"""

import argparse
import glob
import json
import os
import sys

# 항상 허용하는 경로 접두사 (방법론·프로젝트 데이터·agent 설정)
ALLOW_PREFIXES = (
    "workspace/",
    ".mpa-workspace/",
    ".claude/",
    ".codex/",
    ".gemini/",
    ".agents/",
)

# 수정 의도를 가진 도구 이름 (agent별 명칭 차이 흡수)
EDIT_TOOLS = {
    "Edit", "Write", "MultiEdit", "NotebookEdit",   # claude
    "apply_patch", "write_file", "replace", "edit",  # codex / gemini
}


def read_input():
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except Exception:
        return {}


def get(d, *keys):
    for k in keys:
        if isinstance(d, dict) and d.get(k):
            return d[k]
    return None


def extract_path(data):
    tool_input = get(data, "tool_input", "toolInput", "input") or {}
    if not isinstance(tool_input, dict):
        return None
    return get(tool_input, "file_path", "path", "filePath", "notebook_path", "absolute_path")


def relativize(path, cwd):
    if not path:
        return None
    p = os.path.normpath(path)
    cwd = os.path.normpath(cwd)
    if os.path.isabs(p):
        try:
            p = os.path.relpath(p, cwd)
        except ValueError:
            return p  # 다른 드라이브 등 — 절대경로 그대로
    return p


def is_always_allowed(rel):
    if rel is None:
        return True  # 경로를 못 찾으면 막지 않는다 (안전 우선)
    norm = rel.replace(os.sep, "/")
    if norm.endswith(".md"):
        return True  # 문서·계획·메모리류는 통과
    return any(norm.startswith(pfx) for pfx in ALLOW_PREFIXES)


def get_approved_scopes(cwd):
    """승인된 태스크와 허용 범위를 반환한다.

    Returns:
        (approved: bool, scopes: list[str])
        - (False, [])      : 승인된 태스크 없음 → 차단 대상
        - (True,  [])      : 빈 .approved → 모든 경로 허용 (기존 동작)
        - (True,  [...])   : 경로 명시 .approved → 해당 경로만 허용
    """
    pattern = os.path.join(cwd, "workspace", "tasks", "active", "*", ".approved")
    files = glob.glob(pattern)
    if not files:
        return False, []

    scopes = []
    for f in files:
        try:
            content = open(f, encoding="utf-8").read().strip()
            for line in content.splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    scopes.append(line)
        except Exception:
            pass
    return True, scopes


def in_approved_scope(rel, scopes):
    """대상 파일이 승인된 범위 안에 있는지 확인한다."""
    norm = rel.replace(os.sep, "/")
    for scope in scopes:
        scope = scope.rstrip("/")
        if norm == scope or norm.startswith(scope + "/"):
            return True
    return False


def emit_warn(agent, message):
    """비차단 경고를 컨텍스트로 주입하고 통과시킨다."""
    event = "BeforeTool" if agent == "gemini" else "PreToolUse"
    out = {"hookSpecificOutput": {"hookEventName": event, "additionalContext": message}}
    print(json.dumps(out, ensure_ascii=False))
    sys.exit(0)


def emit_block(message):
    """도구 호출을 차단한다 (exit 2 + stderr — 3개 agent 공통)."""
    sys.stderr.write(message + "\n")
    sys.exit(2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", default="claude")
    args = ap.parse_args()

    mode = os.environ.get("MPA_GATE", "block").strip().lower()
    if mode == "off":
        sys.exit(0)

    data = read_input()
    cwd = get(data, "cwd") or os.getcwd()

    tool = get(data, "tool_name", "toolName", "tool") or ""
    # 매처가 없는 agent(codex 등) 대비 — 수정 도구가 아니면 통과
    if tool and tool not in EDIT_TOOLS:
        sys.exit(0)

    rel = relativize(extract_path(data), cwd)
    if is_always_allowed(rel):
        sys.exit(0)

    approved, scopes = get_approved_scopes(cwd)

    if not approved:
        target = rel or "(대상 미상)"
        msg = (
            f"⛔ 구현 차단: 승인된 plan 이 없습니다 (수정 대상: {target}).\n"
            "workspace/tasks/active/ 에 plan.md 를 작성하고 사용자 승인을 받은 뒤,\n"
            "해당 태스크 폴더에 .approved 마커를 생성하세요.\n"
            "단순 작업이면 사용자가 '바로 진행' 후 마커를 만들면 됩니다.\n"
            "(이 게이트는 MPA_GATE=warn 또는 off 로 완화할 수 있습니다.)"
        )
        if mode == "warn":
            emit_warn(args.agent, "⚠️ 승인된 plan(.approved) 없이 소스를 수정 중입니다. " + target)
        emit_block(msg)

    # 승인된 태스크 존재
    if scopes and rel:
        # 경로가 명시된 경우 — 범위 검사
        if not in_approved_scope(rel, scopes):
            target = rel or "(대상 미상)"
            emit_warn(
                args.agent,
                f"⚠️ 범위 이탈: '{target}' 은 승인된 태스크의 허용 범위 밖입니다.\n"
                f"허용 경로: {', '.join(scopes)}\n"
                ".approved 파일에 해당 경로를 추가하거나, plan.md 범위를 확인하세요."
            )

    # 빈 .approved 이거나 범위 내 수정 → 허용
    sys.exit(0)


if __name__ == "__main__":
    main()
