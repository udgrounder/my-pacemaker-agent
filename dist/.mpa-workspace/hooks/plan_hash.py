#!/usr/bin/env python3
"""
plan_hash.py — plan.md 본문 해시 계산 / 승인해시 갱신 도구

GATE 1 재진입 검증용. code_gate.py와 같은 알고리즘을 사용한다.

사용법:
  plan_hash.py compute <plan_path>      현재 본문 해시 출력
  plan_hash.py approve <plan_path>      현재 해시를 '승인해시' 필드에 기록 (in-place)
  plan_hash.py check   <plan_path>      승인해시 vs 현재해시 비교 (일치: exit 0, 불일치: exit 1)
  plan_hash.py audit   <plan_path>      프론트매터 필드 검사 (누락 필드를 stdout JSON으로 출력)
  plan_hash.py init    <plan_path> --field key=value [--field ...]
                                        누락된 프론트매터를 주입 (에이전트 추론 후 호출용)

에이전트 사용 시점:
  - 설계 완료 시점 (상태: '설계 완료' 또는 '구현 중'으로 전환 시): approve
  - 사용자 재승인 후: approve
  - 해시만 확인할 때: check
  - 구버전 plan.md 발견 시: audit → 본문 읽고 추론 → 사용자 확인 → init
"""

import hashlib
import json
import re
import sys

REQUIRED_FIELDS = ["태스크", "생성일", "타입", "실패비용", "상태", "승인해시"]
VALID_STATUS = {"설계 중", "설계 완료", "구현 중", "검증 중", "테스트 중", "검토 완료", "완료 승인"}
VALID_TYPE = {"major", "minor"}
VALID_COST = {"critical", "major", "minor"}


def parse(plan_path):
    with open(plan_path, encoding="utf-8") as f:
        content = f.read()
    match = re.match(r"^---\n(.*?)\n---\n?(.*)", content, re.DOTALL)
    if not match:
        return None, content, content
    return match.group(1), match.group(2), content


def compute(body):
    normalized = re.sub(r"\s+", " ", body).strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


def get_field(front_matter, key):
    if not front_matter:
        return None
    for line in front_matter.splitlines():
        if line.startswith(f"{key}:"):
            return line.split(":", 1)[1].strip().strip('"').strip("'")
    return None


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
    new_content = f"---\n{new_front}\n---\n{body}"
    with open(plan_path, "w", encoding="utf-8") as f:
        f.write(new_content)


def audit(plan_path):
    """프론트매터 필드 상태를 검사한다.
    반환: dict {"frontmatter_exists": bool, "missing": [...], "invalid": [{field, value, reason}]}
    """
    front_matter, _, _ = parse(plan_path)
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
        _, body, _ = parse(plan_path)
        print(compute(body))
    elif cmd == "approve":
        front_matter, body, _ = parse(plan_path)
        status = get_field(front_matter, "상태") if front_matter else None
        # minor 자동 승인: 상태가 없거나 '설계 중'/'메모'인 경우도 허용
        ALLOWED_STATUSES = {"설계 완료", "설계 중", "메모", None}
        if status not in ALLOWED_STATUSES:
            sys.stderr.write(
                f"⛔ approve 거부: 현재 상태가 '{status}'입니다.\n"
                "approve는 '설계 완료' 상태에서만 실행할 수 있습니다.\n"
                "이미 '구현 중'이라면 승인해시가 이미 기록된 상태입니다.\n"
            )
            sys.exit(2)
        h = compute(body)
        # 상태를 '구현 중'으로 전환하고 해시를 원자적으로 기록
        set_field(plan_path, "상태", "구현 중")
        set_field(plan_path, "승인해시", h)
        print(f"GATE 1 통과: 상태 → 구현 중 / 승인해시: {h}")
    elif cmd == "check":
        front_matter, body, _ = parse(plan_path)
        approved = get_field(front_matter, "승인해시")
        current = compute(body)
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
