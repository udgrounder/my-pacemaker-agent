---
태스크: issue_collection_and_domain_assetization
생성일: 2026-09-04
타입: major
실패비용: critical
상태: 완료 승인
승인해시: reqspec-v1:1a56d74edce25374
승인대상: 요구사항 명세
---

# 작업 계획서: 이슈 수집과 도메인 지식 자산화 경계 정립

**파생 출처:** `campingtalk-proj` 이슈 수집 점검 — 정상적인 MPA 개선 이슈가 머신 절대 경로 때문에 차단되고, 도메인 지식이 이슈 승격 경로와 혼재하는 문제에서 파생

---

## 요구사항 명세

### 요청 기준

사용자는 실제 수집이 차단된 이슈를 통해 이슈 생성·수집 규칙 전체의 정합성을 점검하도록 요청했다. 추가로 도메인 지식은 중앙 이슈로 생성·수집하지 않고 발견한 프로젝트의 자산으로 즉시 기록해야 한다고 결정했다.

### 목적

MPA 방법론 개선 이슈만 중앙 수집·검토 흐름으로 이동하게 하고, 프로젝트 도메인 지식과 기억은 이슈를 거치지 않고 해당 프로젝트 `workspace/memory/` 자산으로 관리한다. 이슈 본문의 실행 환경 경로 때문에 유효한 개선이 유실되지 않도록 생성·사전 검사·수집 계약을 일치시킨다.

### 범위·제외 범위

- 범위: Runtime 이슈 판정·생성 규칙, 도메인 memory 자산화, Layer 2, source 이슈 preflight·정규화·원자 수집, deployment dry-run, kind 계약, 회귀 테스트와 운영 문서.
- 범위: 차단된 `20260824_codeGateHookCwdDrift.md`를 새 계약으로 안전하게 수집하고 목적지 존재·원본 부재를 확인한다.
- 제외 범위: 개별 수집 이슈의 채택·기각, `code_gate.py` cwd 문제 자체 수정, 기존 inbox·archive·Runtime knowledge 소급 재작성, 새 공용 지식 큐레이션 기능, credential signature 확장, Windows/UNC/file-URI 경로 탐지 확장, process crash 회복 journal, release 생성·배포.

### 완료 기준

- 새 중앙 수집 후보는 `methodology_improvement`로 한정되고, 프로젝트 기능 보완·아키텍처 결정·역할 함정·도메인 지식은 `tasks/`, `docs/`, `workspace/memory/` 자산으로 라우팅된다.
- 도메인 지식은 발견 즉시 `workspace/memory/domains/<domain>/rules.md`에 기록되며 Layer 2가 `knowledge_promotion` 이슈를 생성하지 않는다.
- 기존 `.mpa/runtime/knowledge/`는 읽기 자산으로 보존되지만 project memory에서 자동 승격하거나 이슈 lifecycle에 연결되지 않는다.
- credential-like 내용은 생성·수집에서 계속 강제 거부되고 원본이 보존된다.
- 머신 절대 경로는 생성 지침에서 안전하게 표현되며, legacy 원본은 수집 본문에서 `<project-root>/`나 `<redacted-path>/`로 정규화된 뒤 의미를 보존한 채 수집된다.
- 중복 identity는 머신별 경로에 영향받지 않는 정규화 본문을 기준으로 계산되고 기존 inbox·archive를 덮어쓰지 않는다.
- deployment dry-run은 파일별 `collectable`/`blocked`/`not_candidate`와 비밀값을 포함하지 않는 사유를 기록한다. kind와 무관한 raw credential 및 metadata·candidate 무결성·destination 충돌 등 하나라도 `blocked`면 deploy 전에 중단하고, 프로젝트 자산으로 라우팅해야 할 `not_candidate`는 원본을 보존·고지하되 배포를 차단하지 않는다.
- 수집 실패 시 destination을 정리하고 원본 본문을 손실 없이 복원하며, 지정 원본 제거 외의 대상 프로젝 자산을 변경하지 않는다.
- source Runtime·dist 동기화와 전체 테스트·release audit은 통과하되, 사용자가 release·배포를 요청하지 않으면 새 immutable release를 생성하지 않는다.

### 사용자 결정

- 도메인 지식은 이슈로 올려 수집하지 않고, 발견한 프로젝트의 지속 자산으로 즉시 기록한다.
- 이슈 수집 실패가 프로젝트 보완사항·기억·도메인 지식의 잘못된 이슈화 때문인지 생성·수집 논리 전체에서 구분한다.

### 변경 불가 제약

- 명시 요청 또는 승인된 update batch 없이 이슈를 중앙으로 이동하지 않는다.
- credential-like 내용은 자동 정제하여 수집하지 않고 거부한다.
- 목적지 덮어쓰기 금지, 목적지 확인 후 원본 제거·부재 확인, 실패 시 원본 복원을 유지한다.
- 기존 inbox·archive·release bundle은 재작성하거나 삭제하지 않는다.

### 에이전트 가정

| 가정 | 근거 | 틀렸다면 |
|-----|------|---------|
| “프로젝트 자산화”는 `workspace/memory/` 기록을 의미한다 | 현재 MPA에서 다음 세션의 판단을 바꾸는 프로젝트 지식의 primary source다 | `docs/`나 별도 자산 유형으로 정의하도록 명세를 보완한다 |
| 기존 `.mpa/runtime/knowledge/`는 유효한 읽기 자산이다 | 사용자는 신규 도메인 지식의 이슈 경로를 정정했지 기존 공용 자산 삭제를 요청하지 않았다 | knowledge 자산의 보존·폐기를 별도 결정으로 올린다 |
| 머신 절대 경로는 credential과 달리 자동 치환이 가능하다 | `<project-root>/...`로 바꿔도 방법론 개선 취지가 유지된다 | 경로 자체가 기밀인 패턴은 별도 강제 거부 규칙을 둔다 |
| credential 판정은 현재 `SECRET` 계약을 유지해도 이번 문제를 해결한다 | 재현 문제는 credential 탐지 범위가 아니라 경로와 credential을 하나의 강제 거부로 묶은 것이다 | URL·PEM·encoded secret 등 탐지 확장을 별도 보안 태스크로 분리한다 |

### 결정 대기 항목 (Open Questions)

- 없음

---

## 실행 계획 (Implementation Plan)

### 사전 조사

- `workspace/issues/` 작성 진입점과 `workspace/memory/` 종료·Layer 2 참조 체인을 대조해 이슈와 프로젝트 자산의 라우팅을 단일 계약으로 정리한다.
- `release_manager.py` 수동 수집·update batch·dry-run·rollback 경로와 테스트를 대조해 정규화 공통 경계를 확정한다.

### 구현 단계

- [x] Step 1 — architecture·source 운영 규칙에 소유·권한·상태 계약을 먼저 고정한다. 방법론 이슈만 수집 후보이며, 도메인 지식은 producer 세션이 `memory/domains` 및 INDEX에 즉시 기록하고 collector는 프로젝트 memory를 수정하지 않는다. 기존 Runtime knowledge의 신규·갱신·폐기는 명시적 MPA 변경 작업으로만 열어 둔다. / 이유: 코드 전에 미결정 정책을 없애고 대상 사용자 자산 보존 경계를 지킨다.
- [x] Step 2 — 순수 preflight를 구현한다. 순서는 raw text credential 검사 → raw metadata/type marker parsing·kind 분류 → 현재 POSIX machine-path detector의 경로 token 정규화 → normalized checksum/identity·충돌 검사로 고정한다. raw credential·metadata/candidate 무결성·destination 충돌은 `blocked`, 명시적 비방법론·kind 없음·기존 동일 identity는 `not_candidate`, 안전한 방법론 이슈만 `collectable`로 판정하고 비밀값 없는 reason code를 반환한다. / 이유: 정규화가 secret을 가리지 못하게 하고 dry-run·manual collection·deploy의 판정을 같게 만든다.
- [x] Step 3 — Runtime에서 `methodology_improvement`만 중앙 이슈 후보로 작성하고, 프로젝트 사실·도메인 지식·역할 함정·아키텍처 결정은 memory에 즉시 자산화하며 Layer 2의 `knowledge_promotion` 이슈 지시를 제거한다. 새 도메인 파일은 memory INDEX와 project identity의 가용 도메인 집합을 함께 갱신한다. / 이유: 이슈와 memory의 소유 경계와 실제 로딩 연결을 함께 보장한다.
- [x] Step 4 — 이슈 생성 지침에 credential 금지, machine path의 `<project-root>/...` 표현, 잘못된 후보를 `tasks/docs/memory`로 라우팅하는 우선순위와 정정 절차를 추가한다. / 이유: Runtime이 수집기가 받을 수 없는 원본을 만들지 않고 검증되지 않은 지식을 중앙 이슈로 보내지 않게 한다.
- [x] Step 5 — source 수집기가 Step 2 preflight를 사용하게 한다. manual collection은 `collectable`만 이동하고 나머지를 원본 보존 후 거부한다. update dry-run receipt에는 policy/normalization version, target fingerprint, safe issue ID, raw content checksum, normalized checksum/identity, classification/status/reason code, expected destination state만 결박하고 deploy에서 전체 필드와 issue 집합 추가·삭제를 재검증한다. `not_candidate`는 보존·고지하고 batch에서 제외하며 하나라도 `blocked`면 dry-run을 실패시킨다. Runtime 교체·검증과 config migration 뒤 issue batch를 commit하고, collection 또는 이후 backup·receipt 실패 시 issue와 Runtime·MPA config를 함께 rollback한다. / 이유: 배포 권한이 수집 범위를 확장하지 않고 잘못 분류된 프로젝트 자산이 배포를 계속 차단하지 않게 한다.
- [x] Step 6 — 수동·update batch에 정상, 멱등 경로 정규화, raw credential 차단, kind 오분류, 구/new identity 중복, dry-run 후 변경, destination 동시 생성, source 재생성, destination·source 처리 실패·rollback 테스트를 추가한다. 정규화된 destination을 no-clobber로 게시·checksum 확인한 뒤 raw source를 제거하고, 예외 발생 시 기존 rollback 보장을 유지한다. / 이유: 새 정책이 기존 원자성·보안·동시성을 약화하지 않음을 증명한다.
- [x] Step 7 — Runtime·source 규칙·architecture·guidebook을 동기화하고 `sync-runtime`, source/runtime-dist parity, 전체 테스트를 실행한다. `release-audit`은 기존 immutable bundle의 회귀 없음만 확인하고 신규 Runtime 검증 증빙으로 사용하지 않는다. 이후 등록된 `campingtalk-proj` target-ref로 기존 차단 이슈를 지정 수집한다. / 이유: 실행·설명·dist 정합성과 실제 케이스 해소를 올바른 증빙으로 확인한다.

### 예상 조용한 결정

- 공용 지식: 기존 `runtime/knowledge` 읽기 계약은 보존하고 신규·갱신·폐기는 명시적 MPA 변경 작업으로 다룬다. / 권장: 자동·이슈 기반 승격은 제거하되 저장소를 유지불가 상태로 동결하지 않는다.
- 경로 placeholder: 프로젝트 루트 아래는 `<project-root>/...`, 그 밖은 `<redacted-path>/...`로 단일화한다. / 권장: 재현 맥락과 로컬 정보 노출 최소화를 구분한다.
- legacy kind: 기존 inbox·archive의 `legacy_issue`는 읽기·archive 호환으로 보존하되 새 타입 미지정 plain Markdown의 자동 유입은 닫는다. / 권장: 신규 오분류만 차단한다.

### 수정 대상 파일

| 파일 경로 | 변경 내용 |
|---------|---------|
| `.mpa/runtime/core/agent_rules.md` | memory·issue 종료 점검 문구 정리 |
| `.mpa/runtime/core/agent_rules_detail.md` | 도메인 지식 즉시 자산화, `knowledge_promotion` 이슈 제거, 방법론 이슈 전용·안전 표현 계약 |
| `.mpa/runtime/inject/layer2_checkpoint.md` | 지식 승격 이슈 단계를 project memory 정합성 확인으로 대체 |
| `.mpa/runtime/templates/knowledge_template.md` | issue review 선행 지시 제거 및 명시 큐레이션 경계 명시 |
| `release_manager.py` | preflight, kind 제한, credential 거부, 경로 정규화, 원자 이동·rollback, dry-run 재검증 |
| `tests/test_release_manager.py` | 라우팅·정규화·원자성·dry-run 회귀 테스트 |
| `map-product-rules/issue-intake.md` | 방법론 이슈 전용 수집 규칙 |
| `map-product-rules/command-contract.md` | 수집·deployment dry-run 계약 동기화 |
| `map-product-rules/deployment-coordination.md` | 승인 issue collection의 읽기·commit 예외와 deploy rollback 순서 |
| `MAP_PRODUCT_RULES.md` | 승인 issue collection의 좁은 workspace 예외와 상위 불변식 정합화 |
| `workspace/project_rules.md` | 후속 라우팅에서 `knowledge_promotion` 제거 |
| `workspace/memory/shared/architecture.md` | issue·memory·knowledge 소유 경계와 정규화 계약 갱신 |
| `guidebook/guidebook.md` | 이슈·memory·knowledge 흐름 설명 갱신 |
| `guidebook/persona_skill_principles.md` | 지식 저장소 경계 설명 갱신 |
| `dist/.mpa/runtime/` | `sync-runtime`으로 source Runtime 동기화 |

### 참고 파일 (수정 없음)

- `map-product-rules/issue-triage.md` — 수집 후 채택·기각 계약
- `workspace/issues/README.md` — source 중앙 inbox·archive 경계
- `workspace/issues/inbox/campingtalk-proj/20260903_lightweightDtoFieldOmissionVerificationGap.md` — 정상 수집 사례
- `campingtalk-proj/workspace/issues/20260824_codeGateHookCwdDrift.md` — 절대 경로로 차단된 재현 사례

### 반례 (이 계획이 실패할 수 있는 시나리오)

- 절대 경로 정규화가 재현에 필요한 하위 구조까지 삭제한다. → Step 3: 루트만 placeholder로 치환하고 상대 하위 경로는 보존한다.
- 원문 hash를 identity로 쓰면 머신별 경로 차이로 동일 이슈가 중복된다. → Step 3·5: 정규화 본문 기반 identity를 검증한다.
- `knowledge_promotion` 참조가 설명·템플릿에 남아 구 흐름을 다시 실행한다. → Step 1·6: source·Runtime·guidebook 전체 참조 검사와 parity를 강제한다.
- kind 제한을 소급 적용해 기존 `legacy_issue`를 archive하지 못한다. → Step 3·5: 신규 collection 입구에만 제한하고 기존 자산 호환을 보존한다.
- dry-run이 유효한 방법론 이슈의 보안 차단을 경고만 하면 deploy가 결국 실패한다. → Step 5·6: `blocked`는 dry-run을 실패시키되 `not_candidate`는 수집 승인 범위에서 제외·고지한다.
- 경로 정규화를 credential 검사보다 먼저 하면 민감 값이 placeholder 뒤에 숨어 수집된다. → Step 2·6: raw text를 먼저 검사하고 실패 사유에 match fragment를 포함하지 않는 테스트를 둔다.
- 새 도메인 memory만 만들고 INDEX·project identity를 갱신하지 않으면 다음 세션이 자산을 로드하지 못한다. → Step 3: 새 도메인 생성 시 두 색인을 함께 갱신한다.
- destination 작성 후 원본 제거가 실패해 양쪽에 이슈가 남는다. → Step 3·5: destination을 정리하고 원본을 보존하며, 원본이 재생성되면 두 파일을 보존하고 수동 조정을 요청한다.

---

## 실행 TODO

### 구현·에이전트 검증

- [x] Runtime 이슈·memory 라우팅과 Layer 2 자산화 흐름 수정
- [x] source 이슈 preflight·정규화·kind·dry-run 재검증 구현
- [x] 수동·update batch·rollback·중복·보안 회귀 테스트 통과
- [x] Runtime/source/dist/설명 문서 참조 정합성과 release audit 통과
- [x] 차단된 `campingtalk-proj` 방법론 이슈 정규화 수집 확인

### 사용자 결정·승인 필요

- [x] 이 계획서의 구현 승인

## 검증 결과

### 검증 체크리스트

- [x] 정상 경로: 안전한 `methodology_improvement`가 정규화 metadata·identity를 갖고 inbox로 원자 수집되며, 도메인 지식은 이슈 없이 project memory에 남는다.
- [x] 실패 경로: credential, 허용되지 않은 kind, destination 충돌, 원본 제거·metadata 작성 실패가 덮어쓰기·원본 손실·Runtime 부분 배포를 만들지 않는다.
- [x] 엣지 케이스: 경로만 다른 동일 이슈, 기존 `legacy_issue`, dry-run 후 원본 변경, 수집 중 원본 재생성을 검증한다.

### 설계 검토 결과

- 자기 점검: 명세, 가정, 조용한 결정, 반례, 정상·실패·엣지 검증, 단계별 이유를 확인했다.
- 독립 비평: 보안 경계와 공유 배포 흐름을 변경하므로 수행했다. raw credential 우선 검사, preflight 상태 3분류, dry-run 승인 snapshot 결박, memory 색인 동기화, 공용 knowledge의 명시 변경 lifecycle, 신규 collection에만 kind 제한, 정규화 destination의 no-clobber·rollback을 계획에 반영했다. 세부 결과는 [`critique.md`](critique.md)에 보존했다.
- Step 1 독립 비평 보완: producer/collector 책임 분리, 승인 issue collection의 workspace 예외, 상태·reason 판정표, 단일 preflight 순서, 비밀 비노출 receipt schema, deploy commit·rollback 순서를 계약에 반영했다. 세부 지적과 처리 근거는 [`critique_step1.md`](critique_step1.md)에 보존했다.
- 구현 후 1차 독립 검증: 누적 12개 반례로 TOCTOU·symlink·rollback 연쇄·unsafe ID·복수 batch checksum·identity 과축약·metadata 타입·quarantine 실패를 찾아 보완했고, 최종 actionable finding 0으로 승인됐다. 상세 근거는 [`review_phase1.md`](review_phase1.md)에 보존했다.
- 2차 독립 대조: 1차 결과와 changelog·plan·실제 코드·문서를 대조했으며 즉시 수정 0, 주의 0, 조용한 결정 0, 틀린 가정 0으로 승인됐다. 메타 결과는 [`review_summary.md`](review_summary.md), 상세 근거는 [`review_phase2.md`](review_phase2.md)에 보존했다.
- 최종 자동 검증: 전체 142개 테스트 통과, source Runtime과 dist parity 일치, 기존 13개 immutable release bundle audit 통과, 실제 수집 이슈의 destination 존재·원본 부재·credential/machine absolute path 비노출을 확인했다.

### 완료 시 문서 업데이트 대상

- [x] `guidebook/guidebook.md` — issue·memory·Runtime knowledge 소유 경계
- [x] `guidebook/persona_skill_principles.md` — project domain knowledge 자산화와 공용 knowledge 큐레이션 구분
- [x] `workspace/memory/shared/architecture.md` — 현재 수집·memory 계약 스냅샷

## 운영 시 안내 사항

| 영향 대상 | 운영상 달라지는 점 | 사용자 안내 |
|---|---|---|
| 설치 프로젝트 | 도메인 지식은 중앙 수집 후보가 아니라 project memory에 즉시 축적된다 | 공용 knowledge 필요 시 이슈 수집이 아닌 명시 큐레이션 요청으로 다룬다 |
| map-product 운영 | 수집은 MPA 방법론 개선만 받고 dry-run에서 차단 사유를 먼저 제시한다 | 머신 경로는 정규화되지만 credential은 원본을 수정한 뒤 재수집한다 |

## 실행 중 변경 기록

| 변경 내용 | 이유 | 명세 영향 |
|---|---|---|
| Step 1 독립 비평의 5개 지적을 architecture·상위 불변식·intake·command contract·후속 Step에 반영 | producer/collector 책임, workspace 예외, 상태표, 검사 순서, receipt/rollback 계약이 구현 가능한 수준으로 불명확했음 | 없음 |
| Step 2 정규화가 lexical·resolved project root를 모두 인식하고 외부 경로는 마지막 두 segment만 보존하도록 구현 | macOS의 `/var`→`/private/var` alias에서도 project root를 정확히 치환하고 외부 머신 식별정보 노출을 줄이기 위함 | 없음 |
| Step 3에서 Layer 2의 지식 승격 평가를 domain rules·memory INDEX·project identity 정합성 검사로 대체 | 도메인 지식이 중앙 issue lifecycle로 재진입하던 실행 경로를 제거하고 다음 세션의 로딩 연결을 보장하기 위함 | 없음 |
| Step 4~6에서 Runtime 생성 지침과 manual/update collection을 단일 preflight에 연결하고 macOS `/var` alias를 정규화 | 생성·dry-run·commit 판정 차이와 머신별 identity 중복을 제거하면서 raw credential 우선 차단을 유지하기 위함 | 없음 |
| Step 7에서 source Runtime을 dist에 동기화하고 당시 전체 테스트·parity·13개 기존 release bundle audit을 통과한 뒤 지정 이슈를 수집 | 실행·문서·배포 미러의 정합성과 실제 차단 사례 해소를 함께 검증하기 위함 | 없음 |
| 독립 검증에서 발견된 TOCTOU·symlink·rollback 연쇄 실패·unsafe ID·복수 batch checksum·identity 과축약을 보완 | critical 수집 경계의 실제 반례가 기존 정상 테스트만으로 드러나지 않았기 때문 | 없음 |
| 2차 대조 검증에서 발견된 metadata 타입 우회와 quarantine 삭제 실패 원복을 보완하고 전체 회귀 테스트를 재통과 | malformed candidate와 파일시스템 실패에서도 원본 보존·비노출 계약을 유지하기 위함 | 없음 |
| 독립 재검증에서 quarantine checksum 읽기 오류의 원복 누락을 발견해 `OSError`도 복원 분기에 포함 | 삭제 오류뿐 아니라 검증 I/O 오류도 source 경로와 destination 정리를 동일하게 보장하기 위함 | 없음 |

## 명세 변경 이력

| 승인 시각 | 이전 체크섬 | 새 체크섬 | 변경 요약 |
|---|---|---|---|

| 2026-09-04T03:17:27Z | reqspec-v1:2e0b87045840ca9d | reqspec-v1:1a56d74edce25374 | Step 1 독립 비평에 따라 blocked 판정을 kind와 무관한 보안·무결성·충돌 조건으로 명확화 |
### 구현 후 발견

| 항목 | 유형 | 발견 맥락 | 처리 경로 |
|------|------|-----------|-----------|
| preflight 이후 원본 변경·symlink·unsafe filename·복구 연쇄 실패 | 명세 밖 보완 | 정상·단일 파일 테스트에서는 파일시스템 경계와 검증 직후 경쟁 창이 드러나지 않았음 | 구현·회귀 테스트·changelog 반영 |
| 복수 batch checksum 공유·identity suffix 과축약 | 명세 밖 보완 | 단일 후보와 같은 경로 중복만으로는 loop 변수 누수와 오탐을 관찰할 수 없었음 | issue별 snapshot 결박·identity v2·반례 테스트 반영 |
| metadata 비문자열·quarantine unlink/checksum I/O 실패 | 명세 밖 보완 | 정상 metadata와 성공적인 파일 삭제만 경험해서 실패 중간 상태가 보이지 않았음 | 타입 검증·원위치 복원·직접 테스트 반영 |

**파생된 작업 항목:**
- 없음
