# Changelog

## 수정된 파일

### `.mpa-workspace/core/agent_rules.md`
- `### 3. 컨텍스트 선택 로딩` 섹션 추가 (기존 섹션 3은 4로 번호 변경)
  - Phase 1 (항상): project_rules.md + INDEX.md — 세션 시작 시 이미 읽음
  - Phase 2 필수/선택 파일 테이블 — 태스크 유형+단계별 6가지 상황 정의
- `작업 재개` > `재개 시 공통 처리` 3번 단계: Phase 2 로딩 참조 추가 (기존 inject 직접 참조 → 컨텍스트 선택 로딩 거쳐 inject로)

### `.mpa-workspace/inject/layer1_design.md`
- "작업 시작 전 읽을 파일" 섹션 재구성
  - 제거: project_rules.md (항목 1), INDEX.md (항목 7) — Phase 1로 이동
  - Phase 2 필수 (3개): project_identity, architecture, contracts
  - Phase 2 선택 (3개): direction, architect role, knowledge/*

### `.mpa-workspace/inject/layer1_implement.md`
- "작업 시작 전 읽을 파일" 섹션 재구성
  - 제거: project_rules.md (항목 1), project_identity.md (항목 2), INDEX.md (항목 9)
  - Phase 2 필수 (3개): architecture, contracts, plan.md
  - Phase 2 선택 (4개): domain/rules, domain/registry, knowledge/*, implementer role

### `.mpa-workspace/inject/layer1_review.md`
- "작업 시작 전 읽을 파일" 섹션 재구성
  - 제거: project_rules.md (항목 1), project_identity.md (항목 2)
  - Phase 2 필수 (4개): architecture, contracts, plan.md, changelog.md
  - Phase 2 선택 (2개): knowledge/*, code_reviewer role

### 검토 후 보정 (에이전트 가정 오류 수정)

**`layer1_implement.md`** — Phase 2 선택에 `project_identity.md` 복원
- 이유: architecture.md가 항상 충분한 프로젝트 맥락을 갖는다는 가정은 검증 불가. 도메인 판단이 필요한 구현 시 선택적으로 읽도록 변경

**`layer1_review.md`** — Phase 2 선택에 `project_identity.md` 복원
- 이유: 동일. 사용자 흐름·도메인 판단이 필요한 검토 시 읽도록 변경

**`agent_rules.md`** — 컨텍스트 선택 로딩 테이블 3개 행 선택 컬럼에 `project_identity.md` 추가

### `dist/` 동기화
- 최종 7개 파일 동기화 완료 (초기 4개 + 보정 3개)
