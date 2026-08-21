import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / ".mpa/runtime"


class TodoPolicyTest(unittest.TestCase):
    def test_source_uses_single_plan_template_for_all_task_types(self):
        template = (SOURCE / "templates/plan_template.md").read_text(encoding="utf-8")
        rules = (SOURCE / "core/agent_rules.md").read_text(encoding="utf-8")
        detail = (SOURCE / "core/agent_rules_detail.md").read_text(encoding="utf-8")
        design = (SOURCE / "inject/layer1_design.md").read_text(encoding="utf-8")

        self.assertFalse((SOURCE / "templates/minor_plan_template.md").exists())
        self.assertIn("이번 작업 항목 종료 전 증빙", template)
        self.assertIn("구현·설계·검증이 추가로 필요한 후속 작업은 새 작업 항목", template)
        self.assertIn("사용자·운영자가 수행할 행동", template)
        self.assertIn("이번 작업 항목이 끝나기 전 증빙", rules)
        self.assertIn("구현·설계·검증이 추가로 필요한 후속 작업은 별도 작업 항목", rules)
        self.assertIn("공통 `templates/plan_template.md`를 Read하여 작성한다", detail)
        self.assertNotIn("minor_plan_template.md", detail)
        self.assertIn("이번 태스크 종료 전 증빙", design)


if __name__ == "__main__":
    unittest.main()
