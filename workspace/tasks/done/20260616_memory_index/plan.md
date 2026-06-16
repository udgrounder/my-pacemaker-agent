---
태스크: memory_index
생성일: 2026-06-16
타입: major
실패비용: major
상태: 완료 승인
승인해시: 29a0509372c27e3a
---

# 작업 계획서: memory_index

**파생 출처:** 없음 — "workspace 하위 폴더에도 index가 있는 게 낫지 않을까" 논의에서 도출

---

## 에이전트 보고

> **구현 전에 이 섹션을 먼저 확인하세요.**

### 사용자 결정 필요

- [ ] INDEX 파일 배치 — 단일 `memory/INDEX.md`(domains+roles 한 파일) vs 폴더별(`domains/INDEX.md`+`roles/INDEX.md`)
  - 단일 (권장) → 세션 시작 시 **한 파일만** 읽고 선별. 기존 `tasks/INDEX.md`·`docs/INDEX.md`가 폴더 루트 1파일인 패턴과 일치
  - 폴더별 → 도메인이 많아지면 분리 관리. 대신 매 작업마다 2파일 읽기

### 암묵적 결정

- `shared/`(architecture·contracts·direction·project_identity)는 INDEX에 등록하지 않음 — 라우팅 표가 **고정 이름으로 직접 로드**하므로 선별 대상이 아님. 다른 방향이면: shared도 포함
- INDEX 소비 시점은 "3. 컨텍스트 선택 로딩"(작업 라우팅 시) — 단순 질문·토론 모드 등 메모리 불필요 유형은 읽지 않음
- 빈 INDEX라도 지금 생성 — 등록 규칙의 대상 그릇을 먼저 만들어 둠 (domains/roles는 현재 비어 있음)

### 에이전트 가정

| 가정 | 근거 | 틀렸다면 |
|-----|------|---------|
| dist는 hook(dist_sync.py)이 자동 미러 | `.claude/settings.json`에 등록 확인, detail "dist 직접 편집 금지" 명시 | 수동 동기화 단계 추가 |
| 미래 프로젝트도 같은 구조 필요 → layer0_init에 스캐폴딩 추가 | layer0이 domains/rules.md 초안을 만드는데 INDEX는 안 만듦 → 불일치 | layer0 수정 제외, 이 프로젝트 한정 |

---

## 요청 원문

"workspace 아래 하위 폴더들도 index 파일이 있는 게 낫지 않을까?" → 논의 결과: `exploration/`은 보류, **`memory/`의 가변 영역(domains/roles)에 INDEX**를 두고 작업마다 사전 선별하는 규칙 추가. `shared/`는 고정 이름 직접 로드라 제외.

---

## 목적

매 작업마다 참조되는 `memory/`에서, 읽기 전에 "이 작업에 매치되는 domain/role 메모리"를 골라낼 선별 인덱스를 도입한다.

---

## 요구사항

1. `workspace/memory/INDEX.md` 생성 — domains/roles 선별용 캐시 (shared 제외)
2. 세션의 컨텍스트 로딩 시 INDEX를 먼저 읽어 매치되는 파일만 로드하는 규칙
3. 메모리 파일 생성·갱신 시 INDEX에 등록하는 규칙 (write-side)
4. 신규 프로젝트에도 전파 (layer0_init 스캐폴딩)
5. 방법론 수정 반영 (version bump)

---

## 구현 단계

- [x] Step 1 — `workspace/memory/INDEX.md` 생성 / 이유: 선별 대상 그릇 + 원칙(폴더=정답, INDEX=캐시) 명시
- [x] Step 2 — `core/agent_rules.md` "3. 컨텍스트 선택 로딩"에 Phase 1.5 사전 선별 스텝 추가 / 이유: read-side 규칙
- [x] Step 3 — `core/agent_rules_detail.md` "기억 여부 판단"·"기술/도메인 지식 기록 기준"·"역할 메모리 업데이트"에 INDEX 등록 스텝 추가 / 이유: write-side 규칙 (생성=등록 동기화)
- [x] Step 4 — `inject/layer0_init.md` memory 초안 단계(신규·기존 흐름 양쪽)에 INDEX.md 생성 항목 추가 / 이유: 신규 프로젝트 전파
- [x] Step 5 — `.mpa-workspace/.mpa-version` current_version → 2026-06-16 / 이유: 방법론 의미 변경
- [x] Step 6 — 규칙 간 일관성 점검 완료 (참조처 3파일 일관 · dist 자동 동기화 · 용어 충돌 없음)
- [x] Step 7 — INDEX 부재 시 자동 생성 보강 (추가 요구) / 이유: 이 방법론 도입 이전에 초기화된 기존 프로젝트엔 INDEX가 없음 → read·write 시점에 없으면 만들고 진행
  - `templates/memory_index_template.md` 신규 — 생성 시 단일 소스 (format drift 방지)
  - Phase 1.5(read)·등록 규칙(write)에 "없으면 템플릿에서 생성 후 진행" 추가
  - `layer0_init`도 "빈 표 생성" → "템플릿 복사"로 통일

---

## 예상 조용한 결정

- INDEX 컬럼 구성 / 권장: domains는 `도메인 | 다루는 내용 | 파일 | 업데이트`, roles는 `페르소나 | 기록된 함정 | 파일 | 업데이트`
- 등록 트리거를 detail 3개 섹션 각각에 넣을지, 한 곳에 공통 규칙으로 둘지 / 권장: 각 섹션에 한 줄씩 (해당 작업 흐름에서 바로 보이도록)

---

## 수정 대상 파일

| 파일 경로 | 변경 내용 |
|---------|---------|
| `workspace/memory/INDEX.md` | 신규 생성 — 선별 인덱스 |
| `.mpa-workspace/core/agent_rules.md` | "3. 컨텍스트 선택 로딩"에 INDEX 사전 선별 스텝 |
| `.mpa-workspace/core/agent_rules_detail.md` | 메모리 기록 3개 섹션에 INDEX 등록 스텝 |
| `.mpa-workspace/inject/layer0_init.md` | memory 초안 단계에 INDEX 생성 항목 |
| `.mpa-workspace/.mpa-version` | current_version 갱신 |

## 참고 파일 (수정 없음)

- `workspace/tasks/INDEX.md` — 인덱스 형식·원칙(폴더=primary, INDEX=cache) 참조 기준
- `.mpa-workspace/hooks/dist_sync.py` — dist 자동 미러 (수동 동기화 불필요)

---

## 반례 (이 계획이 실패할 수 있는 시나리오)

- 시나리오 1: domains/roles가 비어 INDEX도 비면 "효과 없는 빈 파일"로 보임 → 등록 규칙이 핵심이고 INDEX는 그 결과물임을 원칙 주석으로 명시 (구현 1단계에 포함)
- 시나리오 2: INDEX가 본체와 드리프트 → "폴더가 정답, INDEX는 캐시" 원칙 명시 + tasks/INDEX 동기화 원칙과 동일 처리 (구현 1단계에 포함)
- 시나리오 3: 매 작업 INDEX 읽기가 추가 비용 → 메모리 불필요 유형(단순 질문·토론)은 제외하도록 소비 시점을 "컨텍스트 선택 로딩"으로 한정 (구현 2단계에 포함)

---

## 검증 체크리스트

- [ ] 정상 경로: 새 도메인 메모리 생성 → INDEX 등록 → 다음 세션이 INDEX로 매치 판단
- [ ] 실패 경로: shared 파일이 INDEX에 잘못 등록되지 않는지 (제외 규칙 동작)
- [ ] 엣지 케이스: domains/roles 빈 상태에서도 규칙·INDEX가 모순 없이 성립

---

## 완료 시 문서 업데이트 대상

- [ ] 없음 (방법론 파일 자체가 대상, docs/ 별도 반영 없음)

---

## 구현 후 발견

| 항목 | 유형 | 발견 맥락 | 처리 경로 |
|------|------|-----------|-----------|
| (결과를 경험한 후 채워짐) | | | |
