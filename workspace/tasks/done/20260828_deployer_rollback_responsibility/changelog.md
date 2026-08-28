# 태스크 내역서: 배포자와 복구 책임자 일원화

**작업일:** 2026-08-28
**계획서:** `plan.md`

---

## 변경 파일 목록

| 파일 경로 | 변경 유형 | 설명 |
|---------|---------|------|
| `release_manager.py` | 수정 | 별도 복구 책임자 입력을 `operator` 실행자 기록으로 대체 |
| `tests/test_release_manager.py` | 수정 | 새 CLI·receipt 계약과 기존 게이트 회귀 검증 |
| `README.md`, `install.md`, `guidebook/guidebook.md` | 수정 | 운영 명령 예시와 실행자 원칙 갱신 |
| `map-product-rules/*.md` | 수정 | 배포·이력 정리 계약을 실행자 책임 모델로 통일 |
| `workspace/memory/shared/architecture.md` | 수정 | 현재 배포 기록 구조 스냅샷 갱신 |

---

## 상세 변경 내역

### `release_manager.py`

- **대상:** `deploy`, `rollback`, `history_cleanup`, `migrate_runtime_backups` 및 CLI parser
- **변경 유형:** 수정
- **내역:** `rollback_owner` 입력·검증·receipt 기록을 제거하고, 별도 `operator`를 필수 실행자 기록으로 추가했다. 성공·실패 deploy/rollback receipt에 실행자를 남기며, 승인자·승인 기록·dry-run·backup 검증은 유지했다.

### `tests/test_release_manager.py`

- **대상:** deployment/rollback fixture와 CLI·receipt 계약 검증
- **변경 유형:** 수정
- **내역:** 새 `operator` 입력을 사용하도록 fixture를 갱신하고, deploy help에 `--operator`만 노출되며 새 receipt에 `rollback_owner`가 없는지 검증했다.

## 요구사항 명세 대비 변경 사항

| 변경 | 이유 | 명세 영향 | 보고 |
|---|---|---|---|
| Runtime source/dist 동기화 단계 미실행 | 별도 복구 책임자 요구는 source 배포 도구·운영 문서에만 존재했고 `.mpa/runtime/`에는 변경 대상이 없었다. | 없음 | 구현 종료 시 보고 |

## 검증 포인트

- [x] 정상 경로 확인: 74개 unit test가 deploy·rollback·이력 정리·backup migration의 새 `operator` 계약을 통과했다.
- [x] 실패 경로 확인: operator·승인자·승인 기록 누락 거부와 rollback 실패 receipt의 원래 오류 보존을 확인했다.
- [x] 독립 검증: 1차에서 install 예시와 네 관리 명령의 CLI 회귀 검증 누락을 발견했고, 수정 뒤 2차에서 통과를 확인했다.
- [x] plan.md 완료 기준 충족 여부: 구현·문서·CLI·기록 변경과 독립 검증을 완료했다.
