---
태스크: version-history-split
생성일: 2026-06-11
타입: minor
실패비용: minor
상태: 완료 승인
승인해시: 26b444b9ce623fe9
---

# 작업 계획서: version-history-split

**파생 출처:** self-upgrade에서 `installed_at`이 06-01→06-11로 리셋되는 회귀 발견. 근본 원인은 "방법론 버전"과 "프로젝트 설치 이력"을 한 파일(.mpa-workspace/.mpa-version)에 묶은 것. 두 정보는 생명주기가 다름(버전=교체 갱신, 이력=보존).

---

## 에이전트 보고

### 사용자 결정 필요
- 없음 (사용자가 구조·이름·갱신 방식 모두 확정, 2026-06-11)

### 암묵적 결정
- `current_version` 값은 **날짜**(방법론 마지막 수정일). 이번 반영 시점은 2026-06-11.
- 두 파일 이름 분리: 버전=`.mpa-version`, 이력=`.mpa-version-history`.

### 에이전트 가정
| 가정 | 근거 | 틀렸다면 |
|-----|------|---------|
| 기존 프로젝트는 `.mpa-workspace/.mpa-version`에 installed_at 또는 harness_date를 가짐 | 직전 버전 형식 | 없으면 today로 기록 |

### minor 판단 근거
- 단일 관심사: `.mpa-version` 버전/이력 분리
- git 가역 / 외부연동·취향 결정 없음
- (구현 중 마이그레이션 로직이 복잡해지면 major 전환)

---

## 요청 원문
"current_version은 .mpa-workspace에, 설치/업그레이드 정보는 workspace에. current_version은 시스템 수정 날짜로 작업 처리 시 갱신. workspace/.mpa-version → .mpa-version-history로 이름 변경."

---

## 목적
방법론 버전(current_version)과 프로젝트 설치 이력(installed_at/upgraded_at)을 위치·파일로 분리해, 업그레이드 시 이력이 보존되도록 한다.

---

## 구현 단계
- [ ] Step 1 — `dist/.mpa-workspace/.mpa-version`을 `current_version: 2026-06-11` 한 줄로 교체 (방법론 버전)
- [ ] Step 2 — `dist/workspace/.mpa-version-history` 신규: placeholder 주석 (installed_at/upgraded_at은 설치 시 기록)
- [ ] Step 3 — `install.py` `write_version` 재작성:
  - 대상을 `workspace/.mpa-version-history`로 변경, 호출을 `copy_workspace_template` 이후로 이동
  - installed_at: 기존 history 값 우선 → 없으면 **마이그레이션 인자**(교체 전 레거시 .mpa-version에서 읽은 날짜) → 그래도 없으면 today
  - upgraded_at: 업그레이드 시 today
- [ ] Step 4 — `install.py` `run_install`: upgrade 분기에서 `.mpa-workspace` rmtree **전에** 레거시 `.mpa-version`의 installed_at/harness_date를 읽어 write_version에 전달(1회 마이그레이션)
- [ ] Step 5 — `agent_rules_detail.md` "MPA 파일 수정 세부"에 규칙 추가: "방법론 수정 완료 시 `dist/.mpa-workspace/.mpa-version`의 `current_version`을 작업일로 갱신"
- [ ] Step 6 — 이 레포 정리: `.mpa-workspace/.mpa-version` → `current_version: 2026-06-11`, `workspace/.mpa-version-history` 신규(`installed_at: 2026-06-01`, `upgraded_at: 2026-06-11`), 손상 복구
- [ ] Step 7 — dist ↔ 설치본 동기화 + 단위 테스트(신규설치 today / 업그레이드 보존 / 레거시 승계)

---

## 수정 대상 파일
| 파일 경로 | 변경 |
|---------|------|
| `dist/.mpa-workspace/.mpa-version` | current_version 한 줄로 교체 |
| `dist/workspace/.mpa-version-history` | 신규 placeholder |
| `install.py` | write_version 재작성 + run_install 마이그레이션 |
| `dist/.mpa-workspace/core/agent_rules_detail.md` | current_version 갱신 규칙 추가 |
| 이 레포 설치본 (`.mpa-workspace/.mpa-version`, `workspace/.mpa-version-history`, core 동기화) | 정리·복구·동기화 |

## 참고 (수정 없음)
- 기존 `mpa-version-dates` 태스크 산출물을 이 태스크가 재설계 — 회고: 위치 분리를 처음부터 못 봄
