---
태스크: issue_request_routing
생성일: 2026-08-28
타입: major
실패비용: major
상태: 완료 승인
승인해시: reqspec-v1:63bcd9510b2226ed
승인대상: 요구사항 명세
---

# 작업 계획서: 이슈 요청 라우팅과 저장 위치 명확화

**파생 출처:** 없음

---

## 요구사항 명세

### 요청 기준

이슈 생성 요청이 명백한 `workspace/issues/` 대신 작업 항목 등 다른 흐름으로 처리되는 원인을 해소한다. 또한 에이전트가 이슈의 내용을 판단해 시스템의 행동 방식·규칙·개선점에 관한 관찰이면, 시스템 개선을 위한 `methodology_improvement` issue로 분류하여 프로젝트 로컬 `workspace/issues/`에 기록해야 한다. 분석 결과, 이슈 생성 요청의 독립 라우팅·분류 기준·정확한 저장 계약이 Runtime 지침에 충분히 없다.

### 목적

에이전트가 이슈 생성·등록 요청을 새 기능/리팩터링으로 오분류하지 않고, 이슈 내용이 시스템 행동 방식·규칙·개선점에 해당하는지 판단해 `methodology_improvement`로 기록하도록 한다. 모든 로컬 원본 이슈는 대상 프로젝트의 `workspace/issues/`에 남기고, 로컬 이슈와 source 중앙 수집함의 역할도 구분한다.

### 범위·제외 범위

- 범위: Runtime 요청 유형 분류, 이슈 기록 세부 계약, source 이슈 README를 보완하고 `dist/.mpa/runtime/`에 동기화한다.
- 범위: 설치 프로젝트가 작성한 `methodology_improvement` 원본 이슈를 source의 `issue-collect`가 동일 kind의 수집 이슈로 정규화하는 동작을 구현·자동 검증한다.
- 범위: 배포 Runtime의 문서·hook 주석에서 source 전용 `release_manager.py` 실행 지시를 제거하고, source 운영 절차는 source 문서에만 남긴다.
- 제외 범위: 기존 이슈 파일의 이동·재구성, 수집/triage 정책 변경, 새 이슈 관리 기능 또는 외부 이슈 트래커 연동.

### 완료 기준

- 이슈 생성·등록 요청이 독립 요청 유형으로 명시되고, 새 작업 항목 생성 흐름으로 라우팅되지 않는다.
- 이슈 내용이 시스템의 행동 방식·규칙·개선점에 관한 관찰이면 `methodology_improvement`로 판정하는 기준과 기록 행동이 명시된다.
- 지침이 로컬 원본 이슈의 정확한 저장 경로와 중앙 수집 이슈의 경계를 구분한다.
- 설치 프로젝트에서 작성한 `methodology_improvement` 원본 이슈를 source가 수집할 때, 원래 kind가 보존된 canonical metadata로 정규화된다.
- Runtime release와 `dist/.mpa/runtime/`의 실행 지침·주석에 `release_manager.py` 실행 지시가 남지 않는다.
- source Runtime과 `dist/.mpa/runtime/`가 동기화되고, 관련 테스트가 통과한다.

### 사용자 결정

- 없음 — 요청한 보완 범위에 따라 Runtime 지침과 source 운영 문서를 함께 정비한다.

### 변경 불가 제약

- 이슈 생성은 대상 프로젝트의 `workspace/issues/`에 남기며, 사용자 요청 또는 승인 없는 중앙 수집·archive를 수행하지 않는다.
- 제품 기능·코드의 일반 버그와 시스템 행동 방식·규칙의 개선 관찰을 혼동하지 않는다. 후자만 `methodology_improvement`로 기록한다.
- 설치 Runtime은 source 전용 `release_manager.py`를 호출하지 않는다. 설치 프로젝트에서 직접 작성한 원본 Markdown은 source의 `issue-collect`가 수집 가능한 형식이어야 한다.
- source 전용 운영 명령의 이름·실행 방법은 Runtime이 아니라 source 운영 문서에만 둔다.
- `dist/.mpa/runtime/`는 직접 편집하지 않고 source Runtime 동기화 결과로만 갱신한다.
- Runtime 변경만으로 새 release를 생성하지 않는다.

### 에이전트 가정

| 가정 | 근거 | 틀렸다면 |
|---|---|---|
| 사용자가 말한 “다른 곳”은 이슈 생성 요청이 일반 작업 요청으로 분류되는 현상이다. | 현재 요청 분류표에 이슈 생성 유형이 없고, `issue-create` 구현 경로는 정확하다. | 실제 잘못 저장된 구체 경로를 확인해 라우팅 외의 생성자·호출부를 별도 조사한다. |
| 시스템 행동 방식·규칙·개선점은 기존 `methodology_improvement`의 의미로 기록한다. | Runtime은 이미 이 kind를 방법론 개선에 사용하지만, 이슈 요청 판단 기준과 legacy 수집 정규화에 연결하지 않았다. | kind 체계 또는 수집 정책을 별도 작업 항목에서 재설계한다. |
| 이슈의 수명주기 정책 자체는 유지한다. | 요청은 위치 문제의 보완 계획이며 수집·triage 변경을 요구하지 않았다. | 정책 변경 요구가 확인되면 별도 요구사항 결정과 계획 갱신이 필요하다. |

### 결정 대기 항목 (Open Questions)

- 없음

---

## 실행 계획 (Implementation Plan)

### 사전 조사

- [x] source Runtime, 배포 Runtime, `release_manager.py`, 관련 테스트의 현재 동작을 재대조했다. / 이유: 새 지침이 이미 구현된 canonical 저장 계약과 어긋나지 않아야 한다.

### 구현 단계

- [x] Step 1 — `.mpa/runtime/core/agent_rules.md`에 이슈 생성/등록 요청과 운영 중 MPA 문제 발견을 모두 `issue 기록` 상세 지침으로 보내는 트리거를 추가했다. / 이유: 명시 요청뿐 아니라 설치 프로젝트에서 작업·검토·회고 중 발견한 시스템 문제도 누락 없이 분류해야 한다.
- [x] Step 2 — `.mpa/runtime/core/agent_rules_detail.md`의 `issue 기록` 섹션에 시스템 행동 방식·규칙·개선점의 `methodology_improvement` 판정 기준과 대상 프로젝트 `workspace/issues/` 원본 기록 계약을 추가했다. / 이유: 설치된 Runtime은 source 도구 없이도 수집 가능한 원본 이슈를 남겨야 한다.
- [x] Step 3 — `.mpa/runtime/core/agent_rules_detail.md`와 `.mpa/runtime/hooks/dist_sync.py`에서 source 전용 `release_manager.py`의 직접 실행 지시·언급을 제거하고, 설치 Runtime에 유효한 일반 제약으로 바꿨다. / 이유: 배포본에 존재하지 않는 도구를 에이전트가 실행 가능한 것으로 오해하지 않게 한다.
- [x] Step 4 — `release_manager.py`에서 설치 프로젝트의 기존 Markdown 템플릿(`**타입**: 방법론 개선`)을 수집할 때 canonical metadata의 kind를 `methodology_improvement`로 정규화했다. / 이유: 수집 뒤에도 시스템 개선 이슈라는 분류가 보존돼 source triage가 정확히 처리할 수 있어야 한다.
- [x] Step 5 — source `workspace/issues/README.md`를 중앙 수집함 전용 문서로 명확히 하고, 설치 프로젝트의 로컬 원본 → 명시 수집 → `inbox/` → 검토·archive 흐름을 문서화했다. / 이유: source 중앙 수집함을 설치 프로젝트의 직접 기록 위치로 오해하지 않게 한다.
- [x] Step 6 — 설치 프로젝트의 plain Markdown `methodology_improvement` 원본을 `issue-collect`로 수집하는 테스트와 release Runtime에 source 전용 명령이 노출되지 않는 검증을 추가·보강했다. / 이유: 배포 Runtime이 남긴 원본 이슈의 수집 호환성과 source/Runtime 경계를 함께 회귀 방지한다.
- [x] Step 7 — source 운영 절차로 Runtime을 `dist/.mpa/runtime/`에 동기화하고 source/dist 차이를 검증했다. / 이유: 설치 대상 Runtime에도 동일한 판단·기록 지침과 source 경계가 적용된다.

### 예상 조용한 결정

- 이슈 요청의 인식 범위: “이슈 등록/생성/기록”, “issue create”처럼 생성 의도가 분명한 발화와, 작업·검토·회고 중 감지한 MPA 시스템 문제를 기록 대상으로 처리한다. 단순히 “이슈를 검토해줘”는 기존 검토 또는 source intake 흐름을 따른다.
- issue kind 판정: 에이전트의 작업 절차, 행동 방식, Runtime 규칙, inject·persona 지침의 결함 또는 개선 제안이면 `methodology_improvement`로 기록한다. 제품 기능·도메인 로직 자체의 버그는 이 기준만으로 시스템 개선 issue로 승격하지 않는다.
- 설치 프로젝트 기록 방식: Runtime의 Markdown 템플릿을 대상 프로젝트 `workspace/issues/`에 직접 기록한다. source 전용 `release_manager.py`를 설치 Runtime에서 호출하지 않으며, source 수집 시 템플릿의 타입을 canonical kind로 정규화한다.
- 배포 Runtime의 source 운영 절차 표현: source 도구명·명령줄 대신 “source 운영자가 사용자 요청 뒤 release·수집을 처리한다”는 제약만 남긴다. 구체 명령은 source 전용 운영 문서에서만 설명한다.
- source 저장소 예외: `workspace/issues/inbox/`와 `archived/`는 수집·검토 결과의 중앙 저장소이며, 일반 프로젝트의 로컬 원본 생성 경로가 아니다.

### 수정 대상 파일

| 파일 경로 | 변경 내용 |
|---|---|
| `.mpa/runtime/core/agent_rules.md` | 이슈 생성 요청 라우팅과 상세 지침 로드 트리거 추가 |
| `.mpa/runtime/core/agent_rules_detail.md` | 설치 프로젝트에서의 `methodology_improvement` 판정 기준과 원본 이슈 기록·수집 경계 계약 명시 |
| `.mpa/runtime/hooks/dist_sync.py` | 배포 hook 주석의 source 전용 도구명 제거 |
| `workspace/issues/README.md` | source 중앙 수집함과 로컬 원본 이슈의 역할 구분 |
| `release_manager.py` | 설치 Runtime의 Markdown `methodology_improvement` 원본을 수집 시 canonical kind로 정규화 |
| `tests/test_release_manager.py` | 설치 프로젝트 원본 이슈의 `issue-collect` 호환성·kind 보존 회귀 검증 |
| `dist/.mpa/runtime/` | sync-runtime 산출물로 source Runtime 변경 반영 |

### 참고 파일 (수정 없음)

- `release_manager.py` — canonical 생성 경로와 metadata의 구현 기준
- `map-product-rules/issue-intake.md` — 중앙 수집의 허용 조건과 이동 보장
- `map-product-rules/command-contract.md` — `issue-create` / `issue-collect` 운영 계약
- `workspace/project_rules.md` — source 프로젝트의 수집 issue 처리 경계

### 반례 (이 계획이 실패할 수 있는 시나리오)

- “이슈를 검토해줘”까지 생성 요청으로 인식해 잘못 파일을 만들 수 있다. → Step 1에 생성 의도가 분명한 발화만 해당한다고 명시하고, 검토·수집은 기존 흐름으로 유지한다.
- 제품 버그를 모두 시스템 개선 issue로 분류해 실제 제품 작업을 놓칠 수 있다. → Step 2에 시스템 규칙·행동 방식 문제일 때만 `methodology_improvement`로 기록한다는 판정 경계를 둔다.
- 설치 Runtime이 source 전용 명령을 호출해 이슈 생성에 실패할 수 있다. → Step 2에서 대상 프로젝트에 직접 원본 Markdown을 기록하도록 하고, Step 3·4·6에서 source 도구 노출 제거와 수집 호환성을 보장한다.
- source 저장소에서 로컬 원본 이슈와 중앙 inbox를 같은 폴더로 혼동해 수집 절차를 우회할 수 있다. → Step 5에서 source 중앙 수집함의 역할과 사용자 승인 없는 이동 금지를 명시한다.
- source만 수정하고 배포 Runtime을 갱신하지 않아 설치된 프로젝트가 이전 라우팅을 유지할 수 있다. → Step 7에 동기화와 source/dist 검증을 완료 조건으로 둔다.

---

## 실행 TODO

### 구현·에이전트 검증

- [x] Runtime의 운영 중 MPA 문제 감지·`methodology_improvement` 판정·원본 이슈 기록 계약과 source 도구 참조를 수정했다.
- [x] source 이슈 README의 경로 역할 설명을 수정했다.
- [x] source의 `issue-collect`가 설치 프로젝트 원본 이슈의 kind를 보존하도록 구현하고 테스트했다.
- [x] release Runtime에 source 전용 `release_manager.py` 실행 지시가 남지 않는지 검증했다.
- [x] Runtime을 `dist/.mpa/runtime/`에 동기화하고 차이를 검증했다.

### 사용자 결정·승인 필요

- [x] 계획서를 검토하고 구현을 승인했다. (2026-08-28 사용자 요청: "작업 진행해줘")

## 검증 결과

### 검증 체크리스트

- [x] 정상 경로: 설치 프로젝트 운영 중 감지한 시스템 행동 방식·규칙·개선점이 로컬 `workspace/issues/`에 `methodology_improvement` 원본 이슈로 기록되도록 Runtime 계약을 추가했다.
- [x] 정상 경로: source의 `issue-collect`가 해당 원본을 `inbox/<project-ref>/`로 이동하고 canonical metadata의 kind를 `methodology_improvement`로 보존함을 단위 테스트로 확인했다.
- [x] 실패 경로: 설치 Runtime이 source 전용 명령에 의존하지 않고, 사용자 요청 또는 승인 없는 중앙 수집·archive를 수행하지 않도록 지침을 명시했다.
- [x] 실패 경로: source·배포 Runtime에서 `release_manager.py` 및 수집 명령 실행 지시가 없음을 검색으로 확인했다. release ZIP은 기존 immutable bundle이므로 새 release를 만들지 않았다.
- [x] 엣지 케이스: 제품 버그 및 이슈 검토·수집 요청은 시스템 개선 issue 생성과 혼동되지 않도록 판정 경계를 명시했다.

### 완료 시 문서 업데이트 대상

- [ ] 없음 — source `workspace/issues/README.md`가 이번 변경의 운영 문서다.

## 운영 시 안내 사항

| 영향 대상 | 운영상 달라지는 점 | 사용자 안내 |
|---|---|---|
| 설치된 MPA 프로젝트 | 이슈 생성 요청은 별도 작업 항목 대신 로컬 이슈 기록으로 처리된다. | 중앙 수집은 계속 명시 요청 또는 승인된 update 절차가 필요하다. |
| my-pacemaker-agent source | `workspace/issues/inbox/`는 수집 후 검토 대상이라는 의미가 더 분명해진다. | 기존 inbox·archive 이슈는 이동하거나 수정하지 않는다. |
| 설치된 MPA 프로젝트 | Runtime 지침 변경이 실제 에이전트의 이슈 기록 행동에 적용되는지 확인할 수 있다. | 시스템 규칙·행동 방식 문제를 한 건 발견 또는 가정해 `workspace/issues/`에 `**타입**: 방법론 개선` 원본 이슈가 남는지 확인한다. |

## 실행 중 변경 기록

| 변경 내용 | 이유 | 명세 영향 |
|---|---|---|
| 설치 Runtime의 MPA 개선 issue 판정·원본 기록 계약 추가 | 운영 중 발견된 개선점을 수집 가능한 로컬 이슈로 남기기 위해 | 없음 |
| legacy Markdown 수집 시 `methodology_improvement` kind 보존 | source 수집 뒤 triage가 시스템 개선 이슈를 식별하도록 하기 위해 | 없음 |
| Runtime의 source 전용 명령 언급 제거 | 설치 프로젝트가 배포되지 않은 도구를 호출하지 않게 하기 위해 | 없음 |

## 명세 변경 이력

| 승인 시각 | 이전 체크섬 | 새 체크섬 | 변경 요약 |
|---|---|---|---|

### 구현 후 발견

| 항목 | 유형 | 발견 맥락 | 처리 경로 |
|---|---|---|---|
| (결과를 경험한 후 채움) | 명세 밖 보완 / 명세 변경 / 신규 작업 항목 | 왜 보기 전에는 보이지 않았는가 | 실행 기록 갱신 / 승인 이력 갱신 / INDEX.md 등록 |

**파생된 작업 항목:**
- (신규 작업 항목 생성 시 여기에 추가됨)
