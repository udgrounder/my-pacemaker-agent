---
태스크: release_deployment_management
생성일: 2026-08-05
타입: major
실패비용: major
상태: 구현 중
승인해시: 23cb0d7d250cb40d
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
- source 저장소의 회수함은 `workspace/issues/`다. 명시적 수집 또는 Runtime 업데이트의 수집 단계가 `workspace/issues/inbox/<project-ref>/`에 넣고, 처리 완료 후에는 `workspace/issues/archived/YYYY/MM/<project-ref>/`로 이동한다. 이 경로는 배포·신규 설치 골격에 포함하지 않는다.
- 기존 `upgrade-candidates`는 폐기하고 issue의 `methodology_improvement` 분류로 이관한다. 새 후보는 `.mpa-workspace/`가 아니라 프로젝트 소유 `workspace/issues/`에 생성하고, source 저장소로의 수집은 명시적 요청일 때만 실행한다.
- `docs/`는 프로젝트 루트의 사용자 소유 문서 경로다. 단, `docs/INDEX.md`는 agent가 관리하는 색인 예외 파일로, 최초 설치·Runtime 업데이트 시 없으면 생성하고 문서 생성·갱신 후 agent가 갱신한다. 일반 문서 내용·이동·삭제는 사용자 소유이며 배포 자산에 포함하지 않는다.
- **map-product plane**(`MAP_PRODUCT_RULES.md`, `map-product-rules/`, `release_manager.py`, `install.py`, `agent-specs/`, source `workspace/`, `docs/`)은 이 저장소의 이슈 회수·릴리스·배포·설치 정책을 관리하며 배포하지 않는다. **Runtime/deployment plane**(`.mpa-workspace/` → `dist/.mpa-workspace/`)은 대상 프로젝트에 공통으로 적용할 규칙·정책·실행 소스만 관리한다. 대상 프로젝트의 `workspace/`·`docs/`는 사용자 소유 데이터다.
- source 저장소의 `AGENTS.md`는 `MAP_PRODUCT_RULES.md`를 Runtime 규칙보다 먼저 로드한다. map-product route가 이슈 회수·review/triage·릴리스 준비·배포·rollback 요청을 먼저 처리하고, 그 밖의 대상 프로젝트 작업만 Runtime `agent_rules.md`에 위임한다.
- **최초 설치**는 `install.py`가 명시된 빈 대상에 `.mpa-workspace/`, `dist/workspace/`의 초기 골격, agent 진입 설정을 한 번만 설치한다. **Runtime 업데이트**는 준비된 release manifest를 입력으로 `release_manager.py deploy`가 대상 `workspace/issues/`의 수집 후보를 먼저 확인하고, Runtime 검증 성공 후 수집 receipt를 기록하면서 승인된 issue를 source 저장소 `workspace/issues/inbox/<project-ref>/`로 원자 이동해 대상 원본을 정리한 뒤 대상 `.mpa-workspace/`만 backup·교체한다. `install.py --upgrade`의 기존 전체 교체 경로는 Runtime 업데이트에 사용하지 않으며, 설치 도구·agent 설정 변경은 기존 설치본에 자동 적용하지 않는다.
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
- Circled Wiki의 장점인 버전 중심 release lineage, immutable manifest/receipt, 대상별 전환 이력과 사후 검증을 흡수한다. checksum·asset map은 버전 식별자가 아니라 해당 버전 배포물의 무결성 증빙으로 사용한다.
- Git clean worktree·커밋·push·revision 일치 검증은 도입하지 않는다. 단, 이용 가능한 경우 release 관련 allowlist 경로만 Git diff로 확인하고 Git source 식별자를 receipt에 보조 정보로 기록한다. 관계없는 dirty 파일은 무시한다.
- 배포 자산 allowlist, manifest, release receipt, deployment receipt, backup·rollback·보존 데이터 보호 원칙을 정의한다.
- 기존 `dist/` 단일 배포 소스와 신규 설치용 `install.py` 경로를 훼손하지 않는다. 단, release deployment는 `install.py --upgrade`를 호출하지 않고 `.mpa-workspace/`만 적용한다.
- 프로젝트 내부 이슈 생성, 명시적 수집, 사용자 검토, 원인 분류, 작업 연결, archive 이력을 지원한다.
- 수집 대상 이슈와 중앙 이슈는 중복 보관하지 않고, 민감정보·머신 절대 경로를 기록하지 않으며, 수집·분류·archive는 사용자 확인이 있어야 한다.
- `upgrade-candidates` 용어·경로·자동 이전/초기화 규칙을 `issues`로 전환하고, 방법론 개선은 issue 분류값으로 표현한다.
- Runtime 규칙·템플릿의 문서 경로를 루트 `docs/`로 통일한다. `docs/` 이동·생성·배포는 수행하지 않는다.
- source 전용 map-product 규칙·프로필과 배포 전용 Runtime 규칙·실행 소스를 분리하고, 어느 파일도 두 영역을 동시에 소유하지 않게 한다.
- 최초 설치, Runtime 업데이트, installation tooling 갱신을 서로 다른 입력·적용 범위·rollback 책임으로 정의한다.
- Runtime 업데이트는 대상의 미수집 issue를 수집·원본 정리까지 포함한 하나의 운영 절차로 정의한다. 수집 대상이 없으면 issue 단계는 no-op이며, 수집 실패·검증 실패·사용자 보류 issue는 원본을 보존한다.

---

## 구현 계획 (Implementation Plan)

### 계획 사용법

이 문서는 **재승인할 설계 원본**이고, 세부 작업의 완료 표시는 [`TODO.md`](TODO.md)만 사용한다. 각 TODO는 구현·테스트·명령 출력의 세 근거가 갖춰질 때만 완료로 바꾼다. 과거의 중복 Step 번호와 추정 완료 표시는 삭제했다.

### 현재 기준선

기반 구현으로 `sync-runtime`, immutable package/manifest/receipt, deployment dry-run, deploy/rollback, issue create/collect/review/triage/resolve/archive, 최초 설치 dry-run이 존재한다. 다만 아래 표의 계약을 아직 완성·검증하지 않았으므로, 이 기반 기능만으로 완료 판정을 하지 않는다.

| 비교 기준 | Circled Wiki 절차 | 현재 MPA의 부족점 | 보완 원칙 |
|---|---|---|---|
| Version lineage | source revision과 release manifest로 사람이 읽을 수 있는 릴리스 전환을 추적 | `mpa-<asset-hash>`가 사실상 버전이며 `.mpa-version`은 deployment lifecycle에 참여하지 않음 | 선언 Runtime 버전을 primary identity로 하고 `from_version → to_version` 이력을 남긴다. Git revision은 선택적 보조 정보로만 둔다. |
| Release 준비 | validation·allowlist·manifest·receipt를 하나의 실패-원자 절차로 처리 | 과거 artifact migration, validation 결과와 receipt 참조 검증이 부족 | legacy를 명시 분리하고 active schema·receipt 무결성을 audit한다 |
| Deployment | release receipt, dry-run, backup, verification을 대상별로 기록 | dry-run 만료·대상 map/history 재검증과 상태 전이가 불완전 | apply 전후 asset map과 receipt 관계를 확인한다 |
| Installation | dependency·launcher·보존 영역을 dry-run에서 판정 | 현재 dry-run은 파일 존재 확인 중심 | 구조화된 계획과 hook smoke, 보존 테스트를 추가한다 |
| Issue lifecycle | canonical key·발생 정보·검토·archive 근거를 기록 | cross-filesystem 이동/receipt 실패 원복과 정상 전이 증빙 부족 | 원자 이동과 evidence referential integrity를 강제한다 |
| 운영 문서 | source 정책과 Runtime 정책을 분리 | CLI·profile·사용자 문서의 행 단위 계약 검증 부족 | 한 계약표를 기준으로 문서와 테스트를 대조한다 |

> **의도적 차이:** Circled Wiki의 clean worktree·commit Gate와 intake 원본 Git Gate는 도입하지 않는다. 사용자가 정한 대로 scoped Git 식별은 receipt 보조 정보로만 남기며, 관계없는 dirty 파일은 release/intake를 차단하지 않는다.

### 범위·소유권

| 영역 | 소유자 | 허용 작업 | release 포함 |
|---|---|---|---|
| `map-product` (`release_manager.py`, `install.py`, `MAP_PRODUCT_RULES.md`, `map-product-rules/`, source `workspace/`) | 이 저장소 | release·deploy·installation refresh·issue 회수 정책 | 아니오 |
| Runtime (`.mpa-workspace/` → `dist/.mpa-workspace/`) | 대상 프로젝트 | 공통 규칙·템플릿·hooks | 예, 이 경로만 |
| 설치 골격 (`dist/workspace/`) | 최초 설치 대상 | 빈 초기 구조만 제공 | 아니오 |
| 대상 `workspace/`, `docs/`, agent 설정·일반 소스 | 사용자 | 사용자 데이터와 설정. 단 `docs/INDEX.md`는 agent 관리 색인 | 아니오, deploy/rollback은 `docs/INDEX.md`가 없을 때만 생성 가능 |

`docs/`는 사용자가 프로젝트 루트에 준비한다. 이 작업은 `workspace/docs/` 참조를 `docs/`로 바꾸되, 문서를 이동·생성·배포하지 않는다. `upgrade-candidates`는 `methodology_improvement` issue로 이관하며, 새 issue는 프로젝트별 `workspace/issues/`에 만든다.

### 고정 안전 계약

| 영역 | 계약 |
|---|---|
| Validation | `--validation-command`는 shell을 실행하지 않는 argv JSON 배열로 받는다. timeout 120초, stdout/stderr는 각 4 KiB까지만 receipt에 저장한다. 실패·timeout이면 package/manifest/release receipt를 만들지 않는다. |
| Version identity | `.mpa-workspace/.mpa-version`의 선언 Runtime version은 release의 primary identity다. 같은 version에 서로 다른 package checksum/asset map을 연결하는 release는 거부한다. 재배포·rollback은 version과 immutable release receipt를 함께 참조한다. |
| Release artifact | active manifest는 `runtime_version`, immutable `release_id`, source snapshot(선택적 Git 보조 정보 포함), asset checksum/map, package, metadata, validation result, release receipt reference를 가져야 한다. asset checksum은 package 무결성 검증용이며 version을 대체하지 않는다. 과거 형식은 `legacy/`에만 두며 migration receipt로 사유를 연결한다. |
| Update issue intake | Runtime update는 없는 `workspace/`·`workspace/issues/`·루트 `docs/`만 생성하고, `docs/INDEX.md`가 없으면 agent 관리 색인 템플릿만 만든다. 이미 있는 docs·INDEX·일반 문서는 변경하지 않는다. dry-run은 대상 `workspace/issues/`의 수집 후보 key·상대 경로·checksum을 사용자에게 고지하고 기록한다. apply는 이 inventory를 재확인한 뒤 Runtime 검증 성공 후 자동 수집한다. 중앙 receipt 확정·원본 삭제를 하나의 이동으로 처리하고, 수집된 issue·원본 정리 결과 또는 실패·보류 사유를 사용자에게 고지한다. 실패·보류·재검증 불일치면 대상 원본을 보존한다. |
| Dry-run | dry-run에는 `from_version`, `to_version`, release ID, release receipt, target 절대 경로, target asset map, target history 상태, issue collection inventory, 생성 시각, 30분 만료 시각을 기록한다. apply 직전에 이 모든 값을 다시 확인하며 하나라도 달라지면 거부한다. |
| Target history | `history/releases/`는 대상 관리 이력이며 package asset map에서는 제외한다. deploy는 교체 전 history를 보존해 새 Runtime에 복사하고, history 파싱 실패·version/release ID 충돌은 apply 전에 중단한다. history와 receipt는 `from_version → to_version`, backup, verification을 함께 기록한다. backup에는 history를 포함한다. |
| Installation refresh | 별도 `installation-refresh --plan <receipt>`로만 실행한다. plan에는 대상, agent, 변경 allowlist, preserve 목록, backup, 승인 reference가 필수다. 일반 install과 Runtime deploy는 refresh를 호출하지 않는다. |
| Issue 이동 | 동일 파일시스템이면 rename, 다른 파일시스템이면 목적지 임시 파일→fsync→rename→원본 삭제 순서로 이동한다. receipt 기록 실패 시 destination을 원복하고 source 보존을 확인한다. |
| User review | review receipt에는 `approved_by`, `approval_ref`, `decision`을 기록한다. CLI actor만으로 사용자 확인을 대체하지 않으며 rejected는 archive/triage를 금지하고 inbox에 보존한다. |

### 실행 순서와 산출물

| 순서 | 작업 묶음 | 선행 조건 | 산출물 | 완료 증빙 |
|---|---|---|---|---|
| 1 | Versioned release artifact | 선언 Runtime version·Runtime source/dist 동기화 | version lineage, active/legacy inventory, migration receipt, schema audit | version↔manifest↔receipt↔package가 일대일이고 checksum은 무결성만 검증 |
| 2 | Deployment 상태 | 유효한 versioned release | from/to version dry-run, issue collection inventory, target history, applied/rolled_back/failed receipt | stale dry-run·version/history·issue inventory 충돌·검증 실패가 apply 전에 중단 |
| 3 | Installation 계약 | 설치 골격·agent spec | 구조화된 dry-run, smoke 결과, refresh plan | 기존 설치와 사용자 영역을 변경하지 않는 테스트 |
| 4 | Issue lifecycle | release/deployment evidence 형식 | canonical issue schema, 원자 이동, review/triage/resolve/archive receipt | 정상 전이와 실패 시 inbox/원본 보존 테스트 |
| 5 | 운영 정합성 | 1~4 구현 | profile·CLI·문서 계약표, 검증 보고 | source/dist sync, audit, 전체 테스트, dirty/No-Git 검사 |

실행 항목·입력·검증 명령은 [`TODO.md`](TODO.md)에 유지한다. 순서 5는 앞의 네 묶음이 모두 완료된 뒤에만 완료할 수 있다.

### 설계 결정

- 버전과 release ID: `.mpa-workspace/.mpa-version`의 `current_version`을 manifest·receipt·deployment history의 공식 `runtime_version`으로 사용한다. `release_id`는 그 version의 immutable release instance 식별자이고, asset map 해시만으로 version을 만들지 않는다. 같은 `runtime_version`으로 다른 package checksum/asset map을 준비하면 거부한다.
- checksum 역할: allowlist asset map의 정규화된 상대 경로·SHA-256 값은 package와 대상 Runtime의 무결성 검증에 사용한다. Git 식별자, 대상 프로젝트, backup 경로, 사용자 데이터는 checksum 입력에서 제외한다.
- Git 범위 처리: `git diff`는 allowlist·설치/배포 도구 경로로 제한한다. 범위 밖 dirty 파일은 무시하며 Git 없음·실패는 `source.git`에 `unavailable`로만 남긴다. Git은 어떤 Gate도 아니다.
- release 검증: validation command는 shell 없이 명시된 실행 파일·인자 목록으로 저장하고 종료 코드·표준 출력 요약·실행 시각을 receipt에 기록한다. 검증 실패 시 manifest/package/receipt를 생성하지 않는다.
- deployment 승인: `approved_by`, approval reference, rollback owner는 필수 값이며 dry-run 결과의 `from_version`·`to_version`·release ID·target·asset map과 실제 apply 입력이 정확히 같아야 한다.
- update issue collection: update가 지정된 대상 `workspace/issues/`를 검사해 후보 key·상대 경로·checksum을 dry-run 단계에서 사용자에게 고지하고 고정한다. Runtime 검증 후 중앙 `workspace/issues/inbox/<project-ref>/`로 자동 원자 수집하고 receipt가 확정된 항목만 대상 원본을 삭제한다. apply 완료 시 수집 목록·원본 정리 결과 또는 no-op/실패·보류 사유를 사용자에게 고지한다. inventory 변경은 원본을 보존하고 update completion을 실패로 보고한다.
- docs index ownership: `docs/INDEX.md`는 agent 관리 색인이다. 최초 설치·Runtime update는 파일이 없을 때만 템플릿을 생성하고, agent는 문서 산출물 생성·갱신 뒤 해당 색인을 갱신한다. 기존 INDEX 또는 일반 docs 파일을 배포·rollback이 덮어쓰거나 삭제하지 않는다.
- 대상 history: source release manifest를 복사하지 않고, `from_version`·`to_version`·release ID·manifest/receipt 경로·asset checksum/map·backup·applied/rolled_back 상태와 검증 결과를 `.mpa-workspace/history/releases/`에 기록한다. 이 history는 Runtime update 관리 파일로 배포 자산에는 포함하지 않는다.
- backup 범위: 대상 `.mpa-workspace/`만 보관한다. `workspace/`, agent 설정, 임의 설정, 일반 소스 파일은 backup·읽기·덮어쓰기 대상에서 제외한다.
- issue 수집: copy 후 delete가 아닌 동일 파일시스템에서는 rename, 다른 파일시스템에서는 임시 목적지+원본 보존 확인을 사용하는 원자적 이동으로 구현한다.
- 민감정보 검사: credential 형태와 절대 경로를 휴리스틱으로 거부하며, 애매한 경우 자동 마스킹하지 않고 사용자에게 수정 요청한다.

### 예상 수정 대상

| 파일 경로 | 변경 내용 |
|---|---|
| `workspace/memory/shared/architecture.md` | 파일 영역별 소유자·복사 방향·release 포함 여부를 SSOT로 정리 |
| `AGENTS.md` | map-product → Runtime 순의 source 전용 진입점으로 갱신 |
| `.mpa-workspace/` 및 `dist/.mpa-workspace/` | `upgrade-candidates` 제거, root `docs/` 참조, issue template 동기화 |
| `release_manager.py` | release schema/audit, deploy/rollback 상태, issue lifecycle CLI 보완 |
| `install.py` | 구조화 dry-run, smoke, 최초 설치·refresh 계약 보완 |
| `MAP_PRODUCT_RULES.md` | map-product 운영 불변식 신규 정의 |
| `map-product-rules/{installation,issue-intake,issue-triage,release-preparation,deployment-coordination}.md` | map-product 전용 설치·업데이트·이슈·릴리스 단계별 운영 프로필 신규 정의 |
| Runtime 규칙·inject·template | Runtime에는 로컬 issue·root `docs/`만 남기고 source 정책 참조 제거 |
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

### 주요 실패 시나리오와 대응

- release에 사용자 데이터가 섞임 → asset map과 deploy 범위를 `dist/.mpa-workspace/`와 대상 `.mpa-workspace/`로 고정한다.
- 관계없는 dirty 파일이 작업을 막음 → scoped Git은 receipt 보조 정보로만 쓰고 No-Git도 성공 경로로 검증한다.
- stale dry-run 또는 손상된 history로 덮어씀 → 만료·asset map·history를 apply 직전에 재검증한다.
- 업데이트 중 issue를 잃거나 중복 보관함 → 대상 issue inventory를 dry-run/apply에서 재검증하고, 중앙 receipt 확정 뒤에만 원본을 삭제한다. 실패·보류 항목은 대상에 남긴다.
- installation이 기존 설정을 바꿈 → 기존 설치는 거부하고, refresh는 승인된 plan의 allowlist만 적용한다.
- issue 이동 중 오류로 원본을 잃음 → rename 또는 임시 파일·fsync·rename·원복 절차와 실패 테스트를 강제한다.
- release와 무관한 issue를 archive함 → accepted review와 task·release·deployment·verification evidence의 참조 무결성을 확인한다.

---

## 완료 기준 (Definition of Done)

### 완료 검증 체크리스트

- [ ] Release: runtime version↔manifest↔receipt↔package 일대일성, argv validation의 성공·실패·timeout, active/legacy migration, schema/receipt audit을 검증한다.
- [ ] Deployment: valid `from_version → to_version` dry-run과 issue collection inventory만 apply하고, 대상 외 파일 보존·post-deploy verification·issue 원자 수집/원본 정리·rollback·실패 history/receipt를 검증한다.
- [ ] Installation: 구조화 dry-run·hook smoke와 기존 `.mpa-workspace`, `workspace`, `docs`, agent 설정의 무변경을 검증한다. 단 없는 `docs/INDEX.md`의 생성·agent 색인 갱신은 허용하며 기존 INDEX 내용은 보존하는지 검증한다.
- [ ] Issue: create→collect→review→triage→resolve→archive 정상 경로와 rejected/needs-information/중복/근거 불일치/이동 실패의 보존 경로를 검증한다.
- [ ] 운영 정합성: profile/CLI/doc matrix, source/dist sync, release audit, 전체 테스트, `git diff --check`, scoped dirty Git·No-Git을 검증한다.

### 완료 시 갱신할 문서

- [ ] `README.md` — release manager 사용법과 Git의 선택적 역할을 추가
- [ ] `guidebook/guidebook.md` — MPA release/deployment/issue lifecycle과 보존 경계를 추가

### 구현 후 발견 기록

| 항목 | 유형 | 발견 맥락 | 처리 경로 |
|---|---|---|---|
| (구현 후 채움) | 조정 / 계획 확장 / 신규 태스크 | 왜 보기 전에는 보이지 않았는가 | plan.md 수정 / INDEX.md 등록 |

**파생된 태스크:**
- (신규 태스크 생성 시 여기에 추가됨)
