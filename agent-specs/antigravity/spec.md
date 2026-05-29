---
agent: antigravity
tool: Antigravity (Gemini)
---

# Antigravity — Agent Spec

## 감지 조건
- `GEMINI.md` 존재 (프로젝트 루트)
- `.gemini/` 폴더 존재

## 폴더 규칙

| 항목 | 위치 |
|------|------|
| 진입점 | `GEMINI.md` (프로젝트 루트) |
| 공용 폴더 | `.agents/` (codex와 공유 가능) |
| 규칙 파일 | `.agents/rules/*.md` |

## 설치 처리

1. `inject/GEMINI.md` 내용을 프로젝트 `GEMINI.md`에 추가 (없으면 생성)
2. `files/` 하위 파일을 프로젝트에 복사 (없는 경우만)
   - `.agents/rules/mpa_pacemaker.md` → native rules/ 폴더에 규칙 파일 등록
   - `.agents/workspace/memory/` → 프로젝트 메모리 — codex와 공유, 이미 있으면 건너뜀
   - `.agents/workspace/tasks/` → 태스크 관리 — codex와 공유, 이미 있으면 건너뜀
   - `.agents/workspace/docs/` → 문서 — codex와 공유, 이미 있으면 건너뜀

## 파일 참조 문법

Antigravity의 파일 import 문법을 확인 필요. 현재는 텍스트 참조 방식 사용.
