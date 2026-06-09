---
태스크: completion-intent-criteria
생성일: 2026-06-09
타입: minor
실패비용: minor
상태: 완료 승인
승인해시: c079f3e34de31be7
---
**목적:** 완료 인정 기준을 발화 예시 목록 → 의도 판별 기준 2개로 교체

### 핵심 기능
- agent_rules.md minor/major 두 곳의 완료 인정 기준 수정
- 발화 목록 기반 → 의도 기반 판별 + 모호한 경우 확인 질문 추가

### 사용자 결정
- 없음

### 암묵적 결정
- minor/major 동일 형식으로 통일

### 에이전트 가정
- 없음

### minor 판단 근거
- 단일 파일(agent_rules.md) 수정
- 설계 결정 불필요: 방향 명확
- git reset으로 복구 가능

### 구현
1. agent_rules.md minor 완료 기준 수정
2. agent_rules.md major 완료 기준 수정
3. dist/ 동기화
