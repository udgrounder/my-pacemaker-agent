# 규칙·용어·제약 거버넌스 감사 보고서

감사일: 2026-08-19  
범위: 실행 규칙·설명 문서·배포 계약·배포본·설치 진입점  
방식: 읽기 전용 (감사 산출물과 태스크 INDEX 외 대상 파일 미변경)

## 기준선과 판정 모델

- Git HEAD: `71f7016218e3df718c159e28be31aa37e5d71b46`
- 기준선의 작업 트리 변경: 이 감사 태스크의 `workspace/tasks/INDEX.md` 및 `workspace/tasks/active/20260819_rule_governance_audit/`만 존재한다.
- Runtime source와 `dist/.mpa-workspace/`는 `diff -rq` 결과 차이가 없다.
- 적용 배포 기준본: `workspace/releases/20260819111934-c43058f6/`의 immutable bundle. 현재 source·dist의 `current_release`도 동일 ID다.

### 판정 우선순위

| 충돌 범위 | 우선 근거 | 처리 |
|---|---|---|
| 실제 상태 전이·명령 동작 | hook·Python 코드와 그 입력 계약 | 문서가 다르면 실행 규칙 결함 또는 문서 drift로 기록 |
| Runtime 배포·rollback | `MAP_PRODUCT_RULES.md`와 `map-product-rules/`, manifest·명령 계약 | source 전용 자산과 Runtime 자산을 분리해 판정 |
| 일반 agent 작업 흐름 | `.mpa-workspace/core/agent_rules.md` | workflow·inject·설명 문서가 다르면 정본과의 불일치로 기록 |
| 사용자 대면 설명 | README·guidebook·agent spec | 실행 레이어를 바꾸지 않지만, 사용자의 행동을 잘못 유도하면 결함으로 기록 |

같은 층위의 규칙이 충돌하고 사용자 의도가 문서로 확인되지 않으면, 우선순위로 임의 결정하지 않고 질문으로 보류한다.

### 사용자 의도에 따른 감사 원칙

이 체계의 목적은 사용자를 절차로 제한하는 것이 아니라, **사용자의 명확한 의도에 맞게 agent가 작업하도록 돕는 것**이다. 암묵지·가정·범위를 계획서에 드러내는 이유도 사용자의 확인 없이 agent가 다른 방향으로 진행하는 일을 막기 위해서다.

따라서 다음 기준으로 규칙을 판정한다.

- 사용자 의도·가치 판단·완료 판단이 필요한 지점에는 확인 경로가 있어야 한다.
- 계획 범위 안의 가역적 실행·기록·조사는 agent가 불필요하게 멈추지 않고 진행할 수 있어야 한다.
- 사용자에게 확인을 요구하는 규칙은 **무엇을 결정하거나 통제하는지**가 짧고 명확해야 한다.
- 확인이 실제 사용자 의도 보호에 기여하지 않거나, 같은 확인을 반복하면 완화·통합 후보가 된다.
- 계획서·변경 기록·검증 결과는 통제 수단이 아니라, agent의 해석과 실행을 사용자의 의도에 계속 정렬시키는 공유 근거다.

## 🚨 즉시 해소 필요

> 아래 항목은 사용자 확인을 늘리자는 제안이 아니다. 이미 필요한 사용자 통제를 문서·상태·hook이 같은 방식으로 설명하도록 맞춰, agent가 확인을 건너뛰거나 불필요하게 멈추지 않게 하는 정합성 수정이다.

### 1. minor 완료 승인 규칙이 실행 문서에서 상충

- 근거: `.mpa-workspace/core/agent_rules.md`는 minor도 구현 후 사용자(또는 위임 에이전트) 확인 뒤에만 done 처리한다고 명시한다. `hooks/code_gate.py`도 done 이동 전 `완료 승인` 상태를 요구한다.
- 충돌: `core/session_protocol.md`의 실패 비용 표는 minor를 “Zone 3 — 자동 처리 후 간략 고지”로 표현한다. `workspace/memory/shared/architecture.md`의 게이트 대칭 원칙도 minor가 계획 승인과 완료 승인 확인을 자동 생략한다고 적는다.
- 영향: minor 작업을 자동 done 처리해도 되는지 agent마다 다르게 해석할 수 있으며, 상태·hook·설명 규칙이 충돌한다.
- 권장: 정본에 맞춰 session protocol과 architecture를 “계획 승인은 자동 처리하지만, 완료 승인 확인은 사용자/위임 확인이 필요하다”로 정정한다. `Zone 3`은 완료 전 문서·상태 업데이트와 계획 범위 안의 가역적 실행을 자동 처리한다는 뜻으로 분리한다. 이로써 agent는 작업 중에는 불필요하게 멈추지 않고, 결과가 사용자 의도와 맞는지 확인할 때만 멈춘다.

### 2. guidebook의 완료 흐름이 필수 사용자 확인을 누락

- 근거: `guidebook/guidebook.md`의 상태 흐름은 major·minor 모두 done 이동에 완료 승인 확인이 필요하다고 설명한다.
- 충돌: 같은 문서의 작업 결과 검토 표와 흐름도는 “추가 작업 없음 → 검토 완료 + done/ 이동”으로 바로 이동한다고 쓴다.
- 영향: guidebook을 기준으로 운용하는 사용자가 완료 요청 없이 done 이동하는 것으로 이해할 수 있다.
- 권장: 해당 두 표현을 “검토 완료 → 사용자 완료 확인 → done 이동”으로 교체한다. 이는 완료 게이트를 추가하는 것이 아니라 이미 존재하는 사용자 결과 통제를 설명과 실제 흐름에 맞춘다.

## ⚠️ 다음 스프린트 전 처리

### 3. `openagent`는 설치 선택지이지만 설치 가능한 통합 계약이 완결되지 않음

- 근거: `install.py --agents` 도움말과 `AGENT_CONFIG_MAP`은 `openagent`를 지원 agent로 제시한다.
- 관찰: `openagent`의 config map은 `None`이고, `agent-specs/openagent/spec.md`의 감지 조건·폴더 규칙·설치 처리는 모두 `TBD` 또는 설치 시 agent에게 질의하도록 되어 있다. install은 진입점·hook을 구성하지 않고 안내만 출력한 뒤 성공 완료 메시지를 낸다.
- 영향: 사용자는 설치 완료를 Runtime과 OpenAgent 연결 완료로 오해할 수 있으며, 배포본에 필요한 agent wiring이 빠진다.
- 권장: (A) OpenAgent를 실험적/수동 설정 대상으로 명시해 선택지와 완료 메시지에서 분리하거나, (B) 확인된 진입점·import·hook 계약과 설치 asset을 구현한 뒤 정식 지원으로 승격한다.

### 4. 외부 도구 용어의 표준성 판정 절차가 없음

- 관찰: glossary는 MPA 내부 용어의 구분에는 강하지만, "외부 표준과의 충돌"을 실제로 어느 공식 출처로 검증할지 정의하지 않는다.
- 영향: 보안·도구·프로토콜 같은 고유 용어를 “표준 용어”로 바꾸자는 제안이 근거 없이 나올 수 있다.
- 권장: 감사 보고서에서 외부 용어는 `공식 출처 확인`, `내부 정의만 확인`, `미검증` 중 하나의 근거 라벨을 의무화한다. 이번 감사에서는 외부 표준 미검증 항목을 변경 후보로 확정하지 않는다.

## 📝 용어·표현 감사

| 항목 | 판정 | 근거 및 권장 |
|---|---|---|
| `계획서` / `plan.md` / 플랜 / 설계서 | 적합 | glossary가 정본 표기와 통용 별칭을 명확히 구분한다. 변경 불필요. |
| 계획 승인 / 완료 승인 확인 / 완료 승인 | 적합 | glossary가 절차와 상태를 분리한다. 다만 위 완료 흐름의 문서 drift를 수정해야 정의가 실제 흐름과 일치한다. |
| GATE | 제한적 유지 | 훅·환경변수 같은 내부 기술 명칭에는 유지하고, 사용자 대면 절차명은 계획 승인/완료 승인 확인으로 쓰는 현재 원칙이 적합하다. |
| `작업`과 `태스크` | 정의 추가 권장 | **작업**은 사용자가 원하는 활동 또는 결과를 가리키는 자연어, **태스크**는 그 작업을 계획서·상태·증빙으로 관리하는 단위로 정의한다. 사용자 대면 문구에서는 “작업”, 관리 상태·파일 경로에서는 “태스크”를 기본 표기로 쓰면 간결하면서도 혼동이 줄어든다. |
| “자동 처리 후 간략 고지” | 부정확 | minor의 완료 승인까지 자동이라는 인상을 줘, “완료 전 자동 처리 / 완료는 사용자 확인 후”처럼 경계를 분리해야 한다. |

## 배포본 완결성 감사

### 기준본과 파일 구성

- 최신 bundle: `20260819111934-c43058f6`
- package checksum: manifest의 `d6e428…e74ab652`와 실제 SHA-256 일치
- Runtime asset 수: manifest 59개, ZIP 59개, `dist/.mpa-workspace/` 59개
- `python3 release_manager.py release-audit` 결과: `release audit passed: 5 release bundle(s)`
- ZIP에는 `workspace/`, `docs/`, `agent-specs/`, `map-product-rules/`, symlink·캐시 파일이 포함되지 않았다.

### 경로별 결과

| 경로 | 필요 계약 | 결과 |
|---|---|---|
| 신규 설치 | `dist/.mpa-workspace/`, `dist/workspace/`, 선택 agent spec, 신규 config·docs 초기화 | Runtime·workspace·agent spec 존재. OpenAgent만 위의 미완결 통합 위험이 있다. |
| Runtime update | immutable package·manifest, dry-run, 승인·rollback 책임자, additive-only config | profile·command contract·코드가 같은 흐름을 설명한다. 현재 bundle도 release audit 통과. |
| rollback | 대상 `.mpa-backups/`의 Runtime·config snapshot, receipt/history 검증 | profile·architecture·코드가 동일한 복구 경계를 사용한다. 현재 release의 validation 기록에 deploy/rollback 시나리오가 포함된다. |

## 대표 요청 계약 검증 (정적)

| 입력 예시 | 기대 라우팅·우선순위 | 필수 근거 | 관찰 증거 | 실패 판정 |
|---|---|---|---|---|
| “현재 구조 알려줘” | 단순 질문, 태스크 없이 처리 | `agent_rules.md` Task 필요 여부 | 단순 질문/탐색은 Task 없이 바로 처리 | 불필요한 task·계획 승인을 강제 |
| “규칙 바꿔줘” | MPA 시스템 파일 수정 | `agent_rules.md` 트리거 → detail의 MPA 수정 절차 | `mpa_system_designer`·release 준비 요구 | 일반 코드 수정 흐름 또는 `dist` 직접 편집으로 라우팅 |
| “전체 정합성 점검해줘” | Layer 2 체크포인트 | `agent_rules.md` 라우팅 표 → `layer2_checkpoint.md` | integration auditor와 실행/설명 레이어 분리 | 일반 code review로 라우팅하거나 memory·INDEX 검사를 누락 |
| “Runtime 배포해줘” | map-product deployment profile 우선 | `MAP_PRODUCT_RULES.md` → deployment coordination | dry-run·승인·rollback 책임자 계약 | 일반 Runtime 규칙으로 우회하거나 대상 변경을 dry-run 전에 수행 |
| “이어서 해줘” | active/hold 기준 태스크 재개 | agent rules trigger → detail 재개 절차 | active 1개면 plan/changelog부터 읽음 | active task 무시·모호한 다중 task를 임의 선택 |

실행이 상태를 변경할 수 있는 배포·설치 시나리오는 실제 대상에서 실행하지 않았다. release validation의 격리된 deploy/rollback 기록과 규칙·코드 참조 체인으로 검증했다.

## 제약 비례성 판정

| 제약 | 판정 | 이유 |
|---|---|---|
| source 전용 map-product 자산을 Runtime에 배포하지 않음 | 유지 | 운영 도구·issue·receipt와 Runtime의 소유 경계를 지키며 ZIP inventory로 검증 가능하다. |
| Runtime update 전에 dry-run·승인·rollback 책임자 요구 | 유지 | 대상 Runtime을 교체하고 backup retention까지 수행하는 고영향 작업이며, 코드 계약으로 강제·검증된다. |
| 모든 major task의 계획 승인·완료 승인 확인 | 유지, 추가 강화 금지 | 계획 승인에서는 의도·범위·위험을, 완료 승인 확인에서는 결과가 사용자 의도에 맞는지 사용자가 통제한다. 이 확인은 짧고 구체적으로 요청해야 하며, 같은 결정을 되묻거나 계획 범위 안의 가역적 실행을 멈추게 해서는 안 된다. guidebook에서 누락된 완료 승인을 정정해야 한다. |
| minor의 계획 승인 자동화 | 유지 | 단일 관심사·가역·결정 불필요라는 네 조건에 한정되어 준수 비용을 줄인다. 완료 확인까지 자동화하면 안 된다. |
| `.mpa-workspace/` 직접 수정 억제 | 유지하되 표현 정리 | "되도록 직접 수정하지 않는다"와 정당한 수정 절차가 함께 있어 실질적 금지는 아니다. agent가 사용자 의도와 다른 방법론 변경을 독단적으로 적용하지 않게 하는 경계다. “원칙적으로 issue→review, 예외적으로 승인된 MPA 수정 태스크”처럼 짧게 명명하면 더 명확하다. |

## 결론과 후속 조치

- 즉시 수정 후보: minor 완료 승인 규칙과 guidebook 완료 흐름의 불일치. 두 수정 모두 사용자 통제를 새로 늘리지 않고, agent가 사용자 의도를 확인해야 할 단 한 지점을 일관되게 만든다.
- 다음 태스크 후보: OpenAgent 지원 범위 확정, 외부 표준 용어 근거 라벨 도입.
- 용어 정리 후보: glossary에 “작업=사용자 활동·결과, 태스크=계획·상태·증빙 관리 단위”를 추가한다.
- 이번 감사는 대상 규칙·Runtime·release 자산을 변경하지 않았다.
