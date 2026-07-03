---
태스크: version_timestamp_precision
생성일: 2026-07-03
타입: minor
실패비용: minor
상태: 완료 승인
승인해시: 770114cacf711632
---
**목적:** 버전 관련 필드(`current_version`, `installed_at`, `upgraded_at`)에 날짜만이 아니라 시분초까지 기록해, 같은 날 여러 번 갱신되는 경우도 구분 가능하게 한다.
**요청:** "버젼을 시분초도 추가해줘" — 범위·형식 확인 질문에 대해 "current_version + installed_at/upgraded_at 모두" / "YYYY-MM-DD HH:MM:SS" 형식으로 답변받음.

### 핵심 기능
- `.mpa-workspace/.mpa-version`의 `current_version`을 `YYYY-MM-DD HH:MM:SS` 형식으로 갱신.
- `core/agent_rules_detail.md`의 current_version 갱신 지시문을 시분초 포함 형식으로 수정.
- `install.py`의 `write_version()`이 `installed_at`/`upgraded_at`을 `datetime.date.today()`(날짜만) 대신 `YYYY-MM-DD HH:MM:SS`로 기록하도록 수정.

### 사용자 결정
- 적용 범위: current_version + installed_at/upgraded_at 모두
- 표기 형식: `YYYY-MM-DD HH:MM:SS` (공백 구분)

### 에이전트 가정
- 기존에 이미 기록된 과거 이력 값(`workspace/.mpa-version-info`의 installed_at: 2026-06-01 등, `dist/workspace/.mpa-version-info`의 예시값)은 실제 시각 정보가 없으므로 소급 조작하지 않는다 — 로직 변경은 **앞으로의** 기록부터 적용한다.
- `install.py`의 `installed_at`/`upgraded_at` 파싱(`line.split(":", 1)`)은 값에 콜론이 포함돼도 최초 1개 콜론만 분리하므로 시분초 추가로 인한 파싱 깨짐은 없음 (확인 완료).

### 구현
1. [x] `.mpa-workspace/core/agent_rules_detail.md` — current_version 갱신 지시문 형식 갱신
2. [x] `.mpa-workspace/.mpa-version` — current_version을 현재 시각(시분초 포함)으로 갱신
3. [x] `install.py` — `write_version()`의 `today` → `now_str`(시분초 포함)으로 교체, 문법 검사 및 install/upgrade 시뮬레이션으로 파싱 회귀 없음 확인
4. [x] dist 동기화 확인 (agent_rules_detail.md·.mpa-version diff 일치, install.py는 dist 미보관 대상이라 해당 없음)
