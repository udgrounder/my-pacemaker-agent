---
태스크: install-config-verify
생성일: 2026-06-05
타입: minor
실패비용: minor
상태: 완료 승인
점검: 미점검
승인해시: 877a0a68d6f4fb1d
---
**목적:** install.py 업그레이드 시 CLAUDE.md Agents Workspace 섹션 내용을 최신과 비교해 자동 갱신

### 구현
1. `_extract_mpa_section` / `_replace_mpa_section` 헬퍼 추가
2. `append_agent_config` — 섹션 존재 시 내용 비교 후 갱신
