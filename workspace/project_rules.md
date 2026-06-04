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

## upgrade-candidates 처리 워크플로우

> **이 워크플로우는 my-pacemaker-agent 프로젝트 전용이다.**  
> 다른 프로젝트에서 upgrade-candidates를 작성하는 것까지는 배포 규칙(agent_rules.md)이 담당한다.  
> 작성된 후보를 실제 MPA 시스템에 반영하는 작업은 여기서만 수행한다.

### 처리 흐름

사용자가 upgrade-candidates 검토를 승인하면:

1. `.mpa-workspace/upgrade-candidates/` 폴더의 파일을 읽는다
2. 각 후보를 타입별로 분류한다:
   - **타입 A (방법론 개선):** MPA 시스템 파일 수정 태스크로 등록 → `agent_rules.md`의 "MPA 시스템 파일 수정 규칙" 절차 따름
   - **타입 B (도메인 지식):** `.mpa-workspace/knowledge/[도메인].md`에 직접 반영
3. 반영이 완료된 후보 파일은 삭제한다
4. `dist/.mpa-workspace/`에 동기화한다
