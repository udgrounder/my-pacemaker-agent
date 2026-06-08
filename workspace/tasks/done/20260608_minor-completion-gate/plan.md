---
태스크: minor-completion-gate
생성일: 2026-06-08
타입: minor
실패비용: minor
상태: 완료 승인
승인해시: aea7d3287f68c16e
---
**목적:** minor 자동 완료 제거 — 구현 후 사용자(또는 위임 에이전트) 확인 후 done 처리
**요청:** 자동 완료로 인해 버그 발견 시 새 태스크를 계속 만들어야 하는 문제 개선

### 핵심 기능
- minor 완료 흐름: 자동 done → 구현 보고 후 사용자 확인 대기
- 완료 인정 기준은 major와 동일하게 적용
- done 처리 절차(INDEX 업데이트, mv)는 기존과 동일

### 사용자 결정
- 없음

### 암묵적 결정
- minor 단계 모델 설명(`메모 [자동 승인] → 구현 중 → done`)도 함께 수정
- layer1_implement.md minor fast-path의 자동 done 처리도 함께 수정

### 에이전트 가정
- 없음

### minor 판단 근거
- 한 파일/단일 관심사: agent_rules.md + layer1_implement.md 완료 처리 부분
- 설계 결정 불필요: 방향 명확
- git reset으로 복구 가능: 문서 파일만 수정

### 구현
1. agent_rules.md 단계 모델 minor 설명 수정
2. agent_rules.md minor 완료 섹션 수정
3. layer1_implement.md minor fast-path 수정
