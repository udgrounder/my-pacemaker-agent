# Tasks 레이어 가이드

> **목적:** 작업 단위로 계획서와 내역서를 관리하고, 진행 상태를 추적한다.

---

## 파일 구조

```
workspace/tasks/
├── README.md                    ← 이 파일
├── INDEX.md                     ← 전체 작업 색인 (agent가 최초 세션에 생성)
├── _template/
│   ├── plan_template.md         ← 계획서 템플릿
│   └── changelog_template.md   ← 내역서 템플릿
├── active/                      ← 진행 중인 작업
│   └── yyyymmdd_[작업명]/
│       ├── plan.md
│       └── changelog.md
└── done/                        ← 완료된 작업
    └── yyyymmdd_[작업명]/
```

---

## 작업 라이프사이클

```
작업 생성 → active/yyyymmdd_[작업명]/plan.md 작성 → 사용자 검토
         → 작업 진행 → changelog.md 작성 → 사용자 검토
         → 완료 → done/yyyymmdd_[작업명]/으로 이동
```

---

## 파일 역할

| 파일 | 작성 시점 | 용도 |
|------|---------|------|
| `plan.md` | 작업 시작 전 | 요청 원문 + 계획. 사용자 검토 후 승인 |
| `changelog.md` | 작업 완료 후 | 변경 파일/메소드/내역. 검증 agent가 plan.md와 비교 |

---

## 새 작업 추가 절차

1. `.mpa-workspace/templates/plan_template.md`를 복사해서 `active/yyyymmdd_[작업명]/plan.md`로 저장
2. 내용 채우기
3. `INDEX.md`에 한 줄 추가

---

## INDEX.md 관리

| 컬럼 | 내용 |
|------|------|
| 작업명 | 폴더명과 동일 |
| 상태 | active / done |
| 요약 | 한 줄 설명 |
| 날짜 | 생성일 |
