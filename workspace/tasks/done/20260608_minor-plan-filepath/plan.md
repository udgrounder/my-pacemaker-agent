---
태스크: minor-plan-filepath
생성일: 2026-06-08
타입: minor
실패비용: minor
상태: 완료 승인
승인해시: a6c82112bb15a76c
---
**목적:** minor 계획서 제시 시 plan.md 파일 경로 표시 추가
**요청:** 사용자가 plan.md 파일을 직접 열어볼 수 있도록 경로를 함께 제시

### 핵심 기능
- agent_rules.md minor 계획서 제시 형식에 파일 경로 한 줄 추가

### 사용자 결정
- 없음

### 암묵적 결정
- 없음

### 에이전트 가정
- 없음

### minor 판단 근거
- 한 파일/단일 관심사: agent_rules.md 형식 한 줄 추가
- 설계 결정 불필요: 방향 명확
- git reset으로 복구 가능: 문서 파일만 수정

### 구현
1. agent_rules.md minor 계획서 제시 형식에 `계획서: workspace/tasks/active/...` 경로 추가
