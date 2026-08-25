# 2차 독립 구현 검증

## 결론

`changelog.md`의 구현·문서 동기화 및 64개 단위 테스트 통과 주장은 대체로 사실이다. 그러나 1차 검증의 승인 gate·retention 무결성·history checksum·ZIP 자원 제한 문제는 그대로 남아 있으며, 성공 ZIP을 만든 뒤 후속 receipt/history 기록이 실패하는 경우 이번 시도의 backup 자체가 사라지는 추가 결함을 확인했다. 따라서 현재 상태는 테스트 진행 가능이 아니라 수정 필요다.

## 1차 검증 대조

- 확인됨 — rollback은 `approved_by`·`approval_ref`·`rollback_owner`의 비공백 값을 검사하지 않는다. `deploy()`만 `release_manager.py:1246-1247`에서 검사하고 `rollback()`은 receipt에 그대로 기록한다(`release_manager.py:1377-1428`). 1차의 [P1]은 유효하다.
- 확인됨 — retention은 ZIP의 marker만 읽는다(`release_manager.py:880-902`). `_validate_backup_archive()`로 asset checksum과 Runtime tree를 확인하지 않으므로, 1차의 [P1]은 유효하다.
- 확인됨 — archive 작성은 `history/`를 포함하지만(`release_manager.py:263-275`), `asset_map()`은 `IGNORED_RUNTIME_NAMES`에 든 history를 checksum에서 제외한다(`release_manager.py:148-154`, `970-1000`). 1차의 [P2]는 유효하다.
- 확인됨 — `materialized_backup()`은 `_extract_runtime()`을 사용하며, 이 해제기는 경로·중복·파일 형식은 검사하지만 entry 수·해제 총량·개별 파일 크기 제한은 없다(`release_manager.py:304-352`). 1차의 [P2]는 유효하다.

## 추가 발견

### [P1] archive publish 뒤 receipt/history 기록 실패 시 이번 backup을 삭제해 실패 backup 보존 계약을 깨뜨린다

- 근거: deploy는 marker 작성, ZIP 검증·publish, 원본 디렉터리 삭제를 `release_manager.py:1291-1294`에서 receipt/history 기록보다 먼저 수행한다. 이후 `write_safe_receipt()` 등이 실패하면 예외 처리에서 published ZIP을 `unlink()`한다(`1333-1338`). 이미 `backup_directory`는 `rmtree()`됐으므로 해당 시도의 디렉터리 snapshot도 남지 않는다.
- 계약 위반: `MAP_PRODUCT_RULES.md`와 `workspace/memory/shared/architecture.md`는 실패 backup을 보존하고, `plan.md`의 실패 경로는 오류 시 디렉터리형 backup으로 복구·보존한다는 방향을 정한다.
- 영향: receipt I/O처럼 Runtime 교체 뒤 발생하는 실패에서 Runtime은 `previous`로 복원될 수 있지만, 진단·재시도·명시 rollback에 쓸 이번 backup은 사라진다. 이는 “성공 ZIP만 retention”과 별개인 실패 snapshot 보존을 만족하지 못한다.
- 누락 검증: `test_deploy_collection_failure_restores_runtime_and_issue`는 receipt write 실패를 만들지만 backup의 ZIP 또는 디렉터리 보존을 확인하지 않는다.

### [P2] 실행 계획의 수정 대상·실행 중 변경 기록이 실제 문서 변경 범위를 완전히 추적하지 않는다

- 근거: `plan.md`의 수정 대상은 `release_manager.py`, 테스트, `deployment-coordination.md`, `architecture.md` 네 파일만 열거한다. 실제 diff에는 추가로 `MAP_PRODUCT_RULES.md`, `map-product-rules/command-contract.md`, `README.md`가 포함된다.
- changelog 대조: “배포 규칙·명령 계약·README·아키텍처 메모리 동기화”라는 `changelog.md`의 서술은 실제 변경과 일치한다. 다만 plan의 Step 4·수정 대상·실행 중 변경 기록에는 이 확장된 문서 범위와 이유가 남아 있지 않다.
- 명세 이력: 요구사항 명세 자체는 바뀌지 않아 `명세 변경 이력`이 비어 있는 것은 적절하다. 그러나 문서 범위 확장은 명세 밖 실행 기록 보완이므로 `실행 중 변경 기록`에 파일 범위와 이유를 남겨야 한다.

## changelog 및 검증 대조

- 일치: `release_manager.py`는 성공 후 검증된 ZIP publish, 원본 디렉터리 제거, ZIP·디렉터리 rollback 분기를 실제로 구현했다.
- 일치: `tests/test_release_manager.py`에는 성공 ZIP, archive 실패 복구, ZIP rollback, legacy directory rollback, ZIP retention 테스트가 있다.
- 일치: 규칙·명령 계약·README·architecture의 ZIP backup 서술도 실제로 갱신됐다. `workspace/memory/shared/contracts.md`는 존재하지 않아 별도 계약 메모리 갱신 대상은 없다.
- 누락: changelog는 위의 승인 gate, retention의 marker-only 판정, history checksum 제외, ZIP 자원 제한, receipt 실패 뒤 backup 삭제 위험을 기록하지 않는다. 구현 완료 주장 전에 수정 또는 알려진 제한으로 분류돼야 한다.
- 재실행 결과: `python3 -m unittest tests.test_release_manager -v`는 64 tests passed, `git diff --check`는 passed였다. 테스트 통과는 위의 미검증 반례를 해소하지 않는다.

## 분류

- 즉시 수정 필요: 3건 — rollback 승인 gate, retention 전체 무결성 검증, receipt/history 실패 후 backup 보존.
- 주의 필요: 3건 — history checksum 범위, ZIP resource-limit, plan 실행 기록 동기화.
- 조용한 결정: 2건 — Runtime history를 backup archive에는 보존하면서 checksum에서는 제외, 계획에 없던 운영 문서 세 곳의 동기화.
- 틀린 에이전트 가정: 0건 — plan의 두 명시 가정은 코드·요청 범위와 충돌하지 않았다. 다만 “검증된 ZIP만 retention”이라는 구현 가정은 marker 검증만으로는 성립하지 않는다.
