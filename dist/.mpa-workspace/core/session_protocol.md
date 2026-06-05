# 세션 프로토콜

> **이 파일의 용도:**  
> `agent_rules.md`의 자동 판단 구조를 보완하는 레퍼런스.  
> 에이전트는 대부분의 경우 `agent_rules.md`의 "세션 시작 루틴"으로 자동 처리한다.  
> 이 파일은 수동 제어가 필요한 경우, 또는 전체 구조를 파악하고 싶을 때 참조한다.

---

## 수동 세션 진입 가이드

에이전트의 자동 판단을 우회하거나, 특정 세션을 명시적으로 시작하고 싶을 때:

```
새 프로젝트? 또는 기존 프로젝트에 MPA 시스템 처음 적용?
    │
    ├── Yes (새 프로젝트)           → @inject/layer0_init.md (A. 신규 흐름)
    ├── Yes (기존 프로젝트 첫 적용)  → @inject/layer0_init.md (B. 기존 흐름)
    │
    └── No (진행 중 프로젝트)
            │
            ├── 전체 워크플로우가 필요할 때 → workflows/ 참조
            │   ├── 새 기능 개발   → workflows/new_feature.md
            │   ├── 버그 수정      → workflows/bug_fix.md
            │   ├── 리팩토링       → workflows/refactoring.md
            │   ├── 코드 리뷰      → workflows/code_review.md
            │   └── 팀 협업        → workflows/team_collaboration.md
            │
            └── 단일 세션만 명시적으로 시작할 때 → inject/ 직접 사용
                ├── 기능 설계 / 계획 수립                       → @inject/layer1_design.md
                ├── 계획 독립 비평 (서브에이전트로 실행)         → @inject/layer1_critique.md
                ├── 설계 완료된 태스크 구현                     → @inject/layer1_implement.md
                ├── 에이전트 검증 (`검증 중` 단계, 서브에이전트)     → @inject/layer1_review.md
                ├── 결과물을 보고 수정·추가 사항이 생겼을 때    → @inject/layer1_discovery.md
                └── 정합성 점검                                 → @inject/layer2_checkpoint.md
```

---

## 세션별 요약

| 세션 | 페르소나 | 주입 컨텍스트 | 산출물 |
|------|---------|-------------|--------|
| layer0_init | Architect | 없음 (첫 세션) | memory 초안 전체 + tasks/INDEX.md |
| layer1_design | Task Designer | shared/ 전체 | 태스크 계획 (plan.md) |
| layer1_critique | Plan Critic | shared/ + plan.md만 | 비평 결과 (권장 기준 → layer1_critique.md 참조) |
| layer1_implement | Implementer | shared/ + 도메인/ + 태스크 계획 | 구현 코드 + 결정 목록 |
| layer1_review | Result Reviewer | shared/ + 태스크 계획 | 검토 리포트 |
| layer1_discovery | Task Designer | shared/ + 태스크 계획 | plan.md 업데이트 + INDEX.md 등록 |
| layer2_checkpoint | Integration Auditor | memory 전체 | 충돌 목록 + memory 업데이트 |

---

## 스레드 운영 원칙

**모든 inject 파일 = 새 스레드 시작**  
같은 스레드 연속 작업 → inject 파일 불필요, 그냥 진행

**새 스레드를 열어야 하는 신호:**
- 세션 유형이 바뀔 때 (설계 → 구현, 구현 → 검토)
- 현재 스레드가 길어져 컨텍스트가 흐릿해질 때
- 다른 도메인으로 전환할 때 (UI → Backend)

---

## 세션 재개 (중단된 세션 이어가기)

> 새 세션 시작 시 `agent_rules.md`의 세션 시작 루틴이 자동으로 진행 중 태스크를 감지하고 재개를 제안한다.  
> 수동으로 이어가고 싶다면 "이어서 해줘" 또는 "[태스크명] 계속해줘"라고 말한다.

```
plan.md 상태 확인
    ├── "구현 중" → changelog.md 읽기 → 첫 미완료 단계부터 재개
    └── "설계 완료" → @inject/layer1_implement.md 로 구현 세션 시작
```

---

## 실패비용 등급과 사용자 개입

**세션 시작 전, 먼저 실패 비용을 추정하라 (T6):**

세부 판단 기준: `inject/layer1_design.md` "실패 비용 추정" 섹션 참조.

| 등급 | 조건 | 사용자 개입 (Zone) |
|------|------|-----------------|
| `critical` | 보안·외부 연동·비가역 변경 | Zone 1 — 하드 게이트, 명시적 확인 필수 |
| `major` | 그 외 기본값 | Zone 2 — 핵심 항목 확인 요청 |
| `minor` | 단일 관심사·자명한 방법·즉시 복구 가능 | Zone 3 — 자동 처리 후 간략 고지 |

---

## 도메인 분리 원칙

**도메인이 다르면 독립 스레드로 운영**

```
공통 주입:        shared/ (project_identity + architecture + contracts)
도메인별 추가:    domains/[도메인명]/rules.md + registry.md (있는 경우)
```

**도메인 걸치는 작업 (예: 로그인 end-to-end):**
```
1단계: API 계약 세션 → contracts.md 먼저 확정 (Interface-First)
2단계: [도메인 A] 세션 → 계약 구현
3단계: [도메인 B] 세션 → 계약 소비
```

API 계약 = 두 도메인 세션의 유일한 동기화 포인트  
→ 도메인 폴더 구성은 `memory/GUIDE.md` 참조
