---
태스크: template-readme-update
생성일: 2026-06-08
타입: minor
실패비용: minor
상태: 완료 승인
승인해시: 1a66298c89dbf447
---
**목적:** plan_template.md 섹션 보완 및 workspace/tasks/README.md 현행화
**요청:** 계획서에 사용자 결정/암묵적 결정/에이전트 가정 필수 명시, minor_plan_template.md 통합, README.md 오류 수정

### 핵심 기능
- plan_template.md에 `### 암묵적 결정` 섹션 추가
- 사용자 결정·암묵적 결정·에이전트 가정 "없으면 섹션 생략" → "없으면 `없음` 명시"
- minor 태스크용 `### minor 판단 근거` 체크리스트 추가
- agent_rules.md의 minor_plan_template.md 참조 → plan_template.md로 변경
- workspace/tasks/README.md 5개 오류 수정

### 사용자 결정
- minor_plan_template.md 별도 유지 불필요 — plan_template.md 하나로 통합

### 암묵적 결정
- minor_plan_template.md 파일 자체는 삭제하지 않고 참조만 제거

### 에이전트 가정
- 없음

### minor 판단 근거
- 한 파일/단일 관심사: MPA 템플릿·규칙 문서만 수정
- 설계 결정 불필요: 사용자가 변경 방향 명시
- git reset으로 복구 가능: 문서 파일만 수정

### 구현
1. plan_template.md 수정
2. agent_rules.md 참조 수정
3. workspace/tasks/README.md + dist/ 수정
