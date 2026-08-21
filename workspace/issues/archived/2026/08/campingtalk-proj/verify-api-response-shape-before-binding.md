---
{
  "type": "issue",
  "status": "archived",
  "kind": "methodology_improvement",
  "canonical_key": "verify-api-response-shape-before-binding",
  "canonical_issue_key": "verify-api-response-shape-before-binding",
  "occurrence": "first_observed",
  "area": "external-api-contract",
  "observed_release": "legacy-upgrade-candidate",
  "collection_purpose": "review",
  "source_issue_id": "verify-api-response-shape-before-binding",
  "workspace_issue_id": "campingtalk-proj-verify-api-response-shape-before-binding",
  "created_at": "2026-08-20T09:40:42+00:00",
  "review_status": "rejected",
  "reviewed_at": "2026-08-20T12:18:56+00:00",
  "approved_by": "codex",
  "approval_ref": "user-rejection-request-20260820",
  "decision": "rejected",
  "decided_by": "kjkim",
  "decided_at": "2026-08-21T01:11:13+00:00",
  "decision_reason": "기존 탐색과 계약 확인에 포함되는 기본 행동이라 별도 전역 규칙의 효용이 낮다",
  "follow_up_task": null
}
---

# API 응답 구조를 코드 반영 전에 확인
**타입**: 방법론 개선
**발견 상황**: `20260810_calendarHolidayAndBookingDaysPolicy`에서 `maxBookingDays` 응답의 `bookingOpenMaxDate` 경로를 추정해 한 차례 잘못 바인딩했다.
**적용 범위**: 모든 프로젝트

## 현재 방식

기존 코드의 객체 구조나 이름을 근거로 외부 API 응답의 중첩 구조를 추정해 프론트 바인딩을 구현할 수 있다.

## 개선 방안

외부 API 필드를 새로 사용할 때는 실제 응답 JSON, DTO 또는 컨트롤러 계약 중 하나로 경로를 먼저 확인하고 구현·검증 기록에 남긴다.

## 적용 대상 파일

- `.mpa/runtime/core/agent_rules.md`

## 처리 결과

- 사용자 결정: `rejected`
- 판단자: kjkim
- 판단 근거: 기존 탐색과 계약 확인에 포함되는 기본 행동이라 별도 전역 규칙의 효용이 낮다
