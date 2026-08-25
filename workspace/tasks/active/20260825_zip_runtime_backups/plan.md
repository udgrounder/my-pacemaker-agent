---
태스크: zip_runtime_backups
생성일: 2026-08-25
타입: major
실패비용: major
상태: 검증 중
승인해시: reqspec-v1:14afb0f1d5818993
승인대상: 요구사항 명세
---

# 작업 계획서: 성공 배포 Runtime 백업의 ZIP 보관

**파생 출처:** 없음

---

## 요구사항 명세

### 요청 기준

`campingtalk-proj` Runtime 업그레이드마다 `.mpa/backups/<version>/runtime/` 아래의 많은 개별 파일이 보관된다. 사용자는 버전별 backup 디렉터리는 유지하되, 업그레이드가 문제없이 끝난 뒤 그 안의 `runtime/`만 ZIP으로 압축하고 원본 파일을 삭제하도록 절차 보완을 요청했다. 기존 디렉터리형 Runtime rollback 호환은 더 이상 필요하지 않으며, 기존 backup의 ZIP 전환 실패는 원본을 보존한 채 사용자에게 알려 다음 처리를 받는다. 전환 결과와 실패 원인은 별도 receipt 대신 각 backup의 `backup-metadata.json`에 남긴다. 오래된 release·배포·backup 이력은 자동 정리하지 않고, 사용자가 명시적으로 정리 요청했을 때 전체 후보를 확인·승인받아 일괄 정리한다.

### 목적

성공한 Runtime 배포의 각 버전 backup에서 Runtime tree만 단일 ZIP으로 줄이되, 배포 실패 시 즉시 복구와 이후 rollback 기능을 보존한다.

### 범위·제외 범위

- 범위: `release_manager.py`의 성공 배포 backup 내부 `runtime/` 보관·검증·rollback 흐름, `campingtalk-proj`의 기존 backup 전환, 사용자가 요청한 전체 이력 정리 dry-run·승인 apply command, 관련 단위 테스트와 Runtime 배포 규칙을 ZIP 아카이브 방식에 맞춘다.
- 제외 범위: 배포 중 전체 Runtime 원자 교체 방식 변경, release bundle 형식 변경, 대상 프로젝트의 업무 코드·workspace 데이터 변경, backup root·버전별 backup 디렉터리·선택적 config snapshot의 ZIP화.

### 완료 기준

- 성공 배포가 검증을 마친 뒤 대상 `.mpa/backups/<version>/`에 `backup-metadata.json`과 선택적 config snapshot은 유지하고, `runtime.zip`만 남긴다. ZIP 무결성이 확인된 후 원본 `runtime/` 디렉터리를 삭제한다.
- 배포 중 오류가 발생하면 디렉터리형 백업을 이용해 기존 Runtime과 MPA 관리 설정을 복구한다.
- rollback은 버전별 backup 안의 `runtime.zip` 무결성을 검증한 뒤 기존 Runtime과 필요 시 MPA 관리 설정을 복원한다.
- retention은 성공한 `runtime.zip` backup에만 적용하며 사용자 수동 백업·실패 백업은 보존한다.
- 기존 `runtime/` 디렉터리형 backup은 `campingtalk-proj`에서 모두 전환하며 rollback 호환을 제거한다.
- 이력 정리 명령은 release bundle, 등록된 대상의 deployment receipt·history·backup 후보를 읽기 전용으로 제시하고, 승인 정보와 apply가 있을 때만 삭제한다.

### 사용자 결정

- 성공 후 보관 형식 — 버전별 backup 디렉터리는 유지하고 `runtime.zip`만 보관한다. 배포 성공 및 검증 전에는 즉시 복구를 위해 임시 `runtime/` 디렉터리를 사용하고, ZIP 무결성을 확인한 뒤 해당 개별 파일을 삭제한다.
- 기존 backup 전환 실패 — 실패한 `runtime/`은 보존하고, agent가 실패 원인·경로·다음 안전한 처리 선택지를 사용자에게 제시한다.
- 전환 이력 — `backup-metadata.json`에 `archive_migration` 상태·시각·archive 경로·원본 삭제 여부·실패 원인을 기록한다.
- 이력 정리 — 사용자가 정리 요청할 때만 전체 후보를 확인한다. 기본 보관 수는 10개이며, apply 전에 대상·삭제 후보·보존 기준을 사용자에게 제시한다.

### 변경 불가 제약

- deployment dry-run·승인·rollback 책임자 게이트와 release ZIP의 불변성은 변경하지 않는다.
- 대상의 `workspace/`, `docs/`, agent 설정, 일반 소스는 배포·rollback에서 변경하지 않는다.
- 배포 성공 전에는 복구 가능한 원본을 삭제하거나 ZIP 하나에만 의존하지 않는다.

### 에이전트 가정

| 가정 | 근거 | 틀렸다면 |
|-----|------|---------|
| 사용자가 말한 ZIP은 대상별 Runtime 복구 백업을 뜻한다. | 대화가 `.mpa/backups/` 디렉터리형 백업 수에 관한 것이었다. | release bundle 또는 별도 보관 위치 요구사항을 다시 확정한다. |
| `campingtalk-proj`의 기존 backup은 모두 현재 관리형 `runtime/` 구조다. | 실제 3개 backup에서 `backup-metadata.json`과 `runtime/.mpa/runtime`을 확인했다. | 관리형이 아닌 backup은 보존하고 사용자에게 별도 처리 여부를 묻는다. |

### 결정 대기 항목 (Open Questions)

없음

---

## 실행 계획 (Implementation Plan)

### 사전 조사

- 현재 `deploy`는 배포 시작 직후 Runtime을 디렉터리에 복사하고, 검증·receipt 기록 후 marker를 작성해 최신 3개 디렉터리만 유지한다.
- 현재 `rollback`은 marker와 디렉터리 내부의 `runtime/.mpa/runtime`·선택적 `runtime-config/config.yaml`을 직접 읽는다. 따라서 ZIP 보관에는 archive 검증·임시 해제와 기존 디렉터리 호환 분기가 필요하다.

### 구현 단계

- [x] Step 1 — version backup 내부 `runtime.zip`의 작성·무결성 검증·안전한 임시 해제 helper를 구현했다. / 이유: 성공 후 원본 `runtime/`을 지우기 전에 rollback 가능한 archive임을 증명해야 한다.
- [x] Step 2 — 성공 배포의 마지막 단계에서 `runtime/`을 임시 ZIP으로 아카이브하고 검증·원자 publish한 뒤 원본 `runtime/`만 삭제하도록 deploy·marker·retention을 갱신했다. / 이유: 버전별 backup metadata와 config snapshot을 유지한 채 파일 수만 줄인다.
- [x] Step 3 — rollback이 version backup 내부의 `runtime.zip`만 검증·복원하고 legacy `runtime/`을 거부하도록 변경했다. / 이유: 사용자 결정에 따른 ZIP 전용 Runtime backup 계약을 보장한다.
- [x] Step 4 — 기존 `campingtalk-proj` backup 3개를 전환하고, 실패한 원본은 보존·보고하도록 migration command와 회귀 테스트를 추가했다. / 이유: 기존 보관 파일을 안전하게 ZIP 구조로 맞춘다.
- [x] Step 5 — `history-cleanup` dry-run/apply command를 추가하고 deploy의 자동 backup retention 호출을 제거했다. / 이유: 사용자가 요청한 경우에만 전체 후보를 검토·승인한 뒤 이력을 정리한다.

### 예상 조용한 결정

- ZIP 내부 구조: `runtime/`의 상대 구조(`.mpa/runtime/…`)만 `runtime.zip`에 저장한다. / 권장: 버전별 marker와 config snapshot의 경로를 안정적으로 유지한다.
- 압축 실패 처리: 새 배포 중 archive 실패는 deployment transaction을 실패 처리하고 기존 Runtime·MPA 관리 설정을 복원한다. 기존 backup 전환 실패는 원본 `runtime/`을 보존하고 사용자에게 보고한다. / 권장: 복구 가능한 원본을 자동 삭제하지 않는다.
- rollback: backup 디렉터리 내부의 `runtime.zip`을 임시 해제하고 marker·archive checksum을 검증한 경우에만 Runtime 교체를 시작한다. / 권장: 손상 ZIP이 현재 Runtime을 건드리지 못하게 한다.
- retention: marker와 검증된 `runtime.zip`이 있는 version backup만 성공 백업으로 세고 최신 3개를 유지한다. / 권장: 실패 transaction과 사용자 수동 snapshot은 자동 삭제하지 않는다.
- 이력 정리: release 생성·deploy·rollback은 기존 이력을 자동 삭제하지 않는다. 명시 `history-cleanup` 요청만 10개 보관 기준으로 전체 후보를 계산하고, 사용자 승인 뒤 apply한다. / 권장: 일반 작업에서 과거 복구·감사 근거가 사라지는 것을 방지한다.

### 수정 대상 파일

| 파일 경로 | 변경 내용 |
|---|---|
| `release_manager.py` | version backup 내부 `runtime.zip` lifecycle, migration, ZIP 전용 rollback, retention 구현 |
| `tests/test_release_manager.py` | runtime.zip backup·migration 실패 보존·ZIP rollback·retention 회귀 테스트 |
| `map-product-rules/deployment-coordination.md` | 성공 후 ZIP 보관과 rollback 계약 명시 |
| `workspace/memory/shared/architecture.md` | Runtime backup 보관 정책의 현재 상태 갱신 |

### 참고 파일 (수정 없음)

- `.mpa/runtime/inject/layer0_update.md` — 대상 업데이트 흐름의 결과 확인 기준
- `workspace/releases/<release-id>/manifest_<release-id>.json` — Runtime release ZIP과 대상 backup ZIP의 역할 분리 기준

### 반례 (이 계획이 실패할 수 있는 시나리오)

- ZIP 생성·검증·원본 삭제 중 저장 공간 또는 I/O 오류가 난다. → 구현 2·4단계에 포함: 새 배포는 기존 Runtime·MPA 관리 설정을 복원하고, 기존 backup 전환은 원본 `runtime/`을 보존한 뒤 사용자에게 보고한다.
- ZIP 파일이 손상됐는데 원본 `runtime/`을 먼저 삭제한다. → 구현 1·2단계에 포함: archive 작성 후 안전 해제·asset map·marker 검증이 통과한 경우에만 원본을 삭제한다.
- 손상 ZIP을 선택한 rollback이 현재 Runtime을 일부 교체한다. → 구현 3·4단계에 포함: ZIP 검증·임시 해제가 Runtime 교체보다 먼저 완료되고, 실패 시 현재 Runtime을 변경하지 않는 회귀 테스트를 둔다.
- retention이 실패 transaction의 디렉터리 또는 사용자 수동 snapshot을 삭제한다. → 구현 2·4단계에 포함: marker와 `runtime.zip`을 함께 확인하는 대상 한정 retention을 검증한다.

## 실행 TODO

### 구현·에이전트 검증

- [x] runtime.zip backup lifecycle, migration, rollback 구현을 완료했다.
- [x] 구현과 단위 테스트를 완료했다. `history-cleanup`은 release 10개, 대상 history·receipt 10개, 성공 Runtime backup 3개 보관을 기본값으로 하며 모든 일반 배포·업그레이드의 자동 삭제를 제거했다.
- [x] source 검증을 완료했다. Runtime source·dist asset은 변경하지 않아 동기화 대상이 없다.

### 사용자 결정·승인 필요

- [x] 요구사항 명세와 구현 계획을 승인했다.
- [ ] 실제 대상 배포 전 최종 확인 — source 변경만 완료했다. 릴리즈 생성·`campingtalk-proj` 배포는 사용자 명시 요청이 있을 때 진행한다.

## 검증 결과

### 검증 체크리스트

- [x] 정상 경로: 성공 배포가 version backup 내부에 검증된 `runtime.zip`만 남기며 ZIP rollback이 이전 Runtime을 복원한다.
- [x] 실패 경로: ZIP archive 실패가 기존 Runtime을 복원하고, 기존 backup 전환 실패가 원본 `runtime/`을 보존·보고한다.
- [x] 엣지 케이스: 손상 ZIP rollback 거부, ZIP retention 대상 한정, 기존 `runtime/` backup 거부를 검증한다.
- [x] 이력 정리: dry-run이 전체 관리 후보만 제시하고 파일을 변경하지 않으며, apply는 승인 정보 없이는 거부되고 승인 뒤에만 후보를 삭제함을 검증한다.

### 완료 시 문서 업데이트 대상

- [x] `workspace/memory/shared/architecture.md` — Runtime deploy backup의 보관·rollback 계약 갱신
- [x] `map-product-rules/deployment-coordination.md` — ZIP 보관 정책 갱신

## 운영 시 안내 사항

| 영향 대상 | 운영상 달라지는 점 | 사용자 안내 |
|---|---|---|
| Runtime 배포 대상 | 새 성공 배포부터 version backup 내부의 `runtime.zip`이 남는다. | `runtime/`은 검증 성공 뒤 삭제하며, ZIP 전환 실패분은 보존·보고한다. |

## 실행 중 변경 기록

| 변경 내용 | 이유 | 명세 영향 |
|---|---|---|
| ZIP 변환 실패를 deployment 실패로 처리 | 독립 비평에서 archive 미완료 상태의 retention·rollback 의미가 모호함을 확인 | 없음 |
| ZIP retention의 전체 무결성 검증은 이번 범위에서 제외 | 사용자 결정: marker 기반 retention은 유지 | 없음 |
| rollback 승인 필수값 검증과 receipt 실패 뒤 ZIP 보존 추가 | 독립 검증에서 즉시 수정 필요로 확인 | 없음 |
| 승인 정보 미준비 시 사용자에게 승인 요청하도록 운영 절차 명시 | 사용자 지시: 작업을 차단하지 말고 필요한 승인을 요청해 처리 | 없음 |
| ZIP 보관 단위를 version backup 전체에서 내부 `runtime/`으로 변경 | 사용자 정정: version backup metadata와 폴더는 유지 | 요구사항 명세 갱신·재승인 |
| backup metadata에 ZIP 전환 결과를 기록 | 사용자 결정: 별도 receipt 대신 backup-metadata.json 사용 | 요구사항 명세 갱신·재승인 |
| 자동 retention을 명시 요청형 `history-cleanup`으로 전환 | 사용자 결정: 정리 요청 시 전체 후보 확인·승인 후 일괄 처리 | 요구사항 명세 갱신·재승인 |

## 명세 변경 이력

| 승인 시각 | 이전 체크섬 | 새 체크섬 | 변경 요약 |
|---|---|---|---|

### 구현 후 발견

| 항목 | 유형 | 발견 맥락 | 처리 경로 |
|---|---|---|---|
| (결과를 경험한 후 채워짐) | 명세 밖 보완 / 명세 변경 / 신규 작업 항목 | 왜 보기 전에는 보이지 않았는가 | 실행 기록 갱신 / 승인 이력 갱신 / INDEX.md 등록 |

**파생된 작업 항목:**

- 없음
| 2026-08-25T05:53:11Z | reqspec-v1:3c801543fd407a81 | reqspec-v1:7d99b6e7eacce7f7 | version backup 내부 runtime만 runtime.zip으로 보관하고 ZIP 전용 rollback 및 기존 campingtalk-proj backup 전환을 적용 |
| 2026-08-25T06:15:28Z | reqspec-v1:7d99b6e7eacce7f7 | reqspec-v1:8903c919c9780138 | backup-metadata.json에 runtime.zip 전환 성공·실패 상태와 원본 보존 여부를 기록 |
| 2026-08-25T06:31:10Z | reqspec-v1:8903c919c9780138 | reqspec-v1:14afb0f1d5818993 | 이력 정리는 release·deploy 자동 실행이 아니라 사용자 명시 요청의 전체 후보 확인과 승인 apply로 제한 |
