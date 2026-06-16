---
태스크: discussion-bias-warnings
생성일: 2026-06-16
타입: minor
실패비용: minor
상태: 완료 승인
승인해시: 4cdc22ef5f02c58b
---

# 작업 계획서: discussion-bias-warnings

**파생 출처:** upgrade-candidate `discussion_premature_dichotomy.md` 채택

---

## 에이전트 보고

### 사용자 결정 필요
없음 (문구가 후보에 확정되어 있음)

### 암묵적 결정
- 적용 위치: `discussion_partner.md`의 `## LLM 행동 편향 경고` 절 맨 아래에 2개 항목 추가 (기존 4개 항목 뒤)

### 에이전트 가정
없음

### minor 판단 근거
- 한 파일/단일 관심사: `personas/discussion_partner.md` 한 절에 항목 추가
- 설계 결정 불필요: 후보에 문구 확정
- git reset으로 복구 가능: 규칙 파일 텍스트 변경
- 사용자 취향·의사결정 불필요: 채택 결정 완료

---

## 요청 사항

upgrade-candidate 채택 — discussion_partner 페르소나 편향 경고에 "이분법 조기 폐쇄 경계", "본주제 고도 점검" 2개 항목 추가.

---

## 핵심 기능

- `discussion_partner.md` 편향 경고 절에 항목 2개 추가
- 후보 파일 archive 이동 + 처리 결과 기록
- dist 자동 미러 확인
- current_version 갱신 (방법론 의미 변경)

---

## 구현 항목

- [ ] `personas/discussion_partner.md` — 편향 경고에 2개 항목 추가
- [ ] `.mpa-version` current_version → 2026-06-16 (이미 동일 — 확인만)
- [ ] upgrade-candidate archive 이동 + 처리 헤더 기록
