# map-product Command Contract

이 표는 source 전용 운영 명령과 profile의 단일 계약표다. Runtime에는 이 명령이나 source 경로를 배포하지 않는다.

| Command | Trigger / Input | Checks and gate | Output / failure | Prohibited |
|---|---|---|---|---|
| `install.py --dry-run` | 빈/없는 명시 대상, agent | template·spec·hook·Python 검사 | project root·Runtime·workspace/issues·docs/INDEX 생성 계획 / 파일 무변경 | 기존 설치 update, 기존 사용자 영역 변경 |
| `install.py --installation-refresh --plan` | 승인된 기존 설치 agent 갱신 plan | target·agent allowlist·preserve·backup·approval ref 필수 | refresh receipt / backup 후 원복 | Runtime deploy 호출, workspace·docs·일반 소스 변경 |
| `sync-runtime` | Runtime source 변경 | symlink·비정상 파일 거부 | `dist/.mpa-workspace` 동기화 | `dist/workspace` 변경 |
| `prepare-release` | 선언 Runtime version, argv validation과 metadata | version↔package 일대일, validation 성공, immutable package/receipt/manifest 상호 참조 | versioned release ID, checksum 증빙 / 생성분 원자 정리 | Git clean gate, 사용자 자산 포함 |
| `release-audit` | active manifest | schema·package·assets·receipt·validation 참조 | audit 결과 / 오류 목록 | legacy artifact를 active로 허용 |
| `deployment-dry-run` | manifest, target, target-ref | release package·target version/history·issue inventory 확인 | 만료 가능한 dry-run receipt와 수집 후보 고지 | 대상 변경 |
| `deploy` | recorded dry-run, 승인·rollback 책임 | target/version/asset/history/receipt/issue inventory/만료 재검증 | `from_version → to_version`, 수집·원본 정리 결과 고지, Runtime backup; 없는 `workspace/`·`workspace/issues/`·`docs/INDEX.md` 생성 | 기존 workspace·docs·agent 설정·일반 소스 변경 |
| `rollback` | backup, release ID, 승인·책임 | target history와 backup 범위 검사 | rolled_back receipt/history | backup 범위 밖 읽기·복원 |
| `issue-create` / `issue-collect` | 명시 프로젝트·issue 또는 승인된 update batch | canonical metadata, 민감정보·중복·inventory 검사 | project issue 또는 inbox/collection receipt와 사용자 고지 | dry-run 고지 없는 자동 수집·덮어쓰기 |
| `issue-review` / `issue-triage` | inbox issue, review approval | accepted review·재현성·영향·우선순위 확인 | review/triage receipt 또는 inbox 보존 | review 없는 triage/archive |
| `issue-resolve` / `issue-archive` | triaged issue, release/deploy/verification evidence | evidence release ID와 archive 대상 대조 | resolution/archive receipt | 근거 없는 archive |
