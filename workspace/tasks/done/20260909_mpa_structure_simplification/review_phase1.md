## 검토 결과

문서 로딩 분리와 leaf 추출의 기본 구조는 계획의 방향과 맞는다. 다만 공개 import 호환을 주장하는 새 `mpa_ops` 의존성이 실제로 독립 spec loader에서 성립하는지 검증되지 않았고, ZIP·이슈 facade 및 deploy/rollback 실패 복구의 새 경계에 대한 회귀도 충분하지 않다.

## ✅ 정합성 확인

- `agent_rules.md`의 상세 파일 로드 표는 승인 기록과 완료 처리의 즉시 로드 트리거를 명시하고, 각각 `agent_rules_detail.md`의 정본 섹션으로 연결한다. `layer1_design.md`와 `layer1_implement.md`도 승인 기록 detail을 직접 지시한다. 이는 D2 및 minor가 design을 선행하지 않아야 한다는 D1 제약에 부합한다.
- `release_manager.py`는 ZIP 6개와 이슈 형식 5개 기능을 facade로 남기고 leaf module이 facade를 역방향 import하지 않는다. Runtime ZIP 생성은 계속 `RUNTIME_DIST`만 입력으로 사용하므로 `mpa_ops/`가 Runtime asset에 포함될 경로는 없다.
- deploy의 exception 경로는 issue 이동, Runtime, config, 임시 replacement, receipt/history를 각각 복구하려 시도하며, rollback도 별도의 복구 경로를 유지한다. 추출이 조정 함수 바깥으로 이동하지 않아 트랜잭션 순서가 구조적으로 분산되지는 않았다.

## ⚠️ 주의 필요

1. **11개 정책 도달성 및 source/dist parity의 자동 검증이 부족하다.**
   - 근거: `tests/test_structure_loading.py:19-42`는 두 Runtime 사본에 특정 문자열이 있는지만 검사하고, minor의 template 직접 경로 검사는 source 한 곳만 검사한다. 계획의 D1-D3은 대표 요청별 도달성 11개와 source/dist parity를 요구한다.
   - 권장 조치: 요청 유형별로 “시작 문서 → 트리거 → 정본 섹션”을 표 기반 테스트로 고정하고, source와 dist의 해당 파일 내용 또는 asset map이 동일한지도 별도 assertion으로 확인한다. 최소한 major 승인, minor 실행/계획만 요청, 명세 갱신, 완료 승인, 재개, 비평, 검증을 각각 포함한다.

2. **11개 facade 중 patch 가능성이 두 개만 검증된다.**
   - 근거: `tests/test_release_manager_compatibility.py:41-65`는 `_validate_zip_member`와 `_parse_issue_candidate`만 patch한다. 반면 실제 facade는 `_zip_runtime`, `_write_backup_archive`, `_zip_entries`, `_archive_current_release`, `_extract_runtime`, `_candidate_metadata_is_complete`, 두 normalize 함수, `_metadata_identity`까지 남아 있다 (`release_manager.py:260-288`, `1228-1261`, `1388-1389`).
   - 권장 조치: 추출 대상별 호출자가 release_manager facade를 통해 dispatch되는지 확인하는 table-driven patch 회귀를 추가한다. 특히 prepare-release의 `_zip_runtime`, backup/legacy migration의 `_write_backup_archive`, preflight의 completeness facade, issue identity/normalization facade를 포함한다.

3. **새 ZIP leaf에서 발생하는 deploy/rollback 실패 주입이 복구 결과까지 검증되지 않는다.**
   - 근거: compatibility test의 archive 실패는 `_extract_runtime` 단독 호출의 staging 정리에 한정된다 (`tests/test_release_manager_compatibility.py:41-53`). deploy는 `_extract_runtime` 뒤 Runtime 교체·config migration·issue 이동·backup archive를 순서대로 수행하고 (`release_manager.py:1623-1654`), rollback도 같은 facade로 backup을 materialize한다. 계획은 deploy와 rollback의 실패 복구를 분리해 검증하도록 요구한다.
   - 권장 조치: facade를 patch해 (a) package extraction 실패, (b) backup archive 쓰기/검증 실패를 deploy 및 rollback 각각의 실제 transaction에서 주입하고, 기존 Runtime·config·issue 원본·failed receipt/history 상태를 명시적으로 검증한다.

4. **source-only 경계는 구현으로는 유지되지만 release artifact 수준의 회귀 검사가 없다.**
   - 근거: `release_manager.py:608`은 Runtime dist만 ZIP으로 만든다. 그러나 신규 `mpa_ops/`가 source-only라는 요구를 자동으로 보증하는 테스트는 없고, `tests/test_structure_loading.py`도 문서만 읽는다.
   - 권장 조치: 실제 prepare-release fixture의 package member와 manifest asset map에 `mpa_ops/`, source `workspace/`, map-product 파일이 없음을 검사한다. 이 검사는 source-only 원칙이 향후 sync/packaging 변경으로 깨지는 것을 막는다.

## 🚨 즉시 수정 필요

1. **“repository 밖 legacy spec loader 호환” 테스트가 실제로는 그 조건을 검증하지 않아, 공개 import 호환 요구가 미입증 상태다.**
   - 근거: `release_manager.py:23`은 새 절대 import `from mpa_ops import archive_io, issue_format`를 수행한다. `tests/test_release_manager_compatibility.py:26-29`의 `load_release_manager()`는 테스트 프로세스의 repository-root import path를 그대로 사용한다. `TemporaryDirectory`로 cwd를 바꾸는 부분은 그 뒤 CLI subprocess에만 적용된다 (`:30-37`). `importlib.util.spec_from_file_location()`은 module 파일의 parent를 `sys.path`에 자동 추가하지 않으므로, repository root가 `sys.path`에 없는 외부 spec loader에서는 `mpa_ops` import가 실패하거나 동명 설치 package를 잘못 선택할 수 있다.
   - 권장 조치: root가 `sys.path`에 없는 별도 subprocess에서 `spec_from_file_location`으로 `release_manager.py`를 load하는 회귀를 추가하고 통과시킨다. 그 결과에 맞춰 source package를 안정적으로 해석하는 호환 방식을 설계한다. 이때 계획의 금지사항인 `sys.modules` 교체·leaf의 facade 역방향 import는 사용하지 말고, 기존 spec-loader 공개 계약을 보존해야 한다.

## 📝 조용한 결정 목록

- 새 `mpa_ops` package가 source root의 Python import path에 존재한다는 전제를 도입했다. 이 전제는 기존 단일 `release_manager.py`에는 없었고, 독립 loader 호환에 직접 영향을 준다. 위 즉시 수정 항목을 해결하면서 문서와 compatibility contract에 명시해야 한다.
- facade를 전부 유지하되 compatibility suite는 두 seam만 고정했다. 어떤 facade가 외부/테스트 patch 계약인지와 나머지가 단순 내부 이름인지 경계가 문서화되어 있지 않다. 유지 대상 목록을 `docs/mpa-internal-structure.md` 또는 테스트에 명시하는 것이 필요하다.
- 문서 구조 테스트의 byte 기준은 baseline보다 작다는 단일 조건이다 (`tests/test_structure_loading.py:9,40-42`). 계획이 요구한 “바이트 감소와 요청별 참조량의 분리 보고” 중 후자는 자동 근거가 없다. 효과를 주장하지 않는다는 문구는 유지하되, 비교 대상과 산출 위치를 검증 기록에 남겨야 한다.

## 🔍 에이전트 가정 검증

- **“CLI 입구를 남기고 leaf 책임을 분리할 수 있다”**: CLI와 facade 이름은 남아 있고, CLI help 외부 실행 검사도 있다. 그러나 spec loader 경로는 새 package import 때문에 검증 실패 가능성이 있어 가정은 현재 **미검증**이다.
- **“작은 추출 단위가 안전하다”**: deploy/rollback 조정과 issue 이동 transaction은 `release_manager.py`에 남아 있어 구조상 타당하다. 하지만 새 leaf 예외의 transaction-level recovery 검증이 없어 실패 보존 가정은 **부분 검증**이다.
- **“로드 비용은 실제 참조 경로로 평가한다”**: 항상 로드되는 core의 크기 감소와 detail trigger는 확인할 수 있다. 현재 테스트는 문자열 존재 수준이므로 대표 요청별 실제 도달 경로와 source/dist 동일성은 **미검증**이다.
