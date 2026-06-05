# [처리] 승인 — 2026-06-05
---
타입: A
---

# minor 태스크 완료 시 INDEX.md 업데이트 누락 패턴

## 현상
세션 내 마지막 minor 태스크 완료 후 INDEX.md 업데이트가 누락됨.
(20260605_minor-plan-request-section — 다음 세션에서 발견)

## 원인 추정
minor 완료 흐름이 빠르게 처리되면서 INDEX.md 업데이트 단계를 건너뜀.

## 개선 방향
minor 완료 흐름의 done 처리 단계에 INDEX.md 업데이트를 명시적 체크 항목으로 강조.
현재 agent_rules.md "작업 완료 — minor" 섹션에는 INDEX.md 업데이트가 포함되어 있으나
실제 실행 시 빠지는 경우가 있음 → 단계 설명을 더 명시적으로 강조하거나 순서를 재배치.
