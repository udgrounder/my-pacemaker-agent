#!/usr/bin/env python3
"""
code_gate.py — 코드 수정 게이트 (PreToolUse / BeforeTool)

plan.md YAML 프론트매터의 '상태' 필드를 기준으로 소스 수정을 제어한다.

GATE 1 — 소스 수정 (Edit/Write):
  active 태스크 중 상태 = '구현 중'인 것이 있어야 허용.
  없으면 차단.

GATE 2 — 완료 이동 (Bash mv):
  tasks/active → tasks/done 이동 시
  해당 태스크 plan.md 상태 = '완료 승인'이어야 허용.
  아니면 차단.

동작 강도: MPA_GATE 환경변수
  - block (기본) : 조건 불충족 시 차단 (exit 2)
  - warn         : 차단하지 않고 경고만 주입
  - off          : 게이트 비활성

사용법: code_gate.py --agent {claude|codex|gemini}
입력  : stdin 으로 hook JSON
"""

import argparse
import hashlib
import json
import os
import re
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

# 소스 수정 도구 (agent별 명칭 차이 흡수)
EDIT_TOOLS = {
    "Edit", "Write", "MultiEdit", "NotebookEdit",   # claude
    "apply_patch", "write_file", "replace", "edit",  # codex / gemini
}

# Bash 실행 도구
BASH_TOOLS = {"Bash", "bash", "shell", "run_command"}


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
    if norm.endswith(".md"):
        return True  # 문서·계획·메모리류는 통과
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
                    fields[k.strip()] = v.strip()
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


def compute_plan_hash(body):
    """plan.md 본문(프론트매터 제외)의 해시를 계산한다."""
    # 공백·줄바꿈 정규화 후 해시 — 사소한 포맷 변경에는 둔감
    normalized = re.sub(r"\s+", " ", body).strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


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


def find_task_dir_by_status(cwd, target_status):
    """특정 상태의 첫 active 태스크 폴더 경로를 반환."""
    base = os.path.join(cwd, "workspace", "tasks", "active")
    if not os.path.isdir(base):
        return None
    for name in sorted(os.listdir(base)):
        task_dir = os.path.join(base, name)
        plan_path = os.path.join(task_dir, "plan.md")
        if os.path.exists(plan_path) and parse_plan_status(plan_path) == target_status:
            return task_dir
    return None


def check_hash_integrity(cwd, mode, agent):
    """GATE 1 재진입 — '구현 중' 상태 태스크의 plan.md 해시가 승인해시와 일치하는지 확인."""
    base = os.path.join(cwd, "workspace", "tasks", "active")
    if not os.path.isdir(base):
        return
    for name in sorted(os.listdir(base)):
        task_dir = os.path.join(base, name)
        plan_path = os.path.join(task_dir, "plan.md")
        if not os.path.exists(plan_path):
            continue
        fields, body = parse_plan_fields(plan_path)
        if fields.get("상태") != "구현 중":
            continue
        approved_hash = fields.get("승인해시")
        if not approved_hash:
            # 승인해시 없음 — 구버전 호환 또는 미설정. 경고만.
            emit_warn(
                agent,
                f"⚠️ '{name}' plan.md에 '승인해시'가 없습니다. "
                "설계 완료 시 승인해시를 기록해야 GATE 1 재진입 검증이 가능합니다."
            )
            return
        current_hash = compute_plan_hash(body)
        if current_hash != approved_hash:
            msg = (
                f"⛔ GATE 1 재진입 차단: '{name}' plan.md가 승인 후 변경됐습니다.\n"
                f"  승인해시: {approved_hash}\n"
                f"  현재해시: {current_hash}\n"
                "plan.md 변경이 설계에 영향을 주는지 사용자에게 확인하고:\n"
                "  - 설계 영향 있음 → 상태를 '설계 완료'로 되돌리고 재승인\n"
                "  - 설계 영향 없음 → 사용자 확인 후 '승인해시'를 새 해시로 갱신"
            )
            if mode == "warn":
                emit_warn(agent, msg)
            else:
                emit_block(msg)
            return


def check_bash_mv(data, cwd, mode, agent):
    """GATE 2 — Bash mv tasks/active → tasks/done 차단."""
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
            "사용자의 명시적 완료 승인 후 plan.md 상태를 '완료 승인'으로 업데이트하세요."
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

    mode = os.environ.get("MPA_GATE", "block").strip().lower()
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
    if is_always_allowed(rel):
        sys.exit(0)

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
    # '구현 중' 상태 태스크의 plan.md가 승인 후 변경됐는지 확인
    check_hash_integrity(cwd, mode, args.agent)

    sys.exit(0)


if __name__ == "__main__":
    main()
