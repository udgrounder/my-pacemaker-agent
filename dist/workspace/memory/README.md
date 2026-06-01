# Project Memory 관리 가이드

> **원칙:** 완전한 문서보다 현재 유효하고 선별적으로 주입되는 문서가 낫다. (T10)

---

## 파일 구조

```
workspace/memory/
├── shared/                      ← 모든 세션에 항상 주입
│   ├── shared_template.md       ← 새 파일 추가 시 복사해서 사용
│   ├── project_identity.md      ← Tier 1: 프로젝트 정체성 (거의 변하지 않음)
│   ├── architecture.md          ← Tier 2: 규칙 + 패턴 + 결정 이력 + 안티패턴
│   └── contracts.md             ← Tier 2: 도메인 간 인터페이스 계약 (선택 — 도메인 2개 이상일 때 생성)
│
├── domains/                     ← 해당 도메인 세션에만 주입
│   ├── domains_template.md      ← 새 도메인 추가 시 복사해서 사용
│   └── [도메인명]/              ← 프로젝트에 맞게 직접 생성
│       ├── rules.md             ← 도메인 규칙 (필수)
│       └── registry.md          ← 재사용 요소 목록 (선택, 목록이 많아지면 분리)
│
└── roles/                       ← 페르소나별 프로젝트 누적 학습
    ├── roles_template.md        ← 새 페르소나 추가 시 복사해서 사용
    └── [페르소나명].md          ← 해당 역할이 직접 작성·관리
```

**도메인 예시:**

| 프로젝트 유형 | 도메인 폴더 예시 |
|------------|----------------|
| 풀스택 웹 | `domains/frontend/`, `domains/backend/` |
| 모바일 앱 | `domains/app/`, `domains/api/` |
| CLI 도구 | `domains/cli/`, `domains/core/` |
| 데이터 파이프라인 | `domains/ingestion/`, `domains/transform/`, `domains/output/` |
| 단일 도메인 | `domains/core/` (또는 shared/만 사용) |

---

## 메모리 쓰기 권한

| 파일 | 쓰기 주체 | 원칙 |
|------|-----------|------|
| `shared/project_identity.md` | 프로젝트 초기화 시 한 번 작성 | 거의 변경하지 않음 |
| `shared/architecture.md` | 명시적 결정이 있을 때 | 추정으로 쓰지 않는다 |
| `shared/contracts.md` | 인터페이스 변경 시 | 실제 계약만 기록 |
| `domains/[도메인명]/` | 해당 도메인 담당 에이전트가 직접 | 다른 도메인 에이전트는 수정 안 함 |
| `roles/[페르소나명].md` | 해당 페르소나가 직접 | 다른 역할이 수정하지 않음 |

> **원칙:** 모든 파일을 모든 에이전트가 자유롭게 수정하면 일관성이 무너진다.  
> 각 파일의 소유권을 명확히 하고, 소유권 없이는 수정하지 않는다.

---

## 기억 여부 판단

**작업 유형이 아니라 "발견"으로 판단한다.**

> 핵심 질문 (전역): **"다음 AI 세션이 이걸 모르면 다른 결정을 내리는가?"**  
> 핵심 질문 (역할별): **"다음에 이 역할이 몰랐다면 실수했을 내용인가?"**

### 기술/도메인 지식 기록 위치

| 지식 유형 | 기록 위치 |
|---------|---------|
| 기술 지식 (하면 안 되는 것만) | `domains/[관련 도메인]/rules.md` 절대 금지 섹션 |
| 이 프로젝트 한정 도메인 규칙 | `domains/[도메인]/rules.md` |
| 다른 프로젝트에도 유효한 도메인 지식 | `upgrade-candidates/` → `.mpa-workspace/knowledge/` |
| 역할 행동 패턴 | `roles/[페르소나명].md` |

> **기술 지식 원칙:** Agent 훈련 데이터를 신뢰한다. 일반적인 Best Practice는 기록하지 않고, "하면 안 되는 것"만 기록한다.

```
작업 완료
    ↓
다음 AI 세션의 결정이 달라지는가?
    ├── No  → 기억 불필요 (코드가 이미 답이다)
    └── Yes → 무엇이 달라지는가?
                ├── 새 규칙·금지사항          → architecture.md
                ├── 새 패턴·구조              → architecture.md
                ├── 인터페이스 변경            → contracts.md
                ├── 거부된 접근법              → 안티패턴
                ├── 재사용 요소 추출           → registry.md
                ├── 이 역할만 알아야 할 함정   → roles/[페르소나명].md
                └── 요청 완료                  → tasks/ done + docs/ 반영
```

**작업 유형별 예시 — 유형이 아니라 발견이 기준임을 보여준다:**

| 작업 | 기억 여부 | 판단 근거 |
|------|----------|----------|
| 버그 수정 (단순 오타) | ❌ | AI가 모른다고 다른 결정을 내리지 않음 |
| 버그 수정 → "이 패턴 쓰면 안 됨" 발견 | ✅ | 안티패턴 — 모르면 AI가 같은 실수 반복 |
| 중간 단계 작업 | ❌ | 최종 결과가 기억 대상. 과정은 아님 |
| 리팩토링 (동작 변화 없음) | ❌ | 미래 AI 세션 결정에 영향 없음 |
| 리팩토링 → 새 레이어 구조 확립 | ✅ | architecture.md — AI가 모르면 구조 무시 |
| 새 API 엔드포인트 추가 | ✅ | contracts.md — 다른 도메인 AI가 모름 |
| 기능 구현 완료 | ✅ | tasks/ done + docs/ 반영 필요 |
| 스타일·포맷 수정 | ❌ | 규칙이 이미 있다면 준수한 것일 뿐 |

---

## 업데이트 트리거

| 트리거 | 업데이트 대상 |
|--------|-------------|
| 새 모듈/레이어 추가 | `shared/architecture.md` |
| 도메인 간 인터페이스 변경 | `shared/contracts.md` |
| 기존 규칙과 충돌하는 결정 발생 | `shared/architecture.md` (결정 이력) |
| 같은 패턴 3번 이상 반복 | `shared/architecture.md` (패턴 코드화) |
| 방식 시도 후 거부 | `shared/architecture.md` (안티패턴 추가) |
| 재사용 가능한 요소 추출 | `domains/[도메인명]/registry.md` |
| 도메인 고유 규칙 확립 | `domains/[도메인명]/rules.md` |
| 이 역할만 알아야 할 함정·패턴 발견 | `roles/[페르소나명].md` |
| 요청 구현 완료 | `tasks/` 상태 → done + `docs/` 해당 파일 업데이트 |

---

## AI용 문서 작성 원칙

### 1. 조작 가능성 기준
> "AI가 이 규칙을 따랐는지 확인 가능한가?"

❌ "코드를 깔끔하게 작성한다"  
✅ "파일 하나가 200줄을 넘으면 분리한다"

### 2. 부정 제약(Negative Constraints) 필수
> "하면 안 되는 것"을 명시하지 않으면 AI는 일반 패턴으로 채운다

❌ "Repository 패턴을 사용한다"  
✅ "Repository 레이어를 거치지 않은 직접 DB 접근 금지. 이유: 트랜잭션 관리 일관성"

### 3. Why가 What보다 중요한 경우
> 결정 이력과 안티패턴에는 반드시 이유를 기록한다  
> 이유가 있어야 AI가 엣지 케이스를 올바르게 판단할 수 있다

---

## 세션별 주입 매핑

| 세션 | 주입 파일 |
|------|---------|
| layer0_init | 없음 (생성) |
| layer1_design | `shared/` 전체 + `roles/architect.md` |
| layer1_implement | `shared/` + 작업 관련 `domains/[도메인명]/` + `roles/implementer.md` |
| layer1_review | `shared/` + 관련 도메인 + `roles/code_reviewer.md` |
| layer2_checkpoint | 전체 |

---

## 소스 오브 트루스

| Tier | 소스 | 규칙 |
|------|------|------|
| Tier 1 (불변 규칙) | **문서** | 코드 변경 전 이 문서 먼저 업데이트 |
| Tier 2 (패턴, 계약) | 코드 ↔ 문서 상호 참조 | 불일치 발견 시 즉시 해소 |
| Tier 3 (이력, 안티패턴) | **문서** | 코드에서 추출 불가 — 세션 종료 시 반드시 기록 |

---

## 템플릿 사용법

### 템플릿 위치

템플릿은 `.mpa-workspace/templates/`에 있다. 각 파일 상단의 사용법을 참고해서 복사 후 작성한다.

| 템플릿 | 복사 위치 |
|--------|---------|
| `shared_template.md` | `workspace/memory/shared/[파일명].md` |
| `domains_template.md` | `workspace/memory/domains/[도메인명]/rules.md` |
| `roles_template.md` | `workspace/memory/roles/[페르소나명].md` |
