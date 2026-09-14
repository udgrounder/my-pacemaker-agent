# MPA 내부 구조

이 문서는 MPA source를 유지보수하는 개발자를 위한 지도다. 설치된 프로젝트 사용자는 별도 설정이나 명령을 수행할 필요가 없다.

## Runtime 정책 로딩

`core/agent_rules.md`는 모든 세션에서 참조하는 라우팅·상태 전이·승인/완료 경계와 사용자 부담 최소화 원칙만 둔다. 상세 절차는 조건이 발생할 때 `core/agent_rules_detail.md`를 읽는다.

| 상황 | 정본 |
|---|---|
| major 설계 | `inject/layer1_design.md` |
| minor 계획·자동 승인·최소 확인 | `core/agent_rules_detail.md`의 `minor 경량 처리 절차` → `templates/plan_template.md` |
| 승인 기록·명세 해시 갱신 | detail의 `승인 기록 처리` |
| 완료 인정·done 이동 | detail의 `완료 인정 판별 기준`, `작업 항목 완료 처리` |
| 독립 비평·구현 검증 | `inject/layer1_critique.md`, `inject/layer1_review.md`, `_agent_execution_priority.md` |

minor는 `layer1_design.md`를 선행 조건으로 삼지 않는다. 이 규칙은 필요한 규칙만 읽으면서 기존 minor 흐름을 보존한다.

Runtime 파일을 수정하면 `python3 release_manager.py sync-runtime`으로 `dist/.mpa/runtime/`를 동기화한다. 이는 source와 배포본의 파일을 맞추는 작업일 뿐, release 생성이나 설치 대상 배포를 수행하지 않는다.

## Source 운영 코드

`release_manager.py`는 CLI와 release 생성, backup/config, 이슈 수집 transaction, deploy/rollback 조정을 소유한다. 외부 CLI·함수 이름과 기존 테스트의 monkey patch 지점은 이 파일에 남긴다.

`release_manager.py`는 기존부터 같은 source root의 `project_config.py`를 import하는 source tool이다. 경로 기반 spec loader를 사용할 때도 source root를 Python import path에 둔다. 이 계약으로 외부 작업 디렉터리의 loader와 CLI에서도 `mpa_ops`를 같은 source tree에서 해석한다.

| 모듈 | 책임 | 경계 |
|---|---|---|
| `mpa_ops/archive_io.py` | Runtime/backup ZIP 생성·검사·해제 | facade가 tree/member validator와 ignored name을 전달 |
| `mpa_ops/issue_format.py` | 이슈 metadata 해석·정규화·identity | facade가 regex·marker·path anchor를 전달 |
| `release_manager.py` | 조정·파일 이동·원복·CLI | 내부 모듈을 역방향 import하지 않음 |

deploy는 여러 복구 실패를 수집해 계속 복구를 시도한다. rollback은 현재의 별도 복구 동작을 유지한다. 구조 변경에서 두 흐름을 공통화하거나 관측 가능한 오류·receipt·history 동작을 바꾸지 않는다.

## 검증

구조를 바꿀 때 기존 `tests/test_release_manager.py`와 `tests/test_release_manager_compatibility.py`를 실행한다. 전자는 release, deploy, rollback, issue collection의 정상·실패 경로를 다루며, 후자는 source-root spec loader·CLI·11개 facade patch·source-only release artifact 경계와 ZIP leaf 실패의 deploy/rollback Runtime·issue·config·receipt 복구를 고정한다. Runtime 문서 변경은 `tests/test_structure_loading.py`로 대표 요청 11개 경로, minor 직접 경로, source/dist 전체 파일 parity를 확인한다.
