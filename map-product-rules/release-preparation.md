# Release Preparation Profile

## Trigger

사용자가 명시적으로 릴리즈를 요청했거나 배포 요청에 현재 source Runtime을 담은 최신 유효 release가 없을 때. Runtime 변경·검증만으로는 실행하지 않는다. `prepare-release`가 UTC `YYYYMMDDHHMMSS-uuid8` 단일 release ID를 생성한다.

## Input

Runtime asset, 검증 명령, compatibility·breaking change·migration·rollback condition·release note. 필요한 경우 `runtime_config.json`의 `schema_version`과 `runtime.*` additive defaults를 선택적으로 입력한다.

## Allowed Actions

`sync-runtime`, validation 실행, 선택적 Runtime config migration 검증, immutable ZIP·manifest·note·release receipt 생성, `release-audit` 실행. ZIP은 임시 Runtime으로 해제해 asset checksum과 핵심 hook의 정적 Python 문법을 확인한다.

## Checks

validation exit code, asset checksum, manifest/package 대응, ZIP 임시 Runtime의 `session_start.py`·`code_gate.py` 정적 문법, Runtime config migration의 additive-only·민감정보·경로 규칙, scoped Git 식별자를 확인한다.

## Gates

필수 metadata와 성공한 validation command 없이는 manifest를 생성하지 않는다. Git은 차단 Gate가 아니라 보조 식별자다.

## Output

불변 release ID와 다음 단일 번들:

```text
workspace/releases/<release-id>/
├── package_<release-id>.zip
├── manifest_<release-id>.json
├── note_<release-id>.md
└── release-receipt_<release-id>.json
```

manifest와 receipt는 기계 검증용이고 note는 사람이 읽는 변경 설명이다. 대상별 배포 receipt/history는 번들 밖 `workspace/receipts/deployments/<target-ref>/`에 둔다.

## Failure State

package·manifest·receipt를 만들지 않고 validation 또는 metadata 오류를 보고한다.

## Prohibited

`workspace/`, `docs/`, agent 설정, 사용자 config 원문, `__pycache__`, `.DS_Store`, symlink를 release 자산에 포함하지 않는다. migration metadata에는 `runtime.*` scalar 기본값만 허용하며 기존 값을 덮어쓰지 않는다.
