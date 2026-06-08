# Tasks 레이어 가이드

> **목적:** 작업 단위로 계획서와 내역서를 관리하고, 진행 상태를 추적한다.

---

## 파일 구조

```
workspace/tasks/
├── README.md                        ← 이 파일
├── INDEX.md                         ← 전체 작업 색인
├── active/                          ← 진행 중인 작업
│   └── yyyymmdd_[작업명]/
│       ├── plan.md
│       └── changelog.md             ← major만 작성
└── done/                            ← 완료된 작업
    └── yyyymmdd_[작업명]/
```

> 템플릿 파일: `.mpa-workspace/templates/plan_template.md`

---

## 작업 라이프사이클

### major (7단계)

```
설계 중 → 설계 완료 ⛔G1 → 구현 중 → 검증 중 → 테스트 중 → 검토 완료 ⛔G2 → 완료 승인 → done
```

- **GATE 1**: 사용자 명시 승인 후 `plan_hash.py approve` 실행 → 상태 `구현 중` 전환
- **GATE 2**: 사용자 명시 완료 요청 후 상태 `완료 승인` 전환 → `done/` 이동

### minor (3단계, GATE 생략)

```
메모 [자동 승인] → 구현 중 → done
```

- **GATE 1**: 계획서 제시 후 `plan_hash.py approve` 자동 실행 (사용자 명시 승인 불필요)
- **GATE 2**: 구현 완료 후 보고 → 사용자(또는 위임 에이전트) 확인 후 `done/` 이동
- `changelog.md` 생략

---

## 파일 역할

| 파일 | 작성 시점 | 대상 | 용도 |
|------|---------|------|------|
| `plan.md` | 작업 시작 전 | major·minor | 요청 원문 + 계획. 사용자 검토 후 승인 |
| `changelog.md` | 작업 완료 후 | major만 | 변경 파일/메소드/내역. 검증 에이전트가 plan.md와 비교 |

---

## 새 작업 추가 절차

1. `.mpa-workspace/templates/plan_template.md`를 복사해서 `active/yyyymmdd_[작업명]/plan.md`로 저장
2. 내용 채우기 (minor는 에이전트 보고·핵심 기능·구현 항목만, 나머지 섹션 생략)
3. `INDEX.md`에 한 줄 추가
4. GATE 1 통과:
   ```bash
   # major: 사용자 승인 후
   # minor: 계획서 제시 직후
   python3 .mpa-workspace/hooks/plan_hash.py approve workspace/tasks/active/yyyymmdd_[작업명]/plan.md
   ```

---

## INDEX.md 관리

| 컬럼 | 내용 |
|------|------|
| 태스크명 | 폴더명과 동일 |
| 타입 | major / minor |
| 상태 | done |
| 요약 | 한 줄 설명 |
| 생성일 | plan.md 생성일 필드값 |
| 점검 | `-` (미점검) / `✅` (전체 정합성 점검 완료) |
