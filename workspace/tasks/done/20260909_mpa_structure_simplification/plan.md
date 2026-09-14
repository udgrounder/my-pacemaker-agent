---
태스크: mpa_structure_simplification
생성일: 2026-09-09
타입: major
실패비용: critical
상태: 완료 승인
승인해시: reqspec-v1:456f2beea35009ec
승인대상: 요구사항 명세
---

# 작업 계획서: MPA 문서 로딩·운영 코드 구조 개선

**파생 출처:** [규칙 정합성과 경량 검증 보완](../../done/20260909_mpa_policy_consistency/plan.md). 우선 설계 대상으로 전환했다. [효과 측정 체계](../../hold/20260909_mpa_effectiveness_evaluation/plan.md)는 hold로 유지한다.

## 요구사항 명세

### 요청 기준

항상 읽는 규칙의 부담과 release_manager의 여러 책임 결합을 줄이되, 필요한 정책과 복구 동작을 보존한다.

### 목적

에이전트가 필요한 규칙을 정확하게 찾고, 개발자가 운영 코드를 수정할 때 영향을 파악하기 쉽게 한다.

사용자가 명시한 “사용자를 필요 이상으로 불편하게 하지 않는다”를 적용한다. 내부 구조를 줄이면서 사용자에게 새 명령·설정·수동 문서 관리 부담을 넘기지 않는다.

### 범위·제외 범위

- 범위: 실제 로드 경로·파일 의존성 조사, core의 반복 상세를 기존 on-demand 파일로 이동, 관련 참조 정리, release_manager의 책임별 모듈 분리, 기존 CLI·데이터 호환 검증.
- 제외: 정책 행동 변경, 새로운 기능·상태 형식, 평가에서 확인되지 않은 목표 토큰 절감률 약속, release/receipt 형식 변경, 자동 릴리즈·설치·배포, 과거 이력 재작성, 외부 프로젝트 데이터 조작.

### 완료 기준

1. 진입점부터 필수/조건부 로드까지 참조 지도가 있고, 단순 질문·minor·major·재개·비평·검증별 도달해야 하는 정책을 확인할 수 있다.
2. core는 필수 판단·트리거를 유지하고 반복 상세만 이동한다. 이동 전후 필수 정책 도달성이 같고, 항상 로드되는 바이트 수가 기준선보다 감소한다. 실제 토큰·시간 개선은 별도로 측정하며 바이트 감소로 대신 주장하지 않는다.
3. release_manager의 CLI 명령·인자·종료 코드, manifest·receipt·backup 형식, 실패 시 Runtime/config/issue 복구 순서, 공개 import 경로의 호환성이 유지된다.
4. 모듈 분리는 작은 단위로 수행하고 각 단계마다 기존 테스트가 통과한다. 파일 크기 목표를 맞추려고 트랜잭션 책임을 여러 모듈에 분산시키지 않는다.
5. 결정된 새 모듈 목록·의존 방향과 변경 전후 검증 근거가 있으며, source/dist parity와 독립 검증을 통과한다.
6. 기존 자연어 요청·CLI 사용 흐름을 유지하며 구조 분리 때문에 사용자에게 새 단계·설정·수동 작업을 요구하지 않는다. 내부 문서 위치를 사용자가 직접 선택해야만 진행할 수 있는 흐름을 만들지 않는다.

### 사용자 결정

- 효과 측정보다 구조 개선을 우선한다(2026-09-09 사용자 지정).
- “사용자를 필요 이상으로 불편하게 하지 않는다”를 유지한다. 새 명령·설정·문서 선택을 사용자에게 요구하지 않는다.
- 이번 요청은 상세 설계다. 실제 구조 변경은 완성 계획서의 별도 구현 승인 뒤 시작한다.

### 변경 불가 제약

배포·복구 기능의 관측 가능한 동작과 안전 검사를 약화하지 않는다. 기존 테스트의 기대값을 새 구현에 맞춰 바꿔 회귀를 숨기지 않는다. source-only 모듈을 Runtime에 포함하지 않는다. 실제 대상 배포는 실행하지 않는다.

### 에이전트 가정

| 가정 | 근거 | 틀렸다면 |
|---|---|---|
| 로드 비용은 실행 레이어의 실제 참조 경로로 평가한다 | 가이드 길이와 에이전트 비용은 다름 | 실측 가능한 범위만 보고 |
| CLI 입구를 남기고 leaf 책임을 분리할 수 있다 | AST와 테스트 조사로 ZIP 6개·이슈 형식 5개 함수 및 가변 전역/patch 결합 확인 | 기존 테스트를 유지하고 해당 추출 단위 재설계 |
| 작은 추출 단위가 안전하다 | 배포 복구 순서 결합이 큼 | 결합 영역은 유지하고 범위 축소 제안 |

### 결정 대기 항목 (Open Questions)

사용자 목적·범위에 관한 미결정 항목 없음. 모듈 경계와 호환 방법은 아래 기술 설계로 정했다. 설계 검토 후 구현 승인은 별도로 필요하다.

## 실행 계획 (Implementation Plan)

### 사전 조사

조사 결과와 상세 계약은 [dependency-map.md](dependency-map.md)에 기록했다. core는 현재 385줄·34,731바이트, release_manager는 2,247줄·115개 함수다. 기존 초안의 core 374줄은 최신 기준으로 갱신했다. 크기 자체는 결함 판정이나 추출 목표가 아니다.

진입점·Runtime 참조·기존 테스트를 확인했다. release_manager의 경로 전역과 오류 주입 patch를 보존해야 하므로 전체를 여러 서비스로 재작성하지 않고 ZIP 처리와 이슈 형식 처리만 추출한다. 배포/복구·이슈 이동 transaction·release 생성 조정은 현재 파일에 남긴다.

### 문서 상세 설계

- D1: 작업 생성의 **major 전용** 반복 상세만 기존 `inject/layer1_design.md`와 통합한다. minor의 plan template·자동 승인 전제·최소 확인은 detail의 직접 경로에 남긴다. core에는 계획 작성 진입, TODO 증빙 범위, 별도 후속 작업 분리 요약을 남긴다.
- D2: 승인 명령·해시 기록 상세는 기존 detail 파일의 새 `승인 기록 처리` 섹션으로 이동한다. 최초 승인·자동 승인·기록 복구·명세 변경 경로에서 실제 행동 전에 읽도록 직접 연결한다.
- D3: 완료 파일 이동·정리 상세는 detail의 새 `작업 항목 완료 처리` 섹션으로 이동한다. core에 완료 승인과 상태→INDEX→이동 순서·증거 기반 보고를 유지한다.
- core의 부담 최소화·상태/요청 라우팅·critical 차단·유효 승인 재사용·minor 계획만 요청한 경우의 실행 금지·독립 검증 정본 참조는 유지한다. 기존 제목과 주요 정책 테스트 계약을 보존한다.
- [정책 도달성 11개 사례](dependency-map.md#대표-요청별-정책-도달성-검증표)를 전후 대조하고, core 바이트 감소와 요청별 참조량을 분리 보고한다. 새 Runtime 문서 파일이나 새 로더를 만들지 않는다.

### 운영 코드 상세 설계

| 신규 source-only 파일 | 역할 | 호환 방법 |
|---|---|---|
| `mpa_ops/__init__.py` | 내부 패키지 표시 | import 부작용 없음 |
| `mpa_ops/archive_io.py` | ZIP 생성/검사/해제 6개 함수 | 기존 이름·시그니처 wrapper를 release_manager에 보존; tree/member 검사 callable과 ignore 값을 호출 시 전달 |
| `mpa_ops/issue_format.py` | 후보 parse·완전성·경로 정규화·metadata identity 5개 함수 | 기존 wrapper 유지; 기존 정규식·marker·anchor의 현재 값을 명시 전달 |

정확한 함수 목록·입출력·의존성은 [확정 모듈 경계](dependency-map.md#확정-모듈-경계)에 있다. 내부 모듈은 facade를 import하지 않는다. 가변 전역의 복제나 sys.modules 교체를 사용하지 않는다. 조정 함수가 기존 wrapper를 계속 호출해 기존 patch가 유효하도록 한다.

### 절대 금지

외부 CLI/API·함수 시그니처·데이터 형식·정책 행동 변경, 기존 운영 코드 테스트 수정/삭제, 배포 복구 순서 변경, source-only 패키지의 Runtime 포함, 새 외부 의존성, 실제 설치 대상 조작을 금지한다. 검증 목적의 임시 fixture만 사용한다.

### 구현 단계

1. **상세 설계·비평** — 조사 지도, 자기 점검、독립 비평을 완료하고 반영한다. 이유: critical 운영 경계의 숨은 가정을 구현 승인 전에 확인한다.
2. **승인 후 기준선 고정·명령별 기대값 확정·누락 회귀 보강** — 소스 hash와 전체 테스트를 확인한다. deploy와 rollback의 정상/실패 복구 순서를 별도로 기록한 뒤, 신규 테스트 파일에 spec loader/import/patch/CLI와 실패 주입의 빈칸을 먼저 보강한다. 이유: 새 구조에 맞춰 기대값이나 rollback 동작이 바뀌는 일을 막는다.
3. **문서 D1→D2→D3 이동** — D1의 major 전용 상세와 minor detail 직접 경로를 구분해 각 이동의 정본·트리거·직접 단계 진입을 확인한다. source/dist 동기화 후 기존 정책 테스트와 신규 도달성 검사, 바이트 비교를 수행한다. 이유: 코드 추출 문제와 정책 참조 문제를 분리해 진단한다.
4. **ZIP 처리 추출** — archive_io와 wrapper를 작성하고 기존 release 테스트·ZIP 실패/metadata 검증을 실행한다. 이유: archive 경계를 먼저 고정한 뒤 다음 책임을 옮긴다.
5. **이슈 형식 처리 추출** — issue_format과 wrapper를 작성하고 기존 release 테스트·정규화/identity·오류 주입을 실행한다. 이유: 이슈 수집/원복 transaction을 유지하면서 형식 책임만 분리한다.
6. **통합·독립 검증** — 전체 테스트, CLI/import 호환, 실패 주입표, source/dist parity, diff 검사를 완료한다. 아키텍처 메모리·설명 문서·검증 기록을 갱신하고 1차/2차 독립 구현 검증을 수행한다. 이유: 개별 추출 통과만으로 복합 경로의 보존을 주장하지 않는다.

2→3→4→5→6을 순차 진행한다. 선행 검사가 실패하면 다음 추출로 넘어가지 않는다. 대상 파일 hash가 달라진 경우 해당 의존성만 재조사한다. 기능·권한 제약을 바꿔야 하는 발견은 명세 변경으로 돌아가고, 같은 범위의 기술 수정은 에이전트가 처리한다.

### 예상 조용한 결정

두 내부 모듈만 추출한다. 2,247줄 전체를 얇은 CLI로 만드는 것은 이번 목표가 아니다. wrapper 때문에 일부 중복 선언이 생기더라도 기존 import와 오류 주입 계약을 보존한다. byte 감소를 토큰·시간 개선으로 환산하지 않는다. 사용자 대면 README에 내부 모듈 목록을 늘리지 않는다.

### 수정 대상 파일

| 파일 | 변경 내용 |
|---|---|
| `.mpa/runtime/core/agent_rules.md` | D1–D3 요약·조건부 로드 트리거 |
| `.mpa/runtime/core/agent_rules_detail.md` | 승인 기록·완료 처리 상세 정본 |
| `.mpa/runtime/inject/layer1_design.md`, `layer1_implement.md` | 설계 반복 설명 통합·승인 기록 상세 직접 참조 |
| `release_manager.py` | 기존 함수 wrapper와 내부 모듈 연결 |
| `mpa_ops/__init__.py`, `archive_io.py`, `issue_format.py` | 위의 확정된 leaf 책임 |
| `tests/test_release_manager_compatibility.py`, `test_release_manager_extraction.py` | 기존 테스트에 없는 호환/실패 사례만 추가 |
| `tests/test_structure_loading.py` | D1–D3의 참조·제목·누락 트리거 검출, 바이트 기준 |
| `dist/.mpa/runtime/` | 수정 Runtime 파일 동기화 |
| `workspace/memory/shared/architecture.md` | 실제 적용 뒤 모듈 경계·문서 정본 갱신 |
| `docs/INDEX.md`, `docs/mpa-internal-structure.md` | 내부 유지보수 지도(현재 docs 없음; 구현 때 생성) |
| 현재 작업 폴더의 `TODO.md`, `verification.md`, `changelog.md`, 독립 review 파일 | 항목별 구현 위치·검증 결과 |

### 참고 파일 (수정 없음)

`MAP_PRODUCT_RULES.md`, `install.py`, `project_config.py`, `agent-specs/`, `tests/test_release_manager.py` 및 기존 정책·설치·hash 테스트, 기존 release/receipt fixture, 선행 policy-audit·verification. immutable 이력은 읽기 근거가 필요한 경우에만 참고한다.

### 반례

- 지침 이동 후 로드 트리거 누락 → 모든 대표 요청의 정책 도달성 검사.
- 함수 이동으로 테스트 mock/외부 import가 다른 객체를 가리킴 → import·patch 계약 조사 후 wrapper 또는 테스트 결합만 조정; 기대 동작 유지.
- issue와 Runtime 복구 순서가 분리됨 → 트랜잭션 조정은 한곳에 유지하고 각 실패 시점의 원복 검증.
- 문서 길이 감소에도 재읽기 증가 → 총 참조 비용을 별도 기록, 실제 효율 향상을 단정하지 않음.
- ZIP 공통화 중 Runtime ignore 규칙이 backup에 적용됨 → 4단계에서 두 쓰기 경로를 유지하고 fixture로 대조.
- sys.modules에 등록하지 않는 기존 spec loader가 실패함 → 2단계에서 재현하고 역방향 import/모듈 별칭 교체를 금지.
- core를 읽지 않은 implementer가 승인 상세를 놓침 → 3단계에서 inject의 직접 참조와 minor fast path를 함께 검증.

## 실행 TODO

### 구현·에이전트 검증

- [x] 후속 목표·호환 경계 초안 작성.
- [x] 의존성 조사·수정 파일·모듈 경계 확정: dependency-map.md.
- [x] 자기 점검·독립 비평 및 반영: critique.md의 C1·C2 반영.
- [x] 구현 전 기준선과 누락 회귀 보강: 전체 153개 테스트 및 release_manager 계열 회귀 통과, compatibility 검사 3개 추가.
- [x] 문서 로딩 정리 및 접근성·바이트 비교: core 34,731 → 28,471바이트, source/dist 58파일 parity 및 17개 정책·구조 테스트 통과.
- [x] 운영 코드 점진 분리와 단계별 회귀 확인: ZIP 처리 6개·이슈 형식 5개 함수를 source-only 모듈로 추출하고 release_manager 회귀 확인.
- [x] 실패 복구·CLI/import 호환·전체 테스트·독립 검증·문서·동기화 완료. 1차 지적의 검증 공백을 보완한 뒤 2차 독립 검증으로 최종 확인한다.

### 사용자 결정·승인 필요

- [ ] 상세 설계가 완성된 계획서의 구현 승인.
- [x] 구현·검증 결과 확인 후 완료 승인: 사용자의 “작업 완료 됐으면 완료 처리” 지시에 따라, 2차 독립 검토 통과와 최종 회귀 통과를 근거로 처리.

## 검증 결과

상세 조사·설계 작성 완료. 구현은 미실행. 자기 점검에서 문서 상세 이동 뒤 implementer의 승인 절차 누락, ZIP/backup ignore 규칙 혼합, spec loader 환경의 역방향 import 실패를 확인해 각각 3·4·2단계와 반례에 반영했다.

독립 비평은 [critique.md](critique.md)에 기록했다. C1은 minor가 design을 경유하지 않아도 되도록 D1을 major 전용으로 한정하고 detail 직접 경로를 명시해 해소했다. C2는 deploy와 rollback의 실제 실패 복구가 다름을 확인해 명령별 정상/예외 순서와 실패 주입표로 분리했다. 사용자 목적·범위에 관한 누락 결정은 발견되지 않았다. 배포·복구 관련 공유 운영 코드 변경으로 critical이지만, 비평 반영까지 마쳐 설계 완료로 전환한다.

실제 검사 명령·CLI/import/오류 주입 계약·단계 중단 기준은 [호환 검증 설계](dependency-map.md#호환-검증-설계)를 따른다. 구현 단계에서 source/dist 동기화, compatibility·구조 로딩 12개, 기존 release_manager 91개, 전체 165개 테스트와 `git diff --check`를 통과했다. 1차 독립 구현 검토의 source-root loader 계약·11개 facade·source-only artifact·요청별 라우팅 공백은 새 회귀 검사와 내부 구조 문서로 보완했다. 2차 검토의 ZIP leaf 예외 transaction 회귀 공백도 deploy/rollback 실패 주입 3개로 보완했다. 실제 토큰·시간 효율 향상은 측정하지 않았으며 주장하지 않는다.

### 검증 체크리스트

- [ ] 정상: 기존 CLI와 import 계약 유지, 필수 정책 도달.
- [ ] 실패: 패키지 변조·배포 검증 실패·issue 이동 실패·receipt 실패 후 기존 원복 유지.
- [ ] 경계: 구형 immutable bundle, 사용자 config 보존, 중첩 경로, mock 의존성, 미상 로드 조건.

### 완료 시 문서 업데이트 대상

현재 아키텍처 메모리·관련 운영 가이드·작업 폴더 검증 기록.

## 운영 시 안내 사항

구현 뒤에도 설치 프로젝트는 그대로 유지된다. 배포는 별도 요청이다. 실제 성능·효율 평가는 측정 프로토콜로 확인하며 구조 개선 자체를 생산성 향상으로 간주하지 않는다.

## 실행 중 변경 기록

| 변경 내용 | 이유 | 명세 영향 |
|---|---|---|
| hold 초안 작성 | 조사 없는 대규모 변경을 확정하지 않으면서 후속 범위 보존 | 승인 전 |
| 우선순위 조정·상세 설계 | 사용자 요청에 따라 로딩 이동 3개와 내부 모듈 2개의 경계·호환/실패 검증 확정 | 승인 전, 기존 목적·제약 유지 |
| source 운영 코드 맵 기록 | 코드 탐색에서 확인한 release_manager·install·테스트·진입점 관계를 project memory에 반영 | 없음 |
| 추출 전 호환 회귀 검사 추가 | spec loader·CLI·facade patch 계약을 구조 변경 전에 고정 | 없음 |
| Runtime 문서 조건부 로딩 정리 | major 상세·승인/완료 절차를 detail로 이동하고 minor 직접 경로·core의 불변 조건 보존 | 없음 |
| ZIP 처리 내부 모듈 추출 | archive_io와 6개 facade를 추가해 release_manager의 외부/patch 계약 유지 | 없음 |
| 이슈 형식 내부 모듈 추출 | issue_format과 5개 facade를 추가해 preflight·수집·원복 transaction을 유지 | 없음 |
| 1차 독립 검토 지적 보완 | 기존 source-root import 계약을 명시하고, facade·source-only artifact·11개 라우팅과 source/dist parity 회귀를 강화 | 없음 |

## 명세 변경 이력

| 승인 시각 | 이전 체크섬 | 새 체크섬 | 변경 요약 |
|---|---|---|---|

### 구현 후 발견

최종 독립 구현 검증 통과. 실제 토큰·시간 효율은 후속 효과 측정 작업에서 별도로 평가한다.
