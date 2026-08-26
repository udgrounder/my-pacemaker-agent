---
태스크: circled_wiki_zip_backup_migration
생성일: 2026-08-25
타입: major
실패비용: critical
상태: 완료 승인
승인해시: reqspec-v1:4604d3eb4888948d
승인대상: 요구사항 명세
---

# 작업 계획서: campingtalk-wiki 기존 Control Plane 백업의 ZIP 전환

**파생 출처:** zip_runtime_backups — 성공 배포 백업의 ZIP 보관 원칙을 campingtalk-wiki의 별도 Control Plane 백업 체계에도 적용한다.

## 요구사항 명세

### 요청 기준

초기 조사에서 `.circled-wiki-backups/`를 잘못 요청 대상으로 판단했다. 사용자가 의도한 대상은 `campingtalk-proj/.mpa/backups/`의 version backup 내부 `runtime/`이다. 이 작업은 실행하지 않는다.

### 목적

오판된 별도 작업을 보존 기록으로 남기고 실행하지 않는다.

### 범위·제외 범위

- 범위: 없음. 실제 요구사항은 `zip_runtime_backups`에서 처리한다.
- 제외 범위: campingtalk-wiki의 모든 파일과 백업.

### 완료 기준

- 각 기존 디렉터리 backup은 완전한 ZIP을 만든 뒤 구조와 파일 checksum을 검증한 경우에만 원본 디렉터리를 삭제한다.
- 하나라도 ZIP 생성·검증·원본 삭제에 실패하면 해당 디렉터리는 보존하고, 이미 성공 전환된 ZIP을 훼손하지 않으며 사용자에게 실패 목록·원인·다음 조치를 알린다.
- 이후 updater는 새 backup을 ZIP으로 작성하고, rollback은 ZIP backup만 복원한다.
- `manifest.json`의 `last_backup`이 전환된 ZIP 경로를 가리키며 rollback 검증과 설치된 Runtime의 관련 자동 테스트가 통과한다.

### 사용자 결정

- 보관 형식 — 모든 기존 디렉터리 backup을 ZIP으로 전환하고, 검증 성공한 원본 디렉터리는 삭제한다.
- 호환성 — 디렉터리형 rollback 호환은 제거한다.
- 실패 처리 — 자동 차단·삭제 대신 원본을 보존하고 사용자에게 명시적으로 알려 다음 처리를 승인받는다.

### 변경 불가 제약

- ZIP 검증 전에는 어떤 원본 backup 디렉터리도 삭제하지 않는다.
- ZIP 전환 실패가 다른 backup의 전환·복구 가능성을 손상시키지 않는다.
- 대상의 사용자 소유 `knowledge/`, `workspace/`, 일반 소스와 현재 `.circled-wiki/` Control Plane은 전환 작업에서 변경하지 않는다.

### 에이전트 가정

| 가정 | 근거 | 틀렸다면 |
|---|---|---|
| `.circled-wiki-backups/`의 55개 디렉터리는 모두 Control Plane rollback backup이다. | updater가 같은 경로에 `_backup_operating_system()`으로 생성하고 manifest가 이를 참조한다. | marker/구조 검사에서 제외하고 사용자에게 별도 처리 여부를 묻는다. |
| 설치된 `.circled-wiki/runtime`이 이 대상의 updater source다. | portable CLI가 해당 경로를 Python import 경로로 사용한다. | 별도 source checkout을 찾아 그곳에서 수정 후 정식 배포한다. |

### 결정 대기 항목 (Open Questions)

없음

## 실행 계획 (Implementation Plan)

### 사전 조사

- 대상은 MPA Runtime이 아니라 Circled Wiki Control Plane이며 `.circled-wiki-backups/` 아래에 디렉터리 backup 55개와 ZIP 파일 0개를 보관한다.
- 현재 `bootstrap.py`의 `_backup_operating_system()`과 `rollback_control_plane()`은 각각 `copytree`와 디렉터리 `copytree`를 사용한다. `manifest.json`의 `last_backup`도 디렉터리를 참조한다.

### 구현 단계

- [ ] Step 1 — ZIP 생성·안전 검증·임시 해제 helper와 ZIP 전용 rollback을 구현하고 관련 테스트를 추가한다. / 이유: 새 backup과 rollback의 계약을 먼저 전환한다.
- [ ] Step 2 — 기존 55개 backup을 하나씩 임시 ZIP으로 만들고 entry·checksum 검증 후 원자 publish한다. / 이유: 실패한 archive가 정상 backup처럼 보이지 않게 한다.
- [ ] Step 3 — 각 ZIP publish 뒤에만 대응 디렉터리를 삭제하고, manifest의 `last_backup` 참조를 ZIP으로 갱신한다. / 이유: 삭제 전 rollback 가능한 archive와 참조 무결성을 보장한다.
- [ ] Step 4 — 전환 결과·ZIP rollback·실패 보존을 검증하고, 실패가 있으면 사용자 승인 대기 상태와 구체적 실패 목록을 남긴다. / 이유: 실패를 자동 삭제나 조용한 중단으로 처리하지 않는다.

### 예상 조용한 결정

- ZIP 파일명: 기존 디렉터리 이름에 `.zip`을 붙인다. / 권장: manifest와 운영자가 대응 관계를 바로 알 수 있다.
- 실패 시 성공분 처리: 이미 검증·publish된 ZIP과 원본 삭제 결과는 유지하고 실패한 항목만 디렉터리로 남긴다. / 권장: 대량 전환을 되돌리느라 복구본을 다시 늘리지 않는다.

### 수정 대상 파일

| 파일 경로 | 변경 내용 |
|---|---|
| `campingtalk-wiki/.circled-wiki/runtime/circled_wiki/core/bootstrap.py` | ZIP backup 작성, 검증, ZIP 전용 rollback 및 실패 보고 계약 |
| `campingtalk-wiki/.circled-wiki/runtime/.../tests` | ZIP 생성·rollback·전환 실패 보존 회귀 테스트 |
| `campingtalk-wiki/.circled-wiki/OPERATING_RULES.md` | Control Plane backup의 ZIP 전용 계약 갱신 |
| `campingtalk-wiki/.circled-wiki/manifest.json` | 마지막 backup 참조를 전환된 ZIP으로 갱신 |

### 반례 (이 계획이 실패할 수 있는 시나리오)

- ZIP write 중 저장 공간 또는 I/O 오류가 난다. → Step 2·4에 포함: temp archive만 정리하고 원본 디렉터리를 보존·보고한다.
- ZIP은 열리지만 파일이 누락되거나 손상됐다. → Step 2에 포함: entry와 checksum이 전부 맞을 때만 publish·원본 삭제한다.
- `last_backup`이 디렉터리를 참조한 상태로 전환이 끝난다. → Step 3에 포함: 참조 대상 ZIP 존재·검증을 확인한 뒤 manifest를 갱신한다.

## 실행 TODO

### 구현·에이전트 검증

- [ ] ZIP 전용 backup·rollback 구현 및 대상 규칙 갱신
- [ ] 기존 backup 전환 및 manifest 참조 갱신
- [ ] 자동 테스트와 대상 ZIP inventory 검증

### 사용자 결정·승인 필요

- [x] ZIP 전환, 디렉터리 rollback 제거, 실패 시 사용자 알림 원칙을 승인했다.
- [ ] 전환 실패가 있을 때 개별 실패 backup의 재시도·보존·삭제를 사용자와 결정한다.

## 검증 결과

### 검증 체크리스트

- [ ] 정상 경로: 모든 성공 backup이 ZIP이고 기존 디렉터리는 없다.
- [ ] 실패 경로: 실패한 backup 디렉터리가 보존되고 사용자에게 정확한 실패 정보가 제공된다.
- [ ] 엣지 케이스: manifest `last_backup`과 ZIP rollback이 일치한다.

### 완료 시 문서 업데이트 대상

- [ ] `campingtalk-wiki/.circled-wiki/OPERATING_RULES.md` — ZIP 전용 backup·rollback 계약

## 운영 시 안내 사항

| 영향 대상 | 운영상 달라지는 점 | 사용자 안내 |
|---|---|---|
| campingtalk-wiki 운영자 | rollback 입력은 `.zip` backup만 허용한다. | 디렉터리 backup은 전환 성공 후 삭제되며, 전환 실패분은 명시적 처리 결정을 기다린다. |

## 실행 중 변경 기록

| 변경 내용 | 이유 | 명세 영향 |
|---|---|---|
| 대상 오인으로 구현하지 않고 완료 보관 | 실제 대상은 별도 `zip_runtime_backups` 태스크이며, campingtalk-wiki 백업 변경을 방지 | 실행 취소 기록 |
| 사용자 명시 완료 승인 | 대상 오인 기록을 보관하고 active 목록에서 제거 | 없음 |

## 명세 변경 이력

| 승인 시각 | 이전 체크섬 | 새 체크섬 | 변경 요약 |
|---|---|---|---|

| 2026-08-26T11:45:28Z | reqspec-v1:859becbcef649291 | reqspec-v1:4604d3eb4888948d | 사용자가 대상 오인 태스크의 실행 취소와 완료 보관을 확인 |
### 구현 후 발견

| 항목 | 유형 | 발견 맥락 | 처리 경로 |
|---|---|---|---|
| (결과를 경험한 후 채워짐) | 명세 밖 보완 / 명세 변경 / 신규 작업 항목 | 왜 보기 전에는 보이지 않았는가 | 실행 기록 갱신 / 승인 이력 갱신 / INDEX.md 등록 |

**파생된 작업 항목:**

- 없음
