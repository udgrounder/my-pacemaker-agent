---
태스크: plan_current_state_history
생성일: 2026-10-13
타입: major
실패비용: major
상태: 테스트 중
승인해시: reqspec-v1:74809779fbf1bef0
승인대상: 요구사항 명세
---
# 작업 계획서: 계획서 현재 정보와 변경 이력 분리

**파생 출처:** `workspace/issues/20261013_plan_current_state_and_history_separation.md`

## 요구사항 명세

### 요청 기준
계획서에 불필요한 과거 방향이 누적되는 문제를 개선한다. 2026-10-13 보고한 개선 방향에 대해 사용자가 “개선 진행해줘”로 실행을 승인했다.

### 목적
계획서만 읽어 현재 유효한 작업 기준을 이해하고, 변경 이력에서 이전 판단과 변경 근거를 추적할 수 있게 한다.

### 범위·제외 범위
- 범위: Runtime 템플릿·설계/구현/발견/검증/재개/minor 규칙, 승인 갱신 도구와 관련 테스트, 설명 문서의 연관 참조, dist Runtime 동기화.
- 제외 범위: 완료된 작업 일괄 재작성, 다른 진행 중 작업의 명세 변경, release 생성·설치본 배포.

### 완료 기준
- plan은 현재 유효한 판단·실행·검증 현황을 유지하고 폐기 이력은 changelog에 한 번 기록한다.
- changelog에서 계획 변경과 실제 구현 결과를 구분하고 변경 전후·이유·명세 영향·승인/증빙을 추적한다.
- 새 plan에는 승인 변경 이력 표가 필요 없고 renew-spec이 같은 폴더 changelog에 기록한다. 기존 plan의 승인 이력은 보존하고 구형 배치도 지원한다.
- 승인 명세 해시 알고리즘·승인 필요 조건·독립 검증 격리를 유지한다. 저장 오류로 승인해시와 이력이 어긋나면 실패로 처리하고 원복하거나 복구 근거를 남긴다.
- 관련 테스트와 source/dist 일치 확인을 통과한다.

### 사용자 결정
- 기존 changelog를 확장하고 별도 history 파일은 기본 추가하지 않는다.
- 보고한 범위의 개선을 실행한다. 완료 승인과 릴리즈·배포 요청은 별도다.

### 변경 불가 제약
- 완료 기준을 구현 결과에 맞춰 낮추거나 미충족 증빙을 지우지 않는다.
- 승인해시를 임의 생성하지 않고 기존 approve/renew-spec을 사용한다.
- 사용자 소유 과거 작업·immutable release를 일괄 변경하지 않는다.

### 에이전트 가정
| 가정 | 근거 | 틀렸다면 |
|---|---|---|
| 기존 plan의 이력 표 존재로 구형 저장 배치를 판별할 수 있다 | 기존 템플릿과 renew_spec이 표를 요구한다 | 명시 배치 표지를 추가하고 호환 경로를 검토 |
| 규칙 정리와 제한된 승인 도구 변경으로 해결 가능하다 | 해시 계산은 명세에 한정된다 | 영향 범위·위험 변화 보고 |

### 결정 대기 항목 (Open Questions)
없음.

### 작업 분류 판단 근거
- major: 다중 Runtime 규칙과 승인 기록 저장 계약이 연결된 변경이다. 외부 시스템·배포 변경은 없다.

## 실행 계획

### 생략 항목과 사유
없음.

### 사전 조사
plan_template의 취소선·초기 판단 보존, implement의 중복 기록, review의 이력 대조, hooks/plan_hash.py의 renew_spec, tests/test_plan_hash.py와 연관 문서 참조를 확인했다.

### 구현 단계
- [x] 문서 역할·정리·갱신 절차를 core 정본과 템플릿에 정의한다 — 누적 원인을 제거한다.
- [x] 설계·구현·검증·발견·재개·minor·하위 계획과 관련 설명을 맞춘다 — 상충 지시를 방지한다.
- [x] 승인 갱신의 새 changelog 배치·기존 plan 호환·저장 실패 처리를 구현한다 — 승인 추적을 보존한다.
- [x] 실패·호환·독립 검증·Runtime 동기화를 확인한다 — 관련 53개·전체 219개 테스트와 독립 1차·2차 검증 통과, Runtime 일치 확인.

### 예상 조용한 결정
- 이력 저장 배치는 기존 plan 내부 표가 있으면 유지하고 없는 새 plan은 changelog에 기록한다.
- 사람의 의미 판단은 규칙으로, 승인 저장과 오류 복구는 코드로 처리한다.
- 두 파일 갱신에는 독점 복구 JSON을 먼저 저장한다. 잔존 시 approve/renew/check/audit/gate가 복구 필요로 판단하며, 롤백은 예상 작성본과 일치할 때만 수행해 외부 편집을 보존한다. 커밋 뒤 JSON 삭제 실패도 복구 필요로 보고한다.
- 기존 내부 이력 표 지원은 reqspec-v1 형식의 배치 호환이다. 접두사 없는 구형 해시는 기존 사용자 재승인 절차를 유지한다.
- 후속 보완: 교체·원복 직전 파일을 별도 복구 파일로 확보한 뒤 예상 내용과 대조한다. 새 내용은 경로가 비어 있을 때만 생성하고 다른 writer의 파일을 덮지 않는다. 두 파일과 확보한 원본의 최종 대조를 통과해야 성공·복구 자료 정리로 진행한다. 지원 에이전트의 같은 문서 편집은 갱신 중 직렬화한다.

### 수정 대상 파일
- `.mpa/runtime/core/agent_rules.md`, `agent_rules_detail.md`, `glossary.md`, `session_protocol.md`
- `.mpa/runtime/templates/plan_template.md`, `changelog_template.md`, `sub_template.md`
- `.mpa/runtime/inject/layer1_design.md`, `layer1_implement.md`, `layer1_review.md`, `layer1_discovery.md`
- `.mpa/runtime/hooks/plan_hash.py`, `code_gate.py`, `session_start.py`
- `.mpa/runtime/skills/analysis/discovery_classification.md`, `guidebook/guidebook.md`
- `tests/test_plan_hash.py`, `test_structure_loading.py`, `test_todo_policy.py`, `test_policy_consistency.py`
- `workspace/memory/shared/architecture.md` — 현재 계획·변경 이력과 승인 저장 계약 반영

### 참고 파일 (수정 없음)
- `MAP_PRODUCT_RULES.md`, `workspace/project_rules.md`

### 반례
- 이력 표만 삭제하면 renew-spec 실패 → 승인 도구와 템플릿을 함께 수정한다.
- 이력 저장 성공 뒤 plan 저장 실패 → 원복과 오류 주입 테스트를 수행한다.
- 과거 가정을 지우며 검증 근거까지 잃음 → 변경 이력에 이전 판단·영향 보존, 2차 검증에서 대조한다.
- 기존 계획 정리로 구형 해시 변경 → 기존 승인 블록 자동 변환을 금지하고 호환 경로를 유지한다.

## 실행 TODO
### 구현·에이전트 검증
- [x] 문서·도구·테스트 변경
- [x] 관련 테스트 및 source/dist parity
- [x] 독립 비평·구현 검증과 지적 반영 — 후속 4건·보완 중 발견 2건 해결, 최종 미해결 필수 지적 없음

### 사용자 결정·승인 필요
- [ ] 결과 확인·최종 완료 승인

## 검증 결과
### 검증 체크리스트
- [x] 정상: 새 plan 명세 승인 갱신과 changelog 기록
- [x] 실패: 저장 오류와 잘못된 입력 때 기존 파일 보존 — 추가 경합 재현·원본 확보·빈 경로 설치·최종 대조 테스트 통과
- [x] 엣지: 기존 표 배치·기존 changelog·반복 갱신·표 특수문자

현재 판정: 후속 독립 재검토 P2 3건·P3 1건과 보완 중 발견한 인터럽트 경계·audit 사유 누락을 보완했다. 관련 53개·전체 219개 테스트와 독립 1차·2차 재검증을 통과했고 미해결 필수 지적은 없다. 사용자 결과 확인·완료 승인은 남아 있다. 이전 실패 증빙과 보완 근거는 changelog에 보존한다.

### 검증 범위와 운영 제약
- 실제 저장·원복·최종 대조와 복구 라우팅·섹션 구조를 독립 검증했다. 상세 판정은 [`repair_review_summary.md`](repair_review_summary.md)에 보존한다.
- 지원 writer는 같은 문서 쓰기를 직렬화한다. 비협조 편집기와의 완전한 동시 저장·작업 완료 후 편집·전원 손실 원자성을 보장한다고 판단하지 않는다.
- 이전 실패 근거는 changelog와 연결된 독립 검토 기록에 보존한다. 에이전트 검증 통과가 사용자 완료 승인을 대신하지 않는다.

### 완료 시 문서 업데이트 대상
- [x] 관련 guidebook·승인 명령 설명과 아키텍처의 현재 계약

## 운영 시 안내 사항
- 새 작업부터 새 형식을 사용한다. 기존 작업은 재개 시 필요한 부분만 정리하고 기존 이력을 보존한다.
- 사소한 문구·체크 상태 변경에는 이력을 강제하지 않는다. minor는 의미 있는 변경이 있을 때만 이력 파일을 만든다.

## 변경 이력
[`changelog.md`](changelog.md)에 계획·승인·구현 변경을 기록한다.
