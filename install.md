# my-pacemaker-agent 설치 가이드

이 문서를 읽고 아래 판단 절차에 따라 `install.py` 를 실행한다.

---

## 스크립트 위치

```
harness/install.py
```

---

## 파라메터

| 파라메터 | 필수 | 설명 |
|---------|------|------|
| `--project` | ✅ | 설치 대상 프로젝트 경로 (절대 경로 권장) |
| `--agents` | ✅ | 사용 중인 agent (claude, codex, 또는 claude,codex) |
| `--upgrade` | ❌ | 이미 설치된 경우 업그레이드 모드로 실행 |

---

## 판단 절차

### 1. 프로젝트 경로 결정
- 사용자가 명시한 경우 → 그 경로 사용
- 명시하지 않은 경우 → 현재 작업 디렉토리 사용

### 2. 사용 중인 agent 감지

프로젝트 경로에서 아래를 순서대로 확인한다:

| 조건 | agent |
|------|-------|
| `CLAUDE.md` 존재 또는 `.claude/` 폴더 존재 | `claude` |
| `AGENTS.md` 존재 | `codex` |
| 둘 다 없으면 | 사용자에게 확인 후 결정 |

### 3. 신규 설치 vs 업그레이드 판단

| 조건 | 실행 방식 |
|------|---------|
| `.agents-workspace/` 폴더 없음 | 신규 설치 (--upgrade 없이) |
| `.agents-workspace/` 폴더 있음 | 업그레이드 (--upgrade 추가) |

---

## 실행 예시

```bash
# 신규 설치 — Claude Code만 사용
python harness/install.py --project /path/to/project --agents claude

# 신규 설치 — 두 agent 모두 사용
python harness/install.py --project /path/to/project --agents claude,codex

# 업그레이드
python harness/install.py --project /path/to/project --agents claude,codex --upgrade
```

---

## 설치 결과

신규 설치 시 생성되는 파일:

```
[project]/
├── .agents-workspace/    ← 방법론 스냅샷 (harness에서 복사)
├── workspace/            ← 프로젝트 데이터 템플릿 (없는 경우만 생성)
├── CLAUDE.md             ← Agents Workspace 섹션 추가 (--agents에 claude 포함 시)
└── AGENTS.md             ← Agents Workspace 섹션 추가 (--agents에 codex 포함 시)
```

업그레이드 시 추가 동작:
- `.agents-workspace/upgrade-candidates/` 파일을 harness로 이동 후 `.agents-workspace/` 교체

> **설치·업그레이드 공통 규칙:**  
> `.agents-workspace/upgrade-candidates/` 디렉토리는 생성되지만 **내용은 비워진다**.  
> 하네스 자체의 개선 후보는 프로젝트로 넘어가지 않는다.
