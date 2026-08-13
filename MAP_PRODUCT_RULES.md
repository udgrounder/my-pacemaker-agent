# MAP Product 운영 규칙

이 파일은 my-pacemaker-agent source 저장소에서만 사용한다. `dist/`나 설치 대상에 배포하지 않는다.

## 라우팅 우선순위

다음 요청은 Runtime 규칙보다 먼저 `map-product-rules/`의 해당 프로필을 읽고 처리한다.

| 요청 | 프로필 |
|---|---|
| 설치·installation refresh | `installation.md` |
| 이슈 회수·검토·분류 | `issue-intake.md`, `issue-triage.md` |
| 릴리스 준비·manifest·receipt | `release-preparation.md` |
| Runtime 배포·rollback | `deployment-coordination.md` |

그 밖의 대상 프로젝트 작업은 `.mpa-workspace/core/agent_rules.md`를 따른다.

## 불변식

- map-product 규칙·도구·`workspace/issues/`·release receipt는 source 전용이다.
- Runtime release는 `dist/.mpa-workspace/`만 대상으로 한다.
- release manifest는 같은 ID의 `workspace/releases/packages/<release-id>/` 불변 스냅샷과 함께 존재해야 한다. 배포는 현재 `dist/`가 아니라 이 스냅샷만 사용한다.
- 대상 프로젝트의 `workspace/`, `docs/`, agent 설정, 일반 소스는 Runtime deployment와 rollback에서 읽거나 변경하지 않는다. 단, 없는 `workspace/`, `workspace/issues/`, `docs/`, `docs/INDEX.md`는 초기화할 수 있다.
- 대상 프로젝트의 `.mpa-project/config.yaml`은 설치 고유 설정이다. 최초 설치 시 없으면 기본 프로젝트명·초기화 시각·절대 root path로 만들고, 있으면 누락 필드만 추가한다. Runtime deployment/rollback은 기존 값을 덮어쓰지 않으며, config의 절대 경로를 release asset·manifest checksum·issue·중앙 receipt에 복사하지 않는다.
- 이슈 수집은 원칙적으로 명시 요청 대상만 처리한다. 단, 승인된 Runtime update는 dry-run에서 후보를 고지한 뒤 검증 성공 시에만 batch를 원자 수집하고 원본 정리 결과를 고지할 수 있다.
