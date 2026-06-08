---
태스크: taskfolder-date-prefix
생성일: 2026-06-08
타입: minor
실패비용: minor
상태: 완료 승인
승인해시: b2bd7d679046dc16
---
**목적:** 태스크 폴더명 yyyymmdd_ 접두사 누락 위치 일괄 수정
**요청:** 날짜 없이 폴더가 생성되는 문제 — approve·done 이동 경로 예시에 날짜 접두사 추가

### 핵심 기능
- agent_rules.md: approve 명령 ×2, done 이동 ×2 경로 수정
- layer1_design.md: approve 명령 ×1 경로 수정
- layer1_implement.md: done 이동 ×1 경로 수정

### 사용자 결정
- 없음

### 암묵적 결정
- 없음

### 에이전트 가정
- 없음

### minor 판단 근거
- 한 파일/단일 관심사: 경로 문자열 일괄 수정
- 설계 결정 불필요: 기존 규칙(yyyymmdd_) 일관 적용
- git reset으로 복구 가능: 문서 파일만 수정

### 구현
1. agent_rules.md 4곳 수정
2. layer1_design.md 1곳 수정
3. layer1_implement.md 1곳 수정
