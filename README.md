# my pacemaker agent

!!!! 계속 작업 중입니다. 작동은 하지만 완벽함을 개런티 하지 않습니다. !!!!

> **상위 원칙:** LLM의 한계는 주어진 것이다. 구조는 설계하는 것이다.

이 하네스는 AI agent와의 협업 구조를 체계화한 실용 도구다.  
→ 설계 사고 과정: [`guidebook/logs/discussion_log.md`](guidebook/logs/discussion_log.md)  
→ 실용 안내서: [`guidebook/guidebook.md`](guidebook/guidebook.md)

---

## 설치

`install.md`를 참조하도록 설정된 agent에게 설치 요청을 하면 된다.

```
@install.md 설치해줘
```

Agent가 `install.md`의 절차에 따라 프로젝트 경로와 agent를 확인한 뒤 자동으로 설치한다.  
이미 설치된 프로젝트는 업그레이드 모드로 자동 감지하여 처리한다.

---

## 사용 방법

설치된 프로젝트에서 agent에게 자연어로 작업을 요청하면 된다.

```
[하고싶은 작업] 태스크 생성해줘
```

Agent가 계획서를 작성하고 검토를 요청한다. 승인하면 구현을 진행한다.

**예시:**
```
로그인 기능 태스크 생성해줘
결제 API 연동 버그 수정 태스크 생성해줘
사용자 목록 페이지 리팩토링 태스크 생성해줘
```

### 작업 재개

중단된 작업을 다시 시작할 때는 작업명을 언급하거나, 진행 중인 작업이 하나뿐이면 그냥 이어달라고 하면 된다.

```
[작업명] 이어서 진행해줘
```

Agent가 `workspace/tasks/active/`에서 해당 태스크의 `plan.md`와 `changelog.md`를 읽고 중단된 지점부터 재개한다.

**예시:**
```
로그인 기능 이어서 진행해줘
어디까지 했어?
이전 작업 계속해줘
```

---

## 3레벨 구조

이 시스템은 3개의 레벨로 구성된다. 각 레벨은 상위 레벨의 산출물이다.

```
principles/              ← 레벨 0: 왜 (Why)
                           AI 협업의 기본 원칙
                           변경: 협업 방식의 근본이 바뀔 때
        ↓ 근거 제공
my-pacemaker-agent/      ← 레벨 1: 어떻게 (How)
                           하네스를 만들고 운용하는 시스템
                           변경: 방법론이 개선될 때
        ↓ 템플릿 제공
workspace/               ← 레벨 2: 무엇을 (What)
                           이 프로젝트의 실제 하네스
                           변경: 프로젝트가 진행될 때
```

**레벨 구분의 의미:**  
하네스는 "프로젝트의 하네스를 만들기 위한 시스템"이다.  
레벨 1을 수정하면 모든 프로젝트에 영향을 준다.  
레벨 2를 수정하면 해당 프로젝트에만 영향을 준다.

---

## 구조 원칙

| | 레벨 0 (principles/) | 레벨 1 (my-pacemaker-agent/) | 레벨 2 (workspace/) |
|--|---------------------|------------------|---------------------|
| 질문 | 왜 이렇게 일하는가 | 어떻게 일하는가 | 이 프로젝트는 무엇인가 |
| 내용 | 기본 원칙, 판단 기준 | 방법, 절차, 템플릿 | 프로젝트 데이터 |
| 변경 주체 | 팀 논의 | 하네스 설계자 | 프로젝트 팀 |
| 재사용 | 모든 하네스의 근거 | 모든 프로젝트 공통 | 프로젝트마다 별도 |

---

## 전체 구조

```
my-pacemaker-agent/                   ← 마스터 레포 (git)
│
├── dist/                             ← 설치 소스 (프로젝트에 복사되는 파일들)
│   │
│   ├── .mpa-workspace/               ← 방법론 스냅샷 (복사 소스)
│   │   ├── core/                         ← 원칙과 프로토콜
│   │   ├── personas/                     ← agent 역할 정의 (WHO)
│   │   ├── skills/                       ← agent 능력 정의 (WHAT IT KNOWS)
│   │   ├── inject/                       ← 세션 패키지
│   │   └── upgrade-candidates/           ← 하네스 업그레이드 후보 수집
│   │
│   └── workspace/                    ← workspace/ 초기화 템플릿 (복사 소스)
│       ├── memory/
│       │   ├── README.md
│       │   ├── shared/shared_template.md
│       │   ├── domains/domains_template.md
│       │   └── roles/roles_template.md
│       ├── tasks/
│       │   ├── README.md
│       │   ├── _template/plan_template.md
│       │   └── _template/changelog_template.md
│       └── docs/
│           ├── README.md
│           └── docs_template.md
│
├── agent-specs/                      ← agent별 설치 스펙
├── think-more/                       ← 사고 실험/탐구 공간 (설치되지 않음)
├── install.py                        ← 설치 스크립트
└── install.md                        ← 설치 가이드 (agent가 참조)
```

---

## 설치된 프로젝트 구조

```
[project]/
├── .mpa-workspace/    ← 방법론 (업그레이드로 최신화, 직접 수정 금지)
│   ├── core/, personas/, skills/, workflows/, inject/
│   └── upgrade-candidates/   ← 작업 중 발견된 하네스 개선 후보
│
└── workspace/            ← 프로젝트 데이터 (agent가 직접 관리)
    ├── memory/
    ├── tasks/
    └── docs/
```

| 폴더 | 역할 | 업데이트 방식 |
|------|------|--------------|
| `.mpa-workspace/` | 방법론 (HOW) — 직접 수정 금지 | 업그레이드로만 교체 |
| `workspace/` | 프로젝트 데이터 (WHAT) — agent가 관리 | 작업할 때마다 자동 업데이트 |

---

## 하네스 업데이트 파이프라인

```
작업 중 더 나은 방법 발견
      ↓
[project]/.mpa-workspace/upgrade-candidates/ 에 후보 파일 추가
      ↓
.mpa-workspace/ 업데이트 시 my-pacemaker-agent/dist/.mpa-workspace/upgrade-candidates/ 로 자동 이동 (1단계)
      ↓
검토 및 정제 → my-pacemaker-agent/dist/.mpa-workspace/ 해당 파일에 반영
              (절차: my-pacemaker-agent/harness-maintenance.md 참조)
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
               → 기존 프로젝트: .mpa-workspace/ 재복사 필요

[non-breaking] principles: T9 설명 보완
               → 기존 프로젝트 영향 없음
```

---

## 빠른 참조

| 상황 | inject 파일 | 스레드 |
|------|------------|--------|
| 새 프로젝트 초기화 | `.mpa-workspace/inject/layer0_init.md` | 새 스레드 |
| 하네스 업데이트 / 재설치 | `.mpa-workspace/inject/layer0_update.md` | 새 스레드 |
| 기능 설계 / 계획 작성 | `.mpa-workspace/inject/layer1_design.md` | 새 스레드 |
| 계획 독립 비평 | `.mpa-workspace/inject/layer1_critique.md` | **반드시 새 스레드** |
| 구현 | `.mpa-workspace/inject/layer1_implement.md` | 같은 스레드 |
| 코드 검토 | `.mpa-workspace/inject/layer1_review.md` | 새 스레드 |
| 정합성 점검 | `.mpa-workspace/inject/layer2_checkpoint.md` | 새 스레드 |
