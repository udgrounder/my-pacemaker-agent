# MPA 협업 효과 비교 프로토콜

이 문서는 MPA 적용(`mpa`)과 미적용(`baseline`)의 작업 결과를 로컬에서 비교하는 방법이다. 집계 결과는 실험 설계와 표본 수의 한계 안에서만 읽으며, 성과 개선이나 인과관계를 자동으로 주장하지 않는다.

## 비교 단위

각 `pair_id`는 같은 scenario·초기 소스·요청을 한 번씩 실행한 `mpa`와 `baseline` run을 묶는다. 두 run의 model, model version, settings reference, tool permissions, source reference, request reference, time limit은 동일해야 한다. 집계기는 다르면 입력 오류로 거부한다.

각 scenario는 조건당 3회 pilot을 권장한다. 실행 순서는 pair마다 교차한다. 예를 들어 첫 pair는 baseline→mpa, 다음 pair는 mpa→baseline 순서로 실행한다. 각 run은 독립 작업 디렉터리와 독립 세션에서 실행해 이전 대화나 작업 파일이 다음 조건에 영향을 주지 않게 한다.

## 기록

평가자는 작업 시작/종료 시각, active time, user wait time, token count가 제공된 경우만 기록한다. 값을 알 수 없으면 `null`로 남긴다. 시각은 모두 UTC ISO-8601(`Z`)으로 기록한다. `session_resume`는 `resume_requested_at`과 `first_acceptance_action_at`을 함께 기록하고, 집계기는 두 시각의 차이를 재개 시간으로 계산한다. 사용자에게 별도 설문, 수동 타이머, 같은 입력의 재입력을 요구하지 않는다. 기존 run 기록에서 추출할 수 없는 값은 평가 비용 또는 미확인으로 보고한다.

`events`에는 다음 사건을 남긴다.

| kind | 의미 |
|---|---|
| `user_intervention` | 사용자의 추가 판단·답변 |
| `duplicate_intent_request` | 이미 전달된 의도/승인을 다시 요청 |
| `blocking_wait` | 사용자 응답이 없어서 진행을 멈춘 대기 |
| `correction` | 사용자가 agent 판단을 정정 |
| `defect` | 결과 결함 발견 |
| `rework` | 이전 결과를 다시 작업 |

`necessity`는 당시 정보로 `necessary`, `unnecessary`, `unknown`을 기록한다. 사용자 대기 시간 자체는 생활 여건의 영향을 받으므로 불필요한 질문의 증거가 아니다.

## 판정과 중단

성공은 `status=completed`와 `quality=accepted`가 모두 성립할 때다. failed·stopped run도 전체 표본수와 성공률 분모에 포함한다. 실행을 중단하면 `status=stopped`와 비어 있지 않은 `stop_reason`을 함께 기록한다. stopped가 아닌 run의 `stop_reason`은 `null`이다. 품질을 판단하지 못하면 `quality=unverified`로 남긴다.

시간 차이는 양쪽이 모두 성공한 pair에서만 별도로 계산한다. 전체 표는 모든 run의 active time을 포함하며, 누락 시간은 제외한 표본수와 함께 표시한다. token count를 제공하지 않은 run은 0 token으로 취급하지 않는다.

## 보안과 해석 제한

입력 파일에 실제 프로젝트 내용, credential, 개인 경로, 대화 원문을 넣지 않는다. 결과는 로컬에만 저장하고 원격 전송이나 모델 호출을 하지 않는다. 합성 fixture는 집계기 검증용이며 실사용 성과 증거가 아니다.
