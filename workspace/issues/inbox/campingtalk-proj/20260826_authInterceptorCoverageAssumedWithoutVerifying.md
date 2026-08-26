---
{
  "type": "issue",
  "status": "open",
  "kind": "legacy_issue",
  "canonical_key": "legacy-b41f40f67b6f5648",
  "canonical_issue_key": "legacy-b41f40f67b6f5648",
  "occurrence": "legacy_import",
  "area": "unspecified",
  "observed_release": "unknown",
  "collection_purpose": "review",
  "source_issue_id": "legacy-source-b41f40f67b6f5648",
  "workspace_issue_id": "legacy-workspace-b41f40f67b6f5648",
  "created_at": "2026-08-26T12:19:25+00:00",
  "legacy_source_filename": "20260826_authInterceptorCoverageAssumedWithoutVerifying.md"
}
---
# 인증 인터셉터 적용 범위를 확인 없이 가정하고 첫 방어 로직을 작성함

**타입**: 방법론 개선
**발견 상황**: `20260826_bookingDrawApplyOwnershipCheck` 작업 항목 진행 중. bookingDrawApplyId 소유권 검증을 위해 컨트롤러에 "비로그인 + bookingDrawApplyId 존재 시 차단" 로직을 먼저 추가했는데, 이때 `pubsec/order` 엔드포인트가 `WebApplicationConfig.checkMemberUrls`에 등록돼 있어 `CheckMemberInterceptor`(로그인 토큰 파싱)가 실제로 실행되는지 확인하지 않은 채 `MemberThreadRepository.getTokenInfo()`가 로그인 여부를 정확히 반영한다고 가정했다. 서브에이전트 검증에서 이 가정이 틀렸음이 드러났고(실제로는 해당 엔드포인트가 목록에 없어 TokenPayload가 항상 null), 사용자가 직접 근본 원인을 짚어준 뒤에야 바로잡았다.
**적용 범위**: 인증/인가 관련 버그 수정 전반 (이 프로젝트처럼 인터셉터/필터 기반 인증에 화이트리스트 방식 경로 등록이 필요한 구조)

## 현재 방식

인증 상태를 참조하는 코드(`MemberThreadRepository.getTokenInfo()` 같은 ThreadLocal/컨텍스트 조회)를 수정할 때, 그 값이 실제로 이 요청 경로에서 채워지는지(인터셉터/필터가 이 URL에 실제로 걸리는지)를 검증하지 않고 "이 API 계층에서 흔히 그렇듯 인증 상태가 정확할 것"이라고 암묵적으로 가정했다.

## 개선 방안

인증/인가 검증 로직을 추가하거나 수정할 때는, 그 값을 채우는 미들웨어(인터셉터/필터/AOP)가 **해당 엔드포인트에 실제로 적용되는지**를 코드(경로 매칭 설정)로 먼저 확인하는 단계를 명시적으로 거친다. "인증 컨텍스트가 있다"와 "인증 컨텍스트가 이 경로에서 신뢰할 수 있게 채워진다"는 별개의 사실이며, 후자를 확인하지 않으면 방어 로직이 형식적으로만 존재하고 실질적으로 우회 가능한 상태가 된다.

## 적용 대상 파일

- `agent_rules_detail.md` "코드 탐색" 섹션 또는 `personas/code_reviewer.md`에 위 원칙을 규칙으로 추가하는 것을 검토
