# workspace/ — 이 프로젝트의 데이터

이 폴더는 **my pacemaker agent**가 관리하는 이 프로젝트의 실제 작업 데이터다. agent에게 자연어로 작업을 요청하면 대부분 자동으로 채워지므로, 사람이 직접 편집할 일은 많지 않다. 아래는 "무엇이 어디에 있는지" 파악용 안내다.

> 방법론(어떻게 일하는가)을 보려면 형제 폴더 `.mpa-workspace/`를 참고한다. 그쪽은 직접 수정하지 않는다 (아래 참조).

---

## 폴더 구조

```
workspace/
├── memory/        ← 프로젝트 기억 (세션이 바뀌어도 유지돼야 하는 사실)
├── tasks/         ← 작업 단위 — 계획서·진행 상태·완료 이력
├── issues/        ← 방법론 개선 등 프로젝트 issue
└── exploration/   ← 작업하며 도출되는 사고·연구 공간 (토론 모드 기록 위치)
    ├── discussion/   ← 논의 + 토론 모드 산출물
    ├── research/     ← 기술 동향 리서치
    └── use_cases/    ← 실전 활용 사례
```

| 폴더 | 무엇을 담나 | 누가 쓰나 |
|------|-----------|----------|
| `memory/` | `shared/`(아키텍처·계약·정체성), `domains/`(도메인 규칙), `roles/`(역할별 학습) | agent가 결정·발견 시 기록 |
| `tasks/` | `active/`(진행 중), `done/`(완료), `INDEX.md`(색인) — 각 작업은 `plan.md`로 시작 | agent가 작업마다 생성·갱신 |
| `issues/` | 방법론 개선 등 회수 가능한 관찰 기록 | 프로젝트 agent가 생성, source는 명시 요청으로 수집 |
| `exploration/` | `discussion/`(논의·토론 기록), `research/`(기술 조사), `use_cases/`(사례) | 토론 모드 등 자유 탐구 시 (Task 면제) |

- **tasks vs docs:** `tasks/`는 "무엇을 만들까"(구현 전), 루트 `docs/`는 "만든 것이 어떻게 동작하나"(구현 후)다. 루트 `docs/`는 프로젝트 사용자가 소유한다.
- **작업 흐름:** 새 작업은 `tasks/active/yyyymmdd_[작업명]/plan.md`로 시작해, 완료되면 `tasks/done/`으로 이동한다. 상태는 `plan.md`의 YAML 프론트매터로 추적된다.
- **exploration:** 토론 모드(주제를 심도 있게 논의하며 과정·결과를 living document로 남기는 비개발 트랙)의 기록 위치다. 이 폴더 내 작업은 Task를 만들지 않는다.

---

## 형제 폴더 `.mpa-workspace/` 란?

`.mpa-workspace/`는 agent가 이 프로젝트에서 **어떻게 일하는지를 정의한 협업 방법론**이다 (페르소나·세션 절차·규칙·hook·템플릿).

> ⚠️ **`.mpa-workspace/`는 직접 수정하지 않는다.** 방법론 개선이 필요하면 `workspace/issues/`에 `methodology_improvement` issue를 기록하고, 사용자가 승인한 수집·검토·release 절차로 반영한다. 직접 수정하면 다음 Runtime 배포 때 덮어쓰여 사라진다.

| | `workspace/` | `.mpa-workspace/` |
|--|-------------|-------------------|
| 역할 | 이 프로젝트의 데이터 (WHAT) | 일하는 방법 (HOW) |
| 변경 | 작업할 때마다 agent가 갱신 | 승인된 Runtime release로 최신화 |
| 직접 편집 | 필요 시 가능 | 하지 않음 |

---

## 시작하기

설치된 프로젝트에서 agent에게 자연어로 요청하면 된다.

```
[하고 싶은 작업] 태스크 생성해줘
[작업명] 이어서 진행해줘
[주제] 논의하자              ← 토론 모드 (만들지 않고 깊이 논의·기록)
```

agent가 작업의 실패 비용을 판단해 흐름(minor/major)을 고르고, 게이트를 거쳐 진행한다. 자세한 운영 방식은 마스터 레포의 가이드북(`guidebook/guidebook.md`)을 참고한다.
