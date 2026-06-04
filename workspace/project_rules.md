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

- 이 프로젝트는 MPA 시스템 자체다. `dist/.mpa-workspace/`를 수정한 후 반드시 `.mpa-workspace/`에도 동기화한다.
- `workspace/project_rules.md` 자체를 수정할 때는 MPA 시스템 파일 수정 규칙을 따르지 않는다 (이 파일은 프로젝트 소유).
