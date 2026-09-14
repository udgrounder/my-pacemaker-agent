# 1차 구현 검토: MPA 협업 효과 측정 체계

## 판정

**수정 필요**. 여섯 시나리오, 로컬 입력만 사용하는 CLI, 실패 run을 성공률 분모에 넣는 집계, `null`을 0으로 바꾸지 않는 요약은 계획과 대체로 일치한다. 그러나 중단·재개·시간 표현 계약과 사용자 개입의 scenario별 집계가 완료 기준을 충족하지 못한다. JSON Schema를 실제 validator와 같은 계약으로 쓸 수도 없다.

## 발견사항

### P1 — 중단 사유와 재개 시간 기록 계약이 구현되지 않았다

- **근거:** `evaluations/protocol.md:30`은 stopped run의 중단 이유를 `notes`에 기록하라고 한다. 그러나 `evaluations/schema.json:40-56`의 run은 `additionalProperties: false`이고 `notes`가 없다. 반대로 Python validator는 run의 추가 키를 금지하지 않아 `notes`를 받아들인다. 즉 프로토콜대로 만든 기록은 Schema에서 거부되고 CLI에는 통과한다.
- **재개 누락:** `evaluations/scenarios/session_resume.md:5`는 재개 요청부터 최초 기준 충족 행동의 시각 기록을 수용 기준으로 둔다. schema와 `summarize.py`에는 그 시각 또는 재개 소요 시간을 저장·검증·요약할 필드가 없다. 이는 계획 완료 기준 3의 재개 시간 정의를 재생성 가능한 원시 기록으로 남기지 못한다.
- **재현:** 정상 fixture의 첫 run에 `"notes": "reason"`를 추가하면 `validate_study()`는 통과하지만 Schema는 `additionalProperties: false` 때문에 거부해야 한다. 현재 테스트에는 이 상호 운용성 검증이 없다.
- **수정 방향:** 중단 사유와 재개 요청/최초 기준 충족 시각을 정식 필드로 계약화하고, Schema와 Python validator가 같은 허용/필수/추가 속성 규칙을 적용하게 한다. stopped run에서의 사유 필수 여부도 명시한다.

### P1 — 시간대가 섞인 유효하지 않은 입력이 제어된 validation 오류가 아니라 `TypeError`를 낸다

- **근거:** `summarize.py:34-40`은 timezone 유무를 검사하지 않고 `datetime.fromisoformat()` 결과를 반환한다. 이어 `summarize.py:81`의 `ended < started` 및 `:99`의 event 범위 비교는 naive/aware datetime 조합에서 `TypeError`를 발생시킨다. `StudyValidationError`만 CLI에서 처리하므로 사용자는 입력 오류 설명 대신 traceback을 받는다.
- **재현:** `valid-study.json`의 첫 run `started_at`을 `"2026-09-10"` 또는 `"2026-09-10T00:00:00"`으로 바꾸고 `validate_study()`를 호출하면 `TypeError: can't compare offset-naive and offset-aware datetimes`가 난다. `"2026-09-10T00:00:00+09:00"`은 통과한다.
- **영향:** 설계의 UTC ISO-8601 계약(`design-notes.md:32`)과 Schema의 date-time 형식이 Python 검증에서 일관되게 강제되지 않는다. 비교 기록의 시간 역전·단위 오류를 거부한다는 완료 기준 6의 오류 처리도 이 경로에서는 성립하지 않는다.
- **수정 방향:** timezone을 가진 UTC timestamp만 명시적으로 허용하고, 모든 시간 파싱/비교 실패를 `StudyValidationError`로 변환한다. 이 경우를 CLI와 단위 테스트에 넣는다.

### P1 — 사용자 불편 사건을 scenario별로 집계하지 않는다

- **근거:** `design-notes.md:44`와 계획 완료 기준 7은 조건·scenario별로 개입, 중복 의도/승인 요청, blocking wait, 정정·결함·재작업을 necessity 분류와 함께 집계하도록 정한다. `summarize.py:131-145`는 condition 전체의 사건 수만 만들고 scenario별 결과를 반환하지 않는다.
- **영향:** 한 시나리오에서 반복된 불필요한 질문이 다른 시나리오의 정상 결과에 가려진다. 따라서 필요한 판단을 유지하면서 불필요한 개입을 줄였는지, 사용자 불편 최소화라는 측정 목적을 사례 단위로 검토할 수 없다.
- **수정 방향:** `condition → scenario`별 event kind 및 necessity summary를 JSON/Markdown에 추가하고, mixed-scenario fixture로 집계값을 검증한다.

### P2 — Schema 검증과 실패·중단 경계 테스트가 비어 있다

- **근거:** `tests/test_evaluation_summary.py`는 Python validator와 CLI만 호출하며 `evaluations/schema.json`을 읽거나 Schema의 허용/거부 결과를 검증하지 않는다. `valid-study.json`은 failed run 하나만 포함하고 stopped run, stopped 사유, 정상 completed-but-unpaired run, 재개 시각, timezone 오류를 검증하지 않는다.
- **영향:** 현재처럼 Schema와 validator가 갈라져도 5개 테스트가 모두 통과한다. changelog의 “필수 측정값 누락” 검증은 존재하지만, 완료 기준의 중단 처리와 JSON Schema 계약은 회귀 방지 대상에서 빠진 상태다.
- **수정 방향:** Schema와 Python validator의 같은 입력에 대한 contract tests를 추가하고, stopped·null·unpaired·재개·timezone 혼합 사례를 독립 fixture 또는 명시적 test case로 다룬다.

## 확인한 충족 사항

- `evaluations/scenarios/`의 여섯 문서는 모두 입력·초기 상태·수용 기준·실패 판정·중단 조건을 포함한다.
- `summarize.py:133-153`은 failed/stopped를 조건별 run 수와 성공률 분모에 포함하고, 성공·accepted 양쪽 조건을 통과한 pair에 한해 active-time 차이를 계산한다. `null` 시간·토큰은 0이 아닌 missing/count로 보존한다.
- `protocol.md:13, 26, 32`는 매 턴 설문·수동 타이머를 요구하지 않고, user wait를 불필요한 질문의 직접 증거로 사용하지 않으며, 성공 pair의 시간 비교를 별도 처리한다.
- `python3 -m unittest tests/test_evaluation_summary.py` 실행 결과: 5 tests passed.

## 남은 한계

이 검토는 계획에 지정된 평가 산출물과 테스트만 대상으로 한 정적·합성 입력 검토다. 실제 모델 실행, 실사용 프로젝트 수집, 성과 또는 인과효과의 검증은 수행하지 않았다. 다만 위 계약 결함은 실제 실험 이전에 해소되어야 비교 기록을 재현 가능하게 읽을 수 있다.
