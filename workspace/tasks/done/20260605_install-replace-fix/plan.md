---
태스크: install-replace-fix
생성일: 2026-06-05
타입: minor
실패비용: minor
상태: 완료 승인
점검: 미점검
승인해시: 6082f9a9729843d8
---
**목적:** _replace_mpa_section이 섹션 외부 내용을 재조립해 변경하는 버그 수정 — 문자 단위 범위 교체로 변경

### 구현
1. `_replace_mpa_section` 재작성 — 섹션 start/end 문자 인덱스만 교체
