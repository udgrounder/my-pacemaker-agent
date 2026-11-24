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
| 완료 보고 준비·승인 후 보조 자료 정리 | detail의 `완료 산출물 정리`: 최소 정보 저장·대조 → 참조/등록/승인 확인 → 삭제·실제 상태 확인. 정합성 실패 시 이동 보류 |
| 계획 생성·편집·검증 입력 준비·재개 | detail의 `계획서와 변경 이력 관리` — 단일 수정자·복구 우선·현재 실패 노출을 행동 전에 확인 |
| 완료 후 점검 제안·실제 점검 완료 기록 | detail의 `Layer 2 현황 표시` — 제안과 실제 점검 완료를 구별 |
| 독립 비평·구현 검증 | `inject/layer1_critique.md`, `inject/layer1_review.md`, `_agent_execution_priority.md` |

minor는 `layer1_design.md`를 선행 조건으로 삼지 않는다. 이 규칙은 필요한 규칙만 읽으면서 기존 minor 흐름을 보존한다.

Runtime 파일을 수정하면 `python3 release_manager.py sync-runtime`으로 `dist/.mpa/runtime/`를 동기화한다. 이는 source와 배포본의 파일을 맞추는 작업일 뿐, release 생성이나 설치 대상 배포를 수행하지 않는다.

## 작업 INDEX와 공통 계획 점검

일상 작업은 현재 작업 행과 실제 plan/폴더 위치만 대조한다. 다른 작업 행의 불일치나 선행 편집은 보존하며 전체 대조·정리는 사용자 명시 요청 범위에서 수행한다. 대상 행의 편집과 저장 후 보존 확인은 Runtime의 `core/agent_rules_detail.md`에 있다. 파생 작업도 최소 plan 저장 뒤 등록하고, 완료 이동은 기존 승인 뒤에 해당 행만 제거한다.

공통 방법론 계획의 작성·자기 점검·독립 비평은 같은 상세 규칙의 범위 점검을 참조한다. 선택 설계·검증 문서에서도 출처 사례가 공통 합격 조건으로 쓰이는지 확인한다.

## 에이전트 위임

`inject/agent_delegation.md`는 호출 전 위임 판단·모델 상한·단일 수정자 인계의 정본이다. `hooks/agent_policy.py`는 JSON으로 받은 근거를 평가하며 설치·호스트 연결을 수정하지 않는다. `.mpa/config/agent_policy.json`은 설치별 사용자가 관리한다. 필수 독립 실행의 격리·실패 처리는 기존 정본을 따른다.

## Source 운영 코드

`release_manager.py`는 CLI와 release 생성, backup/config, 이슈 수집 transaction, deploy/rollback 조정을 소유한다. 외부 CLI·함수 이름과 기존 테스트의 monkey patch 지점은 이 파일에 남긴다.

`release_manager.py`는 기존부터 같은 source root의 `project_config.py`를 import하는 source tool이다. 경로 기반 spec loader를 사용할 때도 source root를 Python import path에 둔다. 이 계약으로 외부 작업 디렉터리의 loader와 CLI에서도 `mpa_ops`를 같은 source tree에서 해석한다.

| 모듈 | 책임 | 경계 |
|---|---|---|
| `mpa_ops/archive_io.py` | Runtime/backup ZIP 생성·검사·해제 | facade가 tree/member validator와 ignored name을 전달 |
| `mpa_ops/issue_format.py` | 이슈 metadata 해석·정규화·identity | facade가 regex·marker·path anchor를 전달 |
| `release_manager.py` | 조정·파일 이동·원복·CLI | 내부 모듈을 역방향 import하지 않음 |

deploy는 여러 복구 실패를 수집해 계속 복구를 시도한다. rollback은 현재의 별도 복구 동작을 유지한다. 구조 변경에서 두 흐름을 공통화하거나 관측 가능한 오류·receipt·history 동작을 바꾸지 않는다.

## Hook 루트와 설치 설정

`hooks/project_root.py`는 실행 스크립트의 실제 `.mpa/runtime/hooks/` 위치에서 소유 프로젝트를 확인한다. code_gate·session_start·turn_end는 이 루트로 작업 상태를 읽는다. code_gate의 상대 파일·일반적인 `mv active/... done/` 요청은 입력 cwd(없으면 프로세스 cwd)에서 해석한 뒤 소유 루트에 상대화한다. Bash 감시는 줄 시작이나 일반 명령 구분자 뒤에 직접 적힌 일반 `mv`의 리터럴 출발·도착 경로를 확인하는 보조 절차다. 완료 승인 확인의 정본은 작업 항목 완료 처리 규칙이다. 경계 밖·외부로 이어지는 symlink 대상에는 workspace 허용 prefix를 적용하지 않는다. Bash 검사는 shell 전체를 실행·해석하는 보안 경계가 아니다.

`install.py --repair-hooks`는 최신 Runtime이 있는 대상에서 선택한 Claude·Codex settings의 알려진 MPA 명령만 갱신한다. 생성 명령은 가장 가까운 Runtime을 찾되 cwd를 변경하지 않는다. 기존 사용자 설정·모르는 명령은 보존하며 JSON 임시 저장·원본 변경 대조·권한 유지·파일 교체로 저장 실패의 원본 손상을 방지한다. Runtime deploy/rollback은 이 설정을 변경하지 않는다.

`tests/test_hook_project_root.py`는 복사한 실제 Runtime과 생성 명령을 실행해 중첩 cwd·상대 파일·critical 승인·해시·symlink 경계·SessionStart/Stop·일반 mv 판정을 확인한다. `tests/test_install.py`는 관리 명령 이관·사용자 설정 보존·저장 실패와 hook 전용 CLI를 확인한다. `test_plan_hash.py`의 단위 fixture는 소유 루트 resolver만 주입하고 승인 로직을 직접 검증하며, 실제 경로 판정은 별도 통합 fixture가 검증한다. 단위·명령 테스트로 호스트 hook 지원을 보장하지 않는다.

## 검증

구조를 바꿀 때 기존 `tests/test_release_manager.py`와 `tests/test_release_manager_compatibility.py`를 실행한다. 전자는 release, deploy, rollback, issue collection의 정상·실패 경로를 다루며, 후자는 source-root spec loader·CLI·11개 facade patch·source-only release artifact 경계와 ZIP leaf 실패의 deploy/rollback Runtime·issue·config·receipt 복구를 고정한다. Runtime 문서 변경은 `tests/test_structure_loading.py`로 대표 요청 경로, minor 직접 경로, source/dist 전체 파일 parity를 확인한다.


## 선택형 작업 문서

새 작업은 templates/plan_minimal_template.md를 사용한다. major/minor와 문서 수는 분리하고 필요한 implementation/verification/ui_design만 선택한다. inject/task_documents.md가 등록·정본·인계·전환을 소유한다. hooks/task_documents.py는 읽기 전용 구성/경로/기준 검사와 역할 입력 생성을 소유하며 plan_hash audit/approve/check와 기존 gate·SessionStart 안내에 연결된다. 승인 저장/명세 갱신은 기존 plan_hash의 plan 및 plan/changelog 거래를 유지한다.
