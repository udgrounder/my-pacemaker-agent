---
태스크: migrate-exclude-archive
생성일: 2026-06-11
타입: minor
실패비용: minor
상태: 완료 승인
승인해시: 723a647f414e62bd
---

# 작업 계획서: migrate-exclude-archive

**파생 출처:** classification-bias-warning 후보를 archive로 옮긴 뒤, install.py `migrate_upgrade_candidates`가 업그레이드 시 `upgrade-candidates/` 하위를 순회하며 `.gitkeep`만 건너뛰므로 `archive/` 폴더째 dist로 이동하는 문제 발견.

---

## 에이전트 보고

### 사용자 결정 필요
- 없음

### 암묵적 결정
- `archive/`는 처리 완료 후보의 이력 보관소이므로 dist로 이동(승격 파이프라인) 대상이 아니다 — 제외한다.

### minor 판단 근거
- 단일 관심사: migrate 시 archive 제외
- 방법 자명: skip 목록에 "archive" 추가
- git 가역 / 외부연동·취향 결정 없음

---

## 요청 원문
"archive는 dist에 제외하게 해줘."

---

## 목적
업그레이드 시 `upgrade-candidates/archive/`가 dist로 이동되지 않도록 한다.

---

## 구현 단계
- [ ] Step 1 — `install.py` `migrate_upgrade_candidates`의 iterdir 순회에서 `.gitkeep`과 함께 `archive` 디렉토리도 skip
- [ ] Step 2 — 단위 테스트: 후보 파일은 이동되고 archive/는 보존되는지 확인

---

## 수정 대상 파일
| 파일 경로 | 변경 |
|---------|------|
| `install.py` | `migrate_upgrade_candidates` skip 목록에 `archive` 추가 |
