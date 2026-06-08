---
태스크: workflow-and-planmd-cleanup
생성일: 2026-06-08
타입: major
실패비용: minor
상태: 완료 승인
승인해시: b8ec9867d06b74fe
---

# 태스크: workflows/ 역할 정리 + 구형 plan.md 마이그레이션

**목적:** workflows/ 파일의 역할을 명확히 정의하고, 구형(YAML 프론트매터 없는) plan.md 20개에 최소 프론트매터를 주입한다.

---

## 에이전트 보고

### 사용자 결정 필요
- ~~**[2번] workflows/ 처리 방향**~~ → **결정: 옵션 A — 에이전트 라우팅에 통합**

### 에이전트 가정
| 가정 | 근거 | 틀렸을 때 영향 |
|------|------|--------------|
| 구형 plan.md 20개는 모두 done 상태이므로 상태 필드는 "완료 승인"으로 통일 | done/ 폴더에 있음 | 일부가 다른 상태라면 개별 확인 필요 |
| 타입/실패비용은 "minor"로 기본값 설정 (검증 불가) | 당시 시스템에 해당 필드 없었음 | INDEX.md 기록된 타입과 다르면 나중에 수동 수정 |
| workflows/ 파일 5개 모두 에이전트 라우팅에서 실제 로드되지 않음 | agent_rules.md 라우팅 테이블 미참조 확인 | 없음 |

---

## 구현 단계

- [x] **2. workflows/ 에이전트 라우팅 통합**
  - agent_rules.md 라우팅 테이블에 workflows/ 파일 로드 추가:
    - 새 기능 → `workflows/new_feature.md`
    - 버그 수정 → `workflows/bug_fix.md`
    - 리팩터링 → `workflows/refactoring.md`
    - 작업 결과 검토 → `workflows/code_review.md`
  - workflows/ 파일 각각에 "에이전트가 세션 시작 시 읽는다"는 역할 명시
  - dist/ 동기화 포함

- [x] **3. 구형 plan.md 마이그레이션 (20개)**
  - 자동화 스크립트로 일괄 처리:
    - 폴더명 → 태스크명, 생성일 추출 (`yyyymmdd_이름` 패턴)
    - 상태: `완료 승인`
    - 타입: `minor` (기본값, INDEX.md 참조해 일부 major 보정)
    - 실패비용: `minor` (기본값)
    - 승인해시: `""` (done이므로 불필요)
  - 단, INDEX.md에서 major로 기록된 항목은 타입을 major로 수정

---

## 검증 체크리스트
- [ ] plan_hash.py audit 실행 시 20개 파일 모두 통과
- [ ] workflows/ 파일 역할이 에이전트 또는 사용자에게 명확히 전달되는가

## 반례
- 구형 plan.md의 본문에 이미 "타입: major" 같은 내용이 있을 수 있음 → 스크립트가 기존 내용 보존 후 상단에 프론트매터만 추가

## 수정 대상 파일
- `workspace/tasks/done/20260604_*/plan.md` (20개)
- `agent_rules.md` 또는 workflows/ 파일들 (방향에 따라)
- `README.md` (옵션 B 선택 시)
