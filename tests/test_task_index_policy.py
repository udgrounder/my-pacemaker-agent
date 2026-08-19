import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TaskIndexPolicyTest(unittest.TestCase):
    def assert_runtime_policy(self, runtime):
        rules = (runtime / "core/agent_rules.md").read_text(encoding="utf-8")
        detail = (runtime / "core/agent_rules_detail.md").read_text(encoding="utf-8")
        design = (runtime / "inject/layer1_design.md").read_text(encoding="utf-8")
        implement = (runtime / "inject/layer1_implement.md").read_text(encoding="utf-8")
        checkpoint = (runtime / "inject/layer2_checkpoint.md").read_text(encoding="utf-8")

        self.assertIn("active/hold 폴더에 맞는 행만 남기고", rules)
        self.assertIn("해당 active/hold 행을 제거", rules)
        self.assertIn("`tasks/done/`은 과거 결정의 근거가 현재 기준만으로 불명확할 때만 선택적으로 참조", rules)
        self.assertIn("새 태스크 행을 `상태: active`로 추가", detail)
        self.assertIn("INDEX는 현재 처리할 **생명주기 상태**(`active`/`hold`)만", design)
        self.assertIn("해당 active/hold 항목을 제거", implement)
        self.assertIn("done 태스크를 INDEX에 등록하지 않는다", checkpoint)
        self.assertIn("현재 점검의 기본 입력이 아니며", checkpoint)

    def assert_index_policy(self, index):
        text = index.read_text(encoding="utf-8")
        self.assertIn("| 태스크명 | 타입 | 상태 | 요약 | 생성일 |", text)
        self.assertNotIn("완료일", text)
        self.assertNotIn("| done |", text)
        self.assertIn("[Layer 2 완료]", text)

    def test_source_runtime_and_current_index_use_active_hold_only(self):
        self.assert_runtime_policy(ROOT / ".mpa-workspace")
        self.assert_runtime_policy(ROOT / "dist/.mpa-workspace")
        self.assert_index_policy(ROOT / "workspace/tasks/INDEX.md")
        self.assert_index_policy(ROOT / "dist/workspace/tasks/INDEX.md")

    def test_new_install_has_active_hold_only_index(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "project"
            result = subprocess.run(
                ["python3", "install.py", "--project", str(target), "--agents", "codex"],
                cwd=ROOT, text=True, capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assert_index_policy(target / "workspace/tasks/INDEX.md")


if __name__ == "__main__":
    unittest.main()
