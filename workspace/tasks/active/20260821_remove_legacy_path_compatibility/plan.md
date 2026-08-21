---
태스크: 20260821_remove_legacy_path_compatibility
생성일: 2026-08-21
타입: major
실패비용: major
상태: 검증 중
승인해시: reqspec-v1:6920c5c150f82a17
승인대상: 요구사항 명세
---

# 작업 항목 계획서: 이전 MPA 경로 호환 규칙 제거

**파생 출처:** `campingtalk-proj`의 `.mpa` 컨테이너 전환·재배포가 완료되어, 이전 경로 호환 규칙이 더 이상 운영 대상이 아니게 됨

## 요구사항 명세

### 요청 기준

현재 MPA Runtime 사용 대상은 `campingtalk-proj` 하나이며 `.mpa/runtime`, `.mpa/config`, `.mpa/backups` 구조로 전환 배포가 끝났다. 이전 경로 정보를 계속 보존·지원하지 않고, 향후 설치·업그레이드 절차를 현재 구조만 기준으로 단순화한다.

### 목적

Runtime 소스·배포 도구·설치 및 운영 문서에서 이전 경로 호환 분기를 제거하여, MPA의 유일한 활성 구조를 `.mpa/` 컨테이너로 고정한다.

### 범위·제외 범위

- 범위: 이전 Runtime·config·backup 경로 탐지와 자동 migration 코드를 제거하고, 현재 `.mpa` 구조만 허용하도록 설치·업그레이드 사전 점검을 정리한다.
- 범위: Runtime, release 도구, 테스트, 설치·업그레이드 문서 및 관리 대상 agent 경로 안내에서 이전 경로 설명을 제거한다.
- 범위: 패키징된 Runtime의 asset checksum과 핵심 hook 정적 문법을 검증하고, 새 release를 준비한다.
- 제외 범위: `campingtalk-proj`의 업무 코드·`workspace/` 데이터·프로젝트 고유 설정 값·과거 backup 및 release receipt의 감사 이력 변경.
- 제외 범위: 다른 구조를 사용하는 대상 프로젝트를 위한 호환성·자동 migration 제공.

### 완료 기준

- 설치·업그레이드·rollback의 활성 경로 계약은 `.mpa/runtime`, `.mpa/config`, `.mpa/backups`만 사용한다.
- Runtime이 `.mpa/runtime`에 없는 대상은 자동 변환하지 않고, 명확한 사전 점검 오류로 중단한다.
- `.mpa/config/config.yaml` 및 `.mpa/config/config.toml`의 기존 값 보존·누락값 additive 초기화·rollback snapshot 규칙은 유지된다.
- 불변 release ZIP을 대상으로 asset checksum과 핵심 hook 정적 문법 검증이 통과한다.

### 사용자 결정

- 이전 구조는 전환 완료 이력일 뿐, 이후 설치·업그레이드에서 지원하거나 반복 검사하지 않는다.
- Runtime의 유일한 설치 위치는 `.mpa/runtime`이다.
- 프로젝트 고유 설정은 `.mpa/config`에 계속 보존한다.

### 변경 불가 제약

- Runtime 배포는 프로젝트 고유 설정의 기존 값을 덮어쓰지 않는다.
- 과거 backup·release receipt·task 이력은 삭제하거나 재작성하지 않는다.
- 새 release는 source `dist/`가 아니라 검증된 immutable ZIP·manifest만으로 배포한다.

### 에이전트 가정

| 가정 | 근거 | 틀렸다면 |
|---|---|---|
| 현시점에 이전 경로 구조를 사용하는 배포 대상은 없다. | 사용자가 `campingtalk-proj`만 사용하며 전환 배포가 완료됐다고 확인했다. | 호환 제거를 중단하고 대상별 migration 계획을 별도 수립한다. |
| 과거 경로 기록은 backup·receipt·task 이력에서만 필요하다. | 운영 규칙이 아닌 감사·복구 근거다. | 보존이 필요한 활성 문서를 별도 allowlist로 정한다. |

### 결정 대기 항목 (Open Questions)

- 없음

## 실행 계획

### 사전 조사

- `release_manager.py`, `install.py`, `project_config.py`, agent spec, Runtime 및 배포 문서에서 이전 경로 탐지·변환·설명 위치를 전수 조사한다.
- 실행 레이어와 설명·감사 이력을 구분해, 제거 대상과 보존 대상을 파일 목록으로 확정한다.

**조사 결과:** 이전 경로의 실행 전환 로직은 `release_manager.py`의 Runtime 해석·설정 이동·agent wiring 치환과 deploy receipt에만 있었다. Runtime·설치 문서·agent spec에는 활성 참조가 없었다. package 검증 경로는 `prepare_release` → `validate_packaged_runtime` 및 `audit_releases` → `validate_packaged_runtime`으로 정리한다.

### 구현 단계

- [x] 이전 경로 fallback·migration 로직을 제거하고, 설치·배포 preflight가 현재 `.mpa` 구조만 허용하도록 수정한다.
- [x] 설정 보존·additive 초기화·rollback snapshot 동작이 legacy 분기 없이 유지되도록 테스트를 갱신한다.
- [x] 설치·업그레이드·배포 운영 문서를 현재 경로 전용 절차로 개정한다.
- [x] 패키징된 Runtime의 asset checksum과 핵심 hook 정적 문법을 검사하는 release 검증을 추가한다.
- [x] 테스트·release audit을 실행하고, 새 release를 준비한다.

### 예상 조용한 결정

- 이전 경로가 감지되면 자동 변환 대신 오류를 낸다. 사용자가 정한 “더 이상 지원하지 않음”을 기계적으로 보장하기 위해서다.
- 과거 backup·receipt·task 이력의 문자열은 수정하지 않는다. 이들은 실행 경로가 아닌 감사 기록이기 때문이다.
- agent wiring 파일은 현행 `.mpa/runtime` 참조만 검증하며, 배포가 사용자 설정을 임의로 재작성하지 않는다.

### 수정 대상 파일

| 파일 경로 | 변경 내용 |
|---|---|
| `release_manager.py` | 이전 경로 탐지·migration·fallback 제거, current-layout preflight 및 manifest 기반 검증 보강 |
| `install.py`, `project_config.py` | `.mpa` 전용 초기 설치·설정 보존 계약으로 정리 |
| `tests/` | current-layout 거부·보존·rollback·패키지 정적 검증 테스트 |
| `MAP_PRODUCT_RULES.md`, `map-product-rules/*.md` | 설치·배포·release 절차를 현재 구조 전용으로 개정 |
| `README.md`, `install.md` 및 관련 Runtime 문서 | 이전 경로 설명 제거, 파일 소유권·검증·rollback 절차 명시 |
| `.mpa/runtime/` 및 `dist/.mpa/runtime/` | Runtime 내부의 이전 경로 참조 제거 및 동기화 |

### 참고 파일 (수정 없음)

- `workspace/releases/` — 불변 release 이력
- `workspace/receipts/` — 대상별 배포·rollback 감사 이력
- `campingtalk-proj/.mpa/backups/` — 대상 Runtime 복구 snapshot

### 반례

- 다른 대상에 이전 구조가 뒤늦게 발견된다 → 자동 변환하지 않고 배포를 중단한다. 해당 대상 전용 migration 작업을 별도로 설계한다.
- 제거 과정에서 설정 보존 로직까지 함께 사라진다 → 구현 2단계의 config 보존·rollback 테스트로 방지한다.
- release ZIP의 hook이 손상된다 → 구현 4단계의 ZIP 임시 해제·정적 문법 검사로 방지한다.

## 실행 TODO

### 구현·에이전트 검증

- [x] current-layout 전용 코드·문서·테스트 반영
- [x] package asset checksum·핵심 hook 정적 문법, 자동 테스트와 release audit 통과
- [x] immutable release 준비 및 dry-run 결과 확인

### 사용자 결정·승인 필요

- [ ] 요구사항 명세 승인

## 검증 결과

### 검증 체크리스트

- [x] 정상 경로: `.mpa` 구조의 신규 설치·업그레이드가 Runtime 교체와 설정 보존을 수행한다. — 74개 자동 테스트 통과
- [x] 실패 경로: Runtime이 없는 대상은 파일 변경 없이 현재 구조 초기화 오류로 중단한다. — `test_deployment_dry_run_requires_current_runtime_layout`
- [x] 엣지 케이스: `config.yaml`·`config.toml`이 그대로 유지되고, rollback이 Runtime 및 예정된 설정 snapshot만 복원한다. — 기존 config migration·rollback 회귀 테스트 통과
- [x] 패키지 검증: release ZIP을 임시 설치 위치에 풀어 매니페스트 해시·핵심 hook 정적 문법을 확인한다. — 75개 자동 테스트 및 release audit 17개 bundle 통과

### 완료 시 문서 업데이트 대상

- [x] `README.md` — 현재 설치 구조와 파일 소유권
- [x] `install.md` — 신규 설치·업그레이드·rollback 절차
- [x] `map-product-rules/installation.md` — current-layout 전용 설치 계약 (기존 계약 유지 확인)
- [x] `map-product-rules/deployment-coordination.md` — current-layout 전용 배포·rollback 계약

## 운영 시 안내 사항

| 영향 대상 | 운영상 달라지는 점 | 사용자 안내 |
|---|---|---|
| `campingtalk-proj` | 이후 Runtime update는 `.mpa` 구조만 검사·교체한다. | 현재 구조가 유지되는 한 추가 migration은 필요 없다. |
| 예상 밖의 구식 설치본 | 자동 migration을 제공하지 않는다. | 별도 migration 작업을 승인한 뒤 처리한다. |

## 실행 중 변경 기록

| 변경 내용 | 이유 | 명세 영향 |
|---|---|---|
| 이전 경로 fallback·config/agent 자동 migration 제거 | 전환 배포가 완료되어 호환 지원이 더 이상 필요하지 않음 | 없음 |
| ZIP 임시 Runtime hash·핵심 hook 정적 문법 검증으로 전환 | package를 release audit 중 실행하지 않고 손상된 hook을 차단 | 명세 변경 |
| release `20260821072219-509b2b84` 준비 및 campingtalk-proj dry-run 성공 | 축소된 검증 계약으로 immutable bundle 재생성·배포 가능성 확인 | 없음 |
| manifest `asset_root`를 `.mpa/runtime`으로 명시 | 대상 Runtime 기준의 독립 해시 검증 경로를 명확화 | 없음 |
| release `20260821064957-b096f109` 준비 및 campingtalk-proj dry-run 성공 | current-layout 전용 release의 배포 가능성 확인 | 없음 |

## 명세 변경 이력

| 승인 시각 | 이전 체크섬 | 새 체크섬 | 변경 요약 |
|---|---|---|---|

### 구현 후 발견

| 항목 | 유형 | 발견 맥락 | 처리 경로 |
|---|---|---|---|
| (결과를 경험한 후 채워짐) | 명세 밖 보완 / 명세 변경 / 신규 작업 항목 | 왜 보기 전에는 보이지 않았는가 | 실행 기록 갱신 / 승인 이력 갱신 / INDEX.md 등록 |
| 2026-08-21T07:22:04Z | reqspec-v1:3e63a1e0508d8c5d | reqspec-v1:6920c5c150f82a17 | Remove retired-path string scanning and replace packaged hook execution with static syntax validation |
