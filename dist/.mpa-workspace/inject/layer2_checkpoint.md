# Layer 2 — 통합 체크포인트

> **사용 시점:** 여러 기능이 축적된 후 전체 정합성 점검 시
> **권장 주기:** 3~5개 태스크 완료 후, 또는 스프린트 종료 시

---

## 역할

`.mpa-workspace/personas/integration_auditor.md` 를 읽고 그 역할로 작업한다.

---

## 작업 시작 전 읽을 파일

다음 파일을 모두 읽는다:

1. `workspace/memory/shared/project_identity.md`
2. `workspace/memory/shared/architecture.md`
3. `workspace/memory/shared/contracts.md` (존재하는 경우)
4. `workspace/memory/shared/direction.md` (존재하는 경우)
5. `workspace/memory/domains/` 하위 모든 `rules.md`, `registry.md`
6. `workspace/memory/roles/` 하위 모든 `.md` 파일 (존재하는 경우)
7. `workspace/tasks/INDEX.md`
8. `workspace/docs/INDEX.md`

---

## 스킬 참조

필요 시 다음을 읽는다:
- `.mpa-workspace/skills/analysis/dependency_mapping.md`
- `.mpa-workspace/skills/analysis/counterexample_finding.md`
- `.mpa-workspace/skills/analysis/path_tracing.md`

---

## 점검 항목

> **착수 전 — 대상의 층위를 먼저 분류한다.** 점검 대상이 **실행 레이어**(매 세션 로드돼 agent 행동을 규정: `core/*`·`inject/*`·`hooks/*`)인지 **설명 레이어**(사람이 읽는 문서: `guidebook/*`·README 등 — 로드되지 않음)인지 구분한다. "실행 비용·준수 지속가능성·절차 무게"에 관한 지적은 실행 레이어에만 유효하고, 설명 레이어엔 가독성·정확성만 적용된다. 라벨로 단정하지 말고 진입점 참조 체인 grep으로 확인한다.

순서대로 점검한다:

### 1. 문서 vs 현실 괴리 (Documentation Drift)
- 현재 코드에서 `architecture.md` 규칙을 위반한 부분이 있는가?
- `architecture.md`에 기록된 결정이 실제로 바뀌었는데 문서는 이전 내용 그대로인 항목이 있는가?
- `contracts.md`에 없는 인터페이스가 실제로 사용되고 있는가?
- registry에 없는 재사용 요소가 새로 만들어졌는가?
- `workspace/project_rules.md`가 존재하는 경우: 현재 프로젝트 상태와 맞는가? (라우팅 힌트가 유효한가, 금지 패턴이 실제로 지켜지고 있는가)

### 2. 로컬 최적화 트랩
- 각 기능은 잘 동작하지만 서로 충돌하는 결정이 있는가?
- 같은 문제를 다른 방식으로 해결한 부분이 있는가? (비일관성)

### 3. 안티패턴 누적
- 이미 `architecture.md`에 기록된 안티패턴이 반복되고 있는가?
- 새로 발견된 안티패턴이 있는가?

### 4. direction.md 정합성 (존재하는 경우)
- 기록된 UX 원칙이 지금까지 구현된 것과 실제로 일치하는가?
- 태스크들을 거치면서 방향이 바뀌었는데 direction.md에 반영되지 않은 것이 있는가?
- direction.md에 없지만 지금은 명확해진 방향 원칙이 있는가?
- direction.md에 있지만 실제로는 포기된 방향이 있는가?

### 5. memory 업데이트 필요 사항
- 실제로 사용되고 있지만 문서에 없는 패턴은?
- 문서에는 있지만 실제로는 사용되지 않는 규칙은?

### 6. 요청 / 문서 동기화 점검
- `tasks/INDEX.md`에서 `done`으로 표시됐지만 문서 업데이트가 미처리된 항목이 있는가?
- `tasks/active/`에 오래 방치된 요청이 있는가?
- `docs/INDEX.md`에서 관련 요청이 없는 문서가 있는가?

### 7. INDEX vs 태스크 폴더 동기화

`active/` 및 `done/` 폴더의 태스크가 INDEX.md에 모두 등록됐는지 확인한다.

```bash
ls workspace/tasks/active/ workspace/tasks/done/
```

- 폴더에 있는데 INDEX에 없는 항목 → INDEX에 추가 (타입·상태·요약·생성일·점검 채움)
- INDEX에 있는데 폴더에 없는 항목 → INDEX에서 제거 또는 경로 확인

> **점검 상태는 INDEX.md가 단일 소스다.** plan.md에는 점검 필드가 없으므로 INDEX가 손상되면 점검 상태는 재확인이 필요하다.

> 이 검사는 매 태스크마다 하지 않는다. Layer 2 시 일괄로 처리해 인지 부담을 분산한다.

### 8. 사용자 회고 (외부 감사)

> 에이전트는 세션 간 연속성이 없어 반복 패턴을 스스로 인식하지 못한다.
> 이 단계는 연속성을 가진 사용자가 패턴을 발견하기 위한 것이다.

에이전트가 다음 두 가지를 준비해 사용자에게 제시한다:

**1. 최근 upgrade-candidates 요약**
`.mpa-workspace/upgrade-candidates/` 파일 목록과 각 파일의 발견 상황 한 줄 요약.

**2. 에이전트 가정 오류 사례**
이번 Layer 2 대상 태스크들의 plan.md에서 "에이전트 가정" 항목 중 구현 중 틀린 것으로 밝혀진 사례를 수집한다.
(결정 이력에 "가정 → 사실로 확정" 또는 plan 재수정 기록이 있는 항목)

제시 형식:
```
[사용자 회고 요청]

upgrade-candidates 누적: [N]개
에이전트 가정 오류 사례:
  - [태스크명]: "[가정 내용]" → 실제: "[결과]"
  - (없으면 생략)

이 패턴들을 보면서 에이전트가 반복적으로 틀리거나 놓치는 것이 보이시나요?
없으면 "없음"으로 넘어가도 됩니다.
```

**사용자 답변 처리:**
- 패턴 발견 → `.mpa-workspace/upgrade-candidates/[내용].md`에 타입 A(방법론 개선)로 기록
- "없음" 또는 무응답 → 다음 단계로 진행

---

### 9. 지식 승격 후보 평가

`workspace/memory/domains/*/rules.md`에 누적된 지식 중 다음 질문을 통과하는 항목을 식별한다:

> **"이 지식이 다른 프로젝트의 의사결정도 바꾸는가?"**

통과 항목은 `.mpa-workspace/upgrade-candidates/[내용].md`에 도메인 지식 형식(타입 B)으로 export한다.
형식: `core/agent_rules_detail.md` "upgrade-candidates 형식" 섹션 참조.

> 매 태스크마다 경계를 판단하지 않는다. Layer 2에서 한꺼번에 평가하는 것이 단방향 흐름 원칙이다.
> 사용자가 upgrade-candidates를 승인하면 `.mpa-workspace/knowledge/[도메인].md`로 승격된다.

---

## 완료 기준

- [ ] Documentation Drift 점검 완료
- [ ] 로컬 최적화 트랩 확인 완료
- [ ] 안티패턴 누적 검토 완료
- [ ] memory 업데이트 항목 도출됨
- [ ] 요청/문서 동기화 점검 완료
- [ ] INDEX vs 태스크 폴더 동기화 확인 (누락·불일치 없음)
- [ ] 사용자 회고 제시 완료 (upgrade-candidates 요약 + 가정 오류 사례)
- [ ] 지식 승격 후보 평가 완료 (`domains/` → `upgrade-candidates/`)
- [ ] 발견 사항이 즉시 / 다음 스프린트 / 기록으로 분류됨

---

## 산출물 형식

```
## Layer 2 체크포인트 결과

### 🚨 즉시 해소 필요
- 충돌 1: [내용]

### ⚠️ 다음 스프린트 전 처리
- 항목 1: [내용]

### 📝 workspace 업데이트 목록
- `shared/architecture.md` 추가/수정: [내용]
- `shared/contracts.md` 업데이트: [내용]
- `shared/direction.md` 업데이트: [추가/수정/삭제할 방향 원칙]
- 안티패턴 추가: [패턴] / 이유: [내용]
- `domains/[도메인명]/registry.md` 업데이트: [내용]
- `tasks/` 미처리 항목: [내용]
- `docs/` 미반영 항목: [내용]

### ✅ 정합성 확인된 항목
- 항목:
```

---

## 세션 종료 시

산출물에 따라 `workspace/` 파일을 직접 업데이트한다.
MPA 시스템 개선 후보 발견 시 `.mpa-workspace/upgrade-candidates/[내용].md` 에 기록한다.
