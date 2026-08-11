# Installation Profile

## 최초 설치

`install.py`는 `.mpa-workspace/`가 없는 명시된 대상에만 Runtime과 초기 workspace 골격, 선택된 agent 진입 설정을 설치한다.

## 기존 설치본

기존 `.mpa-workspace/`가 있는 대상의 Runtime 업데이트는 `release_manager.py deploy`를 사용한다. `install.py --upgrade`는 허용하지 않는다.

## Installation refresh

agent 설정이나 설치 골격 갱신은 사용자가 명시적으로 요청한 경우에만 별도 절차로 수행한다. Runtime deployment에 포함하지 않는다.
