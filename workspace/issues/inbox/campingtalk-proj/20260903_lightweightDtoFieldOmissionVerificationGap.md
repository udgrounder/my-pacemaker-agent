---
{
  "type": "issue",
  "status": "open",
  "kind": "methodology_improvement",
  "canonical_key": "legacy-901551dcf70e8efd",
  "canonical_issue_key": "legacy-901551dcf70e8efd",
  "occurrence": "legacy_import",
  "area": "unspecified",
  "observed_release": "unknown",
  "collection_purpose": "review",
  "source_issue_id": "legacy-source-901551dcf70e8efd",
  "workspace_issue_id": "legacy-workspace-901551dcf70e8efd",
  "created_at": "2026-09-04T01:07:51+00:00",
  "legacy_source_filename": "20260903_lightweightDtoFieldOmissionVerificationGap.md"
}
---
# 경량 DTO 신규 도입 시, 검증 체크리스트가 "기존 대비 필드 삭제 여부"를 확인하지 않음

**타입**: 방법론 개선
**발견 상황**: `20260903_nolChannelCampListEnhance` 태스크 — 공유 클래스(`ChannelCampMappingResult`)를 다른 컨트롤러(홈페이지·파트너 API)로부터 보호하기 위해 신규 경량 결과 클래스(`ChannelSettlementCampResult`)를 도입하면서, 기존 클래스에 있던 `latestSettlementDate` 필드를 SELECT 절 설계 시 빠뜨렸다. 이 필드는 `adjustNol.mustache`(동기화 화면)의 "동기화 기준일" 컬럼이 실제로 사용하고 있었는데, 1차·2차 에이전트 검증(review_phase1.md, review_phase2.md) 모두 이를 발견하지 못했고, 코드 리뷰 관점에서 "D절(adjustNol 프런트) 정합성 확인"으로 통과 처리됐다. 실제로는 사용자가 "엑셀 업로드 처리시에 캠핑장 조회하는 부분은 문제 없어?"라고 직접 질문해 에이전트가 재조사하는 과정에서 발견됐다.
**적용 범위**: 모든 프로젝트 (기존 공유 DTO/Result 클래스를 대체하는 신규 경량 클래스를 도입하는 모든 리팩터링 작업)

## 현재 방식

`layer1_review.md`의 검증 체크리스트(1.1 설계 정합성, 1.5 UI/UX 및 기능 동작)는 "plan.md의 각 step이 구현됐는가", "요구사항 명세 완료 기준을 충족하는가"만 확인한다. 신규 결과 타입이 대체하는 **기존 타입의 필드 목록과 diff**를 명시적으로 대조하는 항목이 없다. 이번 태스크의 plan.md도 "수정 대상 파일"에 신규 클래스의 필드를 나열했지만, "기존 `ChannelCampMappingResult`가 가진 필드 중 소비 화면(JS/mustache)이 실제로 쓰는 필드는 무엇인가"를 사전에 grep으로 전수 확인하는 단계가 없었다.

## 개선 방안

- `layer1_design.md`(또는 `layer1_implement.md`)에 "기존 공유 타입을 신규 전용 타입으로 대체/분리하는 경우, 소비 측(프론트 JS/템플릿, 다른 서비스 메서드)의 필드 접근 전수 목록(`grep -oE "camp\.[a-zA-Z]+"` 류)을 사전에 뽑아 신규 타입 설계에 반영한다"는 체크 항목 추가.
- `layer1_review.md`의 1.1 설계 정합성 체크리스트에 "신규/변경된 DTO·Result 클래스가 있다면, 대체 대상 기존 타입과의 필드 diff를 확인했는가?"를 명시적 항목으로 추가. 특히 "필드를 추가했는가"뿐 아니라 "필드를 빠뜨리지 않았는가"를 대칭적으로 검증하도록 문구를 조정.
- 이런 종류의 회귀는 코드만 봐서는 "무엇이 없다"를 알아차리기 어렵고(존재하지 않는 것의 부재를 인지해야 함), "무엇이 있었는데 사라졌는가"를 원본과 대조해야 발견되므로, 검증 프롬프트에 "이전 버전(git diff의 `-` 라인)에서 삭제된 필드가 다른 곳에서 여전히 참조되는지" 확인하라는 지시를 명시하면 재발을 줄일 수 있다.

## 적용 대상 파일
- `.mpa/runtime/inject/layer1_review.md`
- `.mpa/runtime/inject/layer1_design.md`
