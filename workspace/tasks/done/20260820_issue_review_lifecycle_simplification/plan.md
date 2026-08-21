---
태스크: issue_review_lifecycle_simplification
생성일: 2026-08-20
타입: major
실패비용: major
상태: 완료 승인
승인해시: reqspec-v1:dddaa55f25645f1e
승인대상: 요구사항 명세
---

# 작업 항목 계획서: 이슈 검토 생명주기 단순화

**파생 출처:** `campingtalk-proj`에서 수집한 방법론 개선 이슈의 검토 흐름

---

## 요구사항 명세

### 요청 기준

수집 이슈의 검토 결과는 사용자에게 먼저 제시되어야 한다. 별도 review receipt 파일을 만들지 않고, 사용자가 채택을 결정하면 새 작업 항목과 계획을 만든 뒤 이슈에 작업 경로를 기록하고 바로 archive한다. 기각을 결정하면 판단 근거를 수집 이슈 파일 자체에 기록한 뒤 바로 archive한다.

### 목적

이슈 검토의 사용자 판단과 그 결과의 보관 위치를 단순하고 일관되게 만들어, receipt가 사용자를 대신해 결론을 내리는 구조를 제거한다.

### 범위·제외 범위

- 범위: review·triage·archive 명령과 규칙·테스트를 위 흐름으로 변경하고, 현재 기각된 CampingTalk 이슈 두 건을 새 절차로 archive할 수 있게 한다.
- 범위: issue 수집·update 수집의 별도 receipt를 제거하고, 목적지 파일 존재와 원본 부재 확인으로 이동 완료를 판정한다.
- 제외 범위: release·deployment receipt, Runtime 배포 방식 및 다른 프로젝트의 일반 작업 생명주기는 변경하지 않는다.

### 완료 기준

- review receipt 및 review/triage의 별도 상태 전이 의존성이 제거된다.
- 채택된 이슈는 사용자 승인 뒤 새 작업 항목의 plan.md와 연결되고, 채택·작업 경로가 기록된 상태로 즉시 archive된다.
- 기각된 이슈는 사용자 판단 근거가 이슈 파일에 남은 상태로 receipt 없이 archive된다.
- 수집·update 수집은 별도 receipt를 만들지 않고, 목적지 파일을 안전하게 만든 뒤 존재를 확인하고 원본을 삭제한다.
- 변경된 명령·규칙·테스트가 서로 일치하고 Runtime 배포본에도 동기화된다.

### 사용자 결정

- 별도 review receipt는 만들지 않는다.
- 채택은 새 작업 항목을 만들어 계획을 수립하고, 이슈에 해당 작업 경로를 기록한 뒤 즉시 archive하는 것으로 처리한다.
- 기각은 판단 근거를 수집 이슈에 기록하고 즉시 archive한다.

### 변경 불가 제약

- 이슈 수집의 원자 이동·중복·민감정보 검사는 유지한다.
- 수집은 목적지 확인 전 원본을 삭제하지 않는다. 원본 삭제에 실패하면 목적지 생성을 되돌려 원본만 보존한다.
- release·deployment의 검증 근거와 receipt 구조는 유지한다.
- archive 대상 이슈의 기존 본문과 수집 메타데이터는 보존한다.

### 에이전트 가정

| 가정 | 근거 | 틀렸다면 |
|-----|------|---------|
| 채택은 대화형 계획 수립이므로 CLI 명령이 자동 생성하지 않는다 | 새 작업에는 범위·완료 기준·사용자 결정을 정하는 설계 단계가 필요하다 | 채택용 명령의 역할과 입력 계약을 별도 설계한다 |
| 기각 근거는 이슈 메타데이터와 본문에 기록해 archive된 파일만으로 판단을 확인할 수 있다 | 사용자가 별도 review 파일 없이 수집된 파일에 근거 기록을 요청했다 | archive 경로나 별도 인덱스의 최소 메타데이터를 추가로 설계한다 |

### 결정 대기 항목 (Open Questions)

없음.

---

## 실행 계획 (Implementation Plan)

### 구현 단계

- [x] Step 1 — 이슈 결정·아카이브 명령을 단일 상태 전이로 재설계한다. / 이유: 채택·기각의 판단 근거와 archive를 이슈 파일 한 곳에 원자적으로 남긴다.
- [x] Step 2 — review·triage·resolve receipt 의존 코드와 CLI를 제거하고, 채택에는 기존 작업 항목 식별자 연결을 요구한다. / 이유: 사용자 판단을 별도 receipt나 별도 triage 상태로 중복 보관하지 않는다.
- [x] Step 3 — map-product 운영 규칙·프로젝트 워크플로우·명령 계약을 새 흐름과 일치시킨다. / 이유: 대화 절차와 자동화가 같은 생명주기를 가리켜야 한다.
- [x] Step 4 — 이슈 수집, 채택 archive, 기각 archive, 잘못된 작업 연결, 기존 release/deployment receipt 보존을 자동 테스트한다. / 이유: 수집 안전성과 새 결정 전이가 함께 유지되는지 검증한다.
- [x] Step 5 — 이번 세션에 만들어진 review receipt 4개를 제거하고, 이미 기각된 CampingTalk 이슈 2건에 판단 근거를 기록해 archive한다. / 이유: 현재 저장소 상태를 새 규칙에 맞춘다.
- [x] Step 6 — Runtime 동기화와 전체 테스트를 실행해 source·배포본·동작의 일치를 확인한다. / 이유: MPA 시스템 변경은 설치본까지 검증해야 한다.
- [x] Step 7 — collection·update-collection receipt 생성과 기존 기록을 제거하고, 이동 완료 확인으로 수집 안전성을 검증한다. / 이유: 수집 기록을 최소화하되 원본 정리 조건은 유지한다.
- [x] Step 8 — 수집을 목적지 생성·확인 뒤 원본 삭제로 보완하고, 원본 삭제 실패 rollback을 검증한다. / 이유: 이동 중 파일 손상 우려 없이 완료 조건을 명확히 한다.

### 예상 조용한 결정

- archive 상태 표현: `accepted`·`rejected`라는 사용자 결정을 frontmatter에 보존하고, 최종 보관 상태는 `archived`로 통일한다. / 권장: `decision` 필드로 결정을 분리한다. archive가 해결 완료를 뜻하지 않게 한다.
- 작업 연결 형식: 채택 archive는 새 작업 항목의 plan.md 상대 경로를 기록한다. / 권장: `workspace/tasks/.../plan.md`만 허용해 존재 여부를 검증한다.
- 기존 기각 이슈: 현재 대화에서 확정한 “전역 MPA 보완의 효용이 낮다”를 판단 근거로 기록한다. / 권장: 이 근거로 두 항목을 `rejected` archive한다.

### 수정 대상 파일

| 파일 경로 | 변경 내용 |
|---|---|
| `release_manager.py` | review·triage·resolve receipt 흐름을 사용자 결정 기록+즉시 archive 흐름으로 교체 |
| `tests/test_release_manager.py` | 새 채택·기각 archive 계약과 기존 수집 안전성 검증 |
| `map-product-rules/issue-intake.md` | 검토·채택·기각의 사용자 판단 및 archive gate 갱신 |
| `map-product-rules/issue-triage.md` | 별도 triage 대신 채택 작업 이관/기각 archive 프로필로 정리 |
| `map-product-rules/command-contract.md` | 제거·변경된 issue 명령 계약 반영 |
| `workspace/project_rules.md` | 수집 이슈의 채택→작업 생성→archive, 기각→archive 흐름 반영 |
| `workspace/issues/README.md` | inbox·archive의 간결한 보관 규칙 반영 |
| `workspace/issues/inbox/campingtalk-proj/*.md` | 현재 기각된 두 이슈에 판단 근거를 기록한 뒤 archive |
| `workspace/receipts/issues/reviews/*.json` | 별도 review receipt 제거 |
| `workspace/receipts/issues/collections/*.json` | 수집 완료 receipt 제거 |
| `workspace/receipts/issues/update-collections/*.json` | update 수집 receipt 제거 |

### 참고 파일 (수정 없음)

- `.mpa-workspace/core/agent_rules_detail.md` — MPA 시스템 수정·승인·release 절차
- `MAP_PRODUCT_RULES.md` — source 전용 이슈 처리 불변식
- `/Users/kjkim/Study/circled-wiki/src/circled_wiki/engineering/issue_workspace.py` — 이슈 파일 내 사용자 판단 기록 사례

### 반례 (이 계획이 실패할 수 있는 시나리오)

- 채택 archive가 존재하지 않는 작업을 가리킨다 → 구현 [2]단계에 포함: task plan 경로가 workspace 내부에 존재하는지 검증한다.
- archive 중 파일 기록이 실패해 inbox와 archive가 불일치한다 → 구현 [1]단계에 포함: 렌더링·이동 실패 시 원본을 유지하거나 복원한다.
- 기각 archive가 해결됨으로 오해된다 → 구현 [1]단계에 포함: `decision`과 `archive_status`를 분리해 처리 결과를 명시한다.

## 실행 TODO

### 구현·에이전트 검증

- [x] 단일 결정·archive 명령 구현 및 단위 테스트
- [x] 운영 규칙·명령 계약·프로젝트 워크플로우 동기화
- [x] 기존 review receipt 제거 및 현재 기각 이슈 2건 archive
- [x] Runtime 동기화와 전체 테스트 통과
- [x] 수집·update 수집 receipt 제거, 이동 완료 확인 및 전체 회귀 테스트
- [x] 목적지 확인 뒤 원본 삭제 및 삭제 실패 rollback 테스트

### 사용자 결정·승인 필요

- [x] 사용자 결정: 채택·기각 모두 즉시 archive, 채택은 새 작업 항목과 연결
- [x] 사용자 승인: 제안한 변경 및 검증 진행

## 검증 결과

### 검증 체크리스트

- [x] 정상 경로: 채택 이슈가 존재하는 작업 plan과 연결된 상태로 archive된다. (`test_accepted_issue_requires_existing_task_plan_and_archives_with_link`)
- [x] 정상 경로: 기각 이슈가 판단 근거와 함께 archive된다. (`test_rejected_issue_records_reason_and_archives_without_a_receipt`)
- [x] 실패 경로: 없는 작업 경로·archive 충돌·기록 실패 시 inbox 원본을 보존한다. (`test_archive_write_failure_restores_open_issue`, 완료 task 거부 검사)
- [x] 회귀: issue 수집의 원자 이동·중복·민감정보 검사가 유지된다. (전체 69 tests)
- [x] 회귀: 수집·update 수집이 별도 receipt 없이 목적지 존재·원본 부재를 확인하고 실패 시 원본을 보존한다. (`test_collect_confirms_destination_and_source_removal_without_receipt`, `test_update_collects_issues_only_after_runtime_verification`, 원본 삭제 실패·원본 재생성·목적지 경합·임시파일 정리 실패 보존 검사; 전체 73 tests)

### 완료 시 문서 업데이트 대상

- [x] `map-product-rules/` 및 `workspace/issues/README.md` — 새 이슈 생명주기 반영

## 운영 시 안내 사항

기존 review·collection·update-collection receipt는 더 이상 생성하지 않으며, 이 태스크에서 생성된 기록은 제거한다. release·deployment receipt는 유지한다.

## 실행 중 변경 기록

| 변경 내용 | 이유 | 명세 영향 |
|---|---|---|
| 기존 결정 메타데이터를 archive 명령이 직접 기록하도록 변경 | 별도 review·triage receipt 제거 | 없음 |
| 채택 연결을 active task plan으로 제한 | 완료·무관 작업 연결 방지 | 없음 |
| 수집·update 수집 receipt 제거 | 별도 기록 대신 목적지 확인 후 원본 삭제로 충분하다는 사용자 결정 | 요구사항 명세 갱신 |
| 목적지 확인 뒤 원본 삭제 | 수집 이동 중 파일이 깨지지 않도록 사용자 요청 | 요구사항 명세 갱신 |
| 목적지 경합 시 no-clobber 생성 | 독립 리뷰에서 임시 파일 rename이 기존 목적지를 덮어쓸 수 있음을 발견 | `os.link` 기반 no-clobber 생성과 경쟁 테스트 추가 |
| 임시파일 정리 실패 rollback | no-clobber 생성 뒤 임시파일 제거 실패 시 목적지 상태가 누락될 수 있음을 재검토에서 발견 | 목적지 생성 상태를 즉시 기록하고 rollback 테스트 추가 |
| Release `20260821031029-aa4940ea` 생성·감사 | 사용자의 release 요청 | Runtime 동기화, release audit 및 전체 73 tests 통과 |
| 원본 재생성 충돌을 보존·보고 | 독립 리뷰에서 확인 실패 시 inbox·원본 동시 잔존 가능성을 지적 | 요구사항 명세의 충돌 처리 제약 보완 |

## 명세 변경 이력

| 승인 시각 | 이전 체크섬 | 새 체크섬 | 변경 요약 |
|---|---|---|---|

### 구현 후 발견

| 항목 | 유형 | 발견 맥락 | 처리 경로 |
|---|---|---|---|
| 원본 재생성 충돌 | 명세 밖 보완 | 이동 후 원본이 새로 생기면 자동 rollback이 안전하지 않다 | 두 파일을 보존하고 수동 조정으로 보고하도록 구현·테스트 |

**파생된 작업 항목:**

- (신규 작업 항목 생성 시 여기에 추가됨)
| 2026-08-21T01:22:21Z | reqspec-v1:8e9baa002ee33f01 | reqspec-v1:18727f0d987aa971 | 수집·update 수집 receipt를 제거하고 이동 직후 원본 부재·목적지 존재 확인으로 완료를 판정 |
| 2026-08-21T01:26:00Z | reqspec-v1:18727f0d987aa971 | reqspec-v1:77c1571b88ffb9df | 수집 이동 중 원본 재생성 충돌은 두 파일을 보존하고 수동 조정으로 보고하도록 보완 |
| 2026-08-21T02:59:22Z | reqspec-v1:77c1571b88ffb9df | reqspec-v1:dddaa55f25645f1e | 수집을 목적지 생성·확인 후 원본 삭제 순서로 보완하고 삭제 실패 시 목적지를 되돌리도록 변경 |
| 2026-08-21T03:00:48Z | reqspec-v1:dddaa55f25645f1e | reqspec-v1:dddaa55f25645f1e | 목적지 확인 뒤 원본을 삭제하는 수집 순서와 삭제 실패 시 목적지 rollback 검증을 완료 |
