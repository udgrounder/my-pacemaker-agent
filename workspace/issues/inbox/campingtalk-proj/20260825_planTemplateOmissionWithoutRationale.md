---
{
  "type": "issue",
  "status": "open",
  "kind": "legacy_issue",
  "canonical_key": "legacy-3d51d5f92493eac0",
  "canonical_issue_key": "legacy-3d51d5f92493eac0",
  "occurrence": "legacy_import",
  "area": "unspecified",
  "observed_release": "unknown",
  "collection_purpose": "review",
  "source_issue_id": "legacy-source-3d51d5f92493eac0",
  "workspace_issue_id": "legacy-workspace-3d51d5f92493eac0",
  "created_at": "2026-08-26T12:19:25+00:00",
  "legacy_source_filename": "20260825_planTemplateOmissionWithoutRationale.md"
}
---
# plan.md 템플릿의 "생략" 표기가 생략 근거 없이 허용됨

**타입**: 방법론 개선
**발견 상황**: `20260825_taxInvoiceExcelUploadDownload` 작업 항목의 plan.md 작성 중, `### minor 판단 근거` 섹션에 템플릿 지시대로 `(major 태스크 — 생략)`만 적고 넘어감. 사용자가 이 부분(및 유사하게 근거 없이 "생략"만 적힌 항목들)을 문제로 지적함.
**적용 범위**: 모든 프로젝트 (MPA `plan_template.md`를 쓰는 모든 태스크)

## 현재 방식

`plan_template.md`의 여러 섹션(`### 사전 조사`, `### minor 판단 근거`, `### 예상 조용한 결정` 등)은 "불필요하면 섹션째 생략" 또는 major/minor 조건에 따라 "생략"이라고만 적도록 되어 있다. 이때 **왜 이 섹션이 이 태스크에 해당하지 않는지에 대한 한 줄 근거를 남기라는 지시가 없다** — 그냥 "생략"이라는 상태만 기록하면 형식적으로 통과된다.

## 개선 방안

템플릿 지시문에 "섹션을 생략할 때는 반드시 생략 사유를 한 줄로 남긴다"는 규칙을 추가한다. 예:
- `### minor 판단 근거` → major 태스크면 `(생략 — 이 태스크는 major로 분류됨: [실패비용 등급 판단 근거 요약])`처럼 상위 판단과 연결된 사유를 남긴다.
- `### 사전 조사`, `### 완료 시 문서 업데이트 대상` 등 "불필요하면 생략" 섹션도 마찬가지로 "불필요한 이유"를 짧게 남긴다.

목적은 "생략"이 늘 형식적 문구가 아니라, 검토자(사용자·다른 에이전트)가 그 판단이 타당했는지 나중에 확인할 수 있는 최소 근거를 남기는 것이다.

## 적용 대상 파일

- `.mpa/runtime/templates/plan_template.md`
- (연동 지시가 있다면) `.mpa/runtime/inject/layer1_design.md`의 "완료 기준" 체크리스트에 "생략 표기에 근거가 있는가"를 추가하는 것도 고려
