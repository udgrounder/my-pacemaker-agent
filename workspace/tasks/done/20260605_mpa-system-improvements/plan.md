---
태스크: mpa-system-improvements
생성일: 2026-06-05
타입: major
실패비용: major
상태: 완료 승인
점검: 미점검
승인해시: ""
---

# MPA 시스템 개선: 평가 기반 8개 이슈 처리

## 목적
MPA 시스템 평가에서 발견된 결함을 우선순위 순서대로 수정한다.

## 구현 단계

### 🔴 즉시
- [x] #1. `hooks/code_gate.py` — 승인해시 없을 때 현재 상태 자동 등록 + `parse_plan_fields` 따옴표 파싱 버그 수정
- [x] #2. `hooks/code_gate.py` — `.md` 전면 허용 제거, ALLOW_PREFIXES로 일원화

### 🟡 단기
- [x] #3. `agent_rules.md` — `minor` 경량 흐름 분기 (단계 모델·작업 생성·작업 완료 3곳 수정)
- [x] #4. `hooks/dist_sync.py` 신규 + `settings.json` PostToolUse 등록 — .mpa-workspace/ 저장 시 dist/ 자동 동기화
- [x] #5. `agent_rules.md` — 두 메모리 시스템 우선순위 원칙 추가 (workspace/ 우선, 세션 메모리 보조)

### 🟢 중기
- [x] #6. `inject/layer1_critique.md` — 서브에이전트 없는 환경: 구체적 자가 비평 절차 추가 (제약 3개 + 체크리스트 5개)
- [x] #7. `agent_rules.md` + `agent_rules_detail.md` — routing_mismatches.md 제거, upgrade-candidates/ 타입 A로 일반화
- [x] #8. `inject/layer2_checkpoint.md` — 사용자 회고(외부 감사) 단계 추가 (항목 #8, 완료 기준 반영)

## 진행 방식
각 이슈를 하나씩 사용자와 확인하며 처리. 각 단계 완료 후 dist/ 동기화.

### 재평가 후 추가 수정 (6개)
- [x] R1. `session_start.py` — `.approved 마커` 구식 메시지 수정
- [x] R2. `agent_rules.md` — minor 완료 처리 4단계 명시 + `완료 승인` 상태 설정 포함
- [x] R3. `code_gate.py` — `check_hash_integrity` `return` → `continue` (전체 태스크 검사)
- [x] R4. `layer1_design.md` — minor 판단 시 경량 흐름 전환 참조 추가
- [x] R5. `code_gate.py` — GATE 2 차단 메시지에 우회 방법 동일 규칙 명시
- [x] R6. `dist_sync.py` — `dist/` 없는 환경 조기 종료 가드 추가

## 결정 이력
| 시점 | 결정 내용 | 근거 |
|------|---------|------|
| 설계 | 8개 이슈 우선순위 결정 | MPA 시스템 전체 평가 결과 |
