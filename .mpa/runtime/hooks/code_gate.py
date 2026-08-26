#!/usr/bin/env python3
"""
code_gate.py — 코드 수정 게이트 (PreToolUse / BeforeTool)

plan.md YAML 프론트매터의 '상태' 필드를 기준으로 소스 수정을 제어한다.

GATE 1 — 소스 수정 (Edit/Write):
  active 태스크 중 상태 = '구현 중'인 것이 있어야 허용.
  기본 warn 모드에서는 절차 경고만 주입한다. 단, CURRENT_TASK로 선택한
  critical 태스크의 승인 누락·승인해시 무결성 오류는 차단한다.

GATE 2 — 완료 이동 (Bash mv):
  tasks/active → tasks/done 이동 시
  해당 태스크 plan.md 상태 = '완료 승인'이어야 허용.
  아니면 차단.

동작 강도: MPA_GATE 환경변수
  - block (명시 설정 시) : 조건 불충족 시 차단 (exit 2)
  - warn (기본) : 일반 절차 위반은 경고만 주입. 선택한 critical 태스크의
                  승인 무결성 오류는 차단
  - off          : 게이트 비활성

사용법: code_gate.py --agent {claude|codex|gemini}
입력  : stdin 으로 hook JSON
"""

import argparse
import json
import os
import re
import sys
from plan_hash import HASH_REQUIRED_STATUSES, approval_hash_issue

# 항상 허용하는 경로 접두사 (방법론·프로젝트 데이터·agent 설정)
ALLOW_PREFIXES = (
    "workspace/",
    ".mpa/runtime/",
    ".claude/",
    ".codex/",
    ".gemini/",
    ".agents/",
    "CLAUDE.md",
    "AGENTS.md",
    "GEMINI.md",
)

# 소스 수정 도구 (agent별 명칭 차이 흡수)
EDIT_TOOLS = {
    "Edit", "Write", "MultiEdit", "NotebookEdit",   # claude
    "apply_patch", "write_file", "replace", "edit",  # codex / gemini
}

# Bash 실행 도구
BASH_TOOLS = {"Bash", "bash", "shell", "run_command"}

CURRENT_TASK_PATH = ("workspace", "tasks", "CURRENT_TASK")


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
            return p
    return p


def is_always_allowed(rel):
    if rel is None:
        return True  # 경로 미상 — 막지 않는다
    norm = rel.replace(os.sep, "/")
    return any(norm.startswith(pfx) for pfx in ALLOW_PREFIXES)


def parse_plan_fields(plan_path):
    """plan.md YAML 프론트매터에서 필드들을 파싱해 dict로 반환."""
    fields = {}
    body = ""
    try:
        with open(plan_path, encoding="utf-8") as f:
            content = f.read()
        match = re.match(r"^---\n(.*?)\n---\n?(.*)", content, re.DOTALL)
        if match:
            for line in match.group(1).splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    fields[k.strip()] = v.strip().strip('"').strip("'")
            body = match.group(2)
        else:
            # 폴백: 프론트매터 없는 구형 plan.md
            for line in content.splitlines():
                if "상태" in line and ":" in line:
                    val = line.split(":", 1)[1].strip()
                    if val and "상태" not in fields:
                        fields["상태"] = val
            body = content
    except Exception:
        pass
    return fields, body


def parse_plan_status(plan_path):
    """plan.md '상태' 필드만 반환 (하위 호환용)."""
    fields, _ = parse_plan_fields(plan_path)
    return fields.get("상태")


def find_active_statuses(cwd):
    """active 태스크의 (태스크명, 상태) 목록을 반환한다."""
    base = os.path.join(cwd, "workspace", "tasks", "active")
    if not os.path.isdir(base):
        return []
    results = []
    for name in sorted(os.listdir(base)):
        task_dir = os.path.join(base, name)
        if not os.path.isdir(task_dir):
            continue
        plan_path = os.path.join(task_dir, "plan.md")
        if os.path.exists(plan_path):
            results.append((name, parse_plan_status(plan_path)))
    return results


def read_current_task(cwd):
    """사용자가 현재 선택·재개한 태스크명을 읽는다.

    CURRENT_TASK는 agent가 사용자 선택을 받은 뒤 기록하는 한 줄 파일이다.
    경로를 포함한 값은 무시해 task 경로 탈출이나 다른 파일의 우발적 참조를 막는다.
    """
    path = os.path.join(cwd, *CURRENT_TASK_PATH)
    try:
        with open(path, encoding="utf-8") as f:
            name = f.read().strip()
    except OSError:
        return None
    if not name or name in {".", ".."} or os.path.basename(name) != name:
        return None
    return name


def current_task_plan(cwd):
    """선택 태스크의 (이름, fields, body)를 반환한다. 없거나 잘못되면 None."""
    name = read_current_task(cwd)
    if not name:
        return None
    plan_path = os.path.join(cwd, "workspace", "tasks", "active", name, "plan.md")
    if not os.path.isfile(plan_path):
        return None
    fields, body = parse_plan_fields(plan_path)
    return name, fields, body


def _approval_recovery_message(name, status, issue):
    return (
        f"⛔ 구현 승인 기록 복구 필요: '{name}' plan.md 상태는 '{status}'이며 승인해시가 유효하지 않습니다.\n"
        f"  사유: {issue}\n"
        "승인해시를 직접 입력하거나 날짜·승인 문구로 바꾸지 마세요. 아래 중 하나로 명시적으로 복구하세요:\n"
        "  1. 사용자 승인 이력이 불명확함 → 상태를 '설계 완료'로 되돌리고 plan.md 검토 후 재승인\n"
        "  2. 사용자 승인 뒤 기록만 누락됨 → 현재 변경 내용을 사용자에게 확인받은 뒤 approve 실행\n"
        "  3. 승인된 요구사항 명세 변경 → 사용자 승인 후 renew-spec 실행\n"
        "최초 승인 명령:\n"
        f"  python3 .mpa/runtime/hooks/plan_hash.py approve workspace/tasks/active/{name}/plan.md"
    )


def check_selected_critical_integrity(cwd):
    """선택한 critical 태스크만 기본 모드에서 하드 차단할 사유를 반환한다."""
    current = current_task_plan(cwd)
    if not current:
        return None
    name, fields, body = current
    if fields.get("실패비용") != "critical":
        return None
    status = fields.get("상태")
    if status not in HASH_REQUIRED_STATUSES:
        return (
            f"⛔ critical 작업 시작 전 승인 필요: '{name}'의 현재 상태는 '{status or '미상'}'입니다.\n"
            "사용자에게 계획서 검토 후 구현 승인을 받은 뒤 plan_hash.py approve로 '구현 중' 상태와 승인해시를 기록하세요."
        )
    front_matter = "\n".join(f"{k}: {v}" for k, v in fields.items())
    issue = approval_hash_issue(front_matter, body)
    if issue:
        return _approval_recovery_message(name, status, issue)
    return None


def check_hash_integrity(cwd, mode, agent):
    """승인해시를 검사한다.

    기본 warn 모드는 선택되지 않은 기존 태스크의 이상을 경고로만 남긴다.
    명시적 block 모드는 과거와 같이 모든 승인 이후 태스크를 하드 차단한다.
    """
    base = os.path.join(cwd, "workspace", "tasks", "active")
    if not os.path.isdir(base):
        return
    for name in sorted(os.listdir(base)):
        task_dir = os.path.join(base, name)
        plan_path = os.path.join(task_dir, "plan.md")
        if not os.path.exists(plan_path):
            continue
        fields, body = parse_plan_fields(plan_path)
        status = fields.get("상태")
        if status not in HASH_REQUIRED_STATUSES:
            continue
        front_matter = "\n".join(f"{k}: {v}" for k, v in fields.items())
        issue = approval_hash_issue(front_matter, body)
        if issue:
            msg = _approval_recovery_message(name, status, issue)
            if mode == "warn":
                emit_warn(agent, msg)
            else:
                emit_block(msg)
            return


def check_done_write(rel, cwd, agent):
    """GATE 2 절차 확인 — Write/Edit로 workspace/tasks/done/ 직접 쓰기 시 경고 주입.

    하드 블록하지 않는다 (교착 방지). 에이전트에게 상태를 알려 절차를 따르도록 유도한다.
    active/에 같은 이름 태스크가 없으면(이미 이동 완료) 경고 없이 통과.
    """
    if rel is None:
        return
    norm = rel.replace(os.sep, "/")
    if not norm.startswith("workspace/tasks/done/"):
        return

    parts = norm.split("/")
    if len(parts) < 4:
        return
    task_name = parts[3]

    active_plan = os.path.join("workspace", "tasks", "active", task_name, "plan.md")
    if not os.path.exists(active_plan):
        return  # 이미 이동됐거나 done/ 원본 파일 — 통과

    status = parse_plan_status(active_plan)
    if status != "완료 승인":
        msg = (
            f"⚠️ 완료 절차 확인: '{task_name}' plan.md 상태가 '완료 승인'이 아닙니다"
            f" (현재: {status or '미상'}).\n"
            "done/ 경로 직접 쓰기 전에 사용자 완료 승인 → plan.md 상태 업데이트 순서를 확인하세요.\n"
            "※ 이 경고는 차단이 아닙니다 — 절차 확인 목적입니다."
        )
        emit_warn(agent, msg)


def check_bash_mv(data, cwd, mode, agent):
    """GATE 2 — Bash mv tasks/active → tasks/done 절차 경고 또는 명시적 차단."""
    tool_input = get(data, "tool_input", "toolInput", "input") or {}
    command = tool_input.get("command", "") if isinstance(tool_input, dict) else ""

    # mv .../workspace/tasks/active/<task> ... 패턴 감지
    pat = re.search(r"mv\s+\S*workspace/tasks/active/([^\s/]+)", command)
    if not pat:
        return  # 관련 없는 Bash 명령 — 통과

    task_name = pat.group(1)
    plan_path = os.path.join(cwd, "workspace", "tasks", "active", task_name, "plan.md")
    status = parse_plan_status(plan_path)

    if status != "완료 승인":
        msg = (
            f"⛔ 완료 처리 차단: '{task_name}' plan.md 상태가 '완료 승인'이 아닙니다"
            f" (현재: {status or '미상'}).\n"
            "사용자의 명시적 완료 승인 후 plan.md 상태를 '완료 승인'으로 업데이트하세요.\n"
            "※ mv 이외의 방법(shutil, Python 파일 조작 등)으로 이동해도 동일 규칙이 적용됩니다."
        )
        if mode == "warn":
            emit_warn(agent, msg)
        else:
            emit_block(msg)


def emit_warn(agent, message):
    """비차단 경고를 컨텍스트로 주입하고 통과시킨다."""
    event = "BeforeTool" if agent == "gemini" else "PreToolUse"
    out = {"hookSpecificOutput": {"hookEventName": event, "additionalContext": message}}
    print(json.dumps(out, ensure_ascii=False))
    sys.exit(0)


def emit_block(message):
    """도구 호출을 차단한다 (exit 2 + stderr)."""
    sys.stderr.write(message + "\n")
    sys.exit(2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", default="claude")
    args = ap.parse_args()

    mode = os.environ.get("MPA_GATE", "warn").strip().lower()
    if mode == "off":
        sys.exit(0)

    data = read_input()
    cwd = get(data, "cwd") or os.getcwd()
    tool = get(data, "tool_name", "toolName", "tool") or ""

    # ── GATE 2: Bash mv 차단 ──────────────────────────────────────────
    if tool in BASH_TOOLS:
        check_bash_mv(data, cwd, mode, args.agent)
        sys.exit(0)

    # ── GATE 1: 소스 수정 차단 ────────────────────────────────────────
    if tool and tool not in EDIT_TOOLS:
        sys.exit(0)

    rel = relativize(extract_path(data), cwd)
    check_done_write(rel, cwd, args.agent)  # GATE 2 절차 확인: done/ 직접 쓰기 경고
    if is_always_allowed(rel):
        sys.exit(0)

    # 선택한 critical 태스크는 다른 active 태스크의 상태와 무관하게 먼저 보호한다.
    critical_issue = check_selected_critical_integrity(cwd)
    if critical_issue:
        emit_block(critical_issue)

    statuses = find_active_statuses(cwd)
    implementing = [n for n, s in statuses if s == "구현 중"]

    if not implementing:
        target = rel or "(대상 미상)"
        if statuses:
            current = ", ".join(f"{n}:{s or '미상'}" for n, s in statuses)
            msg = (
                f"⛔ 구현 차단: '구현 중' 상태인 태스크가 없습니다 (수정 대상: {target}).\n"
                f"현재 태스크 상태: {current}\n"
                "plan.md 상태를 '구현 중'으로 업데이트한 뒤 진행하세요.\n"
                "(MPA_GATE=warn 또는 off 로 완화할 수 있습니다.)"
            )
        else:
            msg = (
                f"⛔ 구현 차단: active 태스크가 없습니다 (수정 대상: {target}).\n"
                "workspace/tasks/active/ 에 plan.md를 작성하고 사용자 승인을 받으세요."
            )
        if mode == "warn":
            emit_warn(args.agent, f"⚠️ '구현 중' 상태 태스크 없이 소스 수정 중. {target}")
        emit_block(msg)

    # ── GATE 1 재진입: 승인해시 검증 ──────────────────────────────────
    # 명시적 strict 모드에서는 모든 승인 이후 태스크의 plan.md를 차단 검사한다.
    check_hash_integrity(cwd, mode, args.agent)

    sys.exit(0)


if __name__ == "__main__":
    main()
