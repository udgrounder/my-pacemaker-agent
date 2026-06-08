---
태스크: direction_memory
생성일: 2026-06-04
타입: minor
실패비용: minor
상태: 완료 승인
승인해시: ""
---
# 태스크: 방향 메모리 및 전진 증류 원칙

**요청일:** 2026-06-04
**상태:** 검토 완료
**파생 출처:** 20260604_post_impl_discovery — 신규 태스크 간 방향 연속성 문제

---

## 목적

태스크가 늘어날수록 방향 연속성을 유지하는 구조를 만든다. 과거 plan.md를 읽는 방식이 아닌, 배운 것을 shared/ 파일로 증류하는 방식으로.

---

## 배경

구현 후 발견으로 신규 태스크가 생길 때, 부모 태스크의 맥락을 이어받는 방법이 필요하다. "부모 plan.md를 읽는다"는 접근은 태스크가 쌓일수록 불가능해진다. 근본 해법은 방향 연속성을 전진 방향으로 증류하는 것이다.

---

## 구현된 내용

- `dist/.mpa-workspace/templates/direction_template.md` 신규 — 제품/UX 방향 메모리 템플릿
- `dist/.mpa-workspace/inject/layer1_design.md` — `direction.md` 읽기 추가
- `dist/.mpa-workspace/inject/layer1_implement.md` — 방향 증류 단계 추가 (의무)
- `dist/.mpa-workspace/inject/layer1_discovery.md` — direction.md 업데이트 단계 추가
- `dist/.mpa-workspace/inject/layer2_checkpoint.md` — direction.md 정합성 점검 추가
- `dist/.mpa-workspace/personas/memory_curator.md` — direction.md 유지보수 기준 추가
- `workspace/memory/shared/direction.md` 신규 (이 프로젝트)

---

## 핵심 결정

**전진 증류 원칙:** shared/ 파일들이 항상 현재 상태를 정확히 반영하면, 어떤 태스크도 과거를 거슬러 읽을 필요가 없다.

- `architecture.md` = 기술 결정 (어떻게 만드는가)
- `direction.md` = 제품/UX 방향 (무엇이, 어떻게 느껴져야 하는가)
- 둘 다 스냅샷이며 append 누적 금지
