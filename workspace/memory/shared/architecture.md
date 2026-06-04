# 아키텍처 결정

## 디렉토리 구조 원칙

### dist/ 가 단일 배포 소스
모든 시스템 파일 변경은 `dist/.mpa-workspace/` 안에서 한다.  
`install.py`가 이 폴더를 대상 프로젝트로 복사한다.  
`agent-configs/`는 구버전 호환 fallback이며 신규 개발 대상이 아니다.

### agent-specs/ 분리 이유
에이전트마다 진입점 파일명과 주입 방식이 다르다 (CLAUDE.md / AGENTS.md / GEMINI.md).  
`agent-specs/{agent}/inject/` — 진입점 파일  
`agent-specs/{agent}/files/` — 대상 프로젝트에 복사할 파일  
`agent-specs/{agent}/spec.md` — 설치 내용 설명

### workspace/ vs .mpa-workspace/ 분리
`.mpa-workspace/` — 에이전트 행동 규칙 (모든 프로젝트 공통, 체계 버전과 함께 변경)  
`workspace/` — 이 프로젝트 고유 데이터 (업그레이드 시 보존)

---

## 핵심 설계 결정

### shared/ 파일은 로그가 아니라 현재 상태 스냅샷
결정이 바뀌면 기존 항목을 교체한다. 이전 내용을 남기지 않는다.  
폐기된 규칙은 삭제한다.  
append 누적은 모순을 만든다.

### 전진 증류 원칙
태스크 간 방향 연속성은 과거 plan.md를 읽어서 유지하지 않는다.  
각 태스크 종료 시 배운 것을 `shared/` 파일로 증류한다.  
이후 태스크는 항상 최신 `shared/` 파일만 읽는다.

### 게이트 대칭 원칙
사용자 명시적 승인 없이 구현을 시작하지 않는다.  
사용자 명시적 확인 없이 검토 완료로 처리하지 않는다.  
두 게이트는 동등한 원칙이다. 생략은 사용자가 명시적으로 요청할 때만 허용된다.

### 태스크 종료 순서
신규 태스크(발견 항목)를 먼저 등록한다.  
등록 완료 확인 후 원래 태스크를 종료한다.  
원래 태스크를 먼저 닫으면 파생 맥락이 끊긴다.

### Layer 2 주기 추적
Layer 2 완료 시 `workspace/tasks/INDEX.md` 하단에 `[Layer 2 완료] YYYY-MM-DD` 한 줄을 추가한다.  
에이전트는 태스크 완료 시 마커 이후 done 태스크를 타입별로 세어 트리거 조건을 확인한다:
- `major` 1개 이상 → 즉시 Layer 2 제안
- `minor`만 5개 이상 → Layer 2 제안
마커가 없으면 done 전체를 기준으로 한다. 타입 컬럼 없는 기존 태스크는 `minor`로 간주한다.

### 프로젝트 확장 영역
`.mpa-workspace/`는 MPA 시스템 소유 — 업그레이드 시 덮어씌워짐. 직접 수정 금지.  
`workspace/`는 프로젝트 소유 — 업그레이드해도 보존됨. 여기서 자유롭게 확장.

프로젝트 고유 확장 지점:
- `workspace/project_rules.md` — 라우팅 힌트, 금지 패턴, 행동 규칙 (모든 세션에서 최우선 로드)
- `workspace/memory/domains/[도메인]/rules.md` — 도메인 규칙
- `workspace/memory/shared/architecture.md` — 아키텍처 결정

### MPA 시스템 파일 수정 거버넌스
`.mpa-workspace/` 하위 파일 수정은 일반 소스 코드 수정과 다른 규칙을 따른다.
- 페르소나: `personas/mpa_system_designer.md`
- 코드 게이트 미적용 (`.approved` 마커 불필요)
- 비평: 새 스레드 원칙 / 환경 미지원 시 같은 스레드 허용
- 수정 후 `dist/`와 설치본 양쪽 동기화 필수
- 라우팅 키워드: "규칙 바꿔줘", "inject 수정", "페르소나 수정", "MPA 시스템 파일 수정"

---

## 파일별 역할 (dist/.mpa-workspace/)

| 파일 | 역할 |
|------|------|
| `core/agent_rules.md` | 에이전트 행동 규칙 전체. 세션 시작 루틴, 게이트, 상태 전이 |
| `core/session_protocol.md` | inject 파일 선택 가이드 (사용자용) |
| `inject/layer*.md` | 세션 레시피. 새 스레드 시작 시 에이전트에게 전달 |
| `personas/*.md` | 역할 정의. 에이전트가 읽고 해당 역할로 작동 |
| `skills/analysis/*.md` | 분석 방법론. 페르소나가 참조 |
| `templates/*.md` | 파일 생성 시 복사해 쓰는 골격 |

---

## 안티패턴

- `dist/` 외부에서 시스템 파일을 직접 수정하지 않는다 (agent-configs/ 포함)
- shared/ 파일에 결정 로그를 누적하지 않는다. 현재 상태만 유지한다
- 에이전트가 사용자 확인 없이 태스크 상태를 완료로 전환하지 않는다
