---
태스크: 20260821_approval_hash_integrity
생성일: 2026-08-21
타입: major
실패비용: major
상태: 검토 완료
승인해시: reqspec-v1:08810e80c55081c6
승인대상: 요구사항 명세
---

# 작업 계획서: 승인해시 생성·검증 규칙 강제

**파생 출처:** `campingtalk-proj`의 `vcpDatePickerNativeInputMigration` 계획서에 `user-approved-2026-08-21`이라는 사람이 입력한 문자열이 승인해시로 기록되어, 형식·일치 검증 없이 `검증 중` 상태까지 진행된 사실

## 요구사항 명세

### 요청 기준

승인해시는 날짜나 임의의 승인 문구가 아니라, 승인 대상인 요구사항 명세에서 도구가 계산한 값이어야 한다. 생성 규칙을 명시하고, 사람이 직접 입력한 값이나 승인 절차를 건너뛴 상태 전이가 자동 검증에서 드러나도록 보완한다.

minor 계획서도 major와 같은 `# 작업 계획서` 표제와 `## 요구사항 명세` 구조를 사용해야 한다. minor의 경량화는 요구사항 명세를 생략하는 방식이 아니라 실행·검증 절차의 규모를 줄이는 방식이어야 하며, 체크섬은 두 유형에서 동일하게 요구사항 명세 영역만 계산해야 한다. 이 구조는 별도 템플릿이 아니라 단일 `plan_template.md`에서 관리해야 한다.

### 목적

MPA major 계획서의 승인 기록을 `plan_hash.py approve` 및 사용자 승인 뒤 `renew-spec`만 생성·갱신할 수 있는 결정적 형식으로 고정하고, 구현 이후 모든 작업 상태에서 그 유효성을 확인한다.

### 범위·제외 범위

- 범위: 최신 plan의 승인해시 생성 형식, 생성 주체, 허용 상태 전이와 검증 규칙을 Runtime 문서·템플릿·hook에 일치시킨다.
- 범위: `구현 중`, `검증 중`, `테스트 중`, `검토 완료`, `완료 승인` 상태의 active plan은 현재 요구사항 명세와 정확히 일치하는 `reqspec-v1:<16자리 소문자 16진수>` 승인해시가 있어야 한다.
- 범위: audit, 세션 시작 안내, 코드 수정 게이트에서 잘못된 형식·누락·불일치를 진단하고 block 모드에서는 소스 수정을 막는다.
- 범위: major/minor plan template을 공통 `# 작업 계획서` 표제와 동일한 요구사항 명세 필드로 정렬하고, minor 체크섬 범위를 회귀 테스트한다.
- 범위: `minor_plan_template.md`를 제거하고 모든 plan이 `plan_template.md`를 사용하도록 minor 절차·회귀 테스트를 전환한다.
- 범위: 회귀 테스트를 수행하고, 릴리즈 생성은 사용자 명시 요청 또는 배포 요청에 최신 릴리즈가 없을 때만 수행하도록 절차를 명시한다.
- 제외 범위: 이미 존재하는 대상 프로젝트 plan의 승인 상태·내용을 임의로 수정하거나 과거 task 이력을 재작성하지 않는다.

### 완료 기준

- `approve`가 요구사항 명세에서 계산한 `reqspec-v1:<16자리 소문자 16진수>`만 신규 승인해시로 기록하며, 수동 입력 문자열은 유효 승인으로 취급되지 않는다.
- 승인 이후 상태의 plan은 audit과 code gate에서 형식·요구사항 명세 일치 여부를 검사한다.
- 세션 시작 안내가 승인해시 이상을 누락 필드와 구분해 표시한다.
- 규칙·템플릿·테스트가 같은 생성 규칙을 설명하고 검증한다.
- minor는 동일한 요구사항 명세를 승인해시 대상으로 사용하며, 실행 계획·검증 절차만 경량화한다.
- 템플릿은 `plan_template.md` 하나만 유지한다.
- Runtime 변경만으로 릴리즈를 자동 생성하지 않으며, 사용자의 명시 릴리즈 요청 또는 배포 요청 때만 최신 릴리즈 필요 여부를 판정한다.

### 사용자 결정

- 승인해시 생성 규칙을 명시해야 한다.
- 과거 대상 프로젝트의 잘못된 plan을 이번 작업에서 자동 수정하지 않는다.
- 릴리즈는 사용자의 명시 요청 또는 배포 요청에 최신 릴리즈가 없을 때만 만든다.
- plan의 공통 명칭은 `작업 계획서`로 한다.
- `minor_plan_template.md`를 제거한다.

### 변경 불가 제약

- `승인해시`는 사용자 승인 자체를 대체하지 않으며, 사용자 승인 기록의 무결성 표식이다.
- `renew-spec`은 사용자에게 제시·승인된 요구사항 명세 변경을 기록하는 경우에만 사용한다.
- 사용자가 요청하지 않은 신규 immutable release는 만들지 않는다. 이미 생성된 release 이력은 삭제하지 않는다.

### 에이전트 가정

| 가정 | 근거 | 틀렸다면 |
|-----|------|---------|
| 구형 plan의 호환 계산은 유지해야 한다. | Runtime은 과거 task 이력을 읽고 audit할 수 있어야 한다. | 구형 이력의 지원 종료 작업을 별도로 설계한다. |
| 승인 이후 상태 목록은 현재 `VALID_STATUS`의 진행·완료 전 상태로 충분하다. | `approve`가 `구현 중`으로 원자 전환하고, 이후 상태는 모두 그 승인에 의존한다. | 새 상태를 추가할 때 목록과 테스트를 함께 갱신한다. |

### 결정 대기 항목 (Open Questions)

- 없음

## 실행 계획

### 구현 단계

- [x] `plan_hash.py`에 승인 이후 상태와 `reqspec-v1` 형식·현재 요구사항 명세 일치 검증을 공용 규칙으로 구현한다.
- [x] `code_gate.py`가 구현 중뿐 아니라 모든 승인 이후 상태를 검사하도록 하고, 복구 안내에 수동 입력 금지와 정상 생성 명령을 포함한다.
- [x] 세션 시작 진단과 Runtime 규칙·계획서 템플릿에 생성 주체·형식·허용 전이 규칙을 명시한다.
- [x] 정상 승인, 수동 날짜 문자열, 누락 해시, 검증 중 불일치, 구형 plan 호환의 회귀 테스트를 추가한다.
- [x] Runtime source와 테스트를 검증하고, 릴리즈 필요 여부를 사용자 요청 시에만 판정하도록 절차를 문서화한다.
- [x] minor template의 작업 계획서·요구사항 명세 구조를 major와 정렬하고 체크섬 범위를 검증한다.
- [x] 단일 plan template으로 통합하고 minor 경량 절차·회귀 테스트를 전환한다.

### 예상 조용한 결정

- 해시 검증이 필요한 상태 집합은 한 모듈의 상수로 정의하고 gate가 import해 중복 목록을 만들지 않는다.
- `설계 중`·`설계 완료`에서는 빈 승인해시를 허용한다. 그 외 상태에서의 비어 있거나 불일치한 값은 오류다.
- 사람의 의미 있는 승인 메모는 `사용자 결정` 또는 명세 변경 이력에 남기며 승인해시 필드에는 쓰지 않는다.
- 사용자 요청 기반 release 판정은 Runtime source를 수정한 직후가 아니라 명시 release/배포 요청을 받았을 때 수행한다.

### 수정 대상 파일

| 파일 경로 | 변경 내용 |
|---------|---------|
| `.mpa/runtime/hooks/plan_hash.py` | 승인해시 형식·상태별 일치 검사 공용화 및 audit 보강 |
| `.mpa/runtime/hooks/code_gate.py` | 모든 승인 이후 상태의 해시 검증 및 복구 안내 보강 |
| `.mpa/runtime/hooks/session_start.py` | 세션 시작 시 승인해시 이상 표시 |
| `.mpa/runtime/core/agent_rules.md`, `.mpa/runtime/templates/*_plan_template.md` | 생성 주체·형식·직접 입력 금지, major/minor 최신 명세 형식 명시 |
| `.mpa/runtime/core/agent_rules_detail.md` 및 `plan_template.md` | minor 경량화 경계와 공통 작업 계획서 구조 명시 |
| `.mpa/runtime/templates/minor_plan_template.md` | 삭제 — 단일 `plan_template.md`로 통합 |
| `tests/test_plan_hash.py` 및 관련 hook 테스트 | 우회 사례를 포함한 회귀 검증 |
| `map-product-rules/release-preparation.md` 및 Runtime 규칙 | 릴리즈 생성 조건을 사용자 요청·배포 필요 시점으로 제한 |

### 반례

- 날짜 문자열이 `검증 중` 상태에 들어간다 → audit 및 gate가 형식 오류로 표시·차단한다.
- 요구사항 명세가 승인 뒤 수정된다 → 현재 계산값 불일치로 재승인 안내를 낸다.
- 구현 체크박스만 바뀐다 → 요구사항 명세 전용 해시가 같아 정상 통과한다.
- 구형 plan을 audit한다 → 기존 호환 계산을 유지하고 최신 형식으로 오판하지 않는다.

## 실행 TODO

### 구현·에이전트 검증

- [x] 승인해시 생성·상태 전이·검증 구현
- [x] Runtime 규칙 및 템플릿 반영
- [x] 회귀 테스트 통과 및 릴리즈 생성 조건 문서화 — 81개 자동 테스트 통과
- [x] 독립 검증 결과 기록 — 2회 독립 검토에서 minor legacy 우회·legacy approve 회귀를 발견·해소하고 최종 발견사항 없음 확인

### 사용자 결정·승인 필요

- [x] 요구사항 명세 승인 — 사용자가 “보완 진행해줘”와 생성 규칙 명시 요구로 승인함

## 검증 결과

### 검증 체크리스트

- [x] 정상 경로: `approve` 후 `구현 중` plan이 gate를 통과한다. — `test_gate_allows_new_plan_execution_only_change`
- [x] 실패 경로: `user-approved-날짜` 같은 값이 `검증 중` plan에서 audit/gate 오류가 된다. — `test_audit_rejects_manual_approval_date_in_post_approval_status`, `test_gate_checks_manual_hash_in_verification_status`
- [x] 엣지 케이스: 실행·검증 체크 상태만 바꾼 최신 plan과 구형 plan이 의도대로 처리된다. — 관련 16개 단위 테스트 통과
- [x] 릴리즈 조건: Runtime 변경만으로 release를 생성하지 않고, 명시 요청 또는 배포 시 최신 release 필요 여부만 판단한다. — `MAP_PRODUCT_RULES.md`, release profile·command contract, MPA Runtime 세부 규칙 반영
- [x] minor checksum: 요구사항 명세 변경은 해시가 바뀌고 실행 계획 변경은 바뀌지 않는다. — `test_minor_specification_hash_excludes_execution_plan`, 독립 검토 통과
- [x] 구형 승인 경로: 구형 plan은 `approve`가 상태 변경 전에 거부하고, 최신 major/minor plan은 `reqspec-v1` 승인으로 전환한다. — 독립 재검토 및 `test_approve_rejects_legacy_plan_before_state_transition`, `test_approve_transitions_current_plan_and_records_reqspec_hash`
- [x] 전체 회귀: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests` — 83 tests OK

### 완료 시 문서 업데이트 대상

- [ ] `README.md` 또는 설치 문서 — 사용자 조작 절차가 바뀌지 않으면 변경하지 않음
- [x] `.mpa/runtime/core/agent_rules.md` — 승인해시 생성·release 요청 규칙
- [x] `.mpa/runtime/templates/*_plan_template.md` — major/minor 승인해시 안내

## 운영 시 안내 사항

| 영향 대상 | 운영상 달라지는 점 | 사용자 안내 |
|---|---|---|
| 이후 MPA Runtime 대상 | 승인 이후 상태의 임의 해시가 경고·차단 대상이 된다. | 승인 문구는 plan 본문에 기록하고 해시는 `approve`/`renew-spec`으로만 생성한다. |

## 실행 중 변경 기록

| 변경 내용 | 이유 | 명세 영향 |
|---|---|---|
| 승인 이후 상태 공용 집합·형식·일치 검사 추가 | 사람이 입력한 날짜/문구가 유효 승인으로 통과하지 않게 하기 위함 | 없음 |
| major approve를 `설계 완료`로 제한, minor 경량 상태만 예외 유지 | 상태를 직접 건너뛰는 우회 경로를 줄이기 위함 | 없음 |
| 릴리즈 생성 조건을 사용자 요청 또는 배포 시 최신 release 부재로 제한 | 변경마다 불필요한 immutable release가 쌓이지 않게 하기 위함 | 사용자 결정 반영 |
| minor template도 요구사항 명세 표지로 통일하고, 승인 이후 구형 해시를 거부 | 독립 검토에서 발견된 신규 minor legacy 해시 우회 제거 | 없음 |
| 구형 plan의 approve를 상태 변경 전 거부하고 README·install까지 release 조건 보강 | 독립 재검토에서 발견된 legacy approve 회귀와 문서 누락 해소 | 없음 |
| 새 release 미생성 | 사용자 요청 기반 release 생성 규칙을 이번 작업에 즉시 적용 | 없음 |
| minor 계획서를 major와 공통 표제·요구사항 명세 구조로 통일 | 승인해시의 보호 범위와 경량화 경계를 분명히 하기 위함 | 사용자 결정 반영 |
| `minor_plan_template.md` 제거, 공통 template 기반 minor 생략 규칙으로 전환 | 템플릿 드리프트를 없애고 경량화 위치를 절차로 한정 | 사용자 결정 반영 |
| 공통 템플릿 전환 뒤 “두 템플릿” 문구 정정 | 독립 검토에서 발견된 활성 규칙 표현 불일치 해소 | 없음 |
| release `20260821085459-5314021a` 생성 | 사용자의 명시 릴리즈 요청에 따라 source Runtime을 dist·immutable bundle에 동기화 | 없음 |
| (구현 중 채움) |  | 없음 / 확인 필요 |

## 명세 변경 이력

| 승인 시각 | 이전 체크섬 | 새 체크섬 | 변경 요약 |
|---|---|---|---|
| 2026-08-21T07:40:14Z | reqspec-v1:0dd016cc68896050 | reqspec-v1:cb8e613906be417f | 릴리즈는 사용자 명시 요청 또는 배포 시 최신 release 부재일 때만 생성하도록 변경 |
| 2026-08-21T07:46:23Z | reqspec-v1:cb8e613906be417f | reqspec-v1:16a58faa7604d885 | minor도 공통 작업 계획서·요구사항 명세 구조와 동일 체크섬 범위를 사용하도록 보완 |
| 2026-08-21T07:49:59Z | reqspec-v1:16a58faa7604d885 | reqspec-v1:08810e80c55081c6 | major/minor plan을 단일 plan_template.md로 통합하고 minor 전용 템플릿을 제거 |
