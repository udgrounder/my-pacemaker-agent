# my-pacemaker-agent 설치 가이드

이 문서를 읽고 아래 **질의응답 절차**에 따라 사용자와 대화하며 파라메터를 결정한 뒤 `install.py`를 실행한다.

---

## 스크립트 위치

```
install.py
```

---

## 파라메터

| 파라메터 | 필수 | 설명 |
|---------|------|------|
| `--project` | ✅ | 설치 대상 프로젝트 경로 (절대 경로 권장) |
| `--agents` | ✅ | 사용할 agent (claude, codex, antigravity, openagent 또는 조합) |
| `--upgrade` | ❌ | 이미 설치된 경우 업그레이드 모드로 실행 |

---

## Agent Spec 구조

각 agent의 폴더 규칙과 주입 파일은 `agent-specs/` 에 정의되어 있다.

```
agent-specs/
  {agent}/
    spec.md          ← 이 agent의 감지 조건·폴더 규칙·설치 처리 정의
    inject/          ← 진입점 파일(CLAUDE.md 등)에 추가할 내용
    files/           ← 프로젝트에 복사할 파일 (디렉터리 구조 그대로)
```

| Agent | 진입점 | 감지 조건 |
|-------|--------|---------|
| `claude` | `CLAUDE.md` | `CLAUDE.md` 또는 `.claude/` 존재 |
| `codex` | `AGENTS.md` | `AGENTS.md` 존재 |
| `antigravity` | `GEMINI.md` | `GEMINI.md` 또는 `.gemini/` 존재 |
| `openagent` | 미정 | 감지 불가 → 사용자에게 확인 |

---

## 질의응답 절차

아래 순서대로 진행한다. 각 단계에서 이미 알고 있는 정보는 질문하지 않는다.

---

### Q1. 프로젝트 경로

| 상황 | 처리 |
|------|------|
| 사용자가 이미 경로를 알려준 경우 | 그 경로 사용, 바로 Q2로 진행 |
| 경로를 알 수 없는 경우 | 아래 질문 |

> "설치할 프로젝트 폴더 경로를 알려주세요."

---

### Q2. 사용할 Agent

경로가 결정되면 해당 폴더를 확인하여 agent를 감지한다.

| 감지 결과 | 처리 |
|-----------|------|
| 하나 이상 감지된 경우 | 감지 결과를 기본값으로 제시하며 아래 질문 |
| 감지 안 된 경우 | 아래 질문 |
| 사용자가 이미 명시한 경우 | 그 값 사용, 바로 Q3 진행 |

> (감지된 경우) "다음 agent가 감지됩니다: [목록]. 이대로 진행할까요, 아니면 변경하시겠어요? (claude / codex / antigravity / openagent 또는 조합)"
> (감지 안 됨) "어떤 agent를 사용하시나요? (claude / codex / antigravity / openagent 또는 조합)"

**openagent가 포함된 경우:** `agent-specs/openagent/spec.md` 를 읽고 질의 절차에 따라 사용자와 대화하여 설정을 결정한다. 확인된 내용으로 `spec.md`를 업데이트한다.

---

### Q3. Agent Spec 파일 적용

agent가 결정되면 각 agent의 `agent-specs/{agent}/spec.md` 를 읽어 설치 내용을 파악한다.

**agent별 파일 배치 규칙:**

각 agent는 자신의 전용 폴더 아래에만 파일을 설치한다. `agent-specs/{agent}/files/` 의 디렉터리 구조가 프로젝트에 그대로 복사된다.

| Agent | native 폴더 (직접 배치) |
|-------|----------------------|
| `claude` | `.claude/agents/mpa_pacemaker.md` |
| `codex` | `.agents/rules/mpa_pacemaker.md` |
| `antigravity` | `.agents/rules/mpa_pacemaker.md` (codex와 공유) |
| `openagent` | spec.md 질의 결과에 따름 |

workspace는 어떤 agent를 사용하든 동일하므로 프로젝트 루트에 한 번만 설치한다.

**install.py가 자동 처리하는 항목:**
- `inject/` → 진입점 파일(CLAUDE.md 등)에 Agents Workspace 섹션 추가
- `files/` → agent 전용 폴더에 파일 복사 (없는 경우만)

**install.py 실행 전 안내:**
- 어떤 파일이 어느 폴더에 설치되는지 사용자에게 요약하여 알린다

---

### Q4. 신규 설치 vs 업그레이드 (자동 판단)

질문 없이 자동으로 결정한다.

| 조건 | 모드 |
|------|------|
| `.mpa-workspace/` 폴더 없음 | 신규 설치 |
| `.mpa-workspace/` 폴더 있음 | 업그레이드 |

---

### Q5. 설치 실행

Q1~Q4에서 수집한 정보를 요약하여 사용자에게 알린 뒤 `install.py`를 실행한다.

```
모드   : 신규 설치 | 업그레이드
경로   : <결정된 경로>
agents : <결정된 agent>
```

```bash
# 신규 설치
python3 install.py --project <경로> --agents <agent>

# 업그레이드
python3 install.py --project <경로> --agents <agent> --upgrade
```

---

## 설치 결과

신규 설치 시 생성되는 파일:

```
[project]/
├── .mpa-workspace/          ← 방법론 스냅샷 (harness에서 복사)
├── CLAUDE.md                   ← claude 포함 시 (Agents Workspace 섹션)
├── AGENTS.md                   ← codex 포함 시 (Agents Workspace 섹션)
├── GEMINI.md                   ← antigravity 포함 시 (Agents Workspace 섹션)
├── workspace/                  ← 모든 agent 공용 (프로젝트 루트)
│   ├── memory/
│   ├── tasks/
│   └── docs/
├── .claude/                    ← claude 포함 시
│   └── agents/mpa_pacemaker.md ← native 폴더에 직접 배치
└── .agents/                    ← codex 또는 antigravity 포함 시
    └── rules/mpa_pacemaker.md  ← native 폴더에 직접 배치
```

업그레이드 시 추가 동작:
- `.mpa-workspace/upgrade-candidates/` 파일을 harness로 이동 후 `.mpa-workspace/` 교체

> **설치·업그레이드 공통 규칙:**  
> `.mpa-workspace/upgrade-candidates/` 디렉토리는 생성되지만 **내용은 비워진다**.  
> 하네스 자체의 개선 후보는 프로젝트로 넘어가지 않는다.
