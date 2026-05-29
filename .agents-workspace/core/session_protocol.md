# 세션 프로토콜

## 세션 유형 결정 트리

```
새 프로젝트? 또는 기존 프로젝트에 하네스 처음 적용?
    │
    ├── Yes → inject/layer0_init.md
    │
    └── No (진행 중 프로젝트)
            │
            ├── 어떤 작업 유형인가? → workflows/ 참조 (시퀀스 전체)
            │   ├── 새 기능 개발   → workflows/new_feature.md
            │   ├── 버그 수정      → workflows/bug_fix.md
            │   ├── 리팩토링       → workflows/refactoring.md
            │   ├── 코드 리뷰      → workflows/code_review.md
            │   └── 팀 협업        → workflows/team_collaboration.md
            │
            └── 특정 단일 세션만 필요할 때 → inject/ 직접 사용
                ├── 기능 설계 / 계획 수립    → inject/layer1_design.md
                ├── 설계 완료된 태스크 구현  → inject/layer1_implement.md
                ├── 구현 완료 후 코드 검토   → inject/layer1_review.md
                └── 정합성 점검             → inject/layer2_checkpoint.md
```

---

## 세션별 요약

| 세션 | 페르소나 | 주입 컨텍스트 | 산출물 |
|------|---------|-------------|--------|
| layer0_init | Architect | 없음 (첫 세션) | project_memory 초안 전체 |
| layer1_design | Plan Critic | shared/ 전체 | 태스크 계획 |
| layer1_implement | Implementer | shared/ + 도메인/ + 태스크 계획 | 구현 코드 + 결정 목록 |
| layer1_review | Code Reviewer | shared/ + 태스크 계획 | 검토 리포트 |
| layer2_checkpoint | Integration Auditor | project_memory 전체 | 충돌 목록 + project_memory 업데이트 |

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

이전 세션이 중간에 끊겼거나, 구현이 완료되지 않은 상태로 종료된 경우:

```
tasks/active/[태스크명]/plan.md 열기
    ↓
"구현 진행 상태" 섹션 확인
    ├── 상태가 "구현 중" → changelog.md 읽기 → 중단된 단계부터 재개
    └── 상태가 "설계 완료" → 구현 세션 새로 시작 (layer1_implement.md)

changelog.md가 존재하면 → 완료된 부분 파악 후 이어가기
changelog.md가 없으면 → 처음부터 시작
```

**재개 세션도 동일한 inject 파일(layer1_implement.md)을 사용한다.**  
inject 파일 내 "구현 전 체크 1번"이 이전 진행 상태를 자동으로 처리한다.

---

## 자율성 레벨

**세션 시작 전, 먼저 실패 비용을 추정하라 (T6):**

| 축 | 판단 신호 | 위험 방향 |
|----|----------|----------|
| 심각도 | 외부 공개? 보안·금융·규정에 닿는가? | 높을수록 위험 |
| 발견 가능성 | 실행하면 즉시 알 수 있는가? 아니면 운영 후에야? | 낮을수록 위험 |
| 가역성 | 되돌리기 쉬운가? 영구 저장되는가? | 낮을수록 위험 |

> 심각도 높음 **또는** 발견 가능성 낮음 **또는** 가역성 낮음 → 레벨 1~2  
> 셋 다 안전 방향이면 → 레벨 3~4 고려 가능

| 레벨 | 설명 | 언제 사용 |
|------|------|---------|
| 1 — 제안 | AI가 옵션 제시, 인간이 결정 | 가치 결정, 처음 하는 유형, 실패 비용 높음 |
| 2 — 초안 | AI 결과물 생성, 인간 검토 후 적용 | **기본값 (대부분의 경우)** |
| 3 — 실행 후 보고 | AI 실행 → 인간 사후 확인 | 실패 비용 낮음 + 가역적 |
| 4 — 완전 자율 | 체크 없이 진행 | 완전 명세 + 완전 가역 + 반복 검증된 경우만 (실제로 드묾) |

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
→ 도메인 폴더 구성은 `project_memory/GUIDE.md` 참조
