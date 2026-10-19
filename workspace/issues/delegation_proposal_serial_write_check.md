# 위임 제안 전에 현재 구현 직렬화 규칙 확인

**타입**: 방법론 개선
**발견 상황**: 현재 모델 상한 기반 자동 위임 계획 수립. 초기 설명에서 파일별 병렬 구현을 제안했으나, 현재 architecture.md의 단일 순차 구현 규칙을 확인한 뒤 계획에서는 순차 위임으로 정정했다.
**적용 범위**: 모든 프로젝트

## 현재 방식

서브에이전트 도구가 지원하는 병렬 실행을 설명할 때 현재 프로젝트의 공유 상태 변경 규칙을 확인하지 않으면 기존 구현 직렬화 원칙과 충돌하는 방식을 제안할 수 있다.

## 개선 방안

일반 위임 정책의 설계·제안 전에 현재 architecture와 실행 정본을 확인한다. 읽기 작업과 독립 산출물은 병렬 검토하되 source·memory·plan·INDEX의 공유 변경은 단일 수정자 원칙으로 판단한다. 도구의 지원 여부만으로 병렬 구현을 허용하지 않는다. 현재 개선은 workspace/tasks/active/20261013_bounded_agent_delegation/plan.md에 반영했으며 Runtime 구현은 미승인 상태다.

## 적용 대상 파일

- .mpa/runtime/inject/agent_delegation.md (계획상 신규)
- .mpa/runtime/inject/layer1_implement.md
