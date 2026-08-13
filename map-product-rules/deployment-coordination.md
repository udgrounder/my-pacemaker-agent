# Deployment Coordination Profile

## Trigger

승인된 Runtime release를 명시된 대상에 적용하거나 rollback할 때.

## Input

manifest, target, target-ref, recorded dry-run, 승인자·승인 기록·rollback 책임자.

## Allowed Actions

dry-run, release ZIP의 안전한 임시 해제, 배포 전 `.mpa-workspace`와 예정된 MPA `runtime.*` 설정 snapshot backup, Runtime 교체·검증·설정 additive migration, target history와 deployment/rollback receipt 기록. 성공한 deploy 뒤에는 대상 `.mpa-backups/`의 성공 marker가 있는 Runtime backup 디렉터리만 최신 3개 유지한다. marker 없는 사용자 snapshot은 건드리지 않는다.

## Backup Purpose

Runtime release의 ZIP은 배포 기준이자 릴리즈 이력·감사용 불변 원본이다. deploy가 만드는 `.mpa-backups/<release-id>-<timestamp>-<attempt-id>/` 디렉터리는 `runtime/.mpa-workspace/`와 `runtime-config/config.yaml`(migration이 있을 때)을 보존하는 운영 snapshot이며 release archive를 대신하지 않는다. config snapshot은 rollback 원문 복원을 위한 local copy일 뿐 MPA가 사용자 값을 해석·수정한다는 뜻이 아니다. Runtime 프로젝트의 사용자 설정 변경과 전체 프로젝트 백업은 Runtime 프로젝트 자체의 버전 관리·백업 절차로 처리한다.

## Checks

dry-run의 release·target·target-ref와 실제 apply 입력, package checksum, 대상 asset map, config checksum 및 migration 후보를 비교한다.

## Gates

dry-run·승인·rollback 책임자 없이는 apply하지 않는다. rollback 원본은 대상 `.mpa-backups/` 아래만 허용한다. retention은 성공 receipt/history가 기록된 후에만 수행하며, 실패한 deploy에서는 기존 backup을 정리하지 않는다.

## Output

deployment 또는 rollback receipt와 대상 history.

## Failure State

기존 Runtime과 자동 수집된 issue 원본을 함께 복원하고, 실패·복구 결과를 receipt/history에 남긴다. 대상별 동시 deploy/rollback은 lock으로 중복 실행을 막고, lock 자체는 운영 파일로 보존한다.

## Prohibited

`.mpa-workspace/`가 존재하는 대상에서만 Runtime을 교체한다. `workspace/`, `workspace/issues/`, 루트 `docs/`와 없는 `docs/INDEX.md`만 생성할 수 있으며, 이미 존재하는 폴더·내용·agent 설정·일반 소스는 읽거나 변경하지 않는다. `runtime.*` migration은 누락값만 추가하고 사용자 값을 덮어쓰지 않는다. 업데이트 issue batch는 dry-run 후보 고지와 Runtime 검증 성공 뒤에만 원자 수집하고, 원본 정리 결과를 사용자에게 고지한다.
