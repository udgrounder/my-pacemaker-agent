---
태스크: arcstudio_rule_absorption
생성일: 2026-07-03
타입: minor
실패비용: minor
상태: 완료 승인
승인해시: a066f71c42c2143d
---
**목적:** 외부 프로젝트(ArcStudio) 검토 과정에서 확인한 두 가지 아이디어를 MPA 규칙에 반영한다.
**요청:** "그래 1,2번 반영해줘" — 직전 턴에서 제안한 두 항목(① 스크립트 vs 지침 결정 기준표, ② 완료 보고 시 인용 근거 요구)을 MPA 파일에 적용.

### 핵심 기능
- `personas/mpa_system_designer.md`에 "스크립트화 여부 판단" 절 추가 — `hooks/*.py` 스크립트로 만들지 `.md` 지침으로 남길지 결정하는 기준표.
- `core/agent_rules.md` "작업 완료" 섹션에 완료 보고 시 근거(파일 인용·명령 출력 등)를 최소 1개 포함해야 한다는 공통 원칙 추가.
- `inject/layer1_implement.md`의 minor fast-path 완료 보고 템플릿(agent_rules.md와 동일 문구가 중복 존재)에도 동일 원칙 반영 — 불일치 방지.

### 사용자 결정
- 없음 (직전 턴에서 항목 2개와 배치 방향 합의됨)

### 에이전트 가정
- 항목 2(증거 인용 요구)는 minor·major 두 흐름 모두에 적용되는 공통 원칙이므로 `agent_rules.md` "작업 완료" 섹션 최상단(공통 원칙)에 배치하고, minor 절 안에서는 참조만 한다.
- `layer1_implement.md`는 기존에 동일 템플릿을 중복 보유하고 있어 별도 리팩터링(중복 제거) 없이 동일 문구만 추가한다 — 이번 태스크 범위는 중복 구조 정리가 아니다.
- 항목 1(스크립트화 기준)은 `.mpa-workspace/` 파일 수정 시 로드되는 `mpa_system_designer.md`에 배치한다.

### 구현
1. [x] `.mpa-workspace/personas/mpa_system_designer.md` — "스크립트화 여부 판단" 절 추가
2. [x] `.mpa-workspace/core/agent_rules.md` — "작업 완료" 섹션에 증거 인용 공통 원칙 추가
3. [x] `.mpa-workspace/inject/layer1_implement.md` — minor fast-path 완료 보고 템플릿에 동일 원칙 반영 (동일 문구 중복 위치 grep으로 확인, 추가 중복 없음)
4. [x] `dist/` 자동 동기화 확인 (diff 3파일 모두 일치) + `.mpa-version` current_version → 2026-07-03 갱신
