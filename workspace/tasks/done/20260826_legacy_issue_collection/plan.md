---
태스크: legacy_issue_collection
생성일: 2026-08-26
타입: major
실패비용: major
상태: 완료 승인
승인해시: reqspec-v1:13acc55b17e425ad
승인대상: 요구사항 명세
---

# 작업 계획서: 메타데이터 없는 issue 수집 지원

**파생 출처:** campingtalk-proj Runtime 업그레이드 중 legacy issue 수집이 `issue metadata is missing`로 배포를 되돌린 문제

---

## 요구사항 명세

### 요청 기준

사용자는 “이슈 수집은 메타 데이터가 없어도 무조건 해줘”라고 결정했다. 현재 legacy Markdown issue 두 건이 메타데이터 부재로 Runtime 업그레이드를 막고 있다.

### 목적

legacy 형식 issue도 안전 검사와 원자적 이동을 유지한 채 source inbox로 수집하고, 메타데이터 부재가 Runtime 배포 실패 원인이 되지 않게 한다.

### 범위·제외 범위

- 범위: `release_manager.py`의 update issue 수집에서 metadata 없는 issue를 원문 그대로 inbox로 먼저 수집한 뒤, 수집된 inbox 사본에만 legacy 메타데이터를 추가하고 성공·실패 동작을 자동 테스트한다.
- 제외 범위: 비밀값·절대 경로 안전 검사 완화, 중복 수집 방지 제거, 기존 metadata issue의 스키마 변경, 대상 프로젝트의 일반 소스 수정.

### 완료 기준

- metadata 없는 Markdown issue가 Runtime deploy와 함께 원문 그대로 inbox로 수집된 뒤 inbox 사본에 legacy 메타데이터가 추가되며 deploy가 성공한다.
- metadata가 있는 issue의 기존 수집·중복 방지·롤백 동작은 유지된다.
- credential-like 값 또는 절대 경로를 포함한 issue는 계속 수집 거부된다.
- 수정 Runtime으로 새 immutable release를 만들고 campingtalk-proj 업그레이드를 재시도한다.

### 사용자 결정

- legacy issue는 metadata가 없어도 무조건 수집한다 — 업그레이드 차단 사유로 삼지 않는다.

### 변경 불가 제약

- 수집은 원자적으로 처리하고, 실패 시 이미 이동한 issue를 원복한다.
- Runtime 배포 본체의 검증·백업·rollback 보장은 유지한다.
- 안전 검사에 실패한 issue는 자동 수집하지 않는다.

### 에이전트 가정

| 가정 | 근거 | 틀렸다면 |
|---|---|---|
| legacy issue에는 비밀값·절대 경로가 없다 | 현재 두 후보 파일을 검사했고 관련 오류가 아니었다 | 안전 검사로 배포가 계속 중단되며 사용자에게 해당 issue 처리를 요청한다 |
| 사용자 요청은 수집 후 inbox 사본의 legacy metadata 추가를 허용한다 | inbox lifecycle은 metadata 기반이므로 수집 후 형식화가 필요하다 | metadata 없는 파일을 그대로 보관하는 별도 수집 경로를 설계한다 |

### 결정 대기 항목 (Open Questions)

- 없음

---

## 실행 계획 (Implementation Plan)

### 사전 조사

- `collect_update_issues_transaction`, `read_issue`, 이동·롤백 흐름과 관련 회귀 테스트를 확인한다.

### 구현 단계

- [x] Legacy Markdown body에서 결정론적 fallback metadata를 생성하는 정규화 경로를 추가한다.
- [x] 수집 대상 metadata가 없으면 원문을 destination inbox로 먼저 원자 이동하고, 이동 확인 뒤 destination inbox 사본에 metadata를 추가하도록 수집 경로를 확장한다.
- [x] metadata issue의 기존 검증과 secret/path 검사, 중복 검사, rollback을 유지한다.
- [x] legacy metadata 없는 issue가 deploy를 막지 않고 먼저 수집된 뒤 inbox 사본에 metadata가 추가되는 회귀 테스트를 추가한다.
- [x] 전체 release manager 테스트와 release audit을 실행한다. 새 Runtime package는 변경 대상이 아니어서 기존 최신 immutable release를 사용한다.
- [x] 검증된 최신 release로 campingtalk-proj deployment dry-run과 deploy를 재시도한다.

### 예상 조용한 결정

- legacy canonical key: 파일 본문 SHA-256 기반의 안정적 `legacy-` key를 사용한다. 동일 본문 재수집을 중복으로 감지하기 위해서다.

### 수정 대상 파일

| 파일 경로 | 변경 내용 |
|---|---|
| `release_manager.py` | legacy issue 정규화 및 수집 경로 확장 |
| `tests/test_release_manager.py` | metadata 없는 issue 배포·수집 회귀 테스트 |
| `workspace/releases/<new-release-id>/` | 수정 Runtime의 불변 release 산출물 |

### 참고 파일 (수정 없음)

- `map-product-rules/deployment-coordination.md` — backup·rollback·issue 수집 불변식
- `workspace/issues/archived/2026/08/campingtalk-proj/*.md` — legacy issue의 기존 사례

### 반례 (이 계획이 실패할 수 있는 시나리오)

- metadata 없는 파일이 동일 파일명으로 이미 archive되어 있음 → 구현 단계에서 기존 이름 충돌 검사를 유지해 수집을 멈추고 source를 보존한다.
- legacy issue에 credential 또는 절대 경로가 있음 → 구현 단계에서 기존 `check_issue_text` 검사를 먼저 실행해 안전하게 거부한다.

---

## 실행 TODO

### 구현·에이전트 검증

- [x] legacy issue 원자 수집 후 inbox metadata 추가 구현
- [x] 자동 테스트와 release audit 실행
- [x] campingtalk-proj Runtime 업그레이드 재시도

### 사용자 결정·승인 필요

- [ ] 이 계획의 구현 승인

## 검증 결과

### 검증 체크리스트

- [x] 정상 경로: legacy issue가 deploy와 함께 inbox로 수집된 뒤 inbox 사본에 metadata가 추가된다. (실제 2건 수집 확인)
- [x] 실패 경로: 안전 검사 또는 수집 이동 실패 시 Runtime과 source issue가 복구된다. (자동 테스트 통과)
- [x] 엣지 케이스: 기존 metadata issue의 중복 identity 검사가 유지된다. (자동 테스트 통과)

### 완료 시 문서 업데이트 대상

- [ ] 없음 — 배포 도구의 동작은 release receipt와 테스트로 검증한다.

## 운영 시 안내 사항

| 영향 대상 | 운영상 달라지는 점 | 사용자 안내 |
|---|---|---|
| Runtime 업그레이드 대상 | legacy issue가 metadata 없이도 자동 수집된다 | 민감정보·절대 경로가 없는지 기존처럼 확인한다 |

## 실행 중 변경 기록

| 변경 내용 | 이유 | 명세 영향 |
|---|---|---|
| (구현 중 채움) |  | 없음 / 확인 필요 |

## 명세 변경 이력

| 승인 시각 | 이전 체크섬 | 새 체크섬 | 변경 요약 |
|---|---|---|---|

### 구현 후 발견

| 항목 | 유형 | 발견 맥락 | 처리 경로 |
|---|---|---|---|
| (결과를 경험한 후 채워짐) | 명세 밖 보완 / 명세 변경 / 신규 작업 항목 | 왜 보기 전에는 보이지 않았는가 | 실행 기록 갱신 / 승인 이력 갱신 / INDEX.md 등록 |

**파생된 작업 항목:**
- 없음
