---
agent: openagent
tool: OpenAgent (실험적·수동 설정 지원)
---

# OpenAgent — Agent Spec

> **지원 상태: 실험적·수동 설정.** `install.py`는 MPA Runtime만 설치하며 OpenAgent의 진입점·규칙 파일·hook을 자동으로 연결하지 않는다. 아래 계약을 실제 환경에서 확인한 뒤에만 수동 설정한다. 확인 전에는 설치 완료를 OpenAgent 연결 완료로 해석하지 않는다.

## 감지 조건

미정 — 설치 시 실행 중인 AI agent에게 질의하여 결정한다.

## 질의 절차

수동 설정을 시작할 때 실행 중인 AI agent 또는 공식 문서에서 아래를 순서대로 확인한다:

1. "OpenAgent의 진입점 파일은 무엇인가요? (예: OPENAGENT.md, .openagent/config.md)"
2. "규칙/설정 파일은 어느 폴더에 두어야 하나요?"
3. "파일 import 문법을 지원하나요? 지원한다면 어떤 문법인가요?"
4. "hook(이벤트 기반 자동 실행/도구 차단/세션시작 컨텍스트 주입)을 지원하나요?
   지원한다면 설정 파일 위치·형식과 이벤트 명칭(세션시작/도구실행전/응답종료에 해당하는 것)은?"

## 확인 후 처리

확인된 결과를 바탕으로 수동으로:
1. 진입점 파일에 Agents Workspace 섹션 추가
2. 규칙 파일(`pacemaker.md`)을 해당 폴더에 생성
3. hook을 지원하면 `.mpa/runtime/hooks/` 의 3개 스크립트
   (`session_start.py` / `code_gate.py` / `turn_end.py`)를 해당 이벤트에 등록한다.
   차단은 exit 2 + stderr 공통, 스크립트는 `--agent <agent>` 플래그를 받는다.
4. 이 `spec.md`의 감지 조건·폴더 규칙·설치 처리·hook 항목을 업데이트하여 다음 설치에 재사용한다. 검증되지 않은 추정값은 기록하지 않는다.

## 폴더 규칙

TBD

## 설치 처리 (자동화되지 않음)

`install.py --agents openagent`는 Runtime·workspace 골격만 설치하고 이 문서의 자동 연결을 수행하지 않는다. OpenAgent 연결은 위 확인 절차를 마친 뒤 사용자가 관리하는 별도 수동 설정이다.
