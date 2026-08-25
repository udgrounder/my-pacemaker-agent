---
태스크: 20260824_project_hardening
생성일: 2026-08-24
타입: major
실패비용: critical
상태: 구현 중
승인해시: reqspec-v1:fb71ee35cdfdbbc5
승인대상: 요구사항 명세
---

# 작업 계획서: MPA 프로젝트 보완 및 안전성 강화

**파생 출처:** 2026-08-24 프로젝트 구조·설치·배포·게이트 검토에서 확인된 경로 불일치, 승인 상태 불일치, 경계 검증 취약점, 검증 공백

---

## 요구사항 명세

### 요청 기준

대상 프로젝트에 설치된 MPA가 AI agent와의 작업을 계획·승인·구현·검토하는 목적을 실제 설치 환경에서도 안정적으로 수행하는지 보완한다. 검토에서 확인된 실행 경로 불일치와 안전성 공백을 우선순위에 따라 해소하고, 수정 결과를 자동 검증할 수 있어야 한다.

### 목적

설치된 MPA의 모든 agent 진입점·규칙·hook이 동일한 `.mpa/runtime` 계약을 사용하고, 계획 승인·코드 게이트·파일 경계·릴리즈 검증이 문서와 구현에 일치하도록 만든다. 사용자가 작업을 효율적이고 안전하게 진행할 수 있도록 실패를 조기에, 설명 가능한 방식으로 드러낸다.

### 범위·제외 범위

- 범위: `agent-specs/`, 설치 스크립트, source Runtime, `dist/.mpa/runtime/`의 활성 경로 참조와 hook 등록 정합성 보완
- 범위: active plan의 승인해시·상태·legacy 경로 정합성 감사 및 정상 복구 절차 정리
- 범위: code gate의 기본 모드·승인 상태·작업 범위 검증 정책 정렬
- 범위: runtime/config/workspace/docs 및 백업 경계의 symlink·path traversal 방어와 설정 symlink 오류 수정
- 범위: 사용자가 명시한 외부 task·명세·로그·자료의 읽기, 지속 입력 보관 시 출처 기록, 외부 파일 수정 권한 경계 정의
- 범위: release package 검증, legacy 경로 탐지, hook 문법 검증, 로그·receipt의 민감 경로 노출 최소화
- 범위: Claude/Codex/Antigravity/OpenAgent 설치·hook 회귀 테스트와 CI 자동 검증 추가
- 범위: agent별 지원 수준, memory 초기화·보존 정책, guardrail의 한계를 문서에 명확히 표시
- 제외 범위: 대상 프로젝트의 업무 코드·사용자 데이터·기존 immutable release/receipt/backup 이력 재작성 또는 삭제
- 제외 범위: 사용자의 명시적 요청 없는 새 release 생성·실제 대상 프로젝트 배포·rollback 실행
- 제외 범위: 기존 active plan을 승인 없이 직접 완료·삭제·재작성하는 처리

### 완료 기준

- 새 설치의 모든 활성 agent 진입점·native rule·hook 명령이 존재하는 `.mpa/runtime` 경로를 가리키고, clean-install 실행 검증이 통과한다.
- source Runtime과 `dist/.mpa/runtime/`가 동일하며, 활성 소스·패키지에서 retired `.mpa-workspace` 실행 참조가 검출되지 않는다.
- active plan의 승인 이후 상태는 현재 요구사항 명세와 일치하는 `reqspec-v1` 승인해시를 갖고, 불일치 plan은 사용자 승인 절차를 거친 복구 경로로만 정상화된다.
- code gate의 기본 동작이 문서·agent spec·테스트와 일치하고, 위험한 우회 경로와 적용 범위가 명시된 검증으로 탐지된다.
- runtime/config/관리 대상 디렉터리의 symlink 및 대상 root 외부 접근이 preflight에서 안전하게 거부되며, 설정 symlink가 예외를 발생시키지 않는다.
- 사용자가 명시한 외부 파일은 읽기 전용으로 검토할 수 있고, 지속적으로 참조할 자료는 출처·무결성 정보를 남겨 보관하며, 외부 파일 수정은 명시 승인과 좁은 대상 범위가 있어야만 수행된다.
- release audit가 모든 활성 hook의 정적 문법과 legacy 경로·민감한 절대 경로 노출을 검증하고, 원본 immutable 이력은 보존한다.
- 지원 대상 agent별 설치·hook 실행 회귀 테스트와 CI 명령이 재현 가능하며, 전체 테스트·release audit·runtime/dist parity 검증이 통과한다.

### 사용자 결정

- 사용자 불편을 최소화하기 위해 모든 작업을 기본 차단하지 않는다. 일반 작업은 절차 안내·경고를 기본으로 하고, critical 작업·release/deploy와 승인 무결성 위반처럼 실패 비용이 큰 상황에서만 강한 차단을 적용하는 위험도 적응형 gate를 설계한다. 사용자는 필요 시 strict block 모드를 명시적으로 선택할 수 있어야 한다.
- `critical`의 기본 차단은 사용자가 선택·재개하여 `workspace/tasks/CURRENT_TASK`로 식별한 작업에만 적용한다. 선택되지 않은 기존 active task의 이상은 경고로 남기며, 모든 active task에 대한 전역 차단은 명시적 `MPA_GATE=block`에서만 적용한다. release/deploy/rollback의 사전 차단은 작업 선택과 무관하게 유지한다.
- 신규 설치에서 누락된 Claude·Codex·Gemini guide 문서는 모두 생성한다. 다만 native 설정·hook은 사용자가 선택한 agent에만 연결하며, 기존의 선택하지 않은 agent guide 문서는 수정하지 않는다.
- 보완은 다음 3개 하위 작업으로 순차 진행한다: Runtime wiring, adaptive gate·plan integrity, release boundary·CI.
- 이미 완료된 작업의 plan·이력·artifact는 처리하지 않는다. 진행 중인 기존 작업은 사용자가 해당 작업을 다시 요청할 때에만 현재 보완 내용을 범위에 흡수하고 정상 승인 절차를 밟는다.
- legacy 문자열 검사는 활성 source·agent 설정·배포 package에만 적용한다. immutable release·receipt·backup·완료 task 이력은 보존하고 검사 실패 대상으로 삼지 않는다.
- 외부 task·명세·로그 등의 검토는 사용자가 지정한 경로를 읽기 전용으로 허용한다. 지속 입력은 `workspace/references/` 등 보존 위치에 출처·해시와 함께 기록하고, 외부 파일 수정은 사용자의 명시 승인과 정확한 경로 범위가 있을 때만 허용한다.

### 변경 불가 제약

- Runtime 배포 소스는 source `.mpa/runtime/`이며, 변경 후 `dist/.mpa/runtime/`를 동기화한다.
- 기존 대상 프로젝트의 사용자 설정·workspace·agent 사용자 정의·일반 소스는 보존하고, migration·정리 작업을 자동으로 수행하지 않는다.
- MPA 관리 경로의 symlink는 허용하지 않되, 사용자가 지정한 외부 파일의 읽기와 승인된 외부 파일 수정은 별도의 명시적 입력·권한 경로로 처리한다.
- immutable release·receipt·backup·과거 task 이력은 감사 근거로 보존하며, 활성 실행 코드·문서와 분리해 검사한다.
- 사용자의 명시적 release/deploy 요청 없이 release 생성이나 대상 배포를 실행하지 않는다.
- critical 작업은 계획 승인과 단계별 위험 확인 없이 구현을 시작하지 않는다.

### 에이전트 가정

| 가정 | 근거 | 틀렸다면 |
|-----|------|---------|
| 현재 정본 경로는 `.mpa/runtime`이고 `.mpa-workspace`는 retired 실행 경로다. | architecture 및 설치 검토에서 source/dist/runtime 계약이 `.mpa/runtime`으로 통일되어 있음 | legacy 호환을 유지해야 하는 대상별 migration 계획으로 범위를 재작성한다. |
| 보완은 source·dist·설치 spec·테스트를 함께 변경해야 완결된다. | clean install에서 native agent 파일과 hook marker의 불일치가 확인됨 | 영향 범위를 재조사하고 단일 파일 minor 작업으로 축소한다. |
| 과거 immutable artifact의 문자열은 실행 참조가 아닌 감사 이력이다. | release/receipt 보존 불변식 | 보존 이력도 실행 검증 대상이라는 정책을 별도 결정으로 올린다. |
| 기존 active plan의 invalid hash는 자동 수정하지 않고 사용자 승인 기반으로 복구해야 한다. | `plan_hash.py`의 승인·renew-spec 거버넌스 | 해당 plan 소유자와 복구 승인 범위를 먼저 확정한다. |

### 결정 대기 항목 (Open Questions)

- 없음

### minor 판단 근거

이 작업은 다중 파일·설계 결정·critical 안전 경계·설치/배포 영향이 있으므로 minor가 아니다.

---

## 실행 계획 (Implementation Plan)

### 작업 분할과 순서

| 순서 | 하위 작업 | 결과물 | 선행 조건 |
|---|---|---|---|
| 0 | [Release boundary·CI](sub_03_release_boundary_ci.md)의 최소 preflight | install·archive의 path/symlink 안전 기반 | 없음 |
| 1 | [Runtime wiring](sub_01_runtime_wiring.md) | 설치된 agent·hook의 단일 `.mpa/runtime` 경로 계약 | 0단계 안전 기반 |
| 2 | [Adaptive gate·plan integrity](sub_02_adaptive_gate_and_plan_integrity.md) | 위험도 적응형 차단 정책과 진행 중 task의 정상 흡수 절차 | 1단계 경로 계약 |
| 3 | [Release boundary·CI](sub_03_release_boundary_ci.md)의 나머지 | package 검증, 외부 입력 경계, E2E·CI | 1·2단계 검증 결과 |

### 명령별 파일 경계

| 명령·흐름 | 읽기·쓰기 허용 경로 | symlink 정책 |
|---|---|---|
| 신규 install | 대상 root 내부의 `.mpa/`, `workspace/`, `docs/`, agent 설정 | 생성·병합 전에 해당 경로가 대상 root 내부의 실제 디렉터리인지 확인 |
| deploy / rollback | `.mpa/runtime/`, `.mpa/config/`, `.mpa/backups/` 및 검증된 release bundle | 이 경로만 검사·교체하며 `workspace/`, `docs/`, agent 설정은 읽거나 변경하지 않음 |
| release audit | source Runtime과 staging package | ZIP의 symlink·special file·traversal 항목을 거부하고, immutable 이력은 검사 root에서 제외 |
| 외부 자료 검토 | 사용자가 명시한 외부 파일·디렉터리 | 읽기 전용. 보관 시 출처·해시 기록, 수정은 승인 시점의 실경로·무결성 재확인 후 정확한 대상만 허용 |

### 구현 단계

- [x] Step 1 — install·deploy·rollback·audit의 허용 경로와 symlink 검사 지점을 명령별로 구현하고, ZIP의 symlink·special file·traversal 항목을 거부한다. / 이유: clean-install·package 실행 전에 대상 root 경계와 archive 안전성을 먼저 고정한다. — install 16개·release manager 48개 회귀 테스트 통과
- [x] Step 2 — active source·agent spec·설치 결과의 실행 경로를 `.mpa/runtime` 하나로 고정하고 clean-install E2E를 추가한다. / 이유: 설치 성공 표시와 실제 native agent/hook 실행의 차이를 제거한다. — `test_install.py` 15개 통과
- [x] Step 3 — 기본 경고, 선택된 critical·release/deploy 보호, 명시적 strict mode와 진행 중 task의 승인 무결성 진단을 하나의 판정 경로로 구현·문서화한다. / 이유: 일상 작업의 흐름을 지키면서 승인 우회와 일시적 정책 불일치를 막는다. — `CURRENT_TASK` 기반 회귀 테스트와 `README.md`·`agent_rules.md` 반영
- [ ] Step 4 — 사용자 지정 외부 입력의 읽기·보관·수정 권한을 구현하고, 승인 시점과 수정 직전의 실경로·무결성을 재확인한다. / 이유: 외부 작업 근거 사용은 보장하면서 symlink 교체로 다른 파일을 수정하는 위험을 막는다.
- [ ] Step 5 — 활성 package의 legacy 실행 참조·모든 hook 문법·민감한 절대 경로 노출을 검증하고, receipt 기록을 최소화한다. / 이유: 재발 방지 검증은 유지하되 immutable 감사 이력은 훼손하지 않는다.
- [ ] Step 6 — agent별 E2E, symlink·gate·package 회귀 테스트와 CI 명령을 추가하고 source/runtime-dist parity·전체 테스트·release audit을 실행한다. / 이유: 향후 경로 드리프트와 안전 경계 회귀를 자동으로 발견한다.

### 위험도 적응형 gate 정책

| 상황 | 기본 동작 | 사용자 개입 |
|---|---|---|
| 일반 소스 변경의 작업 항목·계획 누락 | warn: 이유와 복구 경로를 고지하고 작업 흐름은 유지 | 필요 시 agent가 계획 등록을 제안 |
| critical plan의 승인 누락·승인해시 불일치 | block: 변경을 중단하고 승인/복구 절차를 제시 | 사용자가 계획을 검토·승인 |
| release/deploy/rollback | 별도 preflight에서 block: package·경계·승인 조건 미충족 시 실행 불가 | 사용자가 dry-run 결과와 실행을 명시 승인 |
| 사용자가 strict mode를 켠 경우 | block: 모든 gate 위반을 차단 | 사용자가 `MPA_GATE=block`을 명시 |

### 예상 조용한 결정

- `block`은 사용자에게 자동 문의를 보내는 동작이 아니라 hook의 비정상 종료이며, agent가 필요한 경우에만 평이한 복구 안내를 제시한다.
- adaptive 정책의 critical 판정은 plan frontmatter의 `실패비용: critical`과 release/deploy 명령의 별도 preflight를 기준으로 구현한다.
- 기존 active task는 일괄 정리하지 않는다. 재개 요청 시에만 기존 사용자 결정·요구사항을 보존한 채 신규 보완 범위를 추가하고 재승인을 받는다.
- legacy 문자열 검사는 파일 전체 삭제·치환 도구가 아니라 실행 등록이 과거 경로를 가리키는지 확인하는 allowlist 기반 검증이다.
- 외부 자료는 MPA 관리 디렉터리를 향하는 symlink로 연결하지 않고, 명시적 읽기 경로 또는 출처를 기록한 보관본으로 취급한다.

### 수정 대상 파일

| 파일 경로 | 변경 내용 |
|---|---|
| `agent-specs/`, `.claude/`, `.codex/`, `.agents/` | 활성 agent rule·hook·설치 파일의 retired 경로 제거 및 설치 계약 정렬 |
| `install.py` | hook marker를 현재 Runtime 경로로 정렬 |
| `project_config.py`, `release_manager.py` | 설치/설정 path 검증, symlink 방어, package·receipt 처리 보완 |
| `.mpa/runtime/hooks/`, `.mpa/runtime/core/`, `.mpa/runtime/templates/` | adaptive gate와 plan integrity 진단·문서·테스트 계약 반영 |
| `tests/`, CI 설정 파일 | clean install, agent별 hook, gate, symlink, package 검증 회귀 테스트 |
| `README.md`, `install.md`, `map-product-rules/*.md` | 지원 범위, 안전 정책, 운영 절차와 guardrail 한계 설명 |
| `dist/.mpa/runtime/` | source Runtime 동기화 결과만 반영 |

### 참고 파일 (수정 없음)

- `workspace/releases/`, `workspace/receipts/` — immutable 감사 이력으로 보존
- `workspace/tasks/done/` — 완료 task 이력으로 보존
- 기존 active task의 `plan.md` — 사용자가 해당 task 재개를 요청하기 전에는 변경하지 않음

### 반례 (이 계획이 실패할 수 있는 시나리오)

- 일반 작업도 critical로 오분류되어 반복 차단된다 → Step 2에 plan frontmatter·명시 strict mode 기반 판정과 warn 회귀 테스트를 포함한다.
- native agent 파일 하나가 새 경로로 갱신되지 않아 설치 후 hook이 실패한다 → Step 1에 지원 agent별 clean-install 후 등록된 경로 존재·실행 검증을 포함한다.
- symlink 검사만 추가하고 backup/rollback 보조 경로가 빠진다 → Step 4에 runtime/config/workspace/docs/backups 전체의 거부 테스트를 포함한다.
- 외부 task 파일까지 차단되어 작업 근거를 읽지 못한다 → Step 4에 사용자 지정 외부 파일의 읽기 허용과 MPA 관리 symlink 거부를 구분하는 테스트를 포함한다.
- immutable 과거 receipt의 legacy 문자열 때문에 release audit이 항상 실패한다 → Step 5에 검사 roots를 활성 source·staging package로 고정하고 이력 제외 테스트를 포함한다.
- 검사 뒤 symlink가 교체되거나 ZIP이 특수 파일을 포함한다 → Step 1에서 staging 해제·검사·교체의 허용 파일 유형과 원자적 처리 규칙을 검증한다.

---

## 실행 TODO

### 구현·에이전트 검증

- [x] 하위 작업 1: Runtime wiring 구현 및 clean-install E2E 통과 — `python3 -m unittest discover -s tests -p 'test_install.py' -v` (15 tests OK)
- [x] 하위 작업 2: adaptive gate·plan integrity 구현 및 정상/경고/차단 회귀 테스트 통과 — 선택된 critical task만 기본 차단, `test_plan_hash.py` 26개 통과
- [ ] 하위 작업 3: release boundary·CI 구현 및 symlink/package/로그 검증 통과
- [x] source/runtime-dist parity, 전체 단위 테스트, release audit 통과 — parity 일치, 전체 101 tests OK, release audit 20 bundles 통과
- [ ] 독립 비평 결과를 반영하고 critical 변경의 검증 증빙 기록

### 사용자 결정·승인 필요

- [x] 위험도 적응형 gate 정책 결정
- [x] 3개 하위 작업 순차 분할 결정
- [x] 완료 작업 미처리 및 진행 중 task의 사용자 요청 기반 흡수 결정
- [x] 활성 source·package만 legacy 실행 참조 검사 결정
- [x] 명시적 외부 입력의 읽기·보관·수정 권한 경계 결정
- [x] 요구사항 명세 승인 후 `plan_hash.py approve`로 구현 전환 — `reqspec-v1:307bd6a456ea0ac6`

## 검증 결과

### 검증 체크리스트

- [x] 설계 단계: 기존 테스트 83개와 release audit 19개 bundle이 현재 baseline에서 통과함을 확인
- [x] 설계 단계: clean install에서 native agent 경로·hook marker 불일치를 재현함
- [x] 설계 단계: active plan 1건의 승인해시 불일치와 symlink 경계 오류를 재현함
- [x] 독립 검증: `test_install.py` 16개·`test_release_manager.py` 48개 및 `git diff --check` 통과. 상세: [independent_validation.md](independent_validation.md)
- [x] 독립 검증 보완: config 상위 symlink·deploy/rollback symlink·ZIP symlink/type mismatch 회귀 테스트 추가 후 install 17개·release manager 51개 통과
- [x] 구현 후 정상·실패·엣지 케이스 검증 — 선택 critical의 승인 전·해시 불일치 차단, 미선택 critical 경고, CURRENT_TASK traversal 거부 회귀 테스트 통과

### 완료 시 문서 업데이트 대상

- [x] `README.md` — 안전 게이트 기본값·선택 task 기반 guardrail 동작 반영
- [x] `install.md` — 기본 warn·선택 critical 차단 정책과 실제 hook/agent 경로 확인 절차 반영
- [ ] `map-product-rules/release-preparation.md` — package 검증·로그 정제 규칙
- [ ] `workspace/memory/shared/architecture.md` — 보완 결과가 기존 경계 결정을 바꿀 때만 현재 상태로 갱신

## 운영 시 안내 사항

| 영향 대상 | 운영상 달라지는 점 | 사용자 안내 |
|---|---|---|
| MPA 설치 사용자 | 설치 후 agent별 native rule과 hook 연결 검증이 수행됨 | 지원 agent별 설치 결과와 hook 실행 결과를 확인해야 함 |
| MPA 작업 사용자 | gate 기본 정책과 승인해시 오류 처리 방식이 명확해짐 | 계획 승인·완료 확인 없이 상태를 우회하지 않음 |
| release 운영자 | 활성 package만 legacy·민감 경로 검증 대상이 됨 | immutable 과거 release/receipt는 감사 목적으로 보존 |

## 실행 중 변경 기록

| 변경 내용 | 이유 | 명세 영향 |
|---|---|---|
| 명령별 파일 경계·archive 안전성·외부 수정 재확인 규칙을 실행 계획에 추가 | 독립 비평에서 deploy 경계 충돌·TOCTOU·ZIP 특수 파일 위험을 확인 | 없음 |
| source agent 설정·agent spec의 retired 경로를 `.mpa/runtime`으로 통일하고 current hook marker 회귀 테스트 추가 | clean install은 성공해도 native agent/hook이 존재하지 않는 retired 경로를 가리키던 문제 해소 | 없음 |
| Runtime·backup·필수 설치 경로의 symlink와 ZIP 특수 파일을 사전 거부하고 config symlink를 정상 경고로 처리 | 대상 root 외부 읽기·쓰기와 config inspection의 내부 오류 방지 | 없음 |
| 독립 검증에서 config 상위 symlink·rollback symlink·ZIP 파일 유형별 거부 테스트가 부족함을 확인 | 구현은 통과했으나 critical 경계의 회귀 증빙을 완결해야 함 | 없음 |
| 독립 검증에서 발견된 경계 분기를 회귀 테스트로 추가 | config parent·deploy/rollback·archive type 분기까지 차단 증빙을 완결 | 없음 |
| CURRENT_TASK로 사용자 선택 task를 식별하고 선택된 critical task의 승인 전·승인해시 오류만 기본 차단 | 과거 active critical task의 오류가 관련 없는 일상 수정을 전역 차단하지 않게 하면서 재개한 고위험 작업은 보호 | 사용자 정책 명확화·승인 반영 |
| 비-Git 프로젝트 하위 폴더에서 Codex hook이 상위 `.mpa/runtime`을 찾도록 보완하고, 신규 설치의 누락 guide 문서를 3개 agent용으로 생성 | 설치 검토에서 hook 경로 실패와 agent 전환 시 guide 문서 누락을 재현 | 사용자 요청 반영 |
| 실행 상태 최신화 | 완료된 Step 3·전체 검증·설치 문서 증빙을 체크하고, 외부 입력·package/로그·CI 작업은 미완료로 유지 | 없음 |

## 명세 변경 이력

| 승인 시각 | 이전 체크섬 | 새 체크섬 | 변경 요약 |
|---|---|---|---|

### 구현 후 발견

| 항목 | 유형 | 발견 맥락 | 처리 경로 |
|------|------|-----------|-----------|
| (구현 후 채움) | 명세 밖 보완 / 명세 변경 / 신규 작업 항목 | 결과물을 직접 사용한 뒤 확인 | 실행 기록 갱신 / 승인 이력 갱신 / INDEX.md 등록 |
| config 상위 경로·rollback 및 ZIP type mismatch의 회귀 테스트 부족 | 독립 검증에서 모든 거부 분기가 직접 증명되지 않음 | `tests/test_install.py`, `tests/test_release_manager.py`에 회귀 테스트 추가 |
| config 상위 경로·rollback 및 ZIP type mismatch 회귀 테스트 추가 | 독립 검증 M2 발견을 즉시 보완 | `test_install.py` 17개, `test_release_manager.py` 51개 통과 |

**파생된 작업 항목:**
- (사용자 결정 후 필요 시 추가)
| 2026-08-24T11:25:01Z | reqspec-v1:307bd6a456ea0ac6 | reqspec-v1:c40c43beaadff725 | 선택·재개한 critical 작업만 기본 차단하고 전역 strict 차단은 MPA_GATE=block으로 한정 |
| 2026-08-25T01:55:21Z | reqspec-v1:c40c43beaadff725 | reqspec-v1:fb71ee35cdfdbbc5 | 비-Git 하위 폴더 Codex hook 경로 보완 및 누락된 Claude·Codex·Gemini guide 문서 공통 생성 |
