---
태스크: multi-agent-utility-discussion
생성일: 2026-06-12
타입: minor
실패비용: minor
상태: 완료 승인
승인해시: d20e68dcc8381e84
정리: 20260612_discussion-mode — 토론을 개발 minor로 미스라우팅한 사례(이 태스크가 discussion-mode upgrade 후보를 낳음). 회의록 multi_agent_utility.md는 workspace/exploration/discussion/로 이관됨(단일 진실원). 토론 모드로 재시작 시 같은 문서에 이어씀. done 보관.
---
**목적:** discussion 모드에서 "멀티에이전트/서브에이전트의 효용성"을 토론하고, 그 토론 내용을 think-more/discussion/에 회의록으로 기록한다.
**요청:** "discussion 모드에서 멀티에이전트 또는 서브에이전트의 효용성에 대해 논의하고 싶어. 토론을 진행하고 토론 내용을 회의록에 작성해줘"

### 핵심 내용
- 서브에이전트(위임·격리) vs 멀티에이전트(동료 토론·앙상블) 구분
- 효용의 출처: "관점의 독립성"이지 "에이전트 수"가 아님 — 맥락적 독립 vs 인식론적 독립
- 같은 모델 클론의 상관된 오류 / 거짓 합의 위험
- 검증 무한후퇴, 준수 지속가능성 비용
- MPA 시스템 설계(비평·검증=서브에이전트, minor 제외, 출력 재검증)와의 정합성

### 에이전트 가정
- think-more/는 설치되지 않는 설계 사고 공간 — 자유 서술 형식
- 파일명: multi_agent_utility.md (영문 스네이크, 기존 관례)
- v1 living document — 사용자 반론·보정으로 정밀화 예정

### minor 판단 근거
- 단일 파일 생성: O
- 설계 결정 불필요(기록 대상은 이번 세션 토론): O
- git reset 복구: O
- 취향·의사결정 불필요: O

### 구현
1. think-more/discussion/multi_agent_utility.md 작성 (회의록: 안건 → 논점 → 쟁점·반론 → 결론 → 미결 질문)
