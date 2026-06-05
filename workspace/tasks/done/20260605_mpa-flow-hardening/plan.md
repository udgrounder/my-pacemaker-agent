---
태스크: mpa-flow-hardening
생성일: 2026-06-05
타입: major
실패비용: major
상태: 완료 승인
점검: 미점검
승인해시: 2e4096cdb626310b
---

# 작업 계획서: MPA 흐름 강화

## 요청 원문

> 2 번-> 명시적 복구 플로우를 만들자.  
> 3번 더 단순화 하자.  
> 4번 사용자만 직접 확인 하게 하지 말고 대안을 좀 더 강구하자.  
> 이 순서대로 작업을 진행하자.

## 목적

MPA의 실제 개발 효율을 저해하는 세 지점(승인해시 복구, minor 경량 흐름, 검증 결과 전달)을 순서대로 개선한다.

## 실패 비용 판단

- 타입: `major`
- 실패비용: `major`
- 근거: `.mpa-workspace/` 규칙과 hook 동작을 바꾸며, 설치 대상 프로젝트의 미래 세션 전체에 영향을 준다.

## 수정 순서

1. 승인해시 없음 처리 개선
   - 현재: `code_gate.py`가 승인해시 없음 상태를 자동 등록하고 통과시킨다.
   - 변경: 자동 등록을 제거하고, 명시적 복구 절차를 안내하며 차단한다.
   - 대상: `.mpa-workspace/hooks/code_gate.py`, `.mpa-workspace/hooks/README.md`, `.mpa-workspace/core/agent_rules.md`

2. minor 흐름 단순화
   - 현재: minor도 active/done 이동, INDEX 업데이트, plan 최소 형식을 요구한다.
   - 변경: minor를 “기록은 남기되 운영 부담은 최소”로 재정의한다.
   - 방향: 최소 plan은 유지하되 review/test/docs/Layer2 제안/복잡한 완료 절차를 생략하고, 완료 기록은 한 번에 자동 처리한다.
   - 대상: `.mpa-workspace/core/agent_rules.md`, `.mpa-workspace/inject/layer1_design.md`, `.mpa-workspace/inject/layer1_implement.md`

3. 검증 결과 전달 대안 개선
   - 현재: 메인 에이전트가 review 파일을 읽지 않고 사용자에게 직접 확인만 요청한다.
   - 변경: 편향 방지 원칙은 유지하되, 메인 에이전트가 구조화된 메타 요약만 전달하도록 한다.
   - 방향: 서브에이전트가 `review_summary.md` 또는 반환 메타데이터에 counts/severity/next_action만 남기고, 상세 근거는 review 파일에 둔다.
   - 대상: `.mpa-workspace/inject/layer1_review.md`

4. 완료 확인 질문 규칙 완화
   - 현재: 에이전트가 먼저 “완료 처리할까요?”를 묻지 못한다.
   - 변경: 완료 처리를 물어보는 것은 허용하되, 사용자 승인 없이 완료 처리하는 것만 금지한다.
   - 대상: `.mpa-workspace/core/agent_rules.md`, `.mpa-workspace/inject/layer1_review.md`

5. dist 동기화
   - 변경한 `.mpa-workspace/` 파일을 `dist/.mpa-workspace/`에 동일 반영한다.

## 검증 체크리스트

- [x] 승인해시 없음 상태에서 자동 approve가 더 이상 실행되지 않는다.
- [x] 승인해시 복구 절차가 사용자 확인을 요구한다.
- [x] minor 흐름이 기존보다 짧고, 생략 항목이 명확하다.
- [x] review 결과 전달이 “사용자 직접 확인만”에 의존하지 않는다.
- [x] `.mpa-workspace/`와 `dist/.mpa-workspace/`가 동기화된다.

## 결정 이력

| 시점 | 결정 내용 | 근거 |
|------|---------|------|
| 설계 | 사용자 지정 순서대로 2 → 3 → 4를 처리한다 | 사용자가 명시한 작업 순서 |
| 설계 | MPA 시스템 파일 수정이므로 major로 처리한다 | 모든 미래 세션 행동 규칙에 영향 |
| 구현 전 | 완료 질문 금지는 제거하고 무승인 완료 처리만 금지한다 | 사용자 추가 정정 |
| 구현 | 승인해시 없음은 자동 등록 대신 차단형 복구 안내로 처리한다 | 사후 승인 우회 방지 |
| 구현 | minor는 fast-path로 일반 구현 종료 절차를 우회한다 | 작은 작업의 운영 비용 절감 |
| 구현 | review_summary.md 메타 요약만 메인 에이전트가 읽는다 | 편향 방지와 사용자 부담 절충 |
