# Layer 1 — 구현 세션

> **사용 시점:** 설계가 완료된 태스크를 구현할 때

---

## 역할

`.mpa-workspace/personas/implementer.md` 를 읽고 그 역할로 작업한다.

---

## 작업 시작 전 읽을 파일

다음 파일을 순서대로 읽는다:

1. `workspace/memory/shared/project_identity.md`
2. `workspace/memory/shared/architecture.md`
3. `workspace/memory/shared/contracts.md` (존재하는 경우)
4. `workspace/memory/domains/[작업 도메인]/rules.md`
5. `workspace/memory/domains/[작업 도메인]/registry.md` (존재하는 경우)
6. `.mpa-workspace/knowledge/` — 관련 도메인 파일이 있으면 읽는다 (존재하는 경우)
7. `workspace/memory/roles/implementer.md` (존재하는 경우) — 이 프로젝트에서 implementer 역할이 축적한 학습
8. `workspace/tasks/INDEX.md` — 이번 작업의 원본 요청 확인
9. 이번 태스크의 설계 계획 파일 (`workspace/tasks/active/yyyymmdd_[태스크명]/plan.md`)

관련 기술 스킬이 있으면 `.mpa-workspace/skills/tech/` 에서 해당 파일을 읽는다.

---

## 스킬 참조

필요 시 다음을 읽는다:
- `.mpa-workspace/skills/analysis/silent_decision_extraction.md`

---

## 구현 전 체크

구현 시작 전 다음을 확인한다:

0. **관련 태스크 맥락 파악** — plan.md 상단의 다음 두 필드를 먼저 읽는다:
   - **파생 출처**: 이 태스크가 어떤 맥락에서 분리됐는가 → 작업 배경을 이해
   - **파생된 태스크** (구현 후 발견 섹션): 이미 다른 태스크로 넘어간 항목 → 이 항목들은 여기서 다시 검토하지 않는다

   이 두 정보를 인식한 상태에서 구현을 시작한다.

1. **코드 탐색 및 계획 검증** — plan.md의 "수정 대상 파일"을 실제로 열어보고 확인한다:
   - 에이전트 가정(plan.md "에이전트 가정" 테이블)이 실제 코드와 맞는가?
   - 예상치 못한 의존성이나 제약이 있는가?
   - 구현 범위가 plan에서 예상한 것과 맞는가?
   → **불일치 또는 계획 수정이 필요한 발견 시: 구현 시작 전 사용자에게 보고하고 plan 재검토**

2. **이전 진행 확인** — `plan.md`의 "구현 단계" 체크리스트를 읽는다.
   - `changelog.md`가 이미 존재하면 읽어서 완료된 부분을 파악한다.
   - 체크된 단계는 건너뛰고, 첫 번째 미완료 단계부터 이어간다.
   - 이어가는 경우: plan.md 상태를 `구현 중`으로 업데이트하고 시작.

3. **가역성 확보** — 현재 브랜치/커밋 상태가 clean한가?
   → 아니라면 현 상태를 먼저 커밋하고 시작 (롤백 지점 확보)

4. **인터페이스 우선** — 다른 모듈과 연결되는 계약이 있다면 인터페이스 정의를 먼저 확정
   → 구현 전 `workspace/memory/shared/contracts.md` 관련 항목 확인

5. **범위 고정** — 태스크 계획의 scope를 넘어서는 변경 발견 시 구현 중단 후 보고
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
> 2. 구현 단계 체크리스트에서 완료된 항목은 체크, 건너뛴 항목은 ~~취소선~~ 후 이유 메모
> 3. `changelog.md`에 완료된 부분까지 기록 (다음 세션에 이어가기 위해)
>
> → 다음 세션은 이 정보를 읽고 중단된 지점부터 재개한다.

작업 완료 후 다음을 확인하고 필요한 파일을 직접 업데이트한다:

1. 아키텍처 업데이트 → `workspace/memory/shared/architecture.md`
   - **추가:** 구현 중 새로 내린 결정
   - **수정:** 기존 결정이 바뀌었다면 기존 항목을 교체 (이전 내용을 남기지 않는다)
   - **삭제:** 더 이상 유효하지 않은 규칙이나 패턴
2. 아키텍처 충돌 발견 → 즉시 보고 후 다음 작업 전 해소
3. 인터페이스 계약 변경 → `workspace/memory/shared/contracts.md`
4. 재사용 가능한 요소 추출 → `workspace/memory/domains/[도메인명]/registry.md`
5. **방향 증류** — 구현하면서 확인되거나 수정된 제품/UX 방향이 있으면 `workspace/memory/shared/direction.md`에 반영
   - "이 구현 방식이 맞다는 것을 확인했다" / "이 방식은 아니다" / "이런 흐름이 자연스럽다"
   - 기록할 것이 없으면 생략. 단, 없다고 판단한 것도 명시적으로 확인한다.
6. 역할 메모리 업데이트 → 자가 개선 필터 적용 후 `workspace/memory/roles/implementer.md`에 기록 (기억할 것이 없으면 생략)
7. 기능 문서 업데이트 → 요청 문서의 "완료 시 문서 업데이트 대상" 확인 후 `workspace/docs/` 반영
8. **plan.md 상태를 `구현 완료`로 업데이트한다**
9. MPA 시스템 개선 후보 발견 → `.mpa-workspace/upgrade-candidates/[내용].md`
10. **다음 작업 예측:** *"작업 결과 검토를 진행할까요?"*
