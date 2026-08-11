# Deployment Coordination Profile

승인된 release manifest와 일치하는 불변 package만 배포한다. 대상 `.mpa-workspace/`만 backup·교체·rollback하고 deployment receipt를 기록한다.

`target-ref`는 소문자 안전 식별자만 허용하며, rollback 원본은 대상 `.mpa-backups/` 아래의 생성된 backup만 허용한다. 배포 중 검증에 실패하면 기존 Runtime을 즉시 복원한다.
