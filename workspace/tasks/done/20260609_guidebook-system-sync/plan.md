---
태스크: guidebook-system-sync
생성일: 2026-06-09
타입: minor
실패비용: minor
상태: 완료 승인
승인해시: bfe5b4d78bfca4d0
---
**목적:** 가이드북↔시스템 정합성 점검에서 발견된 불일치 수정 — 가이드북이 실제 시스템을 정확히 설명하도록(시스템이 정답, 가이드북 보강)
**요청:** "그래 진행해줘" (⚠️ 3건 수정, 강등한 contracts·수렴/발산은 손대지 않음)
### 핵심 기능
- 6.4 Layer 2 트리거: "3개 이상" → "major 1개+ 또는 minor 5개+" (agent_rules와 일치)
- 5.2 .mpa-workspace 구조 트리: hooks/·agent_rules_detail.md 누락 보강
- 8.2 페르소나 표: mpa_system_designer 추가
- 6.3/상태 모델: 검증 중(에이전트)·테스트 중(사용자) 단계 구분 설명 추가
### 에이전트 가정
- 강등 2건(contracts.md 선택적 파일, 수렴/발산 의도적 보류)은 수정 안 함 — 점검에서 확정
### minor 판단 근거
- 단일 관심사(가이드북을 시스템에 맞춤): O
- 설계 결정 불필요(수정 내용 점검에서 확정): O
- git reset 복구: O
- 취향·의사결정 불필요(사용자 승인): O
### 구현
1. guidebook 6.4 — Layer 2 트리거 수치 교정
2. guidebook 5.2 — 구조 트리에 hooks/·agent_rules_detail.md 추가
3. guidebook 8.2 — 페르소나 표에 mpa_system_designer 행 추가
4. guidebook 6.3/상태 — 검증 중·테스트 중 단계 설명 추가
