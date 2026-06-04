# Changelog — 프로젝트 확장 지점 구축

## 신규 파일

### `dist/.mpa-workspace/templates/project_rules_template.md`
- 프로젝트 고유 규칙 파일 템플릿
- 섹션: 라우팅 힌트 / 기본 자율성 레벨 / 금지 패턴 / 행동 규칙

### `workspace/project_rules.md`
- 이 프로젝트(my-pacemaker-agent)용 초안
- MPA 시스템 파일 수정 라우팅 힌트 + dist/ 동기화 규칙 포함

## 수정 파일

### `dist/.mpa-workspace/core/agent_rules.md`
- 세션 시작 루틴: `workspace/project_rules.md` 읽기 1번으로 추가
- 라우팅 판단: project_rules.md 우선 적용 안내 추가

### `dist/.mpa-workspace/inject/layer1_design.md`
- "작업 시작 전 읽을 파일" 1번에 `workspace/project_rules.md` 추가 (번호 재정렬)

### `dist/.mpa-workspace/inject/layer1_implement.md`
- "작업 시작 전 읽을 파일" 1번에 `workspace/project_rules.md` 추가 (번호 재정렬)

### `dist/.mpa-workspace/inject/layer0_init.md`
- "두 영역의 소유권 안내" 섹션 추가 (.mpa-workspace/ vs workspace/ 경계 명시)
- 초기화 완료 시 project_rules.md 생성 안내

### `dist/.mpa-workspace/inject/layer0_update.md`
- "0단계 — .mpa-workspace/ 직접 수정 감지" 신규 추가
- diff 명령으로 직접 수정 감지 → upgrade-candidates 이전 또는 덮어쓰기 선택

## 계획 이탈 없음
