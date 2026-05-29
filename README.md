# my pacemaker agent

> **상위 원칙:** LLM의 한계는 주어진 것이다. 구조는 설계하는 것이다.

이 하네스는 AI agent와의 협업 구조를 체계화한 실용 도구다.  
→ 설계 사고 과정: [`guidebook/logs/discussion_log.md`](guidebook/logs/discussion_log.md)  
→ 실용 안내서: [`guidebook/guidebook.md`](guidebook/guidebook.md)

---

## 3레벨 구조

이 시스템은 3개의 레벨로 구성된다. 각 레벨은 상위 레벨의 산출물이다.

```
principles/          ← 레벨 0: 왜 (Why)
                       AI 협업의 원칙과 철학
                       변경: 협업 철학이 바뀔 때
        ↓ 근거 제공
harness/             ← 레벨 1: 어떻게 (How)
                       하네스를 만들고 운용하는 시스템
                       변경: 방법론이 개선될 때
        ↓ 템플릿 제공
workspace/           ← 레벨 2: 무엇을 (What)
                       이 프로젝트의 실제 하네스
                       변경: 프로젝트가 진행될 때
```

**레벨 구분의 의미:**  
하네스는 "프로젝트의 하네스를 만들기 위한 시스템"이다.  
레벨 1을 수정하면 모든 프로젝트에 영향을 준다.  
레벨 2를 수정하면 해당 프로젝트에만 영향을 준다.

---

## 구조 원칙

| | 레벨 0 (principles/) | 레벨 1 (harness/) | 레벨 2 (workspace/) |
|--|---------------------|------------------|---------------------|
| 질문 | 왜 이렇게 일하는가 | 어떻게 일하는가 | 이 프로젝트는 무엇인가 |
| 내용 | 테제, 철학적 근거 | 방법, 절차, 템플릿 | 프로젝트 데이터 |
| 변경 주체 | 철학 논의 | 하네스 설계자 | 프로젝트 팀 |
| 재사용 | 모든 하네스의 근거 | 모든 프로젝트 공통 | 프로젝트마다 별도 |

---

## 전체 구조

```
think-more/                           ← 사고 실험/탐구 공간 (하네스 외부)
                                        철학, 설계 원칙, 기술 동향, 실전 사례 연구
                                        하네스 구조에 인코딩되기 전 단계의 생각들

harness/                              ← 마스터 레포 (git)
│
├── .agents-workspace/                ← 방법론 스냅샷 (복사 소스)
│   ├── core/                         ← 원칙과 프로토콜
│   │   ├── principles.md
│   │   └── session_protocol.md
│   │
│   ├── personas/                     ← agent 역할 정의 (WHO)
│   │   ├── architect.md
│   │   ├── plan_critic.md
│   │   ├── implementer.md
│   │   ├── code_reviewer.md
│   │   └── integration_auditor.md
│   │
│   ├── skills/                       ← agent 능력 정의 (WHAT IT KNOWS)
│   │   ├── analysis/
│   │   │   ├── silent_decision_extraction.md
│   │   │   ├── counterexample_finding.md
│   │   │   ├── path_tracing.md
│   │   │   └── dependency_mapping.md
│   │   └── tech/
│   │       ├── _template.md
│   │       ├── spring.md
│   │       ├── python.md
│   │       ├── react.md
│   │       └── nodejs.md
│   │
│   ├── workflows/                    ← 세션 시퀀스 (HOW TO RUN)
│   │   ├── new_feature.md
│   │   ├── bug_fix.md
│   │   ├── refactoring.md
│   │   ├── code_review.md
│   │   └── team_collaboration.md
│   │
│   ├── inject/                       ← 세션 패키지 (새 AI 스레드에 붙여넣기)
│   │   ├── layer0_init.md
│   │   ├── layer1_design.md
│   │   ├── layer1_implement.md
│   │   ├── layer1_review.md
│   │   └── layer2_checkpoint.md
│   │
│   └── upgrade-candidates/           ← 하네스 업그레이드 후보 수집
│
└── workspace-template/               ← workspace/ 초기화 템플릿 (복사 소스)
    ├── project_memory/
    │   ├── GUIDE.md
    │   ├── shared/
    │   │   ├── project_identity.md
    │   │   ├── architecture.md
    │   │   └── contracts.md
    │   ├── domains/
    │   │   └── _template.md
    │   └── roles/                        ← 페르소나별 프로젝트 누적 학습
    │       └── _template.md
    │
    ├── tasks/
    │   ├── GUIDE.md
    │   ├── INDEX.md
    │   ├── _template_request.md
    │   ├── active/
    │   └── done/
    │
    └── docs/
        ├── GUIDE.md
        ├── INDEX.md
        └── _template_doc.md
```

---

## 새 프로젝트 시작

`install.py`를 사용한다. 자세한 사용법은 `install.md` 참조.

```bash
python harness/install.py
```

신규 설치와 업그레이드를 자동으로 감지하며, upgrade-candidates 이전도 함께 처리한다.

프로젝트 디렉토리 구조:

```
[project]/
├── .agents-workspace/    ← 방법론 (덮어쓰기로 업데이트 가능)
│   ├── core/, personas/, skills/, workflows/, inject/
│   └── upgrade-candidates/   ← 작업 중 발견된 하네스 개선 후보
│
└── workspace/            ← 프로젝트 데이터 (직접 수정)
    ├── project_memory/
    ├── tasks/
    └── docs/
```

**두 폴더의 역할:**

| 폴더 | 역할 | 업데이트 방식 |
|------|------|--------------|
| `.agents-workspace/` | 방법론 (HOW) — 건드리지 않음 | 하네스에서 덮어쓰기 |
| `workspace/` | 프로젝트 데이터 (WHAT) — 매 세션 업데이트 | 직접 수정 |

---

## 세션 사용법

1. `.agents-workspace/core/session_protocol.md`에서 오늘 작업에 맞는 세션 유형 선택
2. `.agents-workspace/inject/`에서 해당 파일 열기
3. 플레이스홀더를 `workspace/` 파일 내용으로 채우기
4. 완성된 텍스트를 새 AI 스레드 첫 메시지로 붙여넣기
5. 작업 종료 후 보고 내용을 `workspace/`에 반영

```
inject 파일 열기 (.agents-workspace/inject/)
      ↓
personas/ → [페르소나] 채우기
      ↓
workspace/ → [컨텍스트] 채우기
      ↓
새 AI 스레드에 붙여넣기
      ↓
작업
      ↓
세션 종료 보고 → workspace/ 업데이트
              → 하네스 개선 후보 → .agents-workspace/upgrade-candidates/
```

---

## 하네스 업데이트 파이프라인

```
작업 중 더 나은 방법 발견
      ↓
[project]/.agents-workspace/upgrade-candidates/ 에 후보 파일 추가
      ↓
.agents-workspace/ 업데이트 시 harness/upgrade-candidates/ 로 자동 이동 (1단계)
      ↓
검토 및 정제 → harness/.agents-workspace/ 해당 파일에 반영
              (절차: harness/harness-maintenance.md 참조)
      ↓
다음 프로젝트 업데이트 시 새 스냅샷으로 배포
```

### 업데이트 기준

| 상황 | 조치 |
|------|------|
| 더 나은 검증·세션 방법 발견 | inject 파일 수정 |
| 새 작업 유형 필요 | workflow / inject 추가 |
| 기존 방식이 반복 실패 | principles 검토 후 harness 수정 |
| 특정 프로젝트에서만 필요한 것 | harness 건드리지 않음 — workspace에 둠 |

### 커밋 태그 규칙

```
[breaking]     layer1_design: [요청 문서] 섹션 추가
               → 기존 프로젝트: .agents-workspace/ 재복사 필요

[non-breaking] principles: T9 설명 보완
               → 기존 프로젝트 영향 없음
```

---

## 빠른 참조

| 상황 | inject 파일 |
|------|------------|
| 새 프로젝트 초기화 | `.agents-workspace/inject/layer0_init.md` |
| 하네스 업데이트 / 재설치 | `.agents-workspace/inject/layer0_update.md` |
| 기능 설계 | `.agents-workspace/inject/layer1_design.md` |
| 구현 | `.agents-workspace/inject/layer1_implement.md` |
| 코드 검토 | `.agents-workspace/inject/layer1_review.md` |
| 정합성 점검 | `.agents-workspace/inject/layer2_checkpoint.md` |
