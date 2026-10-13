# 보완 구현 독립 검증 2차 대조

검증일: 2026-10-13
최종 판정: 현재 미해결 필수 finding **0개**. 원래 P2 3건·P3 1건과 1차 보완 검증 중 inode/SIGINT·audit 지적은 최종 구현에서 해결됐다. 검증 중 현재성 기록 정리 2건을 전달했고 메인 에이전트의 반영을 실제 문서에서 확인했다. 사용자 결과 확인·완료 승인은 별도다.

## 대조 범위

대화 상속 없이 plan/changelog/repair_review_phase1과 실제 source Runtime, 지정 테스트, guidebook·architecture 및 Git diff를 대조했다. 1차 설명을 판정 근거로 대신하지 않았다. 소스는 수정하지 않았으며 이 보고서와 repair_review_summary만 Write 도구로 작성했다.

| 지적 | 최종 구현·실행 근거 | 판정 |
|---|---|---|
| 검사 뒤 교체·원복 직전 외부 편집 유실 | plan_hash.py:216–276 guarded_write가 실제 inode를 rename으로 확보하고 예상 원본 대조 후 link로 빈 경로에 설치한다. 원복도 같은 경로다. 교체 직전 편집·설치 직전 충돌·원복 직전 충돌 테스트가 외부 증빙 보존을 확인한다. | 해결 |
| 이력 승인행 유실 뒤 성공 오인 | :279–285가 plan/changelog와 확보 파일 실제 내용까지 대조한다. :363–369는 불일치·정리 실패를 복구 필요로 반환한다. 이력 저장 뒤 편집·확보 inode 편집 테스트 통과. | 해결 |
| 복구 상세 로드·재승인 경로 누락 | core 필수 트리거, detail:16/49/72/87–98, gate 저장 중단 메시지, session_start JSON 우선 안내, audit/check/approve/init/renew 잔존 탐지를 대조했다. plan 없는 선택 critical·세션 테스트 통과. | 해결 |
| 발견 제목의 운영 안내 하위 편입 | plan_template:165/173의 운영 안내와 구현 후 발견은 `##` 형제다. minor 생략 참조·구조 테스트와 일치한다. | 해결 |
| rename 성공 후 captured 설정 이전 SIGINT | :237–238 예약 inode와 :257–262 실제 inode 대조로 이동 성공을 판단하고 미확인도 삭제 근거로 삼지 않는다. 실제 신호 경계 재현 통과. | 해결 |
| 프론트매터 없는 외부 plan의 audit 사유 누락 | :440–445 조기 반환에도 JSON 잔존 복구 invalid를 추가한다. 해당 실제 임시파일 테스트를 읽고 실행했다. | 해결 |

## 실행 증거

- `python3 -m unittest discover -s tests`: **219 tests, OK**, exit 0 (요약 확보 실행 4.759s).
- `python3 -m pytest -q tests/test_plan_hash.py tests/test_structure_loading.py tests/test_todo_policy.py`: **59 passed in 0.19s**, exit 0. 구조·TODO 테스트가 포함되므로 changelog의 plan_hash 관련 53개와 모순되지 않는다.
- 기존 interrupt 회귀 테스트 fixture/assertions를 사용하되 디스크 소스 수정 없이 메모리에서 `raise KeyboardInterrupt`를 `os.kill(os.getpid(), signal.SIGINT)`로 바꾸어 실행했다. 실제 rename 성공 직후 신호 전달이며 현재 경로와 JSON preserved 파일 모두의 외부 증빙 보존 assertion이 통과했다.
- 같은 경계를 history rollback에도 적용했다. write_plan 실패로 원복을 유발한 뒤 history 실제 rename 직후 SIGINT를 전달했다. 현재 history와 preserved 파일의 외부 증빙 보존 assertion이 통과했다.
- 현재 plan check: **reqspec-v1:74809779fbf1bef0 일치**, exit 0. audit: frontmatter_exists=true, missing=[], invalid=[], exit 0.
- source/dist 전체 `diff -qr`와 `git diff --check`: 출력 없음, exit 0.

## 이력·승인·한계 대조

최초 승인해시는 유지됐고 명세 변경 이력 표에 새 갱신 행은 없다. 실행 보완·독립 재검증은 명세 밖 기록이며 기존 요구사항·해시 알고리즘을 낮추거나 변경하지 않았다. changelog는 이전 208개·후속 실패 4건·217개 보완·최종 219개 및 추가 두 지적을 보존하고, 이전 '0개'를 현재 판정으로 사용하지 않는다.

지원 writer 직렬화는 모든 편집기를 잠그는 기능이 아니다. core:294의 단일 담당자·JSON 잔존 시 편집 중단과 O_EXCL journal/잠금 후 원본 재대조가 지원 경로의 계약이다. detail:98·write_approval_pair docstring·plan 현재 검토 대상은 비협조 편집기의 완전 동시 쓰기, 완료 후 외부 저장, 전원 손실 두 파일 원자성을 명시적으로 제외한다. guidebook·architecture도 완전 동시 저장을 주장하지 않는다. 최종 대조 뒤 cleanup 중 새 비협조 쓰기까지 검출한다고 해석할 수 없다. 이번 테스트·재현은 확인된 경계의 보존 근거이며 모든 신호 경계·전원 손실 안전성의 증명은 아니다.

## 기록 현재성 대조

검증 중 두 정리 사항을 발견했다: plan 마지막 구현 단계에 '지적의 수정이 남아 있다'는 오래된 설명이 있었고, 수정 대상 목록에 실제 변경 code_gate.py/session_start.py/session_protocol.md가 명시되지 않았다. session_protocol 재개 흐름 변경도 changelog에 직접 명시되지 않았다.

메인 에이전트 반영 후 실제 문서를 재조회했다. plan 마지막 단계는 보완·재검증 통과와 독립 2차 최종 기록 확인으로 갱신됐고, 대상 Runtime·테스트·분류 문서 목록을 보완했다. changelog 실제 구현에는 session_protocol 변경이 추가됐으며 기록 정리 근거도 남았다. 두 정리 사항은 해결됐다.

보고서 저장 시점에는 plan/changelog의 독립 재검증 중/남은 확인 표시가 이 검증의 최종 기록 반영을 기다리는 상태다. 이 보고서 이후 주 에이전트가 최종 검증 상태를 반영하면 된다. 사용자 확인 전 active 유지와 릴리즈·배포 제외는 적절하다.
