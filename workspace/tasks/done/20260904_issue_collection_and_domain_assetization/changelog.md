# 태스크 내역서: issue_collection_and_domain_assetization

**작업일:** 2026-09-04 ~ 2026-09-08
**계획서:** `plan.md`

---

## 변경 파일 목록

| 파일 경로 | 변경 유형 | 설명 |
|---------|---------|------|
| `MAP_PRODUCT_RULES.md` | 수정 | 승인 issue collection의 좁은 workspace 예외와 rollback 경계 명시 |
| `map-product-rules/issue-intake.md` | 수정 | producer/collector 분리, 상태 판정표, receipt schema 명시 |
| `map-product-rules/command-contract.md` | 수정 | issue-create/collect 계약 분리와 deploy 원자성 명시 |
| `map-product-rules/deployment-coordination.md` | 수정 | collection 읽기·commit 범위와 rollback 순서 명시 |
| `workspace/memory/shared/architecture.md` | 수정 | issue·project asset·공용 knowledge 소유 경계 기록 |
| `workspace/project_rules.md` | 수정 | 도메인 지식의 project memory 직접 자산화 라우팅 반영 |
| `release_manager.py` | 수정 | read-only issue preflight와 machine path 정규화 구현 |
| `.mpa/runtime/core/agent_rules.md` | 수정 | 종료 시 project memory와 methodology issue 경계 확인 |
| `.mpa/runtime/core/agent_rules_detail.md` | 수정 | 도메인 지식 즉시 자산화와 공용 knowledge 명시 변경 계약 적용 |
| `.mpa/runtime/inject/layer2_checkpoint.md` | 수정 | knowledge promotion을 project domain memory 정합성 검사로 대체 |
| `.mpa/runtime/templates/knowledge_template.md` | 수정 | issue 승격 지시 제거 및 명시적 MPA 변경 경계 적용 |
| `dist/.mpa/runtime/` | 동기화 | source Runtime 변경을 배포 미러에 반영 |
| `guidebook/guidebook.md` | 수정 | 방법론 이슈·프로젝트 자산·공용 knowledge의 분리 흐름 설명 |
| `guidebook/persona_skill_principles.md` | 수정 | 도메인 지식의 즉시 자산화와 명시적 공용 큐레이션 경계 설명 |
| `tests/test_release_manager.py` | 수정 | preflight·정규화·상태·원자성·rollback·machine별 중복 회귀 검증 |
| `workspace/issues/inbox/campingtalk-proj/20260824_codeGateHookCwdDrift.md` | 생성 | 기존 차단 방법론 이슈를 canonical metadata로 안전하게 수집 |
| `workspace/tasks/active/20260904_issue_collection_and_domain_assetization/review_phase1.md` | 생성·갱신 | changelog 비참조 1차 독립 검증 근거 |
| `workspace/tasks/active/20260904_issue_collection_and_domain_assetization/review_phase2.md` | 생성·갱신 | 1차 결과와 changelog·실제 코드의 2차 대조 근거 |
| `workspace/tasks/active/20260904_issue_collection_and_domain_assetization/review_summary.md` | 생성·갱신 | 독립 검증 메타 요약 |

---

## 상세 변경 내역

### `release_manager.py`

- **대상:** `_parse_issue_candidate`, `normalize_issue_machine_paths`, `preflight_issue` 및 보조 함수
- **위치:** issue collection metadata 처리 영역
- **변경 유형:** 추가
- **내역:** raw credential을 가장 먼저 차단하고 raw metadata/type marker로 kind를 분류한 뒤, 허용 후보만 machine path 정규화와 normalized checksum/identity·중앙 충돌 검사를 수행하는 무변경 preflight를 추가했다. 결과에는 안전한 issue ID, 정책·정규화 버전, checksum/identity, classification/status/reason code, 예상 destination 상태만 포함한다.
- **내역:** manual collection과 update dry-run/deploy가 같은 preflight snapshot을 사용한다. 정규화 destination을 no-clobber로 게시하고 checksum을 확인한 후에만 raw source를 제거하며, 이후 실패 시 raw bytes와 Runtime·config를 함께 복원한다. `issue-create`는 `methodology_improvement`만 허용한다.

### source 운영 계약과 architecture

- **대상:** issue intake, command/deployment contract, 상위 불변식, project memory architecture
- **위치:** issue collection·deployment·자산 소유 경계
- **변경 유형:** 수정
- **내역:** 방법론 issue producer와 source collector를 분리하고, 도메인 지식의 즉시 project memory 자산화, 세 상태의 우선순위, 승인 collection의 workspace 예외, receipt 비밀 비노출 및 deploy rollback 순서를 고정했다.

### Runtime domain memory 라우팅

- **대상:** `agent_rules.md`, `agent_rules_detail.md`, `layer2_checkpoint.md`, `knowledge_template.md`
- **위치:** 기술/도메인 지식 기록, issue 기록, Layer 2 단계 9, task 종료 확인, 공용 knowledge 작성법
- **변경 유형:** 수정
- **내역:** local issue 생성을 `methodology_improvement`로 한정했다. 도메인 지식 발견 시 domain rules·memory INDEX·project identity를 같은 작업 단위로 갱신하고, Layer 2에서는 이 세 자산의 누락·stale·충돌만 점검하게 했다. 공용 Runtime knowledge는 자동 승격 없이 명시적으로 승인된 MPA 변경 작업에서만 관리한다.

### 검증·실제 수집

- `python3 -m unittest discover -s tests`: 142개 통과
- `diff -qr .mpa/runtime dist/.mpa/runtime`: 차이 없음
- `python3 release_manager.py release-audit`: 기존 13개 release bundle 통과
- `campingtalk-proj/workspace/issues/20260824_codeGateHookCwdDrift.md`: preflight `collectable/ready` 확인 후 중앙 inbox 게시·원본 부재 확인
- manual `not_candidate`는 원본을 보존하고 비방법론 후보에 안전한 producer handoff를 반환하도록 직접 검증
- guidebook의 구형 승격 용어·일반 issue 도식을 방법론 issue 전용/직접 project memory 자산화 흐름으로 교체

---

## 요구사항 명세 대비 변경 사항

> 명세 변경은 사용자 승인·체크섬 갱신 이력을, 명세 밖 보완은 이유와 누적 보고 여부를 기록한다.

| 변경 | 이유 | 명세 영향 | 보고 |
|---|---|---|---|
| `blocked`를 kind와 무관한 보안·무결성·충돌 조건으로 명확화 | Step 1 독립 비평의 상태 우선순위 지적 | 승인된 명세 갱신 (`reqspec-v1:1a56d74edce25374`) | 사용자 보완 요청 반영 |
| lexical·resolved project root를 모두 정규화 대상으로 사용 | macOS 경로 alias에서도 `<project-root>` 의미를 보존 | 없음 | 반영 완료 |
| project 외부 absolute path는 마지막 두 segment만 보존하고 비 UTF-8 issue는 `metadata_invalid`로 안전하게 판정 | machine 식별정보를 줄이면서 최소 재현 단서를 유지하고 batch 전체의 예외 중단을 피함 | 없음 | 반영 완료 |
| macOS `/var`와 `/private/var`를 같은 project root로 정규화 | 호출 경로 표기에 따라 identity가 달라지는 회귀 테스트를 해결 | 없음 | 반영 완료 |
| preflight 이후 원본 변경을 checksum 재검증과 atomic quarantine으로 차단 | 판정 직후 credential 유입·승인 snapshot 밖 원본 삭제 TOCTOU를 방지 | 없음 | 독립 검증 지적 반영 |
| project issue 경로의 디렉터리·개별 파일 symlink와 unsafe filename을 거부 | 프로젝트 밖 파일 읽기·삭제와 receipt 식별자 비노출/불일치를 방지 | 없음 | 독립 검증 지적 반영 |
| deploy 복구 단계를 독립 실행하고 복구 오류를 누적 | issue 복구 실패가 Runtime·config 복구를 중단하지 않게 함 | 없음 | 독립 검증 지적 반영 |
| identity v2에서 머신 루트만 제거하고 안정 suffix를 보존 | 구형 절대 경로 중복은 잡되 서로 다른 파일 관련 이슈를 합치지 않게 함 | 없음 | 독립 검증 지적 반영 |
| required metadata를 비어 있지 않은 문자열로 제한하고 quarantine 삭제 실패 시 원위치 복원 | metadata 타입 우회와 숨은 격리 복제본 잔류를 방지 | 없음 | 2차 독립 검증 지적 반영 |
| quarantine checksum 읽기 자체의 `OSError`도 변경 판정으로 처리해 원위치 복원 | 검사 실패가 숨은 `.collecting-*` 복제본을 남기는 반례를 방지 | 없음 | 2차 독립 재검증 지적 반영 |

---

## 검증 포인트

- [x] 정상 경로 확인: 방법론 이슈가 `collectable/ready`와 normalized checksum/identity를 반환하고 project root를 `<project-root>`로 치환
- [x] 실패 경로 확인: raw credential은 kind와 무관하게 `blocked/credential_detected`, malformed metadata는 `blocked/metadata_invalid`
- [x] 분기 확인: 도메인 지식은 `not_candidate/project_asset`, 같은 normalized identity는 `not_candidate/already_collected`
- [x] plan.md 구현 단계 완료 기준 충족: Step 1~7 완료, 독립 재검증 진행
