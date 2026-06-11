---
agent: claude
tool: Claude Code (Anthropic)
---

# Claude Code — Agent Spec

## 감지 조건
- `CLAUDE.md` 존재 (프로젝트 루트)
- `.claude/` 폴더 존재

## 폴더 규칙

| 항목 | 위치 |
|------|------|
| 진입점 | `CLAUDE.md` (프로젝트 루트) |
| 설정 폴더 | `.claude/` |
| 서브에이전트 | `.claude/agents/*.md` |
| 슬래시 커맨드 | `.claude/commands/*.md` |
| 설정 파일 | `.claude/settings.json` |

## 설치 처리

1. `inject/CLAUDE.md` 내용을 프로젝트 `CLAUDE.md`에 추가 (Agents Workspace 섹션)
2. `files/` 하위 파일을 프로젝트에 복사 (없는 경우만)
   - `.claude/agents/mpa_pacemaker.md` → native agents/ 폴더에 서브에이전트 등록
3. **hook 자동 등록** (install.py가 처리) — `.claude/settings.json` 의 `hooks` 에 안전 병합
   - 기존 설정을 보존하고, 이미 등록돼 있으면 건너뛴다 (멱등)

## Hooks

`.claude/settings.json` 의 `hooks` 에 다음을 등록한다. 스크립트는 `.mpa-workspace/hooks/` 에 있다.

| 이벤트 | matcher | 스크립트 | 역할 |
|--------|---------|---------|------|
| `SessionStart` | — | `session_start.py` | 진행 태스크·라우팅 규칙 주입 |
| `PreToolUse` | `Edit\|Write` | `code_gate.py` | 승인 마커 없는 소스 수정 차단 |
| `Stop` | — | `turn_end.py` | changelog/memory 갱신 리마인드 |

- 차단: `code_gate.py` 가 exit 2 + stderr 로 도구 호출을 막는다.
- 컨텍스트 주입: `hookSpecificOutput.additionalContext` 사용.
- 게이트 강도는 환경변수 `MPA_GATE` (block/warn/off) 로 조절한다.

## 파일 참조 문법

Claude Code는 `@path/to/file` 문법으로 파일을 import한다.
