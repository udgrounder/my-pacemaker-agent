import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class NextActionTerminologyTest(unittest.TestCase):
    def test_runtime_uses_next_action_proposal_not_task_prediction(self):
        runtime = ROOT / ".mpa-workspace"
        files = [
            runtime / "core/agent_rules.md",
            runtime / "core/agent_rules_detail.md",
            runtime / "core/glossary.md",
            runtime / "inject/layer0_init.md",
            runtime / "inject/layer1_design.md",
            runtime / "inject/layer1_discovery.md",
            runtime / "inject/layer1_implement.md",
        ]
        combined = "\n".join(path.read_text(encoding="utf-8") for path in files)
        self.assertIn("다음 행동 제안", combined)
        self.assertNotIn("다음 작업 예측", combined)
        self.assertIn("새 작업 항목 등록은 가능한 선택지 중 하나", combined)


if __name__ == "__main__":
    unittest.main()
