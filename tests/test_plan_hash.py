import importlib.util
import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("plan_hash", ROOT / ".mpa/runtime/hooks/plan_hash.py")
plan_hash = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(plan_hash)
HOOK_DIR = ROOT / ".mpa/runtime/hooks"
sys.path.insert(0, str(HOOK_DIR))
GATE_SPEC = importlib.util.spec_from_file_location("code_gate", HOOK_DIR / "code_gate.py")
code_gate = importlib.util.module_from_spec(GATE_SPEC)
GATE_SPEC.loader.exec_module(code_gate)


NEW_PLAN = """---
태스크: example
생성일: 2026-08-19
타입: major
실패비용: major
상태: 구현 중
승인해시: oldhash
승인대상: 요구사항 명세
---
## 요구사항 명세
목적: 결과를 만든다.
완료 기준: 결과가 검증된다.
## 실행 계획
- [ ] 구현한다.
## 검증 결과
- [ ] 아직 확인하지 않음
## 명세 변경 이력

"""


class PlanHashTest(unittest.TestCase):
    def new_plan_hash(self, content=NEW_PLAN):
        _, front_matter, body = content.split("---\n", 2)
        return plan_hash.compute_for_plan(front_matter, body)

    def run_gate(self, root, mode):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                code_gate.check_hash_integrity(str(root), mode, "codex")
            except SystemExit as error:
                return error.code, stdout.getvalue(), stderr.getvalue()
        return None, stdout.getvalue(), stderr.getvalue()

    def write_active_plan(self, root, content):
        path = root / "workspace/tasks/active/example/plan.md"
        path.parent.mkdir(parents=True)
        path.write_text(content, encoding="utf-8")

    def test_spec_hash_ignores_execution_and_verification_changes(self):
        baseline = plan_hash.compute(NEW_PLAN.split("---\n", 2)[2])
        changed = NEW_PLAN.replace("- [ ] 구현한다.", "- [x] 다른 방식으로 구현한다.")
        changed = changed.replace("- [ ] 아직 확인하지 않음", "- [x] 확인 완료")
        self.assertEqual(baseline, plan_hash.compute(changed.split("---\n", 2)[2]))

    def test_spec_hash_detects_spec_change(self):
        baseline = plan_hash.compute(NEW_PLAN.split("---\n", 2)[2])
        changed = NEW_PLAN.replace("결과를 만든다.", "다른 결과를 만든다.")
        self.assertNotEqual(baseline, plan_hash.compute(changed.split("---\n", 2)[2]))

    def test_legacy_plan_uses_existing_algorithm(self):
        legacy = "## 목적\n같음\n## 구현 계획\n- [ ] a\n"
        changed = "## 목적\n같음\n## 구현 계획\n- [x] b\n"
        self.assertEqual(plan_hash.compute(legacy), plan_hash.compute(changed))

    def test_renew_spec_preserves_status_and_records_history(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "plan.md"
            approved = self.new_plan_hash()
            path.write_text(NEW_PLAN.replace("oldhash", approved).replace("결과를 만든다.", "바뀐 결과를 만든다."), encoding="utf-8")
            old_hash, new_hash, _ = plan_hash.renew_spec(str(path), "목적 변경 승인")
            text = path.read_text(encoding="utf-8")
            self.assertNotEqual(old_hash, new_hash)
            self.assertIn("상태: 구현 중", text)
            self.assertIn("목적 변경 승인", text)
            self.assertIn(f"승인해시: {new_hash}", text)

    def test_renew_spec_appends_a_second_history_row(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "plan.md"
            initial = self.new_plan_hash()
            path.write_text(NEW_PLAN.replace("oldhash", initial).replace("결과를 만든다.", "첫 변경"), encoding="utf-8")
            _, first, _ = plan_hash.renew_spec(str(path), "첫 승인")
            path.write_text(path.read_text(encoding="utf-8").replace("첫 변경", "둘째 변경"), encoding="utf-8")
            _, second, _ = plan_hash.renew_spec(str(path), "둘째 승인")
            text = path.read_text(encoding="utf-8")
            self.assertEqual(text.count("| 승인 시각 | 이전 체크섬 | 새 체크섬 | 변경 요약 |"), 1)
            self.assertIn("첫 승인", text)
            self.assertIn("둘째 승인", text)
            self.assertIn(f"승인해시: {second}", text)
            self.assertNotEqual(first, second)

    def test_renew_spec_uses_exact_history_heading_not_inline_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "plan.md"
            initial = self.new_plan_hash()
            inline_reference = NEW_PLAN.replace(
                "## 실행 계획", "`## 명세 변경 이력`을 참고한다.\n## 실행 계획"
            ).replace("oldhash", initial).replace("결과를 만든다.", "변경된 결과")
            path.write_text(inline_reference, encoding="utf-8")
            _, new_hash, _ = plan_hash.renew_spec(str(path), "명세 승인")
            text = path.read_text(encoding="utf-8")
            self.assertIn("`## 명세 변경 이력`을 참고한다.", text)
            self.assertIn("| 승인 시각 | 이전 체크섬 | 새 체크섬 | 변경 요약 |", text)
            self.assertIn(f"승인해시: {new_hash}", text)

    def test_spec_format_rejects_missing_specification_heading(self):
        front = "\n".join([
            "태스크: example", "생성일: 2026-08-19", "타입: major", "실패비용: major",
            "상태: 구현 중", "승인해시: oldhash", "승인대상: 요구사항 명세",
        ])
        body = NEW_PLAN.split("---\n", 2)[2].replace("## 요구사항 명세\n", "")
        with self.assertRaises(ValueError):
            plan_hash.compute_for_plan(front, body)

    def test_header_alone_keeps_legacy_hash_behavior(self):
        front = "상태: 구현 중\n승인해시: legacyhash"
        body = NEW_PLAN.split("---\n", 2)[2]
        self.assertEqual(plan_hash.compute_for_plan(front, body), plan_hash.compute_legacy(body))
        self.assertFalse(plan_hash.compute_for_plan(front, body).startswith(plan_hash.SPEC_HASH_PREFIX))

    def test_unknown_hash_prefix_is_rejected(self):
        front = "상태: 구현 중\n승인해시: reqspec-v2:abcdef"
        body = NEW_PLAN.split("---\n", 2)[2]
        with self.assertRaises(ValueError):
            plan_hash.compute_for_plan(front, body)

    def test_gate_allows_new_plan_execution_only_change(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            approved = self.new_plan_hash()
            changed = NEW_PLAN.replace("oldhash", approved).replace("- [ ] 구현한다.", "- [x] 다른 방식으로 구현한다.")
            self.write_active_plan(root, changed)
            code, output, error = self.run_gate(root, "block")
            self.assertIsNone(code)
            self.assertEqual(output, "")
            self.assertEqual(error, "")

    def test_gate_warns_and_blocks_new_plan_spec_change(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            approved = self.new_plan_hash()
            changed = NEW_PLAN.replace("oldhash", approved).replace("결과를 만든다.", "다른 결과를 만든다.")
            self.write_active_plan(root, changed)
            code, output, error = self.run_gate(root, "warn")
            self.assertEqual(code, 0)
            self.assertIn("요구사항 명세가 변경됐는지 확인", output)
            self.assertEqual(error, "")
            code, output, error = self.run_gate(root, "block")
            self.assertEqual(code, 2)
            self.assertEqual(output, "")
            self.assertIn("요구사항 명세가 변경됐는지 확인", error)

    def test_gate_rejects_new_format_without_specification_heading(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            invalid = NEW_PLAN.replace("## 요구사항 명세\n", "")
            self.write_active_plan(root, invalid)
            code, output, error = self.run_gate(root, "warn")
            self.assertEqual(code, 0)
            self.assertIn("요구사항 명세 형식 오류", output)
            self.assertEqual(error, "")

    def test_gate_blocks_legacy_plan_requirement_change(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            legacy_body = "## 목적\n초기 목적\n## 구현 계획\n- [ ] 구현\n"
            approved = plan_hash.compute(legacy_body)
            legacy = "---\n상태: 구현 중\n승인해시: " + approved + "\n---\n" + legacy_body.replace("초기 목적", "변경된 목적")
            self.write_active_plan(root, legacy)
            code, output, error = self.run_gate(root, "block")
            self.assertEqual(code, 2)
            self.assertEqual(output, "")
            self.assertIn("구형 plan의 요구사항 변경", error)


if __name__ == "__main__":
    unittest.main()
