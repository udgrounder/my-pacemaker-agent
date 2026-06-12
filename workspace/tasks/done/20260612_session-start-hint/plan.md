---
태스크: session-start-hint
생성일: 2026-06-12
타입: minor
실패비용: minor
상태: 완료 승인
승인해시: d4c5381357b430ea
---

# 작업 계획서: session-start-hint

**파생 출처:** discussion-mode 후속 — 진행 중 작업이 없는(idle) 세션에서 사용자가 토론 모드 존재를 모르는 디스커버리 문제. (프로젝트가 새것인지 여부와 무관 — "세션을 새로 연 시점 + idle"이 기준)

## 에이전트 보고

### 사용자 결정 필요
없음

### 암묵적 결정
- **트리거 = "세션 시작 + 진행 중 태스크 없음(idle)"** — 오직 이 두 조건. **프로젝트가 새것인지(첫 실행/done 비었는지)는 보지 않는다.** 매 세션 시작 시 idle이면 1회 안내. session_start 훅이 세션당 1회 발화하므로 "이후 침묵"은 자연 보장(같은 세션 내 반복 안 함). (사용자 확정: "세션을 새로 연 경우 한정해서 안내하고 이후 침묵")
- 진행 중 태스크가 있으면 기존 태스크 목록 안내가 우선 — 두-경로 힌트는 idle일 때만.

### 에이전트 가정
없음 (session_start.py 동작 실제 확인함)

### minor 판단 근거
- 단일 관심사: idle 세션 시작 안내
- 방법 자명: 기존 idle 분기 메시지에 힌트 추가 + §1 idle 문구 교체
- git reset 복구 가능
- 취향: 안내 문구 정도

## 요청 원문
"처음 실행하면 작업을 하거나 논의를 하거나 할 것 같은데 힌트를 어떻게 줄까" → "세션을 새로 연 경우 한정 안내, 이후 침묵"

## 목적
idle 상태로 세션을 열면, 사용자가 **작업(개발)** 과 **논의(토론 모드)** 두 경로를 한 줄로 안내받게 한다.

## 구현 단계
- [ ] Step 1 — `.mpa-workspace/hooks/session_start.py` idle 분기("진행 중인 태스크 없음")에 두-경로 안내 지시 추가
- [ ] Step 2 — `.mpa-workspace/core/agent_rules.md §1` "진행 중 태스크가 없는 경우" 문구를 "세션 시작 시 두 경로 1회 안내 후 대기"로 교체
- [ ] Step 3 — `workspace/README.md` + `dist/workspace/README.md` "시작하기"에 논의 예시 1줄 추가
- [ ] Step 4 — dist 자동 미러 확인 (.mpa-workspace 편집분)

## 수정 대상 파일
| 파일 | 변경 |
|------|------|
| `.mpa-workspace/hooks/session_start.py` | idle 분기에 두-경로 안내 텍스트 |
| `.mpa-workspace/core/agent_rules.md` | §1 idle 대기 → 1회 안내 후 대기 |
| `workspace/README.md`, `dist/workspace/README.md` | "시작하기"에 논의 예시 |
| dist 미러 | 자동 동기화 |
