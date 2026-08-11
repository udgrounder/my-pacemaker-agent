---
태스크: release_deployment_management
생성일: 2026-08-05
타입: major
실패비용: major
상태: 구현 중
승인해시: bcb2619334f43335
---

# 태스크 계획서: release_deployment_management

**파생 출처:** 없음

---

## PRD

> **구현 전에 이 PRD 섹션 전체를 먼저 확인하세요. PRD가 확정되기 전엔 "구현 단계"를 작성하지 않습니다.**

### 에이전트 보고

#### 사용자 결정 필요 (Open Questions)

- 없음 — 사용자가 릴리스·배포뿐 아니라 이슈 생성·수집까지 같은 참고 모델로 개선하길 요청했다. 따라서 절차 규칙과 이를 지원하는 결정론적 도구를 함께 구현한다.

#### 암묵적 결정

- Git은 release asset allowlist와 설치·배포 도구 경로에 한정해 후보 변경 파일을 찾고 사람이 읽을 수 있는 source 식별자(HEAD·scoped diff 요약)를 receipt에 덧붙이는 **선택적 보조 수단**으로만 쓴다. 이 범위 밖의 dirty 파일은 release를 차단하지 않으며, clean worktree·커밋·push·revision 일치 여부도 Gate가 아니다.
- MPA 릴리스의 배포 자산은 `dist/.mpa-workspace/`의 관리 파일만으로 한정한다. `dist/workspace/`는 신규 설치용 골격이고, `agent-specs/`·`install.py`는 설치 도구이므로 release manifest·배포·rollback 대상에서 제외한다.
- release(배포 가능한 MPA 패키지)와 deployment(명시된 프로젝트에 적용한 결과)는 별도 산출물·별도 상태로 관리한다.
- issue는 프로젝트에서 생성한 관찰 기록과 MPA source 저장소가 수집한 개선 항목을 분리하고, 수집·분류·보관 전환은 사용자 검토 기록 뒤에만 허용한다.
- source 저장소의 회수함은 `workspace/issues/`다. 명시적 수집 시 `workspace/issues/inbox/<project-ref>/`에 넣고, 처리 완료 후에는 `workspace/issues/archived/YYYY/MM/<project-ref>/`로 이동한다. 이 경로는 배포·신규 설치 골격에 포함하지 않는다.
- 기존 `upgrade-candidates`는 폐기하고 issue의 `methodology_improvement` 분류로 이관한다. 새 후보는 `.mpa-workspace/`가 아니라 프로젝트 소유 `workspace/issues/`에 생성하고, source 저장소로의 수집은 명시적 요청일 때만 실행한다.
- `docs/`는 사용자가 미리 만든 프로젝트 루트 경로로 전제한다. 문서는 배포·신규 설치 골격에 포함하지 않고, Runtime 규칙·템플릿의 `workspace/docs/` 참조만 루트 `docs/`로 바꾼다. 문서 이동·생성은 수행하지 않는다.
- **map-product plane**(`MAP_PRODUCT_RULES.md`, `map-product-rules/`, `release_manager.py`, `install.py`, `agent-specs/`, source `workspace/`, `docs/`)은 이 저장소의 이슈 회수·릴리스·배포·설치 정책을 관리하며 배포하지 않는다. **Runtime/deployment plane**(`.mpa-workspace/` → `dist/.mpa-workspace/`)은 대상 프로젝트에 공통으로 적용할 규칙·정책·실행 소스만 관리한다. 대상 프로젝트의 `workspace/`·`docs/`는 사용자 소유 데이터다.
- source 저장소의 `AGENTS.md`는 `MAP_PRODUCT_RULES.md`를 Runtime 규칙보다 먼저 로드한다. map-product route가 이슈 회수·review/triage·릴리스 준비·배포·rollback 요청을 먼저 처리하고, 그 밖의 대상 프로젝트 작업만 Runtime `agent_rules.md`에 위임한다.
- **최초 설치**는 `install.py`가 명시된 빈 대상에 `.mpa-workspace/`, `dist/workspace/`의 초기 골격, agent 진입 설정을 한 번만 설치한다. **Runtime 업데이트**는 준비된 release manifest를 입력으로 `release_manager.py deploy`가 대상 `.mpa-workspace/`만 backup·교체한다. `install.py --upgrade`의 기존 전체 교체 경로는 Runtime 업데이트에 사용하지 않으며, 설치 도구·agent 설정 변경은 기존 설치본에 자동 적용하지 않는다.
- Circled Wiki의 clean worktree·commit Gate는 도입하지 않는다. 이는 관계없는 dirty 파일 때문에 작업이 중단되지 않아야 한다는 사용자 결정과 충돌한다. 대신 release asset map, scoped Git 식별자, 실행된 검증 명령과 결과를 immutable receipt에 함께 남긴다.
- release manifest는 asset map 외에 compatibility, breaking change, migration, rollback condition, release note를 명시한다. 이 중 하나라도 미기록이면 release 준비를 완료하지 않는다.
- deployment는 `dry-run → 명시 승인 정보·rollback 책임자 기록 → backup → apply → Runtime 검증 → deployment receipt` 순서로만 진행한다. 대상 `.mpa-workspace/history/releases/<release-id>.json`에는 승인된 manifest asset map과 적용 결과를 기록한다.
- issue triage는 accepted review receipt뿐 아니라 재현성, 영향도, 우선순위, archive 유사 관계(`recurrence`/`regression`/`duplicate`/`related`/`new`/`undetermined`)와 후속 task를 기록한다. 근거가 부족하면 archive하지 않고 inbox의 `needs_information` 또는 `undetermined`로 유지한다.

#### 에이전트 가정 (Assumptions)

| 가정 | 근거 | 틀렸다면 |
|---|---|---|
| 버전·배포 관리는 이 저장소의 MPA 방법론 기능을 뜻한다 | 현재 구현은 `.mpa-version`, `dist/`, `install.py --upgrade`만 제공하며, 참고 저장소도 제품 규칙과 배포 도구를 함께 둔다 | 대상 프로젝트용 운영 기능으로 범위를 바꿔야 한다 |
| manifest와 receipt는 이 저장소 `workspace/`에 보존해도 된다 | 이 경로는 이 프로젝트가 소유하며, 설치 대상에 복사되는 `dist/`와 분리돼 있다 | 별도 release 저장소나 외부 기록소가 필요하다 |
| 신규 설치는 기존 `install.py`가 담당하고, release deployment는 `.mpa-workspace/`만 교체한다 | 설치 골격·agent 설정과 MPA 릴리스 자산은 생명주기와 소유권이 다르다 | 설치 도구까지 release에 포함돼 사용자 파일·설정에 불필요하게 영향을 준다 |
| Git 메타데이터는 release 관련 경로로 범위를 제한해 receipt에 기록한다 | 사용자는 관계없는 파일 수정이 release를 멈추게 하는 문제를 피하면서 변경 파일 확인과 source 식별에는 Git 사용을 원한다 | Git 없는 저장소에서도 파일 해시만으로 식별하도록 유지해야 한다 |
| 이슈 수집은 명시된 프로젝트와 이슈 파일만 대상으로 한다 | 다른 프로젝트의 관찰 기록을 임의로 이동하면 운영 문맥과 소유권이 깨질 수 있다 | 중앙 수집 정책과 별도 접근 권한 모델이 필요하다 |
| 기존 upgrade-candidates의 이력은 issue로 이관해 보존한다 | 이름만 바꾸고 삭제하면 아직 처리되지 않은 방법론 개선 제안의 맥락을 잃는다 | 별도 legacy archive를 유지하는 migration 계획이 필요하다 |
| 루트 `docs/`는 구현 전에 사용자가 만들어 둔다 | 문서 구조의 실제 이동·생성은 사용자 소유이고, 이번 변경은 Runtime 참조 경로 정정으로 한정한다 | 대상 프로젝트에 `docs/`가 없으면 Runtime 문서 작성 시 사용자가 먼저 경로를 만들어야 한다 |
| source 운영 정책과 배포 Runtime 정책은 별도 진입점으로 분리한다 | 이슈 회수·release·deploy 정책을 Runtime에 넣으면 모든 설치본이 source 저장소의 권한·경로를 전제하게 된다 | source-only policy와 Runtime rule을 한 파일에 계속 혼합하게 된다 |
| source→dist 삭제 반영은 명시적 prune 명령으로만 수행한다 | 현재 자동 동기화 훅은 제외 경로와 삭제를 처리하지 않아 stale 배포 파일이 남는다 | 일반 편집 훅에 광범위한 삭제 권한을 주거나 source/dist가 드리프트한다 |
| 기존 설치본의 업데이트는 release manifest를 통해서만 한다 | install.py의 전체 upgrade는 사용자 workspace·설정에 영향을 줄 수 있어 Runtime release 경계와 맞지 않는다 | install tool 실행이 Runtime 업데이트를 겸하며 사용자 영역을 다시 병합·변경한다 |

### 요청 원문

버젼 관리 및 배포 관리 기능을 git 체크하는 부분을 제외 하고 /Users/kjkim/Study/circled-wiki 를 참고 해서 개선하고 싶어

이슈 생성과 수집하는것도 마찬가지로 참고 해서 하고 싶어

### 목적

Git 의존성 없이도 이슈 생성·수집부터 분류, 재현 가능한 릴리스와 대상별 배포 이력까지 추적하도록 MPA 운영 체계를 개선한다.

### 요구사항

- Circled Wiki의 release preparation / deployment coordination 분리를 MPA 구조에 맞게 적용한다.
- Git clean worktree·커밋·push·revision 일치 검증은 도입하지 않는다. 단, 이용 가능한 경우 release 관련 allowlist 경로만 Git diff로 확인하고 Git source 식별자를 receipt에 보조 정보로 기록한다. 관계없는 dirty 파일은 무시한다.
- 배포 자산 allowlist, manifest, release receipt, deployment receipt, backup·rollback·보존 데이터 보호 원칙을 정의한다.
- 기존 `dist/` 단일 배포 소스와 신규 설치용 `install.py` 경로를 훼손하지 않는다. 단, release deployment는 `install.py --upgrade`를 호출하지 않고 `.mpa-workspace/`만 적용한다.
- 프로젝트 내부 이슈 생성, 명시적 수집, 사용자 검토, 원인 분류, 작업 연결, archive 이력을 지원한다.
- 수집 대상 이슈와 중앙 이슈는 중복 보관하지 않고, 민감정보·머신 절대 경로를 기록하지 않으며, 수집·분류·archive는 사용자 확인이 있어야 한다.
- `upgrade-candidates` 용어·경로·자동 이전/초기화 규칙을 `issues`로 전환하고, 방법론 개선은 issue 분류값으로 표현한다.
- Runtime 규칙·템플릿의 문서 경로를 루트 `docs/`로 통일한다. `docs/` 이동·생성·배포는 수행하지 않는다.
- source 전용 map-product 규칙·프로필과 배포 전용 Runtime 규칙·실행 소스를 분리하고, 어느 파일도 두 영역을 동시에 소유하지 않게 한다.
- 최초 설치, Runtime 업데이트, installation tooling 갱신을 서로 다른 입력·적용 범위·rollback 책임으로 정의한다.

---

## 구현 계획 (Implementation Plan)

### 사전 조사

- Circled Wiki는 `release preparation`과 `deployment coordination`을 분리하고, release manifest·release receipt를 대상 배포 전에 고정하며, deployment/verification receipt는 대상별로 기록한다.
- 현재 MPA는 `dist/`를 설치 원본으로 사용하고 `install.py --upgrade`가 `.mpa-workspace/`와 신규 workspace 골격을 함께 처리한다. 설치 이력만 `workspace/.mpa-version-info`에 남으며, release·deployment·issue lifecycle 기록과 backup이 없다.
- `dist/.mpa-workspace/`만 release asset map에 포함한다. `dist/workspace/`는 최초 설치의 빈 골격이고, `agent-specs/`·`install.py`는 설치 도구이며, `upgrade-candidates/`는 프로젝트별 피드백이므로 모두 release에서 제외한다.

### 구현 단계

- [ ] Step 1 — 현재 저장소 파일을 map-product plane(`AGENTS.md`, `MAP_PRODUCT_RULES.md`, `map-product-rules/`, `release_manager.py`, `install.py`, `agent-specs/`, source `workspace/`, `docs/`), Runtime/deployment plane(`.mpa-workspace/` → `dist/.mpa-workspace/`), 신규 설치 골격(`dist/workspace/`), 대상 사용자 데이터(`workspace/`, `docs/`)로 전수 분류하고 각 영역의 소유자·진입점·복사 방향·release 포함 여부를 SSOT로 문서화한다. `AGENTS.md`에는 map-product 규칙을 Runtime보다 먼저 로드하는 source 전용 진입점을 추가한다. 루트 `docs/`는 사용자 제공 경로로 분류하고, 문서 이동·생성·배포 없이 Runtime 참조만 정정한다. `.mpa-workspace/upgrade-candidates/`와 `dist/.mpa-workspace/upgrade-candidates/`의 기존 후보·archive는 source `workspace/issues/`의 방법론 개선 issue로 이관해 보존한 뒤 경로를 제거한다. `install.py`의 후보 자동 이전·초기화도 제거한다. / 이유: source 운영 정책과 배포 Runtime 정책의 경계를 먼저 고정해야 release allowlist·backup 범위·권한이 안전하게 결정된다.
- [ ] Step 2 — source 저장소 전용 `release_manager.py` CLI에 `sync-runtime`과 release asset allowlist를 구현한다. `sync-runtime`은 `.mpa-workspace/`를 `dist/.mpa-workspace/`로 복사하고, **이 두 명시 경로 안에서만** source에 없는 파일을 prune한다. 이를 `upgrade-candidates` 제거와 Runtime 변경 뒤에 명시적으로 실행한다. 이어서 확정된 `dist/.mpa-workspace/` 관리 자산만 해시한 안정적 asset map으로 release ID를 계산하고, manifest·release receipt를 `workspace/releases/`와 `workspace/receipts/releases/`에 원자적으로 기록한다. Git diff와 HEAD는 이 allowlist만 대상으로 변경 후보·source 식별자 메타데이터를 기록하며, 이 범위 밖 dirty 파일은 무시한다. / 이유: 자동 편집 훅에 삭제 권한을 부여하지 않으면서 source/dist stale 파일을 제거하고 같은 MPA 배포 자산을 같은 release로 식별해야 한다.
- [ ] Step 3 — release manager의 deploy/rollback 명령을 구현한다. 승인된 manifest를 먼저 검증한 뒤 대상 `.mpa-workspace/`만 backup·교체·복구하며, `workspace/`, agent 설정, 일반 소스, `install.py`가 설치한 초기 골격은 읽거나 수정하지 않는다. 적용 뒤 대상 `.mpa-workspace/`의 관리 자산 해시를 확인하고 deployment receipt를 기록한다. / 이유: 설치와 릴리스 배포의 소유 경계를 분리해 사용자 파일·설정에 불필요하게 영향을 주지 않는다.
- [ ] Step 3 — 설치·업데이트 절차를 분리해 구현한다. `install.py install`(또는 호환되는 기본 설치)은 최초 설치 대상에만 `.mpa-workspace/`, `dist/workspace/` 초기 골격, 선택한 agent 진입 설정을 설치하며, 이미 `.mpa-workspace/`가 있는 대상은 자동 upgrade하지 않고 Runtime update 절차를 안내한다. `install.py --upgrade`의 전체 교체 경로는 제거하거나 명시적으로 거부한다. 설치 도구·agent 설정의 변경은 기존 설치본에 자동 적용하지 않고, 별도 명시 요청의 installation refresh로만 처리하도록 map-product 정책에 기록한다. / 이유: 최초 설치와 Runtime update를 같은 명령으로 처리하면 update가 사용자 영역과 설정까지 변경하는 경계 침범이 발생한다.
- [ ] Step 4 — release manager의 deploy/rollback 명령을 구현한다. 승인된 manifest를 먼저 검증한 뒤 대상 `.mpa-workspace/`만 backup·교체·복구하며, `workspace/`, agent 설정, 일반 소스, `install.py`가 설치한 초기 골격은 읽거나 수정하지 않는다. 적용 뒤 대상 `.mpa-workspace/`의 관리 자산 해시를 확인하고 deployment receipt를 기록한다. / 이유: 설치와 릴리스 배포의 소유 경계를 분리해 사용자 파일·설정에 불필요하게 영향을 주지 않는다.
- [ ] Step 5 — source 저장소에 `workspace/issues/inbox/`·`workspace/issues/archived/`·README와 issue schema를 만들고, CLI에 `issue create`·`issue collect`를 구현한다. create는 지정 프로젝트의 로컬 `workspace/issues/`에 안전한 식별자와 관찰 정보만 가진 issue를 만들며, `methodology_improvement`는 기존 upgrade-candidate의 역할을 대체한다. collect는 사용자가 지정한 프로젝트·issue만 source `workspace/issues/inbox/<project-ref>/`로 원자적으로 이동하고, 중복·동시 inbox/archive 존재·민감정보/절대 경로를 차단한다. / 이유: 운영 관찰과 MPA 개선 검토를 하나의 lifecycle로 다루면서도 요청되지 않은 데이터 이동을 막는다.
- [ ] Step 6 — CLI에 issue review·triage·resolution·archive 전이를 추가한다. review receipt가 있는 항목만 triage할 수 있게 하고, 분류·유사 archive 관계·연결 태스크/release/deployment/verification receipt를 기록한다. 완료 처리된 issue는 release/deployment/verification 근거가 있을 때만 source `workspace/issues/archived/YYYY/MM/<project-ref>/`로 원자 이동한다. / 이유: 증상 수집만으로 해결됐다고 오인하지 않고, 이슈에서 실제 배포 검증까지 추적한다.
- [ ] Step 7 — source 전용 `MAP_PRODUCT_RULES.md`와 `map-product-rules/`를 추가해 최초 설치·installation refresh·이슈 회수·review/triage·release preparation·deployment coordination의 입력·Gate·출력·금지사항을 관리한다. map-product route는 Runtime route보다 먼저 이 요청을 잡고, Runtime `.mpa-workspace`에는 대상 프로젝트에서 필요한 공통 규칙과 로컬 issue 생성 규칙만 남긴다. source 경로·회수·release·deploy 권한을 전제하는 규칙은 모두 map-product plane으로 옮긴다. `upgrade-candidates`는 `core/agent_rules*`, `inject/{discussion_mode,layer0_update,layer1_critique,layer1_design,layer1_implement,layer1_review,layer2_checkpoint}.md`, `templates/knowledge_template.md`, `install.py`, `workspace/project_rules.md`에서 issue lifecycle과 `methodology_improvement` 분류로 이관한다. Runtime의 `core/agent_rules.md`, `inject/{layer1_design,layer1_implement,layer2_checkpoint}.md`, `templates/{docs_template,plan_template}.md`는 사용자 제공 루트 `docs/`를 사용하도록 `workspace/docs/` 참조만 정정한다. `docs/` 이동·생성·배포는 하지 않는다. / 이유: 같은 파일이 source 운영과 대상 Runtime을 동시에 통치하면 배포본이 잘못된 권한·경로를 전제하고, 불완전한 용어 이관은 구 흐름을 재활성화한다.
- [ ] Step 8 — 단위·통합 테스트를 추가한다. 최초 설치 성공·기존 설치본의 install 거부 및 Runtime update 안내·installation refresh 명시 요청 Gate, map-product 진입점 우선 라우팅과 Runtime source 경로 미참조, 영역 분류, live Runtime·template에서 `workspace/docs/` 검색 0건과 루트 `docs/` 참조, 문서 이동·생성·설치 골격 변경 미발생, 기존 upgrade-candidates의 issue 이관·경로 제거·자동 수집 미발생, live Runtime·install source에서 `upgrade-candidates` 검색 0건, `sync-runtime`이 `dist/.mpa-workspace/` 안의 stale 파일만 prune하고 그 밖의 dist/user 파일을 보존하는지, 동일 asset map의 release ID 재현, Git 부재/오류에도 release 생성, allowlist 밖 자산 거부, backup→deploy→rollback, 사용자 workspace 보존, issue 생성→수집→review→triage→release 연결→archive, 중복·미승인 전이·민감정보 거부를 검증한다. 마지막으로 설치본 dry-run과 source/dist 동기화를 확인하고 `current_version`을 갱신한다. / 이유: 상태 전이·파일 이동·데이터 보존은 문서 검토만으로 회귀를 방지할 수 없기 때문이다.
- [ ] Step 9 — release manager와 map-product profile을 Circled Wiki의 절차 수준으로 보완한다. `prepare-release`는 실제 validation command·exit result를 받아 실행·기록하고, compatibility/breaking/migration/rollback condition/release note를 갖춘 manifest와 release receipt를 만든다. `deploy`는 `dry-run` 산출물, 명시 승인 정보, rollback 책임자 없이는 apply하지 않으며, 대상 `.mpa-workspace/history/releases/<release-id>.json`에 manifest asset map·적용 결과를 기록한다. rollback 실패도 receipt로 남긴다. / 이유: asset hash만으로는 대상 적용의 안전 조건과 호환성 판단을 재현할 수 없다.
- [ ] Step 10 — installation·issue lifecycle을 보완한다. 최초 설치 전 Python/runtime dependency·launcher smoke·기존 설정 보존 조건을 dry-run으로 확인하고, issue intake는 archive 유사 이력 후보를 제시한다. triage는 재현성·영향·우선순위·관계·후속 task를 기록하며, resolve/archive는 release·deployment·독립 검증 근거와 일치해야 한다. / 이유: 검토됨과 해결됨, 설치 가능과 안전한 적용을 구분해야 한다.
- [ ] Step 11 — `MAP_PRODUCT_RULES.md`와 모든 `map-product-rules/*.md`를 `Trigger / Input / Allowed Actions / Checks / Gates / Output / Failure State / Prohibited` 구조로 정규화하고, README·install.md·guidebook에 신규 release/deploy/rollback/dry-run 절차를 반영한다. / 이유: source 전용 운영 절차가 Runtime 규칙보다 먼저 일관되게 적용돼야 한다.
- [ ] Step 12 — 확장된 테스트를 추가한다. validation command 실패 시 manifest/receipt 미생성, 누락된 release metadata 거부, dry-run/approval/rollback owner 부재 시 apply 거부, target history와 deployment receipt·manifest 일치, rollback 실패 receipt, dependency/smoke 실패의 최초 설치 중단, issue 관계·needs_information 유지·근거 불일치 archive 거부를 검증한다. / 이유: 새 Gate가 문자열 문서에만 남으면 기존의 안전 경계와 충돌할 수 있다.

### 예상 조용한 결정

- release ID: allowlist asset map의 정규화된 상대 경로·SHA-256 값만 해시한다. Git 식별자, 대상 프로젝트, backup 경로, 사용자 데이터는 ID 입력에서 제외한다.
- Git 범위 처리: `git diff`는 allowlist·설치/배포 도구 경로로 제한한다. 범위 밖 dirty 파일은 무시하고, Git 실행 실패·저장소 부재만 `source.git` 메타데이터에 `unavailable`로 남긴다. release 관련 변경은 manifest asset map과 scoped diff 양쪽에 기록한다.
- release 검증: validation command는 shell 없이 명시된 실행 파일·인자 목록으로 저장하고 종료 코드·표준 출력 요약·실행 시각을 receipt에 기록한다. 검증 실패 시 manifest/package/receipt를 생성하지 않는다.
- deployment 승인: `approved_by`, approval reference, rollback owner는 필수 값이며 dry-run 결과의 release ID·target·asset map과 실제 apply 입력이 정확히 같아야 한다.
- 대상 history: source release manifest를 복사하지 않고, release ID·manifest 경로·asset map·backup·applied/rolled_back 상태와 검증 결과만 `.mpa-workspace/history/releases/`에 기록한다. 이 history는 Runtime update 관리 파일로 배포 자산에는 포함하지 않는다.
- backup 범위: 대상 `.mpa-workspace/`만 보관한다. `workspace/`, agent 설정, 임의 설정, 일반 소스 파일은 backup·읽기·덮어쓰기 대상에서 제외한다.
- issue 수집: copy 후 delete가 아닌 동일 파일시스템에서는 rename, 다른 파일시스템에서는 임시 목적지+원본 보존 확인을 사용하는 원자적 이동으로 구현한다.
- 민감정보 검사: credential 형태와 절대 경로를 휴리스틱으로 거부하며, 애매한 경우 자동 마스킹하지 않고 사용자에게 수정 요청한다.

### 수정 대상 파일

| 파일 경로 | 변경 내용 |
|---|---|
| `workspace/memory/shared/architecture.md` | 파일 영역별 소유자·복사 방향·release 포함 여부를 SSOT로 정리 |
| `AGENTS.md` | map-product → Runtime 순의 source 전용 진입점으로 갱신 |
| `.mpa-workspace/upgrade-candidates/` · `dist/.mpa-workspace/upgrade-candidates/` | 기존 후보·archive를 issue로 이관한 뒤 경로 제거 |
| `.mpa-workspace/core/agent_rules.md` · `inject/{layer1_design,layer1_implement,layer2_checkpoint}.md` · `templates/{docs_template,plan_template}.md` | `workspace/docs/` 참조를 사용자 제공 루트 `docs/`로 정정 |
| `release_manager.py` | runtime release/receipt/deploy/rollback 및 issue lifecycle CLI 신규 구현 |
| `install.py` | upgrade-candidates 자동 이전·초기화와 전체 upgrade 로직 제거; 최초 설치 전용 도구로 정리 |
| `MAP_PRODUCT_RULES.md` | map-product 운영 불변식 신규 정의 |
| `map-product-rules/{installation,issue-intake,issue-triage,release-preparation,deployment-coordination}.md` | map-product 전용 설치·업데이트·이슈·릴리스 단계별 운영 프로필 신규 정의 |
| `.mpa-workspace/core/agent_rules.md` | 이슈·릴리스·배포 요청 라우팅과 기본 안전 경계 |
| `.mpa-workspace/core/agent_rules_detail.md` | release preparation, deployment coordination, issue intake/triage 상세 절차 |
| `.mpa-workspace/inject/{discussion_mode,layer0_update,layer1_critique,layer1_design,layer1_implement,layer1_review,layer2_checkpoint}.md` | issue lifecycle·문서 경로·source/Runtime 경계로 이관 |
| `.mpa-workspace/templates/{docs_template,knowledge_template,plan_template}.md` | 루트 docs 경로와 issue lifecycle으로 이관 |
| `workspace/project_rules.md` | upgrade-candidates 반영 워크플로우를 source issue review·triage 흐름으로 교체 |
| `.mpa-workspace/templates/issue_template.md` | 로컬 관찰 issue 템플릿 신규 |
| `dist/workspace/issues/README.md` | 신규 설치에만 제공되는 issue 경로·수명주기 설명 (release asset 제외) |
| `workspace/issues/{README.md,inbox/,archived/}` | source 저장소의 명시적 회수함·archive·receipt 연결 운영 구조 |
| `workspace/tasks/INDEX.md` | active 태스크 등록 |
| `.mpa-workspace/.mpa-version` | 방법론 의미 변경 후 current_version 갱신 |

### 참고 파일 (수정 없음)

- `dist/.mpa-workspace/**` — `.mpa-workspace/` 변경의 자동 미러 산출물
- `workspace/project_rules.md` — MPA 시스템 파일 수정·dist 동기화 원칙
- `/Users/kjkim/Study/circled-wiki/product-agent-rules/release-preparation.md` — release/manifest/receipt 경계 참고
- `/Users/kjkim/Study/circled-wiki/product-agent-rules/deployment-coordination.md` — 대상별 배포·rollback·verification 경계 참고
- `/Users/kjkim/Study/circled-wiki/product-agent-rules/operational-issue-intake.md` — 명시적 수집·원자 이동·사용자 검토 Gate 참고
- `/Users/kjkim/Study/circled-wiki/product-agent-rules/system-issue-triage.md` — issue 분류·해결 근거 연결 참고

### 반례 (이 계획이 실패할 수 있는 시나리오)

- 시나리오 1: `workspace/`·agent-specs·install 도구까지 release asset map에 포함하면 프로젝트마다 다른 초기 골격·설치 도구 수정 때문에 같은 MPA 변경이 서로 다른 release로 식별되고, 배포가 사용자 영역을 건드릴 수 있다. → 구현 1·2단계에 포함: allowlist와 적용 범위를 `dist/.mpa-workspace/` 관리 자산으로만 한정한다.
- 시나리오 2: 기존 `upgrade-candidates`를 경로만 삭제하면 아직 처리되지 않은 방법론 개선 제안과 archive 이력이 유실된다. → 구현 1·7·8단계에 포함: 각 항목을 `methodology_improvement` issue로 이관·검증한 뒤에만 legacy 경로를 제거한다.
- 시나리오 3: 루트 `docs/`가 아직 없는 대상에서 Runtime 참조만 바꾸면 문서 작성 시 실패할 수 있다. → 구현 1·7·8단계에 포함: `docs/`는 사용자가 미리 만든다는 전제를 명시하고, 이 태스크는 경로 참조만 정정하며 이동·생성·배포를 하지 않는다.
- 시나리오 4: map-product 운영 규칙을 `.mpa-workspace`에 남기면 대상 프로젝트가 존재하지 않는 source 경로·권한을 전제하거나 임의의 release/deploy를 시도한다. → 구현 1·7·8단계에 포함: map-product/Runtime 진입점을 분리하고 Runtime에 map-product 전용 용어·경로가 없는지 검증한다.
- 시나리오 5: source에서 제거한 Runtime 파일이 자동 동기화의 제외·삭제 미지원 때문에 `dist/.mpa-workspace/`에 남아 다음 release에 포함된다. → 구현 2·8단계에 포함: 명시적 `sync-runtime`이 `.mpa-workspace/`와 대응 dist 경로 안에서만 prune하는지 검증한다.
- 시나리오 6: 전체 작업 트리에 Git diff를 적용하면 release와 관계없는 문서·실험 파일 수정에도 배포가 차단된다. → 구현 2·8단계에 포함: Git diff를 release allowlist로 한정하고, 범위 밖 dirty 파일과 Git 없음/오류를 테스트한다.
- 시나리오 7: 기존 설치본에서 `install.py`가 자동 upgrade를 계속 수행하면 Runtime update가 workspace·agent 설정까지 변경한다. → 구현 3·7·8단계에 포함: 기존 설치본은 install을 거부하고 release deployment 또는 명시적 installation refresh로만 진행되게 검증한다.
- 시나리오 8: deployment가 `workspace/`·agent 설정까지 건드리거나 backup에 넣으면 배포 후 생성된 사용자 task·memory 및 사용자 설정에 영향을 줄 수 있다. → 구현 4·8단계에 포함: `.mpa-workspace/`만 snapshot·교체하며 나머지 경로 무접근을 검증한다.
- 시나리오 9: issue 수집이 copy→delete 또는 수집 후 metadata 기록 실패 방식이면 원본·중앙본이 동시에 남거나 둘 다 유실될 수 있다. → 구현 5·8단계에 포함: 이동 실패 시 원본 존재를 확인하고 metadata 실패 시 원복하는 원자 전이를 테스트한다.
- 시나리오 10: archive가 triage만으로 허용되면 배포되지 않은 수정도 해결됨으로 표시된다. → 구현 6·8단계에 포함: resolved archive에 release/deployment/verification receipt 연결을 필수화한다.

---

## 완료 기준 (Definition of Done)

### 검증 체크리스트

- [ ] 정상 경로: 변경된 `.mpa-workspace` allowlist 자산으로 release manifest·receipt를 만들고, 명시된 대상 `.mpa-workspace/`에만 backup 후 배포·검증 receipt를 남긴 뒤 rollback할 수 있다.
- [ ] 실패 경로: `.mpa-workspace` allowlist 밖 자산, 존재하지 않는 manifest, backup 실패, 해시 불일치, 승인·review receipt 없는 issue 전이, archive 대상 충돌은 원본·대상 상태를 보존하고 실패를 보고한다.
- [ ] 엣지 케이스: release 범위 밖 파일이 dirty이거나 Git이 없거나 오류여도 release는 파일 해시로 생성되며, issue 수집은 중복·민감정보·절대경로를 거부하고 `workspace/`, agent 설정, 일반 소스는 deploy/rollback 뒤에도 전혀 변경되지 않는다.
- [ ] Circled Wiki 비교 보완: validation 실패·manifest metadata 누락·dry-run 또는 명시 승인/rollback owner 부재·target history 불일치·rollback 실패·dependency/smoke 실패·issue 근거 불일치가 각각 안전하게 중단되고 receipt 또는 inbox 상태로 남는다.

### 완료 시 문서 업데이트 대상

- [ ] `README.md` — release manager 사용법과 Git의 선택적 역할을 추가
- [ ] `guidebook/guidebook.md` — MPA release/deployment/issue lifecycle과 보존 경계를 추가

### 구현 후 발견

| 항목 | 유형 | 발견 맥락 | 처리 경로 |
|---|---|---|---|
| (구현 후 채움) | 조정 / 계획 확장 / 신규 태스크 | 왜 보기 전에는 보이지 않았는가 | plan.md 수정 / INDEX.md 등록 |

**파생된 태스크:**
- (신규 태스크 생성 시 여기에 추가됨)
