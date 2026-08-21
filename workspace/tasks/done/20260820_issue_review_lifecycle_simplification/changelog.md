# 태스크 내역서: 이슈 검토 생명주기 단순화

**작업일:** 2026-08-21
**계획서:** `plan.md`

---

## 변경 파일 목록

| 파일 경로 | 변경 유형 | 설명 |
|---|---|---|
| `release_manager.py` | 수정 | review·triage·resolve 명령을 제거하고 결정 기반 archive 명령으로 교체 |
| `tests/test_release_manager.py` | 수정 | 채택·기각·복구·완료 task 거부 검증 추가 |
| `map-product-rules/*.md` | 수정 | 사용자 검토 후 즉시 archive 흐름 반영 |
| `workspace/project_rules.md` | 수정 | 채택 작업 이관·기각 archive 절차 반영 |
| `workspace/issues/archived/2026/08/campingtalk-proj/*.md` | 추가 | 기각 근거를 포함한 현재 수집 이슈 archive |

## 상세 변경 내역

### `release_manager.py`

- **대상:** `archive_issue`, `task_plan_reference`, CLI parser
- **변경 유형:** 수정·삭제
- **내역:** 결정과 판단 근거를 이슈 파일에 먼저 기록한 뒤 archive한다. 채택은 실제 존재하는 `workspace/tasks/active/.../plan.md` 연결을 요구하고, 기각은 작업 연결을 허용하지 않는다.

### `tests/test_release_manager.py`

- **대상:** issue lifecycle tests
- **변경 유형:** 수정
- **내역:** 별도 receipt·triage·resolve 체인을 제거하고, 결정 결과 보존·archive 실패 복구·완료 작업 연결 거부를 검증한다.

## 요구사항 명세 대비 변경 사항

| 변경 | 이유 | 명세 영향 | 보고 |
|---|---|---|---|
| archive 전에 이슈 파일을 먼저 갱신하도록 순서 보완 | 독립 검토에서 archive에 근거 없는 파일이 남을 수 있는 창을 발견 | 없음 | 완료 |
| 채택 작업 연결을 active task로 한정 | 완료 작업 재연결 방지 | 없음 | 완료 |

## 검증 포인트

- [x] 정상 경로: 채택 archive와 기각 archive
- [x] 실패 경로: 기록 실패 시 inbox 원본 복원, 없는·완료 task 연결 거부
- [x] 전체 테스트: `python3 -m unittest discover -s tests -p 'test_*.py'` — 69 passed
