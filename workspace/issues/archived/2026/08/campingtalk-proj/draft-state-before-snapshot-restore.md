---
{
  "type": "issue",
  "status": "archived",
  "kind": "methodology_improvement",
  "canonical_key": "draft-state-before-snapshot-restore",
  "canonical_issue_key": "draft-state-before-snapshot-restore",
  "occurrence": "first_observed",
  "area": "ui-editing-workflow",
  "observed_release": "legacy-upgrade-candidate",
  "collection_purpose": "review",
  "source_issue_id": "draft-state-before-snapshot-restore",
  "workspace_issue_id": "campingtalk-proj-draft-state-before-snapshot-restore",
  "created_at": "2026-08-20T09:40:42+00:00",
  "review_status": "rejected",
  "reviewed_at": "2026-08-20T12:18:56+00:00",
  "approved_by": "codex",
  "approval_ref": "user-rejection-request-20260820",
  "decision": "rejected",
  "decided_by": "kjkim",
  "decided_at": "2026-08-21T01:11:13+00:00",
  "decision_reason": "특정 달력 구현의 설계 선택으로 보관할 내용이며 전역 MPA 규칙의 효용이 낮다",
  "follow_up_task": null
}
---

# 임시 UI 편집은 복원보다 draft 상태를 우선 검토
**타입**: 방법론 개선
**발견 상황**: 20260807_rangeCalendarToAutoSetting 태스크에서 달력 닫힘 취소 동작을 구현하는 중 발견
**적용 범위**: 모든 프로젝트

## 현재 방식
취소 가능한 UI 편집에서 원본 상태를 직접 변경한 뒤 스냅샷으로 복원하는 접근을 먼저 선택할 수 있다.

## 개선 방안
명시적 완료 버튼이 있는 UI는 원본 상태와 draft 상태를 분리할 수 있는지 먼저 검토한다. 가능하면 draft만 편집하고 완료 시점에만 원본에 반영해, 복원 이벤트·배경 표시 분기를 줄인다.

## 적용 대상 파일
- `.mpa-workspace/core/agent_rules.md`

## 처리 결과

- 사용자 결정: `rejected`
- 판단자: kjkim
- 판단 근거: 특정 달력 구현의 설계 선택으로 보관할 내용이며 전역 MPA 규칙의 효용이 낮다
