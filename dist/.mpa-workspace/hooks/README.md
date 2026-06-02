# hooks/

방법론을 **산문 규칙**에서 **agent 하네스가 강제하는 메커니즘**으로 끌어올리는 hook 스크립트 모음이다.
설치 시 각 agent의 설정 파일에 자동 등록된다 (claude/codex). antigravity/openagent는 설치 시 질의로 등록한다.

모두 `python3` 로 작성되어 jq 등 외부 의존성이 없다. 실행 디렉터리는 프로젝트 루트를 가정한다.

---

## 스크립트

| 파일 | 이벤트 | 차단 | 하는 일 |
|------|--------|------|--------|
| `session_start.py` | SessionStart | ❌ | 진행 중 태스크 목록 + 라우팅 규칙을 컨텍스트에 주입 |
| `code_gate.py` | PreToolUse(Edit\|Write) / BeforeTool | ✅ | 승인된 plan 없이 소스 수정 시 차단/경고 |
| `turn_end.py` | Stop / AfterAgent | ❌ | 진행 중 태스크가 있으면 changelog/memory 갱신 리마인드 |

---

## 코드 수정 게이트 (`code_gate.py`)

소스코드를 수정하려면 **승인 마커**가 있어야 한다.

- **승인 마커:** `workspace/tasks/active/<task>/.approved`
  - 사용자가 plan 을 승인하면 agent 가 생성한다.
  - 사용자가 직접 만들거나 지워도 된다 (파일이라 직접 제어 가능).
- **항상 허용(차단 대상 아님):**
  - `workspace/**`, `.mpa-workspace/**`, `.claude|.codex|.gemini|.agents/**`
  - 모든 `*.md` 파일 (plan·changelog·memory·문서)
  - → plan.md 조차 못 쓰는 교착을 방지한다.
- **차단 대상:** 위에 해당하지 않는 프로젝트 소스코드. active 태스크에 `.approved` 마커가 하나도 없으면 차단한다.

### 강도 조절 — 환경변수 `MPA_GATE`

| 값 | 동작 |
|----|------|
| `block` (기본) | 마커 없으면 소스 수정 차단 |
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
- **거친 판정:** active 에 `.approved` 가 하나라도 있으면 무관한 파일 수정도 통과한다. 에어타이트 봉쇄가 아니라 가드레일이다.
- **마커 생성은 agent 가 한다:** 완전한 강제는 아니다. 다만 코드 수정이 *파일의 물리적 존재*에 묶이므로 산문 규칙보다 건너뛰기 어렵고, 감사 추적이 남고, 사용자가 직접 끌 수 있다.

---

## agent별 설정 위치

| agent | 설정 파일 | 이벤트 명칭 |
|-------|----------|-----------|
| claude | `.claude/settings.json` | SessionStart / PreToolUse / Stop |
| codex | `.codex/hooks.json` | SessionStart / PreToolUse / Stop |
| gemini(antigravity) | `.gemini/settings.json` | SessionStart / BeforeTool / AfterAgent |

스크립트는 `--agent` 플래그로 출력 형식(이벤트 명칭 등)을 맞춘다. 차단은 exit 2 + stderr 로 3개 agent 공통이다.
