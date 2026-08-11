# [처리] 승인 — 2026-06-12 / 적용: 20260612_discussion-mode (agent_rules.md §2/§3/§4, personas/discussion_partner.md, inject/discussion_mode.md). code_gate 마찰은 workspace/exploration/ 통합으로 자동 해소(code_gate.py 변경 없음).

# 토론 모드(discussion)를 독립 라우팅 유형으로 신설

**타입**: 방법론 개선
**발견 상황**: 사용자가 "discussion 모드에서 멀티에이전트 효용성을 논의하고 회의록에 기록"을 요청. 에이전트가 이를 minor 개발 태스크(plan.md·approve·GATE 2·완료 처리)로 처리했고, 사용자가 정정함 — "토론 모드는 개발이 아니라, 특정 주제를 심도있게 논의하며 의견을 주고받고, 그 과정과 결과를 문서로 남기는 모드".
**적용 범위**: 모든 프로젝트

## 현재 방식
- agent_rules.md 라우팅 표에 "토론/논의" 유형이 없다.
- 문서 산출물이 있으면 자동으로 개발 파이프라인(설계→구현→검증→완료, GATE)으로 흡수된다.
- 결과: ① 다회 의견 교환 없이 1회성 결론을 내고 ② "완료 처리/GATE 2"로 종료를 압박하는 잘못된 프레임이 됨.
- 또한 `think-more/`가 code_gate ALLOW_PREFIXES에 없어, 토론 기록을 남기려면 `구현 중` 태스크가 강제되는 구조적 마찰이 있다.

## 개선 방안
- 라우팅 표에 **토론 모드** 추가. 발화 힌트: "논의하고 싶어", "토론하자", "~에 대해 의견을 나누자", "discussion 모드".
- 토론 모드의 성격 명문화:
  - 개발 파이프라인(설계/구현/검증/완료, GATE 1·2)을 **적용하지 않는다.**
  - 핵심은 **다회 의견 교환** — 1회성 결론·기록으로 끝내지 않는다. 에이전트는 동조(`feedback_concept_precision`) 없이 입장을 개진하고 반론을 받는다.
  - 산출물은 **논의 과정과 결과를 담은 living document**(회의록). 토론이 진전될 때마다 갱신.
  - "완료 처리"가 아니라 **사용자가 토론을 마치겠다고 할 때** 종료.
- 기록 위치: `think-more/discussion/` (자유 서술). code_gate가 토론 기록 경로를 막지 않도록 처리 방안 검토 — 옵션: (a) `think-more/`를 ALLOW_PREFIXES에 추가, (b) 토론 모드 전용 경량 상태.

## 적용 대상 파일
- `.mpa-workspace/core/agent_rules.md` (라우팅 표 + 토론 모드 섹션)
- `.mpa-workspace/hooks/code_gate.py` (think-more/ 게이트 마찰 해소 검토)
- 동기화: `dist/.mpa-workspace/`
