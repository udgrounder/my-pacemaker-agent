import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / ".mpa-workspace"
RUNTIME = ROOT / "dist/.mpa-workspace"


class TodoPolicyTest(unittest.TestCase):
    def assert_policy(self, workspace):
        major = (workspace / "templates/plan_template.md").read_text(encoding="utf-8")
        minor = (workspace / "templates/minor_plan_template.md").read_text(encoding="utf-8")
        rules = (workspace / "core/agent_rules.md").read_text(encoding="utf-8")
        detail = (workspace / "core/agent_rules_detail.md").read_text(encoding="utf-8")
        design = (workspace / "inject/layer1_design.md").read_text(encoding="utf-8")

        self.assertIn("이번 작업 항목 종료 전 증빙", major)
        self.assertIn("구현·설계·검증이 추가로 필요한 후속 작업은 새 작업 항목", major)
        self.assertIn("사용자·운영자가 수행할 행동", major)
        self.assertIn("이번 작업 항목 종료 전 증빙", minor)
        self.assertIn("구현·설계·검증이 추가로 필요한 후속 작업은 새 작업 항목", minor)
        self.assertIn("이번 작업 항목이 끝나기 전 증빙", rules)
        self.assertIn("구현·설계·검증이 추가로 필요한 후속 작업은 별도 작업 항목", rules)
        self.assertIn("templates/minor_plan_template.md", detail)
        self.assertNotIn("`templates/plan_template.md`를 Read하여 작성한다", detail)
        self.assertIn("이번 태스크 종료 전 증빙", design)

    def test_source_and_packaged_runtime_include_todo_policy(self):
        self.assert_policy(SOURCE)
        self.assert_policy(RUNTIME)

    def test_installed_runtime_includes_todo_policy(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "project"
            result = subprocess.run(
                ["python3", "install.py", "--project", str(target), "--agents", "codex"],
                cwd=ROOT, text=True, capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assert_policy(target / ".mpa-workspace")


if __name__ == "__main__":
    unittest.main()
