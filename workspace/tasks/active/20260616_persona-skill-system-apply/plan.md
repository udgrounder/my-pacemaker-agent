---
태스크: persona-skill-system-apply
생성일: 2026-06-16
타입: major
실패비용: major
상태: 설계 완료
승인해시: ""
---

# 작업 계획서: 페르소나·스킬 원칙의 MPA 시스템 적용

**파생 출처:** persona_skill_relationship 토론(R1~14) + 본 설계 세션 추가 정밀화 → guidebook/persona_skill_principles.md → 실제 시스템 적용

---

## 수렴된 모델 (이 계획의 토대)

> 토론(R1~14) 이후 본 설계 세션에서 추가로 정밀화된 결론. **M1~M11 확정, D1~D4 결정 완료.** 독립 비평(critique_design.md) 반영해 보정됨.
> **작업 무게중심 = `.mpa-workspace/`(재사용 방법론 시스템).** 페르소나·워크플로우·inject·agent_rules·도메인 스킬(analysis·programming)이 모두 여기 있다. `workspace/`는 이 프로젝트 인스턴스(memory·tasks)일 뿐 거의 안 건드린다.

- **M1 — 구성 층위 = 내용 3종, 주입은 직교 메커니즘 (재정정):**
  - **[가이드북 정합] 용어 구분:** 이 모델의 **"구성 층위"(내용 종류: 워크플로우/역할/스킬)** 는 가이드북의 **"Layer 0/1/2"(작업 구조)와 다른 개념**이다. 같은 단어 충돌을 피해 — 내용 종류=**구성 층위**, 작업 구조=**Layer**로 문서 전체에서 구별한다.
  - **구성 층위(무엇을 합성·전달하나 — 명사):** ① 워크플로우(메타/작업/단계 3수준) ② 역할(`personas/`) ③ 스킬·도메인(`skills/`).
  - **주입(inject)은 레이어가 아니라 직교 메커니즘(동사)** — 위 내용을 워크플로우 단계에 따라 (새) 쓰레드 컨텍스트에 *싣는 행위*. "재료(워크플로우·역할·스킬) vs 굽기(주입)"처럼 차원이 다르다. 앞선 "4레이어에 주입 나열"은 범주 오류였다.
  - **`inject/` 폴더의 정체 = 단계 워크플로우(내용)** — '주입'은 그 내용에 가하는 행위로 붙은 폴더명일 뿐. 폴더 자체는 워크플로우다(M10·M11에서 규정).
  - **워크플로우가 주(主):** 일의 단계 시퀀스 + 각 단계 자원 바인딩. `workflows/bug_fix.md`가 이미 이 구조. 합성: 워크플로우 단계 → 주입(메커니즘)이 역할+스킬을 적재.
- **M2 — 분석 = 방법 도메인:** analysis는 페르소나에 접어 넣는 게 아니라 *역할 무관 방법 지식의 도메인*이다. 평가 역할은 이 도메인을 **구성적으로 *요구*** 한다(접어넣기 아니라 의존 선언). "역할 종속"은 *내용*이 아니라 *필요*가 역할마다 다른 것이었다.
- **M3 — 절차 ≠ 스킬:** 시퀀싱·오케스트레이션 = 절차(inject) / 한 지점에서 적용하는 방법·지식 = 스킬. `plan_interview`는 절차(잘못 놓인 위치) → inject로. `discovery_classification`은 분류 *방법*(스킬) + 호출 *시점*(절차)로 갈림.
- **M4 — `tech` → `programming`:** 주제 도메인 이름으로 정합화. 폴더명은 영문 유지.
- **M5 — 도메인 두 종류:** 방법 도메인(analysis) / 주제 도메인(programming·finance). 둘 다 스킬, 답하는 것이 "어떻게 따지나" vs "무엇에 관한 지식인가"로 다름.
- **M6 — 저장은 소유(이식성)로 분리 (개념적 소유 ≠ 물리적 저장):** MPA 배포 도메인(analysis, programming 템플릿) → `.mpa-workspace/skills/`. 프로젝트 고유 도메인(finance) → `workspace/`(업그레이드 보존). 도메인은 개념상 나란하나 저장은 소유로 갈린다.
  - **[가이드북 정합] 도메인 관련 저장소는 셋(역할 구분):**

  | 저장소 | 내용 | 성격 |
  |--|--|--|
  | `.mpa-workspace/skills/<도메인>/` | 도메인 **방법·패턴**(어떻게 쓰나) | MPA 배포 |
  | `.mpa-workspace/knowledge/[도메인].md` | 승격된 **검증 사실**(크로스 프로젝트) | upgrade-candidates 승인 후 승격 |
  | `workspace/memory/domains/<도메인>/` | 이 프로젝트의 **규칙·레지스트리**(=기억) | 프로젝트 데이터 |

  → skills=방법 / knowledge=검증 사실 / memory/domains=프로젝트 기억. 플랜이 knowledge/를 누락했었음(검토 발견 2) — 이 표로 정합화.
- **M7 — 스킬은 역할 무관 → 전 역할 합성 + 역할-면 구조:** `programming ⊗ {implementer·code_reviewer·task_designer}` 모두 성립. **[비평 F1 정정] tech는 이미 구현(`layer1_implement.md:29`)+검토(`layer1_review.md:159`) 양쪽에 바인딩됨 — "구현 전용 묶임"은 사실 오류. 진짜 갭은 *설계 단계(`layer1_design`) 미바인딩* 하나뿐.** 도메인 파일은 `[구현자 면]`·`[리뷰어 면]` 등 역할-면으로 구조화(예: spring.md "모르면 물어볼 것"이 이미 암묵적 역할-면).
- **M8 — 워크플로우 = 단계↔자원 바인딩의 단일 소스 (원칙 13 구체화):** 단계별 선언이 흩어짐 — **[비평 F3 정정] 페르소나는 삼중(workflows/ + inject/ + 라우팅 표), 스킬은 이중(workflows/ + inject/ — 라우팅 표는 스킬 미선언)**. `workflows/`를 정본으로 세우고 inject/·라우팅의 중복을 제거(파생). "새 구조 신설"이 아니라 "기존 workflows/를 정본화".

- **M9 — 실행 모델 (런타임에 4레이어가 도는 방식):**
  ```
  요청 → [유형 확인] → workflow 로드
    → workflow가 단계마다 inject로 페르소나·스킬 적재
    → 각 단계가 결과물(파일) 생성
    → 결과물 + 공유 캐시(memory)를 다음 (새 스레드) 단계에 전달
    → 단계 경계엔 사람 노드(게이트·가치 결정)
    → 반복
  ```
  네 가지 디테일이 이 모델을 정확하게 만든다:
  1. **핸드오프 매개 = 결과물(파일), 다음 단계는 새 스레드가 받음** — 대화 맥락을 잇지 않고 파일을 읽는다. 격리(정박 탈출)의 핵심(multi_agent R3·R10). workflows/가 단계마다 "🆕 새 스레드" 명시.
  2. **전달 = 결과물 + 공유 캐시** — `architecture.md`·`contracts.md`가 맥락 재주입 비용을 낮추는 캐시(multi_agent 원칙 11). 결과물만 넘기지 않는다.
  3. **단계 경계에 사람 노드** — GATE 1·가치 결정은 사람(목적론적 권위, R2·R13). 순수 agent→agent 사슬 아님.
  4. **페르소나는 국면 단위 + 구현은 단일 순차** — 한 국면 내내 한 페르소나 유지, 국면 전환 시 교체. write(구현)는 쪼개지 않고 단일 순차(R7~8).

- **M10 — 메타 워크플로우 vs 작업 워크플로우 (구성 층위 최종형):**
  - **메타 워크플로우 = `core/agent_rules.md`** — 작업 워크플로우를 *조합*(라우팅·로드)하고 *잘 돌아가게 통치*(게이트·상태 전이·정합성 점검 layer2). 작업 내용이 아니라 작업 *과정*을 다루는 메타 작업.
  - **무조건 로드 규칙:** 메타 워크플로우는 `CLAUDE.md`의 `@agent_rules.md` import로 **진입(PM) 쓰레드가 세션 시작 시 무조건 로드**(현재 메커니즘). 단 **디스패치된 단계 서브스레드(워커)는 메타 불필요 — 자기 작업 워크플로우만 로드.** "진입=메타 무조건 / 워커=작업 워크플로우만"이 정확한 규칙(M9 PM/서브스레드 연결, 워커에 통치 로직 적재는 낭비).
  - **구성 층위 최종형 (내용):**
    ```
    메타 워크플로우 (agent_rules)            ← 진입 쓰레드 무조건 로드, 오케스트레이션·통치
       └─ 작업 워크플로우 (workflows/)        ← 작업유형 단계 시퀀스
            └─ 단계 워크플로우 (inject/layerN)  ← 재사용 단계 절차 + 자원 바인딩 (개발 작업 도메인)
                 └─ 역할(personas) + 스킬·도메인(skills)  ← 단계에 합성
    ```
  - **주입(inject)은 이 스택의 레이어가 아니다** — 각 단계에서 위 내용을 쓰레드에 *싣는 직교 메커니즘*. `inject/` 폴더는 "주입 레이어"가 아니라 단계 워크플로우(내용). [M1 재정정]
  - **작업 도메인 vs 주제 도메인 명명:** layer1_* = "개발 작업 도메인" 워크플로우(추상 형 `계획→실행→검증`의 개발 구체화). 토론 = `discussion_mode`(다른 작업 도메인). 주제 도메인(금융·프로그래밍)·방법 도메인(분석)은 작업 워크플로우에 합성된다. MPA는 현재 "개발 작업 도메인" 시스템(+토론).

- **M11 — 개발 워크플로우의 두 티어 + inject 4종 분류:**
  - **두 티어:** 전체 흐름(`workflows/` — 작업유형 순서) / 세부 작업(`inject/layer1_*` — 단계 세부 절차). 둘 다 개발 워크플로우.
  - **단, "레이어들"은 한 종류가 아니다** — `inject/` 파일을 역할로 4종 분류:

  | inject 파일 | 역할 | 귀속 |
  |--|--|--|
  | layer1_design/implement/review/critique/discovery | 개발 세부 작업 워크플로우 | 개발 작업 도메인 |
  | layer2_checkpoint | 교차 태스크 정합성 = 통치 | 메타 워크플로우 |
  | layer0_init / layer0_update | 프로젝트 생애주기 | 메타/생애주기 |
  | discussion_mode | 토론 | 다른 작업 도메인 |
  | _agent_execution_priority | inject 우선순위 | 메타 |

  - **재정립 방식 = A(분류 명문화), 저장≠소유:** 파일은 `inject/`에 두되 architecture.md에 역할을 *선언*. 물리적 재배치(B)는 고위험이라 별도 태스크로. layer1_*만 "개발 세부 워크플로우"로 분류(layer2=통치/layer0=생애주기/discussion=타 도메인은 개발 아님).

---

## 범위 경계 (전략 B 결정 — 2026-06-16)

> 웹 스캔([llm_agent_usage_domains.md])으로 확장 우선순위 검증 후, 전략 **B**(토대만, 확장은 후속)로 결정.

**이 태스크가 하는 것 (IN):**
- 일반 코어(메타 워크플로우·합성 모델) ⊥ 개발 작업 도메인의 **개념적 분리를 라벨로 명문화** (M10·M11).
- 개발 작업 도메인 안에서 페르소나·스킬·워크플로우·도메인을 원칙대로 정리.
- 산출물에 "일반 / 개발" 라벨을 달아 미래 확장의 토대를 만든다.

**이 태스크가 하지 않는 것 (OUT — 후속 프로그램):**
- **작업 도메인 팩 "계약(contract)" 정의** — 새 작업 도메인이 갖춰야 할 규격(워크플로우 형+역할+스킬).
- **리서치 작업 도메인 팩 구축** — 확장 최우선 갭이나, 실데이터 없이 계약 추측 위험 → 별도.
- **일반 코어의 물리적 분리** — 파일/폴더를 일반/개발로 *이동*하는 것(M11-B). 본 태스크는 라벨 선언까지만.

**후속 프로그램(별도 태스크로 등록 예정):**
1. 작업 도메인 팩 계약 정의 → 2. 리서치 도메인 팩 구축(일반성 실증) → 3. (선택) 일반 코어 물리 분리.

---

---

## 에이전트 보고

### 사용자 결정 필요

> M1~M11 확정. 아래 D1~D4 결정 완료 (독립 비평 반영).

- [x] **D0 (결정됨) — 페르소나 신설 없음.** `implementer`를 개발자 역할로 인정(이름 유지), `분석가` 미신설(평가 역할로 분해됨). tech/도메인은 전 역할 합성[M7].

- [x] **D1 (결정: 축소) — 프로젝트 고유 주제 도메인 저장 위치** [M6 귀결] → 이 프로젝트는 방법론이라 **고유 주제 도메인 없음**. `workspace/skills/` **신설 안 함**. `workspace/memory/domains/`(프로젝트 *기억* — 도메인 규칙·결정·레지스트리)는 스킬이 아니므로 **그대로 둔다**(흡수·재배선 없음 → **비평 F2 해소**). 미래 규칙만 명시: 프로젝트 고유 주제 도메인이 생기면 `.mpa-workspace/skills/`(재사용)와 분리해 둔다.
  - 선택 A: 기존 `workspace/memory/domains/<도메인>/` 사용 — 현 구조 존중. 명칭이 `skills/`와 `memory/domains/`로 갈림(비대칭).
  - 선택 B: `workspace/skills/<도메인>/` 신설 — `.mpa-workspace/skills/`와 같은 "skills/" 어휘 통일, 두 root(MPA/프로젝트)에 동형. 기존 `memory/domains/`를 여기로 흡수 정리 필요.
  - 에이전트 권장: **B** (사용자의 "모든 도메인=skills/<도메인>" 멘탈 모델 + 기존 workspace↔.mpa-workspace 분리 패턴과 동형).

- [x] **D2 (결정: B) — 배선 정본화(M8: workflows/ 단일 소스)** [재정의] → **별도 후속 태스크**. 이번엔 Phase 1~4(레이어 분리·도메인 정합)까지. Phase 5 제외.
  - 선택 A: 이번 포함 — `workflows/`를 단계↔자원 바인딩 정본으로 세우고, inject/·라우팅 표의 중복 선언 제거 + 페르소나의 분석 도메인 구성적 요구 선언. 런타임 행동 변경, 고위험, **독립 비평 필수**.
  - 선택 B: 별도 후속 태스크 — 이번엔 레이어 분리·도메인 정합(Phase 1~4)까지, 정본화는 후속.
  - 에이전트 권장: **B** (구조 안정화 먼저, 정본화는 영향 범위가 커 독립 비평과 함께 별도로).

- [x] **D3 (결정: A) — 가용 도메인 집합 선언 위치** [기존 D4 유지] → **`project_identity.md`**. 이 프로젝트는 데이터 비움(방법론), 규칙만 정함.
  - 선택 A: `workspace/memory/shared/project_identity.md`(사실, 코드 작업 시 로드). 권장.
  - 선택 B: `workspace/project_rules.md`(항상 로드).
  - 주: 이 프로젝트(방법론)는 가용 주제 도메인이 사실상 없음 → **규칙만 정하고 데이터는 비움**. 다른 프로젝트 도입 시 실증.

- [x] **D4 (결정: A) — `discovery_classification` 처리** [M3 회색지대] → 분류 **방법=스킬 유지**(분석 도메인), **호출 시점=`layer1_discovery` 절차**가 담당.
  - 선택 A: 분류 *방법*은 스킬로 유지(분석 도메인), 호출은 `layer1_discovery` 절차가. 권장.
  - 선택 B: 절차로 흡수(inject).

### 암묵적 결정

- 변경은 설치본 `.mpa-workspace/`에서 하고 `dist/`로 동기화(project_rules·architecture). dist 직접 편집 안 함.
- `programming` 도메인 파일의 *템플릿*(버전 미정 골격)은 MPA 배포, *채워진 값*(이 프로젝트의 Spring 버전 등)은 프로젝트 고유 → 채운 값은 D1 위치로.
- guidebook/persona_skill_principles.md(설명 레이어)는 이번 변경 대상 아님. 대상은 실행 레이어(`personas`·`skills`·`inject`·`architecture.md`).

### 에이전트 가정

| 가정 | 근거 | 틀렸다면 |
|-----|------|---------|
| 사용자는 전체 적용을 원함(단일 폴더 아님) | "실제 시스템에 적용 및 보완" 발화 | 범위를 한 Phase로 축소 |
| 배선 통합(D2)은 위험이 커 분리가 나음 | 모든 세션 행동에 영향 | D2=A 시 한 태스크로 통합 |
| 이 프로젝트엔 주제 도메인 데이터가 거의 없음 | 방법론 프로젝트 | 구체 예시 필요 시 추가 |

---

## 요청 원문

"그럼 실제 현재 시스템에 적용 및 보완 방법에 대해서 계획을 작성하자" + 후속 정밀화(분석가 불요/개발자=implementer / 분석=도메인 / 절차·스킬 분리 / tech→programming / finance=프로젝트 도메인).

---

## 목적

수렴된 모델(M1~M11)을 **`.mpa-workspace/`(재사용 방법론 시스템)** 구조·규칙에 반영해, 워크플로우/주입/역할/스킬·도메인 레이어를 분리하고 도메인 합성 구조를 정합화한다. (`workspace/`쪽은 architecture.md 명문화 + project_identity 규칙 정도 — 무게중심은 `.mpa-workspace/`.)

---

## 요구사항

1. 네 레이어(워크플로우/주입/역할/스킬·도메인) 분리 + 워크플로우 일차성을 시스템이 참조 가능하게 명문화. [M1·M8]
2. 분석을 방법 도메인으로 인정, 평가 페르소나가 "구성적 요구"를 선언. [M2]
3. 절차/스킬 분리 — `plan_interview`를 inject로 이동. [M3]
4. `skills/tech/` → `skills/programming/` 개명 + 역할-면 구조 도입. [M4·M7]
5. 도메인 저장을 소유로 분리하는 규칙 확정(MPA skills vs 프로젝트 도메인 위치). [M5·M6·D1]
6. tech/도메인 스킬을 전 역할 합성으로 해제(구현 전용 묶임 제거). [M7]
7. 가용 도메인 집합 선언 위치 규칙 확정. [D3]
8. 페르소나 인벤토리 현행 유지(신설 없음). [D0]

---

## 구현 단계 (위험 오름차순)

> 독립 단위가 많아 분리 가능. D2 결정이 Phase 5 포함/분리를 가른다.

**Phase 1 — 명문화 (저위험, 행동 변경 없음)**
- [ ] Step 1 — `architecture.md`에 **구성 층위 최종형**(메타/작업/단계 워크플로우 / 역할 / 스킬·도메인) + "워크플로우 일차성" + "구성 층위≠Layer 용어 구분" + "도메인(작업/주제/방법)·도메인 3저장소" + "저장≠소유" 결정 추가. [M1·M5·M6·M8·M10]
- [ ] Step 1b — `architecture.md`에 **실행 모델**(M9 런타임 트레이스 + 네 디테일: 파일 핸드오프·캐시·사람 노드·국면 단위 페르소나) + **로드 규칙**(진입 쓰레드=메타 워크플로우 무조건 / 워커=작업 워크플로우만) 추가. [M9·M10]
- [ ] Step 2 — `architecture.md` "파일별 역할" 표 갱신(agent_rules=메타 워크플로우, workflows=작업 워크플로우 정본, inject=단계 워크플로우, skills=도메인). **[비평 V2] 기존 평면 표를 구성 층위 위계로 *대체*(병기 아님 — 단일 소스).**
- [ ] Step 2b — [M11] `architecture.md`에 inject 4종 분류(개발 세부 / 메타 통치 / 생애주기 / 타 도메인) 명문화. 물리 이동 없이 역할 선언만(저장≠소유).

**Phase 2 — 절차/스킬 분리 (중위험)** [M3]
- [ ] Step 3 — `plan_interview`를 `skills/analysis/`에서 inject 절차로 이동(예: `inject/plan_interview.md`). **[비평 A1] `layer1_design.md` 내 참조 3곳(line 36·59·171) 모두 갱신** — 특히 minor 분기(59)·GATE1 직전(171) 누락 주의.
- [ ] Step 4 — `discovery_classification`은 D4 결정대로 처리.
- [ ] Step 5 — 남은 분석 렌즈 4개(counterexample·silent_decision·dependency·path_tracing)를 "분석 방법 도메인"으로 확정(폴더 유지, 역할 표기 정리).

**Phase 3 — 도메인 정합화 (중위험)** [M4·M5·M6·M7]
- [ ] Step 6 — `skills/tech/` → `skills/programming/` 개명(mv) + 참조 경로 일괄 갱신.
- [ ] Step 7 — `programming/_template.md`에 역할-면 섹션 형식 정의 → 기존 4개 파일 적용. **[비평 V3] 판정 기준:** 기존 4파일(nodejs·python·react·spring)은 *단일 면(공통 사실)으로 시작*; 역할별로 명확히 갈리는 내용(예: spring "모르면 물어볼 것"=설계/구현 면)이 있을 때만 면 태그 도입.
- [ ] Step 8 — [D1 축소] 프로젝트 고유 주제 도메인 *규칙*만 명시(미래용): 생기면 `.mpa-workspace/skills/`(재사용)와 분리. `workspace/skills/` 신설·`memory/domains/` 변경 **없음**.
- [ ] Step 8b — [비평 F1] `layer1_design.md`에 tech/도메인 스킬 참조 추가 — **설계 단계 미바인딩 해소**(가산적·저위험). 검토(`layer1_review:159`)·구현(`layer1_implement:29`)은 이미 바인딩됨 → 건드리지 않음.

**Phase 4 — 페르소나 의존 선언 (중위험)** [M2]
- [ ] Step 9 — 평가 페르소나(code_reviewer·plan_critic·architect·integration_auditor)에 "구성적 요구 도메인" 선언 섹션 **추가(가산)**. **[비평 A2] 기존 inject의 분석 스킬 직접 참조(예: `layer2_checkpoint:31-34`)는 이번엔 유지** — 제거(이관)는 단일 소스화이므로 Phase 5(후속). 선언↔참조가 일시 이중화되나 정본화에서 정리.

**Phase 5 — 배선 정본화 (제외 — D2=B 확정, 후속 태스크)** [M8·원칙 13]
> **[비평 S1] D2=B로 이번 범위에서 제외.** 아래는 후속 프로그램으로 이관. 단 F1의 *설계 단계 바인딩*(원래 Step 11의 일부)은 Phase 3 **Step 8b**로 끌어와 이번에 처리 — 죽은 단계로 방치하지 않음.
- ~~Step 10~~ → **후속:** workflows/ 정본화 + inject/·라우팅 중복 제거 + analysis 직접 참조의 페르소나 선언 이관. 독립 비평 필수.
- ~~Step 11~~ → 검토·구현 바인딩은 이미 존재(F1), 설계 바인딩은 **Step 8b로 이동**.

**Phase 6 — 규칙 확정 (저위험)** [D3]
- [ ] Step 12 — 가용 도메인 집합 선언 위치를 `architecture.md`/`layer1_design.md`에 규칙으로 명시.

**Phase 7 — 가이드북 정합 (저위험, 문서) [검토 반영]**
- [ ] Step 12b — `guidebook.md` 5.2 디렉토리 트리 갱신: `tech`→`programming`, `plan_interview`를 inject로, inject 4종 분류(M11) 반영. 6장 "3 Layer"와의 인접 정합 확인.
- [ ] Step 12c — `guidebook.md` 용어정의(부록 C)에 **"구성 층위 vs Layer" 구분** + 합성(페르소나⊗스킬)·도메인 3저장소·주입=메커니즘 용어 추가.
- [ ] Step 12d — `guidebook/persona_skill_principles.md` **전면 개정** — M8~M11·주입 정정·도메인 3저장소(knowledge 포함)·F1 교정·용어("구성 층위") 반영(현재 R1~14 시점이라 stale).

**공통 마무리**
- [ ] Step 13 — mpa_system_designer 일관성 점검. **[비평 S3] grep 패턴 명시:** `skills/tech`(개명 후 0), `skills/programming`, `plan_interview`(이동 후 경로 일관), `discovery_classification`. 개명·이동 누락 0 확인(설치본+dist 양쪽).
- [ ] Step 14 — `dist/` 동기화 + `.mpa-workspace/.mpa-version` current_version 갱신. **[비평 V1] tech→programming 폴더 개명의 dist 처리:** 설치본 mv 후 dist_sync가 신규 폴더 미러 — 구 `dist/.mpa-workspace/skills/tech/`가 자동 제거 안 되면 동기화 산물로서 수동 정리(dist 직접편집 아님). 동기화 메커니즘의 rename 처리 여부를 Step 6 착수 전 확인.

---

## 예상 조용한 결정

- 역할-면 표기법 — 권장: 기존 spring.md "모르면 물어볼 것"과 호환되는 헤더 섹션(`## [구현자 면]`).
- 페르소나 "도메인 의존 선언" 섹션 위치 — 권장: 신규 섹션("요구 도메인").
- plan_interview 이동 후 파일명 — 권장: `inject/plan_interview.md`(절차임을 위치로 표현).

---

## 수정 대상 파일

| 파일 경로 | 변경 내용 | Phase |
|---------|---------|------|
| `workspace/memory/shared/architecture.md` | 3레이어·도메인·저장≠소유 결정 + 파일별 역할 표 | 1 |
| `.mpa-workspace/skills/analysis/plan_interview.md` | inject 절차로 이동 | 2 |
| `.mpa-workspace/skills/analysis/discovery_classification.md` | D4대로 처리 | 2 |
| `.mpa-workspace/skills/analysis/*` (렌즈 4) | 분석 방법 도메인으로 정리 | 2 |
| `.mpa-workspace/skills/tech/` → `programming/` | 개명 + 역할-면 + 참조 경로 갱신 | 3 |
| `.mpa-workspace/inject/layer1_design.md` | [비평 F1] 설계 단계 tech/도메인 참조 추가 | 3(8b) |
| ~~`workspace/skills/`~~ · `memory/domains/` | [D1 축소] 신설/변경 **없음** | — |
| `.mpa-workspace/personas/{code_reviewer,plan_critic,architect,integration_auditor}.md` | 요구 도메인 선언 | 4 |
| `.mpa-workspace/inject/{layer1_design,layer1_implement,layer1_review,layer1_discovery}.md` | 참조 갱신(절차 이동·도메인 합성) | 2·5 |
| `.mpa-workspace/core/agent_rules*.md` | 라우팅/주입 규칙 정합 | 5·6 |
| `dist/.mpa-workspace/**` · `.mpa-version` | 동기화·버전 | 마무리 |

## 참고 파일 (수정 없음)

- `guidebook/persona_skill_principles.md` — 원칙 단일 소스 (변경 후 부록 미결 해소 표기 가능)
- `workspace/exploration/discussion/persona_skill_relationship.md` — 근거
- `guidebook/multi_agent_principles.md` — 주입/입도 교차참조

---

## 반례 (이 계획이 실패할 수 있는 시나리오)

- 시나리오 1: **Phase 5 배선 변경이 기존 세션 동작을 깨뜨림**(페르소나 의존 선언 누락 경로에서 분석 도메인 미적재) → D2=B(분리)로 위험 격리, 포함 시 독립 비평 필수. (사용자 판단 = D2)
- 시나리오 2: **`tech`→`programming` 개명 시 dist·설치본·참조 경로 누락** → Step 13 grep 검증으로 흡수.
- 시나리오 3: **finance를 `.mpa-workspace/skills/`에 두면 업그레이드 때 소실** → M6 규칙으로 차단(프로젝트 도메인은 workspace). 이 반례가 D1을 강제하는 이유.
- 시나리오 4: **역할-면 도입 과설계**(단순 도메인 파일 비대) → Step 7에서 면 1개면 태그 생략.
- ~~시나리오 5: memory/domains와 workspace/skills 중복~~ → **[비평 F2 해소] D1 축소로 workspace/skills 신설 안 함 + memory/domains 불변 → 중복·고아화 없음.**

---

## 검증 체크리스트

- [ ] 정상 경로: 변경 후 설계/구현/검토 진입 시 역할+도메인 합성이 끊기지 않음
- [ ] 실패 경로: 페르소나 도메인 선언 누락 시 fallback 정의됨
- [ ] 엣지 케이스: 역할-면 1개 도메인 / 가용 도메인 0개 프로젝트 / 개명 후 잔존 참조 0

---

## 완료 시 문서 업데이트 대상

- [ ] `workspace/memory/shared/architecture.md` — Phase 1에서 반영
- [ ] `guidebook/guidebook.md` — 5.2 트리(tech→programming·plan_interview 이동·inject 분류) + 용어정의 C(구성 층위/Layer 구분·합성·도메인 3저장소·주입=메커니즘) [Phase 7]
- [ ] `guidebook/persona_skill_principles.md` — **전면 개정**(M8~M11·주입 정정·knowledge 포함 도메인 3저장소·F1·용어). 부록 미결(분석 재배치·tech 개명·도메인 위치)도 해소 표기 [Phase 7]

---

## 구현 후 발견

| 항목 | 유형 | 발견 맥락 | 처리 경로 |
|------|------|-----------|-----------|
| (결과 경험 후 채워짐) | 조정 / 계획 확장 / 신규 태스크 | | |
