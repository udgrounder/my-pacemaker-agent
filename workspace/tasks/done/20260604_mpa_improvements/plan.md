---
태스크: mpa_improvements
생성일: 2026-06-04
타입: major
실패비용: major
상태: 완료 승인
승인해시: ""
---
# 태스크: MPA 시스템 비평 반영 개선
**상태:** 검토 완료  
**목적:** 논리적 비평에서 도출된 8개 항목을 구현 가능한 범위에서 수정한다

---

## 실패 비용 추정

| 축 | 판단 | 레벨 |
|----|------|------|
| 심각도 | MPA 시스템 → 모든 미래 세션 영향 | 높음 |
| 발견 가능성 | hooks는 Python — 로컬 테스트 가능, md는 즉시 확인 | 보통 |
| 가역성 | git reset으로 되돌릴 수 있음 | 높음 |

→ **자율성 레벨 2** (초안 생성, 사용자 검토 후 적용)

---

## 에이전트 보고

### 사용자 결정 필요

- **[가치 결정]** `.md` 파일 게이팅 옵션(`MPA_GATE_MD`)을 기본 `off`로 둘지 `block`으로 둘지  
  - [off 기본] → 기존 동작 유지, 소스 .md도 열려 있음. 현재 사용자에게 영향 없음  
  - [block 기본] → 더 엄격하지만 기존 사용자 워크플로우가 깨질 수 있음  
  - → **기본값 `off` 방향으로 설계됨**

### 에이전트 가정

| 가정 | 근거 | 틀렸을 때 영향 |
|------|------|--------------|
| dist/ 동기화는 파일 복사로 충분 | 현재 dist/도 동일 구조 | 빌드 스크립트가 따로 있으면 무시될 수 있음 |
| `workspace/tasks/.current_task` 경로가 사용 안 됨 | ls 결과 없음 | 충돌 없음 |
| hooks는 Python 3.6+ 호환 | 기존 코드 스타일 | walrus operator 등 신문법 쓰면 에러 |

---

## 태스크 분리

구현 단계 8개, 독립 단위 3개 → `sub_` 파일로 분리

| 서브태스크 | 파일 | 독립성 |
|----------|------|--------|
| sub_gate.md | code_gate.py + session_start.py | Python 코드 변경 |
| sub_rules.md | agent_rules.md | 규칙 문서 변경 |
| sub_critique.md | layer1_critique.md | 비평 세션 명확화 |

---

## 구현 단계 (전체 체크리스트)

### [sub_gate] code_gate.py

- [ ] **Step 1** — session_start.py: 다중 active 태스크 시 선택 UX 개선  
  이유: 여러 태스크가 있을 때 사용자가 작업할 태스크를 선택하면, 그 태스크의 상태(plan.md)에 따라 다음 단계가 결정된다. 이 흐름은 agent_rules.md "작업 재개" 섹션에 이미 존재하나, session_start.py의 출력이 선택을 유도하기에 충분하지 않음  
  - active 태스크가 2개 이상이면 각 태스크의 이름 + 상태(plan.md 상태) + 승인 여부를 목록으로 출력  
  - "작업할 태스크를 선택해 주세요" 안내 문구 추가  
  - `.current_task` 파일 불필요 — 선택 후 흐름은 agent_rules.md "작업 재개"가 담당  
  - code_gate.py 변경 없음 (단일 책임 유지)

### [sub_rules] agent_rules.md

- [ ] **Step 2** — 라우팅 표 보완  
  이유: 모호한 발화가 케이스 α로만 수렴하는 문제 완화  
  - 패턴 추가: 성능/느림 → 버그 또는 리팩터링 분기 유도  
  - 케이스 α 처리를 더 구체화 (분기 질문 개선)

- [ ] **Step 3** — INDEX.md 역할 명확화 + 동기화 전략 변경  
  이유: 매 세션마다 INDEX.md와 폴더 구조를 완전 동기화하면 불필요한 토큰 비용 발생  
  - **전략:** `workspace/tasks/active/` 폴더를 primary source로 삼는다. INDEX.md는 cache이며 전체 재동기화하지 않는다  
  - **세션 시작:** active/ 폴더를 직접 읽어 진행 중 태스크를 파악 (session_start.py가 이미 이렇게 동작 — 규칙 문서에도 명시)  
  - **불일치 확인 범위:** active/ 폴더에 있는데 INDEX.md에 없는 항목만 확인 (누락 탐지). 반대(INDEX에 있는데 폴더 없음)는 자연스럽게 완료 처리된 케이스로 간주  
  - **업데이트 시점:** 태스크 생성 시 / 태스크 완료(done 이동) 시 / Layer 2 체크포인트 시에만 INDEX.md 업데이트. 그 외 시점에서는 읽기 전용

- [ ] **Step 4** — upgrade candidates 처리 워크플로우 구체화  
  이유: 후보 등록 → 실제 반영 사이클이 닫혀 있지 않음. 단, 반영 작업은 my-pacemaker-agent 프로젝트 전용이므로 배포 파일(agent_rules.md)이 아닌 이 프로젝트의 project_rules.md에 추가한다  
  - **agent_rules.md (배포):** 변경 없음 — "upgrade-candidates에 기록한다"까지가 배포 범위  
  - **workspace/project_rules.md (이 프로젝트 전용):** 아래 내용 추가  
    - 세션 시작 시 upgrade-candidates 파일 고지 후 사용자가 검토를 승인하면 → MPA 시스템 파일 수정 태스크로 분리 등록  
    - 반영 완료 후 해당 upgrade-candidates 파일 삭제

### [sub_critique] layer1_critique.md

- [ ] **Step 5** — 동일 스레드 비평 허용 조건 명확화  
  이유: "새 스레드 필수"가 이 환경에서 불가능하다는 현실을 솔직하게 반영  
  - 새 스레드가 가능한 환경 vs 불가능한 환경 명시  
  - 동일 스레드 비평 시 적용해야 할 추가 제약 (역할 전환 선언, 설계 내용 불참조 등)

---

## 검증 체크리스트

- [ ] `session_start.py` — 다중 active 태스크 시 상태 목록 + 선택 안내 출력 확인
- [ ] `agent_rules.md` — INDEX.md 동기화 전략 변경이 기존 완료 처리 흐름과 충돌 없음
- [ ] dist/ 동기화 완료

---

## 반례

- 사용자가 태스크 선택 없이 바로 작업 지시 → agent_rules.md "작업 재개" 로직이 active 1개면 자동 선택, 2개 이상이면 선택 요청 — 기존 규칙으로 처리됨
- `MPA_GATE_MD` 옵션을 모르는 기존 사용자 → 기본값 `off`이므로 기존 동작과 동일

---

## 완료 시 문서 업데이트 대상

- `dist/` 동기화 (모든 수정 파일)
- `.mpa-workspace/.mpa-version` 날짜 업데이트
