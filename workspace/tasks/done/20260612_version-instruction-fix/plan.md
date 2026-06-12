---
태스크: version-instruction-fix
생성일: 2026-06-12
타입: minor
실패비용: minor
상태: 완료 승인
승인해시: 64f6e500c4e338a0
---

# 작업 계획서: version-instruction-fix

**파생 출처:** upgrade-candidates/version-edit-source-not-dist.md — discussion-mode 작업 중 발생한 버전 역전의 근본 원인(지시가 dist를 가리킴) 정정.

## 에이전트 보고

### 사용자 결정 필요
없음

### 암묵적 결정
- 수정 문구는 "설치본 `.mpa-workspace/.mpa-version` 갱신 → dist_sync가 dist로 미러"로 통일. (dist_sync.py 확인: `.mpa-workspace/` 편집을 dist로 복사, upgrade-candidates만 제외 → `.mpa-version`은 소스 편집 시 자동 동기화)

### 에이전트 가정
없음 (dist_sync 동작 실제 확인함)

### minor 판단 근거
- 단일 관심사: agent_rules_detail.md "current_version 갱신" 지시 문구
- 설계 결정 불필요: 해법이 후보에 명시됨
- git reset 복구 가능: 문서 편집
- 취향 불필요

## 요청 원문
upgrade-candidate `version-edit-source-not-dist.md` 반영 ("마저 정리하자")

## 목적
current_version 갱신 지시가 dist를 직접 가리켜 버전 역전을 유발하던 것을, 소스 편집 + 자동 미러로 정정한다.

## 구현 단계
- [ ] Step 1 — `.mpa-workspace/core/agent_rules_detail.md` L276 "current_version 갱신" 지시를 소스(.mpa-workspace) 편집 기준으로 수정
- [ ] Step 2 — L274 처리 흐름의 "dist/ 동기화 → current_version 갱신" 표현 정합 확인
- [ ] Step 3 — dist 자동 미러 확인
- [ ] Step 4 — upgrade-candidate 파일 반영 완료 처리 (삭제, project_rules 워크플로우)

## 수정 대상 파일
| 파일 | 변경 |
|------|------|
| `.mpa-workspace/core/agent_rules_detail.md` | current_version 갱신 지시 문구 정정 |
| dist 미러 | 자동 동기화 |
| `.mpa-workspace/upgrade-candidates/version-edit-source-not-dist.md` | 반영 후 삭제 |
