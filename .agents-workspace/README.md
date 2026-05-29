# my pacemaker agent — Agents Workspace

이 폴더는 AI agent 협업 방법론 파일들이다. **되도록 직접 수정하지 않는다.**  
개선이 필요하면 `upgrade-candidates/` 에 후보를 기록하고, 하네스 업데이트로 반영한다.

---

## 폴더 구조

| 폴더 | 역할 |
|------|------|
| `core/` | 원칙과 세션 프로토콜 |
| `personas/` | agent 역할 정의 |
| `skills/` | agent 분석·기술 스킬 |
| `workflows/` | 작업 유형별 세션 흐름 |
| `inject/` | 새 AI 스레드에 붙여넣는 세션 패키지 |
| `upgrade-candidates/` | 하네스 개선 후보 적재 (작업 중 발견 시) |

---

## 세션 시작

1. 오늘 작업 유형 확인 → `core/session_protocol.md`
2. 해당 inject 파일 열기 → `inject/`
3. 플레이스홀더를 `workspace/` 내용으로 채우기
4. 완성된 텍스트를 새 AI 스레드 첫 메시지로 붙여넣기

| 작업 | inject 파일 |
|------|------------|
| 새 프로젝트 초기화 | `inject/layer0_init.md` |
| 기능 설계 | `inject/layer1_design.md` |
| 구현 | `inject/layer1_implement.md` |
| 코드 검토 | `inject/layer1_review.md` |
| 정합성 점검 | `inject/layer2_checkpoint.md` |

---

## 프로젝트 데이터

작업에 필요한 프로젝트 데이터는 이 폴더가 아닌 `workspace/` 에 있다.

| 폴더 | 내용 |
|------|------|
| `workspace/project_memory/shared/` | 아키텍처 규칙, 프로젝트 정체성 |
| `workspace/project_memory/domains/` | 도메인별 규칙 |
| `workspace/tasks/` | 요청 문서 |
| `workspace/docs/` | 기능·설계 문서 |

---

## 하네스 개선 후보 기록

작업 중 더 나은 방법을 발견하면 `upgrade-candidates/` 에 파일로 기록한다.  
파일명은 발견 내용을 반영한다. (예: `better-review-checklist.md`)  
하네스를 업데이트할 때 이 파일들이 하네스 프로젝트로 이전된다.
