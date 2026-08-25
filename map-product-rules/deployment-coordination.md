# Deployment Coordination Profile

## Trigger

승인된 Runtime release를 명시된 대상에 적용하거나 rollback할 때.

## Input

manifest, target, target-ref, recorded dry-run, 승인자·승인 기록·rollback 책임자.

## Allowed Actions

dry-run, release ZIP의 안전한 임시 해제, 배포 전 `.mpa/runtime`와 예정된 MPA `runtime.*` 설정 snapshot backup, Runtime 교체·검증·설정 additive migration, target history와 deployment/rollback receipt 기록. 성공한 deploy 뒤에는 version backup 내부의 `runtime/`만 `runtime.zip`으로 압축·검증한 뒤 원본을 삭제한다. 일반 deploy/rollback은 과거 release·history·receipt·backup을 정리하지 않으며, marker 없는 사용자 snapshot은 언제나 건드리지 않는다.

## Backup Purpose

Runtime release의 ZIP은 배포 기준이자 릴리즈 이력·감사용 불변 원본이다. deploy는 `.mpa/backups/<release-id>-<timestamp>-<attempt-id>/` 디렉터리에 `runtime/.mpa/runtime/`와 `runtime-config/config.yaml`(migration이 있을 때)을 먼저 보존해 배포 실패를 복구하고, 성공 검증 뒤 같은 version 디렉터리의 `runtime.zip`만 남긴다. `backup-metadata.json`의 `archive_migration`은 archive 경로·성공 또는 실패 시각·원본 `runtime/` 삭제 여부·실패 원인을 해당 backup의 전환 receipt로 기록한다. config snapshot은 rollback 원문 복원을 위한 local copy일 뿐 MPA가 사용자 값을 해석·수정한다는 뜻이 아니다. rollback은 version backup의 marker와 `runtime.zip`을 검증·안전 해제한 뒤에만 Runtime 교체를 시작한다. Runtime 프로젝트의 사용자 설정 변경과 전체 프로젝트 백업은 Runtime 프로젝트 자체의 버전 관리·백업 절차로 처리한다.

## Checks

dry-run의 release·target fingerprint·target-ref와 실제 apply 입력, package checksum, 대상 asset map, config checksum 및 migration 후보를 비교한다. dry-run은 Git 비추적 `workspace/.local/deployment-targets/<target-ref>.json`에만 절대경로·fingerprint를 기록한다. 대상 절대경로와 사용자 입력에 포함된 credential·machine path는 deployment/rollback receipt와 대상 history에 저장하지 않는다. rollback에서 `--target`을 생략하면 이 로컬 등록부를 사용하며, 없거나 fingerprint가 달라지면 중단한다. 대상은 `.mpa/runtime/`이 있는 현재 설치 구조여야 하며, 자동 구조 변환은 수행하지 않는다.

## Gates

dry-run·승인·rollback 책임자 없이는 apply하지 않는다. 이 정보가 아직 없으면 agent는 apply/rollback 명령을 호출해 오류를 내는 대신 dry-run 또는 rollback 후보·영향을 제시하고 사용자에게 승인을 요청한다. 승인 뒤에만 승인 기록과 책임자를 입력해 실행한다. rollback 원본은 대상 `.mpa/backups/` 아래만 허용한다. 이력 정리는 사용자 명시 요청의 `history-cleanup`에서만 수행한다. 이 명령은 먼저 전체 후보를 읽기 전용으로 제시하고, 승인 정보와 `--apply` 뒤에만 release·대상 history/receipt 및 검증된 성공 ZIP backup을 삭제한다. 실패 backup·marker 없는 사용자 snapshot·등록부 불일치 대상은 보존한다.

## Output

Git 비추적 `workspace/.local/receipts/deployments/<target-ref>/`의 deployment 또는 rollback receipt와 대상 history.

## Failure State

기존 Runtime과 자동 수집된 issue 원본을 함께 복원하고, 실패·복구 결과를 receipt/history에 남긴다. 대상별 동시 deploy/rollback은 lock으로 중복 실행을 막고, lock 자체는 운영 파일로 보존한다.

## Prohibited

`.mpa/runtime/`가 존재하는 대상에서만 Runtime을 교체한다. `workspace/`, `workspace/issues/`, 루트 `docs/`와 없는 `docs/INDEX.md`만 생성할 수 있으며, 이미 존재하는 폴더·내용·agent 설정·일반 소스는 읽거나 변경하지 않는다. `runtime.*` migration은 누락값만 추가하고 사용자 값을 덮어쓰지 않는다. 업데이트 issue batch는 dry-run 후보 고지와 Runtime 검증 성공 뒤에만 원자 수집하고, 원본 정리 결과를 사용자에게 고지한다.
