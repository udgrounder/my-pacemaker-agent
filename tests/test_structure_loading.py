"""Regression checks for the split between always-loaded and on-demand policy."""

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_ROOTS = (ROOT / ".mpa/runtime", ROOT / "dist/.mpa/runtime")
CORE_BASELINE_BYTES = 34_731
ROUTE_CONTRACTS = (
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


if __name__ == "__main__":
    unittest.main()
