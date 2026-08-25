# MAP Product 운영 규칙

이 파일은 my-pacemaker-agent source 저장소에서만 사용한다. `dist/`나 설치 대상에 배포하지 않는다.

## 라우팅 우선순위

다음 요청은 Runtime 규칙보다 먼저 `map-product-rules/`의 해당 프로필을 읽고 처리한다.

| 요청 | 프로필 |
|---|---|
| 최초 설치 | `installation.md` |
| 이슈 회수·검토·분류 | `issue-intake.md`, `issue-triage.md` |
| 릴리스 준비·manifest·receipt | `release-preparation.md` |
| Runtime 배포·rollback | `deployment-coordination.md` |

그 밖의 대상 프로젝트 작업은 `.mpa/runtime/core/agent_rules.md`를 따른다.

## 불변식

- map-product 규칙·도구·`workspace/issues/`·release receipt는 source 전용이다.
- Runtime release는 `dist/.mpa/runtime/`만 대상으로 한다.
- release는 `workspace/releases/<release-id>/` 아래의 `package_<release-id>.zip`, `manifest_<release-id>.json`, `note_<release-id>.md`, `release-receipt_<release-id>.json` 번들이다. 배포는 현재 `dist/`가 아니라 ZIP과 manifest가 검증한 불변 번들만 사용한다.
- **릴리즈 생성은 사용자 요청 기반이다.** Runtime 변경·검증만으로 `prepare-release`를 실행하지 않는다. 사용자가 명시적으로 릴리즈를 요청하거나 배포를 요청했을 때, 현재 source Runtime을 담은 최신 유효 release가 없을 경우에만 새 release를 생성한다. 기존 immutable release는 삭제·재작성하지 않는다.
- Runtime deploy는 배포 중 대상 `.mpa/backups/<version>/runtime/`에 디렉터리 snapshot을 만들어 즉시 복구에 사용한 뒤, 성공 검증 후 `runtime.zip`으로 압축·검증하고 원본 `runtime/`만 삭제한다. version backup의 marker·선택적 config snapshot은 유지한다. release ZIP의 장기 보관 용도와는 구분한다. release·배포·backup 이력은 일반 deploy/upgrade에서 자동 삭제하지 않는다. 사용자가 명시적으로 정리를 요청하면 `history-cleanup`이 전체 후보를 dry-run으로 제시하고, 승인 정보와 `--apply`가 함께 있을 때만 release·대상 history/receipt와 성공 `runtime.zip` backup을 보관 기준에 따라 정리한다. 실패·사용자 snapshot은 보존한다.
- 대상 프로젝트의 `workspace/`, `docs/`, agent 설정, 일반 소스는 Runtime deployment와 rollback에서 읽거나 변경하지 않는다. 단, 없는 `workspace/`, `workspace/issues/`, `docs/`, `docs/INDEX.md`는 초기화할 수 있다.
- 대상 프로젝트의 `.mpa/config/config.yaml`은 설치 고유 설정이다. 최초 설치 시 없으면 기본 프로젝트명·초기화 시각·절대 root path로 만들고, 있으면 누락 필드만 추가한다. 릴리즈가 `runtime_config` additive migration을 명시한 경우 deploy가 `runtime.*` 누락값만 추가하며 기존 project/user 값은 덮어쓰지 않는다. 이때 배포 전 config를 Runtime과 함께 백업하고 rollback 때 함께 복원한다. `${project.name}`, `${project.root_path}`, `${project.initialized_at}` 참조는 대상 로컬 값으로 해석하고, config의 절대 경로 원문은 release asset·manifest checksum·issue·중앙 receipt에 복사하지 않는다.
- 이슈 수집은 원칙적으로 명시 요청 대상만 처리한다. 단, 승인된 Runtime update는 dry-run에서 후보를 고지한 뒤 검증 성공 시에만 batch를 원자 수집하고 원본 정리 결과를 고지할 수 있다.
