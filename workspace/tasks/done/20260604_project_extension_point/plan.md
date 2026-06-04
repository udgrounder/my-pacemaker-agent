# 태스크: 프로젝트 확장 지점 구축
**상태:** 구현 완료  
**목적:** `.mpa-workspace/`를 건드리지 않고 `workspace/memory/`에서 MPA 동작을 확장할 수 있는 공식 메커니즘을 만든다

---

## 에이전트 보고

### 사용자 결정 필요

- [x] **`project_rules.md` 위치** → `workspace/project_rules.md` (memory/ 밖, 눈에 띄는 위치)
- [x] **페르소나 확장** → 이번 범위 제외. 사용하는 에이전트에 맡김
- [x] **dist/ 불일치 감지** → 세션 시작 제외. `layer0_update.md` 업그레이드 시에만 감지

### 에이전트 가정
| 가정 | 근거 | 틀렸을 때 영향 |
|------|------|--------------|
| inject 파일에 project_rules.md 읽기를 추가하는 것이 "단 한 번의 수정"으로 충분하다 | 모든 세션이 inject 파일을 통해 진입함 | 직접 진입 경로가 있으면 추가 수정 필요 |
| project_rules.md는 "없어도 동작" 방식이어야 한다 | 신규 프로젝트에서 이 파일이 없을 수 있음 | 필수화하면 기존 설치 프로젝트에서 에러 가능 |

---

## 수정 대상 파일

**신규 생성:**
- `dist/.mpa-workspace/templates/project_rules_template.md` — 프로젝트 rules 파일 템플릿
- `workspace/memory/shared/project_rules.md` — 이 프로젝트용 rules 파일 (초안)

**수정:**
- `dist/.mpa-workspace/core/agent_rules.md` — 세션 시작 시 project_rules.md 읽기 추가 (+ 불일치 감지 선택 A 시)
- `dist/.mpa-workspace/inject/layer1_design.md` — "작업 시작 전 읽을 파일" 목록에 추가
- `dist/.mpa-workspace/inject/layer1_implement.md` — 동일
- `dist/.mpa-workspace/inject/layer0_init.md` — 초기화 시 project_rules.md 생성 안내
- `dist/.mpa-workspace/inject/layer0_update.md` — 업그레이드 시 직접 수정 감지 + 이전 안내

---

## `project_rules.md` 포함 가능한 내용 (설계)

```markdown
## 라우팅 힌트
# "배포해줘", "릴리즈" → 새 기능 설계로 처리
# 프로젝트 고유 발화 패턴과 처리 유형을 정의한다

## 기본 자율성 레벨 오버라이드
# 이 프로젝트에서 기본 자율성 레벨: 2 (초안)

## 프로젝트 고유 금지 패턴
# 이 프로젝트에서 절대 하지 말아야 할 것들

## 프로젝트 고유 행동 규칙
# agent_rules.md의 규칙을 프로젝트 맥락에 맞게 보완하는 내용
```

---

## 구현 단계

- [ ] **Step 1** — 사용자 결정 항목 확정
- [ ] **Step 2** — `project_rules_template.md` 신규 작성
- [ ] **Step 3** — `workspace/memory/shared/project_rules.md` 이 프로젝트용 초안 작성
- [ ] **Step 4** — `agent_rules.md` 세션 시작 루틴에 project_rules.md 읽기 추가
- [ ] **Step 5** — `layer1_design.md`, `layer1_implement.md` 읽기 목록 추가
- [ ] **Step 6** — `layer0_init.md` 초기화 시 project_rules.md 생성 안내 추가
- [ ] **Step 7** — `layer0_update.md` 직접 수정 감지 및 이전 플로우 추가
- [ ] **Step 8** — 설치본 동기화

---

## 검증 체크리스트

- [ ] project_rules.md 없어도 에이전트가 정상 동작하는가
- [ ] project_rules.md에 라우팅 힌트 추가 시 에이전트가 반영하는가
- [ ] 신규 프로젝트 초기화 시 project_rules.md가 안내되는가
- [ ] 업그레이드 시 직접 수정 감지 후 upgrade-candidates 이전 흐름이 동작하는가

---

## 반례

- project_rules.md의 라우팅 힌트가 agent_rules.md의 기본 라우팅과 충돌 시 → project_rules.md를 우선한다고 명시 필요
- project_rules.md 파일이 커지면 맥락 낭비 → "간결하게 유지" 가이드라인 필요
