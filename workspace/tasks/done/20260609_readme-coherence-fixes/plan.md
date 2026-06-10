---
태스크: readme-coherence-fixes
생성일: 2026-06-09
타입: minor
실패비용: minor
상태: 완료 승인
승인해시: 96ebd56e89ac4c41
---
**목적:** README.md 정합성 점검에서 발견된 불일치 3건 수정 (minor GATE 2 오류 + 상태 모델 양끝 + 보정 나선 미반영)
**요청:** "전부 수정해줘" (🚨 minor GATE 2 + ⚠️ 상태 모델 + ⚠️ 철학 부분)
### 핵심 기능
- README:88 minor "GATE 2 없이 done" → "사용자 확인(GATE 2) 후 done"으로 수정 (현재 규칙과 일치)
- README:94 상태 모델에 양끝(설계 중/done)·게이트(⛔G1/⛔G2) 추가
- README 철학부에 "의도 보정 나선" 한 단락 추가 (guidebook 4.0 반영)
### minor 판단 근거
- 단일 관심사(README 정합화): O
- 설계 결정 불필요(수정 내용 점검에서 확정): O
- git reset 복구: O
- 취향·의사결정 불필요(사용자 전부 수정 승인): O
### 구현
1. README.md:88 — minor GATE 2 문장 교정
2. README.md:94 — 상태 모델 블록에 설계 중·done·GATE 표기 추가
3. README.md:29 앞 — 보정 나선 한 단락 추가
