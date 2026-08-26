#!/usr/bin/env python3
"""
plan_hash.py — plan.md 본문 해시 계산 / 승인해시 갱신 도구

GATE 1 재진입 검증용. code_gate.py와 같은 알고리즘을 사용한다.

사용법:
  plan_hash.py compute <plan_path>      현재 본문 해시 출력
  plan_hash.py approve <plan_path>      현재 승인 대상 해시를 '승인해시' 필드에 기록 (in-place)
  plan_hash.py renew-spec <plan_path> --summary <변경 요약>
                                        진행 중 요구사항 명세의 승인 기록을 갱신
  plan_hash.py check   <plan_path>      승인해시 vs 현재해시 비교 (일치: exit 0, 불일치: exit 1)
  plan_hash.py audit   <plan_path>      프론트매터 필드 검사 (누락 필드를 stdout JSON으로 출력)
  plan_hash.py init    <plan_path> --field key=value [--field ...]
                                        누락된 프론트매터를 주입 (에이전트 추론 후 호출용)

에이전트 사용 시점:
  - 설계 완료 시점 (상태: '설계 완료' 또는 '구현 중'으로 전환 시): approve
  - 사용자 명세 변경 승인 후: renew-spec
  - 해시만 확인할 때: check
  - 구버전 plan.md 발견 시: audit → 본문 읽고 추론 → 사용자 확인 → init
"""

import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone

REQUIRED_FIELDS = ["태스크", "생성일", "타입", "실패비용", "상태", "승인해시"]
SPEC_FORMAT_FIELD = "승인대상"
SPEC_FORMAT_VALUE = "요구사항 명세"
SPEC_HASH_PREFIX = "reqspec-v1:"
SPEC_HASH_RE = re.compile(r"^reqspec-v1:[0-9a-f]{16}$")
VALID_STATUS = {"작성 중", "설계 중", "설계 완료", "구현 중", "검증 중", "테스트 중", "검토 완료", "완료 승인"}
HASH_REQUIRED_STATUSES = {"구현 중", "검증 중", "테스트 중", "검토 완료", "완료 승인"}
VALID_TYPE = {"major", "minor"}
VALID_COST = {"critical", "major", "minor"}


def parse(plan_path):
    with open(plan_path, encoding="utf-8") as f:
        content = f.read()
    match = re.match(r"^---\n(.*?)\n---\n?(.*)", content, re.DOTALL)
    if not match:
        return None, content, content
    return match.group(1), match.group(2), content


HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")


def strip_implementation_sections(body):
    """헤딩 텍스트가 '구현'으로 시작하는 섹션(그 헤딩부터 다음 헤딩 전까지)을 제외한다.

    '구현'/'구현 단계'/'구현 후 발견' 등 승인 이후 자연스럽게 갱신되는 진행 기록
    섹션을 해시 대상에서 빼, 체크박스·완료 노트 추가만으로 GATE 1 재진입이
    걸리지 않도록 한다. 그 외 섹션(목적·핵심 기능·반례 등)은 그대로 해시된다.
    """
    kept = []
    excluding = False
    for line in body.splitlines():
        m = HEADING_RE.match(line)
        if m:
            excluding = m.group(2).strip().startswith("구현")
        if not excluding:
            kept.append(line)
    return "\n".join(kept)


def extract_specification(body):
    """새 plan 형식의 `## 요구사항 명세` 본문만 반환한다.

    None은 구형 plan으로, 빈 문자열은 새 형식이지만 비어 있는 명세로 구분한다.
    """
    lines = body.splitlines()
    start = None
    for index, line in enumerate(lines):
        if re.match(r"^##\s+요구사항 명세\s*$", line.strip()):
            start = index + 1
            break
    if start is None:
        return None
    end = len(lines)
    for index in range(start, len(lines)):
        if re.match(r"^##\s+", lines[index]):
            end = index
            break
    return "\n".join(lines[start:end])


def compute_legacy(body):
    """구형 plan의 기존 본문 해시를 계산한다."""
    normalized = re.sub(r"\s+", " ", strip_implementation_sections(body)).strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


def compute_specification(body):
    """요구사항 명세 블록의 원시 체크섬을 계산한다."""
    specification = extract_specification(body)
    if specification is None:
        raise ValueError("`## 요구사항 명세` 섹션이 누락됐습니다")
    normalized = re.sub(r"\s+", " ", specification).strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


def compute(body):
    """본문만 제공되는 기존 호출자의 호환 함수.

    plan 전체의 형식 판별은 반드시 compute_for_plan을 사용한다.
    """
    return compute_specification(body) if extract_specification(body) is not None else compute_legacy(body)


def compute_for_plan(front_matter, body):
    """승인해시 버전과 형식 표지로 구형·최신 plan을 명시적으로 판별한다."""
    approved_hash = get_field(front_matter, "승인해시")
    format_is_spec = get_field(front_matter, SPEC_FORMAT_FIELD) == SPEC_FORMAT_VALUE
    hash_is_spec = bool(approved_hash and approved_hash.startswith(SPEC_HASH_PREFIX))

    if approved_hash and ":" in approved_hash and not hash_is_spec:
        raise ValueError(f"지원하지 않는 승인해시 형식입니다: {approved_hash.split(':', 1)[0]}")
    if hash_is_spec and not format_is_spec:
        raise ValueError("reqspec-v1 승인해시에는 `승인대상: 요구사항 명세`가 필요합니다")
    if format_is_spec:
        if extract_specification(body) is None:
            raise ValueError("요구사항 명세 형식 plan에서 `## 요구사항 명세` 섹션이 누락됐습니다")
        return SPEC_HASH_PREFIX + compute_specification(body)
    if hash_is_spec:
        raise ValueError("요구사항 명세 형식 plan에서 `## 요구사항 명세` 섹션이 누락됐습니다")
    return compute_legacy(body)


def approval_hash_issue(front_matter, body):
    """승인 이후 상태의 승인해시 형식·현재 명세 일치 문제를 반환한다.

    최신 plan(`승인대상: 요구사항 명세`)의 승인해시는 반드시
    `plan_hash.py approve` 또는 사용자 승인 뒤 `renew-spec`가 만든
    `reqspec-v1:<16자리 소문자 16진수>`여야 한다. 구형 plan은 기존 본문
    해시와의 일치만 검사해 과거 이력의 읽기 호환성을 유지한다.
    """
    status = get_field(front_matter, "상태")
    if status not in HASH_REQUIRED_STATUSES:
        return None

    approved_hash = get_field(front_matter, "승인해시")
    if not approved_hash:
        return "승인 이후 상태에는 승인해시가 필요합니다"

    if not SPEC_HASH_RE.fullmatch(approved_hash):
        return (
            "승인 이후 상태의 승인해시는 `reqspec-v1:<16자리 소문자 16진수>` 형식이어야 합니다 "
            "(`approve` 또는 사용자 승인 뒤 `renew-spec`만 기록 가능)"
        )

    try:
        current_hash = compute_for_plan(front_matter, body)
    except ValueError as error:
        return str(error)
    if approved_hash != current_hash:
        return f"승인해시가 현재 승인 대상과 일치하지 않습니다 (현재: {current_hash})"
    return None


def get_field(front_matter, key):
    if not front_matter:
        return None
    for line in front_matter.splitlines():
        if line.startswith(f"{key}:"):
            return line.split(":", 1)[1].strip().strip('"').strip("'")
    return None


def write_plan(plan_path, front_matter, body):
    new_content = f"---\n{front_matter}\n---\n{body}"
    tmp_path = plan_path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    os.replace(tmp_path, plan_path)


def set_field(plan_path, key, value):
    front_matter, body, content = parse(plan_path)
    if front_matter is None:
        sys.stderr.write("프론트매터 없음 — 갱신 불가\n")
        sys.exit(2)
    new_lines = []
    found = False
    for line in front_matter.splitlines():
        if line.startswith(f"{key}:"):
            new_lines.append(f"{key}: {value}")
            found = True
        else:
            new_lines.append(line)
    if not found:
        new_lines.append(f"{key}: {value}")
    new_front = "\n".join(new_lines)
    write_plan(plan_path, new_front, body)


def renew_spec(plan_path, summary):
    front_matter, body, _ = parse(plan_path)
    if front_matter is None or extract_specification(body) is None:
        raise ValueError("renew-spec은 `## 요구사항 명세`가 있는 plan.md에서만 사용할 수 있습니다")
    if not summary.strip():
        raise ValueError("renew-spec에는 사용자에게 제시한 변경 요약이 필요합니다 (--summary)")
    old_hash = get_field(front_matter, "승인해시")
    if not old_hash:
        raise ValueError("기존 승인해시가 없습니다. 최초 승인은 approve로 처리하세요")
    history_match = re.search(r"(?m)^##\s+명세 변경 이력\s*$", body)
    if history_match is None:
        raise ValueError("`## 명세 변경 이력` 섹션이 없어 승인 이력을 기록할 수 없습니다")
    new_hash = compute_for_plan(front_matter, body)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    row = f"| {timestamp} | {old_hash} | {new_hash} | {summary.strip()} |"
    start = history_match.end()
    next_heading_match = re.search(r"(?m)^#{1,6}\s+", body[start:])
    end = len(body) if next_heading_match is None else start + next_heading_match.start()
    history = body[start:end]
    header = "| 승인 시각 | 이전 체크섬 | 새 체크섬 | 변경 요약 |\n|---|---|---|---|"
    if header not in history:
        history = "\n\n" + header + "\n" + history.strip() + "\n"
    if not history.endswith("\n"):
        history += "\n"
    body = body[:start] + history + row + "\n" + body[end:]
    lines = []
    for line in front_matter.splitlines():
        lines.append(f"승인해시: {new_hash}" if line.startswith("승인해시:") else line)
    write_plan(plan_path, "\n".join(lines), body)
    return old_hash, new_hash, timestamp


def audit(plan_path):
    """프론트매터 필드 상태를 검사한다.
    반환: dict {"frontmatter_exists": bool, "missing": [...], "invalid": [{field, value, reason}]}
    """
    front_matter, body, _ = parse(plan_path)
    result = {"frontmatter_exists": front_matter is not None, "missing": [], "invalid": []}
    if front_matter is None:
        result["missing"] = list(REQUIRED_FIELDS)
        return result

    for key in REQUIRED_FIELDS:
        val = get_field(front_matter, key)
        if val is None:
            result["missing"].append(key)
            continue
        # 빈 값(승인해시는 빈 값 허용)
        if not val and key != "승인해시":
            result["missing"].append(key)
            continue
        # 형식 검증
        if key == "상태" and val not in VALID_STATUS:
            result["invalid"].append({"field": key, "value": val, "reason": f"유효하지 않은 상태값. 허용: {sorted(VALID_STATUS)}"})
        elif key == "타입" and val not in VALID_TYPE:
            result["invalid"].append({"field": key, "value": val, "reason": f"유효하지 않은 타입. 허용: {sorted(VALID_TYPE)}"})
        elif key == "실패비용" and val not in VALID_COST:
            result["invalid"].append({"field": key, "value": val, "reason": f"유효하지 않은 실패비용. 허용: {sorted(VALID_COST)}"})

    issue = approval_hash_issue(front_matter, body)
    if issue:
        result["invalid"].append({
            "field": "승인해시",
            "value": get_field(front_matter, "승인해시") or "",
            "reason": issue,
        })
    return result


def init_frontmatter(plan_path, kv_pairs):
    """프론트매터를 주입한다. 이미 있으면 누락 필드만 추가, 없으면 새로 생성."""
    front_matter, body, content = parse(plan_path)

    new_fields = {}
    if front_matter:
        # 기존 필드 보존
        for line in front_matter.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                new_fields[k.strip()] = v.strip()

    # 새로 주입할 값 덮어쓰기
    for k, v in kv_pairs.items():
        new_fields[k] = v

    # REQUIRED_FIELDS 순서로 정렬 (누락된 것은 빈 값으로)
    ordered_lines = []
    for key in REQUIRED_FIELDS:
        val = new_fields.get(key, "")
        # 승인해시 빈 값은 따옴표로 명시
        if key == "승인해시" and not val:
            ordered_lines.append(f'{key}: ""')
        else:
            ordered_lines.append(f"{key}: {val}")
    # REQUIRED 외 기존 필드는 뒤에 보존
    for key, val in new_fields.items():
        if key not in REQUIRED_FIELDS:
            ordered_lines.append(f"{key}: {val}")

    new_front = "\n".join(ordered_lines)

    # 본문 결정: 프론트매터가 있었으면 body, 없었으면 content 전체
    body_out = body if front_matter is not None else content
    new_content = f"---\n{new_front}\n---\n{body_out}"
    with open(plan_path, "w", encoding="utf-8") as f:
        f.write(new_content)


def parse_field_args(args):
    """--field key=value 쌍을 파싱한다."""
    pairs = {}
    i = 0
    while i < len(args):
        if args[i] == "--field" and i + 1 < len(args):
            kv = args[i + 1]
            if "=" in kv:
                k, v = kv.split("=", 1)
                pairs[k.strip()] = v.strip()
            i += 2
        else:
            i += 1
    return pairs


def main():
    if len(sys.argv) < 3:
        sys.stderr.write(__doc__)
        sys.exit(2)
    cmd, plan_path = sys.argv[1], sys.argv[2]

    if cmd == "compute":
        front_matter, body, _ = parse(plan_path)
        print(compute_for_plan(front_matter, body))
    elif cmd == "approve":
        front_matter, body, _ = parse(plan_path)
        status = get_field(front_matter, "상태") if front_matter else None
        task_type = get_field(front_matter, "타입") if front_matter else None
        # major는 설계 완료 후에만, minor는 경량 흐름상 설계 중에도 승인한다.
        ALLOWED_STATUSES = {"설계 완료"}
        if task_type == "minor":
            ALLOWED_STATUSES.update({"설계 중", "작성 중", None})
        if status not in ALLOWED_STATUSES:
            sys.stderr.write(
                f"⛔ approve 거부: 현재 상태가 '{status}'입니다.\n"
                "major approve는 '설계 완료' 상태에서만 실행할 수 있습니다.\n"
                "이미 '구현 중'이라면 승인해시가 이미 기록된 상태입니다.\n"
            )
            sys.exit(2)
        if (
            get_field(front_matter, SPEC_FORMAT_FIELD) != SPEC_FORMAT_VALUE
            or extract_specification(body) is None
        ):
            sys.stderr.write(
                "⛔ approve 거부: 새 승인에는 `승인대상: 요구사항 명세`와 "
                "`## 요구사항 명세` 섹션이 필요합니다.\n"
                "구형 plan은 자동 변환하지 않습니다. 최신 템플릿 구조로 요구사항 명세를 정리하고 "
                "사용자 승인을 다시 받은 뒤 approve를 실행하세요.\n"
            )
            sys.exit(2)
        try:
            h = compute_for_plan(front_matter, body)
        except ValueError as error:
            sys.stderr.write(f"⛔ approve 거부: {error}\n")
            sys.exit(2)
        # 상태를 '구현 중'으로 전환하고 해시를 원자적으로 기록
        set_field(plan_path, "상태", "구현 중")
        set_field(plan_path, "승인해시", h)
        print(f"구현 승인됨: 상태 → 구현 중 / 승인해시: {h}")
    elif cmd == "renew-spec":
        args = sys.argv[3:]
        summary = ""
        if len(args) >= 2 and args[0] == "--summary":
            summary = args[1]
        try:
            old_hash, new_hash, timestamp = renew_spec(plan_path, summary)
        except ValueError as error:
            sys.stderr.write(f"⛔ 명세 승인 기록 갱신 실패: {error}\n")
            sys.exit(2)
        print(f"요구사항 명세 승인 기록 갱신됨: {old_hash} → {new_hash} / {timestamp}")
    elif cmd == "check":
        front_matter, body, _ = parse(plan_path)
        approved = get_field(front_matter, "승인해시")
        try:
            current = compute_for_plan(front_matter, body)
        except ValueError as error:
            print(f"불일치 — {error}")
            sys.exit(1)
        if approved == current:
            print(f"일치: {current}")
            sys.exit(0)
        else:
            print(f"불일치 — 승인해시: {approved} / 현재해시: {current}")
            sys.exit(1)
    elif cmd == "audit":
        result = audit(plan_path)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if result["missing"] or result["invalid"]:
            sys.exit(1)
        sys.exit(0)
    elif cmd == "init":
        kv = parse_field_args(sys.argv[3:])
        if not kv:
            sys.stderr.write("init은 최소 1개 --field key=value 가 필요합니다\n")
            sys.exit(2)
        init_frontmatter(plan_path, kv)
        print(f"프론트매터 주입 완료: {list(kv.keys())}")
    else:
        sys.stderr.write(f"알 수 없는 명령: {cmd}\n")
        sys.exit(2)


if __name__ == "__main__":
    main()
