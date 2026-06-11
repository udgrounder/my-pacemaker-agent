---
태스크: cost-notation-fix
생성일: 2026-06-11
타입: minor
실패비용: minor
상태: 완료 승인
승인해시: 88db6b70bea7b634
---
**목적:** principles.md 실패비용 표기의 곱셈기호(×) 오해 소지 제거 (Layer 2 발견 항목, 최소 수정)
**요청:** "최소 수정으로 진행하자" — 3축 표기 분산 중 principles.md:46의 × → 나열 형태
### 핵심 기능
- principles.md:46 "실패 비용 = 심각도 × 발견 가능성 × 가역성" → "실패 비용은 세 축으로 추정 — 심각도, 발견 가능성, 가역성" (guidebook:202 본문 정의와 통일)
### 구현
1. .mpa-workspace/core/principles.md:46 등식·곱셈 → 나열
