---
태스크: 20260821_runtime_deployment_boundary
생성일: 2026-08-21
타입: major
실패비용: critical
상태: 설계 완료
승인해시: ""
승인대상: 요구사항 명세
---

# 작업 항목 계획서: Runtime 설치·업그레이드 경계 보완

**파생 출처:** 캠핑톡 프로젝트의 Runtime 배포에서 `.mpa-workspace/config.toml`이 삭제되고, 설치 고유 설정 경계가 불명확했던 문제

## 요구사항 명세

### 요청 기준

설치와 업그레이드 절차에서 배포되는 MPA의 설치 위치와 프로젝트 고유 설정 위치를 명확히 정리한다. Runtime 업그레이드가 기존 설치본의 보존 대상 파일을 삭제하지 않도록 하며, 의미가 모호한 기존 폴더명을 명확한 이름으로 migration한다.

### 목적

신규 설치와 Runtime 업그레이드의 소유권 경계를 명시하고 기계적으로 보장하여, 업그레이드가 `.mpa/runtime/`만 최신화하고 `.mpa/config/`와 프로젝트 데이터는 보존하게 한다.

### 범위·제외 범위

- 범위: legacy 분리 경로를 `.mpa/runtime/`, `.mpa/config/`, `.mpa/backups/` 단일 컨테이너 구조로 migration하고 배포·백업·검증 로직을 구현한다.
- 범위: 기존 설치에 설정 파일이 없을 때 `.mpa/config/config.yaml`을 additive 방식으로 초기화한다.
- 범위: legacy `.mpa-workspace/config.toml`을 `.mpa/config/config.toml`로 보존하고, 기존 agent 진입점·hook 설정의 `.mpa-workspace` 참조를 `.mpa/runtime`으로 전환한다.
- 범위: 신규 설치·업그레이드·rollback 절차와 파일 소유권을 문서화한다.
- 제외 범위: 개별 대상 프로젝트의 업무 코드·`workspace/` 데이터·agent 설정 변경, 기존 대상의 Git 커밋/푸시.

### 완료 기준

- Runtime release 배포가 `.mpa/runtime/`만 교체하고 `.mpa/config/` 및 `workspace/`를 보존함을 검증으로 보장한다.
- 신규 설치, 기존 Runtime 업그레이드, legacy 설치 migration과 rollback의 대상 경계·파일 위치가 문서에 명확히 제시된다.
- 배포 후 관리 대상 agent 설정과 hook에서 `.mpa-workspace` 참조가 남지 않으며, legacy 설정 파일의 내용이 보존된다.
- 자동 테스트가 보존·초기화·rollback 경로를 검증한다.
- 변경된 Runtime은 검증된 단일 release로 준비할 수 있다.

### 사용자 결정

- Runtime은 `.mpa/runtime/`에 설치한다.
- 설치 고유 설정은 `.mpa/config/config.yaml`에 저장한다.
- legacy `config.toml`은 `.mpa/config/config.toml`로 이전하며, 기존 파일이 있으면 덮어쓰지 않는다.
- rollback snapshot 디렉터리는 `.mpa/backups/`를 사용한다.

### 변경 불가 제약

- Runtime deploy는 `.mpa/runtime/`만 교체하며, `.mpa/config/`, `workspace/`, 루트 `docs/`, agent 설정 및 일반 소스를 변경하지 않는다.
- 설치 고유 설정의 기존 값은 덮어쓰지 않는다.
- 배포 변경은 release ZIP·manifest 검증 및 rollback 가능한 backup을 통해서만 적용한다.

### 에이전트 가정

| 가정 | 근거 | 틀렸다면 |
|---|---|---|
| legacy `.mpa-workspace/config.toml`은 공통 workflow Runtime 설정이며 새 release asset에 포함돼야 한다. | 파일 내용은 workflow·routing·gate의 공통 규칙이고, 설치 고유 값이 아니다. | 별도 project override 스키마를 설계한다. |
| `.mpa/config/config.yaml`은 설치 고유 정보 전용이다. | 사용자 결정과 config migration 계약. | 설정 스키마·migration 범위를 확장한다. |

### 결정 대기 항목 (Open Questions)

- 없음

## 실행 계획

### 사전 조사

- `release_manager.py`, `install.py`, `project_config.py`, agent spec, release allowlist와 기존 테스트에서 경로 참조를 전수 조사한다.
- `.mpa/runtime/`, `.mpa/config/`, `workspace/`, `.mpa/backups/`의 소유권과 migration/rollback 순서를 확정한다.

### 구현 단계

- [ ] Runtime asset root와 모든 참조를 `.mpa/runtime/`로 전환하고, legacy `.mpa-workspace/`를 원자적으로 migration한다.
- [ ] 설치 고유 설정을 `.mpa/config/config.yaml`로 전환하며, 기존 `.mpa-project/` 값은 additive·보존 원칙으로 migration한다.
- [ ] legacy `config.toml`과 관리 대상 agent 진입점·hook의 경로 참조를 안전하게 migration한다.
- [ ] deploy/rollback이 Runtime·config migration 상태를 함께 backup·복원하도록 수정한다.
- [ ] 설치·업그레이드 문서에 파일 소유권, 절차, 확인·rollback 방법을 추가한다.
- [ ] 단위 테스트와 release audit을 실행하고 새 Runtime release를 준비한다.

### 예상 조용한 결정

- `.mpa/runtime/`은 release ZIP의 유일한 교체 대상이다.
- `.mpa/config/`은 배포 전 snapshot하고, migration이 명시한 누락값 외에는 변경하지 않는다.
- legacy 폴더는 migration 검증이 성공한 뒤에만 제거하며, 실패하면 backup으로 원복한다.

### 수정 대상 파일

| 파일 경로 | 변경 내용 |
|---|---|
| `release_manager.py` | Runtime/config 경로 migration·backup/rollback 계약 구현 |
| `install.py`, `project_config.py` | 신규 설치 경로와 config 초기화 전환 |
| `agent-specs/` 및 Runtime 참조 파일 | `.mpa/runtime/` 경로 참조 전환 |
| 기존 대상의 `AGENTS.md`·agent hook 설정 | legacy Runtime 경로 참조를 새 경로로 전환 |
| `tests/test_release_manager.py` | legacy/보존/rollback 회귀 테스트 |
| `README.md` | 설치·업그레이드 파일 구조와 소유권 설명 |
| `install.md` | 운영 절차와 점검/rollback 안내 |
| 필요 시 `.mpa-workspace/inject/layer0_update.md` | 업데이트 세션의 확인 항목 정렬 |

### 참고 파일 (수정 없음)

- `project_config.py` — 설치 고유 설정의 additive 초기화 계약
- `map-product-rules/deployment-coordination.md` — Runtime deploy 경계

### 반례

- legacy `config.toml`이 release의 이전 Runtime asset과 다르다 → dry-run에서 충돌로 고지하고 사용자 승인 없이 덮어쓰지 않는다.
- 기존 agent 설정에 사용자 정의 내용이 있다 → `.mpa-workspace`라는 경로 참조만 원자적으로 치환하고 나머지 내용은 보존한다.
- legacy 폴더 이동이나 config migration 중 배포 검증이 실패한다 → Runtime·config·legacy 경로 상태를 backup에서 복원한다.

## 실행 TODO

### 구현·에이전트 검증

- [ ] 보존·초기화·rollback 구현
- [ ] 문서 업데이트
- [ ] 테스트·release audit 통과

### 사용자 결정·승인 필요

- [ ] 요구사항 명세 승인

## 검증 결과

### 검증 체크리스트

- [ ] 정상 경로: 신규 설치가 `.mpa/runtime/`·`.mpa/config/`를 생성하고, legacy 대상이 새 경로로 migration된다.
- [ ] 실패 경로: 배포 검증 실패 시 Runtime·config·legacy 경로가 복원된다.
- [ ] 엣지 케이스: 기존 `.mpa-project/config.yaml`과 `runtime.*` 값이 손실 없이 migration되고, 변경된 legacy `config.toml` 충돌이 사전 고지된다.
- [ ] 경로 검증: 대상 Runtime·config·관리 agent 파일에 legacy 경로가 남지 않는다.

### 완료 시 문서 업데이트 대상

- [ ] `README.md` — 설치된 프로젝트 구조 및 파일 소유권
- [ ] `install.md` — 신규 설치·업그레이드·rollback 절차

## 운영 시 안내 사항

| 영향 대상 | 운영상 달라지는 점 | 사용자 안내 |
|---|---|---|
| 기존 설치본 | upgrade가 legacy 경로를 `.mpa/runtime/`·`.mpa/config/`로 migration | 새 release 적용 전 dry-run 결과와 migration 후보를 확인 |

## 실행 중 변경 기록

| 변경 내용 | 이유 | 명세 영향 |
|---|---|---|
| (구현 중 채움) |  | 없음 / 확인 필요 |
| 상태를 설계 완료로 복구 | 구형 `.mpa-workspace` 대상이 더 이상 없고 승인해시도 현재 요구사항 명세와 불일치한다는 상태 점검 결과. 기존 계획 내용은 보존하고, 재개 시 범위·호환성 정책을 재검토한 뒤 사용자 승인으로 다시 시작한다. | 없음 |

## 명세 변경 이력

| 승인 시각 | 이전 체크섬 | 새 체크섬 | 변경 요약 |
|---|---|---|---|
| 2026-08-21T06:16:09Z | reqspec-v1:6eecb9c2209f9759 | reqspec-v1:bd1ef5424bd10f0e | .mpa 단일 컨테이너 구조로 경로 migration 변경 |
