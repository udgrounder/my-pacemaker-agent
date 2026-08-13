# Deployment Coordination Profile

## Trigger

승인된 Runtime release를 명시된 대상에 적용하거나 rollback할 때.

## Input

manifest, target, target-ref, recorded dry-run, 승인자·승인 기록·rollback 책임자.

## Allowed Actions

dry-run, `.mpa-workspace` backup·교체·검증, target history와 deployment/rollback receipt 기록. 성공한 deploy 뒤에는 대상 `.mpa-backups/`의 Runtime backup 디렉터리를 최신 3개만 유지한다.

## Checks

dry-run의 release·target·target-ref와 실제 apply 입력, package checksum, 대상 asset map을 비교한다.

## Gates

dry-run·승인·rollback 책임자 없이는 apply하지 않는다. rollback 원본은 대상 `.mpa-backups/` 아래만 허용한다. retention은 성공 receipt/history가 기록된 후에만 수행하며, 실패한 deploy에서는 기존 backup을 정리하지 않는다.

## Output

deployment 또는 rollback receipt와 대상 history.

## Failure State

기존 Runtime을 복원하고 rollback 실패도 receipt로 남긴다.

## Prohibited

`.mpa-workspace/`가 존재하는 대상에서만 Runtime을 교체한다. `workspace/`, `workspace/issues/`, 루트 `docs/`와 없는 `docs/INDEX.md`만 생성할 수 있으며, 이미 존재하는 폴더·내용·agent 설정·일반 소스는 읽거나 변경하지 않는다. 업데이트 issue batch는 dry-run 후보 고지와 Runtime 검증 성공 뒤에만 원자 수집하고, 원본 정리 결과를 사용자에게 고지한다.
