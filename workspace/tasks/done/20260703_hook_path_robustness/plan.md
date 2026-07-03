---
태스크: hook_path_robustness
생성일: 2026-07-03
타입: minor
실패비용: minor
상태: 완료 승인
승인해시: dfe8494a3787fbff
---
**목적:** 훅 커맨드의 상대경로가 cwd 드리프트(예: Bash에서 `cd .mpa-workspace`) 시 깨지는 문제(`upgrade-candidates/hook_relative_path_fragility.md`)를 agent별로 안전한 방식으로 해결한다.
**요청:** "그럼 그렇게 해줘" — 앞선 대화에서 확정된 방향: Claude는 공식 문서에 확인된 `${CLAUDE_PROJECT_DIR}` 사용, codex는 `git rev-parse --show-toplevel`로 실행 시점에 저장소 루트를 스스로 찾는 방식. 둘 다 절대경로를 파일에 박지 않아 git 공유 시에도 안전함(사용자 확인 완료).

### 핵심 기능
- `install.py`의 `_hook_cmd()`를 agent별로 분기: claude → `${CLAUDE_PROJECT_DIR}/...`, codex → `git rev-parse --show-toplevel` 기반 래퍼, 그 외(openagent/antigravity 등 hook 미지원 agent) → 기존 방식 유지(회귀 없음).
- 이 레포 자신의 `.claude/settings.json`·`.codex/hooks.json`도 동일 형식으로 직접 수정 (이 두 파일은 `install.py`가 재실행되지 않는 한 자동 갱신되지 않으므로 수동 반영 필요).
- `dist_sync.py`용 PostToolUse 커맨드도 같은 취약점이 있어(`install.py`가 생성하지 않는 수동 등록 항목이지만) 동일하게 수정.
- 처리 완료 후 `upgrade-candidates/hook_relative_path_fragility.md`를 처리결과 기록 후 archive로 이동.

### 사용자 결정
- 메커니즘: agent별로 다른 방식 사용 확정 (Claude: `${CLAUDE_PROJECT_DIR}`, codex: git toplevel 탐색)

### 에이전트 가정
- `dist_sync.py` PostToolUse 항목은 `install.py`의 `build_hook_block()`/`wire_hooks()`가 생성하지 않는, 과거에 수동으로 추가된 항목으로 보인다(코드에 생성 로직이 없음을 grep으로 확인). 이번 태스크는 이 항목의 **문자열 내용만** 같은 패턴으로 고치고, "install.py가 이 항목을 자동 생성하지 않는다"는 별개 구조적 이슈는 범위 밖으로 둔다 — 필요하면 별도 upgrade-candidate로 기록.
- codex의 `bash -c '...'` 래퍼가 codex 훅 실행기에서 실제로 셸을 통해 실행되는지는 코드 구조(claude와 동일한 `{"type": "command", "command": "..."}` 형식)로 미루어 합리적으로 추정한 것이며, 이 세션에서 codex를 직접 구동해 검증할 수는 없다. 문법적으로 유효한 셸 명령인지는 로컬에서 직접 실행해 확인한다.

### 구현
1. [x] `install.py`의 `_hook_cmd()` agent별 분기 구현 완료 — 생성된 명령 문자열 확인 완료
2. [x] `.claude/settings.json`(+ `dist/.claude/settings.json`) 4개 커맨드 `${CLAUDE_PROJECT_DIR}` 형식으로 수정, JSON 유효성 확인
3. [x] `.codex/hooks.json` 4개 커맨드 git-toplevel 래퍼로 수정, 드리프트된 cwd에서 실제 bash 실행으로 정상 동작 확인(기존 방식 재현 시 실패하는 것도 대조 확인)
4. [x] `upgrade-candidates/hook_relative_path_fragility.md` 처리 완료 표시 후 archive로 이동, dist 수동 동기화
