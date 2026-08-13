# Installation Profile

## Trigger

사용자가 명시한 MPA Runtime 프로젝트의 최초 설치 요청.

## Input

대상 경로와 사용할 agent.

## Allowed Actions

`install.py --dry-run` 뒤 최초 설치를 실행한다. 최초 설치는 없는 명시 project root, `.mpa-workspace/`, `workspace/`, `workspace/issues/`, 루트 `docs/`, `docs/INDEX.md`, `.mpa-project/config.yaml`을 만든다. 필요하면 `--runtime-config-json`으로 초기 `runtime.*` additive defaults를 제공할 수 있으며 `${project.*}` 참조는 대상 config 값으로 해석한다. 기존 `.mpa-project/config.yaml`이 있으면 누락 필드만 추가하고 기존 값·주석·순서는 보존한다. 릴리즈 업데이트의 같은 기능은 `release_manager.py deploy`가 수행한다. 이미 존재하는 그 밖의 폴더·내용은 변경하지 않는다. Runtime update는 release deployment로만 처리하며, 기존 설치의 agent wiring·agent spec·설치 config의 사용자 값은 보존한다.

## Checks

Python 최소 버전, Runtime·workspace template, agent spec, 대상 `.mpa-workspace/` 부재와 변경 범위를 확인한다.

## Gates

dry-run이 통과해야 한다. 기존 설치본은 `install.py --upgrade`로 변경할 수 없다. Runtime 프로젝트의 설치 config·agent 설정·사용자 영역은 최초 설치 이후 이 도구가 임의로 변경하지 않는다. 단, release manifest가 명시한 `runtime.*` additive migration은 deploy transaction의 일부로 적용하며, 적용 전 config를 `.mpa-workspace`와 함께 백업한다.

## Output

신규 MPA Runtime, 초기 workspace 골격, `.mpa-project/config.yaml` 생성/보강 결과, 선택 agent 설정 또는 dry-run 결과. 기존 설치 config·agent 설정은 Runtime 프로젝트의 자체 관리 대상이다.

## Failure State

최초 설치는 dry-run에서 누락 의존성·충돌을 확인해 파일을 변경하지 않고 원인을 보고한다. Runtime 배포 실패는 배포가 만든 MPA Runtime 백업을 사용해 복구하고, 백업·복구 오류와 대상 설정은 사용자에게 고지한다.

## Prohibited

Runtime deploy/rollback은 Runtime 프로젝트의 `workspace/`, 루트 `docs/`, 일반 소스, agent 설정과 기존 config의 사용자 값을 변경하지 않는다. 명시된 `runtime.*` 누락값만 추가할 수 있고, Runtime backup은 배포 전 `.mpa-workspace` 및 그 config snapshot을 함께 보존하며 rollback 때 함께 복원한다. Runtime 프로젝트의 그 밖의 설정 변경과 전체 프로젝트 백업은 해당 프로젝트의 자체 버전 관리·백업 절차로 처리한다.
