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

        self.assertIn("일반 작업은 해당 active/hold 행만 편집한다", rules)
        self.assertIn("전체 정리는 사용자가 명시적으로 요청한 범위에서만", rules)
        self.assertIn("조회 시 저장하지 않는다", rules)
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
        self.assert_runtime_policy(ROOT / ".mpa/runtime")
        self.assert_runtime_policy(ROOT / "dist/.mpa/runtime")
        self.assert_index_policy(ROOT / "workspace/tasks/INDEX.md")
        self.assert_index_policy(ROOT / "dist/workspace/tasks/INDEX.md")

    def test_edit_routes_consult_shared_safety_before_writing(self):
        from test_structure_loading import exact_section

        reference = '`core/agent_rules_detail.md`의 "작업 INDEX 편집 안전성"'
        routes = (
            ("core/agent_rules_detail.md", "## 작업 항목 완료 처리", "해당 active/hold 행만 제거"),
            ("inject/layer1_design.md", "## major 설계 절차", "active 행만 tasks/INDEX.md에 등록"),
            ("inject/layer1_discovery.md", "## 진행 순서", "새 작업 행만 등록"),
            ("inject/layer1_implement.md", "## 세션 종료 시", "해당 active/hold 항목을 제거"),
            ("inject/layer2_checkpoint.md", "### 7. INDEX vs 태스크 폴더 동기화", "INDEX에 추가"),
        )
        def reads_before_write(body, write):
            read_at = body.find(reference)
            write_at = body.find(write)
            return 0 <= read_at < write_at

        for runtime in (ROOT / ".mpa/runtime", ROOT / "dist/.mpa/runtime"):
            for filename, heading, write in routes:
                with self.subTest(runtime=runtime, filename=filename):
                    body = exact_section((runtime / filename).read_text(), heading)
                    self.assertTrue(reads_before_write(body, write))
                    missing = body.replace(reference, "")
                    late = missing.replace(write, write + reference, 1)
                    self.assertFalse(reads_before_write(missing, write))
                    self.assertFalse(reads_before_write(late, write))

    def test_shared_index_guardrails_are_in_the_relevant_stages(self):
        from test_structure_loading import exact_section

        cases = (
            ("core/agent_rules_detail.md", "## 태스크 재개",
             ("정확한 작업 경로", "목적지만 남아 있어도 최종 대조", "다른 완료 이력을 탐색하지 않는다")),
            ("inject/layer1_design.md", "## major 설계 절차",
             ("마지막 점검 후 바뀌었으면", "변경된 기준을 승인 직전에 대조")),
            ("core/agent_rules_detail.md", "## 작업 INDEX 편집 안전성",
             ("다른 행의 누락·중복·경로 불일치 때문에 현재 작업을 막거나",
              "다른 행의 상대 순서는 유지", "표 헤더·구분선·설명·빈 줄·과거 마커",
              "별개 행만 바뀌었으면 그 변경을 보존한 최신 원문",
              "전체 이전본으로 덮어쓰거나 done 이력으로 추정 복구하지 않는다")),
            ("core/agent_rules_detail.md", "## 작업 항목 완료 처리",
             ("원본만 있으면 재등록된 행", "목적지만 있으면",
              "양쪽 존재·부재 또는 승인 불명이면 보류", "후속 편집을 덮지 않는 경우에만")),
            ("inject/layer2_checkpoint.md", "### 7. INDEX vs 태스크 폴더 동기화",
             ("전체 대조 요청이 없으면", "대조·보고만 요청됐다면 차이를 보고",
              "아래 조치는 사용자가 INDEX 정리까지 요청한 범위")),
            ("core/agent_rules_detail.md", "## 공통 방법론 계획의 범위 점검",
             ("선택 설계·검증 문서의 기준", "식별자와 사례는 출처·근거로 추적",
              "위치·이름·직간접 참조", "그 사례가 합격 여부를 좌우",
              "프로젝트 전용 계획의 고유 계약은 유지")),
        )
        for runtime in (ROOT / ".mpa/runtime", ROOT / "dist/.mpa/runtime"):
            for filename, heading, criteria in cases:
                with self.subTest(runtime=runtime, heading=heading):
                    body = exact_section((runtime / filename).read_text(), heading)
                    for criterion in criteria:
                        self.assertIn(criterion, body)

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
