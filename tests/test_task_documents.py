"""Behavioral checks for optional documents, approval readiness and role input isolation."""
import importlib.util
import itertools
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
HOOKS = ROOT / ".mpa/runtime/hooks"
sys.path.insert(0, str(HOOKS))
import task_documents as docs
import plan_hash
import code_gate
import session_start

HEADER = """---
태스크: example
생성일: 2026-10-14
타입: major
실패비용: major
상태: 설계 완료
승인해시: ""
승인대상: 요구사항 명세
문서구성: roles-v1
---
"""
SPEC = "\n## 요구사항 명세\n\n### 완료 기준\n- 요구사항을 충족한다.\n"
IMPLEMENTATION = """# 구현
**기준 상태:** 초안
**담당:** 구현 담당
## 설계 기준
구조 계약
```text
## 진행 기록
FENCE_CONTENT
```
## 실행 계획
- [ ] 구현 항목 EXECUTION_CANARY
## 진행 기록
PROGRESS_CANARY
"""
VERIFICATION = "# 검증\n## 검증 기준\n실패 경로와 실제 소스를 확인한다.\n"


class TaskDocumentsTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.plan = self.root / "plan.md"

    def write_plan(self, records=(), header=HEADER, suffix=""):
        markers = "\n".join("<!-- mpa-doc: " + json.dumps(x) + " -->" for x in records)
        self.plan.write_text(header + SPEC + "\n## 선택 문서\n" + markers + suffix, encoding="utf-8")

    def write_doc(self, path, role="implementation"):
        doc = self.root / path
        doc.parent.mkdir(parents=True, exist_ok=True)
        doc.write_text(IMPLEMENTATION if role == "implementation" else VERIFICATION, encoding="utf-8")
        return doc

    def bind(self, records):
        self.write_plan(records)
        fm, body, _ = plan_hash.parse(str(self.plan))
        spec = plan_hash.compute_for_plan(fm, body)
        bound = [{**x, "spec": spec, "basis_sha256": docs.basis_hash((self.root / x["path"]).read_text())}
                 for x in records]
        header = HEADER.replace("설계 완료", "구현 중").replace('승인해시: ""', "승인해시: " + spec)
        self.write_plan(bound, header)
        return bound

    def cli(self, command, *args):
        return subprocess.run([sys.executable, str(HOOKS / "plan_hash.py"), command,
                               str(self.plan), *args], capture_output=True, text=True)

    def test_all_optional_combinations_for_major_and_minor(self):
        roles = ["implementation", "verification", "ui_design"]
        for kind, count in itertools.product(["major", "minor"], range(4)):
            for subset in itertools.combinations(roles, count):
                records = [{"role": role, "path": role + ".md"} for role in subset]
                for record in records:
                    self.write_doc(record["path"], record["role"])
                self.write_plan(records, HEADER.replace("타입: major", "타입: " + kind))
                with self.subTest(kind=kind, roles=subset):
                    self.assertEqual([], docs.inspect(self.plan)["issues"])
                    self.assertEqual(len(subset), len(docs.inspect(self.plan)["documents"]))

    def test_legacy_layout_and_unselected_files_are_unchanged(self):
        self.write_doc("implementation.md")
        self.write_plan([], HEADER.replace("문서구성: roles-v1\n", ""))
        self.assertEqual([], docs.inspect(self.plan)["documents"])
        self.assertEqual([], docs.inspect(self.plan)["issues"])
        self.write_plan([])
        self.assertEqual([], docs.inspect(self.plan)["documents"])

    def test_missing_selected_file_draft_vs_approval(self):
        records = [{"role": "verification", "path": "verification.md"}]
        self.write_plan(records, HEADER.replace("설계 완료", "설계 중"))
        self.assertEqual([], docs.inspect(self.plan)["issues"])
        self.assertTrue(docs.inspect(self.plan)["documents"][0]["pending"])
        self.assertTrue(docs.inspect(self.plan, before_approval=True)["issues"])
        self.write_plan(records)
        original = self.plan.read_text()
        result = self.cli("approve")
        self.assertEqual(2, result.returncode)
        self.assertEqual(original, self.plan.read_text())

    def test_approve_and_metadata_recovery_without_reapproval(self):
        self.write_doc("implementation.md")
        records = [{"role": "implementation", "path": "implementation.md"}]
        self.write_plan(records)
        self.assertEqual(0, self.cli("approve").returncode)
        approved = plan_hash.get_field(plan_hash.parse(str(self.plan))[0], "승인해시")
        self.assertIn("기준명세", docs.issue(self.plan))
        self.assertEqual(1, self.cli("check").returncode)
        self.assertEqual(2, self.cli("approve").returncode)
        self.bind(records)
        self.assertEqual(approved, plan_hash.get_field(plan_hash.parse(str(self.plan))[0], "승인해시"))
        self.assertEqual(0, self.cli("check").returncode)
        self.assertEqual([], plan_hash.audit(str(self.plan))["invalid"])

    def test_partial_connection_then_resume(self):
        records = [{"role": role, "path": role + ".md"} for role in ["implementation", "verification"]]
        for record in records:
            self.write_doc(record["path"], record["role"])
        bound = self.bind(records)
        partial = [bound[0], records[1]]
        self.write_plan(partial, self.plan.read_text().split("---", 2)[1].join(["---", "---\n"]))
        self.assertTrue(docs.inspect(self.plan)["issues"])
        self.bind(records)
        self.assertEqual([], docs.inspect(self.plan)["issues"])

    def test_semantic_change_invalidates_basis_but_progress_does_not(self):
        doc = self.write_doc("implementation.md")
        records = [{"role": "implementation", "path": "implementation.md"}]
        self.bind(records)
        doc.write_text(doc.read_text().replace("[ ]", "[x]").replace("PROGRESS_CANARY", "새 진행 결과"))
        self.assertEqual([], docs.inspect(self.plan)["issues"])
        doc.write_text(doc.read_text().replace("구조 계약", "변경된 구조 계약"))
        self.assertIn("기준 내용", docs.issue(self.plan))

    def test_verification_basis_and_spec_change_invalidate_connection(self):
        doc = self.write_doc("verification.md", "verification")
        self.bind([{"role": "verification", "path": "verification.md"}])
        doc.write_text(doc.read_text().replace("실패 경로", "정상 경로만"))
        self.assertIn("기준 내용", docs.issue(self.plan))
        self.bind([{"role": "verification", "path": "verification.md"}])
        self.plan.write_text(self.plan.read_text().replace("reqspec-v1:", "reqspec-v1:0", 1))
        self.assertIn("기준명세", docs.issue(self.plan))

    def test_role_inputs_exclude_claims_and_keep_fenced_design(self):
        for role in ["implementation", "verification"]:
            self.write_doc(role + ".md", role)
        self.bind([{"role": role, "path": role + ".md"} for role in ["implementation", "verification"]])
        self.plan.write_text(self.plan.read_text() + "\n## 현재 상태\nPLAN_CANARY\n")
        (self.root / "changelog.md").write_text("HISTORY_CANARY")
        first = json.dumps(docs.inputs(self.plan, "review1"))
        self.assertIn("FENCE_CONTENT", first)
        for canary in ["PROGRESS_CANARY", "EXECUTION_CANARY", "PLAN_CANARY", "HISTORY_CANARY"]:
            self.assertNotIn(canary, first)
        second = json.dumps(docs.inputs(self.plan, "review2"))
        self.assertIn("PROGRESS_CANARY", second)
        self.assertIn("HISTORY_CANARY", second)

    def test_minimal_single_plan_inputs(self):
        self.bind([])
        self.plan.write_text(self.plan.read_text() + "\n## 설계 기준\n설계\n## 실행 계획\n실행\n## 검증 기준\n검증\n## 현재 상태\nPLAN_CANARY")
        first = str(docs.inputs(self.plan, "review1"))
        self.assertIn("설계", first)
        self.assertIn("검증", first)
        self.assertNotIn("PLAN_CANARY", first)
        self.assertIn("실행", str(docs.inputs(self.plan, "implement")))
        second = str(docs.inputs(self.plan, "review2"))
        self.assertIn("실행", second)
        self.assertIn("PLAN_CANARY", second)

    def test_large_research_nested_path_is_optional_and_registered(self):
        self.write_doc("research/topic/brief.md", "research")
        self.bind([{"role": "research", "path": "research/topic/brief.md"}])
        self.assertEqual([], docs.inspect(self.plan)["issues"])
        self.assertFalse(any(x["source"] == "research/topic/brief.md" for x in docs.inputs(self.plan, "review1")))
        self.assertIn("research/topic", str(docs.inputs(self.plan, "critique")))

    def test_pre_reqspec_critique_preserves_original_basis_without_migration(self):
        body = """
## 목적
LEGACY_PURPOSE
## 핵심 기능
LEGACY_FEATURE
## 구현 계획
- [x] LEGACY_STEP
## 프로젝트 고유 계약
LEGACY_CUSTOM_CONTRACT
### 검증 체크리스트
- [x] LEGACY_INLINE_CRITERION
```text
## 현재 상태
LEGACY_FENCED_EXAMPLE
```
"""
        digest = plan_hash.compute(body)
        for status, layout in itertools.product(["설계 중", "설계 완료"], ["", "문서구성: single-v1\n"]):
            header = ("---\n타입: major\n상태: " + status
                      + "\n승인해시: " + (digest if status == "설계 완료" else '""')
                      + "\n" + layout + "---\n")
            original = header + body
            self.plan.write_text(original, encoding="utf-8")
            with self.subTest(status=status, layout=layout):
                result = docs.inputs(self.plan, "critique")
                self.assertEqual(1, len(result))
                content = result[0]["content"]
                for token in ["LEGACY_PURPOSE", "LEGACY_FEATURE", "LEGACY_STEP",
                              "LEGACY_CUSTOM_CONTRACT", "LEGACY_FENCED_EXAMPLE"]:
                    self.assertIn(token, content)
                self.assertIn("- [ ] LEGACY_STEP", content)
                self.assertEqual(1, content.count("LEGACY_STEP"))
                self.assertEqual(1, content.count("LEGACY_INLINE_CRITERION"))
                self.assertEqual(original, self.plan.read_text(encoding="utf-8"))
        cli = subprocess.run([sys.executable, str(HOOKS / "task_documents.py"), "inputs",
                              str(self.plan), "--stage", "critique"], capture_output=True, text=True)
        self.assertEqual(0, cli.returncode, cli.stdout + cli.stderr)
        self.assertIn("LEGACY_PURPOSE", json.loads(cli.stdout)[0]["content"])
        self.assertEqual(original, self.plan.read_text(encoding="utf-8"))

    def test_pre_reqspec_critique_keeps_criteria_excludes_progress_and_results(self):
        self.plan.write_text("""---
상태: 설계 중
승인해시: ""
---
## 목적
LEGACY_PURPOSE
## 실행 계획
- [x] LEGACY_STEP
## 진행 기록
LEGACY_PROGRESS
## 실행 결과
LEGACY_EXECUTION_RESULT
## 검증 결과
LEGACY_RESULT_CLAIM
### 검증 체크리스트
- [x] LEGACY_CRITERION
### 확인 결과
LEGACY_CHECK_RESULT
## 현재 상태
LEGACY_STATUS
## 추가 제약
LEGACY_CONSTRAINT
""", encoding="utf-8")
        content = str(docs.inputs(self.plan, "critique"))
        for token in ["LEGACY_PURPOSE", "LEGACY_STEP", "LEGACY_CRITERION", "LEGACY_CONSTRAINT"]:
            self.assertIn(token, content)
        for token in ["LEGACY_PROGRESS", "LEGACY_EXECUTION_RESULT", "LEGACY_RESULT_CLAIM",
                      "LEGACY_CHECK_RESULT", "LEGACY_STATUS"]:
            self.assertNotIn(token, content)
        self.assertEqual(1, content.count("LEGACY_STEP"))

    def test_reqspec_single_plan_does_not_use_legacy_critique_fallback(self):
        for layout in ["", "문서구성: single-v1\n", "문서구성: roles-v1\n"]:
            header = HEADER.replace("문서구성: roles-v1\n", layout)
            self.write_plan([], header, suffix="\n## 현재 상태\nMODERN_PROGRESS\n## 프로젝트 기록\nMODERN_UNSELECTED")
            with self.subTest(layout=layout):
                content = str(docs.inputs(self.plan, "critique"))
                self.assertIn("요구사항을 충족한다.", content)
                self.assertNotIn("MODERN_PROGRESS", content)
                self.assertNotIn("MODERN_UNSELECTED", content)

    def test_execution_inputs_require_approval_and_no_pending_renewal(self):
        self.write_plan([])
        self.assertTrue(docs.inputs(self.plan, "critique"))
        for stage in ["implement", "review1", "review2"]:
            with self.subTest(stage=stage), self.assertRaisesRegex(ValueError, "승인 이후"):
                docs.inputs(self.plan, stage)
        self.bind([])
        approved = self.plan.read_text()
        self.plan.write_text(approved.replace("요구사항을 충족한다.", "새 요구사항"))
        for stage in ["implement", "review1", "review2"]:
            with self.subTest(stage=stage), self.assertRaisesRegex(ValueError, "일치하지"):
                docs.inputs(self.plan, stage)
        self.plan.write_text(approved)
        (self.root / ".plan-renewal.json").write_text("{}")
        for stage in ["implement", "review1", "review2"]:
            with self.subTest(stage=stage), self.assertRaisesRegex(ValueError, "복구 필요"):
                docs.inputs(self.plan, stage)

    def test_legacy_design_criteria_retained_without_execution_claims(self):
        self.bind([])
        self.plan.write_text(self.plan.read_text() + """
## 실행 계획 (Implementation Plan)
### 사전 조사
LEGACY_RESEARCH
### 구현 단계
LEGACY_EXECUTION
### 예상 조용한 결정
LEGACY_DESIGN
### 반례 (이 계획이 실패할 수 있는 시나리오)
LEGACY_COUNTEREXAMPLE
## 실행 TODO
LEGACY_DONE
## 검증 결과
### 검증 체크리스트
LEGACY_CRITERION
### 완료 시 문서 업데이트 대상
LEGACY_DOC_DONE
""")
        first = str(docs.inputs(self.plan, "review1"))
        for criterion in ["LEGACY_RESEARCH", "LEGACY_DESIGN", "LEGACY_COUNTEREXAMPLE", "LEGACY_CRITERION"]:
            self.assertIn(criterion, first)
        for claim in ["LEGACY_EXECUTION", "LEGACY_DONE", "LEGACY_DOC_DONE"]:
            self.assertNotIn(claim, first)
        second = str(docs.inputs(self.plan, "review2"))
        self.assertIn("LEGACY_EXECUTION", second)
        self.assertIn("LEGACY_DONE", second)

    def test_unrelated_missing_document_only_blocks_consuming_stages(self):
        records = [{"role": "research", "path": "research/brief.md"}]
        self.write_doc("research/brief.md", "research")
        self.bind(records)
        (self.root / "research/brief.md").unlink()
        self.assertTrue(docs.inspect(self.plan)["issues"])
        for stage in ["implement", "review1"]:
            self.assertTrue(docs.inputs(self.plan, stage))
        for stage in ["critique", "review2"]:
            with self.subTest(stage=stage), self.assertRaisesRegex(ValueError, "선택 문서 없음"):
                docs.inputs(self.plan, stage)

    def test_bad_registry_and_paths_are_rejected(self):
        bad = [
            [{"role": "unknown", "path": "a.md"}],
            [{"role": [], "path": "a.md"}],
            [{"role": {"nested": "work"}, "path": "a.md"}],
            [{"role": "work", "path": "../a.md"}],
            [{"role": "work", "path": "/tmp/a.md"}],
            [{"role": "work", "path": "a\\b.md"}],
            [{"role": "work", "path": "plan.md"}],
            [{"role": "work", "path": "a.md", "typo": 1}],
            [{"role": "work", "path": "a.md", "spec": 123}],
            [{"role": "work", "path": "a.md", "basis_sha256": None}],
            [{"role": "work", "path": "a.md"}, {"role": "work", "path": "a.md"}],
        ]
        for records in bad:
            self.write_plan(records)
            self.assertTrue(docs.inspect(self.plan)["issues"], records)
        self.write_plan([])
        self.plan.write_text(self.plan.read_text() + '\n<!-- mpa-doc: {"role":"work","role":"research","path":"a.md"} -->')
        self.assertTrue(docs.inspect(self.plan)["issues"])
        self.write_plan([])
        self.plan.write_text(self.plan.read_text() + "\n<!-- mpa-doc: broken -->")
        self.assertTrue(docs.inspect(self.plan)["issues"])
        self.write_plan([], HEADER.replace("roles-v1", "future-v2"))
        self.assertTrue(docs.inspect(self.plan)["issues"])

    def test_symlink_cannot_read_outside_and_inspection_is_readonly(self):
        outside = self.root / "outside.md"
        outside.write_text("outside")
        (self.root / "link.md").symlink_to(outside)
        self.write_plan([{"role": "work", "path": "link.md"}])
        before = self.plan.read_bytes()
        self.assertIn("symlink", docs.issue(self.plan))
        self.assertEqual(before, self.plan.read_bytes())

    def test_registration_is_explicit_outside_spec_and_not_from_code_example(self):
        self.write_plan([], suffix='\n```text\n<!-- mpa-doc: {"role":"work","path":"missing.md"} -->\n```\n')
        self.assertEqual([], docs.inspect(self.plan)["issues"])
        self.write_plan([], suffix="\n| [verification.md](verification.md) |\n")
        self.assertIn("명시 등록", docs.issue(self.plan))
        self.write_plan([])
        self.plan.write_text(self.plan.read_text().replace(SPEC, SPEC + '\n<!-- mpa-doc: {"role":"work","path":"a.md"} -->\n'))
        self.assertIn("명세 밖", docs.issue(self.plan))

    def test_session_and_gate_diagnose_documents_without_reapproval(self):
        self.write_doc("implementation.md")
        self.bind([{"role": "implementation", "path": "implementation.md"}])
        (self.root / "implementation.md").unlink()
        invalid = plan_hash.audit(str(self.plan))["invalid"]
        self.assertEqual("작업 문서", invalid[0]["field"])
        missing, errors, has_front = session_start.audit_frontmatter(str(self.plan))
        self.assertTrue(has_front)
        self.assertTrue(errors)
        issue = plan_hash.approval_hash_issue(*plan_hash.parse(str(self.plan))[:2], str(self.plan))
        message = code_gate._approval_recovery_message("example", "구현 중", issue)
        self.assertIn("문서 문제 때문에 approve를 반복", message)
        self.assertNotIn("구현 승인 기록 복구 필요", message)


if __name__ == "__main__":
    unittest.main()
