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

이 저장소의 설치 코드는 `.codex/hooks.json`에 아래 연결 설정을 생성한다. 호스트가 해당 이벤트를 실제 호출하는지는 별도 확인 대상이다.
install.py는 `.codex/hooks.json` 에 Codex 편집 도구명을 포함한 matcher로 등록한다. 스크립트는 `.mpa/runtime/hooks/` 에 있다.

| 이벤트 | matcher | 스크립트 |
|--------|---------|---------|
| `SessionStart` | — | `session_start.py --agent codex` |
| `PreToolUse` | `Edit\|Write\|MultiEdit\|apply_patch\|write_file\|replace\|edit` | `code_gate.py --agent codex` |
| `Stop` | — | `turn_end.py --agent codex` |

- 스크립트는 exit 2와 `additionalContext`를 출력하도록 구현돼 있다. 호스트의 차단·주입 수용까지 단위 테스트가 보장하지 않는다.
- `SessionStart` / `Stop` 설정 생성과 스크립트 실행은 로컬 테스트 범위이며 실제 이벤트 호출은 미확인이다.

## 파일 참조 문법

설치 템플릿은 `@path/to/file` 참조를 기록한다. 실제 호스트에서 자동 로드됐는지는 별도 확인해야 하며, 파일을 명시적으로 읽은 것과 구분한다.

## 서브에이전트 위임

호출 전에 `.mpa/runtime/inject/agent_delegation.md`를 읽는다. 현재 도구 계약에서 명시 모델 지정, 기본 모델 상속과 대화 미상속 옵션을 확인한다. `fork_turns="none"`을 지원하는 호출에서는 이를 지정해 독립 비평·검증 입력을 격리한다. 도구 설명에 없는 옵션은 추정하지 않는다.

현재 역할의 custom agent 설정과 호스트 기본값이 요청한 모델·추론 설정을 덮는지 확인한다. 유효한 설정을 확인할 수 없으면 보장된 안전 상속만 고려하고, 그것도 확인할 수 없으면 공통 지침의 폴백을 적용한다. 요청값과 반환 메타데이터/실행 기록에 나타난 실제 모델은 별도로 기록한다.

## 확인 범위와 한계

이 문서는 저장소의 설치·연결 계약을 설명한다. 로컬 테스트의 설정 생성·스크립트 직접 실행과 실제 호스트의 이벤트 호출·차단·참조 로딩은 별개다. 이번 정합성 검토에서 실제 호스트 통합은 미확인이며, 제품 전체의 지원 여부를 단정하지 않는다. 실제 확인 시 호스트 버전·이벤트·입력·결과를 함께 기록한다.

hook의 도구·입력 경계와 승인해시의 보장 범위는 [가이드북](../../guidebook/guidebook.md)의 "승인과 hook이 확인하는 범위"를 따른다. 독립 비평·검증은 [실행 정본](../../.mpa/runtime/inject/_agent_execution_priority.md)의 격리·산출물·실패 조건을 적용한다.
