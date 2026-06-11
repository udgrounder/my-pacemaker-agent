---
agent: codex
tool: OpenAI Codex
---

# Codex — Agent Spec

## 감지 조건
- `AGENTS.md` 또는 `.codex/` 존재

## 폴더 규칙

| 항목 | 위치 |
|------|------|
| 진입점 | `AGENTS.md` (프로젝트 루트) |
| Codex 설정 | `.codex/` |
| 공용 폴더 | `.agents/` |
| 에이전트 정의 | `.codex/agents/*.toml` |
| 규칙 파일 | `.agents/rules/*.md` |
| 메모리 | `.agents/memory/` |

## 설치 처리

1. `inject/AGENTS.md` 내용을 프로젝트 `AGENTS.md`에 추가 (Agents Workspace 섹션)
2. `files/` 하위 파일을 프로젝트에 복사 (없는 경우만)
   - `.agents/rules/mpa_pacemaker.md` → native rules/ 폴더에 규칙 파일 등록
   - `.codex/agents/mpa_pacemaker.toml` → Codex developer instructions 등록
3. **hook 자동 등록** (install.py가 처리) — `.codex/hooks.json` 에 안전 병합

## Hooks

Codex는 `.codex/hooks.json` 에서 hook을 지원한다.
install.py는 `.codex/hooks.json` 에 Codex 편집 도구명을 포함한 matcher로 등록한다. 스크립트는 `.mpa-workspace/hooks/` 에 있다.

| 이벤트 | matcher | 스크립트 |
|--------|---------|---------|
| `SessionStart` | — | `session_start.py --agent codex` |
| `PreToolUse` | `Edit\|Write\|MultiEdit\|apply_patch\|write_file\|replace\|edit` | `code_gate.py --agent codex` |
| `Stop` | — | `turn_end.py --agent codex` |

- 차단/주입 방식은 claude와 동일 (exit 2 차단, `additionalContext` 주입).
- `SessionStart` / `Stop` 은 도구 이름과 무관하므로 안정적으로 작동한다.

## 파일 참조 문법

Codex는 `@path/to/file` 문법으로 파일을 import한다.
