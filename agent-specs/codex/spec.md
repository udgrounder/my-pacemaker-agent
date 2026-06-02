---
agent: codex
tool: OpenAI Codex
---

# Codex — Agent Spec

## 감지 조건
- `AGENTS.md` 존재 (프로젝트 루트)

## 폴더 규칙

| 항목 | 위치 |
|------|------|
| 진입점 | `AGENTS.md` (프로젝트 루트) |
| 공용 폴더 | `.agents/` |
| 에이전트 정의 | `.agents/agents/*.md` |
| 규칙 파일 | `.agents/rules/*.md` |
| 메모리 | `.agents/memory/` |

## 설치 처리

1. `inject/AGENTS.md` 내용을 프로젝트 `AGENTS.md`에 추가 (Agents Workspace 섹션)
2. `files/` 하위 파일을 프로젝트에 복사 (없는 경우만)
   - `.agents/rules/mpa_pacemaker.md` → native rules/ 폴더에 규칙 파일 등록
3. **hook 자동 등록** (install.py가 처리) — `.codex/hooks.json` 에 안전 병합 (claude와 동일 구조)

## Hooks

Codex는 `.codex/hooks.json` (또는 `.codex/config.toml` 의 `[hooks]`) 에서 hook을 지원한다.
install.py는 `.codex/hooks.json` 에 claude와 동일한 구조로 등록한다. 스크립트는 `.mpa-workspace/hooks/` 에 있다.

| 이벤트 | matcher | 스크립트 |
|--------|---------|---------|
| `SessionStart` | — | `session_start.py --agent codex` |
| `PreToolUse` | `Edit\|Write` | `code_gate.py --agent codex` |
| `Stop` | — | `turn_end.py --agent codex` |

- 차단/주입 방식은 claude와 동일 (exit 2 차단, `additionalContext` 주입).
- **확인 필요(한계):** Codex의 수정 도구 이름이 `Edit`/`Write`와 다를 수 있다(예: `apply_patch`).
  matcher가 안 맞으면 `PreToolUse` 게이트가 발동하지 않을 수 있으므로, 설치 후 실제 차단이 작동하는지
  한 번 검증하고 필요하면 matcher를 해당 agent의 도구 이름으로 조정한다.
- `SessionStart` / `Stop` 은 도구 이름과 무관하므로 안정적으로 작동한다.

## 파일 참조 문법

Codex는 `@path/to/file` 문법으로 파일을 import한다.
