---
{
  "type": "issue",
  "status": "archived",
  "kind": "methodology_improvement",
  "canonical_key": "legacy-bfa44e7e148e4e82",
  "canonical_issue_key": "legacy-bfa44e7e148e4e82",
  "occurrence": "legacy_import",
  "area": "unspecified",
  "observed_release": "unknown",
  "collection_purpose": "review",
  "source_issue_id": "legacy-source-bfa44e7e148e4e82",
  "workspace_issue_id": "legacy-workspace-bfa44e7e148e4e82",
  "created_at": "2026-11-17T03:15:34+00:00",
  "legacy_source_filename": "20261116_unverified_source_granularity_assumptions.md",
  "decision": "accepted",
  "decided_by": "user",
  "decided_at": "2026-11-17T03:22:27+00:00",
  "decision_reason": "사용자가 이슈 채택과 공통 원칙의 계획서 작성을 요청했다. 질문 전 전제 확인, 미확인 가정의 연쇄 확대 방지, 전제 변경 시 기존 답변 재검토는 MPA 공통 방법론으로 반영하고 중요한 가상 위험의 검토는 유지한다. 프로젝트별 수수료·배분 업무 규칙은 제외한다.",
  "follow_up_task": "workspace/tasks/done/20261117_premise_grounded_design_questions/plan.md"
}
---
# 원천 데이터 단위 확인 전 가정 기반 업무 질문 방지
**타입**: 방법론 개선
**발견 상황**: transactionLedgerDesign 설계 인터뷰에서 거래별 확정 채널·PG 수수료가 있는 업무에 합계만 존재하는 경우를 가정하고 비율 배분·끝전 질문을 연속 제시했다. 사용자 정정으로 현재 범위에서 철회했다.
**적용 범위**: 모든 프로젝트

## 현재 방식
확인되지 않은 예외를 사실처럼 다음 결정 항목으로 제시하고, 그 가정에 대한 답변을 바탕으로 후속 설계를 확대했다. 실제 필요와 가정의 적용 범위를 확인하지 않아 사용자 부담과 불필요한 테이블이 늘었다.

## 개선 방안
원천의 거래 단위·확정 값 존재 여부를 근거 또는 사용자 설명으로 먼저 확인한다. 확인되지 않은 예외는 사실/가정/후순위 가능성으로 구분하고 현재 업무에 필요한 질문부터 한다. 기존 사용자 답변도 전제 가정이 달라지면 적용 범위를 재검토하며 철회된 가정은 이력으로만 보존한다.

## 적용 대상 파일
- `<project-root>/docs/02-spec/finance/transaction-ledger-model.md`
- `<project-root>/workspace/tasks/active/20261113_transactionLedgerDesign/changelog.md`
- Agent의 요구사항 인터뷰 및 다음 업무 결정 질문 선정 절차

## 처리 결과

- 사용자 결정: `accepted`
- 판단자: user
- 판단 근거: 사용자가 이슈 채택과 공통 원칙의 계획서 작성을 요청했다. 질문 전 전제 확인, 미확인 가정의 연쇄 확대 방지, 전제 변경 시 기존 답변 재검토는 MPA 공통 방법론으로 반영하고 중요한 가상 위험의 검토는 유지한다. 프로젝트별 수수료·배분 업무 규칙은 제외한다.
- 연결 작업: `workspace/tasks/done/20261117_premise_grounded_design_questions/plan.md`
