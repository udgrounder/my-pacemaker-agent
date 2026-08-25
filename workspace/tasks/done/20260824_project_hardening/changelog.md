# 태스크 내역서: 20260824_project_hardening

**작업일:** 2026-08-24
**계획서:** `plan.md`

---

## 변경 파일 목록

| 파일 경로 | 변경 유형 | 설명 |
|---------|---------|------|
| `.claude/agents/mpa_pacemaker.md`, `.codex/agents/mpa_pacemaker.toml`, `.agents/rules/mpa_pacemaker.md` | 수정 | source native agent rule의 Runtime import 경로를 `.mpa/runtime`으로 통일 |
| `.claude/settings.json`, `.codex/hooks.json` | 수정 | source hook 명령과 Claude 권한 경로를 현재 Runtime 위치로 수정 |
| `agent-specs/*/files/` | 수정 | clean install이 복사하는 Claude·Codex·Antigravity native rule을 현재 Runtime 경로로 수정 |
| `install.py` | 수정 | 현재 hook 명령을 인식하는 idempotency marker로 변경 |
| `tests/test_install.py` | 수정 | clean-install native wiring 및 current marker 회귀 테스트 추가 |
| `project_config.py`, `release_manager.py` | 수정 | config·Runtime·backup·필수 설치 경로의 symlink 및 package 특수 파일 방어 |
| `tests/test_release_manager.py` | 수정 | Runtime parent·backup symlink와 package 특수 파일 거부 회귀 테스트 추가 |
| `release_manager.py` | 수정 | release package 표준 preflight, active source/package content policy, 모든 Python hook 정적 검사, 민감 기록 최소화 추가 |
| `tests/test_release_manager.py` | 수정 | preflight 호출, retired 실행 참조, metadata 절대 경로, 추가 hook 문법 오류 회귀 테스트 추가 |
| `release_manager.py` | 수정 | 직전 유효 bundle과 `.mpa-version` 외 asset map이 같은 package를 기본 거부하고, 명시 override 및 실패 원복 추가 |
| `tests/test_release_manager.py` | 수정 | version-only 거부·source/dist 원복·명시 override 회귀 테스트 추가 |
| `release_manager.py`, `tests/test_release_manager.py` | 수정 | deployment dry-run·receipt·history의 절대경로 노출 제거와 operator 입력 정제 회귀 테스트 추가 |
| `.gitignore`, `release_manager.py`, `tests/test_release_manager.py` | 수정 | Git 비추적 로컬 target 등록부와 target 생략 rollback·stale fingerprint 거부 추가 |
| `README.md`, `install.md`, `map-product-rules/release-preparation.md` | 수정 | package 생성 시 표준 preflight와 추가 validation의 운영 계약 반영 |
| `workspace/releases/20260825031915-e37e66e1/` | 추가 | 사용자 요청으로 생성한 immutable Runtime release bundle |

---

## 상세 변경 내역

### agent wiring과 hook 등록

- **대상:** source 설정, agent spec, `install.py`
- **변경 유형:** 수정
- **내역:** retired `.mpa-workspace` 참조를 활성 `.mpa/runtime` 경로로 바꾸고, 현재 hook 블록을 중복 등록하지 않도록 marker를 맞췄다.

### clean-install 회귀 검증

- **대상:** `tests/test_install.py`
- **변경 유형:** 추가
- **내역:** Claude·Codex·Antigravity clean install에서 root entrypoint·native rule·자동 hook이 현재 Runtime을 참조하고 hook 파일이 존재하는지 검증한다.

### 경로·archive 경계

- **대상:** `project_config.py`, `release_manager.py`
- **변경 유형:** 수정
- **내역:** Runtime·backup 및 install이 생성하는 사용자 루트의 symlink를 사전 거부하고, config path의 symlink는 외부 파일을 읽지 않는 warning으로 처리한다. ZIP extraction은 symlink·traversal뿐 아니라 특수 파일도 거부한다.

### release package preflight와 content policy

- **대상:** `release_manager.py`, release 문서, 회귀 테스트
- **변경 유형:** 수정
- **내역:** `prepare-release`는 source 동기화 후 전체 단위 테스트, runtime/dist parity, 기존 bundle audit을 표준 preflight로 실행한다. 새 source/package는 retired `.mpa-workspace` 실행 참조, 민감 경로·credential, 모든 Python hook 문법을 검사하며, 기존 immutable bundle은 구조·무결성·hook 문법 audit만 유지한다.

### Runtime release 생성

- **대상:** `workspace/releases/20260825031915-e37e66e1/`
- **변경 유형:** 추가
- **내역:** 사용자의 명시 요청으로 standard preflight와 추가 validation을 통과한 package·manifest·note·release receipt immutable bundle을 생성했다.

### version-only release 방지

- **대상:** `release_manager.py`, release 운영 문서, 회귀 테스트
- **변경 유형:** 수정
- **내역:** 직전 유효 release와 `.mpa-version`을 제외한 Runtime asset map이 같으면 artifact 생성 전에 거부한다. 의도적인 재발행만 `--allow-version-only`로 허용하며, 거부 또는 검증 실패 뒤 source와 dist의 Runtime version을 함께 원복한다.

### deployment receipt 경로 정제

- **대상:** `release_manager.py`, deployment 운영 문서, 회귀 테스트
- **변경 유형:** 수정
- **내역:** dry-run은 대상 절대경로 대신 fingerprint로 동일성을 재검증하고, deploy·rollback success/failure receipt 및 target history는 operator 입력의 credential·machine path를 정제해 기록한다. 기존 감사 이력은 재작성하지 않는다.

### 로컬 rollback 대상 등록부

- **대상:** `.gitignore`, `release_manager.py`, deployment 운영 문서, 회귀 테스트
- **변경 유형:** 수정
- **내역:** dry-run이 Git 비추적 `workspace/.local/deployment-targets/<target-ref>.json`에만 target 절대경로와 fingerprint를 저장한다. rollback은 `--target`이 없으면 이 등록부를 사용하고, stale fingerprint면 중단한다.

### deployment receipt 로컬 보관

- **대상:** `release_manager.py`, deployment 운영 문서
- **변경 유형:** 수정
- **내역:** 새 dry-run·deploy·rollback receipt는 Git 비추적 `workspace/.local/receipts/deployments/`에 보관한다.

- **적용:** 이번 `mpa-test4`에서 생성한 untracked receipt 3개를 `workspace/.local/receipts/deployments/mpa-test4/`로 이동했다.

### 기존 tracked deployment receipt 정리

- **대상:** `workspace/receipts/deployments/`
- **변경 유형:** 사용자 승인 이력 정리
- **내역:** 실제 운영 대상으로 검증된 `campingtalk-proj`의 최신 dry-run·deploy receipt 두 개만 Git 비추적 로컬 보관소로 이관했다. dry-run의 대상 절대경로는 target fingerprint로 치환하고 deploy receipt의 내부 참조를 새 위치로 보정했다. 이전 tracked deployment receipt는 제거했으며, legacy release·migration 감사 기록은 유지했다.

---

## 요구사항 명세 대비 변경 사항

| 변경 | 이유 | 명세 영향 | 보고 |
|---|---|---|---|
| current hook marker 회귀 테스트 추가 | 현재 `.mpa/runtime` hook이 이미 등록됐을 때의 중복 등록을 막기 위함 | 없음 | 1단계 완료 보고에 포함 |
| backup·config·package 파일 유형 경계 회귀 테스트 추가 | deploy/rollback이 target root 밖을 읽거나 쓰지 않게 하기 위함 | 없음 | 최소 preflight 완료 보고에 포함 |
| release package 표준 preflight와 content policy | 상시 CI 없이 package 생성 시점에 회귀·parity·audit을 강제하기 위함 | 없음 | release audit 단계 완료 보고에 포함 |
| version-only package 기본 거부와 명시 override | source 전용 release 도구 변경을 Runtime 배포 변경으로 오인한 불필요한 package 생성을 막기 위함 | 사용자 요청 반영 | release 생성 후 발견사항 보완에 포함 |
| deployment receipt의 로컬 경로 노출 제거 | 실제 배포 후 dry-run과 approval reference가 대상 절대경로를 기록한 것을 확인 | 기존 receipt 민감정보 최소화 범위의 보완 | 배포 후 발견사항 보완에 포함 |
| 로컬 target 등록부 | rollback은 대상 위치를 필요로 하지만 공유 receipt에 절대경로를 남기면 안 됨 | 사용자 요청 반영 | 배포 후 발견사항 보완에 포함 |
| tracked deployment receipt 정리 | 과거 이력 제거와 실제 운영 대상의 최신 기록 보정을 사용자가 승인 | 사용자 요청 반영 | 현재 보완에 포함 |

---

## 검증 포인트

- [x] 정상 경로 확인: Claude·Codex·Antigravity clean install이 현재 Runtime을 참조한다.
- [x] 실패 경로 확인: retired path가 source 설정·agent spec·install.py에 남지 않는다.
- [x] 실패 경로 확인: Runtime parent·backup·config symlink 및 ZIP 특수 파일이 변경 전 거부된다.
- [x] plan.md 완료 기준 충족 여부: Runtime wiring과 최소 boundary preflight 완료. 전체 계획은 계속 진행 중.
- [x] 독립 검증 후속: config 상위 경로·deploy/rollback symlink·ZIP symlink/type mismatch 회귀 테스트를 보강했다. — install 17개, release manager 51개 통과
- [x] release package 검증: 표준 preflight, retired 실행 참조·절대 경로·전체 hook 문법 거부 회귀를 추가했다. — release manager 55개, 전체 105개, release audit 20 bundles 통과
- [x] Runtime release 생성: `20260825031915-e37e66e1` — 새 bundle 포함 release audit 21개 통과
- [x] version-only release 검증: 기본 거부 뒤 source/dist asset map 원복, `--allow-version-only` 명시 시 생성 — release manager 58개·전체 108개 통과
- [x] deployment receipt 경로 정제: dry-run target 제거·fingerprint 재검증·operator path 정제 회귀 테스트 통과
- [x] 로컬 target 등록부: target 생략 rollback과 stale fingerprint 거부 회귀 테스트 통과
