# 후속 독립 검토

## 결론

이전 즉시 수정 필요 항목 1(rollback 승인 메타데이터)과 3(receipt/history 기록 실패 후 ZIP 삭제)은 해결됐다. 항목 2(retention의 ZIP 전체 무결성 재검증)는 사용자 결정에 따라 이번 범위에서 제외됐으며, 계획서에 marker 기반 retention을 유지한다는 내용으로 명확히 기록됐다. 이 결정과 남은 P2 주의 사항을 수용하면 테스트 진행 가능하다.

## 항목 1 — rollback 승인 메타데이터

- 해결됨: `rollback()`은 Runtime·backup을 변경하기 전에 `approved_by`, `approval_ref`, `rollback_owner` 모두의 비공백 값을 검사하고 누락 시 `ValueError`를 낸다(`release_manager.py:1396-1400`).
- 회귀 검증: `test_rollback_requires_approval_metadata`가 세 필드를 각각 공백으로 넣어 모두 거부되는지 확인한다(`tests/test_release_manager.py:582-602`).

## 항목 3 — receipt/history 기록 실패 뒤 ZIP 보존

- 해결됨: 예외 정리 경로에서 published `backup_archive`를 삭제하던 코드가 제거됐다. ZIP publish와 원본 디렉터리 삭제 후 receipt 또는 history 기록이 실패해도 ZIP은 `.mpa/backups/`에 남고, Runtime은 이전 `previous` tree로 복원된다(`release_manager.py:1291-1294`, `1320-1345`).
- 회귀 검증: `test_deployment_receipt_failure_preserves_published_zip_backup`은 applied deployment receipt 쓰기를 실패시킨 뒤 기존 Runtime 복원 및 ZIP backup 보존을 확인한다(`tests/test_release_manager.py:538-559`). history receipt 실패도 같은 예외 경로를 사용하므로 ZIP 보존 동작은 동일하다.

## 항목 2 — retention 전체 무결성 검증 제외 기록

- 명확히 기록됨: `plan.md`의 `실행 중 변경 기록`에 “ZIP retention의 전체 무결성 검증은 이번 범위에서 제외 / 사용자 결정: marker 기반 retention은 유지 / 명세 영향: 없음”이 추가됐다.
- 현재 동작과 일치: `prune_runtime_backups()`는 ZIP 내부 marker의 `kind`·`status`만 확인해 retention 후보로 사용한다(`release_manager.py:880-902`). 즉, 이 결정은 구현 상태를 숨기지 않고 명시한다.
- 범위 판단: archive publish 시점의 ZIP은 `_validate_backup_archive()`로 전체 검증한 뒤 생성된다. 다만 보관 후 외부 손상을 retention이 재검증하지 않는다는 기존 위험은 사용자 수용 제한으로 남는다.

## 남은 주의 사항

- `history/`는 backup archive에 포함되나 checksum에서는 제외된다.
- ZIP 임시 해제에는 entry 수·해제 용량 제한이 없다.

## 재검증

- `python3 -m unittest tests.test_release_manager -v` — 66 tests passed
- `git diff --check` — passed
