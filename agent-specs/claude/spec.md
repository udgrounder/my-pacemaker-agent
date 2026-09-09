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

`.claude/settings.json` 의 `hooks` 에 다음을 등록한다. 스크립트는 `.mpa/runtime/hooks/` 에 있다.

| 이벤트 | matcher | 스크립트 | 역할 |
|--------|---------|---------|------|
| `SessionStart` | — | `session_start.py` | 진행 태스크·라우팅 규칙 주입 |
| `PreToolUse` | `Edit\|Write` | `code_gate.py` | 승인 상태·명세 해시 검사 |
| `Stop` | — | `turn_end.py` | changelog/memory 갱신 리마인드 |

- 기본 `warn`은 일반 이상을 경고하지만, 인식된 소스 편집에서 `CURRENT_TASK`로 선택한 critical 작업의 승인 누락·무결성 오류는 exit 2로 차단한다. `MPA_GATE=block`은 인식된 편집 경로에서 검사를 강화하고 `off`는 검사를 건너뛴다.
- 컨텍스트 주입: `hookSpecificOutput.additionalContext` 사용.
- 게이트 강도는 환경변수 `MPA_GATE` (block/warn/off) 로 조절한다.

## 파일 참조 문법

Claude Code는 `@path/to/file` 문법으로 파일을 import한다.

## 확인 범위와 한계

이 문서는 저장소의 설치·연결 계약을 설명한다. 로컬 테스트의 설정 생성·스크립트 직접 실행과 실제 호스트의 이벤트 호출·차단·참조 로딩은 별개다. 이번 정합성 검토에서 실제 호스트 통합은 미확인이며, 제품 전체의 지원 여부를 단정하지 않는다. 실제 확인 시 호스트 버전·이벤트·입력·결과를 함께 기록한다.

hook의 도구·입력 경계와 승인해시의 보장 범위는 [가이드북](../../guidebook/guidebook.md)의 "승인과 hook이 확인하는 범위"를 따른다. 독립 비평·검증은 [실행 정본](../../.mpa/runtime/inject/_agent_execution_priority.md)의 격리·산출물·실패 조건을 적용한다.
