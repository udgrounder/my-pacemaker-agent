# Changelog — Layer 2 트리거 개선 (문제 7)

## 수정 파일

### `dist/.mpa-workspace/core/agent_rules.md`
- 작업 완료 섹션 4번: 태스크 타입 기록 규칙 신규 추가
  - major/minor 정의 테이블 추가 (경계 불명확 시 major로 분류)
  - INDEX.md 컬럼 형식에 타입 컬럼 추가
- 작업 완료 섹션 5번 (기존 4번): Layer 2 트리거 로직 교체
  - 기존: done 태스크 수 3개 이상 → 단순 카운트
  - 변경: major 1개 이상 → 즉시 제안 / minor만 5개 이상 → 제안
  - 타입 컬럼 없는 기존 태스크는 minor로 간주
  - Layer 2 제안 메시지에 major/minor 누적 수 표시

### `workspace/tasks/INDEX.md`
- 타입 컬럼 추가 (기존 태스크 소급 분류)
  - major: MPA시스템개선, post_impl_discovery, direction_memory, review_gate_strengthen, routing_improvement
  - minor: critique_criteria_unify, failure_cost_calibration

## 계획 이탈 없음
