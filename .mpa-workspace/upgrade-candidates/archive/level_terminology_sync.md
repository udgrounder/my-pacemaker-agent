# [처리] 승인 — 2026-06-05
# 자율성 레벨 용어 동기화
**타입**: 방법론 개선
**발견 상황**: failure_cost_grade 태스크 — Level 1/2/3 → major/normal/minor 변경 작업 중

## 현재 상황
`layer1_design.md`, `layer1_implement.md`, `agent_rules.md`, `layer1_review.md`는 `major/normal/minor`로 업데이트됐으나 아래 파일에 구식 용어가 남아 있음:

- `.mpa-workspace/core/session_protocol.md` — "자율성 레벨 1~4" 개념 사용 (별도 개념일 수 있으므로 확인 필요)
- `.mpa-workspace/workflows/new_feature.md` — "자율성 레벨" 참조
- `.mpa-workspace/templates/project_rules_template.md` — "레벨 2 — 초안" 기본값 참조

## 적용 대상 파일
- `.mpa-workspace/core/session_protocol.md`
- `.mpa-workspace/workflows/new_feature.md`
- `.mpa-workspace/templates/project_rules_template.md`
