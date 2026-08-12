# Release Preparation Profile

## Trigger

검증된 Runtime 변경을 배포 가능한 release로 준비할 때. `prepare-release`가 UTC `YYYYMMDDHHMMSS-uuid8` 단일 release ID를 생성한다.

## Input

Runtime asset, 검증 명령, compatibility·breaking change·migration·rollback condition·release note.

## Allowed Actions

`sync-runtime`, validation 실행, immutable package·manifest·receipt 생성, `release-audit` 실행.

## Checks

validation exit code, asset checksum, manifest/package 대응, scoped Git 식별자를 확인한다.

## Gates

필수 metadata와 성공한 validation command 없이는 manifest를 생성하지 않는다. Git은 차단 Gate가 아니라 보조 식별자다.

## Output

불변 release ID, package, manifest, release receipt.

## Failure State

package·manifest·receipt를 만들지 않고 validation 또는 metadata 오류를 보고한다.

## Prohibited

`workspace/`, `docs/`, agent 설정, `__pycache__`, `.DS_Store`, symlink를 release 자산에 포함하지 않는다.
