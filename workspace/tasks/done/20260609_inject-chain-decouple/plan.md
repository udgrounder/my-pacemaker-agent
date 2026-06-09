---
태스크: inject-chain-decouple
생성일: 2026-06-09
타입: minor
실패비용: minor
상태: 완료 승인
승인해시: 1ec60963a0c1a05c
---
**목적:** inject 파일 간 직접 호출 체인 제거 — 상태 전환만 하고 다음 inject 진입은 agent_rules.md 라우팅이 결정

### 핵심 기능
- layer1_implement.md: "다음은 layer1_review.md" 직접 지시 제거
- layer1_review.md: "layer1_discovery.md 세션 시작" 직접 지시 제거 → 신규 태스크 분리 안내로 교체

### 사용자 결정
- 없음

### 암묵적 결정
- layer1_design.md → layer1_critique.md 참조는 유지 (비평은 설계 세션 내 서브태스크)

### 에이전트 가정
- 없음

### minor 판단 근거
- 두 파일의 단일 관심사(inject 체인) 수정
- 설계 결정 불필요: 방향 명확
- git reset으로 복구 가능

### 구현
1. layer1_implement.md 164번 줄 수정 (layer1_review.md 직접 참조 제거)
2. layer1_implement.md 177번 줄 수정 ("자동으로 검증 중 전이" 문구 수정)
3. layer1_review.md 347-350번 줄 수정 (layer1_discovery.md 직접 호출 → 신규 태스크 안내)
4. dist/ 동기화
