# changelog — zone_differentiation

## 수정 파일

### `.mpa-workspace/core/agent_rules.md`
- **추가:** `## 사용자 개입 등급` 섹션 (Zone 1/2/3 정의 테이블)
- **수정:** "작업 생성" 단계 4-5 — 전체 계획서 제시 → 가치 결정/고영향 가정만 추출해 제시 (Zone 2)
- **추가:** "작업 진행" 단계 2 — 실패 비용 Level 1 구현 시작 전 하드게이트 (Zone 1)
- **수정:** "작업 완료" Layer 2 트리거 — major(Zone 2 강조) / minor(Zone 3 한 줄)로 분리

### `.mpa-workspace/inject/layer1_design.md`
- **수정:** 세션 종료 단계 6 — 계획서 제시 방식을 agent_rules.md와 동일하게 변경

### `.mpa-workspace/inject/layer1_review.md`
- **수정:** 세션 종료 단계 5 — 리포트 응답 요구를 🚨(Zone 2 필수) / ⚠️(Zone 3 선택) / ✅(Zone 3 자동)으로 차별화

### `.mpa-workspace/inject/layer1_implement.md`
- **수정:** 세션 종료 항목 — "확인하고 업데이트" → "자동 처리 후 변경 내용 간략 고지"로 전환 (Zone 3)

### `dist/.mpa-workspace/` 동기화
- 위 4개 파일 dist/에 복사 완료
