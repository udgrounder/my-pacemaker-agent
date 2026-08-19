---
태스크: task_index_maintenance
생성일: 2026-07-29
타입: major
실패비용: major
상태: 완료 승인
승인해시: 158a666483c49f9d
---

# 태스크 계획서: 태스크 INDEX 메모리 정리 정책

**파생 출처:** 없음

---

## PRD

### 에이전트 보고

#### 사용자 결정 필요 (Open Questions)

- 없음

#### 암묵적 결정

- `workspace/tasks/INDEX.md`는 모든 MPA 사용 프로젝트에서 최근 태스크를 빠르게 찾기 위한 참조용 메모리다. `workspace/tasks/done/`은 완료 태스크의 이력 원본으로 유지한다.
- 정책은 설치 대상 프로젝트에 전파하며, MPA를 사용하는 현재 프로젝트의 INDEX에도 같은 형식과 유지보수를 적용한다.
- 완료 승인 시 INDEX의 해당 행을 즉시 제거한다. 태스크 폴더·plan.md·Layer 2 완료 마커는 삭제하거나 이동하지 않는다.
- INDEX에 없는 done 폴더는 정상 이력이며 자동 복구하지 않는다. 전체 정합성 점검은 필요할 때 `tasks/done/` 이력을 직접 확인한다.

#### 에이전트 가정 (Assumptions)

| 가정 | 근거 | 틀렸다면 |
|-----|------|---------|
| INDEX는 active·hold 작업만 담는다. | 사용자가 완료 작업은 INDEX에서 즉시 제거하도록 결정했다. | done 행 보존 정책으로 되돌린다. |
| INDEX 정렬은 `active` → `hold` 순이며 각 그룹은 생성일 내림차순, 같은 날짜에는 태스크명 오름차순이다. | 현재 처리할 작업을 먼저 찾게 한다. | 원하는 정렬 기준으로 교체한다. |

### 요청 원문

> MPA 정책을 수정. task 진행 시 참조 혹은 작성하는 INDEX.md 정책을 수정할 것이다. INDEX.md가 참조용 메모리인데 메모리 정리를 하지 않는다. 오래된(완료일로 부터 3개월 이상된 완료된 작업) 거 정리랑, INDEX 내 task간 정렬을 해야 한다. 현재 완료일이 없는 건 현재 시간을 기준으로 처리해줘.

### 목적

태스크 INDEX가 현재 처리할 active·hold 태스크만 담는 정렬된 참조 메모리로 유지되게 한다.

### 요구사항

- INDEX 표에는 active·hold 행만 둔다.
- 완료 승인 시 해당 INDEX 행을 제거하고 태스크 폴더는 `done/`으로 이동한다.
- 기존 done 행은 정책 적용 시 한 번에 INDEX에서 제거한다.
- INDEX를 참조하거나 작성하는 흐름에서 active·hold 행만 정렬하고 마커를 보존한다.
- 전체 정합성 점검은 필요할 때 `tasks/done/` 이력을 직접 확인하며 INDEX done 행에 의존하지 않는다.
- 현재 프로젝트와 신규 설치 템플릿·설치본 규칙이 같은 정책을 사용한다.

---

## 구현 계획 (Implementation Plan)

### 사전 조사

- INDEX를 읽는 세션 시작·Layer 2와, INDEX를 쓰는 태스크 생성·major 완료·minor 완료 흐름을 확인한다.
- 현재 INDEX의 done 행은 정책 적용 시 INDEX에서 제거하고 done 폴더 이력은 보존한다.

### 구현 단계

- [x] Step 1 — 현재 `workspace/tasks/INDEX.md`에서 모든 done 행과 `완료일` 열을 제거하고 active·hold 행만 정책 순서로 정렬한다. / 이유: INDEX를 현재 처리할 작업만 담는 참조 메모리로 만든다.
- [x] Step 2 — `agent_rules.md`에 INDEX active·hold 전용 정책을 추가한다. 세션 시작과 태스크 생성 시 active·hold 행만 정렬하고, 완료 시 행을 즉시 제거하도록 한다. / 이유: 완료 이력을 INDEX와 done 폴더에 중복 보관하지 않는다.
- [x] Step 3 — major·minor·구현 후 발견의 태스크 생성과 major·minor 완료 지점을 맞춘다. 생성 시 active 행을 등록하고, 완료 승인 후에는 INDEX 행을 제거한 다음 done 폴더로 이동한다. / 이유: INDEX가 현재 작업 목록으로 유지된다.
- [x] Step 4 — `layer2_checkpoint.md`의 INDEX 동기화·점검 규칙을 갱신한다. active/hold 폴더만 INDEX 누락을 복구하고, done 폴더는 이력 원본으로만 확인한다. `[Layer 2 완료]` 마커는 보존한다. / 이유: 완료 이력을 자동 재등록하지 않으면서 전체 점검 경로를 남긴다.
- [x] Step 5 — 신규 설치 템플릿 `dist/workspace/tasks/INDEX.md`과 설치 Runtime 규칙을 active·hold 전용 형식으로 반영한다. / 이유: 신규 설치와 현재 프로젝트가 같은 정책을 사용한다.
- [x] Step 6 — 현재 INDEX의 done 행 제거, active·hold 정렬, 완료 시 행 제거, done 이력 보존, Layer 2 점검 경로, source/dist·설치 Runtime 일치를 회귀 검증한다. / 이유: 참조 메모리 단순화가 이력 손실로 이어지지 않게 한다.

### 예상 조용한 결정

- 완료일 보정과 만료 정리는 INDEX를 처음 참조하거나 작성하는 시점에 한 번의 유지보수 순서로 수행한다. 같은 실행에서 기준일을 고정하고 INDEX 전체를 한 번만 저장한다. / 권장: 날짜 보정 뒤 즉시 만료를 판단해 재실행해도 결과가 유지되게 한다.
- INDEX 하단의 `[Layer 2 완료]` 행은 태스크 표와 분리된 상태 마커로 유지한다. / 권장: 태스크 행만 정렬한다.
- INDEX에 없는 done 폴더는 자동 등록하지 않고, Layer 2 제안은 보존 기간 내 INDEX done 행만 사용한다. / 권장: INDEX를 최근 태스크용 캐시로 일관되게 유지한다.

### 수정 대상 파일

| 파일 경로 | 변경 내용 |
|---------|---------|
| `workspace/tasks/INDEX.md` | 완료일 열 추가, 기존 done 완료일 보정, 정렬 |
| `.mpa-workspace/core/agent_rules.md` | INDEX 유지보수·생성·major/minor 완료 정책 갱신 |
| `.mpa-workspace/inject/layer1_design.md` | 신규 INDEX 행의 완료일 기본값 명시 |
| `.mpa-workspace/inject/layer1_implement.md` | minor 완료 시 완료일 기록 명시 |
| `.mpa-workspace/inject/layer2_checkpoint.md` | done 폴더 미재등록과 마커 보존 규칙 반영 |
| `dist/workspace/tasks/INDEX.md` | 신규 설치용 표 형식·정책 설명 반영 |
| `dist/.mpa-workspace/**` | 설치본 MPA 규칙 동기화 산출물 |
| `.mpa-workspace/.mpa-version` | current_version 갱신 |

### 참고 파일 (수정 없음)

- `.mpa-workspace/personas/mpa_system_designer.md` — MPA 시스템 파일 변경 거버넌스
- `workspace/project_rules.md` — dist 동기화 요구

### 반례 (이 계획이 실패할 수 있는 시나리오)

- 시나리오 1: 정리된 done 행을 Layer 2가 폴더만 보고 다시 INDEX에 넣는다. → Step 4에 포함: done 폴더의 INDEX 누락을 오류로 처리하지 않는다.
- 시나리오 2: 완료일 없는 과거 행을 생성일로 추정해 너무 이르게 삭제한다. → Step 1·2에 포함: 정책 적용 시점의 현재 날짜로만 보정한다.
- 시나리오 3: 정렬 중 `[Layer 2 완료]` 마커가 태스크 행으로 취급돼 사라진다. → Step 4에 포함: 마커를 표 정렬 범위에서 제외한다.
- 시나리오 4: 완료 처리 전에 정렬해 새 done 행이 active 위치에 남는다. → Step 2·3에 포함: 상태와 완료일을 먼저 반영한 뒤 공통 유지보수를 실행한다.
- 시나리오 5: 잘못된 완료일을 가진 행이 자동으로 삭제된다. → Step 2·6에 포함: 형식 오류 행은 보존·경고한다.

---

## 완료 기준 (Definition of Done)

### 검증 체크리스트

- [x] 현재 INDEX에 done 행·완료일 열이 없고 active/hold 행만 남는지 확인한다. — 현재 INDEX 및 정책 회귀 테스트 통과
- [x] 완료 승인 절차가 INDEX 행을 제거하고 done 폴더 이력을 보존하도록 명시됐는지 확인한다. — Runtime 지침 회귀 테스트 통과
- [x] active → hold 순서와 생성일·태스크명 보조 정렬이 적용되는지 확인한다. — Runtime 지침 회귀 테스트 통과
- [x] Layer 2가 done 태스크를 INDEX에 재등록하지 않고 done 이력·마커를 보존하는지 확인한다. — Runtime 지침 회귀 테스트 통과
- [x] 신규 설치본의 INDEX와 Runtime이 active·hold 전용 정책을 포함하는지 확인한다. — 설치 회귀 테스트 통과
- [x] source `.mpa-workspace/`와 `dist/.mpa-workspace/`가 일치하고 전체 회귀 테스트가 통과하는지 확인한다. — 68개 테스트 통과

### 완료 시 문서 업데이트 대상

- 없음 — MPA 실행 규칙과 설치 템플릿이 정본이다.

### 구현 후 발견

| 항목 | 유형 | 발견 맥락 | 처리 경로 |
|------|------|---------|
| (결과를 경험한 후 채워짐) | 조정 / 계획 확장 / 신규 태스크 | 왜 보기 전에는 보이지 않았는가 | plan.md 수정 / INDEX.md 등록 |

**파생된 태스크:**
- (신규 태스크 생성 시 여기에 추가됨)
