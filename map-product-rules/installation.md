# Installation Profile

## Trigger

사용자가 명시한 대상의 최초 설치 또는 installation refresh 요청.

## Input

대상 경로, 사용할 agent, 설치 또는 refresh 의도.

## Allowed Actions

`install.py --dry-run` 뒤 최초 설치를 실행한다. 최초 설치는 없는 명시 project root, `.mpa-workspace/`, `workspace/`, `workspace/issues/`, 루트 `docs/`, `docs/INDEX.md`, `.mpa-project/config.yaml`을 만든다. 기존 `.mpa-project/config.yaml`이 있으면 누락 필드만 추가하고 기존 값·주석·순서는 보존한다. 이미 존재하는 그 밖의 폴더·내용은 변경하지 않는다. Runtime update는 release deployment로만 처리한다. 기존 설치의 agent wiring·agent spec 또는 고유 config 보강이 필요하면 `install.py --installation-refresh --plan <JSON>`을 사용한다.

## Checks

Python 최소 버전, Runtime·workspace template, agent spec, 대상 `.mpa-workspace/` 부재와 변경 범위를 확인한다.

## Gates

dry-run이 통과해야 한다. 기존 설치본은 `install.py --upgrade`로 변경할 수 없다. refresh plan은 schema version, 기존 설치 대상, agent, agent 관리 파일 또는 `.mpa-project/config.yaml`의 비어 있지 않은 allowlist, `workspace/`·`docs/`·`.mpa-project/config.yaml`·일반 소스 preserve 목록, 대상 `.mpa-installation-backups/` 아래 backup, 승인 reference를 모두 가져야 한다. config refresh는 additive-only다.

## Output

신규 Runtime, 초기 workspace 골격, `.mpa-project/config.yaml` 생성/보강 결과, 선택 agent 설정 또는 dry-run 결과.

## Failure State

파일을 변경하지 않고 누락 의존성·충돌 원인을 보고한다.

## Prohibited

Runtime deploy는 refresh를 호출하지 않는다. Runtime deploy/rollback은 `.mpa-project/config.yaml`을 덮어쓰지 않는다. refresh도 기존 `workspace/`, 루트 `docs/`, 일반 소스 및 allowlist 밖의 agent 설정을 변경하지 않으며, config는 누락 필드만 추가한다. invalid/future schema는 경고 후 보존한다.
