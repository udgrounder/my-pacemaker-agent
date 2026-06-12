# my pacemaker agent

> **상위 원칙:** LLM의 한계는 주어진 것이다. 구조는 설계하는 것이다.

## 빠른 설치

`install.md`를 참조하도록 설정된 agent에게 이렇게 요청하면 된다.

```
@install.md 설치해줘
```

Agent가 `install.md`의 절차에 따라 프로젝트 경로와 사용할 agent를 확인한 뒤 알아서 설치한다. 이미 설치된 프로젝트면 업그레이드 모드로 자동 처리한다.  
→ 옵션과 설치 결과 등 자세한 내용은 아래 [설치](#설치) 참조.

---

## 왜 만들었나

AI 서비스 회사들은 더 나은 결과를 위해 agent와 개발 도구를 **끊임없이 업그레이드하고 개선해 내놓는다.** 모델은 더 똑똑해지고, 도구는 더 강력해진다. 이렇게 빠르게 좋아지는 도구를 **적극적으로 쓰는 것**이 가장 큰 이득이다.

그런데 도구가 좋아질수록 한 가지 문제가 또렷해진다. AI agent는 **자신감 있게 틀리고, 틀렸다는 신호를 주지 않는다.** 모델이 강력할수록 그럴듯한 결과물이 나오고, 그럴듯할수록 잘못된 결정이 조용히 묻혀 들어간다. "AI를 더 잘 쓰는 법"만으로는 이 간극이 메워지지 않는다.

**my pacemaker agent**는 이 간극을 메우려고 만든 결과물이다. 끊임없이 좋아지는 agent와 개발 도구를 **제대로 활용하도록 안내하는 가이드**이자, 사용자가 **하고 싶은 일을 끝까지 해내도록 페이스를 잡아주는 페이스메이커**다.

> 마라톤의 페이스메이커는 대신 뛰어주지 않는다. 다만 페이스를 잡아 주자가 목표에 도달하게 돕는다.  
> **my pacemaker agent**도 대신 결정하거나 대신 책임지지 않는다. 다만 **협업 구조를 잡아 주어, 좋은 도구가 제 성능을 내고 사용자가 원하는 결과에 닿게** 한다.

사용자의 의도는 처음부터 완성돼 있지 않다 — 무엇을 원하는지는 결과물을 보면서 또렷해진다. 그래서 이 도구는 한 번에 정답을 맞히려 하기보다, 사용자가 차이를 확인하고 다시 전달하는 **보정의 반복**이 잘 돌아가도록 돕는다. (자세한 모델은 가이드북 4.0 참조)

구체적으로는 — 검증을 설계로 강제하고, AI가 조용히 내린 결정을 드러내고, 프로젝트의 기억이 세션마다 사라지지 않게 한다. 모델이 바뀌거나 업그레이드되어도 안정적으로 작동하도록, 특정 모델의 해석에 기대지 않는 구조를 지향한다.

> ⚠️ 계속 작업 중입니다. 작동하지만 완벽함을 보장하지는 않습니다.

→ 실용 안내서: [`guidebook/guidebook.md`](guidebook/guidebook.md)

---

## 가이드북 소개

이 README가 "무엇을, 어떻게 설치·사용하는가"를 다룬다면, [`guidebook/guidebook.md`](guidebook/guidebook.md)는 그 뒤의 **"왜 이렇게 일하는가"**를 처음부터 끝까지 설명하는 실용 안내서다. AI agent와의 협업이 왜 자꾸 어긋나는지부터, 그것을 구조로 푸는 방법과 한계까지 순서대로 읽도록 설계돼 있다.

| 부 | 다루는 질문 |
|----|-----------|
| 1부. 왜 필요한가 | LLM은 어떤 존재이고, 왜 자신감 있게 틀리는가 |
| 2부. 어떻게 생각해야 하는가 | 협업 사고방식을 바꾸는 10개의 관점 |
| 3부. 체계란 무엇인가 | 협업 철학을 파일 구조로 인코딩한다는 것 |
| 4부. 어떻게 일하는가 | 3 Layer 워크플로우 · inject · 페르소나 · 스킬 |
| 5부. 어떻게 시작하는가 | 설치와 세션 연속성 운영 · 팀 협업 |
| 6부. 어떻게 발전시키는가 | 발견을 방법론으로 끌어올리는 개선 파이프라인 |
| 7부. 무엇을 조심해야 하는가 | 이 방식이 풀 수 없는 한계(네 역설) |
| 부록 | 빠른 시작 · 체크리스트 · 용어집 · 분석 도구 |

> **읽는 순서:** 철학부터 보려면 1부, 구조와 실용이 먼저 궁금하면 3부, 일단 써보고 싶으면 **부록 E(빠른 시작)**부터 시작해도 된다.

---

## 설치

설치의 진입점은 `install.md`다. agent가 이 문서를 읽고 질의응답 절차를 거쳐 직접 `install.py`를 실행한다 — 사용자가 스크립트를 직접 돌리지 않는다.

```
@install.md 설치해줘
```

agent가 진행하는 절차:

1. 프로젝트 경로 확인
2. 사용할 agent 결정 — 프로젝트 폴더를 보고 자동 감지한 뒤 사용자 확인
3. `.mpa-workspace/` 존재 여부로 신규 설치 / 업그레이드 자동 판단
4. 수집한 정보를 요약해 알린 뒤 설치 실행

**지원 agent:** `claude`(CLAUDE.md) · `codex`(AGENTS.md) · `antigravity`(GEMINI.md) · `openagent`

설치되면 프로젝트에 `.mpa-workspace/`(방법론 파일)와 `workspace/`(프로젝트 데이터 골격)가 생기고, 선택한 agent의 진입점이 루트 설정 파일에 추가된다. 자세한 절차와 옵션은 [`install.md`](install.md), 운영 맥락은 가이드북 9장을 참조한다.

---

## 사용 방법

설치된 프로젝트에서 agent에게 자연어로 작업을 요청하면 된다.

```
[하고싶은 작업] 태스크 생성해줘
```

Agent가 요청의 실패 비용을 먼저 판단한 뒤 작업 흐름을 고른다.

- `minor`: 최소 `plan.md`를 만들고 `plan_hash.py approve`를 자동 실행한다(GATE 1 자동 승인). approve가 상태를 `구현 중`으로 전환하고 `승인해시`를 기록한다. 구현 완료 후 보고하고, 사용자 확인(GATE 2)을 거쳐 `done` 처리한다 — 자동 완료는 없다.
- `major` 또는 `critical`: `plan.md`를 작성해 사용자 검토를 요청한다. 사용자가 승인하면 `plan_hash.py approve`를 실행한다 — 이 명령이 상태를 `설계 완료 → 구현 중`으로 원자적으로 전환하고 `승인해시`를 기록한다.

소스 수정 게이트는 별도 승인 파일을 쓰지 않는다. `workspace/tasks/active/[작업명]/plan.md`의 YAML 프론트매터가 기준이다.

```
상태: 설계 중 → 설계 완료 ⛔GATE1 → 구현 중 → 검증 중 → 테스트 중 → 검토 완료 ⛔GATE2 → 완료 승인 → done
승인해시: [plan.md 본문 해시]
```

`구현 중` 상태인 active 태스크가 있어야 소스 수정이 허용되고, `완료 승인` 상태가 되어야 `active/`에서 `done/`으로 이동할 수 있다.

**예시:**
```
로그인 기능 태스크 생성해줘
결제 API 연동 버그 수정 태스크 생성해줘
사용자 목록 페이지 리팩토링 태스크 생성해줘
```

### 작업 재개

중단된 작업을 다시 시작할 때는 작업명을 언급하거나, 진행 중인 작업이 하나뿐이면 그냥 이어달라고 하면 된다.

```
[작업명] 이어서 진행해줘
```

Agent가 `workspace/tasks/active/`에서 해당 태스크의 `plan.md`와 `changelog.md`를 읽고 중단된 지점부터 재개한다.

**예시:**
```
로그인 기능 이어서 진행해줘
어디까지 했어?
이전 작업 계속해줘
```

---

## 3레벨 구조

페이스메이커가 일관된 페이스를 잡으려면, "왜 이렇게 일하는가 → 어떻게 일하는가 → 이 프로젝트는 무엇인가"가 분리돼 있어야 한다. 이 도구는 그 세 레벨로 구성된다. 각 레벨은 상위 레벨의 산출물이다.

```
레벨 0: 왜 (Why)        ← AI 협업의 기본 원칙
  원칙                     출처(설계 사고): workspace/exploration/ (이 레포의 탐구 공간)
  ↓ 근거 제공              요약(운용): .mpa-workspace/core/principles.md
                           변경: 협업 방식의 근본이 바뀔 때

레벨 1: 어떻게 (How)    ← 페이스메이커를 움직이는 방법론 (이 도구의 본체)
  .mpa-workspace/          페르소나·스킬·inject·워크플로우
  ↓ 템플릿 제공            변경: 방법론이 개선될 때 (모든 프로젝트에 영향)

레벨 2: 무엇을 (What)   ← 이 프로젝트의 실제 데이터
  workspace/               메모리·태스크·문서
                           변경: 프로젝트가 진행될 때 (이 프로젝트에만 영향)
```

**레벨 구분의 의미:**  
이 도구는 "프로젝트마다 쓸 작업 방식을 만들어 주는 도구"다.  
레벨 1(`.mpa-workspace/`)을 수정하면 모든 프로젝트에 영향을 준다.  
레벨 2(`workspace/`)를 수정하면 해당 프로젝트에만 영향을 준다.  
이 분리 덕분에 도구·방법론이 업그레이드되어도 프로젝트 데이터가 흔들리지 않는다.

---

## 구조 원칙

| | 레벨 0 (원칙) | 레벨 1 (`.mpa-workspace/`) | 레벨 2 (`workspace/`) |
|--|---------------------|------------------|---------------------|
| 질문 | 왜 이렇게 일하는가 | 어떻게 일하는가 | 이 프로젝트는 무엇인가 |
| 내용 | 기본 원칙, 판단 기준 | 방법, 절차, 템플릿 | 프로젝트 데이터 |
| 위치 | `workspace/exploration/` · `core/principles.md` | `.mpa-workspace/` | `workspace/` |
| 변경 주체 | 팀 논의 | 방법론 설계자 | 프로젝트 팀(agent) |
| 재사용 | 모든 방법론의 근거 | 모든 프로젝트 공통 | 프로젝트마다 별도 |

---

## 전체 구조

```
my-pacemaker-agent/                   ← 마스터 레포 (git)
│
├── dist/                             ← 설치 소스 (프로젝트에 복사되는 파일들)
│   │
│   ├── .mpa-workspace/               ← 방법론 스냅샷 (복사 소스)
│   │   ├── core/                         ← 원칙과 프로토콜 (principles / agent_rules / session_protocol)
│   │   ├── personas/                     ← agent 역할 정의 (WHO)
│   │   ├── skills/                       ← agent 능력 정의 (WHAT IT KNOWS)
│   │   ├── inject/                       ← 세션 패키지
│   │   ├── hooks/                         ← agent 가드레일 (세션시작 주입·종료 리마인드 + 코드수정 게이트 — 하드 차단은 게이트뿐)
│   │   ├── knowledge/                     ← 검증된 범용 도메인 지식
│   │   ├── workflows/                    ← 작업 유형별 세션 시퀀스
│   │   ├── templates/                    ← 파일 생성용 템플릿 (plan/changelog/shared 등)
│   │   └── upgrade-candidates/           ← 방법론 개선 후보 수집
│   │
│   └── workspace/                    ← workspace/ 초기화 템플릿 (복사 소스, 골격만)
│       ├── README.md  (workspace·.mpa-workspace 사용 안내 — 설치본 사용자용)
│       ├── memory/   (shared/ domains/ roles/ 빈 골격)
│       ├── tasks/    (INDEX.md, active/ done/)
│       └── docs/     (INDEX.md)
│
├── agent-specs/                      ← agent별 설치 스펙 (claude/codex/antigravity/openagent)
├── guidebook/                        ← 실용 안내서 (guidebook.md)
├── workspace/                        ← 이 레포 자체의 작업 데이터 (memory·tasks·docs)
│   └── exploration/                  ← 설계 사고·탐구 공간 (토론 모드 기록 위치)
├── install.py                        ← 설치 스크립트 (agent가 실행)
└── install.md                        ← 설치 가이드 (agent가 참조하는 진입점)
```

---

## 설치된 프로젝트 구조

```
[project]/
├── .mpa-workspace/    ← 방법론 (업그레이드로 최신화, 직접 수정 금지)
│   ├── core/, personas/, skills/, workflows/, inject/
│   ├── hooks/, templates/, knowledge/
│   └── upgrade-candidates/   ← 작업 중 발견된 방법론 개선 후보
│
└── workspace/            ← 프로젝트 데이터 (agent가 직접 관리)
    ├── README.md         ← 설치본 사용자용 안내 (workspace·.mpa-workspace 소개)
    ├── memory/
    ├── tasks/
    └── docs/
```

| 폴더 | 역할 | 업데이트 방식 |
|------|------|--------------|
| `.mpa-workspace/` | 방법론 (HOW) | 업그레이드로 최신화 / `mpa_system_designer` 프로세스로 직접 수정 가능 |
| `workspace/` | 프로젝트 데이터 (WHAT) — agent가 관리 | 작업할 때마다 자동 업데이트 |

---

## Hook (가드레일)

`.mpa-workspace/hooks/`의 python 스크립트가 세션 시작 시 컨텍스트를 주입하고, 소스 수정 시 게이트로 작동한다. 외부 의존성(jq 등) 없이 `python3`로만 동작하며 실행 디렉터리는 프로젝트 루트를 가정한다.

| 스크립트 | 이벤트 | 차단 | 하는 일 |
|---------|--------|------|--------|
| `session_start.py` | SessionStart | ❌ | 진행 태스크 + 라우팅 규칙 주입 |
| `code_gate.py` | PreToolUse(편집 도구) | ✅ | `구현 중` plan 없이 소스 수정 시 차단 |
| `turn_end.py` | Stop | ❌ | changelog/memory 갱신 리마인드 |

하드 차단(실제로 작업을 막는 것)은 `code_gate.py` 하나뿐이고, 나머지는 컨텍스트 주입·리마인드(보조)다.

### 게이트 강도 — 환경변수 `MPA_GATE`

| 값 | 동작 |
|----|------|
| `block` (기본) | 조건 불충족 시 소스 수정 차단 |
| `warn` | 차단하지 않고 경고만 주입 |
| `off` | 게이트 비활성 |

```bash
MPA_GATE=off claude     # 또는 codex / gemini — 잠시 끄기
```
또는 agent 설정 파일의 `env`에 `MPA_GATE`를 지정한다.

### agent별 설정 위치

| agent | 설정 파일 | 이벤트 명칭 |
|-------|----------|-----------|
| claude | `.claude/settings.json` | SessionStart / PreToolUse / Stop |
| codex | `.codex/hooks.json` | SessionStart / PreToolUse / Stop |
| gemini(antigravity) | `.gemini/settings.json` | SessionStart / BeforeTool / AfterAgent |

스크립트는 `--agent` 플래그로 이벤트 명칭 등 출력 형식을 맞춘다. 차단은 exit 2 + stderr로 3개 agent 공통이다.

### 알려진 한계 (정직하게)

- **Bash 우회:** matcher가 편집 도구(Edit/Write 등)에만 걸리므로 `bash -c 'sed ... > file'` 같은 셸 파일 수정은 걸리지 않는다. (이 프로젝트엔 "shell로 파일 내용 수정 금지" 규칙이 있어 정상 워크플로우에선 Edit/Write를 쓴다.)
- **태스크 범위 판정 한계:** `구현 중` 태스크가 있으면 수정 대상 파일이 그 태스크 범위 안인지까지 완전히 증명하지는 못한다. 에어타이트 봉쇄가 아니라 가드레일이다.
- **승인해시 갱신은 agent가 한다:** 완전한 강제는 아니다. 다만 승인해시가 비어 있으면 자동 복구하지 않고 차단하므로, 사용자 승인 없이 사후 승인하는 우회를 줄인다.

> 게이트 조건(GATE 1·2)·승인해시 복구 절차의 상세는 `.mpa-workspace/core/agent_rules.md`·`agent_rules_detail.md`를 따른다.

---

## 방법론 개선 파이프라인

```
작업 중 더 나은 방법 발견
      ↓
[project]/.mpa-workspace/upgrade-candidates/ 에 후보 파일 추가
      ↓
.mpa-workspace/ 업데이트 시 my-pacemaker-agent/dist/.mpa-workspace/upgrade-candidates/ 로 자동 이동 (1단계)
      ↓
검토 및 정제 → my-pacemaker-agent/dist/.mpa-workspace/ 해당 파일에 반영
              (절차: my-pacemaker-agent/harness-maintenance.md 참조)
      ↓
다음 프로젝트 업데이트 시 새 스냅샷으로 배포
```

### 업데이트 기준

| 상황 | 조치 |
|------|------|
| 더 나은 검증·세션 방법 발견 | inject 파일 수정 |
| 새 작업 유형 필요 | workflow / inject 추가 |
| 기존 방식이 반복 실패 | principles 검토 후 방법론 수정 |
| 특정 프로젝트에서만 필요한 것 | 방법론 건드리지 않음 — workspace에 둠 |

### 커밋 태그 규칙

```
[breaking]     layer1_design: [요청 문서] 섹션 추가
               → 기존 프로젝트: .mpa-workspace/ 재복사 필요

[non-breaking] principles: T9 설명 보완
               → 기존 프로젝트 영향 없음
```

---

## 빠른 참조

| 상황 | inject 파일 | 비고 |
|------|------------|------|
| 새 프로젝트 초기화 | `.mpa-workspace/inject/layer0_init.md` | |
| 방법론 업데이트 / 재설치 | `.mpa-workspace/inject/layer0_update.md` | |
| 기능 설계 / 계획 작성 | `.mpa-workspace/inject/layer1_design.md` | |
| 계획 독립 비평 | `.mpa-workspace/inject/layer1_critique.md` | 서브에이전트로 실행 (컨텍스트 격리) |
| 구현 | `.mpa-workspace/inject/layer1_implement.md` | |
| 코드 검토 / 에이전트 검증 | `.mpa-workspace/inject/layer1_review.md` | 서브에이전트로 실행 권장 |
| 구현 후 발견 정리 | `.mpa-workspace/inject/layer1_discovery.md` | |
| 정합성 점검 | `.mpa-workspace/inject/layer2_checkpoint.md` | |
