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

순서대로 점검한다:

### 1. 문서 vs 현실 괴리 (Documentation Drift)
- 현재 코드에서 `architecture.md` 규칙을 위반한 부분이 있는가?
- `architecture.md`에 기록된 결정이 실제로 바뀌었는데 문서는 이전 내용 그대로인 항목이 있는가?
- `contracts.md`에 없는 인터페이스가 실제로 사용되고 있는가?
- registry에 없는 재사용 요소가 새로 만들어졌는가?

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

---

## 완료 기준

- [ ] Documentation Drift 점검 완료
- [ ] 로컬 최적화 트랩 확인 완료
- [ ] 안티패턴 누적 검토 완료
- [ ] memory 업데이트 항목 도출됨
- [ ] 요청/문서 동기화 점검 완료
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
하네스 개선 후보 발견 시 `.mpa-workspace/upgrade-candidates/[내용].md` 에 기록한다.
