---
태스크: mpa_toml_reference_contract
생성일: 2026-09-14
타입: major
실패비용: major
상태: 테스트 중
승인해시: reqspec-v1:7109a1fa91c52401
승인대상: 요구사항 명세
---

# 작업 계획서: TOML 기반 MPA 참조 계약

**파생 출처:** `workspace/issues/inbox/my-pacemaker-agent/config_toml_external_agent_reference.md` — 외부 에이전트와 자동 검증이 읽을 수 있는 MPA 규칙 계약 필요

## 요구사항 명세

### 요청 기준

사용자는 TOML 기반 참조 계약을 어떤 방식과 범위로 만들지 구현 전에 제시해 달라고 요청했다. 실제 효과 측정 pilot은 별도 hold 작업으로 보류한다.

### 목적

외부 에이전트와 검증 도구가 MPA Runtime의 안정적인 구조 사실을 설치본 기준으로 읽고 검증하게 한다. Markdown의 설명·판단·예외를 설정 파일로 이관하거나, 계약이 agent 동작을 제어하게 만들지 않는다.

### 1차 범위

1차는 **experimental·inspect-only 참조 계약**이다. 다음의 구조 사실만 제공한다.

| 계약 영역 | 외부 소비자가 얻는 값 | 정본과 동치 확인 방식 |
|---|---|---|
| 계약 식별 | protocol id, `contract_version`, profile id, experimental 표식 | 계약 schema 자체 검사 |
| Runtime 발견 | 설치 프로젝트 기준 상대 discovery path와 Runtime 식별 정보 | 설치본 루트 기준 경로 검사 |
| 기본 경로 | 작업·문서 기본 경로 | Markdown의 명시 binding marker와 값 단위 비교 |
| 상태 모델 | `major`/`minor`의 안정 영문 state id, 현재 한국어 label, 허용 전이 | 상태 소유 문서의 binding marker·전이 fixture와 값 단위 비교 |
| 진입 안내 | 규칙 문서의 상대 경로·stable anchor·용도 | file/section 종류·anchor·허용 root 검사 |
| 소비 제한 | `inspect-only`, `not-invokable`, 불일치 시 중단 규칙 | 가상 consumer end-to-end 검사 |

계약의 각 public field에는 `field_id`, owner kind, owner location, stable anchor, 값 도출·동치 규칙을 둔 provenance를 제공한다. 상태에는 표시용 `label_ko`와 기계용 ASCII `id`를 함께 둔다. 한국어 label 변경은 계약 호환성 검토 대상이고, `id` 변경·전이 제거는 버전 올림이 필요한 breaking change다.

### 제외 범위

- Markdown 규칙 전체 이관, 자연어 라우팅·예외·판단의 자동 판정
- TOML로 hook 입력·승인 게이트·코드 수정·배포를 제어하는 기능
- hook 경로·CLI·인자·출력을 public 실행 API로 공개하는 기능
- 외부 서비스 연결, 실제 모델 호출, 실제 효과 측정 pilot, release·deploy 생성
- profile 밖의 일반 TOML 기능을 지원하거나 TOML parser를 범용 라이브러리로 제공하는 기능

### 완료 기준

- `.mpa/runtime/contracts/agent_reference.toml`은 위 1차 범위만 담고, `experimental` 및 `inspect-only` 사용 등급을 계약 안에 명시한다.
- 계약 profile은 UTF-8 without BOM, 허용 table·key·타입·배열 원소·문자열 escape·주석·경로 표기와 금지 문법을 예시까지 포함해 버전별로 명시한다. profile 밖 입력은 안정된 진단 코드로 거부한다.
- Python 3.9에서 외부 설치 의존성 없이 profile 검사기와 validator가 동작한다. 개발 검증에서는 독립 표준 TOML parser(`tomli` 또는 동등 parser)를 oracle로 사용해 유효 fixture의 해석 호환성을 확인한다.
- validator는 `contract_version=1`만 수용하고 미지원 version·unknown required key·손상 계약·unresolved reference·semantic drift를 각각 안정된 종료 코드와 machine-readable diagnostic으로 보고한다. V1은 unknown key를 거부한다.
- 각 public 값은 문서의 stable binding marker 또는 명시적 fixture와 양방향 비교한다. 파일 존재만 확인하는 검사는 충분하지 않다.
- source와 `dist/.mpa/runtime` 각각에서 discovery → profile parse → version check → reference resolution → drift check를 실행하고, 계약·validator·문서 참조의 parity를 확인한다. release·deploy는 하지 않는다.
- 가상 외부 consumer가 계약을 발견·검증·참조 해석하되 hook을 실행하거나 파일을 변경하지 않는 end-to-end 검사를 통과한다.

### 사용자 결정

- TOML 계약의 범위와 방법을 구현 전에 먼저 제시한다.
- 실제 효과 측정 pilot은 보류한다.

### 변경 불가 제약

- 사용자에게 같은 목적·승인을 다시 묻거나 새로운 수동 기록을 요구하지 않는다.
- 외부 소비자에게 실행·수정·승인·배포 권한을 주지 않는다.
- TOML만으로 Markdown의 판단·예외 규칙을 대체하지 않는다.
- Python 3.9 호환성을 깨거나 필수 제3자 **런타임 설치** 의존성을 추가하지 않는다.

### 호환성·권한 정책

| 항목 | V1 정책 |
|---|---|
| protocol/version | `mpa-agent-reference` / `contract_version = 1`만 수용 |
| 키 정책 | V1 schema의 필수 key만 허용; unknown key·table은 거부 |
| 향후 추가 | 선택 field를 포함한 schema 변경은 새 `contract_version`; 구 consumer는 version 불일치로 안전 중단 |
| 오류 처리 | 20: version, 21: profile/schema, 22: reference, 23: semantic drift; 성공은 0 |
| diagnostic | JSON 한 줄: code, field_id, path, message. 비밀값·환경값은 출력하지 않음 |
| 소비자 정책 | 0이 아니면 관찰·보고만 하고 승인·수정·배포·hook 실행을 하지 않음 |
| 실행 권한 | 모든 reference는 `inspect-only` 및 `not-invokable`; 실행 가능한 API는 V1에 없음 |
| source/dist | source checkout은 개발 중일 수 있다. 설치본은 포함된 Runtime artifact만 읽으며, 이번 작업은 dist parity까지만 검증한다. immutable release 생성은 별도 명시 요청에서만 수행한다. |

### 필드 소유·변경 책임

| field_id | 정본 소유자 | 동치 규칙 | 변경 시 처리 |
|---|---|---|---|
| `paths.tasks_root`, `paths.docs_root` | `core/agent_rules.md`의 binding marker | marker의 literal 값과 TOML 값 비교 | 문서·계약을 함께 수정하고 validator 실행 |
| `lifecycle.major`, `lifecycle.minor` | 상태를 설명하는 core 문서의 binding marker 및 전이 fixture | `id`, `label_ko`, 전이 집합의 양방향 비교 | label 변경은 호환성 검토, id/전이 제거는 version 변경 검토 |
| `entry.*` | `core/agent_rules.md` 또는 `core/agent_rules_detail.md`의 stable anchor | owner path·kind·anchor가 모두 존재 | anchor rename 전 계약을 먼저 갱신하고 reference 검사 |
| `contract.*` | `contracts/agent_reference.toml` schema | schema/profile 검사 | schema owner가 version·guidebook·fixture를 함께 갱신 |

Runtime 변경자는 위 표에 걸린 값을 바꿀 때 validator와 source/dist parity 검사를 실행한다. 계약 version·profile·정본 marker의 변경은 이 태스크의 검토 대상으로 남기며, 실제 consumer 제어 기능은 별도 major 작업으로 분리한다.

### 에이전트 가정

| 가정 | 근거 | 틀렸다면 |
|---|---|---|
| 1차 계약은 읽기 전용이어야 한다 | 현 Runtime hook은 Markdown과 Python 로직을 직접 사용하며, TOML 소비자가 아직 없다 | 구체 소비자와 권한 모델을 먼저 정의하는 별도 설계로 전환 |
| 제한 profile은 유지 비용을 통제할 수 있다 | Python 3.9에는 `tomllib`가 없고 설치 대상 의존성도 보장되지 않는다 | profile 확장 요구가 생기면 범용 parser 도입·지원 버전 정책을 별도 재설계 |
| 문서에 binding marker를 둘 수 있다 | 경로·상태값의 drift를 기계적으로 확인하려면 안정된 비교 지점이 필요하다 | 기계 추출 가능한 기존 정본이 확인되면 marker 대신 그 source를 사용 |

### 결정 대기 항목 (Open Questions)

없음. V1은 위 정책으로 한정한다. 실제 consumer가 profile 확장이나 실행 API를 요구할 때만 별도 요구사항·호환성 설계를 연다.

## 실행 계획 (Implementation Plan)

### 사전 조사

현재 규칙은 Markdown과 Python hook에 분산돼 있고 실행 환경은 Python 3.9.6이다. `tomllib`는 없으므로 설치 대상에는 제3자 parser를 요구하지 않는다. 기존 Codex agent 설정의 TOML은 agent 자체 설정일 뿐 MPA Runtime의 구조 계약이 아니다.

### 구현 단계

1. **profile·discovery·호환성 schema 확정** — V1의 허용 TOML 문법/키 공간, `contract_version`, error code, JSON diagnostic, 설치본 discovery와 손상 시 중단 규칙을 `contracts/` 문서와 fixture로 고정한다. / 이유: parser 구현보다 계약 경계를 먼저 검토 가능하게 한다.
2. **provenance와 정본 binding 확정** — 위 소유 표의 각 field에 marker/fixture·owner kind·anchor·허용 root·symlink 거부·동치 규칙을 작성한다. / 이유: 링크 존재 여부가 아닌 값 의미의 drift를 검출한다.
3. **profile 검사기·validator 구현** — Python 3.9 표준 기능만으로 제한 profile을 읽고 schema/reference/drift를 검사하는 CLI를 작성한다. V1 밖 문법은 명시 진단으로 거부하고, hook 실행 경로는 제공하지 않는다. / 이유: 설치본에서도 안전하게 계약을 검증한다.
4. **계약·외부 소비자 검증 구현** — 읽기 전용 TOML, guidebook 사용 예시, 가상 consumer와 profile oracle·old/new version·anchor rename·label 변경·non-execution fixture를 작성한다. / 이유: producer 자기 검사에 그치지 않고 외부 조회 흐름을 검증한다.
5. **source/dist 회귀 검증·문서화** — `sync-runtime` 후 source와 dist에서 validator를 각각 실행하고 contract/validator/문서 참조 parity를 검사한다. / 이유: 배포 대상 Runtime이 빠지거나 오래된 상태로 남는 회귀를 막는다.

### 예상 조용한 결정

- 계약 파일 위치는 `.mpa/runtime/contracts/agent_reference.toml`로 둔다. 외부 consumer는 프로젝트 root에서 이 경로만 탐색하며, 파일 부재·손상·version 불일치는 안전 중단으로 처리한다.
- V1 parser는 일반 TOML 구현이 아니라 명시된 standard-TOML subset의 profile 검사기다. 유효 fixture는 독립 표준 parser oracle로도 읽혀야 한다.
- 상태 표기는 현재 한국어 문구를 `label_ko`로 보존하되, external contract에는 별도 안정 `id`를 둔다. 기존 plan hash·code gate의 입력은 바꾸지 않는다.
- reference에는 문서/section만 싣고 hook은 싣지 않는다. 장래 hook 정보를 추가해야 하면 `not-invokable` authority와 별도 API 검토를 먼저 한다.
- symlink·절대 경로·`..`·허용 Runtime root 밖 참조는 거부한다.

### 수정 대상 파일

| 파일 경로 | 변경 내용 |
|---|---|
| `.mpa/runtime/contracts/agent_reference.toml` | 신규 experimental inspect-only 계약 |
| `.mpa/runtime/contracts/agent_reference_profile.md` | V1 profile, schema, compatibility, provenance 규격 |
| `.mpa/runtime/hooks/contract_reference.py` | profile 검사·validator CLI·안정 diagnostic |
| `.mpa/runtime/core/agent_rules.md` | path/lifecycle binding marker와 계약 정본 경계 |
| `.mpa/runtime/core/agent_rules_detail.md` | 필요한 lifecycle/entry binding marker |
| `tests/test_contract_reference.py` | profile, drift, compatibility, consumer, source/dist 회귀 |
| `guidebook/guidebook.md` | discovery, read/validate 사용법, non-execution 제한 |
| `dist/.mpa/runtime/` | source Runtime 동기화 결과 |

### 참고 파일 (수정 없음)

- `workspace/issues/inbox/my-pacemaker-agent/config_toml_external_agent_reference.md` — 문제 제기와 초안 범위
- `workspace/memory/shared/architecture.md` — Runtime source/dist와 release 경계
- `.mpa/runtime/hooks/plan_hash.py`, `.mpa/runtime/hooks/code_gate.py` — 기존 상태·승인 동작의 소유자

### 반례

- 자체 검사기만 통과하는 비표준 TOML → profile 예시와 독립 parser oracle 검사를 통과하지 못하면 실패한다.
- producer가 key를 추가해 구 consumer가 오해함 → V1 unknown key는 거부하고 새 version으로 올려 안전 중단한다.
- Markdown 상태 전이가 달라졌는데 파일 경로만 남음 → marker/fixture와 전이 집합을 양방향 비교해 drift code 23으로 실패한다.
- 외부 도구가 계약 reference를 실행 API로 오해함 → 계약에는 `inspect-only`, `not-invokable`을 넣고 mock consumer도 실행 기능 없이 검증한다.
- sync가 새 `contracts/`를 누락함 → dist discovery·validator·parity 검사가 실패한다.

## 실행 TODO

### 구현·에이전트 검증

- [x] V1 profile·discovery·호환성·diagnostic schema 확정.
- [x] field provenance·binding marker·동치 fixture 확정.
- [x] 검사기·계약·guidebook·가상 consumer·회귀 테스트 구현.
- [x] source/dist sync 및 독립 구현 검증.

### 사용자 결정·승인 필요

- [x] 계획서 검토 후 읽기 전용 TOML 계약 V1 구현 승인.

## 검증 결과

자기 점검: 1차 범위·제외 범위·호환성·권한·정본 소유자·실행 순서·반례·검증 기준을 확인했다. 독립 비평: 5단계 의존 구현과 Runtime 계약 영향으로 수행했고, 자체 parser의 표준 호환성, version 정책, semantic drift, 외부 consumer 권한, source/dist parity 지적을 모두 profile·provenance·consumer·parity 검증에 반영했다. 구현 후 독립 시행 검증은 final_independent_verification.md에 기록했다.

### 검증 체크리스트

- [x] Python 3.9: 정상 V1 계약을 source와 dist에서 모두 discover·parse·validate했다.
- [x] profile: 허용/금지 문법·중복 key·BOM·unknown key·경로 이탈을 기대 error code로 검사했다.
- [x] compatibility: V1/미지원 version·미래 key·label 변경·id 및 전이 변경 fixture를 검사했다.
- [x] provenance: owner file/section/anchor/marker와 path·상태·전이 값의 양방향 drift를 검사했다.
- [x] consumer: 가상 외부 consumer가 read/validate만 수행하고 hook 실행·파일 변경·승인 판단을 하지 않음을 확인했다.
- [x] parity: sync 뒤 source/dist 계약, validator, profile 문서, guide reference의 parity와 dist validator 실행을 확인했다.

### 완료 시 문서 업데이트 대상

- `guidebook/guidebook.md` — 외부 consumer용 experimental 읽기 전용 계약 안내

## 운영 시 안내 사항

V1 계약은 Runtime 구조를 읽고 검증하는 메타데이터다. validator 오류가 나면 소비자는 관찰과 보고만 하며, 승인·수정·배포·hook 실행을 해서는 안 된다. 계약 값만 바꿔 기존 agent의 승인·라우팅·hook 동작이 바뀌는 연결은 만들지 않는다.

## 실행 중 변경 기록

| 변경 내용 | 이유 | 명세 영향 |
|---|---|---|
| 독립 비평 반영 | TOML 표준 호환성, semantic drift, consumer 권한·source/dist 경계를 명확화 | V1 profile·provenance·호환성·검증 범위를 구체화 |
| 제한 profile의 문자열 배열을 JSON 호환 문법으로 고정 | Python 3.9에서 외부 설치 parser 없이 profile을 결정론적으로 검사 | 없음 — 승인된 제한 profile의 구현 세부 |
| 독립 구현 검토 보완 | same-version public field drift와 손상 입력 오류가 안전 중단해야 함을 확인 | 없음 — 승인된 version·safe-stop 정책의 구현 보완 |
| 배열의 비표준 escape 거부 | 2차 독립 검토에서 scalar와 array profile 검사의 차이를 발견 | 없음 — 표준 TOML subset 경계의 버그 수정 |
| 최종 독립 시행 검증 | 구현 대화와 검토 기록을 보지 않는 검증자가 Python 3.9과 source/dist/실패 경계를 실제 실행 | 없음 — 검증 증빙 추가 |
| immutable Runtime release 생성 | 사용자의 명시적 release 요청으로 release_manager 표준 preflight·전체 테스트·bundle audit 실행 | 없음 — 구현 범위 밖 운영 요청을 별도 실행 |

## 명세 변경 이력

| 승인 시각 | 이전 체크섬 | 새 체크섬 | 변경 요약 |
|---|---|---|---|

### 구현 후 발견

| 항목 | 유형 | 발견 맥락 | 처리 경로 |
|---|---|---|---|
| (결과를 경험한 후 채움) | 명세 밖 보완 / 명세 변경 / 신규 작업 항목 | 왜 보기 전에는 보이지 않았는가 | 실행 기록 갱신 / 승인 이력 갱신 / INDEX.md 등록 |
