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
        review = (SOURCE / "inject/layer1_review.md").read_text(encoding="utf-8")

        self.assertFalse((SOURCE / "templates/minor_plan_template.md").exists())
        self.assertIn("이번 작업 항목 종료 전 증빙", template)
        self.assertIn("구현·설계·검증이 추가로 필요한 후속 작업은 새 작업 항목", template)
        self.assertIn("사용자·운영자가 수행할 행동", template)
        self.assertIn("이번 작업 항목이 끝나기 전 증빙", rules)
        self.assertIn("구현·설계·검증이 추가로 필요한 후속 작업은 별도 작업 항목", rules)
        self.assertIn("공통 `templates/plan_template.md`를 Read하여 작성한다", detail)
        self.assertNotIn("minor_plan_template.md", detail)
        self.assertIn("이번 태스크 종료 전 증빙", design)
        self.assertIn("### 작업 분류 판단 근거", template)
        self.assertIn("### 생략 항목과 사유", template)
        self.assertIn("형식적인 `없음`·`해당 없음`·`불필요`만으로 된 개별 사유는 쓰지 않는다", template)
        self.assertIn("[적용 조건] — [이 작업에서 생략해도 되는 사실]", template)
        self.assertIn("대상 섹션 | 이전 판단 | 새 판단 | 근거 | 명세 영향", template)
        self.assertIn("생략 항목과 사유", design)
        self.assertIn("각 행이 실제 적용 조건과 작업 사실에 맞는지 대조함", design)
        self.assertIn("자동 `approve` 전에", detail)
        self.assertIn("`확인 필요`이면", template)
        self.assertIn("대상 섹션·이전 판단·새 판단·근거·명세 영향", detail)
        self.assertIn("사용자 확인과 `renew-spec`", detail)
        self.assertIn("완료 시 문서 업데이트 대상", design)
        self.assertIn("초기 `생략 항목과 사유` 표", review)


if __name__ == "__main__":
    unittest.main()
