# 1차 구현 검증

## 판정

**수정 요청.** 코드의 현재 CLI 계약은 통과했지만, source 운영 문서에 새 필수 인자를 누락한 실행 불가 예시가 남아 있다.

## 확인 범위·순서

- changelog를 읽기 전에 `plan.md`, 변경 diff, `release_manager.py`, tests 및 운영 문서를 독립적으로 대조했다.
- 그 뒤 `changelog.md`의 주장과 실제 변경을 비교했다.
- 소스 파일은 변경하지 않았다.

## 발견 사항

| 우선순위 | 위치 | 근거 | 영향 / 필요한 수정 |
|---|---|---|---|
| P1 | `install.md:149` | 상단 “Runtime 업데이트” 예시는 `deploy`에 `--manifest`, `--target`, `--target-ref`, `--verified-by`만 전달한다. 현재 parser는 `--dry-run`, `--approved-by`, `--approval-ref`, `--operator`를 모두 필수로 요구한다 (`release_manager.py:1871-1873`). | 사용자가 이 source 운영 문서 예시를 그대로 실행하면 argparse가 필수 인자 누락으로 중단한다. 이 작업의 문서 동기화 완료 기준에도 맞지 않는다. 예시를 완전한 현재 deploy 명령으로 갱신하거나, 상세 절차의 완전한 예시를 명시적으로 참조하도록 바꿔야 한다. 특히 새 `--operator`를 포함해야 한다. |
| P2 | `tests/test_release_manager.py:129` | 새 parser 계약 테스트는 `deploy --help` 하나만 검사한다. 실제 변경 범위인 `rollback`, `history-cleanup`, `migrate-runtime-backups`는 `--rollback-owner` 미노출 및 `--operator` 노출을 자동 회귀 테스트하지 않는다. | 현재 수동 help 점검에서는 네 명령 모두 올바른 인자를 보였지만, 향후 한 parser에 옛 인자가 되돌아와도 테스트가 잡지 못한다. 네 명령을 표 형태/parameterized CLI 테스트로 함께 검증해야 한다. |

## 구현·계약 확인

- `release_manager.py`의 deploy·rollback·history cleanup·backup migration parser, 필수값 검증, 성공/실패 기록에서 `rollback_owner` 참조가 제거됐고 `operator`가 사용된다.
- deploy/rollback의 성공 및 실패 receipt 작성 경로는 `operator`를 포함하며 `write_safe_receipt`로 정제된다. 승인자·승인 기록·dry-run/backup 검증도 유지된다.
- `map-product-rules/command-contract.md`, `deployment-coordination.md`, README, guidebook 및 architecture 스냅샷은 실행자/검증자/승인자 역할을 반영한다. 다만 위 `install.md` 예시 누락은 별도 수정이 필요하다.
- 계획·changelog의 “Runtime source/dist 변경 대상 없음” 주장은 검색 결과와 일치했다. `.mpa/runtime/`와 `dist/.mpa/runtime/`에는 `rollback-owner`/`rollback_owner` 참조가 없었다.

## 실행 증빙

- `python3 -m unittest tests.test_release_manager` → **74 tests, OK**
- `deploy`, `rollback`, `history-cleanup`, `migrate-runtime-backups`의 `--help`를 직접 확인 → 모두 `--operator` 노출, `--rollback-owner` 미노출
- source·문서·Runtime 대상 검색 → `rollback_owner`/`rollback-owner` 잔존 없음 (태스크 문서와 새 테스트 이름 제외)
- `git diff --check` → 공백 오류 없음

## Changelog 대조

changelog의 코드 변경 범위와 74개 단위 테스트 통과 주장은 실제와 일치한다. 그러나 “운영 명령 예시와 실행자 원칙 갱신”은 `install.md`의 상단 deploy 예시가 아직 실행 불가능하므로 완결되지 않았다.
