# Layer 1 — 구현 세션

> **사용 시점:** 설계가 완료된 태스크를 구현할 때

---

## 역할

`.mpa-workspace/personas/implementer.md` 를 읽고 그 역할로 작업한다.

---

## 작업 시작 전 읽을 파일

다음 파일을 순서대로 읽는다:

1. `workspace/project_memory/shared/project_identity.md`
2. `workspace/project_memory/shared/architecture.md`
3. `workspace/project_memory/shared/contracts.md` (존재하는 경우)
4. `workspace/project_memory/domains/[작업 도메인]/rules.md`
5. `workspace/project_memory/domains/[작업 도메인]/registry.md` (존재하는 경우)
6. `workspace/project_memory/roles/implementer.md` (존재하는 경우) — 이 프로젝트에서 implementer 역할이 축적한 학습
7. `workspace/tasks/INDEX.md` — 이번 작업의 원본 요청 확인
8. 이번 태스크의 설계 계획 파일 (`workspace/tasks/active/[태스크명]/plan.md`)

관련 기술 스킬이 있으면 `.mpa-workspace/skills/tech/` 에서 해당 파일을 읽는다.

---

## 스킬 참조

필요 시 다음을 읽는다:
- `.mpa-workspace/skills/analysis/silent_decision_extraction.md`

---

## 구현 전 체크

구현 시작 전 다음을 확인한다:

0. **코드 탐색 및 계획 검증** — plan.md의 "수정 대상 파일"을 실제로 열어보고 확인한다:
   - 에이전트 가정(plan.md "에이전트 가정" 테이블)이 실제 코드와 맞는가?
   - 예상치 못한 의존성이나 제약이 있는가?
   - 구현 범위가 plan에서 예상한 것과 맞는가?
   → **불일치 또는 계획 수정이 필요한 발견 시: 구현 시작 전 사용자에게 보고하고 plan 재검토**

1. **이전 진행 확인** — `plan.md`의 "구현 진행 상태" 섹션을 읽는다.
   - `changelog.md`가 이미 존재하면 읽어서 완료된 부분을 파악한다.
   - 이미 완료된 단계는 건너뛰고, 중단된 단계부터 이어간다.
   - 이어가는 경우: plan.md 상태를 `구현 중`으로 업데이트하고 시작.

2. **가역성 확보** — 현재 브랜치/커밋 상태가 clean한가?
   → 아니라면 현 상태를 먼저 커밋하고 시작 (롤백 지점 확보)

3. **인터페이스 우선** — 다른 모듈과 연결되는 계약이 있다면 인터페이스 정의를 먼저 확정
   → 구현 전 `workspace/project_memory/shared/contracts.md` 관련 항목 확인

4. **범위 고정** — 태스크 계획의 scope를 넘어서는 변경 발견 시 구현 중단 후 보고
   → 범위 밖 변경은 다음 태스크로 분리

---

## 완료 기준

- [ ] 구현 완료
- [ ] 정상 경로 1개 추적 확인
- [ ] 실패 경로 1개 추적 확인
- [ ] 태스크 계획의 조용한 결정 후보가 모두 처리됨 (추정 없이)
- [ ] 범위 밖 변경이 없거나, 있다면 보고됨

---

## 세션 종료 시

> **구현이 완료되지 않은 채 세션을 끝내야 하는 경우:**
> 1. `plan.md` 상태를 `구현 중`으로 업데이트
> 2. 구현 진행 상태 섹션에서 완료된 단계는 ✅, 미완료는 🔄 또는 ⏳로 표시
> 3. `changelog.md`에 완료된 부분까지 기록 (다음 세션에 이어가기 위해)
>
> → 다음 세션은 이 정보를 읽고 중단된 지점부터 재개한다.

작업 완료 후 다음을 확인하고 필요한 파일을 직접 업데이트한다:

1. 구현 중 내린 결정 (태스크 계획에 없었던 것) → `workspace/project_memory/shared/architecture.md` 결정 이력
2. 아키텍처 충돌 발견 → 즉시 보고 후 다음 작업 전 해소
3. 인터페이스 계약 변경 → `workspace/project_memory/shared/contracts.md`
4. 재사용 가능한 요소 추출 → `workspace/project_memory/domains/[도메인명]/registry.md`
5. 역할 메모리 업데이트 → 놀라움 필터 적용 후 `workspace/project_memory/roles/implementer.md`에 기록 (기억할 것이 없으면 생략)
6. 기능 문서 업데이트 → 요청 문서의 "완료 시 문서 업데이트 대상" 확인 후 `workspace/docs/` 반영
7. 요청 상태 → `workspace/tasks/` 해당 파일을 `done/`으로 이동
8. 하네스 개선 후보 발견 → `.mpa-workspace/upgrade-candidates/[내용].md`
