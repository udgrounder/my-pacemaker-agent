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
   - `.claude/workspace/memory/` → 프로젝트 메모리 (domains, roles, shared)
   - `.claude/workspace/tasks/` → 태스크 관리
   - `.claude/workspace/docs/` → 문서

## 파일 참조 문법

Claude Code는 `@path/to/file` 문법으로 파일을 import한다.
