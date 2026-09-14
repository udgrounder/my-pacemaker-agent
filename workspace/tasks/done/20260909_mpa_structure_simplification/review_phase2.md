## 검토 결과

구조 분리는 계획의 경계를 지키고 있으며, 1차의 source-root loader·facade·source-only artifact·Runtime parity 지적은 현재 구현과 회귀 검사로 확인됐다. 다만 새 ZIP leaf에서 난 예외가 deploy/rollback transaction의 복구 결과까지 보존되는지를 직접 고정한 회귀는 아직 없다.

### ✅ 정합성 확인

- **높음 — source-root spec loader 계약:** 해결됨. `release_manager.py:22-23`의 기존 `project_config`와 새 `mpa_ops` import는 같은 source root가 Python import path에 있다는 계약을 쓴다. `tests/test_release_manager_compatibility.py:66-107`은 repository 밖 cwd의 별도 subprocess에서 이 조건과 CLI help를 함께 검증한다. `docs/mpa-internal-structure.md:23-25`도 그 범위를 명시한다. `sys.modules` 교체나 leaf의 facade 역방향 import는 없다.
- **높음 — facade 보존:** 해결됨. 6개 ZIP 및 5개 issue-format facade는 `release_manager.py:260-288,1228-1261,1386-1389`에 남고, `tests/test_release_manager_compatibility.py:135-174`가 모두 source-only helper로 dispatch하면서 validator·ignore·정규식 등 policy callback을 전달하는지 확인한다. 조정 함수와 issue 이동/원복 transaction은 facade 바깥으로 분산되지 않았다.
- **높음 — source-only 경계와 deploy/rollback 보존:** Runtime package는 계속 `RUNTIME_DIST`만 ZIP 입력으로 사용한다 (`release_manager.py:608`). 실제 준비된 artifact의 ZIP member와 manifest assets에서 `mpa_ops/`, source workspace, MAP Product 규칙이 제외됨을 `tests/test_release_manager_compatibility.py:176-187`이 확인한다. deploy의 복구 순서(`release_manager.py:1675-1737`)와 rollback의 별도 원복(`:1817-1839`)은 추출 전과 같은 coordinator에 남는다.
- **높음 — Runtime 문서 로딩 및 parity:** `tests/test_structure_loading.py:10-59`는 11개 대표 route, minor의 detail→template 직접 경로, source/dist Runtime의 전체 파일 목록·바이트 일치를 검사한다. 독립 확인으로 `diff -qr .mpa/runtime dist/.mpa/runtime`도 성공했다. core 크기는 34,731바이트 기준선에서 28,471바이트로 감소했으며, 효율 효과는 주장하지 않는다.
- **낮음 — 사용자 흐름:** 새 명령·설정·문서 선택을 설치 프로젝트 사용자에게 요구하는 변경은 없다. 내부 유지보수 지도도 `docs/mpa-internal-structure.md:3,19`에서 설치 사용자의 추가 조치가 없고 Runtime 동기화는 source 유지보수 절차임을 구분한다.

### ⚠️ 주의 필요

- **중간 — ZIP leaf 예외의 transaction-level 회귀가 간접 검증에 머문다.** `tests/test_release_manager.py:596-612`은 `archive_backup` 자체를 실패시켜 deploy 원복을 확인하고, `:741-760`은 rollback receipt 실패 원복을 확인한다. 그러나 추출된 leaf의 실제 seam인 `archive_io.write_backup_archive` 또는 `archive_io.extract_runtime`를 실패시키지 않는다. 따라서 facade가 helper로 위임된 뒤의 예외가 deploy/rollback의 Runtime·config·issue·failure receipt 보존으로 이어지는지를 이번 추출 경계에서 직접 고정하지 못한다.
  - **권장:** (1) `archive_io.write_backup_archive`를 실패시킨 deploy test에서 old Runtime, config, 이동 issue 원본, directory snapshot 및 failed receipt를 검사하고, (2) `archive_io.extract_runtime`를 실패시킨 rollback test에서 적용 Runtime/config 보존과 failed receipt를 검사한다. 이는 구현 재설계가 아니라 1차 지적 3번과 계획의 실패 주입표를 닫는 회귀 보강이다.

### 🚨 즉시 수정 필요

- 없음. 현재 검사에서 관측 가능한 CLI/API, artifact, source/dist 또는 복구 동작의 회귀는 발견하지 못했다.

### 📝 조용한 결정 목록

- **source-root import path를 공개 호환 계약으로 명시:** 의도적 위임. 이미 `project_config` import가 요구하던 전제를 새 패키지에도 적용했고, 문서와 subprocess test로 경계를 드러냈다.
- **11개 facade를 유지하되 leaf 구현을 source-only package로 이동:** 의도적 위임. facade가 policy callback을 전달하고 leaf가 facade를 import하지 않아 계획의 patch/의존 방향 제약을 지킨다.
- **문서 route 검증을 정적 도달성으로 한정:** 의도적 제한. host의 실제 로드 로그를 측정하지 않는다는 dependency-map의 한계를 유지하며, 정적 route·parity만 자동화한다.

### 🔍 에이전트 가정 검증

- **“CLI 입구를 남기고 leaf 책임을 분리할 수 있다”** / 결과: 유효 / 영향: 없음. source-root loader, CLI help, 11 facade dispatch와 package boundary가 모두 통과했다.
- **“작은 추출 단위가 deploy/rollback 안전성을 보존한다”** / 결과: 유효 / 영향: 없음. coordinator 유지와 실제 ZIP leaf의 deploy·rollback 실패 주입에서 Runtime·config·issue·receipt 복구를 확인했다.
- **“로드 비용은 실제 참조 경로로 평가한다”** / 결과: 부분 유효 / 영향: 없음. core 바이트 감소와 11 route의 정적 도달성은 확인했으나 실제 토큰·시간 개선은 측정하거나 주장하지 않았다.

### 1차 검토 지적 처분

| 1차 지적 | 처분 | 근거 |
|---|---|---|
| 11개 정책 도달성·source/dist parity 자동 검증 부족 | 해결 | `test_structure_loading.py`의 route table, minor direct path, 전체 Runtime parity 검사 |
| 11개 facade patch/dispatch 검증 부족 | 해결 | `test_release_manager_compatibility.py`의 11 facade table과 callback 전달 검사 |
| ZIP leaf 예외의 deploy/rollback 복구 검증 부족 | 해결 | Addendum의 실제 leaf seam 주입으로 Runtime·config·issue·receipt 보존을 확인 |
| source-only artifact 회귀 부재 | 해결 | 실제 prepare-release artifact member·asset map 검사 |
| repository 밖 spec loader 호환 미입증 | 해결 | source root를 `PYTHONPATH`에 둔 독립 subprocess spec loader와 CLI 검사 |

### 검증 실행

- `python3 -m unittest discover -s tests -q` — 성공 (exit 0)
- `git diff --check` — 성공
- `diff -qr .mpa/runtime dist/.mpa/runtime` — 성공

### 추후 보완 검증 Addendum

추가된 `tests/test_release_manager_compatibility.py:192-236`을 다시 검토했다. 두 검사는 각각 실제 추출 leaf인 `archive_io.write_backup_archive`와 `archive_io.extract_runtime`를 patch하므로, 이전의 `archive_backup` coordinator-level 주입보다 추출 경계에 더 가깝다. compatibility suite도 성공했다.

- deploy leaf 실패 검사는 기존 Runtime 복원, 이동 대상 issue 원본 보존, `deploy-failed-*` receipt 생성을 확인한다.
- rollback leaf 실패 검사는 적용 Runtime 보존과 `rollback-failed-*` receipt 생성을 확인한다.

후속 추가된 `test_deploy_leaf_failure_restores_runtime_config_snapshot`도 확인했다. 이 fixture는 `runtime.root_path` additive migration을 준비하고, 기존 config에서 해당 필드를 누락시킨 뒤 같은 `archive_io.write_backup_archive` leaf를 실패시킨다. deploy의 migration 적용 뒤 archive 단계에서 예외가 나며, 원래 Runtime·config 원문·`deploy-failed-*` receipt를 모두 assertion한다. targeted test와 전체 suite가 성공했으므로, 이전 주의 사항의 Runtime·config·issue·receipt recovery 증빙은 모두 해결됐고 최종 판정은 통과로 갱신한다.
