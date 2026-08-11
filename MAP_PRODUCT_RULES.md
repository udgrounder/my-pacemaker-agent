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
- 대상 프로젝트의 `workspace/`, `docs/`, agent 설정, 일반 소스는 Runtime deployment와 rollback에서 읽거나 변경하지 않는다.
- 이슈 수집은 사용자 요청으로 지정된 프로젝트·파일만 대상으로 한다.
