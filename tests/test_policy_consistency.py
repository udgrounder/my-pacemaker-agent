"""Bounded policy-reference regression checks, not a natural-language verifier.

Behavioral evidence for gate boundaries uses the actual script. Semantic policy
cases and host integration need separate review; see the task's policy audit.
"""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / ".mpa/runtime"
PRIORITY = "inject/_agent_execution_priority.md"
DETAIL = "core/agent_rules_detail.md"
CORE = "core/agent_rules.md"

# Stage workers need these references even when they have not loaded core.
REFERENCES = {
    CORE: (PRIORITY, DETAIL),
    DETAIL: (CORE, PRIORITY),
    "core/session_protocol.md": (CORE, DETAIL, PRIORITY),
    "inject/layer1_design.md": (DETAIL,),
    "inject/layer1_implement.md": (CORE, DETAIL, PRIORITY),
    "inject/layer1_critique.md": (PRIORITY,),
    "inject/layer1_review.md": (CORE, PRIORITY),
    "inject/layer1_discovery.md": (CORE,),
    "personas/mpa_system_designer.md": (CORE, PRIORITY),
    "personas/implementer.md": (CORE,),
    "templates/plan_template.md": (CORE, DETAIL),
    "skills/analysis/discovery_classification.md": (CORE,),
}
for workflow in ("new_feature", "bug_fix", "refactoring", "code_review", "team_collaboration"):
    REFERENCES[f"workflows/{workflow}.md"] = (CORE, DETAIL, PRIORITY)

RETIRED = (
    "자가 비평/검증으로 대체",
    "서브에이전트(1순위) → 자가 비평",
    "사용자 응답 후 plan.md를 작성",
    "모든 inject 파일 = 새 스레드 시작",
    "반드시 새 스레드",
    "진행 방향을 알려주세요",
    "비평: 새 스레드 원칙 / 환경 미지원 시 같은 스레드 허용",
    "plan.md 상태 `검토 완료` → INDEX의 원래 태스크 행 제거 → `done/`으로 이동",
    "plan.md 상태 `검토 완료` + `done/` 이동 완료 확인",
    "완료 승인됐습니다. done으로 이동할까요?",
    "스레드: 🆕 새 스레드",
)


def reference_issues(documents):
    issues = []
    for source, targets in REFERENCES.items():
        for target in targets:
            if target not in documents:
                issues.append(f"missing policy file: {target}")
            if target not in documents.get(source, ""):
                issues.append(f"missing reference: {source} -> {target}")
    for source, text in documents.items():
        for phrase in RETIRED:
            if phrase in text:
                issues.append(f"retired instruction: {source}: {phrase}")
    return issues


class PolicyReferenceTest(unittest.TestCase):
    def load(self, root):
        return {str(p.relative_to(root)): p.read_text(encoding="utf-8")
                for folder in ("core", "inject", "workflows", "personas", "templates", "skills/analysis")
                for p in (root / folder).glob("*.md")}

    def test_source_and_distribution_references(self):
        for root in (RUNTIME, ROOT / "dist/.mpa/runtime"):
            with self.subTest(root=str(root)):
                self.assertEqual(reference_issues(self.load(root)), [])

    def test_detects_missing_stage_reference(self):
        docs = self.load(RUNTIME)
        key = "inject/layer1_implement.md"
        docs[key] = docs[key].replace(DETAIL, "missing-detail.md")
        self.assertIn(f"missing reference: {key} -> {DETAIL}", reference_issues(docs))

    def test_detects_missing_definition_and_retired_fallback(self):
        docs = self.load(RUNTIME)
        del docs[PRIORITY]
        docs["inject/layer1_critique.md"] += "\n자가 비평/검증으로 대체"
        issues = reference_issues(docs)
        self.assertIn(f"missing policy file: {PRIORITY}", issues)
        self.assertTrue(any(i.startswith("retired instruction:") for i in issues))

    def test_current_memory_does_not_restore_retired_fallback(self):
        text = (ROOT / "workspace/memory/shared/architecture.md").read_text(encoding="utf-8")
        self.assertEqual(reference_issues({**self.load(RUNTIME), "architecture.md": text}), [])

    def test_minor_fast_path_requires_approved_implementation(self):
        implement = (RUNTIME / "inject/layer1_implement.md").read_text(encoding="utf-8")
        self.assertIn("상태: 구현 중", implement)
        self.assertIn("유효한 `reqspec-v1:` 승인해시", implement)
        self.assertIn("구현·최소 확인을 시작하지 않고", implement)

    def test_runtime_sync_does_not_instruct_target_deployment(self):
        detail = (RUNTIME / "core/agent_rules_detail.md").read_text(encoding="utf-8")
        designer = (RUNTIME / "personas/mpa_system_designer.md").read_text(encoding="utf-8")
        for text in (detail, designer):
            self.assertIn("설치 대상 갱신은", text)
            self.assertIn("명시적 릴리즈·배포 요청", text)
            self.assertNotIn("dist/`와 설치본 양쪽 동기화 필수", text)

    def test_detects_completion_bypass_in_discovery(self):
        docs = self.load(RUNTIME)
        docs["inject/layer1_discovery.md"] += (
            "\nplan.md 상태 `검토 완료` → INDEX의 원래 태스크 행 제거 → `done/`으로 이동"
        )
        self.assertTrue(any("retired instruction: inject/layer1_discovery.md" in issue
                            for issue in reference_issues(docs)))


class GateBoundaryTest(unittest.TestCase):
    def run_gate(self, tool_input, mode="block", tool="Edit"):
        with tempfile.TemporaryDirectory() as directory:
            payload = {"cwd": directory, "tool_name": tool, "tool_input": tool_input}
            return subprocess.run(
                ["python3", str(RUNTIME / "hooks/code_gate.py"), "--agent", "codex"],
                input=json.dumps(payload), text=True, capture_output=True,
                env={**os.environ, "MPA_GATE": mode}, check=False,
            )

    def test_recognized_source_without_task_blocks(self):
        self.assertEqual(self.run_gate({"file_path": "app.py"}).returncode, 2)

    def test_warn_reports_without_blocking_general_missing_task(self):
        result = self.run_gate({"file_path": "app.py"}, mode="warn")
        self.assertEqual(result.returncode, 0)
        self.assertIn("additionalContext", result.stdout)

    def test_off_skips_source_check(self):
        result = self.run_gate({"file_path": "app.py"}, mode="off")
        self.assertEqual((result.returncode, result.stdout), (0, ""))

    def test_documented_uncovered_paths_pass_even_in_block_mode(self):
        for name, payload, tool in (
            ("unknown path", {}, "Edit"),
            ("unknown tool", {"file_path": "app.py"}, "unknown_writer"),
            ("allowed prefix", {"file_path": "workspace/note.md"}, "Edit"),
            ("shell source write is not inspected", {"command": "touch app.py"}, "Bash"),
        ):
            with self.subTest(name=name):
                # The hook inspects this string; it never executes the command.
                self.assertEqual(self.run_gate(payload, tool=tool).returncode, 0)


if __name__ == "__main__":
    unittest.main()
