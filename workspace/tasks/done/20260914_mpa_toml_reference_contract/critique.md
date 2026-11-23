## 비평 결과

### 🚨 실패 시나리오

1. **제한 parser가 TOML 파일의 유효성 판단을 독점해, 외부 소비자와 다른 문법을 받아들이거나 거부할 수 있다.** 계획은 table·문자열·배열·boolean만 지원한다고 하지만 dotted key, quoted key, escape, multiline string, trailing comma, 주석 위치, UTF-8 BOM, 배열 안의 허용 값, table 재선언의 정확한 규칙을 정하지 않는다. "지원하지 않는 구조"를 거부하는 구현은 이 빈칸을 구현자 판단으로 채우게 되고, 같은 파일을 표준 TOML 라이브러리로 읽는 외부 도구와 해석이 달라질 수 있다. 특히 `중복 key`는 TOML 표준 parser가 이미 거부하는 범위와 자체 parser의 범위가 다르기 쉽다. **수정 방향:** 계약 profile을 버전별 문법·타입·키 공간·허용/비허용 예시까지 규격화하고, parser는 그 profile의 단일 검사기로 한정한다. 독립적인 표준 TOML parser로 계약 샘플을 읽는 호환성 시험도 추가해 "우리 parser만 통과"하는 파일을 막아야 한다.

2. **계약 버전이 있어도 forward/backward compatibility 규칙이 없어 새 필드가 곧 장애가 된다.** 계획은 알 수 없는 구조를 거부하므로, producer가 선택 필드를 추가한 순간 이전 validator와 소비자는 전체 계약을 읽지 못한다. 반대로 version이 올라갔을 때 어떤 major/minor 변화가 허용되는지, 소비자가 지원하지 않는 version을 어떻게 실패해야 하는지도 없다. 이는 배포본이 오래 남는 Runtime 구조에서 현실적인 반례다. **수정 방향:** `contract_version`의 호환 정책, 필수/선택 키, 알 수 없는 키 처리, 지원 version 범위와 오류 코드를 명시한다. 새 계약을 추가하는 release와 과거 설치본 validator의 상호 운용 테스트를 둔다.

3. **Markdown과 TOML의 상태 전이가 의미상 어긋나도 존재 경로 검사만 통과할 수 있다.** 완료 기준은 TOML에 major/minor 상태 전이를 넣고 각 필드가 canonical Markdown 또는 hook 소유자를 가리키게 한다. 그러나 계획의 정합성 검사는 "대상 경로"와 "소유자 참조"를 검사할 뿐, TOML 전이와 `agent_rules.md`/`agent_rules_detail.md`의 실제 전이가 동치임을 어떤 규칙으로 판정할지 없다. 예를 들어 Markdown에 `검증 중 → 테스트 중` 조건이 추가돼도 TOML이 이전 목록을 유지하면 파일은 모두 존재하고 hook 동작도 유지되어 테스트가 녹색일 수 있다. **수정 방향:** 상태·기본 경로 각각에 대해 한쪽에서 기계적으로 추출 가능한 canonical fragment를 정하거나, 명시적 양방향 비교 fixture와 변경 책임자를 둔다. 단순 파일 링크가 아닌 값 단위 동치 검증이 필요하다.

4. **source에서만 검사한 뒤 dist에 복사하면 설치본 계약이 깨진 채 남을 수 있다.** 아키텍처는 `sync-runtime`과 source/runtime-dist parity를 Runtime 변경의 경계로 정하고, release preflight는 ZIP을 풀어 hook 문법과 asset map도 확인한다. 하지만 계획 5단계는 "source를 dist에 동기화"라고만 하며, dist의 계약 파일을 dist validator로 실행하고 source와 dist의 asset map·바이트/의미 동치를 검증하는 절차가 없다. sync 대상 누락, 새 `contracts/` 디렉터리 누락, dist의 오래된 validator 같은 오류가 source 테스트로 가려진다. **수정 방향:** sync 직후 dist 경로에서 validator를 실행하고 source/dist 계약·validator·문서 참조의 parity를 테스트 완료 기준에 넣는다. release/deploy는 하지 않더라도, release가 소비할 dist artifact 검증은 별도 명시한다.

5. **외부 소비자가 hook 상대 경로를 실행 인터페이스 또는 권한 증표로 오해할 수 있다.** 실행 문자열을 넣지 않는다는 조치는 충분하지 않다. `entrypoints`와 hook path를 안정적 계약으로 공개하면 소비자는 해당 파일을 호출해도 된다고 추론할 수 있고, 그 결과 현재 내부 hook의 인자·출력·부작용이 암묵적 public API가 된다. 계획은 읽기 전용이라고 서술할 뿐 경로별 `inspect-only`, `not-invokable`, 지원되는 소비 행위와 금지된 행위를 계약 자체에서 식별하지 않는다. **수정 방향:** 각 reference에 authority/usage class를 두고, 실행 가능 API와 단순 canonical-source pointer를 분리한다. guidebook에는 소비자가 수행할 수 있는 read/validate 범위, 지원하지 않는 실행·수정·승인 판단을 계약 versioning의 일부로 명시한다.

### ⚠️ 숨은 가정

1. **"Python 3.9에서 외부 의존성 없이"가 자체 TOML 구현의 유지 비용보다 안전하다는 가정이다.** Python 3.9에는 `tomllib`가 없다는 사실만으로 작은 parser가 안전하다는 결론은 나오지 않는다. 계약이 TOML이라는 이름을 쓰는 이상 프로파일 확장, 보안 경계, 오류 위치 보고, 표준 호환성을 지속적으로 유지할 소유자가 필요하다. **수정 방향:** parser의 허용 문법을 최소화한 이유와 변경 절차를 계약에 기록하고, 허용 profile을 넘어야 할 요구가 생길 때 표준 parser 도입/지원 Python 변경을 재설계하도록 명시한다.

2. **한국어 상태 문자열이 안정된 기계 식별자라는 가정이다.** 계획은 용어 분열을 피하려고 현 상태 문자열을 보존하지만, Markdown의 표시 문구·상태명 정비가 외부 소비자의 breaking change가 되는 순간을 다루지 않는다. 공백, 이모지, 괄호 같은 편집도 기계 키로는 의미 있는 변경이다. **수정 방향:** 사람이 보는 label과 계약 key의 역할을 분리하거나, 상태 문자열 자체를 protocol-stable로 선언하고 rename·deprecated·migration 정책을 세운다. major/minor 전이별 적용 범위도 명시한다.

3. **계약 파일의 위치만으로 외부 소비자가 올바른 Runtime을 발견할 수 있다는 가정이다.** 대상은 source 저장소가 아니라 설치 프로젝트이며, source-only `MAP_PRODUCT_RULES.md`와 release 정보는 배포되지 않는다. 외부 소비자가 `.mpa/runtime/contracts/agent_reference.toml`을 어떻게 발견하고, 여러 Runtime 버전·부분 설치·손상된 dist 중 어느 것을 신뢰하는지 계획에 없다. **수정 방향:** 설치본 기준 discovery path, Runtime/version 식별 방법, 파일 부재·손상 시의 안전한 처리와 source 전용 메타데이터를 사용하지 말아야 함을 계약 문서에 정의한다.

4. **경로 존재가 참조의 유효성을 뜻한다는 가정이다.** `../` 이탈만 막아도 symlink, 파일↔디렉터리 바뀜, rename된 section/anchor, hook 내부에서 추가로 요구하는 파일은 남는다. Markdown 참조는 현재 파일의 어느 section인지, stable anchor가 무엇인지도 계획에 없다. **수정 방향:** reference kind별 기대 대상(file/section/hook), 허용 root, symlink 정책, anchor 검증 방식을 정의하고 존재성 외의 실패 fixture를 넣는다.

### ❓ 미해소 비가시적 위임

1. **누가 semantic drift를 판정·수정하는지 비어 있다.** "각 TOML 필드는 canonical Markdown 또는 hook의 소유 위치를 가리킨다"는 것은 위치만 지정한다. Markdown 규칙 변경자가 계약 값도 바꿔야 하는지, validator 실패를 고칠 권한이 누구에게 있는지, hook 소유자가 상태 표현을 바꿀 때 계약 호환성을 검토하는지 정해지지 않았다. 이 책임 공백은 shared memory가 현재 상태 스냅샷이라는 원칙과 충돌해 시간이 지날수록 조용한 drift를 만든다. **수정 방향:** 필드별 source of truth, 변경 트리거, contract version bump 책임, 검토 책임을 한 표로 확정하고 Runtime 변경 체크리스트에 연결한다.

2. **외부 소비자의 신뢰 모델과 실패 처리 책임이 없다.** 소비자는 계약 불일치 시 경고만 낼지, 자동화를 중단할지, 사람에게 무엇을 제시할지 결정할 수 없다. "읽기 전용"은 소비자 행동을 제한하지 않으며, 권한을 주지 않는다는 producer 의도도 외부 도구의 권한 모델을 대신하지 않는다. **수정 방향:** validator 결과의 안정된 exit code/diagnostic schema와 권장 소비자 정책(불일치 시 관찰만, 승인·배포·수정은 금지)을 계약 문서에 정의한다.

3. **계약이 실제 외부 소비자 요구를 만족하는지 확인할 주체가 없다.** 문제 제기는 "외부 에이전트와 자동 검증"이지만 구체 소비자, 필요한 조회, 안정성 기간, 오류 UX가 없다. 1차를 읽기 전용으로 제한하는 것은 타당해도, 어떤 consumer contract test가 성공 기준인지가 없으면 producer의 self-test만 남는다. **수정 방향:** 최소한 가상 외부 소비자 1개를 명세화해 discovery → parse → version check → reference resolution → non-execution의 end-to-end contract test를 추가하고, 실제 소비자 채택 전에는 experimental 상태를 표시한다.

### 🔧 구조적 문제

1. **계획 단계가 산출물 의존성을 명시하지 않아 구현 순서가 역전될 수 있다.** 1단계의 "필드 목록과 소유자 표"는 어떤 파일에 어떤 규범성으로 남는지 없고, 2단계 parser는 그 표와 profile을 입력으로 삼지 않는다. 3단계 계약 작성 뒤 4단계에서 정합성을 정의하면, validator가 계약을 읽을 수는 있어도 계약의 의미를 검증하지 못하는 사후 구조가 된다. **수정 방향:** (a) discovery·profile·compatibility·authority schema, (b) canonical owner mapping과 동치 규칙, (c) validator/diagnostics, (d) source와 dist 계약, (e) 독립 consumer 및 parity regression 순으로 의존성을 다시 세운다.

2. **"소유자 참조"를 데이터 모델로 만들지 않았다.** TOML 필드가 Markdown/hook을 가리킨다는 설명만 있고, owner가 `path`, `section anchor`, `symbol`, `semantic rule` 중 무엇인지, 여러 owner가 가능한지, owner 문서가 현재 계약을 명시적으로 수용해야 하는지 정의되지 않았다. 따라서 계약은 링크 모음이 되고, 정본 경계를 자동 검증할 수 없다. **수정 방향:** 모든 public field에 stable id, owner kind, owner location, value derivation/consistency rule을 둔 최소 provenance model을 정의한다. 참조 문서에도 같은 stable id를 표기해 rename을 검출한다.

3. **테스트 범위가 parser unit test에 치우쳐 Runtime 경계를 검증하지 못한다.** 체크리스트에는 정상/누락/중복/경로 이탈만 있고, 설치본 discovery, source-dist parity, profile compatibility, 문서 anchor 변경, 한국어 상태 rename, invalid contract의 외부 소비자 안전 중단이 빠져 있다. 또한 Python 3.9 자체에서 실행한다는 검증 방법도 확정되지 않았다. **수정 방향:** Python 3.9 CI 또는 동등 interpreter에서 validator CLI를 실행하는 matrix를 명시하고, source와 dist 각각에 대한 end-to-end fixture 및 과거/미래 contract version fixture를 추가한다.

4. **release 경계의 문서화가 불완전하다.** 요구사항은 release/deploy를 하지 않는다고 하지만, 계약은 Runtime release asset으로 포함되는 배포 인터페이스다. source Runtime에서 contract version을 올리고 dist만 동기화한 상태는 새 immutable bundle을 만들지 않는 정책과 공존한다. 외부 소비자가 source checkout의 contract와 설치된 이전 release contract를 혼동하지 않도록 하는 표식·문서가 없다. **수정 방향:** 계약에 Runtime release identity와 contract protocol version의 관계를 명시하고, source checkout은 개발 중일 수 있으며 설치 대상의 authoritative artifact는 deployed immutable release임을 안내한다. 이번 작업의 검증은 dist parity까지, release compatibility 증빙은 이후 명시 release 절차에서 수행하도록 경계를 분리한다.

