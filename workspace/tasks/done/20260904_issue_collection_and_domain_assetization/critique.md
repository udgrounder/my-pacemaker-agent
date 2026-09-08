## 비평 결과

### 🚨 실패 시나리오

- credential 검사보다 경로 정규화가 먼저 실행되면 `/Users/name/token-abc/...`, credential이 포함된 URL·DSN·query string, private-key 파일 내용 같은 민감 정보가 placeholder에 가려져 강제 거부를 통과할 수 있다. 반대로 raw 본문만 검사하면 안전한 placeholder 결과를 만들 수 있어도 사용자명·`password`라는 일반 경로명 때문에 과잉 차단될 수 있다. raw/normalized 중 무엇을 어떤 순서로 검사하는지, 어느 한쪽 검사가 실패하면 어떻게 처리하는지가 없다.
- “credential-like”의 문법이 없다. URL userinfo, bearer/API key, PEM, SSH private key, cloud credential, JSON/YAML의 secret 필드, 줄바꿈·URL encoding·base64·문자열 연결로 표현된 값 중 무엇을 강제 거부하는지 결정되지 않아 생성기와 collector가 같은 계약을 구현할 수 없다. dry-run의 차단 사유나 로그가 발견한 credential 일부를 다시 노출하는 실패도 다루지 않는다.
- 절대 경로 치환은 POSIX 경로만 상정한 것으로 보인다. Windows drive/UNC, `file://`, WSL, `~`, 심볼릭 링크 경로, 공백·이스케이프·따옴표, stack trace의 `path:line:column`, JSON 문자열, `/project`와 `/project-other`의 prefix 충돌, case sensitivity를 다루지 않으면 경로가 남거나 정상 텍스트가 훼손된다.
- 프로젝트 밖 경로를 전부 `<redacted-path>/...`로 바꾸면 서로 다른 외부 경로가 같은 정규화 본문과 identity로 충돌할 수 있다. 반대로 하위 경로를 그대로 보존하면 사용자명, 조직명, mount 이름 등 machine-identifying 정보가 남는다. “의미 보존”과 “로컬 정보 제거”를 동시에 만족시키는 보존 단위가 정의되지 않았다.
- placeholder가 이미 들어간 문서를 다시 처리할 때의 멱등성이 없다. `<project-root>/...`를 다시 절대 경로처럼 인식하거나 slash·line ending을 달리 정규화하면 dry-run과 deploy가 서로 다른 identity를 계산할 수 있다.
- source와 destination이 다른 filesystem이면 rename은 원자적이지 않다. 임시 파일 생성, byte-for-byte 검증, fsync, no-clobber publish, source 재검증, source 제거 순서와 crash recovery marker가 없어서 프로세스 종료 시 destination만 남거나 양쪽 모두 손실될 수 있다.
- preflight 이후 source가 수정·교체·symlink 전환되는 TOCTOU가 가능하다. dry-run 후 변경 테스트만 언급했을 뿐 raw hash, inode/file identity, size, stat, symlink 거부 여부를 어떤 시점에 다시 묶는지 없다. 복사한 버전과 삭제한 버전이 달라질 수 있다.
- destination 작성 뒤 source 제거가 실패한 경우 “destination을 정리”한다는 규칙과 “원본이 재생성되면 두 파일을 보존”한다는 반례 대응이 충돌한다. 어느 상태가 성공·실패·수동조정인지, 다음 실행이 중복으로 판단할지 정해지지 않아 영구적인 반수집 상태를 만든다.
- destination 충돌이 동일 identity인 경우와 다른 내용인 경우의 처리가 없다. “덮어쓰기 금지”만으로는 이미 수집된 동일 이슈를 성공으로 간주해 source를 제거할지, 중복으로 거부해 source를 보존할지 결정할 수 없다.
- issue 수집과 Runtime 배포가 하나의 transaction인 것처럼 서술되지만 서로 다른 프로젝트와 filesystem에 걸친 원자 rollback은 불가능하다. issue 이동 뒤 Runtime 교체가 실패하거나 Runtime 교체 뒤 receipt 기록이 실패할 때 issue를 되돌리는지, 배포만 rollback하는지, 어떤 순서로 commit하는지 없다.
- “차단 후보가 하나라도 있으면 deploy 중단”은 local issue 폴더에 잘못 분류된 메모 하나만 놓아도 Runtime 보안 패치 배포 전체를 막는 denial-of-service가 된다. 허용 kind가 아닌 파일을 inventory에서 무시·보고·차단 중 무엇으로 처리할지 구분하지 않았다.
- deploy가 dry-run과 “동일 inventory와 결과”를 재검증한다는 표현은 신규 파일 추가, 기존 파일 제거, 목적지 상태 변경, scanner/policy 버전 변경을 만났을 때의 의미가 없다. 새 snapshot으로 자동 진행하면 사용자가 보지 않은 후보가 이동되고, 무조건 중단하면 무관한 파일 추가가 배포를 계속 방해한다.
- 배포 요청이 곧 issue 이동 승인인지 불명확하다. 변경 불가 제약은 명시 요청 또는 승인된 update batch 없이 중앙 이동을 금지하지만 Step 4는 deploy가 후보를 수집하는 흐름을 전제한다. dry-run token에 수집 승인 범위가 결박되지 않으면 배포 권한이 수집 권한으로 확대된다.
- 마지막 단계의 `release-audit`은 기존 immutable bundle을 검사할 뿐 새 source Runtime을 담은 release를 만들지 않는 한 이번 Runtime 변경을 감사하지 못한다. release 생성은 제외 범위이므로 “release audit 통과”가 신규 변경 검증이라는 완료 기준은 현재 architecture 계약상 성립하지 않는다.
- 실제 재현 이슈의 대상 프로젝트 절대 위치, target-ref/fingerprint, 접근 가능성, 수집 승인 batch가 계획에 없다. 구현이 끝나도 `campingtalk-proj/...`라는 서술만으로는 지정 원본을 안전하게 식별하거나 다른 동명 프로젝트를 배제할 수 없다.

### ⚠️ 숨은 가정

- `kind: methodology_improvement`라는 자기 선언이 내용의 실제 성격을 보장한다고 가정한다. 프로젝트 기능 버그가 kind만 바꿔 중앙 유입되는 것을 막을 content validation 또는 사용자 triage 경계가 없다.
- `methodology_improvement`의 판정 기준이 자명하다고 가정한다. Runtime hook 결함, agent 행동 규칙, 설치기 결함, map-product 운영 도구 결함, 재사용 가능한 역할 함정 중 어디까지가 방법론인지 정의되지 않았다. 바로 재현 사례인 `codeGateHookCwdDrift`조차 프로젝트 버그와 Runtime 방법론 결함의 경계 판정 규칙이 없다.
- “프로젝트 기능 보완·아키텍처 결정·역할 함정·도메인 지식”이 `tasks/docs/memory` 중 어디로 가는지 에이전트가 일관되게 판단할 수 있다고 가정한다. 우선순위, 중복 기록, 기존 파일과 병합 방식, 잘못 기록했을 때 정정 절차가 없다.
- 발견 즉시 `workspace/memory/domains/<domain>/rules.md`에 쓰는 것이 안전하다고 가정한다. 관찰이 검증 사실인지, domain slug가 무엇인지, 파일이 없을 때 생성할 schema, 기존 규칙과 충돌할 때의 병합·승인, 출처·신뢰도 표기가 없다. 검증되지 않은 추측이 다음 세션의 primary source가 될 수 있다.
- 새 주제 도메인을 memory에 만들면서 architecture가 요구하는 `project_identity.md`의 “가용 도메인 집합”도 함께 갱신된다고 가정한다. 계획과 수정 대상에는 이 동기화가 명시되지 않아 기록은 생겨도 inject가 해당 도메인을 활성화하지 못할 수 있다.
- project memory와 Runtime knowledge가 같은 사실에 대해 충돌하지 않는다고 가정한다. 읽기 우선순위, local override 여부, stale knowledge 표시, provenance가 없어서 보존된 공용 knowledge가 더 최신인 프로젝트 memory를 덮거나 그 반대가 될 수 있다.
- 기존 Runtime knowledge는 계속 읽히면서 신규 승격 경로를 제거해도 장기 유지가 가능하다고 가정한다. “명시 큐레이션 요청”은 이번 범위에서 구현하지 않으므로 수정·폐기·충돌 해소의 실제 진입점이 사라진다.
- normalized identity가 “본문”만으로 충분하다고 가정한다. title, source project fingerprint, kind, schema version, frontmatter, 첨부/참조, volatile timestamp 중 포함·제외 필드가 없다. 서로 다른 프로젝트의 같은 문구를 하나로 볼지 별개로 볼지도 정해지지 않았다.
- 기존 inbox/archive와 새 identity를 비교할 수 있다고 가정한다. 기존 항목에 identity가 없거나 구 알고리즘 identity가 있을 때 lazy 계산, dual lookup, schema versioning 없이 소급 재작성 금지와 중복 방지를 동시에 달성할 수 없다.
- Unicode normalization, newline, trailing whitespace, slash, placeholder 문법, frontmatter key order 같은 표현 차이를 정규화할 기준이 자명하다고 가정한다. 이 기준이 없으면 머신 독립 identity가 재현 가능하지 않다.
- 원본 “손실 없이 복원”이 본문 bytes만 의미한다고 가정한다. mode, ownership, xattr, timestamps, symlink 상태까지 보존해야 하는지 없으며, collector가 source를 직접 수정하지 않는다면 복원이라는 표현 자체가 어떤 실패 단계에 필요한지도 불명확하다.
- “기존 inbox·archive를 덮어쓰지 않는다”만 지키면 중앙 저장소의 동시 writer와 안전하게 공존한다고 가정한다. 두 collector가 동시에 같은 destination을 publish하거나 archive 이동과 경합하는 시나리오가 없다.
- Runtime의 `knowledge_promotion` 문자열 전체 검색으로 구 흐름 제거를 입증할 수 있다고 가정한다. 다른 이름의 승격 지시, persona/workflow/template 참조, 문맥상 동일한 지시를 검사하는 기준이 없다.

### ❓ 미해소 비가시적 위임

- credential signature 목록, entropy/encoding 처리, false positive 예외, 탐지 버전과 실패 메시지의 비밀 비노출 형식을 구현자에게 위임했다.
- 절대 경로 lexer와 canonical root 판정 방식, 외부 경로에서 보존할 suffix 깊이, 파일명 자체가 민감할 때의 처리, placeholder의 escaping·멱등 규칙을 구현자에게 위임했다.
- normalization pipeline의 순서와 identity schema/algorithm/version, 기존 identity 호환, collision 처리, destination filename 생성 규칙을 구현자에게 위임했다.
- issue 후보 inventory의 정확한 범위가 없다. recursive 여부, 확장자, hidden/temp 파일, symlink, malformed frontmatter, 읽기 권한 실패를 후보·차단·무시 중 어디로 볼지 구현자가 결정하게 된다.
- `methodology_improvement` 판정이 schema validation인지 내용 triage인지, 누가 최종 권위를 갖는지, 잘못된 후보를 collector가 자동 라우팅하는지 단지 거부하는지 결정되지 않았다.
- “안전한 상대 정보”, “구체적 사유”, “의미 보존”은 검증 가능한 계약이 아니다. 로그에 허용되는 project ref·filename·line number·hash prefix와 금지되는 정보 목록이 필요하다.
- dry-run 결과의 저장 위치, snapshot ID, 유효 기간, 승인 주체, deploy 시 bind할 target fingerprint·source hash·destination state·policy version이 결정되지 않았다.
- batch 일부가 blocked일 때 전체 실패 외에 collectable 후보의 상태, 재시도 시 inventory, 이미 수집된 항목의 idempotent 결과를 누가 어떻게 해석할지 미정이다.
- memory 자산화의 편집 권한과 사용자 게이트, 검증 수준, provenance, 충돌 병합, 잘못된 지식 철회는 구현자가 암묵적으로 설계해야 한다.
- 기존 `runtime/knowledge`의 읽기 소비자 목록과 새 project memory와의 precedence를 조사·명세하는 책임이 “참조 체인 대조” 한 문장에 숨겨져 있다.
- 실제 차단 이슈 수집은 외부 프로젝트를 변경하는 별도 operation인데, exact target과 승인 artifact 없이 Step 6 구현자에게 대상 식별과 권한 판단을 맡긴다.

### 🔧 구조적 문제

- Step 1·2가 producer 규칙을 먼저 변경하고 Step 3에서야 collector의 canonical contract를 정한다. contract/schema와 실패 의미를 먼저 고정하고 테스트 fixture를 만든 뒤 producer와 collector를 맞춰야 중간 설계가 서로 다른 해석으로 갈라지지 않는다.
- architecture 변경이 Step 6의 문서 동기화로 밀려 있다. 이번 작업은 memory/knowledge/issue 소유 경계를 바꾸는 architecture 결정이 핵심인데, 구현 뒤 문서화 순서는 구현자가 미결정 정책을 코드로 확정하게 만든다.
- Runtime 생성 규칙, source collector, deploy orchestration, project memory governance, knowledge lifecycle을 한 major 작업의 단일 순차 구현으로 묶었다. 각 영역의 불변조건과 transaction 경계가 다르지만 단계별 승인 가능한 계약 산출물이나 독립 검증 gate가 없다.
- manual collection과 deployment update batch의 공통 preflight를 요구하면서도 두 command의 authority와 side effect 차이를 모델링하지 않았다. 공통 pure normalization/validation과 command별 authorization/commit을 분리하지 않으면 deploy가 수집 권한을 우회하는 구조가 된다.
- “원자 수집”의 transaction 범위가 파일 이동만인지 metadata, inventory, receipt, Runtime deploy까지인지 없다. rollback 테스트를 추가한다는 말로는 commit point와 복구 불변조건을 대신할 수 없다.
- 방법론 전용 수집 정책과 잘못된 후보의 project-local 자산화가 같은 경계에 섞여 있다. 중앙 collector가 project memory를 수정하면 대상 사용자 데이터 보존 경계를 침범하고, 수정하지 않으면 완료 기준의 “라우팅된다”는 표현은 단순 거부 이상의 보장을 하지 못한다.
- Layer 2에서 knowledge promotion을 제거하고 project memory 정합성 확인으로 대체하지만, 무엇을 비교하고 어떤 불일치를 어떻게 해소하는지 workflow가 없다. 단순 참조 삭제는 project memory 품질 관리나 Runtime knowledge와의 충돌 검출을 제공하지 않는다.
- `.mpa/runtime/knowledge/`를 “읽기 자산”으로 보존한다는 것은 architecture의 기존 “upgrade-candidates 승인 후 승격” 계약을 폐기하는 변경이다. 그런데 폐기 후 authoritative cross-project fact의 생성·갱신·retirement lifecycle은 제외 범위라 저장소가 사실상 동결된 채 소비만 계속되는 불완전 상태가 된다.
- 테스트 목록이 범주만 나열하고 oracle을 정의하지 않는다. 특히 encoded credential, path 안의 credential, Windows/UNC/file URI, component-prefix root, symlink, Unicode/newline identity, concurrent collector, cross-filesystem crash, fsync/publish 실패, destination 동시 생성, rollback 자체 실패, 로그 비밀 유출이 빠져 있다.
- 완료 기준의 “source Runtime·dist 동기화와 전체 테스트·release audit”은 신규 release를 만들지 않는 제약과 맞지 않는다. 새 Runtime asset을 대상으로 하는 별도 temporary-package audit 계약을 추가하거나 release audit 요구를 분리해야 한다.
- 운영 안내의 “credential은 원본을 수정한 뒤 재수집”은 collector가 원본을 보존한다는 규칙과 행위 주체가 구분되지 않는다. 사용자가 수동 수정하는 것인지 도구가 수정하는 것인지 명시하지 않으면 강제 거부 후 자동 정제 금지 원칙이 다시 깨질 수 있다.
