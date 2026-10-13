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
import tempfile
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


def approval_hash_issue(front_matter, body, plan_path=None):
    """승인 이후 상태의 승인해시 형식·현재 명세 일치 문제를 반환한다.

    최신 plan(`승인대상: 요구사항 명세`)의 승인해시는 반드시
    `plan_hash.py approve` 또는 사용자 승인 뒤 `renew-spec`가 만든
    `reqspec-v1:<16자리 소문자 16진수>`여야 한다. 구형 plan은 기존 본문
    해시와의 일치만 검사해 과거 이력의 읽기 호환성을 유지한다.
    """
    if plan_path and os.path.lexists(renewal_recovery_path(plan_path)):
        return "승인 기록 복구 필요: .plan-renewal.json의 원본·예상 작성본과 plan/changelog를 대조하세요"
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


def atomic_write(path, content):
    """동일 디렉터리 임시 파일을 원자 교체하고 실패 시 임시 파일을 정리한다."""
    descriptor, tmp_path = tempfile.mkstemp(prefix=".plan-write-", dir=os.path.dirname(os.path.abspath(path)))
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        if os.path.exists(path):
            os.chmod(tmp_path, os.stat(path).st_mode & 0o777)
        os.replace(tmp_path, path)
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def write_plan(plan_path, front_matter, body, transaction=None):
    content = f"---\n{front_matter}\n---\n{body}"
    if transaction is None:
        atomic_write(plan_path, content)
    else:
        recovery_path, recovery, expected = transaction
        guarded_write(plan_path, content, expected, recovery_path, recovery)


def renewal_recovery_path(plan_path):
    return os.path.join(os.path.dirname(os.path.abspath(plan_path)), ".plan-renewal.json")


def read_optional(path):
    if not os.path.lexists(path):
        return None
    if os.path.islink(path):
        raise ValueError("승인 갱신 파일은 심볼릭 링크일 수 없습니다")
    with open(path, encoding="utf-8") as stream:
        return stream.read()


def guarded_write(path, content, expected, recovery_path, recovery):
    """교체할 파일을 먼저 확보하고 빈 경로에만 새 내용을 설치한다.

    예상 원본 비교와 os.replace 사이의 경합을 만들지 않는다. rename으로
    실제 교체 대상 inode를 확보하고 link의 no-clobber 생성으로 외부 파일을
    덮지 않는다. 확보된 파일은 최종 대조 전까지 삭제하지 않는다.
    """
    directory = os.path.dirname(os.path.abspath(path))
    descriptor, stage = tempfile.mkstemp(prefix=".plan-write-", dir=directory)
    backup = None
    captured = False
    reserved_identity = None
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            if content is not None:
                stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        if expected is not None:
            descriptor, backup = tempfile.mkstemp(prefix=".plan-renewal-preserved-", dir=directory)
            os.close(descriptor)
            reserved = os.stat(backup, follow_symlinks=False)
            reserved_identity = (reserved.st_dev, reserved.st_ino)
            recovery.setdefault("preserved", []).append({
                "target": os.path.basename(path), "file": os.path.basename(backup), "expected": expected,
            })
            atomic_write(recovery_path, json.dumps(recovery, ensure_ascii=False, indent=2))
            # 여기서 확보하는 것은 읽기 검사 시점이 아니라 실제 교체 직전 파일이다.
            os.rename(path, backup)
            captured = True
            if read_optional(backup) != expected:
                raise ValueError("교체 직전 외부 편집을 확보했습니다. 자동 교체하지 않습니다")
            os.chmod(stage, os.stat(backup).st_mode & 0o777)
        elif os.path.lexists(path):
            raise ValueError("새 파일 경로에 외부 파일이 생겨 덮어쓰지 않습니다")
        if content is not None:
            os.link(stage, path)  # 경로가 생겼으면 EEXIST, 덮어쓰기 없음.
        elif os.path.lexists(path):
            raise ValueError("삭제 대상 경로에 외부 파일이 생겨 보존합니다")
    except BaseException:
        if backup is not None:
            # rename 성공 직후 captured=True 이전의 인터럽트도 실제 inode로 판별한다.
            try:
                saved = os.stat(backup, follow_symlinks=False)
                captured = reserved_identity is None or (saved.st_dev, saved.st_ino) != reserved_identity
            except OSError:
                captured = True  # 미확인은 삭제 근거로 사용하지 않는다.
        if backup is not None and not captured:
            os.unlink(backup)
            recovery["preserved"].pop()
        if backup is not None and not os.path.lexists(path):
            # 확보 파일을 되돌릴 때도 현재 경로를 덮지 않는다.
            try:
                if captured:
                    os.link(backup, path)
            except OSError:
                pass  # JSON과 확보 파일에서 수동 복구한다.
        raise
    finally:
        if os.path.exists(stage):
            os.unlink(stage)


def verify_approval_files(plan_path, history_path, expected_plan, expected_history, recovery):
    if read_optional(plan_path) != expected_plan or read_optional(history_path) != expected_history:
        raise ValueError("최종 plan/changelog가 예상 작성본과 다릅니다")
    directory = os.path.dirname(os.path.abspath(plan_path))
    for saved in recovery.get("preserved", []):
        if read_optional(os.path.join(directory, saved["file"])) != saved["expected"]:
            raise ValueError("확보한 원본에 외부 편집이 있어 복구 자료를 보존합니다")


def cleanup_approval_recovery(recovery_path, recovery):
    directory = os.path.dirname(recovery_path)
    for saved in recovery.get("preserved", []):
        os.unlink(os.path.join(directory, saved["file"]))
    # 중간 정리 실패가 성공으로 읽히지 않도록 journal은 마지막에 지운다.
    os.unlink(recovery_path)


def approval_history_match(text, plan=False):
    matches = list(re.finditer(r"(?m)^##\s+명세 변경 이력\s*$", text))
    if len(matches) > 1:
        raise ValueError("명세 변경 이력 헤딩이 중복되어 기록 위치를 확정할 수 없습니다")
    if matches and plan:
        headings = list(re.finditer(r"(?m)^##\s+(.+)$", text[:matches[0].start()]))
        if not headings or headings[-1].group(1).strip() == "요구사항 명세":
            raise ValueError("명세 변경 이력은 요구사항 명세 바깥 실행 영역 뒤에 있어야 합니다")
        if not any(heading.group(1).strip() == "요구사항 명세" for heading in headings):
            raise ValueError("명세 변경 이력 위치가 요구사항 명세보다 앞입니다")
    return matches[0] if matches else None


def append_approval_history(text, row):
    """정확한 최상위 이력 헤딩에만 기록하며 후속 섹션을 보존한다."""
    match = approval_history_match(text)
    if match is None:
        text = text.rstrip() + "\n\n## 명세 변경 이력\n"
        match = re.search(r"(?m)^##\s+명세 변경 이력\s*$", text)
    start = match.end()
    next_heading = re.search(r"(?m)^#{1,6}\s+", text[start:])
    end = len(text) if next_heading is None else start + next_heading.start()
    history = text[start:end]
    header = "| 승인 시각 | 이전 체크섬 | 새 체크섬 | 변경 요약 |\n|---|---|---|---|"
    if header not in history:
        history = "\n\n" + header + "\n" + history.strip() + "\n"
    return text[:start] + history.rstrip() + "\n" + row + "\n\n" + text[end:]


def write_approval_pair(plan_path, front_matter, body, history_path, old_history, new_history, old_plan):
    """지원 writer는 갱신 중 문서 편집을 직렬화한다.

    비협조 writer와 충돌하면 실제 교체 원본과 JSON을 보존한다. 두 파일 및
    확보 파일을 최종 대조한 뒤에만 완료한다. 임의 편집기의 작업 완료 후
    저장까지 원자적으로 통제하거나 두 파일 crash-atomicity를 보장하지 않는다.
    """
    recovery_path = renewal_recovery_path(plan_path)
    new_plan = f"---\n{front_matter}\n---\n{body}"
    recovery = {"plan_before": old_plan, "plan_after": new_plan,
                "changelog_before": old_history, "changelog_after": new_history,
                "preserved": []}
    descriptor = os.open(recovery_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
        json.dump(recovery, stream, ensure_ascii=False, indent=2)
        stream.flush()
        os.fsync(stream.fileno())
    if read_optional(plan_path) != old_plan or read_optional(history_path) != old_history:
        os.unlink(recovery_path)
        raise ValueError("승인 갱신 충돌: plan/changelog가 읽은 원본과 달라 저장하지 않았습니다. 최신 기록을 다시 확인하세요")
    try:
        guarded_write(history_path, new_history, old_history, recovery_path, recovery)
        write_plan(plan_path, front_matter, body, (recovery_path, recovery, old_plan))
    except (OSError, ValueError) as error:
        try:
            if read_optional(plan_path) != old_plan:
                raise ValueError("plan에 외부 변경 또는 미완료 저장이 있어 자동 원복하지 않습니다")
            current = read_optional(history_path)
            if current == new_history:
                guarded_write(history_path, old_history, new_history, recovery_path, recovery)
            elif current != old_history:
                raise ValueError("changelog에 외부 변경이 있어 자동 원복하지 않습니다")
            verify_approval_files(plan_path, history_path, old_plan, old_history, recovery)
            cleanup_approval_recovery(recovery_path, recovery)
        except (OSError, ValueError) as rollback_error:
            raise ValueError(f"승인 갱신 실패; 복구 필요: .plan-renewal.json과 확보 파일 보존 ({rollback_error})") from error
        raise ValueError(f"승인 갱신 실패; 기존 승인해시와 이력을 보존했습니다 ({error})") from error
    try:
        verify_approval_files(plan_path, history_path, new_plan, new_history, recovery)
    except (OSError, ValueError) as error:
        raise ValueError(f"승인 갱신 최종 대조 실패; .plan-renewal.json과 확보 파일 보존·복구 필요 ({error})") from error
    try:
        cleanup_approval_recovery(recovery_path, recovery)
    except OSError as error:
        raise ValueError("두 파일 저장 후 복구 기록 정리 실패; .plan-renewal.json 대조·복구 필요") from error


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
    if os.path.lexists(renewal_recovery_path(plan_path)):
        raise ValueError("승인 기록 복구 필요: .plan-renewal.json을 먼저 대조하세요")
    front_matter, body, original = parse(plan_path)
    if front_matter is None or extract_specification(body) is None:
        raise ValueError("renew-spec은 `## 요구사항 명세`가 있는 plan.md에서만 사용할 수 있습니다")
    if not summary.strip():
        raise ValueError("renew-spec에는 사용자에게 제시한 변경 요약이 필요합니다 (--summary)")
    old_hash = get_field(front_matter, "승인해시")
    if not old_hash:
        raise ValueError("기존 승인해시가 없습니다. 최초 승인은 approve로 처리하세요")
    if not SPEC_HASH_RE.fullmatch(old_hash):
        raise ValueError("구형 승인해시는 최신 명세로 정리하고 사용자 재승인 뒤 approve로 처리하세요")
    if get_field(front_matter, "상태") not in HASH_REQUIRED_STATUSES:
        raise ValueError("renew-spec은 최초 승인 이후 상태에서만 사용할 수 있습니다")
    new_hash = compute_for_plan(front_matter, body)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    safe_summary = summary.strip().replace("|", "&#124;").replace("\r", " ").replace("\n", " ")
    row = f"| {timestamp} | {old_hash} | {new_hash} | {safe_summary} |"
    lines = []
    for line in front_matter.splitlines():
        lines.append(f"승인해시: {new_hash}" if line.startswith("승인해시:") else line)
    new_front = "\n".join(lines)
    if approval_history_match(body, plan=True):
        write_plan(plan_path, new_front, append_approval_history(body, row))
    else:
        history_path = os.path.join(os.path.dirname(os.path.abspath(plan_path)), "changelog.md")
        if os.path.islink(history_path) or os.path.islink(plan_path):
            raise ValueError("승인 갱신의 plan/changelog는 심볼릭 링크일 수 없습니다")
        old_history = None
        if os.path.exists(history_path):
            with open(history_path, encoding="utf-8") as stream:
                old_history = stream.read()
        text = old_history if old_history is not None else "# 변경 이력\n\n**계획서:** `plan.md`\n"
        write_approval_pair(plan_path, new_front, body, history_path, old_history,
                            append_approval_history(text, row), original)
    return old_hash, new_hash, timestamp


def audit(plan_path):
    """프론트매터 필드 상태를 검사한다.
    반환: dict {"frontmatter_exists": bool, "missing": [...], "invalid": [{field, value, reason}]}
    """
    if not os.path.isfile(plan_path) and os.path.lexists(renewal_recovery_path(plan_path)):
        return {"frontmatter_exists": False, "missing": list(REQUIRED_FIELDS),
                "invalid": [{"field": "승인해시", "value": "",
                             "reason": "승인 저장 중단 복구 필요: .plan-renewal.json과 확보 파일을 먼저 대조하세요"}]}
    front_matter, body, _ = parse(plan_path)
    result = {"frontmatter_exists": front_matter is not None, "missing": [], "invalid": []}
    if front_matter is None:
        result["missing"] = list(REQUIRED_FIELDS)
        if os.path.lexists(renewal_recovery_path(plan_path)):
            result["invalid"].append({"field": "승인해시", "value": "",
                                      "reason": "승인 저장 중단 복구 필요: .plan-renewal.json을 먼저 대조하세요"})
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

    issue = approval_hash_issue(front_matter, body, plan_path)
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
        if os.path.lexists(renewal_recovery_path(plan_path)):
            sys.stderr.write("approve 거부: 승인 기록 복구 필요 (.plan-renewal.json)\n")
            sys.exit(2)
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
        # 최초 승인도 상태와 해시를 한 번의 원자 교체로 기록한다.
        lines = []
        for line in front_matter.splitlines():
            if line.startswith("상태:"):
                line = "상태: 구현 중"
            elif line.startswith("승인해시:"):
                line = f"승인해시: {h}"
            lines.append(line)
        if get_field(front_matter, "승인해시") is None:
            lines.append(f"승인해시: {h}")
        if get_field(front_matter, "상태") is None:
            lines.append("상태: 구현 중")
        write_plan(plan_path, "\n".join(lines), body)
        print(f"구현 승인됨: 상태 → 구현 중 / 승인해시: {h}")
    elif cmd == "renew-spec":
        args = sys.argv[3:]
        summary = ""
        if len(args) >= 2 and args[0] == "--summary":
            summary = args[1]
        try:
            old_hash, new_hash, timestamp = renew_spec(plan_path, summary)
        except (ValueError, OSError) as error:
            sys.stderr.write(f"⛔ 명세 승인 기록 갱신 실패: {error}\n")
            sys.exit(2)
        print(f"요구사항 명세 승인 기록 갱신됨: {old_hash} → {new_hash} / {timestamp}")
    elif cmd == "check":
        if os.path.lexists(renewal_recovery_path(plan_path)):
            print("불일치 — 승인 기록 복구 필요 (.plan-renewal.json)")
            sys.exit(1)
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
        if os.path.lexists(renewal_recovery_path(plan_path)):
            sys.stderr.write("init 거부: 승인 저장 중단 복구 필요 (.plan-renewal.json)\n")
            sys.exit(2)
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
