# changelog — code_gate_scope

## 수정 파일

### `.mpa-workspace/hooks/code_gate.py`
- **변경:** `has_approved_task()` → `get_approved_scopes()` — `.approved` 파일 내용을 읽어 허용 경로 목록 반환
- **추가:** `in_approved_scope()` — 대상 파일이 허용 범위 내인지 확인 (접두사 매칭)
- **추가:** `main()` 에 범위 검사 로직 — 경로 명시 `.approved`가 있을 때 대상 파일이 범위 밖이면 `emit_warn` 주입
- **유지:** 빈 `.approved` → 기존과 동일하게 모든 경로 허용 (하위 호환)

### `.mpa-workspace/core/agent_rules.md`
- **추가:** "작업 진행" 승인 마커 생성 단계에 Level 1 태스크 경로 작성 안내

### `dist/.mpa-workspace/` 동기화
- `hooks/code_gate.py`, `core/agent_rules.md` 동기화 완료
