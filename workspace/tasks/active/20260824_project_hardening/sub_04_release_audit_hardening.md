# 하위 작업 4: Release audit hardening

## 목적

활성 source와 staging package만 대상으로, legacy 실행 참조·모든 Python hook 문법·receipt/출력의 민감한 절대 경로 노출을 재현 가능하게 검증한다.

## 범위

- `release_manager.py`의 audit 대상과 오류 메시지 정제 규칙 보완
- 활성 Runtime/package의 실행 등록에서 retired `.mpa-workspace` 참조 탐지
- package 안의 모든 Python hook 정적 문법 검증
- manifest·release receipt·audit 출력에 machine absolute path가 남지 않는 회귀 테스트
- `map-product-rules/release-preparation.md`의 package 검증·로그 정제 규칙 반영
- release package 생성 전에 전체 단위 테스트, source/runtime-dist parity, release audit을 순서대로 실행하는 검증 계약 반영
- 직전 유효 release와 `.mpa-version` 외 Runtime asset이 같은 version-only package 기본 거부 및 명시 override 제공

## 제외

- immutable 과거 release·receipt·backup·완료 task 이력의 수정 또는 삭제
- 외부 파일 보관·수정 권한 기능
- 새 release 생성이나 실제 deploy/rollback

## 완료 증빙

- legacy 실행 참조, hook 문법 오류, absolute-path 노출 각각을 실패시키는 회귀 테스트
- 정상 bundle의 `release-audit` 통과
- 전체 단위 테스트·runtime/dist parity 통과
- package 생성 검증이 실패하면 release artifact를 만들지 않는 테스트
- version-only 거부 후 source/runtime-dist version이 원복되고, 명시 override는 package를 생성하는 테스트

## 의존성

- Runtime wiring 및 adaptive gate·plan integrity 완료
