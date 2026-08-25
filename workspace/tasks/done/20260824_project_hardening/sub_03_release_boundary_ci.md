# 하위 작업 3: Release 경계 최소 preflight (완료)

## 목적

runtime 배포·backup·설정 처리가 대상 프로젝트 바깥을 읽거나 쓰지 못하게 하는 최소 경계를 구현한다. 남은 package audit과 package 생성 검증은 별도 하위 작업으로 분리한다.

## 범위

- runtime/config/workspace/docs/backups의 symlink·root escape preflight 거부
- config symlink의 예외를 정상 오류 진단으로 변경
- package의 symlink·special file·type mismatch 사전 거부

## 제외

- immutable 과거 release·receipt·backup의 수정 또는 삭제
- 명시 요청 없는 prepare-release, deploy, rollback
- 외부 파일 보관·수정 권한 기능 — 실제 사용 사례가 생길 때 새 critical 작업으로 설계
- package audit 강화 — [sub_04_release_audit_hardening.md](sub_04_release_audit_hardening.md)에서 처리
- 상시 CI 자동화 — release 중심 운영에는 과하므로 폐기. package 생성 검증은 [sub_04_release_audit_hardening.md](sub_04_release_audit_hardening.md)에서 처리

## 완료 증빙

- symlink 대상이 외부 경로를 가리킬 때 변경 전 중단하는 테스트
- ZIP symlink·special file·type mismatch 거부 테스트
- deploy/rollback 경로의 symlink 거부 테스트

## 의존성

하위 작업 1·2의 경로 및 gate 계약
