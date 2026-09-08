# Step 1 독립 비평

## P1 — `issue-create`까지 collector 금지 규칙에 묶여 즉시 자산화 책임이 사라진다

- 위치: `map-product-rules/command-contract.md:16`, `workspace/memory/shared/architecture.md:166-168`, `workspace/tasks/active/20260904_issue_collection_and_domain_assetization/plan.md:35-36,81`
- 영향: 아키텍처와 계획은 도메인 지식을 발견한 producer 세션이 즉시 `memory/domains/<domain>/rules.md`와 두 색인에 기록해야 한다고 요구한다. 그러나 명령 계약은 `issue-create`와 `issue-collect`를 한 행으로 합친 뒤 둘 모두에 project `tasks/docs/memory` 자동 수정 금지를 적용한다. 이 계약대로 구현하면 도메인 지식 후보는 `not_candidate`로 남고 경로 안내만 받을 뿐, 사용자 결정의 핵심인 “발견 즉시 프로젝트 자산화”를 수행할 주체가 없다.
- 권장 수정: `issue-create`(producer/router)와 `issue-collect`(source collector) 계약을 분리한다. project asset 자동 수정 금지는 collector에만 한정하고, producer는 중앙 issue를 만들기 전에 도메인 지식을 memory와 `workspace/memory/INDEX.md`, `project_identity.md`에 같은 작업 단위로 기록하도록 명시한다. 이미 잘못 생성된 issue를 collector가 발견한 경우에는 원본 보존·안내까지만 하고 producer/대상 프로젝트 작업으로 반환한다는 handoff도 고정한다.

## P1 — deploy의 issue 수집이 “대상 workspace를 읽거나 변경하지 않는다”는 상위 불변식과 충돌한다

- 위치: `MAP_PRODUCT_RULES.md:25-27`, `workspace/memory/shared/architecture.md:13`, `map-product-rules/command-contract.md:13-14`
- 영향: 새 dry-run은 대상 `workspace/issues/` inventory와 원문을 읽어 preflight하고, deploy는 collectable 원본을 제거해야 한다. 반면 상위 불변식과 아키텍처 표는 install/deploy/rollback이 대상 `workspace/`를 보존하며 읽거나 변경하지 않는다고 단정한다. 구현자가 어느 계약을 우선하느냐에 따라 issue 수집이 아예 실행되지 않거나, 배포가 사용자 workspace를 임의 변경하는 것으로 해석될 수 있다.
- 권장 수정: 상위 불변식에 승인된 issue collection만의 좁은 예외를 명시하고 Runtime 교체와 별도 권한·트랜잭션임을 선언한다. dry-run에는 읽기 허용 범위를 지정 issue 파일과 안전한 inventory metadata로, commit에는 승인 snapshot의 `collectable` 원본 제거로 제한한다. collection 실패 시 Runtime/config 교체 전 중단하는지, 교체 후라면 무엇까지 함께 rollback하는지도 command contract에 순서와 원자성으로 고정한다.

## P1 — 세 상태의 판정 우선순위와 deploy 차단 조건이 구현 가능한 수준으로 정의되지 않았다

- 위치: `map-product-rules/issue-intake.md:17,21,29`, `map-product-rules/command-contract.md:13,16`, `workspace/tasks/active/20260904_issue_collection_and_domain_assetization/plan.md:41,82,85`
- 영향: 문서는 결과 이름만 나열하고 credential, 허용되지 않은 kind, 파싱 실패, 중복, archive 충돌, destination 충돌, source 변경이 각각 `blocked`/`not_candidate` 중 무엇인지 정의하지 않는다. 특히 raw credential 검사가 kind보다 먼저이므로 credential을 포함한 비방법론 파일은 `blocked`가 될 수 있는데, deploy 차단 문구는 “`blocked` 방법론 issue”만 실패시킨다. kind를 신뢰할 수 없는 파싱 실패나 destination 충돌도 배포를 막는지 불명확해 manual collection과 dry-run/deploy가 서로 다른 결론을 낼 수 있다.
- 권장 수정: 검사 결과별 상태와 우선순위를 표로 고정한다. 최소한 raw credential 탐지는 kind와 무관하게 `blocked`, 유효하게 파싱됐지만 허용되지 않은 kind는 `not_candidate`, 허용 kind의 무결성·destination·snapshot 오류는 `blocked`처럼 분류하고, 각 상태의 manual 결과·update batch 포함 여부·dry-run 성공 여부를 함께 정의한다. “blocked 방법론 issue”처럼 판정에 실패한 kind를 전제로 하는 표현은 제거하고 보안 차단과 수집 가능성 차단을 별도 코드/필드로 나누는 편이 안전하다.

## P2 — canonical preflight 순서가 두 정본에서 다르다

- 위치: `map-product-rules/issue-intake.md:17`, `map-product-rules/command-contract.md:16`, `workspace/tasks/active/20260904_issue_collection_and_domain_assetization/plan.md:82`
- 영향: issue-intake와 계획은 `raw credential → kind → machine path normalization → identity`를 요구하지만 command contract는 `raw credential → machine path normalization → kind → identity` 순서로 적었다. raw 검사가 첫 단계라는 보안 요구는 유지되지만, kind 판정이 raw 본문과 normalized 본문 중 무엇을 보는지와 `not_candidate`의 checksum/identity 생성 여부가 달라져 공통 순수 preflight라는 전제가 깨진다.
- 권장 수정: 세 문서에서 정확히 같은 순서를 사용하고 각 단계의 입력 표현(raw 또는 normalized)을 명시한다. 권장 순서는 계획대로 raw credential 검사, raw metadata 기반 kind 분류, 본문 경로 정규화, normalized checksum/identity 및 충돌 검사다.

## P2 — dry-run receipt가 어떤 raw 상태를 결박하는지 불명확해 TOCTOU 검증과 비밀 비노출을 동시에 보장할 수 없다

- 위치: `workspace/memory/shared/architecture.md:170`, `map-product-rules/issue-intake.md:9`, `map-product-rules/command-contract.md:13-14`, `workspace/tasks/active/20260904_issue_collection_and_domain_assetization/plan.md:82,85`
- 영향: 계획 Step 2는 `raw checksum`을 preflight 출력으로 요구하지만 Step 5, architecture, intake, command contract는 receipt에 `raw inventory`와 `normalized checksum`만 결박한다고 적는다. `raw inventory`가 경로/원문을 뜻하면 receipt의 issue 원문·machine path·credential 비노출 금지와 충돌하고, 단순 파일명 목록을 뜻하면 dry-run 뒤 raw 본문이 바뀌어도 같은 normalized checksum으로 통과할 여지가 있다. deploy 재검증 대상도 generic `issue inventory`로만 표현돼 승인 snapshot 일치 조건이 불완전하다.
- 권장 수정: receipt schema를 구현 전에 명시한다. 예를 들어 safe project-relative issue id, raw content checksum, normalization policy version, normalized checksum/identity, 판정 상태, expected destination absence/fingerprint만 저장하고 원문·절대경로·match fragment는 저장하지 않는다. deploy는 이 필드 전체와 후보 집합의 추가·삭제를 재검증하고 하나라도 달라지면 새 dry-run을 요구하도록 계약화한다.
