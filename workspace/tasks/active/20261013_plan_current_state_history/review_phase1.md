# 독립 구현 검증 1차

## 검토 범위와 격리

- 기준: 이 태스크의 plan.md, workspace/memory/shared/architecture.md, project_identity.md, Runtime layer1_review.md와 code_reviewer 페르소나.
- 대상: core의 agent_rules.md·agent_rules_detail.md·session_protocol.md·glossary.md, hooks의 plan_hash.py·code_gate.py, plan/changelog/sub 템플릿, 설계·구현·검증·발견 inject, discovery_classification, guidebook 및 test_plan_hash.py·test_todo_policy.py·test_policy_consistency.py.
- 실제 태스크 changelog.md는 읽지 않았다. 변경된 소스와 git diff, 실제 테스트 실행으로 판단했다. 소스 수정 없이 이 결과 파일만 작성했다.
- 검증 중 소스가 갱신되어 최종 write_approval_pair의 old_plan 전달·원본 재대조와 해당 테스트까지 다시 확인했다.

## 검토 결과

### ✅ 정합성 확인 — 검증 근거

- 문서 역할: agent_rules.md의 현재 계획/변경 이력 정본 규칙이 템플릿 및 설계·구현·발견·재개·minor·하위 계획 지시에 연결되어 있다. 취소선과 초기 판단의 plan 누적 지시는 교체되었다. 현재 실패·미충족 증빙, 유효 제약·제외 범위·완료 기준 보존 및 승인 후보 분리는 정본에 명시되어 있다. 관련 Runtime와 guidebook에서 구 지시인 `실행 중 변경 기록`을 요구하는 참조는 남아 있지 않았다.
- 독립 검증: 1차는 현재 plan/실제 결과, 2차는 이력·승인 근거 대조라는 경계가 유지된다. 1차에 필요한 미해결 실패/위험은 plan에 남기도록 명시되어 있어 이력 미열람과 충돌하지 않는다.
- 정상 경로: 새 배치 renew_spec은 기존 승인 형식·상태·summary를 검사하고 명세 해시를 계산한 뒤 changelog 승인 행과 plan 승인해시를 갱신한다. journal 독점 생성 → 원본 재대조 → history 저장 → plan 원본 재확인 → plan 저장 → journal 제거 순서다. 기존 reqspec-v1 내부 표가 있으면 단일 파일 경로로 기록한다. 명세 해시 알고리즘은 변경하지 않았다.
- 실패 경로: history 저장 후 plan 저장 실패는 원본 plan 및 예상 history와 일치할 때 history를 원복한다. 외부 편집으로 예상 내용과 달라졌거나 원복/정리 자체가 실패하면 journal을 남겨 실패를 반환한다. 프로세스 중단 후 잔존 journal은 check/audit/gate 및 approve/renew-spec에서 탐지된다. 기본 warn/block와 선택 critical 정책은 유지된다.
- 호환: 정확한 plan 내부 최상위 이력 헤딩으로 reqspec-v1 기존 배치를 판별한다. 중복 헤딩·명세 영역 내부/이전 헤딩은 거부한다. 내부 표 제거 전 보존/대조 전환은 문서로 지정한다. 접두사 없는 구형 해시는 기존 재승인 절차를 유지하므로 reqspec-v1 배치 호환과 혼동하지 않는다.
- 독립 실행한 테스트: test_plan_hash.py 최종 43개, test_policy_consistency.py 15개, test_todo_policy.py 1개 모두 통과. test_plan_hash.py에는 정상/반복 갱신, 기존 이력·후속 섹션 보존, 저장 실패·중단·원복 실패·외부 편집 보존·정리 실패·입력 거부·gate 경로가 포함된다. Runtime source/dist 전체 디렉터리 비교에서 차이가 없었다.
- 전체 208개 회귀 테스트 통과와 whitespace 확인은 메인 에이전트가 보고했다. 이 1차 검증자가 직접 실행한 증빙과 구분한다. 실제 태스크 이력/사용자 승인 증빙 대조는 2차 대상이므로 여기서 통과로 주장하지 않는다.

### ⚠️ 주의 필요

- 확정한 잔여 지적 0개. 동시 갱신에 대한 초기 위험 후보는 최종 코드의 원본 재대조로 재평가했다. 먼저 시작한 호출의 오래된 plan/history snapshot이 다른 성공 호출 뒤 저장되는 경로는 충돌 실패로 처리된다. 이 판단은 코드의 원본 비교와 관련 최종 테스트를 근거로 한다.
- 도구 journal은 프로세스 중단·저장 실패의 탐지/복구 근거이며 두 파일의 crash-atomicity를 보장한다는 계약은 아니다. 이 제한은 코드와 복구 규칙에 드러나 있으며 본 명세의 실패 처리 조건과 모순되지 않는다. 별도 지적으로 계수하지 않는다.

### 🚨 즉시 수정 필요

- 0개. 검증한 대상과 최종 소스 기준으로 필수 수정이 필요한 명세 불일치·승인 우회·복구 실패 은폐를 확정하지 못했다.

### 📝 조용한 결정 목록

- 계획에 없는 조용한 결정 0개. 내부 이력 표 존재 기반 배치 판별, reqspec-v1만 renew-spec 지원, 두 파일 갱신용 임시 JSON, 외부 편집 시 보존과 실패 처리, 저장 후 JSON 정리 실패의 복구 필요 판정은 plan에 포함되어 있다.

### 🔍 에이전트 가정 검증

- 내부 이력 표로 구형 저장 배치를 판별할 수 있다 / 결과: 유효 / 영향: 없음. approval_history_match(body, plan=True)가 정확한 헤딩을 검사하고 renew_spec이 기존 단일 파일과 새 두 파일 경로를 분기한다. 여기서 구형은 저장 배치이며 접두사 없는 구형 해시와 다르다.
- 규칙 정리와 제한된 승인 도구 변경으로 해결 가능하다 / 결과: 검증 범위에서 유효 / 영향: 없음. 현재/이력 분리의 의미 판단은 문서 지시이며 코드 변경은 승인 기록 배치·저장/복구·무결성 연결에 한정된다. 해시 대상·사용자 승인 필요 조건·독립 검증 격리는 유지된다.
- 틀린 가정 0개.

## 판정

1차 기준 잔여 필수 수정 지적은 없다. changelog 실제 내용·사용자 승인 근거·과거 판단/실패 증빙 보존 여부를 2차에서 대조하고, 전체 회귀 검증 결과와 함께 최종 상태를 판단해야 한다. 이 파일은 사용자 최종 완료 승인을 대신하지 않는다.
