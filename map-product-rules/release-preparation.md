# Release Preparation Profile

## Trigger

사용자가 명시적으로 릴리즈를 요청했거나 배포 요청에 현재 source Runtime을 담은 최신 유효 release가 없을 때. Runtime 변경·검증만으로는 실행하지 않는다. 직전 유효 release와 `.mpa-version`을 제외한 Runtime asset이 같으면 기본적으로 생성하지 않으며, 의도적인 재발행만 `--allow-version-only`로 명시한다. `prepare-release`가 UTC `YYYYMMDDHHMMSS-uuid8` 단일 release ID를 생성한다.

## Input

Runtime asset, 검증 명령, compatibility·breaking change·migration·rollback condition·release note. 필요한 경우 `runtime_config.json`의 `schema_version`과 `runtime.*` additive defaults를 선택적으로 입력한다.

## Allowed Actions

`sync-runtime` 뒤 표준 preflight(전체 단위 테스트, source/runtime-dist parity, 기존 release audit)와 사용자가 제공한 추가 validation을 실행하고, 선택적 Runtime config migration을 검증한 뒤 immutable ZIP·manifest·note·release receipt를 생성한다. ZIP은 임시 Runtime으로 해제해 asset checksum, 모든 Python hook의 정적 문법, retired 실행 경로와 민감한 절대 경로 노출을 확인한다.

## Checks

표준 preflight와 추가 validation의 exit code, 직전 유효 release 대비 `.mpa-version` 외 Runtime asset 변경, asset checksum, manifest/package 대응, ZIP 임시 Runtime의 모든 Python hook 정적 문법, active source/package의 retired `.mpa-workspace` 실행 참조, manifest·receipt·validation 기록의 credential·machine absolute path, Runtime config migration의 additive-only 규칙, scoped Git 식별자를 확인한다.

## Gates

필수 metadata, 성공한 표준 preflight, 성공한 추가 validation command, 그리고 `.mpa-version` 외 Runtime asset 변경 없이는 manifest를 생성하지 않는다. version-only 재발행은 `--allow-version-only`를 명시해야 한다. Git은 차단 Gate가 아니라 보조 식별자다.

## Output

불변 release ID와 다음 단일 번들:

```text
workspace/releases/<release-id>/
├── package_<release-id>.zip
├── manifest_<release-id>.json
├── note_<release-id>.md
└── release-receipt_<release-id>.json
```

manifest와 receipt는 기계 검증용이고 note는 사람이 읽는 변경 설명이다. 대상별 배포 receipt는 Git 비추적 `workspace/.local/receipts/deployments/<target-ref>/`에, 대상 Runtime history는 대상 `.mpa/runtime/history/`에 둔다.

## Failure State

package·manifest·receipt를 만들지 않고 validation·metadata·version-only release 오류를 보고한다. version-only 거부 뒤에는 source와 dist Runtime version을 원래 상태로 되돌린다.

## Prohibited

`workspace/`, `docs/`, agent 설정, 사용자 config 원문, `__pycache__`, `.DS_Store`, symlink를 release 자산에 포함하지 않는다. migration metadata에는 `runtime.*` scalar 기본값만 허용하며 기존 값을 덮어쓰지 않는다.
