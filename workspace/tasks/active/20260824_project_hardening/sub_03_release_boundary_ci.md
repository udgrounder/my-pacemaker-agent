# 하위 작업 3: Release 경계와 CI

## 목적

runtime 배포·backup·설정 처리가 대상 프로젝트 바깥을 읽거나 쓰지 못하게 하고, package와 검증 기록이 재현 가능하고 안전하게 유지되도록 한다.

## 범위

- runtime/config/workspace/docs/backups의 symlink·root escape preflight 거부
- config symlink의 예외를 정상 오류 진단으로 변경
- 사용자가 명시한 외부 파일의 읽기 허용, 지속 입력 보관 시 출처·무결성 기록, 외부 수정 시 명시 승인·대상 범위 확인
- staging package에서 활성 legacy 실행 참조, 전체 hook 문법, asset map 검증
- release manifest·receipt의 절대 경로와 민감 로그 최소화
- agent E2E, boundary, gate, package 검증을 CI에서 실행

## 제외

- immutable 과거 release·receipt·backup의 수정 또는 삭제
- 명시 요청 없는 prepare-release, deploy, rollback

## 완료 증빙

- symlink 대상이 외부 경로를 가리킬 때 변경 전 중단하는 테스트
- 사용자 지정 외부 파일의 읽기 허용과 MPA 관리 symlink 거부를 구분하는 테스트
- 활성 package의 legacy 실행 참조 및 hook 문법 실패 테스트
- absolute path가 receipt에 그대로 남지 않는 테스트
- 전체 단위 테스트, runtime/dist parity, release audit, CI 명령 성공

## 의존성

하위 작업 1·2의 경로 및 gate 계약
