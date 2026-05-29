# Layer 1 — 검토 세션

> **사용 시점:** 구현이 완료된 코드를 독립적으로 검토할 때

---

## 역할

`.mpa-workspace/personas/code_reviewer.md` 를 읽고 그 역할로 작업한다.

---

## 작업 시작 전 읽을 파일

다음 파일을 순서대로 읽는다:

1. `workspace/project_memory/shared/project_identity.md`
2. `workspace/project_memory/shared/architecture.md`
3. `workspace/project_memory/shared/contracts.md` (존재하는 경우)
4. `workspace/project_memory/roles/code_reviewer.md` (존재하는 경우)
5. 이번 태스크의 설계 계획 파일 (`workspace/tasks/active/[태스크명]/plan.md`)
6. 이번 태스크의 구현 내역서 (`workspace/tasks/active/[태스크명]/changelog.md`) — 존재하면 읽기

---

## 스킬 참조

필요 시 다음을 읽는다:
- `.mpa-workspace/skills/analysis/counterexample_finding.md`
- `.mpa-workspace/skills/analysis/path_tracing.md`

관련 기술 스킬이 있으면 `.mpa-workspace/skills/tech/` 에서 해당 파일을 읽는다.

---

## 검토 항목

다음 항목을 순서대로 검토한다:

### 1. 설계 정합성
- 태스크 계획의 각 step이 구현되었는가?
- 사전 결정 필요 사항이 올바르게 처리되었는가?
- **에이전트 가정 검증**: plan.md "에이전트 가정" 테이블의 각 항목이 구현 중 유효했는가?
  - 가정이 틀렸다면 changelog.md에 기록되어 있는가?
  - 틀린 가정이 구현 결과에 어떤 영향을 미쳤는가?

### 2. 아키텍처 규칙 준수
- 절대 금지 항목을 위반한 것이 있는가?
- 기존 패턴을 따랐는가, 아니면 새 패턴을 도입했는가?

### 3. 조용한 결정 탐지
- 설계에 없었던 결정이 코드에 포함되어 있는가?
- 이 코드가 가정하고 있는 것이 무엇인가?

### 4. 실패 경로
- 에러 처리가 되어 있는가?
- 엣지 케이스가 고려되었는가?

---

## 완료 기준

- [ ] 정상 경로 1개 추적 완료
- [ ] 실패 경로 1개 추적 완료
- [ ] 설계(태스크 계획)와의 정합성 확인됨
- [ ] 에이전트 가정 검증 완료 (맞은 가정 / 틀린 가정 / 영향 분류)
- [ ] 아키텍처 규칙 위반 여부 점검됨
- [ ] 조용한 결정이 모두 탐지되고 분류됨 (의도적/비의도적)

---

## 산출물 형식

```
## 검토 결과

### ✅ 정합성 확인
- 항목:

### ⚠️ 주의 필요
- 항목: [문제] / 권장: [수정 방향]

### 🚨 즉시 수정 필요
- 항목: [문제] / 이유:

### 📝 조용한 결정 목록
- 결정 1: [내용] / 판단: [의도적 위임 / 비가시적 위임]

### 🔍 에이전트 가정 검증
- 가정 1: [내용] / 결과: [유효 / 틀림] / 영향: [없음 / 경미 / 계획 변경 필요]
```

---

## 세션 종료 시

작업 완료 후 다음을 확인하고 필요한 파일을 직접 업데이트한다:

1. 새 아키텍처 규칙 또는 안티패턴 발견 → `workspace/project_memory/shared/architecture.md`
2. 역할 메모리 업데이트 → 놀라움 필터 적용 후 `workspace/project_memory/roles/code_reviewer.md`에 기록 (기억할 것이 없으면 생략)
3. 하네스 개선 후보 발견 → `.mpa-workspace/upgrade-candidates/[내용].md`
