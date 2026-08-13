# release_deployment_management TODO

> 이 파일은 실행 순서와 완료 증빙의 원본이다. 항목을 완료로 바꾸려면 **구현 위치·검증 명령·결과**를 해당 항목 바로 아래에 기록한다. 완료된 묶음도 후속 묶음의 전제 조건이 깨지면 다시 미완료로 되돌린다.

## 0. Circled Wiki 장점 흡수: 단일 release key 중심 lineage

- [x] release 산출물을 release-id 단위 immutable bundle로 통합한다.
  - 요구: `workspace/releases/<release-id>/package_<release-id>.zip`, `manifest_<release-id>.json`, `note_<release-id>.md`, `release-receipt_<release-id>.json`을 생성한다.
  - 보존: JSON manifest/receipt는 기계 검증용으로 유지하고 note는 사람용 설명으로 둔다. deployment receipt는 대상별 경로에 분리한다.
  - 검증: bundle 폴더명·파일명·manifest ID·ZIP 내부 `.mpa-version`이 일치하고, 압축 해제 후 asset map이 manifest와 일치한다.

- [x] 단일 release ID를 release의 primary identity로 만든다.
  - 완료: `prepare-release`가 UTC `YYYYMMDDHHMMSS-uuid8`을 생성해 `.mpa-version`의 `current_release`, manifest, release receipt, deployment dry-run, target history, rollback receipt, backup 이름에 같은 값으로 기록한다.
  - 금지: `runtime_version`/`current_version` 또는 asset hash/Git revision을 별도 사용자용 version으로 만들지 않는다.
  - 구현/검증: `release_manager.py`의 `new_release_id()`, `set_current_release()`, `prepare_release()`; `test_release_id_is_the_only_runtime_identity_and_checksum_is_evidence` 통과.
- [x] immutable release와 checksum의 역할을 분리한다.
  - 완료: asset map/checksum은 package·대상 Runtime 무결성 검증에만 쓰고, 릴리스의 표시·전환·backup 식별에는 `release_id` 하나만 쓴다.
  - 검증: manifest·receipt·package의 ID가 불일치하거나 checksum/asset map이 달라지면 실패한다.
  - 구현/검증: schema 4 `load_manifest()`·`release_package()`와 `release-audit`; `20260812090303-ee377e06` release audit 통과.
- [x] Git 없는 source snapshot을 manifest에 남긴다.
  - 완료: allowlist path/asset checksum, validation 결과, compatibility, migration, issue 참조를 source snapshot으로 기록한다. Git 정보가 있으면 보조 필드에만 기록하고, 없거나 dirty여도 release가 계속된다.
  - 검증: `test_release_allows_scoped_dirty_or_no_git_source` 통과.
- [x] versioned release의 legacy migration과 audit을 보완한다.
  - 완료: 기존 분리-version 또는 hash-only artifact는 legacy로 분리하고, active audit은 release ID↔manifest↔receipt↔package의 일대일성과 checksum 무결성을 검증한다.
  - 구현/검증: 새 bundle 외 기존 active 경로는 `workspace/releases/legacy/migrated/<YYYYMMDD>/` 및 `workspace/receipts/legacy/migrations/<YYYYMMDD>/`로 분리; `release-audit`는 bundle inventory와 ZIP 압축 해제 asset map까지 검증한다.

## 1. Release artifact 정합성

- [x] Inventory와 migration schema를 정의한다.
  - 입력: active/legacy manifest·package·release receipt.
  - 완료: active/legacy 구분, migration receipt의 이전 경로·사유·시각·검증자 필드가 문서화된다.
  - 구현: active는 `workspace/releases/<release-id>/` bundle, legacy는 `workspace/releases/legacy/migrated/`·`workspace/receipts/legacy/migrations/`로 분리.
  - 검증: `mpa-097ec1de67e0e55c-schema-v2.json` receipt가 legacy manifest/package/receipt 경로, 사유, migrated_at, verified_by를 기록.
- [x] Active release audit을 구현한다.
  - 완료: schema version, metadata, asset map, package, validation result, release receipt의 상호 참조를 검사한다.
  - 구현: `release_manager.py`의 `load_manifest()`, `release_package()`, `audit_releases()`.
  - 검증: `python3 release_manager.py release-audit` → `release audit passed: 2 release bundle(s)`; `test_release_audit_verifies_zip_and_bundle_inventory` 통과.
  - 독립 감사 보완: manifest 없는 active package/receipt도 거부하도록 inventory 대조를 추가했고 `test_audit_rejects_orphan_active_package_or_receipt` 통과.
- [x] 과거 artifact를 legacy로 이관한다.
  - 완료: metadata 없는 artifact는 active에 남지 않고 migration receipt로 추적된다.
  - 구현: `workspace/releases/legacy/migrated/20260813/`, `workspace/receipts/legacy/migrations/20260813/` (기존 legacy 이력은 `20260812/`에 유지).
  - 검증: active manifest에 schema v2 artifact만 남긴 뒤 `release-audit` 통과.
- [x] release 실패 경로를 테스트한다.
  - 완료: argv timeout·실패·metadata/package 누락 시 active package/manifest/release receipt가 생성되거나 변경되지 않는다.
  - 검증: `test_timeout_and_manifest_write_failure_leave_no_release_artifacts`, `test_failed_validation_creates_no_release_artifacts`, `test_empty_metadata_creates_nothing_and_audit_rejects_missing_package` 통과.

## 2. Deployment 상태와 보존

- [x] deployment를 `from_release → to_release` 전환으로 기록·검증한다.
  - 완료: dry-run, apply, failure, rollback의 receipt/history에 이전·신규 release ID만 남는다.
  - 검증: target Runtime release 또는 history가 dry-run 뒤 바뀌면 apply 전에 거부한다.
  - 구현/검증: `deployment_dry_run()`, `deploy()`, `rollback()`; `test_deploy_legacy_current_version_records_a_single_legacy_origin`, `test_deploy_revalidates_target_receipt_and_approval` 통과.
- [x] Runtime update에 issue 수집·원본 정리 단계를 결합한다.
  - 완료: dry-run이 대상 `workspace/issues/`의 수집 후보 key·상대 경로·checksum을 기록하고 사용자에게 고지하며, apply가 inventory 불일치를 거부한다.
  - 완료: Runtime 검증 성공 후 issue를 source `workspace/issues/inbox/<project-ref>/`로 자동 원자 이동하고, 중앙 수집 receipt가 확정된 뒤에만 대상 원본을 삭제한다.
  - 완료: apply 결과가 수집 목록·원본 정리 결과 또는 no-op/실패·보류 사유를 사용자에게 고지한다.
  - 보존: issue가 없으면 no-op이다. 수집 실패·보류·receipt 실패·inventory 변경이면 대상 원본을 보존하고 update를 완료로 표시하지 않는다.
  - 검증: 성공 수집은 중앙 inbox만 남고 대상 원본이 사라지며, 각 실패 경로는 대상 원본을 유지하는 테스트를 추가한다.

- [x] Runtime update transaction과 recovery를 보강한다.
  - 요구: Runtime 교체·issue 이동·collection receipt·deployment receipt/history 기록을 하나의 복구 가능한 상태 전이로 처리한다.
  - 보존: 후속 기록 실패 시 Runtime과 issue 원본을 함께 복구하고, 실패 receipt에 recovery 결과를 남긴다.
  - 검증: collection 이후 deployment receipt 실패 시 Runtime·issue 원본 복구, 실패 receipt/history 기록을 `test_deploy_collection_failure_restores_runtime_and_issue`와 `test_failed_deploy_restores_runtime_and_records_failed_state`로 확인했다.

- [x] Dry-run receipt에 target 절대 경로, asset map, history 상태, release receipt, 생성·만료 시각을 기록한다.
  - 구현: `release_manager.py`의 `deployment_dry_run()`.
  - 검증: `test_deploy_uses_immutable_package_not_current_dist`, `test_deploy_rejects_repeated_release_history` 통과.
- [x] Apply 전 재검증을 구현한다.
  - 완료: 만료, target map/history 변경, release receipt 불일치, 승인·rollback owner 누락은 모두 apply 전에 거부된다.
  - 구현/검증: `deploy()`의 dry-run target/asset/history/receipt/expiry/approval 검증; `test_deploy_revalidates_target_receipt_and_approval` 통과.
- [x] 상태 전이와 rollback evidence를 구현한다.
  - 완료: deployment receipt와 target history가 `applied`/`rolled_back`/`failed`, backup, verification 결과를 같은 release에 대해 기록한다.
  - 구현: `deploy()`의 `applied`/`failed` receipt/history, `rollback()`의 `rolled_back` receipt/history 및 원자 교체 복구.
  - 검증: `test_deploy_and_rollback_preserve_user_owned_paths`, `test_failed_deploy_restores_runtime_and_records_failed_state` 통과.
- [x] Runtime backup 보존 개수를 최신 3개로 제한한다.
  - 완료: 성공 deploy의 receipt/history 기록 뒤에만 `.mpa-backups/`의 Runtime backup 디렉터리를 수정 시각 순으로 정리하며, 실패 deploy와 일반 파일은 보존한다.
  - 구현/검증: `prune_runtime_backups()`; `test_runtime_backup_retention_keeps_the_newest_three_directories_only` 통과.

- [x] Runtime backup marker와 동시 실행 보호를 추가한다.
  - 요구: 성공 marker가 있는 Runtime backup만 최신 3개 정리 대상이며, 사용자 디렉터리·실패 백업은 보존한다. target별 deploy/rollback lock을 사용한다.
  - 구현: `backup-metadata.json` 성공 marker와 target별 `.mpa-deploy.lock`; marker 없는 snapshot은 retention/rollback 대상이 아니다.
  - 검증: `test_runtime_backup_retention_keeps_the_newest_three_directories_only`, `test_manual_backup_directory_is_not_pruned_or_accepted_for_rollback` 통과.
- [x] 보존 end-to-end 테스트를 추가한다.
  - 완료: deploy/rollback 뒤 `workspace`, `docs`, agent 설정, 일반 소스가 바뀌지 않음을 확인한다.
  - 검증: `test_deploy_and_rollback_preserve_user_owned_paths`가 workspace·docs·AGENTS.md·main.py 보존을 확인.

## 3. Installation 계약

- [x] 설치 고유 설정의 additive-only 계약을 구현한다.
  - 요구: `.mpa-project/config.yaml`이 없으면 `schema_version`, 프로젝트명, 초기화 시각, 절대 `root_path`를 생성한다.
  - 보존: 파일이 있으면 schema registry의 누락 필드만 추가하고 기존 값·주석·순서·사용자 지정 빈 값을 변경하지 않는다. invalid/future schema는 경고 후 파일을 보존한다.
  - 보안: 절대 경로는 대상 로컬 config에만 두고 release asset·manifest checksum·issue·중앙 receipt로 복사하지 않는다.
  - 구현: `project_config.py`의 schema 1 기본값, 원자적 생성/보강, 기존 값·주석 보존, invalid/future schema warn-only, semantic checksum/audit.
  - 검증: `test_new_install_creates_root_docs_but_not_workspace_docs`, `test_existing_project_config_only_adds_missing_fields_and_preserves_content`, `test_missing_schema_is_added_but_future_schema_is_preserved`, `test_config_audit_warns_on_moved_root_without_exposing_absolute_path` 통과.

- [x] 고유 설정 audit와 최초 설치 계약을 연결한다.
  - 완료: dry-run은 config 생성/추가 예정 필드와 preserve 범위를 고지하고, 최초 설치 이후에도 기존 config 값은 Runtime 프로젝트가 소유하며 명시된 `runtime.*` 누락값만 migration한다.
  - 완료: `config-audit`가 schema·필수 필드·경로 안전성·민감정보·semantic checksum을 검사하되 기본은 warn-only다.
  - 구현: `install.py` dry-run/initial install에 config 계획과 additive 보강을 연결하고 `project_config.py audit` CLI를 추가. command-contract·installation profile·README/install·guidebook을 갱신.
  - 검증: `test_invalid_schema_is_preserved_without_duplicate_schema_key`, `test_deploy_and_rollback_preserve_user_owned_paths`, `test_new_install_applies_runtime_config_defaults_and_project_references`, 전체 테스트 49건 통과.

- [x] Runtime 프로젝트 refresh 절차를 제거하고 release-bound config migration으로 대체한다.
  - 요구/완료: 별도 refresh plan·backup·receipt는 만들지 않는다. 필요한 Runtime 초기값은 `prepare-release --runtime-config-json`의 `runtime.*` additive migration으로 선언하고, deploy transaction에서 `${project.*}` 참조를 대상 local config 값으로 해석해 누락값만 추가한다.
  - 검증: 기존 값 보존, `runtime-config/config.yaml` snapshot 생성, Runtime과 config 동시 rollback을 `test_runtime_config_migration_is_additive_and_rolled_back_with_runtime`로 확인했다.

- [x] Runtime version config migration의 백업·복구 경계를 구현한다.
  - 요구: migration이 있는 deploy는 `.mpa-workspace`와 `.mpa-project/config.yaml`을 함께 backup하고 rollback/실패 시 함께 복원한다. 사용자 소유 config 값·agent 설정·workspace·docs·일반 소스는 변경하지 않는다.
  - 구현: `project_config.py` additive scalar merge/참조 해석, `release_manager.py` manifest `runtime_config`, dry-run checksum 재검증, `.mpa-backups/<id>/runtime/` 및 `runtime-config/`, marker schema 2.
  - 검증: 전체 49개 테스트 통과, migration manifest/receipt 정합성 및 legacy backup 호환 경로 확인.

- [x] issue identity·민감정보·receipt 경계를 보강한다.
  - 요구: 생성 시 sensitivity scan, stable source/workspace issue ID와 occurrence를 기록하고 중앙 receipt에서 대상 절대 경로를 제거한다.
  - 구현: `source_issue_id`·`workspace_issue_id`·`canonical_issue_key` 안정 identity, 생성/수집 sensitivity scan, 중앙 receipt의 project fingerprint, resolve/archive의 bundle·applied deployment 재검증.
  - 검증: `test_create_issue_rejects_sensitive_content_before_writing`, `test_collection_receipt_uses_project_fingerprint_not_absolute_path`, lifecycle/evidence 테스트 통과.

- [x] `docs/INDEX.md`를 agent 관리 색인으로 보장한다.
  - 완료: 최초 설치와 Runtime update는 root `docs/`가 없으면 만들고, `docs/INDEX.md`가 없을 때만 색인 템플릿을 생성한다.
  - 보존: 기존 `docs/INDEX.md`와 일반 문서는 설치·배포·rollback이 덮어쓰거나 삭제하지 않는다.
  - 검증: `test_new_install_creates_root_docs_but_not_workspace_docs`, `test_deploy_creates_only_missing_workspace_and_docs_roots`에서 신규 생성과 기존 문서 루트 보존을 확인하고, Runtime 규칙에 문서 산출물 후 INDEX 갱신 절차를 반영했다.

- [x] `install.py --dry-run`을 구조화된 설치 계획으로 출력한다.
  - 완료: 대상, 생성 파일, preserve 목록, dependency·agent 결과, 실패 이유가 machine-readable 출력에 있다.
  - 구현: `install.py`의 `--dry-run --json` plan.
  - 검증: `test_dry_run_json_describes_changes_and_preserves_target` 통과.
- [x] agent spec와 생성 hook command의 smoke 검증을 추가한다.
  - 검증: `test_codex_hook_commands_and_scripts_smoke`가 Codex hook command의 Runtime 경로와 `session_start.py`·`code_gate.py`·`turn_end.py --help` 실행을 확인.
- [x] 기존 설치 보호 테스트를 추가한다.
  - 완료: 기존 `.mpa-workspace`, `workspace`, `docs`, agent 설정은 install 실패·dry-run 모두에서 변경되지 않는다.
  - 검증: `test_existing_install_rejection_preserves_workspace_docs_and_agent_settings`와 고유 config 보존 테스트가 기존 `.mpa-workspace`·workspace·docs·agent 설정·config 값을 보존하는 것을 확인.
## 4. Issue lifecycle

- [x] canonical issue schema를 적용한다.
  - 완료: key, occurrence, area, observed release, collection purpose, user review reference를 기록한다.
  - 구현: `release_manager.py`의 `issue_text()`, `read_issue()`, `review_issue()`.
  - 검증: `test_issue_requires_review_and_keeps_needs_information_in_inbox`, `test_issue_receipt_failure_restores_issue_and_rejected_review_blocks_triage` 통과.
- [x] 원자 collect와 receipt rollback을 구현·테스트한다.
  - 완료: 같은 파일시스템과 cross-filesystem 이동 모두에서 receipt 실패 시 source 보존과 destination 원복을 확인한다.
  - 구현: `move_issue_atomically()`의 EXDEV 임시 파일·fsync·원본 보존, `collect_issue()`의 receipt 실패 원복.
  - 검증: `test_cross_filesystem_move_keeps_source_when_unlink_fails`, `test_collect_receipt_failure_returns_issue_to_project` 통과.
  - 독립 감사 보완: `../` issue path escape를 거부하도록 project issue root 경계를 확인했고 `test_collection_rejects_project_issue_path_escape` 통과.
- [x] 정상 lifecycle을 테스트한다.
  - 완료: create → collect → review → triage → resolve → archive가 evidence reference와 함께 성공한다.
  - 검증: `test_issue_full_lifecycle_links_release_and_deployment_evidence`가 실제 immutable release와 deploy receipt를 resolve/archive evidence로 연결해 통과.
- [x] 실패 lifecycle을 테스트한다.
  - 완료: rejected, needs_information/undetermined, duplicate archive, release/deployment/verification 불일치가 inbox·원본을 보존한다.
  - 검증: `test_issue_receipt_failure_restores_issue_and_rejected_review_blocks_triage`, `test_issue_requires_review_and_keeps_needs_information_in_inbox`, `test_duplicate_archive_blocks_collection_and_preserves_project_issue`, `test_archive_rejects_deployment_evidence_for_another_release` 통과.

## 5. Profile·문서·완료 증빙

- [x] CLI/profile 계약표를 만든다.
  - 완료: 각 CLI 명령의 Trigger, Input, Checks, Gates, Output, Failure State, Prohibited가 profile과 일치한다.
  - 구현: `map-product-rules/command-contract.md`에 install/release/deploy/rollback/issue 명령별 계약을 정리하고 각 profile과 대조.
- [x] 사용자 문서를 갱신한다.
  - 완료: README, install.md, guidebook이 최초 설치·release·dry-run·deploy·rollback·issue 흐름과 비범위(Git Gate 없음, docs 미배포)를 설명한다.
  - 구현: `README.md`, `install.md`, `guidebook/guidebook.md`에 설치·배포 계약·rollback 승인 입력·root docs 비배포를 반영.
- [x] Git 비차단성을 테스트한다.
  - 완료: scoped dirty와 No-Git 모두 release를 막지 않으며 receipt에는 가능한 식별 정보만 남는다.
  - 검증: `test_release_allows_scoped_dirty_or_no_git_source` 통과. scoped diff는 manifest `source_git`에 남고, temp No-Git source도 `unavailable` metadata로 release 준비를 계속한다.
- [x] 종료 검증을 실행한다.
  - 완료: source/dist sync, release audit, 전체 테스트, `git diff --check` 결과를 기록한다.
  - 검증: `python3 release_manager.py release-audit` → `release audit passed: 2 release bundle(s)`, `PYTHONPYCACHEPREFIX=/private/tmp/mpa-pycache python3 -m unittest discover -s tests -q` → 49 tests OK, `git diff --check` → 성공.
- [x] Definition of Done을 증빙에 연결한다.
  - 완료: plan.md의 각 완료 기준에 테스트 또는 명령 결과가 연결된 뒤 사용자 검토를 요청한다.
  - 증빙 연결: Release는 `test_timeout_and_manifest_write_failure_leave_no_release_artifacts`·`release-audit`; Deployment는 `test_deploy_and_rollback_preserve_user_owned_paths`·`test_failed_deploy_restores_runtime_and_records_failed_state`; Installation은 `tests/test_install.py` 설치·config·hook 테스트; Issue는 lifecycle/실패 lifecycle tests; 운영 정합성은 command contract·sync/audit/test/diff 출력.

## 독립 감사 반영 기록

- 2026-08-12: 독립 감사에서 receipt 실패 원복, rollback 상태 이력, 설치 구성 갱신 부재를 지적했다. 당시 별도 갱신 CLI·보존 테스트·rollback 상태 기록·deploy failed 상태·cross-filesystem issue 이동·release manifest write 실패 원복을 보완했으나, 이후 Runtime 프로젝트 자체 관리 원칙에 따라 별도 갱신 절차를 제거했다.
- 2026-08-12 (해소): deploy/rollback이 Runtime 교체 뒤 receipt 또는 target history 기록에 실패할 경우 적용 상태와 기록 상태가 모순되지 않도록 transaction/복구를 강화했다.
- 2026-08-13: release bundle ZIP·manifest·note·release-receipt 통합, ZIP 안전 해제, backup marker·target lock, issue identity/sensitivity/privacy 경계를 추가하고 전체 49개 테스트와 실제 release audit을 통과했다.
- 2026-08-13: Runtime 프로젝트 설정은 프로젝트 자체가 소유하되, 별도 refresh 없이 release-bound `runtime.*` additive migration만 허용하도록 보완했다. migration deploy는 `.mpa-workspace`와 MPA config snapshot을 함께 백업·복원하고 사용자 값을 보존한다.

## 사용자 확인·결정·수동 실행 (마지막 섹션)

- [x] 실제 대상 프로젝트에서 신규 설치 dry-run과 설치를 실행한다.
  - 확인: 선택한 agent의 실제 hook 설정이 실행되고, 사용자 기존 파일을 보존하는지 확인한다.
  - 2026-08-12 부분 확인: `/Users/kjkim/Temp/mpa-test`에 Codex Runtime·AGENTS.md·agent spec·3개 hook이 설치됐고 SessionStart command는 exit 0으로 실행됐다. 다만 과거 template의 `workspace/docs/`가 생성됐고, 당시 정책상 필요했던 루트 `docs/`는 없었다.
  - 보완 및 재확인: 신규 install/update는 없는 `workspace/`·루트 `docs/`만 빈 폴더로 만들고, 이미 존재하는 내용은 건드리지 않도록 변경했다. `test_new_install_creates_root_docs_but_not_workspace_docs`, `test_deploy_creates_only_missing_workspace_and_docs_roots` 통과. `mpa-test`는 upgrade 과정에서 root `docs/`가 생성됐고 기존 사용자 문서·AGENTS.md·hook 설정은 보존됐다.
- [ ] 실제 대상 프로젝트에 승인된 Runtime release를 dry-run → deploy → rollback으로 적용한다.
  - 이전 부분 확인: `mpa-9326fb5686135269`을 `/Users/kjkim/Temp/mpa-test`에 dry-run → deploy 했다. 이는 이전 형식 검증이므로, 단일 release key 구현 뒤 `from_release → to_release`과 rollback을 다시 검증한다.
  - 확인: `AGENTS.md`/agent spec/hook 설정 중 자동 갱신을 허용할 경로를 확정한다.
- [ ] 설치된 운영 프로젝트의 고유 설정 동작을 사용자 환경에서 확인한다.
  - 확인: config가 없을 때 프로젝트명·초기화 시각·절대 경로가 생성되는지, 기존 config가 있을 때 기존 내용은 유지되고 누락 필드만 추가되는지 확인한다.
  - 확인: 프로젝트 이동·잘못된 schema·민감정보 후보가 경고로 안내되고, config의 절대 경로가 release/issue/중앙 receipt로 유출되지 않는지 확인한다.
  - 추가 확인: `runtime.*` migration에서 `${project.name}`·`${project.root_path}`가 대상 local 값으로 해석되고, 기존 값은 유지되며 rollback 후 원문이 복원되는지 확인한다.
