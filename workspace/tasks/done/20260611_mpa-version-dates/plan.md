---
태스크: mpa-version-dates
생성일: 2026-06-11
타입: minor
실패비용: minor
상태: 완료 승인
승인해시: aec7c07d58055731
---

# 작업 계획서: mpa-version-dates

**파생 출처:** `.mpa-version`의 `harness_date` 의미 질문 → 사용처 0건(죽은 필드)이고, `installed_at`/`upgraded_at`이 매번 한 줄로 덮어써져 최초 설치일이 소실되는 결함 발견.

---

## 에이전트 보고

### 사용자 결정 필요

- 없음 (방향은 사용자 논의에서 확정: harness_date 제거 + installed_at 보존 + upgraded_at 갱신)

### 암묵적 결정

- 기존 설치본의 `harness_date` 값은 `installed_at`으로 **승계**한다 — 실제 최초 설치일은 소실됐으므로 방법론 배포일(harness_date)이 최선의 근사치. 사용자 방향 제시(2026-06-11).
- `dist/.mpa-workspace/.mpa-version` 원본에는 날짜 필드를 두지 않는다(placeholder 주석) — 신규 설치 시 `installed_at`이 "설치 당일"로 기록되도록.

### 에이전트 가정

| 가정 | 근거 | 틀렸다면 |
|-----|------|---------|
| harness_date는 버전 비교 등에 안 쓰임 | grep 전수조사 사용처 0 | 쓰이면 제거 불가 |

### minor 판단 근거

- 단일 관심사: `.mpa-version` 날짜 기록 한 가지
- 설계 결정 불필요: 로직 자명(보존/갱신/승계)
- git reset으로 복구 가능: 외부 상태 없음
- 사용자 취향·의사결정 불필요

---

## 요청 원문

"설치일, 업그레이드일 이렇게 있으면 되는 거 아냐" → harness_date 제거하고 installed_at/upgraded_at 두 필드로 정리.

---

## 목적

`.mpa-version`을 `installed_at`(최초 설치일, 보존) + `upgraded_at`(최근 업그레이드일, 갱신) 구조로 바꾸고 죽은 `harness_date`를 제거한다.

---

## 구현 단계

- [ ] Step 1 — `install.py` `write_version()` 재작성:
  - 기존 `.mpa-version`에서 `installed_at`·`upgraded_at`·(레거시)`harness_date` 파싱
  - `installed_at` 확정: 기존 값 우선 → 없으면 레거시 `harness_date` 승계 → 그래도 없으면 today
  - `mode == "upgraded"`면 `upgraded_at = today`
  - 출력: `installed_at` 항상 + `upgraded_at`(있을 때) — `harness_date` 미출력
- [ ] Step 2 — `dist/.mpa-workspace/.mpa-version`을 날짜 필드 없는 placeholder 주석으로 교체
- [ ] Step 3 — 이 레포 설치본 `.mpa-workspace/.mpa-version`도 새 형식으로 정리(동기화)
- [ ] Step 4 — 검증: 신규 설치(installed_at=today)·기존 업그레이드(harness_date→installed_at 승계, upgraded_at=today) 시뮬레이션 단위 테스트

---

## 수정 대상 파일

| 파일 경로 | 변경 내용 |
|---------|---------|
| `install.py` | `write_version()` 재작성 |
| `dist/.mpa-workspace/.mpa-version` | placeholder 주석으로 교체 |
| `.mpa-workspace/.mpa-version` (이 레포 설치본) | 새 형식 동기화 |

## 참고 파일 (수정 없음)

- `install.py` `run_install` — write_version 호출부(mode 인자) 확인용
