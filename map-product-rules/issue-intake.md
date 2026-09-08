# Issue Intake Profile

## Trigger

사용자가 지정 프로젝트의 특정 issue 수집을 요청하거나, 승인된 Runtime update가 dry-run에서 수집 후보를 고지한 뒤 issue batch를 처리할 때.

## Input

project root, safe project-ref, issue filename, 수집 목적. update batch receipt는 아래의 안전한 snapshot 필드만 포함한다.

- `policy_version`, `target_fingerprint`
- safe project-relative `issue_id`
- `raw_checksum`(원문이 아닌 content digest)
- `normalization_version`, `normalized_checksum`, `normalized_identity`
- `classification`, `status`, 비밀값 없는 `reason_code`
- `expected_destination`의 `absent` 또는 기존 안전 fingerprint

원문, 절대 경로, credential 일치 조각은 receipt에 기록하지 않는다. deploy는 이 필드 전체와 issue 집합의 추가·삭제를 재검증하고 차이가 있으면 새 dry-run을 요구한다.

## Producer / Collector Boundary

producer/router는 중앙 issue 생성 전에 내용을 분류한다. `methodology_improvement`만 issue로 작성하며, 프로젝트 기능 보완은 `tasks/`·`docs/`, 아키텍처·계약·역할 함정·도메인 지식은 `workspace/memory/`에 기록한다. 새 도메인 지식은 같은 작업 단위에서 `memory/domains/<domain>/rules.md`, memory INDEX, `project_identity.md`의 가용 도메인 집합을 갱신한다.

source collector는 대상 프로젝트 자산의 작성 주체가 아니다. 이미 잘못 생성된 비방법론 issue는 원본을 보존하고 producer/대상 프로젝트 작업으로 되돌릴 자산 경로와 handoff 사유만 반환한다.

## Allowed Actions

지정된 `methodology_improvement` 또는 dry-run에서 고지·승인된 동일 kind의 update batch만 inbox에 임시 파일을 통해 안전하게 생성한다. machine absolute path는 destination 본문에서 placeholder로 정규화하되 raw 본문은 원본 복원을 위해 commit 완료 전까지 보존한다. 목적지 파일·checksum 존재를 확인한 뒤에만 원본을 삭제한다. 수집 뒤 검토 내용은 사용자에게 먼저 제시한다.

## Checks

공통 순수 preflight를 다음 순서로 실행한다.

1. raw text의 credential 검사
2. raw metadata/type marker의 parsing과 kind 분류
3. 허용 후보 본문의 machine path 정규화
4. normalized checksum/identity와 inbox·archive·destination 충돌 확인

각 단계의 판정은 다음 표를 따른다. 앞 단계의 판정이 뒤 단계보다 우선한다.

| 조건 | 상태 / reason code | 수동 수집 | update dry-run·deploy |
|---|---|---|---|
| kind와 무관하게 raw credential 탐지 | `blocked` / `credential_detected` | 실패, 원본 보존 | dry-run 실패 |
| metadata/type marker가 서로 충돌하거나 파싱 불가 | `blocked` / `metadata_invalid` | 실패, 원본 보존 | dry-run 실패 |
| 명시적 비방법론 kind 또는 신규 파일의 kind 없음 | `not_candidate` / `project_asset` 또는 `kind_missing` | 거부, 원본 보존·handoff | batch 제외·고지, dry-run 성공 가능 |
| 허용 kind이나 필수 metadata·정규화 무결성 오류 | `blocked` / `candidate_invalid` | 실패, 원본 보존 | dry-run 실패 |
| 같은 normalized identity가 inbox/archive에 이미 존재 | `not_candidate` / `already_collected` | 거부, 양쪽 보존 | batch 제외·고지, dry-run 성공 가능 |
| 목적지 filename이 다른 identity로 점유됨 | `blocked` / `destination_conflict` | 실패, 양쪽 보존 | dry-run 실패 |
| 안전한 `methodology_improvement`이고 충돌 없음 | `collectable` / `ready` | 승인된 단일 파일만 이동 | 승인 snapshot의 batch에 포함 |
| dry-run 뒤 source·destination·issue 집합 변경 | `blocked` / `snapshot_changed` | 해당 없음 | deploy 전 중단, 새 dry-run 요구 |

상태와 사유에는 credential 일치 문자열이나 machine path 원문을 노출하지 않는다.

## Gates

명시 요청 또는 update dry-run이 결박한 수집 후보·승인 없이 issue를 이동하지 않는다. update의 읽기 범위는 대상 최상위 `workspace/issues/*.md`로, commit 범위는 승인 snapshot의 `collectable` 원본으로 제한한다. `not_candidate`는 원본을 보존하고 올바른 project asset 경로를 안내하며 collector가 `tasks/`·`docs/`·`memory/`를 자동 수정하지 않는다. 사용자가 채택·기각을 결정하기 전에는 archive하지 않는다.

## Output

inbox issue와 이동 결과 고지. 수집은 목적지 파일 존재 확인 뒤 원본을 삭제하고 원본 부재를 확인한다. 사용자의 기각은 판단 근거를 이슈 파일에 기록한 뒤 즉시 archive하고, 채택은 새 작업 항목 plan.md를 만든 뒤 그 경로를 이슈에 기록하고 즉시 archive한다.

## Failure State

이동 확인 실패 시 원본을 유지·복원하고 차단 이유를 보고한다. 원본이 이동 뒤 새로 생겼다면 두 파일을 보존하고 수동 조정을 요청한다. deploy는 Runtime 교체 전에 receipt 전체를 재검증하고, 교체한 Runtime 검증·config migration 뒤 issue batch를 commit한다. collection 또는 이후 backup·receipt 기록 실패 시 이동 issue와 Runtime·MPA config를 함께 rollback한다.

## Prohibited

raw credential 자동 정제, copy 후 미검증 delete, 목적지 덮어쓰기, 고지 없는 자동 수집, 수집 외 project asset 자동 수정을 하지 않는다. update 수집은 검증 성공 뒤 목적지 존재·checksum·원본 부재를 확인한 경우에만 원본 정리를 완료로 처리한다.
