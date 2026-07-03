---
태스크: minor_initial_status_rename
생성일: 2026-07-03
타입: minor
실패비용: minor
상태: 완료 승인
승인해시: e4da882178e7d2d7
---
**목적:** minor 태스크 초기 상태명 "메모"를 "작성 중"으로 변경하고, 그 김에 발견된 `minor_plan_template.md` 기본값 버그와 `plan_hash.py` `VALID_STATUS` 누락을 함께 바로잡는다.
**요청:** "메모는 단계에 적합하지 않은것 같은데 다른 용어가 없어?" → 확인 질문에 "작성 중" 선택.

### 핵심 기능
- `core/agent_rules.md`의 minor 3단계 모델 표기 `메모 [자동 승인] → 구현 중 → 완료 승인` → `작성 중 [자동 승인] → ...`으로 용어 교체.
- `hooks/plan_hash.py`의 `ALLOWED_STATUSES`(approve 허용 상태 집합)에서 `"메모"` → `"작성 중"` 교체.
- `templates/minor_plan_template.md`의 기본값 `상태: 구현 중`(버그) → `상태: 작성 중`으로 수정 — approve 명령이 즉시 거부되던 기존 버그도 함께 해소.

### 사용자 결정
- 상태명: "작성 중" (기존 상태들의 "~중" 명명 패턴과 일치, "설계"라는 단어를 쓰지 않아 minor의 "설계 결정 불필요" 철학과 충돌하지 않음)

### 에이전트 가정
- `hooks/plan_hash.py`의 `VALID_STATUS` 집합(현재 `{"설계 중", "설계 완료", "구현 중", "검증 중", "테스트 중", "검토 완료", "완료 승인"}`)에는 애초에 "메모"가 빠져 있어 `audit` 명령이 minor 초기 상태를 "유효하지 않음"으로 잘못 판정하는 별개 결함이 있었다. 이번 용어 교체와 동시에 `VALID_STATUS`에 "작성 중"을 추가해 함께 바로잡는다 — 이름을 바꾸면서 방치하면 새 이름도 같은 결함을 그대로 물려받기 때문에 분리하지 않고 같은 태스크에서 처리한다.
- `guidebook.md`·`README.md`는 minor 흐름을 설명할 때 "메모"라는 단어를 직접 쓰지 않아(각각 "구현 중 → 완료 승인", "최소 plan.md를 만들고 approve 자동 실행"로 서술) 수정 대상에서 제외한다 (grep으로 확인).

### 구현
1. [x] `.mpa-workspace/core/agent_rules.md` — 미니 3단계 모델 표기 용어 교체
2. [x] `.mpa-workspace/hooks/plan_hash.py` — `ALLOWED_STATUSES`의 "메모"→"작성 중" 교체 + `VALID_STATUS`에 "작성 중" 추가
3. [x] `.mpa-workspace/templates/minor_plan_template.md` — 기본값 `상태: 구현 중` → `상태: 작성 중`
4. [x] 기능 테스트 — 템플릿 그대로 복사해 `approve` 실행 시 정상 통과 및 `audit` 결과 `invalid: []` 확인, dist 동기화 3파일 diff 일치 확인, `.mpa-version` 갱신
