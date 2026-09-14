# 변경 기록: MPA 협업 효과 측정 체계

## 구현

- `evaluations/scenarios/`에 문구 수정, 설정 수정, 버그 수정, 다단계 기능, 세션 재개, 의도 변경의 6개 비교 사례를 추가했다.
- `evaluations/schema.json`과 `evaluations/protocol.md`에 run·사건·동일 조건 manifest·교차 실행·실패/누락 처리 규칙을 정의했다.
- `evaluations/summarize.py`는 로컬 JSON을 검증하고 조건별 성공률·시간·토큰·사용자 개입 사건·성공 쌍 시간을 JSON/Markdown으로 출력한다.
- `evaluations/fixtures/valid-study.json`과 단위 테스트로 정상·실패·누락·중복 ID·시간 역전·단위 오류·조건 불일치·필수 측정값 누락을 검증한다.
- `evaluations/README.md`와 가이드북에서 실행 방법과 결과 해석 한계를 연결했다.
- 독립 1차 검토에서 확인한 중단 사유·재개 시각·UTC 처리·시나리오별 사건 집계 공백을 보완하고 해당 회귀 테스트를 추가했다.
- 2차 검토에서 확인한 JSON Schema의 문자열·UTC 문법 불일치, Markdown 사건 집계 누락, 출력 경로 오류 traceback을 보완했다.
- 2차 후속 검토에서 확인한 달력상 존재하지 않는 날짜의 Schema/Python 불일치를 공통 UTC 패턴과 실제 Schema corpus 테스트로 보완했다.
- 재검토에서 드러난 year zero 입력도 공통 UTC 패턴과 무효 corpus에 포함해 거부한다.

## 검증

- `python3 -m unittest tests/test_evaluation_summary.py -v` — 10 tests passed.
- `python3 -m unittest discover -s tests` — 175 tests passed.
- `python3 -m py_compile evaluations/summarize.py` 및 `python3 -m json.tool evaluations/schema.json` — 통과.
- 합성 fixture를 CLI에 입력해 JSON과 Markdown 보고서 생성 확인.
- `git diff --check` — 통과.

## 한계

이 변경은 측정 도구의 동작만 검증한다. 실제 모델, 사용자 프로젝트, 외부 계정, 원격 전송을 사용한 실험이나 생산성 효과 주장은 포함하지 않는다.

## 독립 구현 검토

- 1차 검토는 수정 필요 판정이었다. 중단·재개 기록, UTC 검증, scenario별 사건 집계를 보완했다.
- 2차 검토는 Schema 문자열·날짜 계약, Markdown 사건 표시, CLI 출력 오류를 지적했다. 공통 invalid corpus에 날짜·윤일·year zero를 포함해 보완했고, 최종 재검토는 통과했다.
