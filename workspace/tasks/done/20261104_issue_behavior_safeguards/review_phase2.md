# 독립 검증 2차

검증일: 2026-11-04. 구현 대화 미상속. 검토 전용이며 구현 파일·plan·changelog·이슈는 변경하지 않았다.

## 대상과 입력

- `task_documents.py inputs .../plan.md --stage review2`로 승인 명세·실행 기록·changelog를 확보한 뒤 `review_phase1.md`와 대조했다. `task_documents.md`, `_agent_execution_priority.md`, `layer1_review.md`, 검토 페르소나·반례/경로 추적 지침을 적용했다.
- 실제 대상: `.mpa/runtime/core/agent_rules.md`, `core/agent_rules_detail.md`, `inject/layer1_design.md`, `inject/layer1_implement.md`, `inject/layer1_review.md`, `workflows/bug_fix.md` 및 dist 대응본. 아키텍처 정본과 구현 페르소나도 확인했다. contracts.md는 없다.
- 전체 git diff를 읽지 않고 지정 Runtime 파일의 diff만 읽었다. 같은 파일에 함께 존재하는 architecture 현재/이력 분리 변경은 changelog:32에 명시된 기존 작업으로 구분했고 이번 구현으로 귀속하지 않았다.

## 판정

즉시 수정 필요 1건(P2), 주의 필요 0건. 1차 발견을 유지한다. 추가 독립 결함이나 조용한 결정은 발견하지 못했다. 관련 테스트 통과·동기화·archive 기록은 재확인했으나, 모든 진입점 연결과 구현 완료 주장은 아래 결함 때문에 충족하지 않는다.

### 🚨 즉시 수정 필요 — 기존 작업의 버그 수정 진입에 원인 검증 기준 연결 누락

- 정본은 `.mpa/runtime/workflows/bug_fix.md:63`에 있다. 신규 버그는 `core/agent_rules.md:184`, `:200` → `workflows/bug_fix.md:9`의 경로로 해당 기준을 읽는다.
- 반면 `core/agent_rules.md:163`, `:169`는 현재 작업의 구현 진입을 `layer1_implement.md`로 보낸다. 현재 작업 범위 안의 버그는 `:175`–`:178`의 신규 예외가 아니다. 구현 지침의 `:63`–`:81` 및 이곳에서 읽는 `core/agent_rules_detail.md:146`–`:159`에는 원인 가설과 사실 구분·반증 시 가설 재검토 기준이나 bug_fix 참조가 없다. `personas/implementer.md:7`–`:22`도 이 누락을 보완하지 않는다.
- 검증 중 수정 또한 `inject/layer1_review.md:171`–`:174`에서 수정·재검증으로 바로 이어진다. `:177`은 구현 지침의 명세 영향 검사만 연결한다. 검토 페르소나의 반례 탐색은 검토 역할의 분석 기준이며, 이 수정 진입에서 원인 기준을 반드시 읽도록 하는 참조를 대신하지 못한다.
- 반례: 승인된 현재 작업에서 첫 수정 후에도 같은 실패가 재현되고 결과가 최초 가설과 어긋난다. 신규 요청 라우팅을 거치지 않는 이 경로는 범위·명세 확인과 최소 테스트를 하면서도 같은 가설로 수정을 반복할 수 있다. 실제 사용자는 수정 반복과 재작업을 겪을 수 있다. 이를 반드시 발생하는 동작으로 단정하지 않지만, 이번 명세가 요구한 예방 기준의 전달 누락은 확정할 수 있다.
- 심각도는 P2를 유지한다. 즉시 데이터 파괴나 권한 확대를 입증한 P1은 아니나, plan.md:23·:26의 원인 근거 확인 및 관련 진입점 연결이라는 완료 기준을 직접 미충족한다. 이번 작업 완료 판정 전에 수정할 사항이다.
- changelog.md:21의 “bug_fix에 기준 추가”는 사실이다. 그러나 changelog.md:31의 가설 반증 재조사 자기 점검과 plan.md:59·:69의 관련 진입 연결/구현 완료 주장을 전체 수정 흐름의 증거로 쓰기는 어렵다. 구현자의 설명으로 1차 지적을 기각할 근거가 없다. 같은 결함에 따른 기록 정정 필요를 별도 결함으로 중복 집계하지 않았다.
- 권장: 공통 정본 또는 기존 bug_fix의 해당 원인 기준만 구현/검증 중 버그 수정에 명시 연결한다. minor에 major 전체 시퀀스·새 승인 절차를 일괄 적용할 필요는 없다. 수정 후 해당 참조 체인과 반례를 재검증하고 plan/changelog의 완료 주장을 맞춘다. 검토만 요청된 범위이므로 수정하지 않았다.

## 나머지 구현 주장 대조

| 주장 | 실제 파일 근거 | 판정 |
|---|---|---|
| 완료 충돌 확인을 상태·INDEX보다 먼저 수행 | `core/agent_rules_detail.md:104`–`:110`, `core/agent_rules.md:343`–`:345`, `inject/layer1_implement.md:126`–`:130` | 정상 이동·충돌 보존·이동 직전 재확인이 연결된다. 자동 병합/삭제 권한을 추가하지 않는다. |
| 질문 의도·기존 위임 구분 | `inject/layer1_implement.md:81`, `inject/layer1_review.md:177` | 질문 우선 답변, 질문만으로 승인 추정 금지와 유효한 기존 위임 재사용이 함께 규정된다. |
| 관련 변경에만 참조·의존·확장 지점·운영 제약 조사 | `core/agent_rules_detail.md:151`–`:155`, `inject/layer1_design.md:33`, `inject/layer1_implement.md:64`, `core/agent_rules.md:29` | 실제 근거·미확인 한계를 요구한다. 도구/특정 기술/기존 구조 재사용 강제는 없다. |
| dist 동기화 및 기존 테스트 통과 | 아래 직접 실행 결과 | 현재 파일 상태와 테스트 결과는 일치한다. 과거 sync 명령 자체의 성공 로그를 재현한 것은 아니다. |

1차에서 찾은 changelog 누락 변경은 없으며, 이번 대상 diff에도 별도 미기록 행동 정책을 발견하지 못했다. 기존 architecture 작업을 이번 범위에 섞거나 되돌리지 않았다.

## 7개 이슈와 승인·기록 무결성

- 아래 7건 모두 `workspace/issues/archived/2026/11/campingtalk-proj/`에 존재한다. 각 파일 `:4`–`:9`의 metadata는 archived/accepted/decided_by:user와 제한된 decision_reason, 존재하는 동일 follow_up_task를 담는다. 같은 파일명의 inbox 원본은 모두 0건이다. 본문 결정 근거와 연결 작업도 metadata와 대응한다.

| 파일 | 제한된 채택 근거·본문 연결 |
|---|---|
| `20260908_root_cause_verification_before_fix.md` | `:8`, `:44`–`:45`: 가설/사실·반증만 채택, 서버 열람/로그 일괄 의무 제외 |
| `20260915_callsite_enumeration_and_dependency_direction.md` | `:8`, `:48`–`:49`: 호출 외 참조·실제 의존 설정, 도구/Gradle 강제 제외 |
| `20261019_reuse_existing_view_model_path.md` | `:8`, `:42`–`:43`: 확장 지점·예외 조사, 특정 헬퍼/대상 코드 수정 제외 |
| `20261020_static_asset_ownership_before_exclusion.md` | `:8`, `:42`–`:43`: 소스/생성·배포/연결 확인, suffix·min 정책 제외 |
| `20261027_task_archive_duplicate_preflight.md` | `:8`, `:43`–`:44`: 충돌 사전 확인·보존 중단, 통합/사본 삭제 제외 |
| `20261028_s3_lifecycle_prefix_preservation.md` | `:8`, `:41`–`:42`: 운영 제약 일반화, S3 구체 값/대상 메모리·코드 제외 |
| `20261104_no_spec_value_change_on_question.md` | `:8`, `:43`–`:44`: 질문/지시·기존 위임 경계, 명세 밖 값의 무조건 변경 제외 |

- plan.md:7의 승인해시는 현재 요구사항과 일치한다. changelog.md:10은 명확한 적용 요청과 minor 자동 approve를 기록하며 `core/agent_rules_detail.md:350`–`:358`의 실행 요청 minor 경로와 모순되지 않는다. 명세 변경·승인 갱신 이력이나 복구 잔존은 발견하지 못했다. plan의 active/구현 중 유지도 minor 완료 확인 대기와 부합한다.
- 사용자의 원래 적용 발화는 이 검증자에게 전달되지 않았다. plan.md:29와 changelog.md:10 및 이슈의 승인 metadata가 서로 대응한다는 것과 현재 해시 무결성까지 확인했다. 이 문서들만으로 실제 사용자 발화의 진위를 독립 인증하거나 과거 변경 보존 전체를 증명하지 않는다. 승인 증거 축소·무단 명세 변경의 실제 증거는 발견하지 못했다.

## 직접 실행한 확인

- `task_documents.py inputs .../plan.md --stage review2`: exit 0, 입력 반환.
- `python3 -m unittest discover -s tests -p 'test_policy_consistency.py'`: 15개 통과.
- `python3 -m unittest discover -s tests -p 'test_contract_reference.py'`: 13개 통과.
- `python3 -m unittest discover -s tests -p 'test_task_index_policy.py'`: 2개 통과. 총 30개 통과.
- source/dist Runtime 파일 집합·바이트 비교: `__pycache__` 제외 각각 68개, 모두 일치. 대상 6개 파일도 포함된다.
- 대상 source/dist 12개 파일·plan/changelog·7개 archive에 한정한 `git diff --check`: exit 0.
- `plan_hash.py check`: `일치: reqspec-v1:fa2addfe45ee522c`. `audit`: missing=[], invalid=[]. `.plan-renewal.json` 없음.
- 7개 archive metadata·연결 plan 존재·inbox 파일명 부재 검사: 전부 통과.

## 조용한 결정·가정·남은 한계

- 조용한 결정 0건, 틀린 에이전트 가정 0건. “도구 추가 없이 지침으로 전달할 수 있다”는 가능성 가정 자체를 반증한 것은 아니며, 실제 연결의 불완전함은 위 결함으로 집계했다. minor 분류를 뒤집을 새 외부 위험도 확인하지 못했다.
- 실제 에이전트 행동 시뮬레이션·비협조 동시 이동·설치 프로젝트·release/deploy는 실행하지 않았다. 문서 참조와 기존 정책/계약/INDEX 테스트가 호스트의 실제 로드·행동 준수까지 보장하지 않는다.
- 권장 다음 행동은 수정 필요다. 검토 전용 권한을 유지하며 이 보고서와 summary만 작성했다.
