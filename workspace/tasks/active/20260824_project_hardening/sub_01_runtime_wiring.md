# 하위 작업 1: Runtime wiring 정합성

## 목적

설치된 Claude·Codex·Antigravity·OpenAgent의 진입점, native rule, hook 등록이 모두 실제 존재하는 `.mpa/runtime` 파일을 가리키게 한다.

## 범위

- source agent 설정과 `agent-specs/`의 retired `.mpa-workspace` 실행 참조 제거
- `install.py`의 hook 중복 등록 marker를 현재 runtime 경로 계약으로 정렬
- clean target에 각 지원 agent를 설치한 뒤 등록 파일·hook 경로 존재 및 실행 여부를 검증
- source Runtime을 `dist/.mpa/runtime/`에 동기화하고 parity 검증

## 제외

- 대상 프로젝트의 기존 사용자 정의 agent 설정을 일괄 수정하지 않음
- 새 release 생성 또는 실제 대상 프로젝트 배포를 수행하지 않음

## 완료 증빙

- 지원 agent별 clean-install E2E 테스트
- 등록된 모든 runtime/hook 경로의 존재성·실행성 검사
- source/runtime-dist parity 검사

## 의존성

없음
