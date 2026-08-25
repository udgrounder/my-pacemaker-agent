# 하위 작업 5: CI regression automation (폐기)

## 목적

GitHub Actions 같은 상시 CI 대신, release package 생성 시 전체 회귀·Runtime parity·release audit을 실행하도록 검증 계약에 흡수한다.

## 범위

- package 생성 검증에서 아래 명령을 순서대로 실행한다.
  ```sh
  python3 -m unittest discover -s tests -v && diff -qr .mpa/runtime dist/.mpa/runtime && python3 release_manager.py release-audit
  ```
- 실패 시 어느 검증 단계가 실패했는지 식별 가능한 로그를 남긴다.

## 제외

- GitHub Actions workflow 또는 다른 상시 CI 제공자 설정
- 실제 release 생성·deploy·rollback

## 폐기 근거

- 현재 프로젝트는 release 중심으로 운영되며, 상시 CI는 검증 효익보다 구성·운영 비용이 크다.
- package 생성이 검증된 artifact의 유일한 진입점이므로, 해당 시점의 강제 검증이 안전 경계를 충족한다.

## 후속 처리

- 검증 명령과 release artifact 생성 차단은 [sub_04_release_audit_hardening.md](sub_04_release_audit_hardening.md)에서 구현·검증한다.
