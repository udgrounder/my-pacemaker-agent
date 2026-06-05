# hooks/

방법론을 **산문 규칙**에서 **agent MPA 시스템이 강제하는 메커니즘**으로 끌어올리는 hook 스크립트 모음이다.
설치 시 각 agent의 설정 파일에 자동 등록된다 (claude/codex). antigravity/openagent는 설치 시 질의로 등록한다.

모두 `python3` 로 작성되어 jq 등 외부 의존성이 없다. 실행 디렉터리는 프로젝트 루트를 가정한다.

---

## 스크립트

| 파일 | 이벤트 | 차단 | 하는 일 |
|------|--------|------|--------|
| `session_start.py` | SessionStart | ❌ | 진행 중 태스크 목록 + 라우팅 규칙을 컨텍스트에 주입 |
| `code_gate.py` | PreToolUse(Edit\|Write) / BeforeTool | ✅ | `구현 중` plan 없이 소스 수정 시 차단/경고 |
| `turn_end.py` | Stop / AfterAgent | ❌ | 진행 중 태스크가 있으면 changelog/memory 갱신 리마인드 |

---

## 코드 수정 게이트 (`code_gate.py`)

소스코드를 수정하려면 active 태스크의 `plan.md`가 **구현 가능한 상태**여야 한다.

- **GATE 1 — 소스 수정 허용 조건**
  - `workspace/tasks/active/[작업명]/plan.md` YAML 프론트매터의 `상태`가 `구현 중`이어야 한다.
  - `구현 중` 태스크의 `승인해시`가 현재 plan.md 본문 해시와 일치해야 한다.
  - 승인 직후 또는 재승인 직후 agent가 `python3 .mpa-workspace/hooks/plan_hash.py approve [plan.md]`를 실행해 `승인해시`를 갱신한다.
  - `승인해시`가 비어 있으면 자동 등록하지 않고 차단한다. 사용자 승인 이력을 확인한 뒤 명시적으로 복구해야 한다.
- **GATE 2 — 완료 이동 허용 조건**
  - `workspace/tasks/active/[작업명]/`을 `workspace/tasks/done/[작업명]/`로 이동하려면 plan.md `상태`가 `완료 승인`이어야 한다.
- **항상 허용(차단 대상 아님):**
  - `workspace/**`, `.mpa-workspace/**`, `.claude|.codex|.gemini|.agents/**`
  - 모든 `*.md` 파일 (plan·changelog·memory·문서)
  - → plan.md 조차 못 쓰는 교착을 방지한다.
- **차단 대상:** 위에 해당하지 않는 프로젝트 소스코드. `구현 중` 상태인 active 태스크가 없거나, `승인해시`가 현재 plan.md와 다르면 차단한다.

### 강도 조절 — 환경변수 `MPA_GATE`

| 값 | 동작 |
|----|------|
| `block` (기본) | 조건 불충족 시 소스 수정 차단 |
| `warn` | 차단하지 않고 경고만 주입 |
| `off` | 게이트 비활성 |

예) 단순 수정 세션에서 잠시 끄기:
```bash
MPA_GATE=off claude     # 또는 codex / gemini
```
또는 agent 설정 파일의 `env` 에 `MPA_GATE` 를 지정한다.

### 알려진 한계 (정직하게)

- **Bash 우회:** matcher 가 `Edit|Write` 라서 `bash -c 'sed ... > file'` 같은 셸 파일 수정은 걸리지 않는다.
  (이 프로젝트엔 "shell 로 파일 내용 수정 금지" 규칙이 이미 있어 정상 워크플로우에선 Edit/Write 를 쓴다.)
- **태스크 범위 판정 한계:** `구현 중` 태스크가 있으면 수정 대상 파일이 그 태스크 범위 안인지까지 완전히 증명하지는 못한다. 에어타이트 봉쇄가 아니라 가드레일이다.
- **승인해시 갱신은 agent가 한다:** 완전한 강제는 아니다. 다만 승인해시가 비어 있으면 자동 복구하지 않고 차단하므로, 사용자 승인 없이 현재 plan.md를 사후 승인하는 우회를 줄인다.

### 승인해시 없음 복구 절차

`code_gate.py`가 "GATE 1 복구 필요"로 차단하면 자동으로 `approve`를 실행하지 않는다.

1. `plan.md`와 대화 맥락을 확인한다.
2. 아래 중 하나로 분류한다:
   - 사용자 승인 이력이 불명확함 → `상태: 설계 완료`로 되돌리고 사용자 재승인을 받는다.
   - 직전 사용자 승인 후 기록만 누락됨 → 누락 사실과 현재 plan.md 해시를 사용자에게 보여주고 확인받는다.
   - minor 자동 승인 태스크임 → 최소 plan.md가 사용자 요청과 일치하는지 확인한다.
3. 사용자 확인 또는 minor 자동 승인 조건 확인 후에만 실행한다:
   ```bash
   python3 .mpa-workspace/hooks/plan_hash.py approve workspace/tasks/active/[작업명]/plan.md
   ```

---

## agent별 설정 위치

| agent | 설정 파일 | 이벤트 명칭 |
|-------|----------|-----------|
| claude | `.claude/settings.json` | SessionStart / PreToolUse / Stop |
| codex | `.codex/hooks.json` | SessionStart / PreToolUse / Stop |
| gemini(antigravity) | `.gemini/settings.json` | SessionStart / BeforeTool / AfterAgent |

스크립트는 `--agent` 플래그로 출력 형식(이벤트 명칭 등)을 맞춘다. 차단은 exit 2 + stderr 로 3개 agent 공통이다.
