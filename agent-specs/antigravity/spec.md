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
   - 루트 `docs/` → 사용자 문서 — 설치/업데이트에서는 이미 있으면 건너뛰고, 없을 때만 생성

## Hooks (설치 시 질의)

Antigravity 자체의 hook 지원은 공식 확인 불가다. **install.py는 hook을 자동 등록하지 않는다.**
설치 시 실행 중인 agent가 아래를 확인하고 설정한 뒤 이 spec.md를 갱신한다.

확인 항목:
1. hook(이벤트 기반 자동 실행/차단/세션시작 주입)을 지원하는가? 설정 파일 위치·형식은?
2. 지원한다면 아래 강한 기본값(Gemini CLI 기준)을 적용한다.

**기본값 — Gemini CLI 기준** (`.gemini/settings.json`):

```json
{
  "hooks": {
    "SessionStart": [
      { "hooks": [{ "type": "command", "command": "python3 .mpa/runtime/hooks/session_start.py --agent gemini" }] }
    ],
    "BeforeTool": [
      { "matcher": "write_file|replace|edit",
        "hooks": [{ "type": "command", "command": "python3 .mpa/runtime/hooks/code_gate.py --agent gemini" }] }
    ],
    "AfterAgent": [
      { "hooks": [{ "type": "command", "command": "python3 .mpa/runtime/hooks/turn_end.py --agent gemini" }] }
    ]
  }
}
```

- Gemini CLI는 이벤트 명칭이 다르다: `BeforeTool`(차단) / `AfterAgent` / `SessionStart`.
- 차단은 exit 2 + stderr 로 공통 동작하며, 스크립트는 `--agent gemini` 로 출력 형식을 맞춘다.
- matcher의 도구 이름(`write_file` 등)은 실제 Gemini 도구 이름으로 검증 후 조정한다.
- 지원 안 하거나 형식이 다르면, 그 결과로 이 spec.md를 갱신해 다음 설치에 재사용한다.

## 파일 참조 문법

Antigravity의 파일 import 문법을 확인 필요. 현재는 텍스트 참조 방식 사용.

## 확인 범위와 한계

이 문서는 저장소의 설치·연결 계약을 설명한다. 로컬 테스트의 설정 생성·스크립트 직접 실행과 실제 호스트의 이벤트 호출·차단·참조 로딩은 별개다. 이번 정합성 검토에서 실제 호스트 통합은 미확인이며, 제품 전체의 지원 여부를 단정하지 않는다. 실제 확인 시 호스트 버전·이벤트·입력·결과를 함께 기록한다.

hook의 도구·입력 경계와 승인해시의 보장 범위는 [가이드북](../../guidebook/guidebook.md)의 "승인과 hook이 확인하는 범위"를 따른다. 독립 비평·검증은 [실행 정본](../../.mpa/runtime/inject/_agent_execution_priority.md)의 격리·산출물·실패 조건을 적용한다.
