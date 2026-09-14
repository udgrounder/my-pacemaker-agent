# 태스크 내역서: MPA 문서 로딩·운영 코드 구조 개선

**작업일:** 2026-09-10
**계획서:** `plan.md`

---

## 변경 파일 목록

| 파일 경로 | 변경 유형 | 설명 |
|---|---|---|
| `tests/test_release_manager_compatibility.py` | 추가 | 기존 import·CLI·facade patch 계약을 고정하는 추출 전 회귀 검사 |
| `.mpa/runtime/core/agent_rules.md` | 수정 | 항상 로드하는 정책을 라우팅·불변 조건 중심으로 축약 |
| `.mpa/runtime/core/agent_rules_detail.md` | 수정 | 승인 기록·완료 처리의 조건부 상세 절차 추가 |
| `.mpa/runtime/inject/layer1_design.md` | 수정 | major 승인 직전 상세 절차 직접 참조 |
| `.mpa/runtime/inject/layer1_implement.md` | 수정 | minor 자동 승인 경로의 상세 절차 직접 참조 |
| `tests/test_structure_loading.py` | 추가 | 조건부 로드 경로와 core 크기 기준 회귀 검사 |
| `dist/.mpa/runtime/` | 동기화 | source Runtime 문서 변경 반영 |
| `mpa_ops/__init__.py` | 추가 | source-only 내부 운영 패키지 표시 |
| `mpa_ops/archive_io.py` | 추가 | ZIP 생성·검사·해제 책임 6개 함수 |
| `release_manager.py` | 수정 | 기존 ZIP helper facade를 내부 모듈에 연결 |
| `mpa_ops/issue_format.py` | 추가 | 이슈 형식 해석·정규화·identity helper 5개 함수 |
| `release_manager.py` | 수정 | 기존 이슈 형식 helper facade를 내부 모듈에 연결 |

---

## 상세 변경 내역

### `tests/test_release_manager_compatibility.py`

- **대상:** `ReleaseManagerCompatibilityTest`
- **위치:** 전체 파일
- **변경 유형:** 추가
- **내역:** sys.modules 등록에 의존하지 않는 spec loader, 저장소 밖 cwd의 CLI help, `_validate_zip_member`와 `_parse_issue_candidate` facade patch가 실제 호출 경로에 남는지를 검사한다.

### `.mpa/runtime/core/agent_rules.md`와 조건부 상세 문서

- **대상:** 작업 생성·승인 기록·완료 처리 정책
- **위치:** core, detail, design/implement inject
- **변경 유형:** 수정
- **내역:** major 설계의 반복 상세와 승인·완료 절차를 필요할 때 읽는 detail로 이동했다. minor는 `detail → common template` 직접 경로를 유지하며, core에는 라우팅·승인/완료 경계·INDEX 순서와 사용자 부담 최소화 원칙을 남겼다.

### `tests/test_structure_loading.py`

- **대상:** `StructureLoadingTest`
- **위치:** 전체 파일
- **변경 유형:** 추가
- **내역:** source/dist 양쪽의 새 detail 참조, minor의 design 비경유 경로, core 34,731바이트 기준선 미만을 검사한다.

### `mpa_ops/archive_io.py`와 `release_manager.py`

- **대상:** ZIP 생성·검사·해제 6개 helper
- **위치:** `mpa_ops/archive_io.py`, release_manager facade
- **변경 유형:** 추출
- **내역:** ZIP primitive를 source-only 내부 모듈로 옮기고, 기존 `_zip_runtime`, `_write_backup_archive`, `_zip_entries`, `_validate_zip_member`, `_archive_current_release`, `_extract_runtime` 이름과 시그니처는 facade로 보존했다. facade가 현재 tree/member validator와 ignore 값을 전달하므로 기존 monkey patch가 실행 경로에 남는다.

### `mpa_ops/issue_format.py`와 `release_manager.py`

- **대상:** 이슈 후보 해석·metadata 완전성·machine path 정규화·identity helper
- **위치:** `mpa_ops/issue_format.py`, release_manager facade
- **변경 유형:** 추출
- **내역:** 5개 형식 helper를 source-only 내부 모듈로 옮겼다. facade는 기존 정규식·marker·identity anchor를 호출 시 전달하며, 이슈 preflight·수집·이동·복구 transaction은 release_manager에 그대로 남긴다.

### 독립 구현 검토 보완

- **대상:** compatibility·structure loading 회귀와 내부 구조 문서
- **위치:** `tests/test_release_manager_compatibility.py`, `tests/test_structure_loading.py`, `docs/mpa-internal-structure.md`
- **변경 유형:** 검증 보강
- **내역:** 첫 독립 검토의 지적을 반영했다. source root import라는 기존 `project_config` 계약을 명시하고, 저장소 밖 cwd의 spec loader와 CLI를 별도 subprocess로 검사한다. 추출한 11개 facade의 dispatch와 policy callback 전달을 표 기반으로 고정했고, 실제 prepare-release artifact에서 `mpa_ops/`·source workspace·제품 규칙 파일이 빠지는지도 확인한다. Runtime 문서는 대표 요청 11개 라우팅, 양쪽 minor 직접 경로, source/dist 전체 file parity를 자동 검사한다.

---

## 요구사항 명세 대비 변경 사항

| 변경 | 이유 | 명세 영향 | 보고 |
|---|---|---|---|
| 호환 회귀 검사 추가 | 내부 모듈 분리 전에 기존 import·오류 주입 계약을 고정 | 없음 | 단계 종료 보고 |
| Runtime 문서 로딩 정리 | 항상 읽는 규칙을 축약하고 조건부 상세 경로를 명시 | 없음 | 단계 종료 보고 |
| ZIP helper 추출 | source-only archive_io로 책임을 분리하고 release_manager facade 유지 | 없음 | 단계 종료 보고 |
| 이슈 형식 helper 추출 | source-only issue_format으로 책임을 분리하고 release_manager transaction 유지 | 없음 | 단계 종료 보고 |

---

## 검증 포인트

- [x] 정상 경로 확인: spec loader와 CLI help가 성공함.
- [x] 실패 경로 확인: 주입한 ZIP member validator 오류가 staging을 정리하고 extraction failure로 변환됨.
- [x] plan.md 완료 기준 충족 여부: 기준선·추출 전 호환 계약 범위에서 충족. 구조 변경은 아직 미실행.
- [x] 정책 도달성 확인: source/dist 17개 관련 테스트 통과, minor 직접 경로와 완료 INDEX 계약 확인.
- [x] ZIP 추출 확인: release_manager 계열 회귀와 compatibility 3개 테스트 통과, 임시 bytecode cache의 문법 검사 통과.
- [x] 이슈 형식 추출 확인: release_manager 계열 회귀와 compatibility 3개 테스트 통과, 임시 bytecode cache의 문법 검사 통과.
- [x] 독립 검토 보완 확인: compatibility·구조 로딩 9개 테스트와 release_manager 91개 테스트 통과. source-root spec loader·CLI, 11개 facade, source-only package 경계, 11개 요청 라우팅, source/dist file parity를 확인.
- [x] 2차 독립 검토 보완 확인: ZIP leaf write/extract 예외를 deploy·rollback transaction에 직접 주입해 기존 Runtime, issue 원본, failed receipt 보존을 확인하는 compatibility 회귀 2개를 추가.
- [x] config 복구 보완 확인: migration 적용 뒤 ZIP leaf write 실패를 주입해 기존 Runtime·config 원문·failed receipt가 함께 복원됨을 확인.
