---
태스크: deployer_rollback_responsibility
생성일: 2026-08-28
타입: major
실패비용: major
상태: 테스트 중
승인해시: reqspec-v1:d482edd0c58e7c46
승인대상: 요구사항 명세
---

# 작업 계획서: 배포자와 복구 책임자 일원화

**파생 출처:** campingtalk-proj Runtime 업그레이드 — 별도 복구 책임자 입력이 설치자 역할과 중복됨

---

## 요구사항 명세

### 요청 기준

Runtime 배포에서 별도 복구 담당자를 묻고 기록하는 절차가 불필요하다. 사용자는 설치한 사람이 복구를 책임진다고 정했고, 배포 기록에는 별도 복구 책임자를 남기지 않기를 요청했다.

### 목적

배포 관련 변경 명령에서 별도 `rollback-owner` 입력·검증·기록을 제거하고, 새 `operator` 인자로 실제 실행자를 책임 주체로 일관되게 기록한다.

### 범위·제외 범위

- 범위: source 배포·rollback CLI 계약, receipt/history 기록, 단위 테스트, source 운영 문서와 Runtime 배포 지침을 이 원칙에 맞춘다.
- 범위: Runtime source를 `dist/.mpa/runtime/`에 동기화한다.
- 제외 범위: 기존 immutable release, 과거 receipt/history, 대상 프로젝트의 이미 설치된 Runtime을 수정하거나 재배포하는 일.
- 제외 범위: 승인자·승인 기록과 dry-run 재검증 게이트의 제거 또는 완화.

### 완료 기준

- deploy·rollback·이력 정리 apply·백업 마이그레이션은 `rollback-owner` 인자를 요구하거나 기록하지 않는다.
- 새 deployment/rollback receipt와 대상 Runtime history에는 별도 복구 책임자 필드가 없고, 실행자가 책임 주체로 해석되는 계약이 명시된다.
- 별도 복구 책임자 누락을 이유로 배포·rollback이 실패하지 않으며, 승인·승인 기록·dry-run/backup 무결성 검증은 계속 강제된다.
- source와 `dist/.mpa/runtime/`가 동기화되고 관련 자동 테스트가 통과한다.

### 사용자 결정

- 별도 복구 담당자 기록을 제거한다.
- 배포·rollback을 실행한 사람이 복구 책임 주체다.
- 실제 실행자 식별자는 새 `--operator` 인자로 기록한다. 기존 `--verified-by`는 검증자 역할로 유지한다.
- 동일한 복구 책임 원칙을 `history-cleanup --apply`와 `migrate-runtime-backups`에도 적용한다.

### 변경 불가 제약

- 기존 배포·rollback의 승인자와 승인 기록은 계속 필수다.
- 배포는 기록된 만료 전 dry-run과 대상·release 재검증을 계속 요구한다.
- rollback은 검증된 대상 내부 backup만 사용하며 기존 과거 기록을 재작성하지 않는다.
- `dist/.mpa/runtime/`는 source Runtime 동기화 결과로만 바꾼다.

### 에이전트 가정

| 가정 | 근거 | 틀렸다면 |
|---|---|---|
| 과거 receipt/history의 `rollback_owner`는 감사 이력이므로 그대로 보존한다. | 사용자는 새 배포 기록의 항목 제거를 요청했고, 불변 이력 재작성은 범위 밖이다. | 사용자 명시 이력 마이그레이션 요청을 별도 작업으로 다룬다. |

### 결정 대기 항목 (Open Questions)

- 없음 — 사용자가 권장안으로 진행을 승인했다.

---

## 실행 계획 (Implementation Plan)

### 사전 조사

- [x] `release_manager.py`, 배포·rollback 단위 테스트, source 배포 계약과 Runtime 지침에서 `rollback_owner`의 입력·검증·기록 위치를 대조했다. / 이유: CLI, 기록, 문서 중 일부만 변경해 계약이 어긋나는 일을 막는다.

### 구현 단계

- [x] Step 1 — 사용자 결정에 따라 실행자 식별 인자와 적용 명령 범위를 확정하고 source 명령 계약을 먼저 갱신했다. / 이유: 책임 주체의 의미와 게이트를 확정한 뒤 구현해야 기록의 감사 의미가 흔들리지 않는다.
- [x] Step 2 — `release_manager.py`의 해당 명령 파서·검증·성공/실패 receipt/history 작성에서 별도 `rollback_owner` 의존을 제거하고, 확정한 실행자 식별자를 기록했다. / 이유: 중복 입력을 없애면서 실패 경로까지 감사 가능한 실행 주체를 보존한다.
- [x] Step 3 — 단위 테스트 fixture와 CLI 파서 검증을 갱신해 별도 담당자 없는 정상 경로, 실행자·승인 메타데이터 누락 거부, 성공/실패 기록의 필드 부재 및 legacy 이력 공존을 확인했다. / 이유: 계약의 부분 적용과 게이트 약화를 방지한다.
- [x] Step 4 — 운영 가이드, 설치 안내, architecture 스냅샷과 Runtime 배포 지침을 확정된 실행자 원칙으로 통일했다. / 이유: 설치 Runtime과 source 운영 문서가 같은 계약을 안내하게 한다.
- [x] Step 5 — Runtime source/dist 동기화는 수행하지 않았다. / 이유: 조사 결과 별도 복구 책임자 요구는 source 운영 도구·문서에만 존재하며 `.mpa/runtime/`에는 변경 대상이 없었다.

### 예상 조용한 결정

- 실행자 식별: 사용자 결정 전에는 `verified_by`의 의미를 재정의하지 않는다. 자동 사용자 추론은 추가하지 않는다.
- 과거 이력: immutable release와 기존 receipt/history의 `rollback_owner`는 삭제·마이그레이션하지 않는다.
- 문서 범위: 과거 작업 계획서·review 기록은 감사 이력이므로 수정하지 않고, 현재 명령 계약과 운영 안내만 바꾼다.

### 수정 대상 파일

| 파일 경로 | 변경 내용 |
|---|---|
| `release_manager.py` | 관리 변경 명령 CLI, 검증, receipt/history에서 별도 복구 담당자 제거 및 `operator` 기록 |
| `tests/test_release_manager.py` | 새 CLI·기록 계약과 승인 게이트 회귀 테스트 |
| `README.md`, `install.md` | source 명령 예시와 실행자·승인 역할 설명 갱신 |
| `map-product-rules/command-contract.md` | source 명령 계약을 실행자 책임 원칙으로 갱신 |
| `map-product-rules/deployment-coordination.md` | 배포/rollback gate·기록 설명 갱신 |
| `guidebook/guidebook.md` | 운영 예시와 설명에서 `--rollback-owner` 제거 |
| `workspace/memory/shared/architecture.md` | 현재 배포·복구 기록 계약 스냅샷 갱신 |
| `.mpa/runtime/inject/layer0_update.md` | 설치 Runtime 업데이트 안내의 별도 책임자 요구 제거 |
| `.mpa/runtime/core/agent_rules.md` | 배포 관련 기본 규칙의 별도 책임자 요구 제거 |
| `dist/.mpa/runtime/` | source Runtime 동기화 산출물 |

### 참고 파일 (수정 없음)

- `workspace/memory/shared/architecture.md` — 배포 receipt와 대상 fingerprint의 보존 원칙
- `workspace/releases/` — 기존 불변 release 이력

### 반례 (이 계획이 실패할 수 있는 시나리오)

- 기존 `rollback_owner` 키를 새 receipt/history에 빈 문자열로 남긴다. → Step 1·2에 키 자체 부재를 검사한다.
- 별도 담당자 검증을 지우면서 승인자·승인 기록 또는 실행자 검증까지 함께 사라진다. → Step 3에서 각 필수 메타데이터의 빈 값 거부를 계속 검증한다.
- deploy만 변경하고 rollback·history cleanup·backup migration CLI 또는 Runtime 지침이 옛 인자를 계속 요구한다. → Step 1·3·4·5에서 확정된 범위의 모든 명령·문서·배포본을 함께 대조한다.
- 자동화가 실행하고 사람이 검증자만 지정한 경우 책임자가 잘못 기록된다. → 실행자 식별 인자의 의미를 사용자 결정으로 확정하고 Step 2에서 성공·실패 기록 모두에 적용한다.

---

## 실행 TODO

### 구현·에이전트 검증

- [x] 확정 범위의 관리 명령에서 별도 복구 담당자 입력·기록을 제거했다.
- [x] 새 실행자 기록과 기존 승인·무결성 게이트를 자동 테스트했다.
- [x] source 운영 문서와 배포 계약을 동기화했다. Runtime source/dist에는 변경 대상이 없음을 검색으로 검증했다.

### 사용자 결정·승인 필요

- [ ] 계획서를 검토하고 구현을 승인한다.

## 검증 결과

### 검증 체크리스트

- [x] 정상 경로: 확정 범위의 명령이 `rollback-owner` 없이 성공하고 receipt/history는 실행자를 기록한다. / 증빙: 74개 unit test와 네 관리 명령 help 검증.
- [x] 실패 경로: 실행자, 승인자 또는 승인 기록이 비어 있으면 해당 명령이 거부된다. / 증빙: deploy·rollback·history cleanup 테스트.
- [x] 엣지 케이스: 기존 receipt/history는 재작성하지 않고, 새 성공/실패 기록에만 별도 복구 담당자 키가 없다. / 증빙: receipt field·legacy history 호환 테스트와 독립 2차 검증.

### 완료 시 문서 업데이트 대상

- [ ] `guidebook/guidebook.md` — Runtime 업데이트 명령 예시와 책임 주체 설명

## 운영 시 안내 사항

| 영향 대상 | 운영상 달라지는 점 | 사용자 안내 |
|---|---|---|
| source 운영자 | `--rollback-owner`를 전달하지 않는다. | 실행자 식별 인자와 적용 명령 범위는 사용자 결정 뒤 확정한다. |
| 설치 대상 Runtime | 다음 Runtime release를 배포한 뒤 최신 안내가 적용된다. | 이번 작업은 release 생성·대상 재배포 요청을 포함하지 않는다. |

## 실행 중 변경 기록

| 변경 내용 | 이유 | 명세 영향 |
|---|---|---|
| 별도 `operator` 인자 도입 | `verified_by`의 기존 검증자 의미를 보존하면서 실제 실행자와 복구 책임 주체를 명확히 하기 위해 | 없음 |
| 실패 receipt에도 `operator` 기록 | 실패·자동복구 경로에서도 책임 주체를 추적하기 위해 | 없음 |
| Runtime source/dist 동기화 생략 | `.mpa/runtime/`에 해당 계약이 없어 source 운영 도구·문서만 변경됐기 때문에 | 없음 |

## 명세 변경 이력

| 승인 시각 | 이전 체크섬 | 새 체크섬 | 변경 요약 |
|---|---|---|---|

### 구현 후 발견

| 항목 | 유형 | 발견 맥락 | 처리 경로 |
|---|---|---|---|
| (결과를 경험한 후 채움) | 명세 밖 보완 / 명세 변경 / 신규 작업 항목 | 왜 보기 전에는 보이지 않았는가 | 실행 기록 갱신 / 승인 이력 갱신 / INDEX.md 등록 |

**파생된 작업 항목:**
- 없음
