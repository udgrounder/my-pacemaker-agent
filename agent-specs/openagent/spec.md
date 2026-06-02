---
agent: openagent
tool: OpenAgent (미확인)
---

# OpenAgent — Agent Spec

## 감지 조건

미정 — 설치 시 실행 중인 AI agent에게 질의하여 결정한다.

## 질의 절차

설치 시 실행 중인 AI agent에게 아래를 순서대로 확인한다:

1. "OpenAgent의 진입점 파일은 무엇인가요? (예: OPENAGENT.md, .openagent/config.md)"
2. "규칙/설정 파일은 어느 폴더에 두어야 하나요?"
3. "파일 import 문법을 지원하나요? 지원한다면 어떤 문법인가요?"
4. "hook(이벤트 기반 자동 실행/도구 차단/세션시작 컨텍스트 주입)을 지원하나요?
   지원한다면 설정 파일 위치·형식과 이벤트 명칭(세션시작/도구실행전/응답종료에 해당하는 것)은?"

## 확인 후 처리

질의 결과를 바탕으로:
1. 진입점 파일에 Agents Workspace 섹션 추가
2. 규칙 파일(`pacemaker.md`)을 해당 폴더에 생성
3. hook을 지원하면 `.mpa-workspace/hooks/` 의 3개 스크립트
   (`session_start.py` / `code_gate.py` / `turn_end.py`)를 해당 이벤트에 등록한다.
   차단은 exit 2 + stderr 공통, 스크립트는 `--agent <agent>` 플래그를 받는다.
4. 이 `spec.md`의 감지 조건·폴더 규칙·설치 처리·hook 항목을 업데이트하여 다음 설치에 재사용

## 폴더 규칙

TBD

## 설치 처리

TBD
