## 검토 결과

> 1차 검증(독립 스레드, changelog.md 미참조). **changelog.md는 태스크 폴더에 실제로 존재하지 않는다** (`workspace/tasks/active/20260716_mpa_glossary_and_layering/` 내용: `consistency_check.md`, `critique.md`, `critique_fable5.md`, `plan.md`뿐). 아래 판단은 plan.md 서술(체크박스·"완료:" 문구)을 근거로 삼지 않고, git diff(`8f04cef..HEAD`)와 실제 파일 내용을 직접 읽어 확인한 결과다.

### ✅ 정합성 확인

- `.mpa-workspace/core/glossary.md` 신설 확인. Step 2가 요구한 7개 항목(Zone/Tier 정의, 계획서 vs PRD, plan.md/계획서/플랜/설계서 통용 표현, MPA 계획서 체계 vs Claude Code 네이티브 Plan Mode, GATE 절차 설명, DoR/DoD 대응 관계, 완료 승인 확인(절차) vs 완료 승인(상태) 구분) 전부 실제로 존재함(파일 전체 73줄 직접 확인).
- `templates/plan_template.md`의 헤딩 트리가 plan.md Step 2.5에 명시된 구조(`## PRD` → `### 에이전트 보고` → `#### 사용자 결정 필요/암묵적 결정/에이전트 가정/minor 판단 근거` → `### 요청 원문/목적/요구사항` → `## 구현 계획` → ... → `## 완료 기준` → ...)와 정확히 일치.
- `inject/layer1_design.md`에 "PRD 확정 전 구현 단계 작성 금지" 규칙(122행)과 major용 "1단계 PRD만 작성 → 사용자 제시 → 확인" 2단계 패턴(130~151행)이 실제로 반영됨.
- `code_gate.py`/`plan_hash.py`의 출력 메시지 3곳이 plan.md 표와 글자 단위로 정확히 일치: `"⛔ 계획 승인 기록 복구 필요: ..."`(code_gate.py:194), `"⛔ 계획 재승인 필요: ..."`(code_gate.py:211), `"계획 승인됨: 상태 → 구현 중 / 승인해시: {h}"`(plan_hash.py:208).
- `agent_rules_detail.md`(소스, `.mpa-workspace/` 기준)에서 "## GATE 1 재진입 복구" → "## 계획 승인 재확인"으로 섹션명 변경 확인, 그 안의 트리거 인용문도 새 문자열로 갱신됨. `agent_rules.md` 상단 트리거 표(12행)도 동일 문자열을 정확히 인용.
- `agent_rules.md` 단계 모델 다이어그램의 `⛔G1`/`⛔G2` 토큰이 `⛔계획승인`/`⛔완료승인확인`으로 교체됨(61, 70행) 확인.
- `architecture.md` "파일별 역할" 표에 `core/glossary.md` 행 추가 확인(167행, "disclosed reference" 명시 포함), "게이트 대칭 원칙" 문단의 GATE1/2 언급도 "계획 승인"/"완료 승인 확인"으로 교체됨(40~44행) 확인.
- "완료 인정/불인정" 예시 문단 중복 통합 확인: `agent_rules_detail.md`에 "완료로 인정"/"완료로 인정하지 않음" 블록이 각 1회씩만 존재(348행 섹션 내부), `agent_rules.md`에는 트리거 포인터 문구만 남아 실제 중복 콘텐츠 없음.
- `discussion_mode.md`의 GATE 1/2 언급 2곳이 정확히 "계획 승인"/"완료 승인 확인"으로 교체됨(diff 직접 확인).
- `[작업명]` 플레이스홀더는 `.mpa-workspace/` 전체에서 `[태스크명]`으로 교체 완료(태스크 자체 `consistency_check.md`의 grep 결과와 별도로 재확인 시도 시 표본 파일에서 확인됨).
- `workspace/tasks/done/` 하위 과거 plan.md는 diff에 전혀 등장하지 않음 — 소급 수정 없음 확인.
- `MPA_GATE` 환경변수 이름·`os.environ.get("MPA_GATE", ...)` 호출·`session_start.py:163` 부근의 "코드 수정 게이트" 일반 명사 표현은 그대로 유지됨(코드 주석·docstring 내 "GATE 1"/"GATE 2" 다수 잔존은 glossary.md가 명시한 예외 범위 내로 확인).

### ⚠️ 주의 필요

- **Step 2.7 위치 불일치**: plan.md는 "`agent_rules.md` '작업 생성' 섹션에 GATE1 승인 요청용 평이한 문구 템플릿 추가"라고 명시했으나, 실제로 "계획을 승인하고 구현으로 넘어갈까요?" 문구는 `inject/layer1_design.md`(177, 183, 188행)에만 존재하고 `agent_rules.md`의 "태스크 생성" 섹션에는 어디에도 추가되지 않았다(해당 섹션 전체를 직접 읽어 확인 — "명시적 승인 없이 구현을 시작하지 않는다 (계획 승인, major 전용 — minor는 자동 승인)"라는 기존 문장만 있고 예시 문구가 없음). 기능적으로는 layer1_design.md 경유로 같은 효과를 내지만, plan.md가 지정한 위치와 다르다.
- **Step 6(일관성 점검) 커버리지 부족**: 태스크 폴더의 `consistency_check.md`(서브에이전트 산출물로 추정)는 트리거 표 대조·출력 메시지 대조·`[작업명]` 잔존·glossary 참조 정확성 등은 꼼꼼히 확인했으나, 이번 1차 검증에서 발견된 다음 항목들은 전혀 언급하지 않았다: (a) `workflows/new_feature.md` 등 8개 파일이 Step 1 치환에서 완전히 누락된 사실, (b) `hooks/session_start.py`의 결정 14 미반영, (c) `guidebook.md`/`README.md`의 GATE 표기 미반영(결정 13), (d) `writing_great_skills_review.md` 결론 섹션 미갱신(Step 8), (e) Step 2.7 위치 불일치. 즉 Step 6 자체가 "완료"로 보기엔 점검 범위가 이번 검증보다 좁다.
- **"다음 작업 예측" 헤더/문구 미치환**: `agent_rules.md`(22, 201행 유사), `agent_rules_detail.md`(201, 203행), `layer1_discovery.md`(135행), `layer1_implement.md`(179행), `layer1_design.md`(203행), `layer0_init.md`(179행)에 걸쳐 "다음 작업 예측"이라는 동일한 섹션명/문구가 일관되게 "작업"으로 남아있다. 사용자 결정 1(헤더·본문 전부 "태스크"로 통일, "작업"은 진짜 태스크 아닌 활동에만 한정)의 예외 사유(exploration 등)에 해당하지 않아 보이며, 여러 파일에 걸쳐 같은 표현이 반복되는 것으로 보아 실수로 빠진 고유명사적 헤더로 판단된다. 다만 사용자가 별도로 "다음 작업 예측"을 의도적 예외로 결정했을 가능성도 있어(plan.md에 명시적 언급 없음) 최종 판단은 사용자 확인 필요.

### 🚨 즉시 수정 필요

- **`dist/.mpa-workspace/core/agent_rules_detail.md`가 소스와 동기화되지 않음.** `diff -rq .mpa-workspace dist/.mpa-workspace` 결과 이 파일 단 하나만 실질적으로 다르며, diff 내용을 보면 dist 쪽은 여전히 "## GATE 1 재진입 복구", "작업 재개", `[작업명]` 플레이스홀더, 구버전 "GATE 1 복구 필요"/"GATE 1 재진입 차단" 인용문을 담고 있고 "실패비용 추정 기준"·"완료 인정 판별 기준" 섹션 자체가 없다(소스에는 318, 348행에 존재). plan.md의 "완료 기준 > 검증 체크리스트"가 명시한 "`dist/.mpa-workspace/`와 설치본 `.mpa-workspace/` 간 `diff`가 0인지 확인" 항목이 실패한다.
- **`.mpa-workspace/.mpa-version`의 `current_version`이 갱신되지 않음.** 소스·dist 양쪽 모두 `2026-07-03 16:26:26`으로, 이 태스크(2026-07-16 생성, 오늘 2026-07-21) 이전 값에 그대로 머물러 있다. Step 7 "후반부"가 미착수.
- **`guidebook/guidebook.md`, `README.md`의 GATE 1/2 표기가 전혀 교체되지 않음.** 사용자 결정 13번이 명시적으로 범위를 넓혀 이 두 파일을 수정 대상에 포함시켰고 plan.md "수정 대상 파일" 표에도 두 파일이 등재돼 있으나, git diff(`8f04cef..HEAD`)에 이 두 파일이 전혀 등장하지 않는다. 실제로 다음이 그대로 남아있다:
  - `guidebook.md:711` `⛔GATE1`, `:714` `⛔GATE2`/"GATE 1 자동 승인", `:1318` "11.6 팀 환경에서 GATE 1 승인", `:1320`, `:1328` "GATE 1"
  - `README.md:89` "GATE 1 자동 승인"/"GATE 2", `:95` `⛔GATE1`/`⛔GATE2`, `:264` "GATE 1·2"
  이 태스크가 없애려던 "MPA 내부는 '계획 승인'이라 하는데 사용자 대면 문서는 여전히 'GATE 1'"이라는 정확히 그 분열이 그대로 남아있다.
- **Step 1의 ".mpa-workspace/ 전체" 치환 범위에서 최소 8개 파일이 완전히 누락됨.** `inject/layer2_checkpoint.md`, `core/session_protocol.md`, `workflows/new_feature.md`, `workflows/bug_fix.md`, `workflows/code_review.md`, `workflows/refactoring.md`, `inject/layer1_critique.md`, `templates/minor_plan_template.md` — 이 8개 파일은 8f04cef 시점과 "작업" 출현 횟수가 정확히 동일(diff 자체가 0)하다. plan.md 조사 3이 스스로 ".mpa-workspace/ 전체"·"최소 15개 파일 분포"를 확인해놓고, 실제 치환은 `agent_rules.md`/`agent_rules_detail.md`/`layer1_discovery.md`/`layer1_review.md`/`layer1_implement.md`/`layer1_design.md`/`layer0_init.md`/`team_collaboration.md` 8개 파일에만 이뤄졌다. 다만 이 8개 파일 안의 "작업" 잔존 예시(`역할로 작업한다`, `작업 유형의 특성`, `현재 작업 상태를 커밋`)는 문맥상 결정 A의 "일반 동사"·"작업 워크플로우 유형"에 해당해 유지가 맞을 가능성도 있어, "누락"이라기보다 "검토 자체가 이뤄지지 않았다"는 점이 문제다 — diff가 정확히 0이라는 것은 sed조차 실행되지 않았음을 뜻한다.
- **`hooks/session_start.py`가 결정 14를 전혀 반영하지 않음.** 이 파일도 8f04cef 이후 diff가 0이다. plan.md 결정 14는 다음을 명시적으로 요구했으나 전부 미반영:
  - `:140` `새 작업 시작` → `새 태스크 시작`(치환) — 현재도 `"새 작업 시작"` 그대로.
  - `:146` `해당 태스크 작업 진입 시` → `해당 태스크 진입 시`(삭제) — 현재도 `"해당 태스크 작업 진입 시"` 그대로("태스크 작업"이라는 중복 표현이 그대로 남음).
  - `:154` `진행 중 작업이 없으니` → `진행 중 태스크가 없으니`(치환) — 현재도 `"진행 중 작업이 없으니"` 그대로.
  - `:155`, `:160`은 "유지" 결정대로 손대지 않은 것은 맞으나, 이는 애초에 이 세 곳을 처리했어야 발생하는 "선택적 유지"이지, 파일 전체가 방치된 결과와는 다르다.
- **`workspace/exploration/discussion/writing_great_skills_review.md`의 "결론" 섹션이 갱신되지 않음(Step 8).** 여전히 "GATE 1(사용자 승인) 대기 중"이라는 문구가 그대로 있으나, plan.md 프론트매터상 이미 `승인해시: 7365e56bf3a22aed`가 기록돼 있고 상태가 `구현 중`이다 — 계획 승인은 이미 끝난 지 오래(구현이 상당 부분 진행됨)인데 토론 기록은 "승인 대기 중"이라는 낡은 상태를 그대로 보여준다.

### 📝 조용한 결정 목록

- **결정**: Step 6(일관성 점검)이 서브에이전트로 실행된 것으로 보이는 `consistency_check.md`를 산출했으나, 그 점검 결과의 "🚨 불일치 발견" 항목(`layer1_design.md:188`의 옛 "GATE1" 표현)이 이후 실제로 수정된 흔적이 있다(현재 파일에는 해당 표현 없음). 그러나 같은 문서가 "동기화 대기(문제 아님)"로 분류한 dist 불일치는 그대로 남아있고, 이 검증에서 발견된 8개 미치환 파일·session_start.py·guidebook/README 문제는 이 문서에 전혀 언급이 없다. → **판단: 비가시적 위임.** Step 6 산출물이 "일관성 점검 완료"로 오인될 여지가 있으나 실제로는 Step 1·1.5·7·8의 잔여 작업을 잡아내지 못했다.
- **결정**: Step 2.7의 GATE1 승인 문구를 `agent_rules.md` "태스크 생성" 섹션이 아니라 `inject/layer1_design.md`에만 넣은 것 — plan.md에 이 위치 변경에 대한 언급이 없다. → **판단: 비가시적 위임** (의도적 재배치였다면 plan.md나 changelog에 사유가 남아야 하나 없음; changelog.md 자체가 없어 확인 불가).
- **결정**: `.mpa-version`을 갱신하지 않고 dist 동기화를 부분적으로만(agent_rules_detail.md 제외 전부) 수행한 채 방치 — plan.md "완료 기준"이 이를 필수 검증 항목으로 명시했음에도 태스크가 아직 `구현 중` 상태에서 부분 동기화만 이뤄진 상태로 여러 커밋(9a12e32, 9517cbc)이 쌓임. → **판단: 의도적 위임으로 보임**(완료 전 단계라 아직 안 한 것일 수 있음)이나, plan.md의 Step 순서상 Step 7은 Step 1~6 이후 마지막 단계이므로 나머지 Step들의 미완료와 함께 봐야 할 신호.

### 🔍 Step별 실제 완료 여부

- **Step 1** (전역 "작업"→"태스크" 치환, `.mpa-workspace/` 전체): **부분완료.** `agent_rules.md`(21→5)·`agent_rules_detail.md`(18→4)·`layer1_discovery.md`(4→2)·`layer1_review.md`(10→8)·`layer1_implement.md`(12→5)·`layer1_design.md`(9→7)·`layer0_init.md`(17→4)·`team_collaboration.md`(20→8)는 실제 치환됨(개수 직접 대조). 그러나 `inject/layer2_checkpoint.md`·`core/session_protocol.md`·`workflows/new_feature.md`·`workflows/bug_fix.md`·`workflows/code_review.md`·`workflows/refactoring.md`·`inject/layer1_critique.md`·`templates/minor_plan_template.md` 8개 파일은 8f04cef 대비 "작업" 출현 횟수가 정확히 동일(diff 0) — 전혀 손대지 않음. `hooks/session_start.py`의 결정 14(개별 처리) 3곳도 전혀 반영 안 됨(diff 0).
- **Step 1.5** (GATE1/2 절차·출력 메시지 정리): **부분완료.** `code_gate.py`/`plan_hash.py` 출력 메시지 3곳, `agent_rules_detail.md` 섹션명·인용문, `agent_rules.md` 트리거 표·다이어그램 토큰(⛔G1/⛔G2→⛔계획승인/⛔완료승인확인)은 정확히 반영됨(직접 대조 완료). 그러나 결정 13이 요구한 `guidebook.md`·`README.md`의 GATE 표기 교체는 전혀 이뤄지지 않음(두 파일 모두 diff 자체가 없음, grep으로 GATE1/GATE2/⛔GATE1/⛔GATE2 다수 잔존 확인).
- **Step 2** (`glossary.md` 신설, 7개 항목): **완료.** 파일 존재, 7개 항목 전부 실제 내용으로 확인(직접 Read).
- **Step 2.5** (`plan_template.md`·`layer1_design.md` 갱신): **완료.** 헤딩 구조 일치, PRD 규칙·2단계 패턴 반영 확인.
- **Step 2.7** (`agent_rules.md` "태스크 생성" 섹션에 GATE1 평이한 문구 추가): **미착수(지정 위치 기준).** 문구 자체는 `layer1_design.md`에만 존재하고 plan.md가 지정한 `agent_rules.md` "태스크 생성" 섹션에는 없음(해당 섹션 전문 직접 확인).
- **Step 3** (실패비용·완료인정 섹션 이동+개명): **완료(소스 기준).** `agent_rules_detail.md`에 "## 실패비용 추정 기준"(318행)·"## 완료 인정 판별 기준"(348행) 존재, 중복 통합 확인(각 1회). 단, **dist에는 반영되지 않음**(Step 7 문제로 별도 기재).
- **Step 4** (트리거 표 갱신 — glossary 포인터·두 섹션 강제 트리거): **완료.** `agent_rules.md` 상단 표에 glossary 행(27행)·실패비용 행(24행 유사)·완료인정 행(25행) 존재, 본문에 "반드시 즉시 읽는다" 강제 문구 두 곳 모두 확인.
- **Step 5** (`architecture.md` "파일별 역할" 표에 `core/glossary.md` 행): **완료.** 직접 Read로 확인(167행), "게이트 대칭 원칙" 문단 GATE1/2 교체도 확인.
- **Step 6** (일관성 점검, 서브에이전트 실행): **부분완료.** `consistency_check.md` 산출물 존재로 실행 자체는 확인되나, 점검 범위가 이번 1차 검증에서 드러난 다수 문제(Step 1 미완료 파일 8개, session_start.py, guidebook/README)를 놓쳤다 — 커버리지 부족.
- **Step 7** (dist 동기화 + `.mpa-version` 갱신): **부분완료/미착수.** dist 동기화는 `agent_rules_detail.md` 한 파일만 빼고 나머지는 실제로 동일(diff 0) — 부분완료. `.mpa-version`의 `current_version`은 갱신 안 됨(소스·dist 모두 구버전 값 `2026-07-03 16:26:26`) — 이 부분은 미착수.
- **Step 8** (`writing_great_skills_review.md` 결론 갱신): **미착수.** "결론" 섹션이 여전히 "GATE 1(사용자 승인) 대기 중"이라는 옛 상태를 그대로 담고 있음(직접 Read 확인).
