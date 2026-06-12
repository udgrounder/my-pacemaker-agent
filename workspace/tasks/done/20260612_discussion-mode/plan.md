---
태스크: discussion-mode
생성일: 2026-06-12
타입: major
실패비용: major
상태: 완료 승인
승인해시: 4b49c25c875409b2
---

# 작업 계획서: discussion-mode

**파생 출처:** upgrade-candidates/discussion-mode-routing.md + 20260612_think-more-task-exemption(흡수) — "개발이 아닌 토론 모드" 필요성. multi-agent-utility-discussion이 토론을 개발 minor로 미스라우팅한 사례에서 발견됨.

> **독립 비평 반영:** critique.md 13건 중 유효 항목을 아래에 반영함. 반영 위치는 각 Step·반례에 `[비평]`으로 표기.

---

## 에이전트 보고

### 사용자 결정 필요

- [x] **`principles.md` 등 "확립된 원칙" 문서의 행선지** → **사용자 결정: A** — `workspace/exploration/discussion/`에 그대로 둠(논의의 산물). 운용 중 정착되면 추후 memory로 승격. [비평 ❓1]

### 암묵적 결정 (논의로 확정됨)

- **통합 폴더 = `workspace/exploration/{discussion,research,use_cases}`** — think-more/ 해체. (이름: explore/study/inquiry/discovery 비교 후 사용자가 exploration 확정. discovery는 기존 "구현 후 발견"과 충돌해 탈락)
- **code_gate.py 변경 없음** — `ALLOW_PREFIXES`에 `workspace/`가 이미 있어 `workspace/exploration/` 쓰기는 항상 허용.
- **태스크 면제 = 폴더 기반, 존재 비의존 표현** — "`workspace/exploration/` 내 작업은 Task 미생성. 폴더는 첫 사용 시 생성될 수 있음" — 신규 설치본에 폴더가 없어도 룰이 유효하도록 표현. [비평 🚨2/🔧1]
- **재배치 = 침묵 이동 금지** — 기존 discussion/research/use_cases 배치는 대체로 유지하되, 성격이 안 맞는 문서만 골라 **제안 매핑을 사용자에게 보이고 확인 후** 이동. [비평 ❓1]
- **모드 지속 = 라이브 문서 + 세션 시작 스캔** — 토론은 active 미등록이지만, 세션 시작 루틴이 `exploration/discussion/`의 `진행 중` 마커 문서를 스캔해 현황에 표시(망각 방지 안전망). [비평 🚨4]
- **기록 = 라이브**, 단일 위치 `workspace/exploration/discussion/`.

### 에이전트 가정

| 가정 | 근거 | 틀렸다면 |
|-----|------|---------|
| think-more 문서 대다수는 현 폴더가 적절, 소수만 재분류 | 이미 discussion/research/use_cases 구조 존재 | 전면 재분류면 사용자 확인 단계 확대 |
| dist 동기화는 .mpa-workspace 미러지만 upgrade-candidates/는 독립 디렉터리 | dist에 upgrade-candidates/archive/ 별도 존재 확인 | dist archive 별도 처리 [비평 ⚠️1] |
| settings.local.json의 think-more는 permission 리터럴 경로(코드 참조 아님) | grep allow-rule 캐시 항목 | 갱신 우선순위 낮음, 무해 [비평 ⚠️2] |

---

## 요청 원문

"개발이 아닌 토론 모드(discussion mode) 추가 — 주제를 심도있게 논의하며 의견을 주고받고 과정·결과를 문서로." + "think-more를 workspace로 통합" + 폴더명 `exploration` + "내용도 구조에 맞게 재배치" + "이관 후 그 토론을 재시작".

---

## 목적

비개발 인지 트랙 "토론 모드"를 MPA에 추가하고, think-more/를 `workspace/exploration/`으로 통합(용도별 재배치)한다.

---

## 구현 단계

> 의존성 순서 고정. 폴더/이관 → 룰 → 기능 → 정리.

- [ ] **Step 1 — exploration 폴더 생성 + 재배치 제안·확인·이관**
  - `workspace/exploration/{discussion,research,use_cases}` 생성
  - think-more 전체 문서를 인벤토리해 **제안 매핑 표**(현 위치 → 제안 위치, 이동 사유)를 사용자에게 제시 → 확인 후 mv. 대다수는 현 분류 유지, `principles.md` 등 misfit만 사용자 결정(에이전트 보고) 반영. [비평 ❓1]
  - 이유: 통합을 기회로 구조 정돈, code_gate 마찰 제거
- [ ] **Step 2 — think-more/ 해체**
  - `think-more/README.md` → `workspace/exploration/README.md` 이동 + 내용 갱신, 잔여(.DS_Store) 제거
- [ ] **Step 3 — 깨지는 경로 참조 갱신 (구현 단계, grep=0 목표에 포함)** [비평 🚨3/⚠️3/🔧3]
  - `README.md`: think-more/를 *독립 레이어(설치 안 됨)*로 규정한 **아키텍처 서술(L160 표·L192 트리)을 재작성** — 단순 경로 치환이 아님. exploration이 workspace/ 하위로 흡수됨을 반영
  - `guidebook/guidebook.md` L5 등 think-more/discussion/ **직접 경로** 갱신 (설명 *보강*이 아니라 *깨진 경로* 수정이므로 여기서 처리)
  - `dist/.mpa-workspace/core/agent_rules.md`의 think-more 면제 룰(L184) — Step 7과 함께 갱신 대상임을 명시
  - `.claude/settings.local.json`: permission 리터럴 경로(무해) — 선택적 갱신, 낮은 우선순위
- [ ] **Step 4 — `personas/discussion_partner.md` 신규**
  - 행동: 동조 금지·검증, 가정 표면화, steelman 후 반론, 개발 반사 억제, 확립/열림 구분, 정밀성
  - **기존 비평 페르소나와의 구분 명시**: code_reviewer/plan_critic은 *특정 산출물*을 비평, discussion_partner는 *열린 주제*를 함께 탐구 — 대상이 다름(상속 아님, 별개). [비평 🔧2]
- [ ] **Step 5 — `inject/discussion_mode.md` 신규**
  - 흐름: 테제 명료화 → 다회 의견 교환 → 라이브 기록 → 반복
  - 기록 위치: `workspace/exploration/discussion/[주제].md`, **폴더 없으면 생성**
  - 문서 구조: 테제 / 오간 의견 / 확립된 것 / 열린 질문 / 결론 + **`진행 중`/`종료` 마커**(세션 시작 스캔용)
  - **진입/이탈/핸드오프 판정 규칙 명시** [비평 ❓2]: 토론 중 "만들자"=개발 태스크 핸드오프 제안 / "더 논의하자"=지속 / 단순 질문은 토론 이탈 아님(답 후 토론 복귀). 종료는 사용자 선언 시에만
  - 태스크·게이트 미적용 명시
- [ ] **Step 6 — `core/agent_rules.md §2` 라우팅 + 우선순위 수정** [비평 🚨1 — 치명]
  - **판단 우선순위 1단계(명시적 유형 선언)에 토론 모드 포함**: "논의하자/토론하자/discussion 모드/~에 대해 의견 나누자" 명시 발화는 **2단계(동작 서술→리팩터링) 분류보다 먼저** 토론 모드로 판정. (메모를 키워드 테이블 3단계에 붙이는 것으로는 2단계 충돌을 못 막음)
  - 라우팅 표에도 행 추가 (inject/discussion_mode.md + personas/discussion_partner.md)
- [ ] **Step 7 — `core/agent_rules.md §4 + §3 + 세션 시작 루틴`**
  - §4 면제: think-more/ → `workspace/exploration/`, **존재 비의존 표현**("폴더는 첫 사용 시 생성") [비평 🚨2]
  - §3 로딩 표에 토론 모드 행
  - **세션 시작 루틴**: active 태스크 외에 `exploration/discussion/`의 `진행 중` 마커 문서를 스캔해 현황에 표시 [비평 🚨4]
- [ ] **Step 8 — `upgrade-candidates/discussion-mode-routing.md` archive** (dist엔 사본 없음 확인됨 → source만 처리) [비평 ⚠️1]
- [ ] **Step 9 — 엮인 태스크 정리** [비평 ❓3]
  - discussion-record: 회의록 재배치 확인 → done 보관 + INDEX
  - multi-agent-utility-discussion: 회의록(multi_agent_utility.md)을 `exploration/discussion/`에 재배치 — **이 문서가 단일 진실원**. 토론 모드 재시작 시 **같은 문서에 이어씀**(새 문서 생성 안 함). done의 과거 task plan은 *태스크 관리 기록*일 뿐 토론 내용 아님. → done 보관 + INDEX
  - think-more-task-exemption: §7이 그 룰을 대체 → 흡수, done 보관
- [ ] **Step 10 — dist 동기화 확인 + `.mpa-version` current_version 2026-06-12 확인** (`.mpa-workspace` 미러; upgrade-candidates는 독립 디렉터리이므로 별도 확인)

---

## 수정 대상 파일

| 파일 경로 | 변경 내용 |
|---------|---------|
| `workspace/exploration/` (신규) + 하위 | think-more/ 콘텐츠 재배치 이관 |
| `think-more/` | 제거 |
| `README.md` | **아키텍처 서술 재작성**(think-more 독립 레이어 → workspace/exploration 흡수) |
| `guidebook/guidebook.md` | think-more/discussion/ 깨진 경로 갱신 + (완료 후)토론 모드 설명 |
| `dist/.mpa-workspace/core/agent_rules.md` | §4 think-more 면제 룰(L184) 갱신 (Step 7 미러) |
| `.claude/settings.local.json` | permission 리터럴 경로 (선택적, 낮은 우선순위) |
| `.mpa-workspace/personas/discussion_partner.md` (신규) | 토론 파트너 |
| `.mpa-workspace/inject/discussion_mode.md` (신규) | 토론 모드 흐름·기록·판정·출구 |
| `.mpa-workspace/core/agent_rules.md` | §2 우선순위·라우팅 + §3 로딩 + §4 면제 + 세션 시작 스캔 |
| `.mpa-workspace/upgrade-candidates/discussion-mode-routing.md` | archive |
| dist 미러 + `.mpa-version` | 동기화 + current_version |
| `workspace/tasks/active/{discussion-record, multi-agent-utility-discussion, think-more-task-exemption}` | done 보관 + INDEX |

## 참고 파일 (수정 없음)

- `.mpa-workspace/hooks/code_gate.py` — ALLOW_PREFIXES 확인용 (변경 없음)
- `.mpa-workspace/personas/{mpa_system_designer,code_reviewer,plan_critic}.md` — 페르소나 구분 참조

---

## 반례 (실패 시나리오 — 비평 반영)

- 시나리오 1 [🚨1 해소]: 토론 발화가 §2 2단계에서 리팩터링으로 선점 → **Step 6에서 우선순위 1단계에 토론 명시 발화 포함**으로 해소
- 시나리오 2 [🚨2/🔧1 해소]: 신규 설치본에 exploration/ 부재 → §4 룰을 **존재 비의존 표현**(Step 7) + discussion 흐름 폴더 자동 생성(Step 5)
- 시나리오 3 [🚨3 해소]: README가 think-more를 독립 레이어로 서술 → 경로 치환 아닌 **서술 재작성**(Step 3)
- 시나리오 4 [🚨4 해소]: 토론 재진입 누락 → **세션 시작 스캔**(Step 7)으로 진행 중 토론 표면화
- 시나리오 5: 재배치 기준 모호 → **제안 매핑 사용자 확인**(Step 1) + principles 행선지 사용자 결정
- 시나리오 6 [❓3 해소]: 재시작 이중 진실원 → **단일 문서 이어쓰기**(Step 9)

---

## 검증 체크리스트

- [ ] 정상: "X에 대해 논의하자" → 토론 모드 진입(리팩터링 오라우팅 아님), 태스크 미생성, exploration/discussion/ 라이브 문서
- [ ] 정상: 새 세션 시작 → 진행 중 토론이 현황에 표시됨
- [ ] 실패: 토론 중 "이건 만들자" → 개발 태스크 핸드오프 제안
- [ ] 엣지: `grep -rn think-more` (done 태스크 기록·archive 제외) = 0 — **guidebook·README·dist agent_rules 포함** [비평 🔧3]
- [ ] 엣지: 신규 설치 가정 — exploration/ 없어도 §4 룰 문구가 유효한가
- [ ] 일관성: §2 우선순위·§3·§4 충돌 없음, discovery 등 기존 용어 미충돌, 페르소나 구분 명시됨
- [ ] dist와 설치본 일치(.mpa-workspace), current_version 갱신

---

## 완료 시 문서 업데이트 대상

- [x] `guidebook/guidebook.md` — **토론 모드 설명 추가** 완료 (6장·7장 사이 독립 섹션; 깨진 경로는 Step 3에서 선행 수정) [비평 🔧3]

---

## 구현 후 발견

| 항목 | 유형 | 발견 맥락 | 처리 경로 |
|------|------|-----------|-----------|
| (결과를 경험한 후 채워짐) | | | |
