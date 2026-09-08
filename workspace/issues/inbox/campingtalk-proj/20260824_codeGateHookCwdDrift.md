---
{
  "type": "issue",
  "status": "open",
  "kind": "methodology_improvement",
  "canonical_key": "legacy-22f5ce68c73fbfd3",
  "canonical_issue_key": "legacy-22f5ce68c73fbfd3",
  "occurrence": "legacy_import",
  "area": "unspecified",
  "observed_release": "unknown",
  "collection_purpose": "review",
  "source_issue_id": "legacy-source-22f5ce68c73fbfd3",
  "workspace_issue_id": "legacy-workspace-22f5ce68c73fbfd3",
  "created_at": "2026-09-07T09:33:11+00:00",
  "legacy_source_filename": "20260824_codeGateHookCwdDrift.md"
}
---
# code_gate.py 훅이 Bash의 cwd 드리프트에 취약함

**타입**: 방법론 개선
**발견 상황**: `20260821_couponCptModuleMigration` 태스크 구현 중 — 소스가 `campingtalk-proj/campingtalk-proj/`(실제 git 루트) 아래에 있어서 `grep`/`gradle` 명령을 실행하려고 Bash에서 `cd campingtalk-proj/campingtalk-proj && ...`를 반복적으로 호출했다. 그 이후 같은 세션에서 Edit/Write 도구를 호출하면 `PreToolUse:Edit hook`(`code_gate.py`)이 `<마지막 Bash cwd>/.mpa/runtime/hooks/code_gate.py`를 찾다가 `.mpa/runtime`이 프로젝트 루트(`campingtalk-proj/`)에만 있고 중첩 폴더에는 없어서 `[Errno 2] No such file or directory`로 5회 이상 실패했다. 매번 `cd <project-root> && pwd`로 cwd를 되돌려야 다음 Edit/Write가 통과됐다.
**적용 범위**: 이 프로젝트 (소스 루트가 `.mpa/runtime`이 있는 프로젝트 루트보다 한 단계 더 안쪽에 있는 멀티 레포/서브모듈 구조에서는 다른 프로젝트에도 재발 가능)

## 현재 방식
`code_gate.py` 훅이 `.mpa/runtime/hooks/code_gate.py`를 프로세스의 현재 작업 디렉터리 기준 상대경로로 찾는 것으로 보인다. Bash 도구로 실행한 `cd`가 세션 내에서 유지되기 때문에, 소스 코드가 있는 하위 폴더로 `cd`한 뒤 Edit/Write를 호출하면 훅 자체가 실행되지 못하고 에러를 던진다.

## 개선 방안
- 훅 스크립트를 프로젝트 루트 기준 절대경로(또는 훅이 스스로 `.mpa` 상위 디렉터리를 탐색)로 실행하도록 수정하면, 에이전트가 소스 탐색을 위해 `cd`를 쓰더라도 훅이 깨지지 않는다.
- 에이전트 쪽에서도 "소스 루트가 `.mpa/runtime`이 있는 프로젝트 루트와 다른 경우, Bash에서 `cd`로 이동한 뒤에는 다음 Edit/Write 전에 반드시 프로젝트 루트로 되돌린다"는 규칙을 명시적으로 두면 재발을 줄일 수 있다(임시 완화책).

## 적용 대상 파일
- `.mpa/runtime/hooks/code_gate.py`
