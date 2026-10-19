#!/usr/bin/env python3
"""Read-only selection, readiness and role inputs for optional task documents.

Registration outside the requirement specification:
<!-- mpa-doc: {"role":"implementation","path":"implementation.md"} -->
After content review, spec and basis_sha256 bind the reviewed input.
No document, approval or review record is written by this module.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path, PurePosixPath

READY_STATES = {"구현 중", "검증 중", "테스트 중", "검토 완료", "완료 승인"}
ROLES = {"implementation", "verification", "ui_design", "research", "work"}
KEYS = {"role", "path", "spec", "basis_sha256"}
PROGRESS = {"진행 기록", "실행 결과", "검증 결과", "현재 상태"}
MARKER = re.compile(r"^\s*<!--\s*mpa-doc:\s*(.*?)\s*-->\s*$")
HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*$")
FENCE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")


def field(text, name):
    if not text.startswith("---\n"):
        return ""
    end = text.find("\n---", 4)
    if end < 0:
        return ""
    for line in text[4:end].splitlines():
        if line.startswith(name + ":"):
            return line.split(":", 1)[1].strip().strip("\"'")
    return ""


def lines_with_context(text):
    """Yield lines with their pre-line fence state; fence content is not syntax."""
    fence = None
    for line in text.splitlines():
        match = FENCE.match(line)
        in_fence = fence is not None
        yield line, in_fence
        if match:
            fence_marker = match.group(1)
            if fence is None:
                fence = fence_marker
            elif fence_marker[0] == fence[0] and len(fence_marker) >= len(fence):
                fence = None


def section(text, title, level=2):
    selected, output = False, []
    prefix = "#" * level + " "
    for line, fenced in lines_with_context(text):
        match = HEADING.match(line) if not fenced else None
        heading_level = len(line) - len(line.lstrip("#")) if match else None
        if match and heading_level <= level:
            if selected:
                break
            selected = heading_level == level and match.group(1) == title
            if selected:
                output.append(line)
        elif selected:
            output.append(line)
    return "\n".join(output).strip()


def basis_text(text):
    output, excluded = [], False
    for line, fenced in lines_with_context(text):
        if not fenced and line.startswith("## "):
            excluded = line[3:].strip() in PROGRESS
        if excluded:
            continue
        if not fenced and line.startswith(("**기준 상태:**", "**기준명세:**", "**기준 확인:**")):
            continue
        # Check marks are progress, their criterion text remains part of the basis.
        output.append(re.sub(r"^(\s*[-*]\s+)\[[ xX]\]", r"\1[ ]", line))
    return "\n".join(output).strip()


def basis_hash(text):
    return hashlib.sha256(basis_text(text).encode("utf-8")).hexdigest()


def no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("등록 JSON의 중복 필드: " + key)
        result[key] = value
    return result


def registrations(text):
    """Only an explicit marker opts a document in; links or existing files do not."""
    result = []
    for line, fenced in lines_with_context(text):
        if fenced or "mpa-doc:" not in line:
            continue
        match = MARKER.fullmatch(line)
        if not match:
            raise ValueError("작업 문서 등록 형식 오류")
        item = json.loads(match.group(1), object_pairs_hook=no_duplicates)
        if not isinstance(item, dict) or set(item) - KEYS:
            raise ValueError("작업 문서 등록 필드 오류")
        if (not isinstance(item.get("role"), str) or item["role"] not in ROLES
                or not isinstance(item.get("path"), str)):
            raise ValueError("작업 문서 역할/경로 오류")
        for key in ("spec", "basis_sha256"):
            if key in item and not isinstance(item[key], str):
                raise ValueError("작업 문서 기준 필드는 문자열이어야 합니다: " + key)
        result.append(item)
    paths = [item["path"] for item in result]
    if len(paths) != len(set(paths)):
        raise ValueError("작업 문서 경로 중복")
    for role in {"implementation", "verification", "ui_design"}:
        if sum(item["role"] == role for item in result) > 1:
            raise ValueError("역할의 기준 문서는 하나만 등록: " + role)
    return result


def safe_document(plan_path, relative):
    part = PurePosixPath(relative)
    if (not relative or part.is_absolute() or "\\" in relative or ":" in relative
            or any(p in {"", ".", ".."} for p in relative.split("/"))
            or part.suffix != ".md" or relative in {"plan.md", "changelog.md"}):
        raise ValueError("작업 내부 Markdown 상대 경로가 필요합니다")
    root = Path(plan_path).absolute().parent
    candidate = root
    for name in part.parts:
        candidate = candidate / name
        if candidate.is_symlink():
            raise ValueError("작업 문서 symlink는 따라가지 않습니다")
    if not candidate.is_file():
        raise ValueError("선택 문서 없음: " + relative)
    return candidate


def inspect(plan_path, before_approval=False, roles=None):
    """Return findings, never certify semantic correspondence."""
    plan = Path(plan_path)
    result = {"layout": "", "documents": [], "issues": []}
    try:
        text = plan.read_text(encoding="utf-8")
        layout = field(text, "문서구성")
        result["layout"] = layout or "single-v1"
        if layout in {"", "single-v1"}:
            return result
        if layout != "roles-v1":
            raise ValueError("알 수 없는 문서구성: " + layout)
        records = registrations(text)
        if 'mpa-doc:' in section(text, '요구사항 명세'):
            raise ValueError('작업 문서 등록은 요구사항 명세 밖에 둡니다')
        selected_paths = {item['path'] for item in records}
        for relative in re.findall(r'\]\(([^)]+\.md)\)', section(text, '선택 문서')):
            if relative not in selected_paths:
                raise ValueError('선택 문서의 명시 등록 없음: ' + relative)
        ready = not before_approval and field(text, "상태") in READY_STATES
        draft = not before_approval and field(text, "상태") in {"설계 중", "작성 중"}
        for record in records:
            if roles is not None and record["role"] not in roles:
                continue
            item = dict(record)
            result["documents"].append(item)
            try:
                path = safe_document(plan, record["path"])
                content = path.read_text(encoding="utf-8")
                item["current_basis_sha256"] = basis_hash(content)
                if not content.strip():
                    raise ValueError("선택 문서가 비어 있습니다: " + record["path"])
                if record["role"] == "implementation" and not section(content, "설계 기준"):
                    raise ValueError("implementation 설계 기준 섹션 없음")
                if ready:
                    if record.get("spec") != field(text, "승인해시") or not record.get("spec", "").startswith("reqspec-v1:"):
                        raise ValueError("선택 문서 기준명세 연결 미완료: " + record["path"])
                    if record.get("basis_sha256") != item["current_basis_sha256"]:
                        raise ValueError("선택 문서 기준 내용 재확인 필요: " + record["path"])
            except (OSError, ValueError, UnicodeError) as error:
                # Missing draft files may be in preparation; an unsafe path is not.
                if draft and str(error).startswith("선택 문서 없음:"):
                    item["pending"] = str(error)
                else:
                    result["issues"].append(str(error))
    except (OSError, ValueError, UnicodeError) as error:
        result["issues"].append(str(error))
    return result


def issue(plan_path, before_approval=False):
    problems = inspect(plan_path, before_approval)["issues"]
    return "작업 문서 연결 확인 필요: " + "; ".join(problems) if problems else None


def inputs(plan_path, stage):
    """Return reusable role input text, excluding implementation progress in review1."""
    if stage not in {"critique", "implement", "review1", "review2"}:
        raise ValueError("알 수 없는 입력 단계: " + stage)
    text = Path(plan_path).read_text(encoding="utf-8")
    if stage != "critique":
        if field(text, "상태") not in READY_STATES:
            raise ValueError("구현 승인 이후 상태에서만 실행/검증 입력을 생성합니다")
        from plan_hash import parse, approval_hash_issue
        front_matter, body, _ = parse(str(plan_path))
        approval_issue = approval_hash_issue(front_matter, body, str(plan_path), check_documents=False)
        if approval_issue:
            raise ValueError(approval_issue)
    roles = {"implementation", "verification", "ui_design"} if stage in {"implement", "review1"} else None
    check = inspect(plan_path, before_approval=(stage == "critique"), roles=roles)
    if check["issues"]:
        raise ValueError("; ".join(check["issues"]))
    front_end = text.find("\n---", 4) if text.startswith("---\n") else -1
    base = {
        "source": "plan.md",
        "content": "\n\n".join(filter(None, [
            text[:front_end + 4] if front_end >= 0 else "",
            section(text, "요구사항 명세"),
            section(text, "선택 문서"),
            section(text, "설계 기준"),
            section(text, "검증 기준") or section(text, "검증 체크리스트", 3),
        ])),
    }
    # Pre-reqspec plans have no fixed requirement headings. Preserve their
    # reviewed basis for critique instead of silently returning metadata only.
    # This never changes execution approval or the isolated review1 input.
    legacy_critique = (
        stage == "critique" and check["layout"] == "single-v1"
        and field(text, "승인대상") != "요구사항 명세"
        and not field(text, "승인해시").startswith("reqspec-v1:")
        and not section(text, "요구사항 명세")
    )
    if legacy_critique:
        base["content"] = basis_text(text)
        # Old plans may keep verification criteria under a result heading.
        criteria = basis_text(section(text, "검증 체크리스트", 3))
        if criteria and criteria not in base["content"]:
            base["content"] += "\n\n" + criteria
    result = [base]
    if stage == "review1" and not section(text, "설계 기준") and not any(
            d["role"] == "implementation" for d in check["documents"]):
        legacy_design = section(text, "실행 계획 (Implementation Plan)")
        criteria = [section(legacy_design, title, 3) for title in (
            "생략 항목과 사유", "사전 조사", "예상 조용한 결정",
            "반례 (이 계획이 실패할 수 있는 시나리오)")]
        if any(criteria):
            result.append({"source": "plan.md 기존 설계 기준",
                           "content": "\n\n".join(filter(None, criteria))})
    for record in check["documents"]:
        if record.get("pending"):
            raise ValueError(record["pending"])
        role = record["role"]
        content = safe_document(plan_path, record["path"]).read_text(encoding="utf-8")
        if stage == "review1":
            if role == "implementation":
                content = section(content, "설계 기준")
            elif role in {"verification", "ui_design"}:
                content = basis_text(content)
            else:
                continue
        elif stage == "implement":
            if role == "implementation":
                content = basis_text(content)
            elif role not in {"verification", "ui_design"}:
                continue
        elif stage == "critique":
            content = basis_text(content)
        result.append({"source": record["path"], "content": content})
    if stage in {"implement", "critique"} and not legacy_critique and not any(
            d["role"] == "implementation" for d in check["documents"]):
        fallback = section(text, "실행 계획") or section(text, "실행 계획 (Implementation Plan)")
        if fallback:
            result.append({"source": "plan.md 실행 계획", "content": fallback})
    if stage == "review2":
        # The second pass needs execution claims, including single-document plans.
        result[0]["content"] = text
        history = Path(plan_path).parent / "changelog.md"
        if history.is_file() and not history.is_symlink():
            result.append({"source": "changelog.md", "content": history.read_text(encoding="utf-8")})
    return result


def main():
    parser = argparse.ArgumentParser(description="Read-only optional task document inspection")
    parser.add_argument("command", choices=["inspect", "inputs"])
    parser.add_argument("plan")
    parser.add_argument("--stage", choices=["critique", "implement", "review1", "review2"], default="review1")
    parser.add_argument("--before-approval", action="store_true")
    args = parser.parse_args()
    try:
        result = inspect(args.plan, args.before_approval) if args.command == "inspect" else inputs(args.plan, args.stage)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if isinstance(result, dict) and result["issues"] else 0
    except (OSError, ValueError, UnicodeError) as error:
        print(json.dumps({"issues": [str(error)]}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
