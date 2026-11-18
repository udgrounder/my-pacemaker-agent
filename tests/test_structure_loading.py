"""Regression checks for the split between always-loaded and on-demand policy."""

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_ROOTS = (ROOT / ".mpa/runtime", ROOT / "dist/.mpa/runtime")
CORE_BASELINE_BYTES = 34_731
ROUTE_CONTRACTS = (
    ("approval transaction recovery", "core/agent_rules.md", "승인 저장 중단 복구 필요", "core/agent_rules_detail.md", "## 승인 이력 저장과 복구"),
    ("simple question", "core/agent_rules.md", "사용자 부담 최소화", "core/agent_rules.md", "| 단순 질문/탐색 | 없음 | on-demand |"),
    ("major design", "core/agent_rules.md", "layer1_design.md", "inject/layer1_design.md", "## major 설계 절차"),
    ("major approval", "core/agent_rules.md", '"승인 기록 처리"', "core/agent_rules_detail.md", "## 승인 기록 처리"),
    ("minor execution", "core/agent_rules.md", '"minor 경량 처리 절차"', "core/agent_rules_detail.md", "## minor 경량 처리 절차"),
    ("minor plan only", "inject/layer1_design.md", "계획만 요청했으면 구현하지 않는다", "core/agent_rules_detail.md", "공통 `templates/plan_template.md`를 Read하여 작성한다"),
    ("spec renewal", "core/agent_rules.md", "명세 해시 재검증", "core/agent_rules_detail.md", "renew-spec"),
    ("completion", "core/agent_rules.md", '"작업 항목 완료 처리"', "core/agent_rules_detail.md", "## 작업 항목 완료 처리"),
    ("resume", "core/agent_rules.md", "작업 항목 재개", "core/agent_rules_detail.md", "## 태스크 재개"),
    ("critique", "core/agent_rules.md", "layer1_critique.md", "inject/layer1_critique.md", "독립 비평"),
    ("review", "core/agent_rules.md", "layer1_review.md", "inject/layer1_review.md", "독립"),
    ("runtime modification", "core/agent_rules.md", "MPA 파일 수정", "core/agent_rules_detail.md", "## MPA 파일 수정 세부"),
)


def section(text: str, heading: str) -> str:
    start = text.index(heading)
    next_heading = text.find("\n## ", start + len(heading))
    return text[start:] if next_heading == -1 else text[start:next_heading]


DETAIL = "core/agent_rules_detail.md"
MANAGEMENT = "계획서와 변경 이력 관리"
LAYER2 = "Layer 2 현황 표시"
CONSUMER_ROUTES = (
    ("inject/layer1_design.md", "## 문서 선택 선행", MANAGEMENT),
    ("inject/layer1_implement.md", "## 역할 입력 선행", MANAGEMENT),
    ("inject/layer1_review.md", "## 역할 입력 우선", MANAGEMENT),
    ("inject/layer1_discovery.md", "## 역할 내용 위치", MANAGEMENT),
    (DETAIL, "## minor 경량 처리 절차", MANAGEMENT),
    (DETAIL, "## 태스크 재개", MANAGEMENT),
    ("core/session_protocol.md", "## 세션 재개 (중단된 세션 이어가기)", MANAGEMENT),
    (DETAIL, "## 작업 항목 완료 처리", LAYER2),
    ("inject/layer2_checkpoint.md", "## 세션 종료 시", LAYER2),
)


def policy_text(text):
    """Ignore fenced examples; an example heading is not an executable route."""
    lines = []
    fence = None
    for line in text.splitlines():
        match = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence is None:
            if match:
                fence = match.group(1)
                continue
            lines.append(line)
        elif match and match.group(1)[0] == fence[0] and len(match.group(1)) >= len(fence) and not match.group(2).strip():
            fence = None
    return "\n".join(lines)


def exact_section(text, heading):
    lines = policy_text(text).splitlines()
    matches = [i for i, line in enumerate(lines) if line.rstrip() == heading]
    if len(matches) != 1:
        raise ValueError(f"missing or ambiguous heading: {heading}")
    start = matches[0]
    level = len(heading.split(" ", 1)[0])
    stop = next((i for i in range(start + 1, len(lines))
                 if re.match(r"^#{1," + str(level) + r"} ", lines[i])), len(lines))
    return "\n".join(lines[start:stop])


def load_policy_documents(root):
    return {str(p.relative_to(root)): p.read_text(encoding="utf-8")
            for p in root.rglob("*.md")}


def loading_route_issues(documents):
    """Same bounded checker for real Runtime documents and mutated fixtures."""
    issues = []
    core = documents.get("core/agent_rules.md", "")
    try:
        table = exact_section(core, "## 상세 파일 로드 트리거")
    except ValueError as error:
        return [str(error)]
    rows = []
    for line in table.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.split("|")[1:-1]]
        if len(cells) != 2 or cells[0] == "트리거 조건" or set(cells[0]) <= {"-"}:
            continue
        condition, target = cells
        files = re.findall(r"`((?:core|inject|templates)/[^`]+\.md)`", target)
        headings = re.findall(r'"([^"]+)"', target)
        path = files[0] if files else DETAIL
        rows.append((condition, path, headings))
        if path not in documents:
            issues.append(f"missing trigger file: {path}")
        elif headings:
            for name in headings:
                try:
                    exact_section(documents[path], "## " + name)
                except ValueError:
                    issues.append(f"missing trigger heading: {path}: {name}")
        elif not files:
            issues.append(f"unparseable trigger target: {target}")
    required_routes = (
        ("계획 문서 생성·편집 전", MANAGEMENT),
        ("검증 입력 준비 전", MANAGEMENT),
        ("재개 시", MANAGEMENT),
        ("Layer 2 현황 표시 시점", LAYER2),
        ('사용자가 "이어서 해줘"', "태스크 재개"),
    )
    for condition, expected_heading in required_routes:
        matching = [(path, names) for trigger, path, names in rows if condition in trigger]
        if not matching:
            issues.append(f"missing trigger condition: {condition}")
        elif any(path != DETAIL or names != [expected_heading] for path, names in matching):
            issues.append(f"wrong trigger target: {condition}: {DETAIL}: {expected_heading}")
    for source, heading, target in CONSUMER_ROUTES:
        try:
            body = exact_section(documents.get(source, ""), heading)
        except ValueError:
            issues.append(f"missing consumer section: {source}: {heading}")
            continue
        reference = f'`{DETAIL}`의 "{target}"'
        if reference not in body:
            issues.append(f"missing consumer reference: {source}: {heading}: {target}")
        try:
            exact_section(documents.get(DETAIL, ""), "## " + target)
        except ValueError:
            issues.append(f"missing consumer target: {DETAIL}: {target}")
    return issues


class StructureLoadingTest(unittest.TestCase):
    def test_source_and_distribution_keep_on_demand_policy_routes(self):
        for root in RUNTIME_ROOTS:
            for name, start_file, trigger, target_file, target_section in ROUTE_CONTRACTS:
                with self.subTest(root=root, route=name):
                    self.assertIn(trigger, (root / start_file).read_text(encoding="utf-8"))
                    self.assertIn(target_section, (root / target_file).read_text(encoding="utf-8"))

            with self.subTest(root=root, route="implementation approval"):
                implement = (root / "inject/layer1_implement.md").read_text(encoding="utf-8")
                self.assertIn('"승인 기록 처리"', implement)

    def test_minor_detail_keeps_its_direct_template_path(self):
        for root in RUNTIME_ROOTS:
            with self.subTest(root=root):
                detail = (root / "core/agent_rules_detail.md").read_text(encoding="utf-8")
                minor = section(detail, "## minor 경량 처리 절차")
                self.assertIn("공통 `templates/plan_template.md`를 Read하여 작성한다", minor)
                self.assertNotIn("inject/layer1_design.md", minor)

    def test_pending_approval_recovery_is_reachable_before_reapproval(self):
        for root in RUNTIME_ROOTS:
            detail = (root / "core/agent_rules_detail.md").read_text(encoding="utf-8")
            for heading in ("## 프론트매터 누락 처리", "## 구현 승인 재확인", "## 승인 기록 처리"):
                with self.subTest(root=root, heading=heading):
                    self.assertIn("승인 이력 저장과 복구", section(detail, heading))
                    self.assertIn(".plan-renewal.json", section(detail, heading))

    def test_source_and_distribution_runtime_files_are_identical(self):
        source = RUNTIME_ROOTS[0]
        distribution = RUNTIME_ROOTS[1]
        source_files = sorted(path.relative_to(source) for path in source.rglob("*") if path.is_file())
        distribution_files = sorted(path.relative_to(distribution) for path in distribution.rglob("*") if path.is_file())
        self.assertEqual(source_files, distribution_files)
        for relative in source_files:
            with self.subTest(path=relative):
                self.assertEqual((source / relative).read_bytes(), (distribution / relative).read_bytes())

    def test_core_is_smaller_than_the_recorded_pre_refactor_baseline(self):
        core = ROOT / ".mpa/runtime/core/agent_rules.md"
        self.assertLess(len(core.read_bytes()), CORE_BASELINE_BYTES)


class ActualLoadingRoutesTest(unittest.TestCase):
    def test_real_trigger_table_and_consumers_in_both_runtimes(self):
        for root in RUNTIME_ROOTS:
            with self.subTest(root=root):
                self.assertEqual(loading_route_issues(load_policy_documents(root)), [])

    def test_detects_deleted_and_renamed_target_heading(self):
        for name in (MANAGEMENT, LAYER2):
            for replacement in ("", "## " + name + " 변경"):
                with self.subTest(name=name, replacement=replacement):
                    docs = load_policy_documents(RUNTIME_ROOTS[0])
                    docs[DETAIL] = docs[DETAIL].replace("## " + name + "\n", replacement + "\n")
                    self.assertTrue(any("target" in issue or "heading" in issue
                                        for issue in loading_route_issues(docs)))

    def test_example_heading_cannot_mask_missing_target(self):
        for fence in ("```markdown", "~~~markdown"):
            docs = load_policy_documents(RUNTIME_ROOTS[0])
            docs[DETAIL] = docs[DETAIL].replace("## " + LAYER2 + "\n", "## renamed\n")
            docs[DETAIL] += "\n" + fence + "\n## " + LAYER2 + "\n" + fence[:3] + "\n"
            self.assertIn(f"missing trigger heading: {DETAIL}: {LAYER2}", loading_route_issues(docs))

    def test_detects_deleted_trigger_and_wrong_trigger_file(self):
        docs = load_policy_documents(RUNTIME_ROOTS[0])
        original = docs["core/agent_rules.md"]
        row = next(line for line in original.splitlines() if line.startswith("|") and "Layer 2 현황 표시 시점" in line)
        docs["core/agent_rules.md"] = original.replace(row, "")
        self.assertTrue(any("missing trigger condition" in issue for issue in loading_route_issues(docs)))
        docs["core/agent_rules.md"] = original.replace(row, row.replace(f'"{LAYER2}"', f'`core/glossary.md`의 "{LAYER2}"'))
        self.assertIn(f"missing trigger heading: core/glossary.md: {LAYER2}", loading_route_issues(docs))

    def test_detects_valid_but_wrong_trigger_heading(self):
        docs = load_policy_documents(RUNTIME_ROOTS[0])
        original = docs["core/agent_rules.md"]
        row = next(line for line in original.splitlines() if line.startswith("|") and "Layer 2 현황 표시 시점" in line)
        docs["core/agent_rules.md"] = original.replace(row, row.replace(f'"{LAYER2}"', f'"{MANAGEMENT}"'))
        self.assertTrue(any("wrong trigger target" in issue for issue in loading_route_issues(docs)))

    def test_detects_missing_management_load_events(self):
        for removed in ("검증 입력 준비 전·", "·재개 시"):
            with self.subTest(removed=removed):
                docs = load_policy_documents(RUNTIME_ROOTS[0])
                core = docs["core/agent_rules.md"]
                row = next(line for line in core.splitlines() if line.startswith("|") and "계획 문서 생성·편집 전" in line)
                docs["core/agent_rules.md"] = core.replace(row, row.replace(removed, ""))
                self.assertTrue(any("missing trigger condition" in issue for issue in loading_route_issues(docs)))

    def test_detects_broken_consumer_edges_with_target_still_present(self):
        for source, heading, target in CONSUMER_ROUTES:
            for replacement in ("", f'`core/glossary.md`의 "{target}"'):
                with self.subTest(source=source, heading=heading, replacement=replacement):
                    docs = {path: policy_text(text) for path, text in
                            load_policy_documents(RUNTIME_ROOTS[0]).items()}
                    body = exact_section(docs[source], heading)
                    broken = body.replace(f'`{DETAIL}`의 "{target}"', replacement)
                    # The replacement is scoped to this actual consumer section.
                    # Mutations occur only in this in-memory copy.
                    docs[source] = docs[source].replace(body, broken)
                    self.assertIn(f"missing consumer reference: {source}: {heading}: {target}",
                                  loading_route_issues(docs))

    def test_protection_rules_are_reachable_in_the_new_owner(self):
        for root in RUNTIME_ROOTS:
            docs = load_policy_documents(root)
            self.assertEqual(loading_route_issues(docs), [])
            management = exact_section(docs[DETAIL], "## " + MANAGEMENT)
            for phrase in ("갱신 담당자 한 명", ".plan-renewal.json", "문서 편집을 중단",
                           "충돌 시 확보 파일·JSON을 보존", "현재 미확인·재검증 필요",
                           "1차 독립 검증에서도 확인", "실패 증거를 삭제"):
                with self.subTest(root=root, phrase=phrase):
                    self.assertIn(phrase, management)

    def test_layer2_keeps_uncertainty_and_completion_marker_boundary(self):
        for root in RUNTIME_ROOTS:
            text = exact_section(load_policy_documents(root)[DETAIL], "## " + LAYER2)
            for phrase in ("major 1개 이상", "minor만 5개 이상", "minor의 현황 표시는 기본 생략",
                           "집계 미확인", "생성일·폴더명을 완료 시각으로 대체하지 않고",
                           "같은 날 선후관계 불명", "명시적 전체 점검 요청은 횟수와 무관",
                           "제안만 했거나 점검 중단·미완료이면 새 마커를 쓰지 않는다",
                           "과거 마커는 보존", "중복 추가하지 않는다"):
                with self.subTest(root=root, phrase=phrase):
                    self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
