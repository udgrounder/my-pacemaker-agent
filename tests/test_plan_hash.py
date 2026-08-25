import importlib.util
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("plan_hash", ROOT / ".mpa/runtime/hooks/plan_hash.py")
plan_hash = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(plan_hash)
HOOK_DIR = ROOT / ".mpa/runtime/hooks"
sys.path.insert(0, str(HOOK_DIR))
GATE_SPEC = importlib.util.spec_from_file_location("code_gate", HOOK_DIR / "code_gate.py")
code_gate = importlib.util.module_from_spec(GATE_SPEC)
GATE_SPEC.loader.exec_module(code_gate)
SESSION_SPEC = importlib.util.spec_from_file_location("session_start", HOOK_DIR / "session_start.py")
session_start = importlib.util.module_from_spec(SESSION_SPEC)
SESSION_SPEC.loader.exec_module(session_start)


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

MINOR_PLAN = """---
태스크: minor-example
생성일: 2026-08-21
타입: minor
실패비용: minor
상태: 작성 중
승인해시: ""
승인대상: 요구사항 명세
---
# 작업 계획서: minor example
## 요구사항 명세
### 요청 기준
작은 요청을 처리한다.
### 목적
작은 결과를 만든다.
### 범위·제외 범위
- 범위: 단일 파일
- 제외 범위: 구조 변경
### 완료 기준
- 결과가 확인된다.
### 사용자 결정
- 없음
### 변경 불가 제약
- 없음
### 에이전트 가정
- 없음
### 결정 대기 항목 (Open Questions)
- 없음
### minor 판단 근거
- 단일 관심사
## 실행 계획
### 구현 단계
1. 파일을 수정한다.
## 실행 TODO
- [ ] 검증한다.
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

    def run_gate_main(self, root, mode):
        stdout, stderr = io.StringIO(), io.StringIO()
        data = {
            "cwd": str(root),
            "tool_name": "apply_patch",
            "tool_input": {"file_path": str(root / "src.py")},
        }
        with mock.patch.dict(os.environ, {"MPA_GATE": mode}, clear=False), \
             mock.patch.object(sys, "argv", ["code_gate.py", "--agent", "codex"]), \
             mock.patch.object(sys, "stdin", io.StringIO(json.dumps(data))), \
             contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                code_gate.main()
            except SystemExit as error:
                return error.code, stdout.getvalue(), stderr.getvalue()
        return None, stdout.getvalue(), stderr.getvalue()

    def write_active_plan(self, root, content):
        path = root / "workspace/tasks/active/example/plan.md"
        path.parent.mkdir(parents=True)
        path.write_text(content, encoding="utf-8")

    def write_current_task(self, root, name="example"):
        path = root / "workspace/tasks/CURRENT_TASK"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(name + "\n", encoding="utf-8")

    def run_plan_hash_cli(self, *args):
        old_argv = sys.argv
        stdout, stderr = io.StringIO(), io.StringIO()
        try:
            sys.argv = ["plan_hash.py", *args]
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                try:
                    plan_hash.main()
                except SystemExit as error:
                    return error.code, stdout.getvalue(), stderr.getvalue()
        finally:
            sys.argv = old_argv
        return None, stdout.getvalue(), stderr.getvalue()

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

    def test_audit_rejects_manual_approval_date_in_post_approval_status(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "plan.md"
            invalid = NEW_PLAN.replace("상태: 구현 중", "상태: 검증 중").replace(
                "승인해시: oldhash", "승인해시: user-approved-2026-08-21"
            )
            path.write_text(invalid, encoding="utf-8")
            result = plan_hash.audit(str(path))
            self.assertEqual(result["missing"], [])
            self.assertEqual(result["invalid"][0]["field"], "승인해시")
            self.assertIn("reqspec-v1:<16자리 소문자 16진수>", result["invalid"][0]["reason"])

    def test_audit_allows_matching_legacy_hash_before_approval(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "plan.md"
            body = "## 목적\n초기 목적\n## 구현 계획\n- [ ] 구현\n"
            path.write_text(
                "---\n상태: 설계 완료\n승인해시: " + plan_hash.compute(body) + "\n---\n" + body,
                encoding="utf-8",
            )
            self.assertEqual(plan_hash.audit(str(path))["invalid"], [])

    def test_audit_rejects_legacy_hash_in_post_approval_status(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "plan.md"
            body = "## 목적\n초기 목적\n## 구현 계획\n- [ ] 구현\n"
            path.write_text(
                "---\n상태: 검증 중\n승인해시: " + plan_hash.compute(body) + "\n---\n" + body,
                encoding="utf-8",
            )
            result = plan_hash.audit(str(path))
            self.assertEqual(result["invalid"][0]["field"], "승인해시")
            self.assertIn("reqspec-v1:<16자리 소문자 16진수>", result["invalid"][0]["reason"])

    def test_single_plan_template_supports_minor_specification_hash_format(self):
        template = (ROOT / ".mpa/runtime/templates/plan_template.md").read_text(encoding="utf-8")
        self.assertFalse((ROOT / ".mpa/runtime/templates/minor_plan_template.md").exists())
        self.assertIn("# 작업 계획서: [작업 항목명]", template)
        self.assertIn("승인대상: 요구사항 명세", template)
        self.assertIn("## 요구사항 명세", template)
        for heading in (
            "### 요청 기준", "### 목적", "### 범위·제외 범위", "### 완료 기준",
            "### 사용자 결정", "### 변경 불가 제약", "### 에이전트 가정",
            "### 결정 대기 항목 (Open Questions)", "### minor 판단 근거",
        ):
            self.assertIn(heading, template)

    def test_minor_specification_hash_excludes_execution_plan(self):
        _, front_matter, body = MINOR_PLAN.split("---\n", 2)
        baseline = plan_hash.compute_for_plan(front_matter, body)
        self.assertEqual(
            baseline,
            plan_hash.compute_for_plan(front_matter, body.replace("파일을 수정한다.", "다른 순서로 수정한다.")),
        )
        self.assertNotEqual(
            baseline,
            plan_hash.compute_for_plan(front_matter, body.replace("작은 결과를 만든다.", "다른 결과를 만든다.")),
        )

    def test_approve_rejects_legacy_plan_before_state_transition(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "plan.md"
            path.write_text(
                "---\n태스크: legacy\n타입: major\n상태: 설계 완료\n승인해시: \"\"\n---\n## 목적\n구형 계획\n",
                encoding="utf-8",
            )
            code, output, error = self.run_plan_hash_cli("approve", str(path))
            self.assertEqual(code, 2)
            self.assertEqual(output, "")
            self.assertIn("구형 plan은 자동 변환하지 않습니다", error)
            self.assertIn("상태: 설계 완료", path.read_text(encoding="utf-8"))

    def test_approve_transitions_current_plan_and_records_reqspec_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "plan.md"
            current = NEW_PLAN.replace("상태: 구현 중", "상태: 설계 완료").replace(
                "승인해시: oldhash", "승인해시: \"\""
            )
            path.write_text(current, encoding="utf-8")
            code, output, error = self.run_plan_hash_cli("approve", str(path))
            self.assertIsNone(code)
            self.assertIn("상태 → 구현 중", output)
            self.assertEqual(error, "")
            result = plan_hash.audit(str(path))
            self.assertEqual(result["missing"], [])
            self.assertEqual(result["invalid"], [])

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
            code, output, error = self.run_gate_main(root, "warn")
            self.assertEqual(code, 0)
            self.assertIn("승인해시가 현재 승인 대상과 일치하지 않습니다", output)
            self.assertEqual(error, "")
            code, output, error = self.run_gate(root, "block")
            self.assertEqual(code, 2)
            self.assertEqual(output, "")
            self.assertIn("승인해시가 현재 승인 대상과 일치하지 않습니다", error)

    def test_warn_mode_blocks_selected_critical_task_with_hash_issue(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            approved = self.new_plan_hash()
            critical = NEW_PLAN.replace("실패비용: major", "실패비용: critical").replace(
                "oldhash", approved
            ).replace("결과를 만든다.", "승인 뒤 변경된 결과를 만든다.")
            self.write_active_plan(root, critical)
            self.write_current_task(root)
            code, output, error = self.run_gate_main(root, "warn")
            self.assertEqual(code, 2)
            self.assertEqual(output, "")
            self.assertIn("계획 승인 기록 복구 필요", error)

    def test_warn_mode_does_not_block_unselected_critical_task_with_hash_issue(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            approved = self.new_plan_hash()
            critical = NEW_PLAN.replace("실패비용: major", "실패비용: critical").replace(
                "oldhash", approved
            ).replace("결과를 만든다.", "승인 뒤 변경된 결과를 만든다.")
            self.write_active_plan(root, critical)
            code, output, error = self.run_gate(root, "warn")
            self.assertEqual(code, 0)
            self.assertIn("계획 승인 기록 복구 필요", output)
            self.assertEqual(error, "")

    def test_warn_mode_blocks_selected_critical_task_before_approval(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pre_approval = NEW_PLAN.replace("실패비용: major", "실패비용: critical").replace(
                "상태: 구현 중", "상태: 설계 완료"
            ).replace("승인해시: oldhash", '승인해시: ""')
            self.write_active_plan(root, pre_approval)
            self.write_current_task(root)
            code, output, error = self.run_gate_main(root, "warn")
            self.assertEqual(code, 2)
            self.assertEqual(output, "")
            self.assertIn("critical 작업 시작 전 승인 필요", error)

    def test_current_task_rejects_path_traversal_value(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_current_task(root, "../other-task")
            self.assertIsNone(code_gate.read_current_task(str(root)))

    def test_gate_rejects_new_format_without_specification_heading(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            invalid = NEW_PLAN.replace("승인해시: oldhash", "승인해시: reqspec-v1:0123456789abcdef").replace(
                "## 요구사항 명세\n", ""
            )
            self.write_active_plan(root, invalid)
            code, output, error = self.run_gate(root, "warn")
            self.assertEqual(code, 0)
            self.assertIn("`## 요구사항 명세` 섹션이 누락", output)
            self.assertEqual(error, "")

    def test_gate_checks_manual_hash_in_verification_status(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            invalid = NEW_PLAN.replace("상태: 구현 중", "상태: 검증 중").replace(
                "승인해시: oldhash", "승인해시: user-approved-2026-08-21"
            )
            self.write_active_plan(root, invalid)
            code, output, error = self.run_gate(root, "warn")
            self.assertEqual(code, 0)
            self.assertIn("날짜·승인 문구", output)
            self.assertEqual(error, "")
            code, output, error = self.run_gate(root, "block")
            self.assertEqual(code, 2)
            self.assertEqual(output, "")
            self.assertIn("날짜·승인 문구", error)

    def test_session_start_marks_manual_hash_as_invalid(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            invalid = NEW_PLAN.replace("상태: 구현 중", "상태: 검증 중").replace(
                "승인해시: oldhash", "승인해시: user-approved-2026-08-21"
            )
            self.write_active_plan(root, invalid)
            message = session_start.build_message(str(root))
            self.assertIn("유효하지 않은 필드: 승인해시", message)
            self.assertIn("승인해시는 직접 입력하지 않고", message)

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
            self.assertIn("승인 이후 상태의 승인해시는", error)


if __name__ == "__main__":
    unittest.main()
