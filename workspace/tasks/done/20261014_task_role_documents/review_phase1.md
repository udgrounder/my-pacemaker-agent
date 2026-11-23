# 독립 구현 검증 — 1차

판정: 확인한 Runtime 범위 통과. 검증 도중 발견한 P2 결함 R1~R4를 부모가 보완했고 수정 후 모두 재검증했다. 실제 큰 조사/구현 담당 활용, 호스트 hook 실실행 등 아래 미확인은 2차에서 구분해 대조한다.

## 입력과 격리

구현/설계 대화 미상속으로 시작했다. 최초 기준은 `PYTHONDONTWRITEBYTECODE=1 python3 .mpa/runtime/hooks/task_documents.py inputs workspace/tasks/active/20261014_task_role_documents/plan.md --stage review1` 출력이다. plan/implementation 원본 전체, 진행 기록, changelog, 다른 critique/review 결과는 읽지 않았다. 발췌 기준과 실제 Runtime/제품 테스트만 읽고 실제 diff도 Runtime 범위로 제한했다. 테스트 CANARY는 가상 fixture이며 구현자의 현재 완료 주장으로 해석하지 않았다.

engineering:code-review 기준으로 실제 동작·호환·실패 경로를 검토했다. 코드/제품 파일을 수정하거나 추가 에이전트/상위 모델을 호출하지 않았다. 테스트 임시 fixture 외에는 읽기 검사만 수행하고 이 결과 파일만 Edit 도구로 저장했다.

## 발견과 보완 상태

### R1 [P2, 보완 확인] 단일형 review2에 실행 기록이 없었다

원래 task_documents.inputs는 모든 stage에 요구사항/선택 문서/설계/검증 기준만 제공했다. 실행 계획 fallback은 implement/critique에만 적용되고 review2에는 changelog만 추가했다. 읽기 mock의 단일 plan에서 `## 실행 계획`의 SINGLE_EXECUTION, `## 실행 TODO`의 SINGLE_EVIDENCE, `## 현재 상태`의 SINGLE_PROGRESS 모두 review2 결과에 없었다. 기본 plan 단독 또는 verification/UI만 선택한 작업의 단계·증거 대조가 불가능했다.

현실적 수정안은 review2에 단일형 plan 실행 기록을 포함하는 것이다. 부모가 review2에 plan 전체를 제공하도록 수정했다. 현재 task_documents.py:247-252와 수정 후 focused 회귀로 보완을 확인했다. implement 재개 시 실행 TODO/중단 지점 전달 여부는 명시된 계약을 더 다듬을 여지가 있으나 이번 핵심 review2 누락은 해소되었다.

### R2 [P2, 보완 확인] 실행 입력 생성은 승인/복구 유효성을 확인하지 않았다

원래 inputs는 inspect만 호출하고 현재 요구사항으로 계산한 승인해시, 승인 상태, `.plan-renewal.json` 잔존을 검사하지 않았다. 선택 문서 없는 roles-v1/단일형에서는 문서 기준 비교도 없었다.

파일 변경 없는 읽기 mock으로 다음을 재현했다.

- 구현 중이지만 승인해시 0000000000000000과 실제 요구사항 해시 aa2d4d2c46df6a62가 다른 plan → inputs implement 성공; plan_hash.approval_hash_issue는 명세 불일치.
- 현재 명세 해시가 맞지만 복구 기록 존재 → inputs review1 성공; 기존 승인 검사는 복구 필요.
- 설계 완료·빈 승인해시 → inputs implement 성공.

기존 gate/audit는 이를 별도로 진단하므로 기존 승인 경계가 제거된 것은 아니지만, 새 인계 도구의 실행 준비 검사가 미달했다. 수정안은 critique의 초안 입력과 implement/review 실행 입력을 분리하고 후자에 승인/상태/복구 선행 검사를 추가하는 것이다.

부모가 READY_STATES 제한과 approval_hash_issue(check_documents=False) 선행 검사를 추가했다. task_documents.py:195-205와 수정 후 focused 회귀로 보완을 확인했다. 재귀 호출 없이 기존 승인 검사와 stage별 문서 검사를 분리했다.

### R3 [P2, 보완 확인] 불필요한 하위 조사 누락도 review1을 차단했다

원래 inspect는 전체 등록을 검사한 뒤에야 stage 필터를 적용했다. review1은 research/work를 전달하지 않으면서 해당 파일이 없으면 실패했다. 가상 승인 plan에 research/brief.md를 등록하고 파일이 없도록 읽기 mock으로 검사하면 `선택 문서 없음: research/brief.md`로 중단했다. 이는 관련 실행만 보류한다는 기준에 미달했다.

수정안은 전체 audit와 stage별 준비 검사를 분리하는 것이다. 부모가 inspect roles 필터 및 implement/review1 역할 집합을 추가했다. task_documents.py:159-161,206-207과 수정 후 focused 회귀에서 관련 없는 research/work 누락은 입력 생성을 막지 않음을 확인했다. 전체 audit에는 계속 오류가 남는다.

### R4 [P2, 보완 확인] 기존 단일형의 설계 기준이 review1에서 사라졌다

plan_template.md는 사전 조사·예상 결정·수정 파일·반례를 `## 실행 계획 (Implementation Plan)` 안에 둔다. 최초 inputs review1은 새 `## 설계 기준`만 제공하고 실행 계획은 전부 제외했다. 기존 plan을 강제 전환하지 않는 계약과 함께 적용하면 설계 판단/반례가 누락되었다.

읽기 mock의 기존 제목 아래 `### 사전 조사`에 LEGACY_DESIGN, `### 구현 단계`에 LEGACY_DONE를 두면 review1에 둘 다 없었다. 완료 주장의 격리는 성공하지만 승인된 설계 계약까지 잃는다.

수정안: 기존 단일형 실행 계획에서 사전 조사·예상 결정·반례 등 설계 기준만 안전하게 발췌하고 구현 체크·실행 결과·증빙은 제외한다. 해당 설계 기준이 없는 기존 형식은 계약 범위를 별도 명시 전달하는 호환 경로를 둔다. 기존 작업의 형식 전환을 강제하지 않는다. 설계/완료 sentinel을 함께 둔 legacy 회귀로 확인한다.

부모가 기존 실행 계획의 생략 사유/사전 조사/예상 결정/반례 발췌를 추가했다(task_documents.py:225-231). section도 같은 수준뿐 아니라 상위 heading에서 종료하도록 보완했다(:51-65). 새 legacy 회귀에서 설계·반례·검증 기준은 유지하고 구현 단계/TODO/완료 문서 체크는 제외되며 review2에는 실행 기록이 포함됨을 확인했다. focused 17/17 통과로 R4 보완을 확인했다.

## 완료 기준별 증거·판정

| 기준 | 증거 | 판정·미확인 |
|---|---|---|
| 1 최소 plan·major plan 단독 | plan_minimal_template, 지침, major/minor 선택 조합 fixture | 문서 구성 및 R4 보완 후 기존 단일형 입력 통과 |
| 2 선택 문서·관련 실행 보류 | 명시 marker, 파일/기준 검사, 자동 fallback 없음, 역할 조합 fixture | R3 보완 후 통과 |
| 3 상세/진행 단일 소유 | 구현 템플릿 설계/실행/진행 구분, 지침의 단일 소유 | 계약 통과. 현재 task 전체 상세 중복은 격리 때문에 미확인 |
| 4 역할 인계·큰 조사 선택 분리 | 역할 템플릿, 큰 작업/조사 지침, research/topic/brief.md fixture, safe_document | 문서·하위경로·권한 불확대 통과. 실제 별도 큰 조사 담당 수행은 미확인 |
| 5 승인 정본·reqspec·복구 | 승인 53개 회귀, 연결 중단/재개 fixture, code_gate 문서 오류 분류 | 기존 승인 도구 및 R2 보완 통과 |
| 6 1차 격리·2차 대조 | review 지침, split/legacy sentinel, 실제 필터 출력/제한 읽기 | R1/R4 보완 후 통과 |
| 7 전환·기준 변경·이력 보존 | checksum 변경/체크 예외, 명세해시/연결 재개 테스트, 전환 지침 | 결정론적 검사 통과. 현재 원본 전체 이력의 의미 보존은 미확인 |
| 8 실패/복구·source/dist | 회귀 및 Runtime diff -qr | 수정 후 지정 회귀 104개 통과, 최종 Runtime 동치 확인 |
| 9 최소 입력 충분성 | 현재 독립 검증은 기준 발췌로 실제 소스·판정 진행 가능 | 현재 split 검증 및 legacy fixture 전달 통과. 별도 구현 담당 fixture 실수행·정량 효율은 미확인 |

## 실행 증거

최초 회귀: test_task_documents.py 14개, test_plan_hash.py 53개, test_structure_loading.py 5개, test_policy_consistency.py 15개, test_todo_policy.py 1개, test_contract_reference.py 13개, 합계 101개 통과. 모두 PYTHONDONTWRITEBYTECODE=1을 사용했다.

수정 후 focused 17/17, plan_hash 53/53, structure_loading 5/5, policy_consistency 15/15, todo_policy 1/1, contract_reference 13/13, 합계 지정 회귀 104개 재통과. 최종 `diff -qr .mpa/runtime dist/.mpa/runtime`도 exit 0, 차이 출력 없음이다. 부모의 전체 236개 통과 보고는 독립 검증자가 직접 실행한 수치와 구분하며 별도 완료 증거로 자동 인정하지 않았다. release/deploy/sync는 검증자가 실행하지 않았다.

추가 재현은 가상 문자열과 unittest.mock으로 읽기/복구 존재 판단만 대체했다. 현재 화면 구현은 없으므로 실제 UI 시각 검증은 비적용이다. 호스트 hook 실실행, 외부 설치 프로젝트 동작, 다른 기존 task 무변경은 전체 task diff를 읽지 않아 미확인이다.

확인한 오류는 모두 보완되었다. 2차에서는 실행 기록과 본 판정을 대조하고, 실제 인계/큰 조사 수행·현재 task 이력 보존 등 미확인 항목을 별도 확인한다. 단위 테스트 통과나 파일 저장만으로 해당 미확인까지 완료로 처리하지 않는다.

## UI HTML 미리보기 추가 검증

판정: 요청 범위의 실행 지침 보완 통과. 사용자 원문은 “ui 의 경우 요청시 html 파일로 디자인을 보여 주는 부분도 추가해줘”이며 실제 특정 화면/HTML 산출물 제작 요청으로 확대하지 않았다. 지정한 네 문서의 관련 부분만 읽었고 진행 기록·changelog·2차 결과는 읽지 않았다. 코드 변경 없는 문서 보완이므로 추가 테스트를 작성하거나 기존 테스트 범위를 확대하지 않았다.

- `.mpa/runtime/inject/task_documents.md:46-52`: 요청 시 실제 HTML 작성, 브라우저/미리보기 렌더 확인, 열어 보여주기, 클릭 가능한 파일 링크 제공을 명시한다. 도구 부재 시 여는 방법·파일 링크와 렌더링 미확인을 함께 안내한다. HTML은 디자인 자료이며 mpa-doc Markdown 역할 등록 대상이 아니다. ui_design이 없으면 plan의 화면 기준에서 경로·화면·확인 버전/시점을 연결하고 모든 UI 작업에 HTML/추가 문서를 강제하지 않는다.
- `.mpa/runtime/templates/ui_design_template.md:16-24`: 요청 시 미리보기 경로·화면·버전·표현 상태·가상 데이터·제품 동작과 차이 및 렌더 확인/미확인 이유를 기록한다. 요청 없으면 해당 섹션을 생략하고 실제 원본 충돌은 메인에 반환한다.
- `docs/task-documents.md:18-28`: 작은 작업의 plan 지원, 요청 기반 작성/확인/열기/링크와 미지원 안내를 사용자 관점에서 설명한다. 선택 문서/승인·복구 계약은 유지한다.
- `guidebook/guidebook.md:1909-1915`: HTML 확인 절차와 작은 작업의 plan 연결, 예시/가상 동작 표시 및 제품 구현 완료와 구분을 설명하고 실행 정본을 Runtime 지침으로 연결한다.

필요 화면 상태/반응형/확인용 상호작용, 로컬 스타일·샘플 데이터 및 추가 실행 조건 안내가 포함된다. 원본과 요청 흐름을 반영하고 변경 시 HTML/연결 문서를 함께 갱신하며 기준 대응을 다시 확인한다. 문서 checksum을 HTML 검증으로 오인하지 않는 지침도 명시된다. 새 역할 문서 타입·일률적인 추가 문서·새 사용자 승인/생명주기 권한을 도입하지 않았다. 관련 오류/누락은 발견하지 않았다.

실제 HTML 제작·렌더링·열기는 이번 지침 검증의 대상이 아니므로 실행하지 않았으며 해당 사용자 흐름의 실제 수행 결과는 미확인이다.
