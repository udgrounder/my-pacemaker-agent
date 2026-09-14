---
태스크: mpa_toml_reference_contract
생성일: 2026-09-14
타입: major
실패비용: major
상태: 설계 중
승인해시: ""
승인대상: 요구사항 명세
---

# 작업 계획서: TOML 기반 MPA 참조 계약

**파생 출처:** `workspace/issues/inbox/my-pacemaker-agent/config_toml_external_agent_reference.md` — 외부 에이전트와 자동 검증이 읽을 수 있는 MPA 규칙 계약 필요

## 요구사항 명세

### 요청 기준

사용자는 TOML 기반 참조 계약을 어떤 방식과 범위로 만들지 먼저 제시해 달라고 요청했다.

### 목적

외부 에이전트와 검증 도구가 MPA의 안정적인 구조 사실을 읽을 수 있게 하되, 설명·판단·예외를 담은 Markdown 규칙을 기계 설정으로 무리하게 이전하지 않는다.

### 범위·제외 범위

- 범위: Runtime 안의 버전 있는 TOML 참조 계약, 계약 필드의 소유·검증 규칙, 외부 소비자 안내, source/dist 동기화와 회귀 검증.
- 제외 범위: Markdown 규칙 전체 이관, 자연어 라우팅의 자동 판정, 기존 hook의 동작·승인 게이트 변경, 외부 서비스 연결, 설치 대상 배포·release 생성.

### 완료 기준

- TOML은 계약 버전, Runtime 진입 규칙의 상대 경로, major/minor 상태 전이, 문서·작업 기본 경로, 구조화된 안내 참조만 표현한다.
- 각 TOML 필드는 canonical Markdown 또는 hook의 소유 위치를 가리키며, 판단 근거·사례·예외 문구를 중복 저장하지 않는다.
- 계약 파일의 문법·필수 필드·경로 안전성·Markdown 참조 정합성을 Python 3.9 환경에서도 외부 의존성 없이 검증할 수 있다.
- 계약은 1차에서 읽기 전용 참조이며, TOML 값이 hook의 행동이나 사용자의 승인 절차를 직접 바꾸지 않는다.
- Runtime source와 `dist/.mpa/runtime`의 계약·검증기·문서가 동기화되고, 실제 release·deploy는 실행하지 않는다.

### 사용자 결정

- TOML 계약의 범위와 방법을 구현 전에 먼저 제시한다.
- 실제 효과 측정 pilot은 별도 hold 작업으로 보류한다.

### 변경 불가 제약

- 사용자에게 같은 목적·승인을 다시 묻거나 새로운 수동 기록을 요구하지 않는다.
- 외부 에이전트에 권한을 주거나, TOML만으로 Markdown의 판단·예외 규칙을 대체하지 않는다.
- Python 3.9 호환성을 깨거나 필수 제3자 런타임 의존성을 추가하지 않는다.

### 에이전트 가정

| 가정 | 근거 | 틀렸다면 |
|---|---|---|
| 1차 계약은 읽기 전용이어야 한다 | 현 Runtime hook은 Markdown과 Python 로직을 직접 사용하며, TOML 소비자가 아직 없다 | 구체 소비자를 먼저 정의하는 별도 설계로 전환 |
| 제한된 TOML profile 검증이 필요하다 | 현재 실행 Python 3.9에는 `tomllib`가 없고, 설치 대상 의존성도 보장되지 않는다 | 지원 Python·의존성 정책을 요구사항으로 올려 재승인 |

### 결정 대기 항목 (Open Questions)

없음. 1차는 읽기 전용·제한된 계약으로 설계하며, hook 행동을 TOML이 직접 제어하는 2차는 실제 소비자 요구가 생긴 뒤 별도 작업으로 분리한다.

## 실행 계획 (Implementation Plan)

### 사전 조사

현재 규칙은 Markdown과 Python hook에 분산돼 있고, 실행 환경은 Python 3.9.6이다. `tomllib`는 없으므로 1차 계약은 외부 패키지·Python 버전 상향을 전제로 하지 않는다. 기존 Codex agent 설정의 TOML은 agent 자체 설정일 뿐 MPA Runtime의 구조 계약이 아니다.

### 구현 단계

1. 계약 경계 고정 — `contracts/agent_reference.toml`의 필드 목록과 각 필드의 Markdown/hook 소유자를 표로 정의한다. / 이유: TOML이 새로운 규칙 복사본이 되는 것을 막는다.
2. 제한된 TOML profile 검증기 작성 — 지원하는 table·문자열·배열·boolean만 읽고, 알 수 없는 구조·중복 키·상대 경로 이탈을 거부한다. / 이유: Python 3.9에서도 제3자 의존성 없이 계약을 검증한다.
3. 읽기 전용 계약 작성 — lifecycle, paths, entrypoints, guide references를 TOML로 작성하고 Markdown에는 계약의 역할과 정본 경계를 연결한다. / 이유: 외부 소비자가 안정된 식별자를 읽되 기존 agent 행동을 바꾸지 않는다.
4. 정합성 검사 추가 — 계약 필드·대상 경로·상태 전이·소유자 참조의 정상·누락·중복·경로 이탈 사례를 테스트한다. / 이유: TOML과 실제 Runtime이 조용히 어긋나는 회귀를 막는다.
5. Runtime 동기화·문서화 — source를 dist에 동기화하고 외부 소비자용 읽기 예시와 1차 제한을 기록한다. / 이유: 설치본과 원본의 계약을 같게 하고 자동 실행으로 오해하지 않게 한다.

### 예상 조용한 결정

- 계약 파일 위치는 `.mpa/runtime/contracts/agent_reference.toml`로 둔다. Runtime 내부에서 찾기 쉽고 agent별 TOML 설정과 구분된다.
- 상태는 현재 한국어 상태 문자열을 보존하고, 새 영문 enum을 만들지 않는다. 기존 plan hash·code gate와의 용어 분열을 피한다.
- 명령은 실행 문자열이 아니라 hook 상대 경로와 용도 식별자만 기록한다. 외부 소비자가 임의 명령을 실행하게 만들지 않는다.

### 수정 대상 파일

| 파일 경로 | 변경 내용 |
|---|---|
| `.mpa/runtime/contracts/agent_reference.toml` | 신규 읽기 전용 계약 |
| `.mpa/runtime/hooks/contract_reference.py` | 제한된 TOML profile 검증기 및 CLI |
| `.mpa/runtime/core/agent_rules.md` | 계약의 목적·정본 경계·참조 안내 |
| `.mpa/runtime/core/agent_rules_detail.md` | 구조화 필드와 상세 절차의 소유 경계 |
| `.mpa/runtime/templates/` 및 관련 inject | 계약을 중복하지 않는 참조 정리 (필요한 경우만) |
| `tests/test_contract_reference.py` | 계약 검증 회귀 |
| `guidebook/guidebook.md` | 외부 소비자 사용법·제한 |
| `dist/.mpa/runtime/` | source Runtime 동기화 결과 |

### 참고 파일 (수정 없음)

- `workspace/issues/inbox/my-pacemaker-agent/config_toml_external_agent_reference.md` — 문제 제기와 초안 범위
- `workspace/memory/shared/architecture.md` — Runtime source/dist와 release 경계
- `.mpa/runtime/hooks/plan_hash.py`, `.mpa/runtime/hooks/code_gate.py` — 상태·승인 계약의 현 소유자

### 반례

- TOML에 Markdown의 모든 규칙을 복제함 → 서로 다른 정본이 생김. 필드별 소유자 참조와 제한된 범위로 방지한다.
- 제한된 parser가 유효한 일반 TOML을 거부함 → 지원 profile을 명시하고 외부 소비자에게도 profile 준수를 요구한다.
- 외부 도구가 TOML의 hook 경로를 실행 권한으로 해석함 → 명령 문자열 대신 식별자·상대 경로만 제공하고 읽기 전용임을 문서화한다.
- TOML 값 변경이 승인 흐름을 우회함 → 1차 검증기는 읽기 전용이며 plan hash·code gate의 실행 입력으로 연결하지 않는다.

## 실행 TODO

### 구현·에이전트 검증

- [ ] 계약 경계·TOML profile·소유자 표 구현.
- [ ] 검증기·회귀 테스트·source/dist 동기화·문서화.
- [ ] MPA 시스템 파일 정합성 및 독립 구현 검증.

### 사용자 결정·승인 필요

- [ ] 계획서 검토 후 읽기 전용 TOML 계약 1차 구현 승인.

## 검증 결과

설계 초안. 복잡한 5단계 의존 구현과 Runtime 계약 영향이 있어, 설계 완료 전 독립 비평을 수행한다.

### 검증 체크리스트

- [ ] 정상: 유효 계약이 Python 3.9에서 읽히고 모든 참조 경로가 존재한다.
- [ ] 실패: 누락 필드·중복 key·지원하지 않는 구조·경로 이탈을 거부한다.
- [ ] 경계: TOML의 상태·경로가 Markdown/hook 정본과 달라도 hook 행동은 바뀌지 않으며 검증만 실패한다.

### 완료 시 문서 업데이트 대상

- `guidebook/guidebook.md` — 외부 소비자용 읽기 전용 계약 안내

## 운영 시 안내 사항

1차 계약은 외부 소비자가 읽는 메타데이터다. TOML 변경만으로 agent의 승인·라우팅·hook 동작은 바뀌지 않으며, 그런 제어 계약은 실제 소비자 요구가 생긴 뒤 별도 작업으로 검토한다.

## 실행 중 변경 기록

| 변경 내용 | 이유 | 명세 영향 |
|---|---|---|
| (구현 전) |  | 없음 |

## 명세 변경 이력

| 승인 시각 | 이전 체크섬 | 새 체크섬 | 변경 요약 |
|---|---|---|---|

### 구현 후 발견

| 항목 | 유형 | 발견 맥락 | 처리 경로 |
|---|---|---|---|
| (결과를 경험한 후 채움) | 명세 밖 보완 / 명세 변경 / 신규 작업 항목 | 왜 보기 전에는 보이지 않았는가 | 실행 기록 갱신 / 승인 이력 갱신 / INDEX.md 등록 |
