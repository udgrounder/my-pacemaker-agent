# 보완 구현 독립 검증 1차

검증일: 2026-10-13
최종 판정: 남은 필수 수정 finding 없음. 검증 중 P2 1건과 P3 1건을 실제 재현했고, 메인 에이전트 보완 이후 동일 경로를 재검증했다. 테스트 통과만으로 저장 안전성을 판단하지 않았으며 범위 밖 동시성·전원 손실 원자성은 보장하지 않는다.

## 독립성과 대상

대화 상속 없는 호출로 검증했다. 태스크 plan, 지정 hooks(plan_hash/code_gate/session_start), core 규칙·상세, plan_template, 지정 3개 테스트, guidebook, architecture, layer1_review/_agent_execution_priority를 읽었다. changelog와 이전 검토결론 파일은 읽지 않았다. 소스는 수정하지 않았고 이 검증 기록만 작성했다. 검증 중 전달받은 메인 에이전트의 수정 소식은 증거로 삼지 않고 실제 코드와 재현 결과로 판정했다.

## 최종 검토 결과

### 즉시 수정 필요

없음. 아래 검증 중 발견의 보완을 최종 코드에서 재확인했다.

### 주의 필요

- 잔존 JSON의 before/after뿐 아니라 확보 파일 실제 내용을 복구 시 함께 읽어야 한다. 지원 writer 직렬화와 별개로 외부 편집이 확보 inode에 남을 수 있다. 코드·상세 규칙 모두 이를 복구 필요로 처리한다.
- 비협조 편집기 완전 동시지원, 완료 후 외부 쓰기 추적, 전원 손실에 대한 두 파일 원자성은 계약 밖이다. 이 보고서와 테스트 결과는 그 보장을 주장하지 않는다.

## 검증 중 발견과 해결 증거

### [P2, 해결] rename 성공 후 플래그 설정 이전 SIGINT가 확보 원본을 삭제

조건: 실제 os.rename 성공 직후 captured=True 이전 KeyboardInterrupt. 보완 전 `.mpa/runtime/hooks/plan_hash.py:241–242`의 이동/플래그와 `:252–255`의 예외 처리에서 captured=False만으로 backup을 unlink했다. 실제 이동은 이미 끝났으므로 target도 backup도 사라졌다. 교체 직전 외부 증빙은 JSON before에도 없어 복구 불가능했다.

실제 임시파일 재현: os.rename 래퍼가 대상 plan에 `LATE_EXTERNAL_EVIDENCE`를 추가하고 실제 rename를 수행한 다음 `os.kill(os.getpid(), signal.SIGINT)`를 호출했다. 실제 KeyboardInterrupt가 전달됐으며 보완 전 결과는 다음과 같았다.

```text
KeyboardInterrupt delivered after actual rename
target exists: False
captured original exists: False
journal contains external evidence: False
```

이것은 rename를 실패시키는 모사가 아니라 실제 이동 성공과 비동기 인터럽트를 결합한 경계 검증이다. 기존 이력 저장 뒤 write_plan에서 KeyboardInterrupt를 주입하는 테스트는 이 경계를 검증하지 못했다.

최종 소스: `plan_hash.py:237–238`에서 확보 placeholder의 st_dev/st_ino를 기록하고 `:257–262`에서 예외 시 실제 inode를 대조한다. 판정 불가도 삭제 근거로 사용하지 않는다. `:266–272`는 빈 경로에만 확보파일을 링크해 복원한다.

동일 실제 SIGINT 재검증을 최초 plan 확보와 plan 저장 실패 뒤 history 원복 확보에서 각각 수행했다.

```text
plan-capture target evidence: True saved evidence: True journal present: True audit recovery: True
history-rollback target evidence: True saved evidence: True journal present: True audit recovery: True
```

현재 경로와 실제 확보 파일 모두 외부 증빙을 보존하며 JSON이 잔존해 완료로 오인하지 않는다. 해결 판정.

### [P3, 해결] 프론트매터 없는 외부 편집 plan과 JSON이 함께 있을 때 audit 복구 사유 누락

조건: 새 plan 설치 직전 외부 writer가 프론트매터 없는 사용자 증빙 파일을 만든다. link는 EEXIST로 교체를 거부해 해당 파일과 JSON을 보존한다. 그러나 보완 전 audit의 프론트매터 없음 조기 반환(`plan_hash.py:430–432`, 당시 줄)은 missing만 반환하고 recovery invalid를 생략했다. 명령 재실행은 막혔지만 audit 출력만 읽는 사용자가 저장 중단 복구보다 프론트매터 초기화로 잘못 진입할 수 있었다.

실제 충돌 재현: link 직전 실제 파일에 `external user evidence` 생성 → 사용자 내용 보존, JSON 잔존, audit.frontmatter_exists=False/missing=6/invalid=[]. check=1, approve/init/renew-spec=2는 모두 복구 필요 안내였다.

최종 코드로 프론트매터 없는 텍스트+JSON을 다시 검사한 결과:

```json
{"frontmatter_exists": false, "missing": ["태스크", "생성일", "타입", "실패비용", "상태", "승인해시"], "invalid": [{"field": "승인해시", "value": "", "reason": "승인 저장 중단 복구 필요: .plan-renewal.json을 먼저 대조하세요"}]}
```

복구 이유가 다시 우선 표시되므로 해결 판정.

## 실행 근거

- 최종 지정 테스트: `python3 -m pytest -q tests/test_plan_hash.py tests/test_structure_loading.py tests/test_todo_policy.py` → **59 passed in 0.18s**. 최초 57개, audit 보완 후 58개, rename 중단 보완 후 59개를 각각 실행했다. 최종 결과만 현재 판정의 테스트 근거다.
- 실제 정상 임시파일 renew_spec: `.plan-renewal*` 잔존 0개, audit.invalid=[].
- 실제 충돌 추가 재현: link 직전 외부 plan 생성 시 외부 파일 보존과 JSON 잔존, 명령 거부를 확인했다.
- 실제 중단 추가 재현: rename 성공 직후 SIGINT를 최초 plan 교체·history 원복에서 각각 전달하여 실제 확보 inode 보존을 확인했다.
- 테스트 소스를 읽어 실패 주입 위치와 assertions를 대조했다. 기존/부재 changelog 원복, 교체 직전 외부 편집, 빈 경로 설치 직전 충돌, 확보 inode 외부 변경, 원복 설치 직전 충돌, 최종 이력 불일치, 복구 자료 정리 실패, 이력 저장 후 중단을 실제 임시파일과 함께 검증하는 테스트가 통과했다.
- 게이트·세션의 현재 선택 critical+JSON+plan 경로 부재와 복구 우선 안내는 test_plan_hash.py의 실제 임시 workspace 기반 테스트를 통해 확인했다. 별도 `tests/test_code_gate.py`, `tests/test_session_start.py`는 존재하지 않으며 그 이름으로 추가 시도한 호출은 no tests ran이었다. 그 호출을 통과로 집계하지 않았다.
- source/dist 전체 파일별 bytes 비교는 test_structure_loading에서 통과했다. 릴리즈·배포 완료로 해석하지 않았다.

## 계약 대조

- 최종 `guarded_write:244–252`는 교체 직전 대상 inode를 이동·확보하고 예상 원본을 대조한 뒤 hard link로 빈 경로에만 설치한다. 원복도 같은 함수를 사용한다.
- `verify_approval_files:279–285`는 plan/changelog와 확보 원본까지 대조한다. write_approval_pair가 정상 저장·원복 뒤 이를 실행하고 그 뒤에만 cleanup한다. 확인된 확보 inode 외부 편집과 최종 파일 불일치는 JSON/확보파일을 남겨 복구 필요로 처리한다.
- code_gate와 session_start는 경로 부재+JSON도 작업으로 발견하며, gate는 JSON plan_before에서 critical 실패비용을 읽는다. 복구 안내는 상세 규칙의 `승인 이력 저장과 복구`로 직접 진입한다.
- core detail의 복구 트리거는 프론트매터 초기화·명세 재승인보다 먼저 읽도록 연결돼 있다. 명령 루트 check/approve/init/renew 및 audit도 잔존 JSON을 우회하지 않는다.
- plan_template:165의 `## 운영 시 안내 사항`과 :173의 `## 구현 후 발견`은 최상위 형제 섹션이다. 발견이 운영 안내 하위로 흡수되지 않는다. test_todo_policy의 해당 구조 검사도 통과했다.
- 코드 write_approval_pair docstring, core detail `승인 이력 저장과 복구`, guidebook:922, architecture:71, plan 현재 검토 대상은 지원 writer 직렬화와 비협조 편집기의 완전 동시 쓰기 제외에 대응한다. 전원 손실 원자성 및 완료 후 저장 통제를 추가 보장한다고 해석하지 않았다.

## 조용한 결정과 가정

- JSON before/after는 호출 시점 스냅샷이고 preserved는 실제 교체 직전 inode다. 두 시점의 내용은 달라질 수 있다. 의도적으로 분리한 보존 근거이며 최종 코드의 중단 판정 보완 후 실제 보존을 확인했다.
- 기존 plan 내부 승인 이력 표는 단일 파일 저장, 새 배치는 changelog 두 파일 저장이다. 기존 배치 호환 가정과 정합하다. approval_history_match의 정확한 제목·중복·위치 검사와 관련 테스트를 확인했다.
- 해시 명세 알고리즘을 바꾸지 않는 제한된 승인 저장 변경이라는 가정은 유효하다. 다중 문서와 승인 상태/이력/복구가 연결되므로 실패 비용 major에 하향 근거는 없다.

## 남은 검증 한계

검증 범위에서 새 필수 문제는 남지 않았다. 완전 동시 편집이나 전원 손실 원자성은 계약 밖이므로 미지원 영역을 안전하다고 주장하지 않는다. 사용자 결과 확인·완료 승인 판단과 changelog 대조 2차는 이 1차 기록의 대상 밖이다.

정정 회고: 최초 인터럽트 재현에서 확보파일 FileNotFoundError를 단순 테스트 오류로 넘기지 않고 실제 삭제로 확인했다. 잘못된 별도 테스트 파일명으로 시도한 추가 호출은 no tests ran으로 명확히 기록했다.
