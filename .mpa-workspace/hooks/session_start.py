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
    """plan.md YAML 프론트매터에서 '상태' 필드를 읽는다. 구형 포맷 폴백 포함."""
    import re
    try:
        with open(plan_path, encoding="utf-8") as f:
            content = f.read()
        # YAML 프론트매터 우선
        match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if match:
            for line in match.group(1).splitlines():
                if line.startswith("상태:"):
                    return line.split(":", 1)[1].strip()
        # 폴백: 구형 **상태:** 형식
        for line in content.splitlines():
            if "상태" in line and (":" in line or "：" in line):
                return line.strip().lstrip("#").strip()
    except Exception:
        pass
    return "상태 미상"


REQUIRED_FIELDS = ["태스크", "생성일", "타입", "실패비용", "상태", "승인해시"]


def _read_field(plan_path, key):
    """plan.md 프론트매터에서 특정 필드값을 반환한다."""
    import re
    try:
        with open(plan_path, encoding="utf-8") as f:
            content = f.read()
        match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if match:
            for line in match.group(1).splitlines():
                if line.startswith(f"{key}:"):
                    return line.split(":", 1)[1].strip().strip('"').strip("'")
    except Exception:
        pass
    return ""


def audit_frontmatter(plan_path):
    """plan.md 프론트매터 필드 검사. (missing 리스트, has_frontmatter bool) 반환."""
    import re
    try:
        with open(plan_path, encoding="utf-8") as f:
            content = f.read()
        match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if not match:
            return REQUIRED_FIELDS[:], False
        front = match.group(1)
        existing = {}
        for line in front.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                existing[k.strip()] = v.strip()
        missing = []
        for key in REQUIRED_FIELDS:
            val = existing.get(key)
            if val is None:
                missing.append(key)
            elif not val and key != "승인해시":
                missing.append(key)
        return missing, True
    except Exception:
        return [], False


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
        if not os.path.exists(plan):
            rows.append(f"  - {name} — plan.md 없음")
            continue
        status = read_status(plan)
        missing, has_front = audit_frontmatter(plan)
        task_type = _read_field(plan, "타입") if has_front else ""
        type_tag = f" [{task_type}]" if task_type else ""
        if not has_front:
            rows.append(f"  - {name} — {status}  ⚠️ 프론트매터 없음 (구버전 plan.md)")
        elif missing:
            rows.append(f"  - {name} — {status}{type_tag}  ⚠️ 누락 필드: {', '.join(missing)}")
        else:
            rows.append(f"  - {name} — {status}{type_tag}")
    return rows


def build_message(cwd):
    rows = active_tasks(cwd)
    mode = os.environ.get("MPA_GATE", "block").strip().lower()

    lines = ["[my-pacemaker-agent] 세션 시작 루틴"]

    if rows is None:
        lines.append("workspace/ 가 없습니다 — 프로젝트 초기화(Layer 0)가 필요합니다.")
        return "\n".join(lines)

    if rows:
        lines.append("진행 중인 태스크가 있습니다. 번호로 선택해 주세요:")
        for i, row in enumerate(rows, 1):
            lines.append(f"  {i}.{row.lstrip()}")
        lines.append(f"  {len(rows) + 1}. 새 태스크 시작")
        lines.append("→ 번호를 말씀해 주시면 해당 태스크의 상태에 따라 진행합니다.")
        # 프론트매터 누락 항목이 있으면 처리 지시 추가
        if any("⚠️" in row for row in rows):
            lines.append("")
            lines.append("⚠️ 일부 plan.md의 프론트매터가 누락됐습니다.")
            lines.append("해당 태스크 진입 시 다음 절차를 따르세요:")
            lines.append("  1. plan.md 본문을 읽고 누락 필드를 추론 (`plan_hash.py audit <path>`로 정확한 누락 목록 확인)")
            lines.append("  2. 추론한 값과 근거를 사용자에게 짧게 보여주고 확인")
            lines.append("  3. 확인 후 `plan_hash.py init <path> --field key=value ...` 로 주입")
            lines.append("  4. 추론 기준은 agent_rules.md '프론트매터 누락 처리' 섹션 참조")
    else:
        lines.append("진행 중인 태스크 없음.")
        lines.append(
            "→ 진행 중 태스크가 없으니, 사용자에게 두 경로를 한 줄로 안내하세요: "
            "**작업**(\"○○ 만들어줘/고쳐줘\") 또는 **논의**(\"○○ 논의하자\" — 토론 모드)."
        )

    lines.append(
        "요청을 받으면 .mpa-workspace/core/agent_rules.md 의 라우팅 표로 유형을 판단하고 "
        "해당 inject 파일을 로드해 작업하세요."
    )
    lines.append(
        f"코드 수정 게이트: MPA_GATE={mode}. '구현 중' 상태인 태스크 없이 소스를 "
        "수정하면 차단/경고됩니다 — 구현 전 plan.md 상태를 '구현 중'으로 설정하세요."
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
