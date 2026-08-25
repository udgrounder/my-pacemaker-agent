# 1차 독립 구현 검증

## 약점

### [P1] rollback이 승인·rollback 책임자 게이트를 실제로 검사하지 않는다

- 근거: `release_manager.py:1377-1459`의 `rollback()`은 `--approved-by`, `--approval-ref`, `--rollback-owner` 값이 비어 있지 않은지를 검사하지 않는다. 반면 `deploy()`는 `release_manager.py:1246-1247`에서 같은 필드를 명시적으로 검사한다.
- 계약 위반: `map-product-rules/deployment-coordination.md:23-25`와 `map-product-rules/command-contract.md:14`는 rollback에도 승인과 책임자 gate를 요구한다.
- 영향: CLI의 `required=True`는 빈 문자열을 막지 못하므로, 호출자가 `--approved-by '' --approval-ref '' --rollback-owner ''`로 rollback을 실행하고 형식상 receipt까지 남길 수 있다. 승인 traceability가 사라진다.
- 누락 검증: 빈 승인자/승인 참조/rollback 책임자 각각을 거부하는 rollback 단위 테스트가 없다.

### [P1] retention이 “검증된 ZIP backup만”이 아니라 marker만 읽히는 ZIP을 성공 backup으로 세고 삭제 대상을 정한다

- 근거: `release_manager.py:880-902`는 ZIP에서 `backup-metadata.json`을 읽어 `kind`와 `status`만 확인한 뒤 candidate에 넣는다. archive를 안전 해제해 `_validate_backup()`의 asset checksum·Runtime tree를 검증하지 않는다.
- 계약 위반: 계획의 완료 기준(`plan.md:34, 37`)과 운영 계약(`MAP_PRODUCT_RULES.md:24`, `deployment-coordination.md:13, 25`, `command-contract.md:13`)은 무결성이 검증된 성공 ZIP만 retention 대상이라고 정한다.
- 영향: marker는 정상이나 Runtime 파일이 손상·누락된 ZIP도 최신 3개 중 하나로 계산된다. 그 결과 rollback 가능한 오래된 backup을 삭제하고, 실제로는 복구 불가능한 ZIP만 남길 수 있다.
- 누락 검증: `test_runtime_backup_retention_keeps_the_newest_three_zip_archives_only`은 marker-only ZIP을 유효 candidate로 의도적으로 만든다(`tests/test_release_manager.py:477-499`). marker는 정상이고 asset checksum 또는 Runtime tree가 손상된 ZIP을 retention에서 제외하는 테스트가 없다.

### [P2] backup ZIP의 `history/` 내용은 archive에 포함되지만 무결성 checksum에서는 제외되어 rollback 시 검증되지 않은 history가 복원된다

- 근거: `_write_backup_archive()`는 backup 디렉터리의 모든 파일을 ZIP에 기록한다(`release_manager.py:263-275`). 반면 marker checksum은 `asset_map()`으로 만들며, `asset_map()`은 경로 구성 요소에 `history`가 있으면 제외한다(`release_manager.py:148-154`, `970-983`). rollback은 backup Runtime tree 전체를 `copytree()`로 복원한다(`1406-1413`).
- 영향: ZIP 생성 후 `runtime/.mpa/runtime/history/...`가 변조·손상돼도 `_validate_backup_archive()`와 rollback 검증은 통과할 수 있고, 그 파일이 대상 Runtime에 복원된다. 이는 “ZIP 무결성 확인 후 rollback” 계약을 전체 snapshot에는 충족하지 못한다.
- 조용한 결정: Runtime release asset map에서 history를 제외하는 정책을 Runtime backup 전체 snapshot checksum에도 그대로 적용했다. backup의 history를 보존·복원할 필요가 있는지, 필요하다면 checksum에 포함할지를 명시해야 한다.

### [P2] “안전한 임시 해제”에는 ZIP bomb/resource-limit 방어가 없다

- 근거: `materialized_backup()`은 backup ZIP을 `_extract_runtime()`으로 그대로 해제한다(`release_manager.py:341-352`). `_extract_runtime()`은 path traversal·중복명·symlink/type은 검사하지만(`304-338`), 항목 수·압축 해제 총 용량·개별 파일 크기 제한을 두지 않는다.
- 영향: 대상 `.mpa/backups/` 안에 있는 고압축 ZIP을 rollback 대상으로 선택하면 디스크 고갈 또는 과도한 I/O가 발생할 수 있다. archive 검증(retention 보강 시에도 같은 helper 사용)도 같은 위험을 갖는다.
- 누락 검증: 비정상적으로 큰 declared uncompressed size 또는 과도한 entry count를 거부하는 테스트가 없다.

