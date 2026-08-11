# 프로젝트 규칙 (my-pacemaker-agent)

> MPA 시스템 자체를 개발하는 프로젝트의 고유 규칙.  
> `.mpa-workspace/`를 수정하지 않고 이 파일에 확장한다.

---

## 라우팅 힌트

| 발화 패턴 | 처리 유형 | 로딩 |
|---------|---------|------|
| "규칙 바꿔줘", "inject 수정", "페르소나 수정", "MPA 시스템 파일 수정" | MPA 시스템 파일 수정 | `agent_rules.md`의 "MPA 시스템 파일 수정 규칙" 섹션 |

---

## 프로젝트 고유 행동 규칙

- 이 프로젝트는 MPA 시스템 자체다. `.mpa-workspace/`를 수정한 후 반드시 `dist/.mpa-workspace/`에도 동기화한다.
- `workspace/project_rules.md` 자체를 수정할 때는 MPA 시스템 파일 수정 규칙을 따르지 않는다 (이 파일은 프로젝트 소유).

---

## map-product issue 처리 워크플로우

> **이 워크플로우는 my-pacemaker-agent 프로젝트 전용이다.**  
> 다른 프로젝트의 방법론 개선은 local `workspace/issues/`에 기록한다.
> 이 source 저장소로 수집된 `methodology_improvement` issue를 실제 MPA 시스템에 반영하는 작업은 여기서만 수행한다.

### 처리 흐름

사용자가 수집 issue의 review·triage를 승인하면:

1. `workspace/issues/inbox/`의 지정 issue를 읽는다
2. `methodology_improvement`는 MPA 시스템 파일 수정 태스크로 등록하고, `knowledge_promotion`은 `.mpa-workspace/knowledge/[도메인].md` 반영 여부를 결정한다
3. release·deployment·verification 근거를 연결한 뒤 issue를 archive한다
4. Runtime 변경은 `release_manager.py sync-runtime`으로 `dist/.mpa-workspace/`에 동기화한다
