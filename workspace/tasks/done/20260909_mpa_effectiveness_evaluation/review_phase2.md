# 2차 구현 검토: MPA 협업 효과 측정 체계

## 최종 재검증 (후속 수정 반영)

**통과.** 2차에서 제기한 Markdown 사건 집계 누락과 출력 경로 traceback은 해소됐다. Schema와 Python validator도 공백 문자열, 잘못된 `Z` 형식, offset/naive 시각, 존재하지 않는 날짜, year zero를 같은 방식으로 거부한다. 마지막 P1의 공통 UTC contract corpus도 추가돼 재현 가능하게 확인됐다.

| 2차 발견 | 최종 상태 | 재검증 근거 |
|---|---|---|
| Schema/validator timestamp·문자열 불일치 | 해소 | `nonblankString`과 공통 UTC pattern은 공백·`not-a-timeZ`·공백 구분 시각·offset 시각·`2026-02-30`·`0000-01-01`을 양쪽에서 거부한다. 2000/2400 윤일 형식도 공통 pattern과 Python parser에서 유효하다. |
| Markdown 사건·scenario 집계 누락 | 해소 | Markdown에 baseline/mpa별 scenario·사건 종류·necessity 표가 생성되며 fixture 결과에서 `duplicate_intent_request`, `defect`, `wording_edit`, `necessary/unnecessary/unknown`을 확인했다. |
| 출력 경로 traceback | 해소 | 존재하지 않는 output parent 실행은 traceback 없이 argparse 오류와 exit 2로 종료한다. |

`python3 -m unittest tests/test_evaluation_summary.py -v`는 10 tests passed. `PYTHONPYCACHEPREFIX=<tmp> python3 -m py_compile evaluations/summarize.py`, `python3 -m json.tool evaluations/schema.json`, `git diff --check`도 통과했다.

### 마지막 P1 해소 확인 — UTC contract corpus

- **근거 및 재현:** `UTC_TIMESTAMP_PATTERN`의 일반 날짜 year가 이제 `0001`~`9999`로 제한되고, 같은 문자열이 `evaluations/schema.json:16`과 `evaluations/summarize.py:29`에 있다. `tests/test_evaluation_summary.py:105-117`은 `not-a-timeZ`, `2026-02-30T00:00:00Z`, `0000-01-01T00:00:00Z`, naive·공백 구분 시각을 실제 `Draft202012Validator(..., FormatChecker())`와 Python validator 양쪽에서 거부한다고 검증한다.
- **추가 독립 확인:** 같은 Schema/Python 실행에서 year zero와 `2100-02-29`는 모두 거부됐고, `2000-02-29` 및 `2400-02-29`의 timestamp 형식은 두 파서에서 유효했다. 이로써 기존 P1의 UTC 문법·달력 범위 불일치는 해소됐다.

## 최초 2차 검토 기록

## 1차 P1 해소 여부

| 1차 발견 | 2차 판정 | 근거 |
|---|---|---|
| 중단 사유·재개 시간 계약 부재 | 해소 | `stop_reason`, `resume_requested_at`, `first_acceptance_action_at`가 schema와 `RUN_FIELDS`의 필수 키로 함께 선언됐다. stopped의 사유 필수 및 session_resume의 두 timestamp 필수/비대상 null 조건도 양쪽에 있다. `test_stopped_and_session_resume_contract`가 stopped run과 40초 resume 요약을 검증한다. |
| UTC 오류가 TypeError로 누출 | Python 경로 해소, schema 경로 미해소 | `_timestamp()`가 `Z`와 timezone을 검사하고 비교 전에 `StudyValidationError`로 바꾼다. naive timestamp CLI 입력은 usage/error와 exit 2로 끝났다. 다만 Schema는 아래 P1처럼 실질적으로 같은 입력을 거부하지 못한다. |
| scenario별 사건 집계 부재 | JSON만 해소 | `summarize()`는 조건별 `scenario_events`에 kind/necessity 집계를 만든다. 그러나 `render_markdown()`은 그 값과 조건 전체 사건값을 출력하지 않는다. |

## 발견사항

### P1 — JSON Schema가 Python validator와 다른 timestamp·공백 문자열을 허용한다 (후속 수정으로 대부분 해소)

- **근거:** `evaluations/schema.json:14`의 `utcTimestamp`는 `format: date-time`과 `pattern: "Z$"`만 선언한다. Draft 2020-12에서 `format`은 assertion vocabulary를 선언하지 않으면 강제 검증이 아니며, 현재 환경의 `Draft202012Validator`도 `date-time` checker를 등록하지 않았다. 따라서 `"not-a-timeZ"`와 `"2026-09-10 00:00:00Z"`는 schema에 통과했다. 반면 `evaluations/summarize.py:39-47`은 전자를 `StudyValidationError`로 거부하고 후자는 Python `fromisoformat()` 특성상 받아들인다.
- **추가 불일치:** schema의 `minLength: 1`은 공백만 있는 `study_id`, manifest 문자열, `pair_id`, `stop_reason`을 허용하지만 Python `_require_string()`은 `strip()` 뒤 비어 있으면 거부한다. 같은 다섯 입력은 JSON Schema에 통과하고 Python validator에서는 모두 `StudyValidationError`였다.
- **영향:** 1차에서 요구한 schema와 validator의 같은 허용 키·필수성·조건부 계약은 필드 목록 수준에서만 확인됐다. Schema만 사용하는 생성자/검증기는 CLI가 거부할 기록을 유효하다고 볼 수 있어 독립 계약으로 쓸 수 없다.
- **재현:** `jsonschema.Draft202012Validator(schema).iter_errors()`에 정상 fixture의 `started_at="not-a-timeZ"` 또는 `study_id="   "`를 넣으면 오류 0개다. 같은 데이터를 `validate_study()`에 넣으면 각각 ISO-8601 오류와 non-empty string 오류다.
- **수정 방향:** UTC timestamp를 실제로 강제하는 정규식 또는 Draft 2020-12 format-assertion vocabulary와 검증기 지원을 명시하고, Python도 그 같은 RFC 3339/UTC 문법으로 파싱한다. 비어 있지 않은 문자열 정의도 schema pattern과 Python에 동일하게 둔다. 실제 JSON Schema validator와 Python validator에 같은 유효/무효 corpus를 적용하는 contract test를 추가한다.

### P1 — Markdown 보고서에 사건·scenario별 집계가 없어 완료 기준 7을 검토할 수 없다 (후속 수정으로 해소)

- **근거:** `evaluations/summarize.py:177-195`는 `conditions[*].events`와 `scenario_events`를 JSON report에 만든다. 하지만 `render_markdown()`(`:215-226`)은 run/성공률/active 중앙값·누락 및 성공 쌍 active 차이만 출력한다. scenario·event·necessity·resume/token/user wait 요약은 Markdown에 없다.
- **영향:** 사람이 CLI의 Markdown 산출물만 열면 동일 의도/승인의 중복 요청, blocking wait, 정정·결함·재작업과 necessity 분류를 조건·scenario별로 비교할 방법이 없다. 이는 plan 완료 기준 7 및 설계의 “JSON과 Markdown은 같은 값의 사람용 표현” 규칙에 맞지 않는다.
- **재현:** fixture CLI 실행으로 만든 `report.json`에는 `conditions.mpa.scenario_events.wording_edit.by_kind.duplicate_intent_request = 1` 및 `necessity.unnecessary = 1`이 있지만, `report.md`에는 `duplicate_intent_request`, `defect`, `necessity`, `scenario` 문자열이 한 번도 없다.
- **수정 방향:** Markdown에 조건×scenario별 event kind·necessity 표(0값/관측 없음의 표현 포함)를 추가하고, 생성 JSON의 해당 값과 일치하는지 테스트한다. 조건 전체 event 및 resume/time/token 요약도 설계의 “같은 값” 범위를 명확히 하거나 표현한다.

### P2 — 출력 파일 오류가 제어된 CLI 오류가 아니라 traceback으로 종료된다 (후속 수정으로 해소)

- **근거:** `main()`은 input read/JSON parse/`summarize()`만 `try`로 감싼 뒤 `Path.write_text()`를 실행한다(`evaluations/summarize.py:233-240`).
- **재현:** `--json-out /private/tmp/no-such-parent/report.json`으로 실행하면 exit 1과 `FileNotFoundError` traceback이 출력된다. 반대로 naive input timestamp는 exit 2와 `parser.error()` 메시지로 정상 처리된다.
- **영향:** 사용자가 존재하지 않는 출력 디렉터리 또는 쓰기 불가 위치를 주면 원인을 간결히 알 수 없고, JSON은 썼지만 Markdown 쓰기에서 실패하는 경우 부분 산출물이 남을 수 있다.
- **수정 방향:** 두 output 경로의 부모/쓰기 가능 여부와 write를 같은 오류 처리 경로에 넣고, 오류 시 nonzero exit와 한 줄의 진단을 낸다. 필요하면 임시 파일 뒤 rename으로 두 산출물의 부분 기록도 피한다.

## 확인한 충족 사항

- 여섯 scenario 문서는 입력·초기 상태·수용 기준·실패 판정·중단 조건을 갖추고, guidebook은 로컬 도구·동일 조건·실제 성과 주장 금지를 연결한다.
- run과 nested manifest/event의 추가 키 금지, 모든 run 필수 키, stopped/session_resume의 조건부 null/필수성은 schema와 Python 구현에서 일치한다.
- 실패·중단 run은 조건별 표본수와 성공률 분모에 남고, successful/accepted pair만 active-time 차이에 포함된다. `null` 값은 0으로 변환되지 않는다.
- `python3 -m unittest tests/test_evaluation_summary.py -v`는 8 tests passed. `PYTHONPYCACHEPREFIX=<tmp> python3 -m py_compile evaluations/summarize.py`, `python3 -m json.tool evaluations/schema.json`, `git diff --check`도 통과했다.

## 한계

이 검토는 로컬 합성 record와 정적 계약, CLI 오류 경로를 대상으로 했다. 실제 모델 실행, 실사용 프로젝트 데이터, 효과의 인과성·통계적 유의성은 검증하지 않았다. JSON Schema 재현은 설치된 `jsonschema 4.25.1`의 Draft 2020-12 validator로 수행했으며, 특정 외부 validator의 옵션만으로 계약을 보완한다고 가정하지 않았다.
