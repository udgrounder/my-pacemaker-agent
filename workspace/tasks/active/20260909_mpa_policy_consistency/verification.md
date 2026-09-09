# 검증 기록

## 범위

2026-09-09 승인 명세 `reqspec-v1:a2b79449a6018630`에 대한 구현 검증. Runtime 지침·호스트 연결 설명·현재 memory·정적/스크립트 회귀 검사를 대상으로 한다.

## 실행 근거

| 검사 | 결과 | 입증 범위 |
|---|---|---|
| `python3 -m unittest discover -s tests -q` 초기 | 150 tests, OK | 기존 142개 + 새 정책/게이트 경계 8개 |
| 같은 전체 테스트, 1차 지적 수정 후 | 151 tests, OK | 완료 승인 우회 문구 검출 1개 추가 포함 |
| 독립 최종 검증 지적 수정 후 | 153 tests, OK | 설치 대상 배포 경계·minor 직접 진입 승인 상태 검사 2개 추가 포함 |
| `python3 .mpa/runtime/hooks/plan_hash.py check workspace/tasks/active/20260909_mpa_policy_consistency/plan.md` | 일치 | 승인 후 요구사항 명세 불변 |
| source/dist Runtime 파일별 bytes 대조 | 58개 일치 | `__pycache__` 제외한 전체 Runtime asset |
| `git diff --check` | 오류 없음 | 변경 diff 공백 형식 |
| hook/plan_hash/install/release_manager와 Git HEAD bytes 대조 | 일치 | 실행 코드·차단 동작·배포 구현을 이번에 바꾸지 않음 |
| source/dist의 기존 로그 규칙 확인 | 보존 | 사용자 편집을 유지 |

최종 테스트 원시 로그: `/tmp/mpa-policy-final-tests.log` (임시 파일). 이 문서에 결과를 보존하며 테스트가 임시 디렉터리에서 만든 release/배포 fixture를 실제 릴리즈·배포로 세지 않는다.

## 독립 검증

- 1차: 대화 상속 없는 검증자가 plan·실제 파일을 대조했다. 사용량 제한으로 한 번 실패했으나 허용된 1회 재시도 후 `review_phase1.md`를 저장했다. 실패한 호출을 완료로 기록하지 않았다.
- 발견: F1 discovery의 완료 승인 우회, F2 승인 기록 누락 시 중복 확인. 두 항목을 실제 파일에서 수정했다. 회귀 검사 1개 및 관련 참조를 추가했다.
- 2차: `review_phase2.md`에서 1차 지적·changelog·현재 실제 파일을 대조했다. F1/F2 해결을 확인하고 추가 F3(팀 workflow의 새 스레드 지시)를 발견해 수정·재검증했다. 남은 즉시 수정 0건, 주의 0건이며 `review_summary.md`에 최종 판정이 있다.
- F3 반영 후 최종 전체 테스트는 151 tests, OK (3.363초). 검증자가 정책 테스트 9개와 parity를 직접 실행했고 전체 151개 통과는 로그로 대조했다.
- 최종 독립 검증은 P4(Runtime source/dist 동기화와 설치 대상 배포의 경계), P5(minor fast-path의 계획 요청 실행 우회)를 발견했다. 수정 후 검증자가 재대조해 두 항목 해결을 확인했고, 전체 153 tests, OK와 Runtime parity를 확인했다.

## 결과 상태

구현·에이전트 검증을 마쳤고 plan은 `테스트 중`으로 사용자 결과 확인을 기다린다. 사용자 완료 승인은 받지 않았으며 active 유지, 후속 hold 작업 미착수, 릴리즈·배포 미실행이다.

## 한계

정적 검사는 알려진 참조·문구만 검사한다. 승인 없는 종료 지침이 남아 있어도 초기 8개 검사가 통과했으므로 의미 검토를 대신할 수 없다. 자연어 정책 사례는 `policy-audit.md`에 문서 경로와 기대 행동을 기록했다.

실제 호스트의 event dispatch·차단 수용·자동 참조 로딩, 모든 환경의 서브에이전트 격리, 모델의 장기 준수율은 미확인이다. 문서/로컬 테스트 결과를 이들 보장으로 확대하지 않는다. 별도 릴리즈·설치 프로젝트 배포는 수행하지 않았다.
