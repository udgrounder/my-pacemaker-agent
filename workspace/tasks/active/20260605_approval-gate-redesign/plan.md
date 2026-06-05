---
태스크: approval-gate-redesign
생성일: 2026-06-05
타입: major
실패비용: major
상태: 구현 중
점검: 미점검
승인해시: ""
---

# 작업 계획서: 승인 게이트 재설계

## 목적
.approved 파일 기반 게이트를 제거하고, plan.md YAML 프론트매터 상태 기반 7단계 모델로 교체한다.

## 구현 단계

- [x] 1. `templates/plan_template.md` — YAML 프론트매터 추가, 상태값 업데이트
- [x] 2. `hooks/code_gate.py` — YAML 파싱, Bash mv 인터셉트, 구현 중만 허용
- [x] 3. `hooks/session_start.py` — YAML 파싱으로 상태 읽기 통일
- [x] 4. `core/agent_rules.md` — 7단계 모델 반영, .approved 제거
- [x] 5. `inject/layer1_implement.md` — .approved 제거, 단계 전이 업데이트
- [x] 6. `inject/layer1_review.md` — 검증 중·테스트 중 단계 반영
- [x] 7. `dist/` 전체 동기화

## 확정 단계 모델
설계 중 → 설계 완료 ⛔GATE1 → 구현 중 → 검증 중 → 테스트 중 → 검토 완료 ⛔GATE2 → 완료 승인 → done

## GATE 규칙
- GATE 1: 설계 완료→구현 중, plan.md 수정 시 재승인 필요
- GATE 2: 검토 완료→완료 승인, Bash mv done/ 차단
- 소스 수정: 구현 중 상태만 허용
