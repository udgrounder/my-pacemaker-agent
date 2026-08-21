# map-product Command Contract

이 표는 source 전용 운영 명령과 profile의 단일 계약표다. Runtime에는 이 명령이나 source 경로를 배포하지 않는다.

| Command | Trigger / Input | Checks and gate | Output / failure | Prohibited |
|---|---|---|---|---|
| `install.py --dry-run` | 빈/없는 명시 대상, agent, 선택적 `--runtime-config-json` | template·spec·hook·Python·project config 및 `runtime.*` additive migration 검사 | project root·Runtime·workspace/issues·docs/INDEX·`.mpa/config/config.yaml` 생성/보강 계획 / 파일 무변경 | 기존 설치 update, 기존 사용자 영역 변경 |
| `project_config.py audit` | 설치 대상의 `.mpa/config/config.yaml` | schema·필수 필드·경로 불일치·민감정보 패턴 | warning-level audit와 semantic checksum / 파일 무변경 | 절대 경로를 중앙 receipt·release asset·issue로 복사 |
| `sync-runtime` | Runtime source 변경 | symlink·비정상 파일 거부 | `dist/.mpa/runtime` 동기화 | `dist/workspace` 변경 |
| `prepare-release` | **사용자 명시 릴리즈 요청** 또는 **배포 요청 시 최신 release 부재**, argv validation과 metadata, 선택적 `--runtime-config-json` | UTC `YYYYMMDDHHMMSS-uuid8` release ID 생성, source/dist 동기화, validation 성공, ZIP·manifest·note·release receipt 상호 참조, `runtime.*` additive migration 검증 | 단일 release ID와 bundle 경로, checksum 증빙 / 생성분 원자 정리 | Runtime 변경·검증만으로 실행, Git clean gate, 사용자 자산·기존 config 값 포함 |
| `release-audit` | active release bundle | bundle 파일 inventory·schema·ZIP·assets·receipt·validation 참조 | audit 결과 / 오류 목록 | legacy artifact를 active로 허용 |
| `deployment-dry-run` | manifest, target, target-ref | release package·target release/history·issue inventory·config checksum/migration 후보 확인 | 만료 가능한 dry-run receipt와 수집 후보·설정 추가 후보 고지 | 대상 변경 |
| `deploy` | recorded dry-run, 승인·rollback 책임 | target release/asset/history/receipt/issue inventory/config/만료 재검증; 배포 전 `.mpa/runtime`와 migration 대상 config backup | `from_release → to_release`, 설정 migration·수집·원본 정리 결과 고지, Runtime+config backup; 성공 후 최신 3개 유지; 없는 `workspace/`·`workspace/issues/`·`docs/INDEX.md` 생성 | 기존 user config 값·workspace·docs·agent 설정·일반 소스 변경 |
| `rollback` | backup, release ID, 승인·책임 | target history와 backup 범위 검사, Runtime 및 config snapshot 무결성 확인 | Runtime과 MPA config를 함께 rolled_back receipt/history로 복원 | backup 범위 밖 읽기·복원 |
| `issue-create` / `issue-collect` | 명시 프로젝트·issue 또는 승인된 update batch | canonical metadata, 민감정보·중복·inventory 검사, 목적지 생성·존재 확인 뒤 원본 삭제·부재 확인 | project issue 또는 inbox와 사용자 고지 | dry-run 고지 없는 자동 수집·덮어쓰기·별도 collection receipt |
| `issue-archive` | 사용자 검토 뒤 inbox issue, 결정·근거, 채택 시 task plan | 채택 task plan 존재·archive 충돌 확인 | 이슈 파일에 사용자 결정·근거·연결 작업을 기록한 archive / 실패 시 inbox 보존 | 별도 review·triage receipt, 결정 없는 archive |
