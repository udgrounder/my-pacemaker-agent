# 하위 작업 2: Adaptive gate와 plan integrity

## 목적

일반 작업을 불필요하게 멈추지 않으면서, critical 계획·release/deploy·승인 무결성 위반은 실행 전에 차단한다.

## 범위

- warn / critical block / strict block의 정책과 우선순위 정의
- plan frontmatter의 `실패비용`과 승인해시 검증을 이용한 critical 판정
- 기존 active task는 일괄 변경하지 않고, 사용자 재개 요청 시에만 재설계·승인으로 흡수하는 진단·문서화
- 정상·경고·차단 각각의 hook 회귀 테스트

## 제외

- 완료 task·immutable audit 이력의 해시나 상태 변경
- 사용자의 명시적 재개 요청 없는 기존 active task 수정

## 완료 증빙

- 일반 계획 누락은 경고로 통과하는 테스트
- critical plan의 승인 누락·불일치는 차단하는 테스트
- strict mode와 release/deploy preflight의 차단 테스트

## 의존성

하위 작업 1의 agent/hook 경로 계약
