# 태스크: 구현 후 발견 처리 체계 구축

**요청일:** 2026-06-04
**상태:** 검토 완료
**파생 출처:** 없음 — mpaWork3 테스트 관찰에서 발견

---

## 목적

첫 결과물을 경험한 후 생기는 수정·추가 사항을 체계 안에서 구조화된 방식으로 처리하는 흐름을 만든다.

---

## 배경

계획서 기반 개발 후 사용자가 결과를 보면 "이미지와 다르다"는 피드백이 발생한다. 이것은 실패가 아니라 정보 획득(구현 후 발견)이다. 기존 체계에 이 시나리오를 처리하는 경로가 없었다.

---

## 구현된 내용

- `dist/.mpa-workspace/inject/layer1_discovery.md` 신규 — 발견 항목 수집 → 분류 → 유형별 처리 세션
- `dist/.mpa-workspace/skills/analysis/discovery_classification.md` 신규 — 조정/계획 확장/신규 태스크 분류 기준
- `dist/.mpa-workspace/templates/plan_template.md` — "구현 후 발견" 섹션 추가
- `dist/.mpa-workspace/inject/layer1_review.md` — 추가 작업 확인 후 종료 처리 흐름 추가
- `dist/.mpa-workspace/core/session_protocol.md` — layer1_discovery 세션 등록
- `guidebook/guidebook.md` — 구현 후 발견, 전진 증류 원칙, 관련 용어 추가

---

## 핵심 결정

- 발견 항목 유형: 조정(기존 plan 범위) / 계획 확장(plan 보완) / 신규 태스크(별도 사이클)
- 신규 태스크 등록 후 원래 태스크 종료 — 순서 원칙
- 태스크 계보(파생 출처)는 사람용 메타데이터. 에이전트가 부모 plan.md를 추적하는 메커니즘으로 쓰지 않는다
