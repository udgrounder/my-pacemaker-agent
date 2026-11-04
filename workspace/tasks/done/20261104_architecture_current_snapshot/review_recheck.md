# 독립 재검증

## 대상·판정

이전 `review_phase1.md`의 P2와 현재 Runtime 실제 파일만 대조했다. plan 실행 기록·changelog·기존 구현 설명은 읽지 않았다. 과거 검토 보고서는 수정하지 않았다.

**기존 P2 해소, 추가 발견 0건.** core는 34,506 bytes로 기존 기준 34,731 bytes보다 작으며 해당 회귀 검사가 통과한다.

## 의미 보존과 로드 경로

- `core/agent_rules.md:31`의 즉시 읽기 트리거와 89–91행의 최소 정본 규칙이 `core/architecture_memory.md`에 연결된다.
- 새 정본은 현재 설계/이력 분리, 제목 아래 상대 링크, 신규 이력 생성과 기존 파일 보호, 날짜·대상·이전/새 판단·이유·근거 기록, 이력 저장·대조 후 교체/삭제, 실패 시 이전 판단 유지와 보고, 유효한 제약·미해결 위험 유지, 원문 보존 확인 후 migration, 과거 판단 추정 금지, 기존 이력의 줄 수 정리 제외, 선택적 읽기와 INDEX 제외를 유지한다. 1차에서 확인한 핵심 규칙의 누락은 발견하지 못했다.
- detail의 기억 여부 판단, 초기화·업데이트·구현·검증·checkpoint, memory curator, shared/history template은 작업 전에 해당 정본을 반드시 읽도록 직접 참조한다. 초기화는 template과 정본으로, 변경은 먼저 history 저장·대조 후 현재 문서 교체로, 저장 실패는 현재 판단을 삭제하지 않는 경로로 이어진다. 로드 단절은 발견하지 못했다.

## 실제 검증 결과

- `python3 -m unittest tests.test_task_index_policy tests.test_contract_reference tests.test_structure_loading tests.test_policy_consistency`
  - 출력: `Ran 35 tests in 0.642s`, `OK`, 종료 코드 0.
  - 기존 core 크기 검사와 전체 Runtime source/dist 파일 집합·byte 대조 검사 포함.
- 대상 11개 source/dist 파일을 별도 byte 대조: `source-dist files: 11`, `mismatches: []`.
- 크기 확인: `core bytes: 34506`, `baseline bytes: 34731`.
- `git diff --check -- .mpa/runtime dist/.mpa/runtime`: 종료 코드 0, 출력 없음.

## 한계

지침 연결·의미 보존과 지정된 기존 검사에 한정한 재검증이다. 실제 LLM 준수·실패 원자성·workspace history 원문 보존을 보장하지 않는다. 제품 파일·실제 memory는 수정하지 않았다.

정정 회고: 없음.
