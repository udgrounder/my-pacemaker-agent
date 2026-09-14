# MPA 협업 효과 측정 체계 상세 설계

## 경계

- 평가 입력은 평가자가 만든 로컬 JSON 파일이다. 도구는 agent 로그, 소스, credential, 절대 경로를 읽거나 전송하지 않는다.
- 집계는 관측값을 추정하지 않는다. 누락은 `null` 또는 누락 수로 남기고 0으로 바꾸지 않는다.
- 합성 fixture는 집계기의 계산 검증용이며 실제 협업 성과 증거가 아니다.

## 디렉터리와 책임

| 경로 | 책임 |
|---|---|
| `evaluations/scenarios/*.md` | 6개 대표 시나리오의 입력·초기 상태·수용 기준·실패/중단 기준 |
| `evaluations/schema.json` | run record의 검증 가능한 필드·허용값·단위 |
| `evaluations/protocol.md` | 동일 조건, 교차 실행, 채점·중단·개입 분류 절차 |
| `evaluations/summarize.py` | 입력 검증, 중복 탐지, 조건별 통계와 Markdown/JSON 보고서 생성 |
| `evaluations/fixtures/*.json` | 정상·실패·누락·중복·역전·단위 오류 fixture |
| `evaluations/README.md` | 로컬 실행 방법과 결과 해석 한계 |
| `tests/test_evaluation_summary.py` | 정상/실패/경계 집계 회귀 |

## Run record 계약

최상위 JSON은 `schema_version`, `study_id`, `runs`를 가진다. 각 run은 다음 필드를 가진다.

| 필드 | 규칙 |
|---|---|
| `run_id` | study 안에서 유일한 문자열 |
| `scenario_id` | 여섯 scenario 파일의 식별자 |
| `condition` | `mpa` 또는 `baseline` |
| `pair_id` | 같은 초기 조건의 비교 쌍 식별자; 비교할 수 없으면 `null` |
| `status` | `completed`, `failed`, `stopped` 중 하나 |
| `started_at`, `ended_at` | UTC ISO-8601; ended는 started보다 이르지 않음 |
| `active_seconds`, `user_wait_seconds` | 0 이상의 정수 초; 제공되지 않으면 `null` |
| `token_count` | 0 이상의 정수 또는 `null`; 미제공을 0으로 기록 금지 |
| `quality` | `accepted`, `rejected`, `unverified` 중 하나 |
| `events` | 개입·정정·결함·재작업 사건 목록 |

사건은 `kind`, `at`, `necessity`를 가진다. `necessity`는 당시 정보로 판정한 `necessary`, `unnecessary`, `unknown` 중 하나다. `user_wait_seconds`는 비용 지표일 뿐 불필요한 질문의 증거로 사용하지 않는다.

## 집계 규칙

1. 모든 completed/failed/stopped run은 조건별 표본수와 성공률 분모에 포함한다. 성공은 `status=completed`와 `quality=accepted`의 동시 충족이다.
2. 시간 요약은 유효한 `active_seconds`를 가진 전체 run과, 양쪽이 성공한 `pair_id`의 paired subset을 구분한다. 표본수·중앙값·최솟값·최댓값·누락 수를 각 표에 기록한다.
3. 조건·scenario별 개입, 중복 의도/승인 요청, 진행을 막는 사용자 대기, 정정·결함·재작업 사건을 합계와 necessity별 수로 낸다. `unknown`은 별도 표기한다.
4. 같은 `run_id`, 알 수 없는 scenario/condition/status, 음수 값, timestamp 역전, 정수가 아닌 시간/토큰은 입력 오류로 거부한다. 성공 쌍이 없으면 차이를 계산하지 않고 `not_available`로 보고한다.
5. JSON 보고서는 재생성 가능한 기계 결과이고, Markdown 보고서는 같은 값의 사람용 표현이다. 어느 쪽도 통계적 유의성이나 성과 개선을 선언하지 않는다.

## 시나리오

| ID | 작업 | 수용 기준 |
|---|---|---|
| `wording_edit` | 문구 수정 | 지정 문구만 바뀌고 관련 검사가 통과 |
| `configuration_edit` | 설정 수정 | 스키마/기존 값 보존과 검증 명령 통과 |
| `bug_fix` | 재현 가능한 버그 수정 | 재현 실패 경로가 해소되고 회귀 검사 통과 |
| `multi_step_feature` | 다단계 기능 | 명시된 하위 결과와 테스트가 모두 충족 |
| `session_resume` | 중단 작업 재개 | 재개 요청 뒤 최초 기준 충족 행동과 최종 결과 기록 |
| `intent_change` | 진행 중 목적 변경 | 변경 전/후 의도와 승인·재계획 필요성을 분리 기록 |

모든 scenario 문서는 합성 초기 저장소 상태와 중단 조건을 포함한다. 실제 프로젝트나 사용자 파일은 fixture로 사용하지 않는다.

## 구현 순서

1. scenario와 schema/protocol을 함께 확정해 집계 구현이 임의의 입력을 정의하지 않도록 한다.
2. 표준 라이브러리만 쓰는 parser/validator와 JSON 보고서를 만든다.
3. Markdown renderer와 CLI (`input`, `--json-out`, `--markdown-out`)를 추가한다.
4. 정상·누락·중복·실패·역전·단위 오류 fixture로 단위 테스트를 작성한다.
5. README와 guidebook 링크에 실행 예시와 “측정 수단이지 효과 증명 아님” 한계를 기록한다.

## 반례와 완화

- 한 조건이 더 긴 사용자 대기를 기록할 수 있다. → 시간만으로 불필요한 질문을 판정하지 않고 사건 necessity를 `unknown` 허용으로 보존한다.
- run마다 모델/도구 권한이 달라질 수 있다. → protocol의 condition manifest가 다르면 같은 비교 cohort에 넣지 않는다.
- 실패 run이 원시 기록에서 빠질 수 있다. → `status`가 없는 record는 거부하고, 조건별 전체 분모와 제외 사유를 보고한다.
- 소표본의 우연 차이가 커 보일 수 있다. → 중앙값·범위·표본수를 표시하며 개선율·유의성을 결론으로 쓰지 않는다.
