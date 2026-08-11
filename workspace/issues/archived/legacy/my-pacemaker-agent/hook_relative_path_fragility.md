# [처리] 승인 — 2026-07-03 / 적용: install.py(_hook_cmd), .claude/settings.json, .codex/hooks.json, dist/.claude/settings.json (옵션 2 대신 옵션 1 계열 채택: agent별 cwd-독립 커맨드 — claude는 ${CLAUDE_PROJECT_DIR}, codex는 git rev-parse --show-toplevel)

# 훅 상대경로 견고성 — cwd 변경 시 훅 실패

> 타입: A (방법론/시스템 개선)
> 발견: 2026-06-16 (persona-skill-guidebook 작업 중)

## 문제

`.claude/settings.json`의 훅 커맨드가 상대경로를 쓴다:
```
python3 .mpa-workspace/hooks/code_gate.py --agent claude
python3 .mpa-workspace/hooks/session_start.py ...
python3 .mpa-workspace/hooks/dist_sync.py
python3 .mpa-workspace/hooks/turn_end.py ...
```

Bash 도구에서 `cd /…/.mpa-workspace; <cmd>` 형태로 하위 디렉터리에 들어간 직후 PreToolUse(Write/Edit) 훅이 발동하면, 상대경로가 바뀐 cwd 기준으로 해석되어:
```
.mpa-workspace/.mpa-workspace/hooks/code_gate.py  ← 이중화
can't open file ... [Errno 2] No such file or directory
```
훅이 크래시하며 Write/Edit가 차단된다. (이번 세션에서 토론 기록 Write가 한 번 막힘 → cwd 복귀 후 해결.)

## 영향

- 에이전트가 Bash에서 `cd` 한 번만 해도 이후 모든 파일 수정이 막힐 수 있다.
- 사용자가 원인을 알기 어렵다(에러 메시지가 훅 내부 경로라 모호).

## 개선 후보 (택1 또는 병행)

1. **훅 커맨드를 cwd-독립으로** — `$CLAUDE_PROJECT_DIR/.mpa-workspace/hooks/...` 절대경로 사용 (Claude Code가 제공하는 프로젝트 루트 환경변수). install.py가 settings.json 생성 시 이 형식으로 쓰도록.
2. **훅 스크립트 자체가 자기 위치 기준으로 동작** — code_gate.py 등이 `os.path.dirname(__file__)`로 워크스페이스 루트를 역산해 cwd에 의존하지 않게.
3. (보조) 에이전트 행동 규칙 — Bash에서 `cd` 지양, 필요 시 서브셸 `(cd X && cmd)`로 cwd 비영속화. 단 이는 회피책일 뿐 근본 해결 아님.

> 권장: 1 또는 2 (시스템 견고성). 3은 단독으로 불충분.
