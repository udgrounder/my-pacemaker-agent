# 변경 기록: 성공 배포 Runtime 백업의 ZIP 보관

## 2026-08-25

- `release_manager.py` — 성공 배포의 디렉터리 backup을 검증된 ZIP으로 원자 publish한 뒤 원본을 삭제하도록 변경했다. rollback은 ZIP과 기존 디렉터리 backup을 모두 안전 해제·검증·복원한다.
- `tests/test_release_manager.py` — ZIP 보관, 압축 실패 복구, ZIP·기존 디렉터리 rollback, ZIP retention, rollback 승인값, receipt 기록 실패 뒤 ZIP 보존을 포함하도록 회귀 테스트를 갱신했다.
- 배포 규칙·명령 계약·README·아키텍처 메모리를 ZIP backup 계약으로 동기화했고, 승인 정보가 없을 때 에이전트가 사용자 승인 요청을 먼저 하도록 운영 절차를 명시했다.

## 검증

- `python3 -m unittest tests.test_release_manager -v` — 66 tests passed
- `python3 release_manager.py release-audit` — 21 release bundles passed
- `git diff --check` — passed
- 독립 후속 검토 — 즉시 수정 필요 0건. retention의 ZIP 전체 무결성 재검증 제외는 사용자 결정으로 기록했다.
- `runtime.zip` 전환 — version backup 디렉터리와 metadata를 유지하고 내부 `runtime/`만 ZIP으로 보관하도록 deploy·rollback·retention을 재구성했다. legacy `runtime/` rollback은 거부하며, migration 실패는 원본을 보존해 사용자에게 보고한다.
- `campingtalk-proj` 기존 backup 3개를 `runtime.zip`으로 전환했다. 모든 `runtime/` 원본은 검증 성공 뒤 삭제됐고 전환 실패는 없었다.
- `python3 -m unittest tests.test_release_manager -q` — 68 tests passed
- 각 대상 `runtime.zip` — `unzip -tqq` passed
- `backup-metadata.json` — `archive_migration`에 ZIP archive 경로, 완료/실패 시각, 원본 `runtime/` 삭제 여부와 실패 원인을 기록하도록 보완했다. 기존 3개 backup 모두 `completed`로 갱신됐다.
- `history-cleanup` — 사용자 승인 뒤 오래된 release bundle 11개를 정리해 10개를 보관했다. 두 등록 대상의 history·receipt·Runtime backup은 후보가 없어 변경하지 않았으며, 사후 dry-run과 `release-audit`이 모두 통과했다.
- `release_manager.py` — 후보가 없는 등록 대상에는 cleanup lock을 만들지 않도록 보완했다. README는 명시 정리 요청·dry-run·승인 apply와 보존 제외 규칙을 분리해 설명하도록 갱신했다.
- `python3 -m unittest tests.test_release_manager -q` — 70 tests passed
- `python3 release_manager.py release-audit` — 10 retained release bundles passed
