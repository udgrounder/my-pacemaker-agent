# 아키텍처 이력 분리 요청을 프로젝트 문서 정리로만 해석
**타입**: 방법론 개선
**발견 상황**: architecture_current_snapshot 작업에서 사용자가 MPA 시스템 보완 누락을 정정했다.
**적용 범위**: 모든 프로젝트

## 현재 방식
에이전트가 architecture.md와 architecture_history.md만 수정하고 재사용 Runtime의 기록 지침을 확인·보완하지 않았다. 상세 규칙은 변경된 결정을 architecture.md의 결정 이력에 쓰도록 안내하고 있었다.

## 개선 방안
사용자가 지정한 현재 설계/이력 분리를 공통 규칙·템플릿·기록 및 정합성 점검 경로에 반영한다. 동작 방식을 개선하는 요청에서는 현재 산출물 정리와 그 산출물을 생성·관리하는 Runtime 규칙을 함께 확인한다.

## 적용 대상 파일
- `.mpa/runtime/core/agent_rules.md`
- `.mpa/runtime/core/agent_rules_detail.md`
- `.mpa/runtime/templates/shared_template.md`
- `.mpa/runtime/personas/memory_curator.md`
- 관련 초기화·구현·검증·점검 지침

## 연결 작업
[architecture_current_snapshot](../tasks/done/20261104_architecture_current_snapshot/plan.md)에서 사용자 정정에 따라 보완·검증·dist 동기화를 마쳤다. 상세 절차 파일 분리 후 관련 검사 35개 및 독립 재검증을 통과했고 사용자 승인으로 완료 보관했다. 별도 수집·archive는 수행하지 않았다.
