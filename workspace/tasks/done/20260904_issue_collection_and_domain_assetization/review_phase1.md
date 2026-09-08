# 1차 독립 검증 결과

## 검증 범위와 판정

- 검증 대상: `issue_collection_and_domain_assetization` 최신 구현 전체
- 기준 자료: `plan.md`, `workspace/memory/shared/architecture.md`, `map-product-rules/issue-intake.md`, `map-product-rules/command-contract.md`, 최신 `release_manager.py`와 테스트
- 제외 자료: `changelog.md`, 기존 review 산출물
- 검증 방식: 계획·계약·코드 직접 대조, 지정 실패 반례 실행, 전체 회귀 테스트, Runtime source/dist parity와 기존 release bundle audit
- actionable finding: **0건**
- 최종 verdict: **승인**

## 완료 기준별 검증

| plan.md 완료 기준 | 독립 검증 근거 | 결과 |
|---|---|---|
| 중앙 수집 후보는 `methodology_improvement`로 한정 | Runtime 생성 규칙과 source `issue-create`·preflight가 방법론 개선만 허용한다. kind 누락과 프로젝트 자산은 원본을 보존한 `not_candidate`로 분리되며, manual 수집 오류는 안전한 producer handoff를 반환한다. | 통과 |
| 프로젝트 보완·결정·역할 함정·도메인 지식은 project asset으로 라우팅 | architecture와 issue intake 계약은 기능 보완을 `tasks/docs`, 아키텍처·계약·역할·도메인 지식을 `memory`로 보낸다. collector는 대상 자산을 수정하지 않고 원본을 보존한다. | 통과 |
| 도메인 지식은 즉시 memory에 자산화하고 `knowledge_promotion` issue를 만들지 않음 | Runtime detail과 Layer 2가 domain rules·memory INDEX·project identity 동기화를 요구한다. Runtime knowledge는 자동 승격이 아닌 명시적 MPA 변경 작업으로만 관리된다. | 통과 |
| credential-like 내용 강제 거부와 원본 보존 | raw credential 검사가 kind 분류와 경로 정규화보다 선행한다. preflight 이후 credential이 삽입되는 경쟁 반례도 raw checksum 불일치로 중단되어 원본을 남기고 destination을 만들지 않는다. | 통과 |
| 머신 절대 경로의 안전한 정규화와 의미 보존 | 중앙 본문은 프로젝트 경로를 `<project-root>/...`, 외부 경로를 `<redacted-path>/...`로 바꾼다. identity는 머신 root만 제거하고 안정 anchor 또는 상대 suffix를 보존한다. | 통과 |
| 머신 독립 중복 identity와 서로 다른 경로 구분 | legacy absolute path와 신규 placeholder path는 같은 identity로 중복 탐지된다. `src/one.py`와 `src/two.py`는 서로 다른 후보로 유지된다. | 통과 |
| dry-run 3상태와 안전한 승인 snapshot 결박 | receipt는 safe issue ID, raw·normalized checksum, normalized identity, classification/status/reason, destination 상태만 기록한다. `blocked`는 dry-run을 중단하고 `not_candidate`는 원본을 보존한 채 batch에서 제외한다. deploy는 전체 issue 집합과 snapshot을 재검증한다. | 통과 |
| 필수 metadata·candidate 무결성 강제 | structured issue의 필수 metadata는 `status == "open"` 및 비어 있지 않은 문자열이어야 한다. list 같은 truthy 비문자열은 `blocked/candidate_invalid`로 판정된다. | 통과 |
| 수집 실패 시 destination 정리와 원본 무손실 복원 | source는 삭제 전에 같은 디렉터리의 quarantine으로 atomic rename된다. regular-file 여부와 승인 checksum을 확인한 뒤에만 제거하며, checksum 읽기 `OSError`, checksum 불일치, quarantine unlink 실패 모두 source를 원래 경로로 복원하고 destination·숨은 quarantine 파일을 남기지 않는다. | 통과 |
| symlink·unsafe issue ID·no-clobber | project issue 디렉터리와 개별 issue symlink를 거부한다. unsafe filename은 원문을 receipt에 노출하지 않고 hash 기반 안전 ID와 `unsafe_issue_id`로 차단한다. destination은 hard-link no-clobber와 checksum 검증 후에만 source 정리를 시작한다. | 통과 |
| 복수 batch의 issue별 checksum 결박 | update batch의 destination tuple이 각 issue의 raw checksum을 함께 보존한다. 서로 다른 두 collectable issue가 각 checksum으로 정상 수집된다. | 통과 |
| deploy recovery 단계 독립성 | issue rollback 실패와 무관하게 Runtime·config·replacement·receipt·history·created paths 복구를 각각 시도하고 실패 단계를 기록한다. issue 복구 실패 반례에서도 이전 Runtime이 복원된다. | 통과 |
| Runtime source/dist, 전체 테스트, release audit | 전체 142개 테스트가 통과했다. Runtime source와 `dist/.mpa/runtime` 대응 파일 parity가 일치하고 기존 immutable release bundle 13개 audit가 통과했다. 새 release는 생성하지 않았다. | 통과 |
| 지정 `campingtalk-proj` 이슈의 안전한 수집 | 중앙 inbox에 `20260824_codeGateHookCwdDrift.md`가 존재하고 producer 원본은 부재한다. 중앙 본문은 raw 머신 경로 대신 `<project-root>` 표현으로 재현 의미를 보존한다. | 통과 |

## 핵심 반례 재현 결과

아래 12개는 이번 1차 독립 검증 전체 과정에서 코드 대조와 회귀 실행으로 누적 재현한 반례이며 모두 통과했다. 이 중 마지막 최종 보완과 직접 관련된 8개를 별도 집중 테스트 명령으로 다시 실행했고, 나머지 반례는 전체 142개 회귀 테스트와 앞선 독립 재현 결과에서 재확인했다.

1. quarantine checksum 읽기에서 `OSError` 발생 → source 원문 복원, destination 부재, 숨은 quarantine 파일 부재
2. quarantine unlink 실패 → source 원문 복원, destination·quarantine 정리
3. 삭제 직전 source 변경 → atomic quarantine checksum 불일치로 거부, 변경된 source 보존
4. preflight 직후 source 변경·credential 삽입 → 승인 snapshot 불일치로 거부
5. 필수 metadata가 list 등 비문자열 → `blocked/candidate_invalid`
6. 비방법론 project asset 수동 수집 → `not_candidate`, `handoff=producer:tasks/docs/memory`, 원본 보존
7. unsafe filename → 안전 hash ID만 기록, 원본 보존
8. symlinked issue 디렉터리·개별 파일 → 읽기·이동 전 거부
9. 서로 다른 두 collectable issue batch → issue별 raw checksum으로 모두 수집
10. 머신 root만 다른 동일 이슈 → 동일 identity로 중복 탐지
11. 상대 suffix가 다른 이슈 → 별도 identity로 구분
12. issue rollback 실패 → Runtime recovery 계속 수행

최종 보완 직접 집중 테스트 결과(누적 반례 12개 중 8개): `Ran 8 tests` / `OK`  
전체 독립 검증 누적 반례: 12개 / 모두 통과  
전체 테스트 결과: `Ran 142 tests` / `OK`

## 계약 및 불변식 대조

- preflight 순서는 raw credential → raw metadata/type marker 및 kind → machine path 정규화 → normalized checksum/identity·충돌 검사로 계약과 구현이 같다.
- manual과 update collection은 preflight raw checksum을 실제 source bytes와 다시 비교하고, 삭제 시점에는 atomic quarantine checksum으로 재결박한다.
- 필수 metadata의 타입과 공백 제거 후 비어 있지 않음을 확인해 truthy 객체 우회를 허용하지 않는다.
- 비방법론 후보는 collector가 자동 자산화하지 않고 안전한 handoff와 함께 producer 원본을 보존한다.
- 수집 실패에서는 검증된 destination을 정리하고 source를 원래 이름으로 복원하며, 임시 destination·quarantine 파일을 제거한다.
- destination 충돌은 기존 중앙 파일을 덮어쓰지 않는다.
- deploy recovery의 각 단계는 독립 실행되고 불완전 복구는 안전한 receipt에 단계명으로 기록된다.
- Runtime source/dist 규칙과 issue·project memory·공용 knowledge 소유 경계가 architecture 및 command 계약과 일치한다.

## 최종 결론

최신 구현은 plan.md의 완료 기준과 변경 불가 제약을 충족한다. 특히 최종 추가 수정인 quarantine checksum 읽기 실패 복원, metadata 문자열 무결성, producer handoff 원본 보존을 실제 반례로 확인했다. 보안·분류·경로·snapshot·원자 이동·rollback·기존 호환성 측면의 추가 actionable finding은 없다.

**Verdict: 승인**
