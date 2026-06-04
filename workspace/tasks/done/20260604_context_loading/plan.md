# 태스크: 2단계 컨텍스트 선택 로딩
**상태:** 구현 완료  
**목적:** 태스크 선택 후 실제 필요한 파일만 읽도록 로딩 방식을 2단계로 분리해 I/O 오버헤드 감소

---

## 에이전트 보고

**사용자 결정 필요:** 없음

**에이전트 가정:**
| 가정 | 근거 | 틀렸을 때 영향 |
|------|------|--------------|
| project_identity.md는 구현·리뷰 단계에서 불필요 | 설계 시에만 "왜 이 프로젝트인가"가 필요함 | 구현자가 프로젝트 맥락을 오해할 수 있음 → Phase 2로 이동 |
| contracts.md는 구현·리뷰 모두 필수 | 인터페이스 계약은 모든 단계에서 위반 방지에 필요 | contracts 없이 구현 → 계약 위반 미탐지 위험 |
| INDEX.md는 Phase 1 공통 최소 세트에 포함 | 태스크 선택 자체에 필요, 매우 작은 파일 | 영향 없음 |

---

## 핵심 변경 내용

### 변경 1: agent_rules.md — "컨텍스트 선택 로딩" 섹션 추가

세션 시작 루틴의 "현재 상태 파악" 단계를 수정:
- **Phase 1 (항상):** `project_rules.md` + `INDEX.md` 만 읽는다
- 태스크 선택 후 **Phase 2** 진입: 태스크 유형+단계 기준 파일 목록 결정

추가할 테이블:

| 상황 | Phase 2 필수 | Phase 2 선택 (필요 시) |
|------|------------|---------------------|
| 기존 태스크: 구현 중 | plan.md, architecture.md, contracts.md | domain/rules.md, roles/implementer.md |
| 기존 태스크: 설계 완료 | plan.md, architecture.md, contracts.md | roles/architect.md |
| 기존 태스크: 구현 완료 | plan.md, changelog.md, architecture.md, contracts.md | roles/code_reviewer.md |
| 새 태스크: 설계/리팩터링 | project_identity.md, architecture.md, contracts.md | direction.md, knowledge/*, roles/architect.md |
| 새 태스크: 버그 수정 | architecture.md, contracts.md | roles/code_reviewer.md |
| 단순 질문/탐색 | 없음 | on-demand |

> inject 파일의 "작업 시작 전 읽을 파일" 섹션은 Phase 2 선택 파일 중 해당 세션에서 특히 중요한 것을 안내한다. Phase 1에서 이미 읽은 파일은 재읽지 않는다.

### 변경 2: 각 inject 파일 — "작업 시작 전 읽을 파일" 섹션 축소

기존: 전체 파일 목록 (8~10개)  
변경: agent_rules.md Phase 1에서 이미 읽은 파일 제거 + Phase 2 선택 파일만 안내

| 파일 | 제거되는 항목 | 남는 항목 |
|------|------------|---------|
| layer1_design.md | project_rules.md, INDEX.md | project_identity, architecture, contracts, direction, architect role, knowledge |
| layer1_implement.md | project_rules.md, project_identity.md, INDEX.md | architecture, contracts, domain rules, implementer role, plan.md, knowledge |
| layer1_review.md | project_rules.md, project_identity.md | architecture, contracts, reviewer role, plan.md, changelog.md, knowledge |

---

## 수정 대상 파일

| 파일 | 변경 유형 |
|------|---------|
| `.mpa-workspace/core/agent_rules.md` | 세션 시작 루틴 수정 + 컨텍스트 선택 로딩 섹션 추가 |
| `.mpa-workspace/inject/layer1_design.md` | "작업 시작 전 읽을 파일" 섹션 축소 |
| `.mpa-workspace/inject/layer1_implement.md` | "작업 시작 전 읽을 파일" 섹션 축소 |
| `.mpa-workspace/inject/layer1_review.md` | "작업 시작 전 읽을 파일" 섹션 축소 |
| `dist/` 복사본 4개 | 동기화 |

---

## 구현 단계

- [ ] 1. `agent_rules.md` — 세션 시작 루틴 "현재 상태 파악" 수정 + "컨텍스트 선택 로딩" 섹션 추가
- [ ] 2. `layer1_design.md` — "작업 시작 전 읽을 파일" 섹션 수정
- [ ] 3. `layer1_implement.md` — "작업 시작 전 읽을 파일" 섹션 수정
- [ ] 4. `layer1_review.md` — "작업 시작 전 읽을 파일" 섹션 수정
- [ ] 5. `dist/` 4개 파일 동기화
- [ ] 6. 파일 간 일관성 점검

---

## 반례 (이 계획이 실패하는 시나리오)

- **시나리오 1**: inject 파일에서 "이미 읽었다고 가정"한 파일을 에이전트가 실제로 읽지 않은 경우 → Phase 1 로딩이 실제로 실행됐는지 확인하는 메커니즘이 없음. 완화: agent_rules.md Phase 1 정의를 명확하게 명령형으로 작성
- **시나리오 2**: project_identity.md를 구현 단계 Phase 2 선택으로 내렸을 때 에이전트가 프로젝트 맥락 없이 판단해 아키텍처와 무관한 구현 패턴을 선택 → 완화: architecture.md에 프로젝트 핵심 맥락 요약 포함 여부 확인
