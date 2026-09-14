# 구조 개선 의존성 조사와 상세 설계

조사일: 2026-09-09. 기준 commit: `fef7b9605afc44c98b853a12e565f3dd310235aa`. 아래는 파일 읽기·AST 함수/호출 조사·테스트의 import/patch 조사 결과다. 호스트가 실제로 읽은 토큰이나 준수율을 측정한 결과는 아니다.

## 기준선

| 파일 | 줄 | UTF-8 바이트 | SHA-256 |
|---|---:|---:|---|
| `.mpa/runtime/core/agent_rules.md` | 385 | 34,731 | `4e0fe59c61b682e4b7ef1f10d0ab6b7ec91b8e14b59ff2b9ba2183cf9ade9ac6` |
| `.mpa/runtime/core/agent_rules_detail.md` | 346 | 24,403 | `95ff5f4413b7374b1a0eb6759b483bb0af133216e830faea310d30286e6b323d` |
| `release_manager.py` | 2,247 | 109,570 | `7ecbe1cffb6e018a61d5ec2f999418432af073392a6177004cb5c0520b1008eb` |

release_manager의 최상위 함수는 115개, Runtime 파일은 캐시를 제외하고 58개다. `docs/INDEX.md`와 `workspace/memory/shared/contracts.md`는 현재 없다. 운영 계약의 근거는 `MAP_PRODUCT_RULES.md`, `workspace/memory/shared/architecture.md`, 실제 CLI와 기존 테스트다.

## 문서 진입점과 참조 경로

| 출발점 | 다음 경로 | 성격 |
|---|---|---|
| 루트 `AGENTS.md` | `MAP_PRODUCT_RULES.md` → 요청별 `map-product-rules/`; 일반 작업 → `core/agent_rules.md` | source 전용 라우팅 |
| 루트 `CLAUDE.md`, `agent-specs/{claude,codex}/inject/` | `core/agent_rules.md` | 항상 적용되는 Runtime 규칙 |
| antigravity `GEMINI.md`, 각 native rules/agent 등록 파일 | `core/agent_rules.md` | 같은 Runtime 정본 참조 |
| `hooks/session_start.py` | active 계획 상태 안내·core 라우팅 안내 | 안내문 생성. core 전체를 출력하거나 호스트의 실제 로드를 입증하지 않음 |
| `core/agent_rules.md` | `core/agent_rules_detail.md`, 유형별 `workflows/`, 단계별 `inject/` | 조건부 로드 |
| 설계 inject | task_designer·plan_template·shared 메모리, 비평 기준 충족 시 critique | 설계 컨텍스트 |
| 비평/검증 inject | `_agent_execution_priority.md`, 해당 persona, 지정 산출물 | 독립 실행 컨텍스트; core가 먼저 주입됐다고 가정하지 않음 |
| README·guidebook | 사람이 읽는 설명 | 항상 로드 바이트 집계에 포함하지 않음 |

파일에 참조가 있는 것과 실제로 읽혔다는 것은 다르다. 아래 검증은 정적 도달성·의미 대조이며, 호스트 실행 로그가 없으면 실제 로딩·행동은 미확인으로 표시한다.

## 문서 이동 명세

항상 남길 내용: 사용자 부담 최소화 정본, 세션 시작·INDEX 유지보수, 요청/상태 라우팅, 필수/선택 컨텍스트 표, major/minor 구분, 승인과 완료의 경계, critical 차단 조건, 상세 로드 트리거. 기존 섹션 제목을 참조하는 문서는 제목을 남기고 요약과 직접 목적지로 연결한다.

| ID | 현재 내용 | 이동/통합 목적지 | core에 남길 호출 조건과 경계 |
|---|---|---|---|
| D1 | `작업 항목 생성`의 **major 전용** 상세 TODO 설명·가정/질문/검토 설명 | 기존 `inject/layer1_design.md` 해당 절차에 대조·통합 | major 설계에서만 plan 작성 직전 design 로드. TODO의 증빙 범위와 후속 작업 분리 요약 유지 |
| D2 | `승인 시 처리`·`승인해시 생성 규칙`·`요구사항 명세 재검증`의 명령/복구 상세 | detail에 `승인 기록 처리` 섹션 추가; 기존 `구현 승인 재확인`과 역할 분리 | 최초 승인 기록·승인 기록 복구·명세 변경 판단 전에 detail 로드. 유효 승인 재사용, 명세 변경만 재승인, 승인 이후 상태의 해시 필수 조건은 core에도 유지 |
| D3 | minor/major `작업 항목 완료`의 파일 이동·정리 순서 | detail에 `작업 항목 완료 처리` 추가; `완료 인정 판별 기준` 바로 참조 | 완료 처리 판단/실행 전에 detail 로드. 완료 승인 없이 done 금지, 먼저 상태 기록 → INDEX의 해당 active/hold 행을 제거 → 이동 순서 요약과 증거 기반 보고 유지 |

minor 공통 정책(실패비용 판단, 명확한 실행 요청과 계획 요청의 구별, 공통 plan template, 자동 approve의 전제, 최소 확인·완료 확인)은 `core/agent_rules_detail.md`의 `minor 경량 처리 절차`에 남긴다. D1은 이를 design에 중복 이동하지 않는다. minor는 `core → detail: minor 경량 처리 절차 → template`의 직접 경로를 유지하고, 승인 기록이 필요한 시점에는 같은 detail의 `승인 기록 처리`를 직접 참조한다. `layer1_design.md`는 major의 persona·shared 메모리·설계 절차를 위한 파일이며 minor 실행의 선행 조건으로 만들지 않는다.

이번에는 Root README 원칙, 회고, 세션 시작의 메모리 설명, Layer 2 안내를 이동하지 않는다. 상세 파일을 다시 잘게 나누거나 새 로더·설정·캐시를 추가하지 않는다. D2의 minor 자동 승인 경로는 기존 detail 내부에서 새 승인 기록 섹션을 직접 연결해 우회가 없도록 한다.

기존 `tests/test_todo_policy.py`가 요구하는 core의 “이번 작업 항목이 끝나기 전 증빙”, “구현·설계·검증이 추가로 필요한 후속 작업은 별도 작업 항목” 의미와 문구를 요약에 보존한다. `test_task_index_policy.py`의 core INDEX 계약도 보존한다. 테스트를 약화해 이동을 허용하지 않는다.

## 대표 요청별 정책 도달성 검증표

| 사례 | 읽기 경로 | 반드시 도달할 판단 |
|---|---|---|
| 단순 질문/탐색 | 진입점 → core → on-demand 자료 | 작업을 불필요하게 생성하지 않음; 사용자 부담 최소화 |
| minor 실행 요청 | core → detail 실패비용·minor 경량 처리 → 공통 template → detail 승인 기록 처리 | design·persona·shared 메모리 없이 최소 plan, 자동 approve, 유효 해시 뒤 구현, 최소 확인·완료 확인 |
| minor 계획만 요청 | core → detail minor 경량 처리 → 공통 template | design을 읽지 않음; approve/구현 금지 |
| major 설계 | core → workflow → design → critique 기준/독립 실행 정본 | 가정·사용자 결정 구분, 필수 비평, 설계 완료 뒤 최초 구현 승인 |
| major 구현 승인 | core → detail 승인 기록 처리 → implement | 사용자 승인과 명세 일치, 정상 approve 사용, 임의 해시 금지 |
| 재개/상태 요청 | core → detail 태스크 재개 → 상태별 inject | 기존 승인 재사용, plan 상태 기준 재개 |
| 승인 기록 누락·명세 변경 | core 트리거 → detail 구현 승인 재확인/승인 기록 처리 | 동일 승인 복구와 실제 명세 변경 재승인을 구별 |
| 독립 비평 | critique → priority → critic + 지정 파일 | 대화 상속 금지, 산출물 근거, 실패 시 비평 생략 확인 |
| 독립 구현 검증 | review → priority → reviewer + 지정 파일 | 1차/2차 분리, 실패 시 자가 검증·미확인 표시 |
| 완료 요청/완료 여부 질문 | core → detail 완료 인정 판별 기준 → 완료 처리 | 질문을 승인으로 오인하지 않음; 완료 승인 기록 전 이동 금지 |
| Runtime 수정 | core → detail MPA 수정 세부 → system_designer | source/dist 동기화와 실제 대상 배포 권한 분리 |

각 행을 이동 전후 파일·섹션과 대조해 `verification.md`에 근거를 남긴다. 자동 검사는 참조 파일/제목 누락과 폐기 문구만 검출하며 정책 의미를 증명하지 않는다. 누락 트리거를 일부러 제거한 입력에서 검사가 실패하는 음성 사례도 추가한다.

바이트 비교는 core 단독 필수 payload(34,731바이트)를 고정 지표로 삼는다. 요청별로 core와 필요한 파일/섹션의 합집합 바이트, 전체 파일을 읽는 경우의 상한, 재읽기 횟수 미확인을 함께 기록한다. core 감소만 합격해도 요청별 총량이 증가하면 증가를 보고한다. 절감률 목표를 임의로 잡거나 토큰·시간 개선으로 환산하지 않는다.

## 운영 코드의 현재 책임과 결합

| 영역 | 현재 위치(조사 당시) | 주요 결합 |
|---|---|---|
| 경로·안전·JSON·hash | release_manager.py:25–245 | ROOT 등 가변 전역, Path/os, project_config |
| ZIP | :260–366 | 안전한 tree 검증, member 검증, ZIP metadata·정리 |
| 릴리즈 생성/audit | :436–857 | Runtime 버전 원복, preflight, immutable bundle, ZIP |
| 보관/backup/config | :894–1216 | receipt·backup marker·압축·복원 |
| 이슈 분류·정규화 | :1263–1566 | 형식 처리와 파일 검사·중앙 목록 탐색 혼재 |
| 이슈 이동 트랜잭션 | :1569–1688 | checksum 재검사, 원본 quarantine, 역순 복구 |
| deploy/rollback | :1691–1995 | 위 영역 전체를 조정 |
| issue CLI와 main | :1998–2247 | 단일 호출 표면과 종료 코드 |

`install.py`는 `release_manager`를 import하지 않고 `project_config`를 직접 사용한다. 기존 테스트는 `spec_from_file_location` → `module_from_spec` → `exec_module`로 로드하며 sys.modules 등록을 전제하지 않는다. setUp에서 ROOT/RUNTIME_SOURCE/RUNTIME_DIST/WORKSPACE/RELEASES/ISSUES 및 receipt·legacy 경로 전역을 바꾼다.

patch 표면: `run_release_preflight`, `target_lock`, `prune_runtime_backups`, `archive_backup`, `write_safe_receipt`, `write_json`, `verify_target`, `scoped_git`, `write_issue`, `confirm_issue_move`, `delete_issue_source`, `sha`, `preflight_issue`, `_rollback_issue_moves`; 표준 라이브러리의 `subprocess.run`, `os.link`, `Path.replace/unlink`도 사용한다. 추출 후에도 같은 patch가 같은 실행 경로에 영향을 줘야 한다.

## 확정 모듈 경계

신규 source-only 패키지: `mpa_ops/` (`__init__.py`는 무부작용). 이번 추출은 아래 두 모듈로 한정한다. CLI를 얇게 만들기 위해 모든 함수를 일괄 이동하지 않는다.

| 모듈 | 추출 함수(기존 이름) | 입력·출력 및 의존성 |
|---|---|---|
| `mpa_ops/archive_io.py` | `_zip_runtime`, `_write_backup_archive`, `_zip_entries`, `_validate_zip_member`, `_archive_current_release`, `_extract_runtime` | 기존 Path/str 입력과 반환·예외 보존. 쓰기 함수에는 현재 `assert_safe_runtime_tree` callable과 ignored names를 명시 전달. extract에는 현재 `_validate_zip_member` callable 전달. stdlib 외 의존 없음 |
| `mpa_ops/issue_format.py` | `_parse_issue_candidate`, `_candidate_metadata_is_complete`, `normalize_issue_machine_paths`, `normalize_issue_identity_paths`, `_metadata_identity` | 기존 str/dict/Path 입력, tuple/bool/str/dict 출력 보존. 사용하는 정규식·kind/type marker·identity anchors는 facade의 현재 값을 keyword 인자로 전달. Path의 absolute/resolve 정규화는 현행 유지 |

`release_manager.py`는 동일 이름·시그니처·반환 annotation을 가진 명시적 wrapper를 남긴다. 기존 호출 함수들은 wrapper를 계속 호출한다. wrapper의 공개 시그니처에 새 인자를 추가하지 않고 내부 모듈에만 의존성 인자를 전달한다. 상수는 이번에는 facade에 유지하며 내부에 복제하지 않는다. 내부 함수는 전달된 값과 stdlib만 사용한다.

`_normalized_issue_values`, `render_collected_issue`, `legacy_issue_metadata`, `_issue_identity`는 facade에 유지한다. 이들은 시각 생성·hash·파일 읽기·다른 helper와 결합되므로 leaf 추출과 함께 옮기지 않는다. `materialized_runtime_archive`도 `_extract_runtime` wrapper를 호출한 채 유지한다.

의존 방향: CLI/기존 import → release_manager wrapper/조정 함수 → mpa_ops의 두 leaf 모듈 → stdlib. 내부 모듈의 release_manager 역방향 import, sys.modules 별칭 교체, globals 복사, 동적 함수 재바인딩, 범용 서비스 locator는 금지한다. 모듈 상태를 호출마다 덮어쓰는 방식도 금지한다. 별도 패키지 설치나 PYTHONPATH 설정은 요구하지 않는다.

## 배포·실패 복구 순서 보존

`deploy`와 `rollback`, 이슈 이동 transaction, backup/config 조정, release 생성과 cleanup은 이번에 이동하지 않는다.

deploy 정상 순서: target lock·manifest/dry-run/승인 검증 → 초기 디렉터리·backup/config snapshot → ZIP staging → replacement 검증 → 이전 Runtime 보관·교체·재검증 → config additive migration → issue batch commit → backup 압축·marker·검증 → source receipt·target history 기록 → previous 제거.

deploy 예외 경로: issue moves 복구 → Runtime 복구 → config 복구 → replacement 정리 → deployment receipt 정리 → history 정리 → 생성한 빈 경로 정리 → failure receipt/history 기록 → 원래 오류 또는 recovery incomplete 오류. deploy에서만 각 복구 실패를 수집하고 다음 복구를 계속 시도하는 구조를 보존한다. 내부 replacement 실패의 즉시 Runtime 원복도 유지한다.

rollback 정상 순서: target lock·backup/release/승인 검증 → 필수 경로·config 현재값 확보 → backup marker 검증·archive materialize → replacement copy → 기존 Runtime 보관·교체 → config 복원 → source receipt·target history 기록 → previous 제거. rollback 예외 경로는 현재처럼 previous가 있으면 target을 제거한 뒤 previous를 복원하고, config 복원 오류는 억제하며, 생성 receipt/history·빈 경로를 정리하고 실패 receipt를 최선으로 기록한다. deploy와 달리 rollback은 복구 오류 목록을 수집해 후속 복구를 보장하지 않는다. 이 한계는 이번 리팩터링에서 보존 대상이며 개선하지 않는다.

ZIP 추출의 경로 탈출·중복·symlink·특수파일·손상 검출, 권한 metadata와 실패 staging 정리, Runtime ZIP의 ignored name 제외와 backup ZIP의 전체 보존 차이를 유지한다. 이를 공통 옵션 하나로 합치지 않는다.

## 호환 검증 설계

1. 구현 직전 기준선 commit/대상 hash와 테스트 상태를 다시 확인한다. 달라지면 변경분 의존성만 재조사한다. 정상 기준선이 확보되기 전 추출하지 않는다.
2. 기존 `tests/test_release_manager.py`는 수정하지 않고 그대로 실행한다. 별도 `tests/test_release_manager_compatibility.py`에 일반 import, 기존 spec loader, repo 외 cwd에서 절대경로 CLI 호출, 기존 함수 signature/상수, 전역 경로 변경과 기존 patch 효과를 검증한다.
3. 모든 CLI 하위 명령의 `--help`, 필수 인자 누락(exit 2), 성공(exit 0), 검증 오류(exit 1/stderr)를 전후 대조한다. 실행 부작용이 있는 명령의 정상 동작은 임시 fixture에서만 검사한다. golden 결과에서 시각·UUID·임시 root만 정규화하고 schema/checksum/승인 metadata는 제거하지 않는다.
4. 별도 `tests/test_release_manager_extraction.py`에서 ZIP 결정성·권한·ignored 차이, 악성/손상 ZIP와 정리, 이슈 legacy/JSON/marker 충돌/비후보/경로 alias/identity 안정성을 facade 경유로 검증한다. 정상·실패·경계의 기존 테스트가 이미 덮으면 중복 추가하지 않는다.
5. deploy 실패 주입표: replacement 검증, config 적용, issue batch 중간 이동, backup 압축, marker 검증, source receipt, target history, issue rollback 자체 실패. 각 시점에서 Runtime/config checksum·원본/목적지 issue·backup 및 receipt/history 잔존 상태·lock 해제를 현행과 대조한다. rollback 실패 주입표: backup marker/archive 검증·해제, replacement copy·교체, config 복원, source receipt, target history, previous 복원 자체 실패. rollback에서는 Runtime/config·receipt/history·임시 경로·lock의 실제 관측값을 기존 테스트 이름 또는 새 fixture에 연결한다. config와 history 등 기존 테스트에 빈칸이 있으면 추출 전에 보강한다. rollback의 불완전 복구·config 복원 오류 억제는 숨기지 않고 현행 동작으로 검증 기록에 남긴다.
6. 명령: `python3 -m unittest discover -s tests -p 'test_release_manager*.py'`를 추출 단계마다, 최종에는 `python3 -m unittest discover -s tests`, `python3 release_manager.py sync-runtime`, source/dist 파일집합·내용 비교, `git diff --check`. sync 뒤 source/dist를 읽는 정책 테스트를 다시 실행한다.
7. 1차/2차 독립 구현 검증에서 정책 도달성과 실패 복구 순서를 직접 대조한다. 실제 외부 프로젝트 배포, 새 release 생성, history-cleanup apply는 검증에 사용하지 않는다.

## 중단·복원 기준

기존 테스트 실패·patch 효과 상실·CLI/schema 차이·복구 순서 변화·정책 도달성 누락이면 해당 단위의 다음 추출을 중단한다. 이번 단위의 수정만 되돌리거나 고쳐 다시 검증한다. 전체 checkout reset이나 사용자 파일 삭제는 하지 않는다. 결합을 풀기 위해 사용자 경험/권한/데이터 형식을 바꿔야 하면 설계로 돌아가 변경된 명세만 사용자에게 제시한다.
