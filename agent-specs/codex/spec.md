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
   - `.agents/workspace/memory/` → 프로젝트 메모리 (domains, roles, shared)
   - `.agents/workspace/tasks/` → 태스크 관리
   - `.agents/workspace/docs/` → 문서

## 파일 참조 문법

Codex는 `@path/to/file` 문법으로 파일을 import한다.
