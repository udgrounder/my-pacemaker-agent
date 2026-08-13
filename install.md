# my-pacemaker-agent 설치 가이드

이 문서를 읽고 아래 **질의응답 절차**에 따라 사용자와 대화하며 파라메터를 결정한 뒤 `install.py`를 실행한다.

---

## 스크립트 위치

```
install.py
```

---

## 파라메터

| 파라메터 | 필수 | 설명 |
|---------|------|------|
| `--project` | ✅ | 설치 대상 프로젝트 경로 (절대 경로 권장) |
| `--agents` | ✅ | 사용할 agent (claude, codex, antigravity, openagent). 여러 개는 공백 또는 콤마로 구분: `--agents claude codex` 또는 `--agents claude,codex` |
| `--upgrade` | ❌ | 지원하지 않음 — 기존 설치본 Runtime 업데이트에는 `release_manager.py deploy` 사용 |
| `--dry-run` | ❌ | 최초 설치의 dependency·template·agent spec·변경 범위만 확인하고 파일은 변경하지 않음 |

---

## Agent Spec 구조

각 agent의 폴더 규칙과 주입 파일은 `agent-specs/` 에 정의되어 있다.

```
agent-specs/
  {agent}/
    spec.md          ← 이 agent의 감지 조건·폴더 규칙·설치 처리 정의
    inject/          ← 진입점 파일(CLAUDE.md 등)에 추가할 내용
    files/           ← 프로젝트에 복사할 파일 (디렉터리 구조 그대로)
```

| Agent | 진입점 | 감지 조건 |
|-------|--------|---------|
| `claude` | `CLAUDE.md` | `CLAUDE.md` 또는 `.claude/` 존재 |
| `codex` | `AGENTS.md` | `AGENTS.md` 또는 `.codex/` 존재 |
| `antigravity` | `GEMINI.md` | `GEMINI.md` 또는 `.gemini/` 존재 |
| `openagent` | 미정 | 감지 불가 → 사용자에게 확인 |

---

## 질의응답 절차

아래 순서대로 진행한다. 각 단계에서 이미 알고 있는 정보는 질문하지 않는다.

---

### Q1. 프로젝트 경로

| 상황 | 처리 |
|------|------|
| 사용자가 이미 경로를 알려준 경우 | 그 경로 사용, 바로 Q2로 진행 |
| 경로를 알 수 없는 경우 | 아래 질문 |

> "설치할 프로젝트 폴더 경로를 알려주세요."

---

### Q2. 사용할 Agent

경로가 결정되면 해당 폴더를 확인하여 agent를 감지한다.

| 감지 결과 | 처리 |
|-----------|------|
| 하나 이상 감지된 경우 | 감지 결과를 기본값으로 제시하며 아래 질문 |
| 감지 안 된 경우 | 아래 질문 |
| 사용자가 이미 명시한 경우 | 그 값 사용, 바로 Q3 진행 |

> (감지된 경우) "다음 agent가 감지됩니다: [목록]. 이대로 진행할까요, 아니면 변경하시겠어요? (claude / codex / antigravity / openagent 또는 조합)"
> (감지 안 됨) "어떤 agent를 사용하시나요? (claude / codex / antigravity / openagent 또는 조합)"

**openagent가 포함된 경우:** `agent-specs/openagent/spec.md` 를 읽고 질의 절차에 따라 사용자와 대화하여 설정을 결정한다. 확인된 내용으로 `spec.md`를 업데이트한다.

---

### Q3. Agent Spec 파일 적용

agent가 결정되면 각 agent의 `agent-specs/{agent}/spec.md` 를 읽어 설치 내용을 파악한다.

**agent별 파일 배치 규칙:**

각 agent는 자신의 전용 폴더 아래에만 파일을 설치한다. `agent-specs/{agent}/files/` 의 디렉터리 구조가 프로젝트에 그대로 복사된다.

| Agent | native 폴더 (직접 배치) |
|-------|----------------------|
| `claude` | `.claude/agents/mpa_pacemaker.md` |
| `codex` | `.agents/rules/mpa_pacemaker.md`, `.codex/agents/mpa_pacemaker.toml` |
| `antigravity` | `.agents/rules/mpa_pacemaker.md` (codex와 공유) |
| `openagent` | spec.md 질의 결과에 따름 |

workspace는 어떤 agent를 사용하든 동일하므로 프로젝트 루트에 한 번만 설치한다.

**install.py가 자동 처리하는 항목:**
- `inject/` → 진입점 파일(CLAUDE.md 등)에 Agents Workspace 섹션 추가
- `files/` → agent 전용 폴더에 파일 복사 (없는 경우만)
- **hook 등록** → `claude`/`codex`는 settings 파일(`.claude/settings.json` / `.codex/hooks.json`)에 안전 병합 (기존 설정 보존, 멱등)
  - `codex`의 `PreToolUse` matcher는 `apply_patch`, `write_file`, `replace`, `edit` 등 Codex 편집 도구명을 포함해 등록

**hook 미확인 agent (`antigravity` / `openagent`):**
install.py는 hook을 자동 등록하지 않는다. 실행 중인 agent가 `agent-specs/{agent}/spec.md` 의 hook 질의 절차에 따라
지원 여부를 확인하고 설정한 뒤 spec.md를 갱신한다. (antigravity는 Gemini CLI 기준 기본값이 spec.md에 준비돼 있다.)

**install.py 실행 전 안내:**
- 어떤 파일이 어느 폴더에 설치되는지, hook이 어느 settings에 등록되는지 사용자에게 요약하여 알린다

---

### Q4. 신규 설치 vs Runtime 업데이트

질문 없이 자동으로 결정한다.

| 조건 | 모드 |
|------|------|
| `.mpa-workspace/` 폴더 없음 | 신규 설치 — `install.py` 실행 |
| `.mpa-workspace/` 폴더 있음 | 설치 중단 — 승인된 release manifest로 Runtime만 배포 |

---

### Q5. 설치 실행

Q1~Q4에서 수집한 정보를 요약하여 사용자에게 알린 뒤 `install.py`를 실행한다.

```
모드   : 신규 설치
경로   : <결정된 경로>
agents : <결정된 agent>
```

여러 agent를 함께 지정할 때는 공백 또는 콤마로 구분한다 (`--agents claude codex antigravity` 또는 `--agents claude,codex,antigravity`).

```bash
# 신규 설치
python3 install.py --project <경로> --agents <agent ...>

# Runtime 초기값이 필요한 신규 설치
# runtime-config.json은 runtime.* scalar additive defaults만 포함한다.
python3 install.py --project <경로> --agents <agent ...> \
  --runtime-config-json runtime-config.json

# Runtime 업데이트 (source 저장소에서 실행)
python3 release_manager.py deploy \
  --manifest workspace/releases/<release-id>/manifest_<release-id>.json \
  --target <경로> --target-ref <대상-식별자> --verified-by <검증자>
```

### Runtime release 준비·배포·롤백

다음 명령은 **my-pacemaker-agent source 저장소에서만** 실행한다. Runtime release에는 `dist/.mpa-workspace/`만 포함된다. update 시 대상의 `workspace/` 또는 루트 `docs/`가 없으면 빈 폴더만 생성하며, 이미 존재하는 폴더·agent 설정·일반 소스는 변경하지 않는다.

보관 자산은 용도별로 분리한다. `workspace/releases/<release-id>/package_<release-id>.zip`은 배포 기준과 릴리즈 이력을 보존하는 불변 release archive이고, deploy가 대상에 만드는 `.mpa-backups/` 디렉터리는 `runtime/.mpa-workspace/`와 migration 대상인 경우 `runtime-config/config.yaml`을 보존하는 운영 snapshot이다. 기존 사용자 설정은 Runtime 프로젝트 자체의 버전 관리·백업으로 관리하며 MPA deploy가 덮어쓰지 않는다.

```bash
# 1. source 동기화·검증 후 불변 package와 manifest 생성 (출력된 단일 release ID를 기록)
python3 release_manager.py prepare-release \
  --verified-by <검증자> --compatibility <호환성> --breaking-change <없음/내용> \
  --migration <없음/절차> --rollback-condition <조건> --release-note <요약> \
  --validation-command '["python3", "-m", "unittest", "discover", "-s", "tests"]'

# Runtime이 사용할 새 기본값이 필요한 release만 추가
# runtime-config.json: {"schema_version": 2, "additive_defaults": {
#   "runtime.project_name": "${project.name}",
#   "runtime.root_path": "${project.root_path}",
#   "runtime.feature_enabled": true
# }}
# prepare-release에 --runtime-config-json runtime-config.json 을 덧붙인다.

# 2. 모든 활성 release bundle의 ZIP·manifest·note·receipt 정합성 확인
python3 release_manager.py release-audit

# 3. 대상의 현재 release와 새 release를 기록한 dry-run 생성
python3 release_manager.py deployment-dry-run \
  --manifest workspace/releases/<release-id>/manifest_<release-id>.json \
  --target <프로젝트-경로> --target-ref <소문자-식별자>

# 4. dry-run, 명시 승인, rollback 책임자를 연결해 Runtime만 배포
python3 release_manager.py deploy \
  --manifest workspace/releases/<release-id>/manifest_<release-id>.json \
  --target <프로젝트-경로> --target-ref <소문자-식별자> --verified-by <검증자> \
  --dry-run workspace/receipts/deployments/<대상>/dry-run-<release-id>-<id>.json \
  --approved-by <승인자> --approval-ref <승인-기록> --rollback-owner <책임자>

# 5. 문제가 있을 때, deploy 출력의 .mpa-backups/... 값을 그대로 사용해 rollback
python3 release_manager.py rollback \
  --target <프로젝트-경로> --target-ref <소문자-식별자> \
  --backup .mpa-backups/<release-id>-<timestamp>-<id> --release-id <release-id> \
  --verified-by <검증자> --approved-by <승인자> --approval-ref <승인-기록> \
  --rollback-owner <책임자>
```

---

## 설치 결과

신규 설치 시 생성되는 파일:

```
[project]/
├── .mpa-workspace/          ← 방법론 스냅샷 (harness에서 복사)
├── CLAUDE.md                   ← claude 포함 시 (Agents Workspace 섹션)
├── AGENTS.md                   ← codex 포함 시 (Agents Workspace 섹션)
├── GEMINI.md                   ← antigravity 포함 시 (Agents Workspace 섹션)
├── workspace/                  ← 모든 agent 공용 (프로젝트 루트)
│   ├── memory/
│   ├── tasks/
├── docs/                       ← 사용자 문서 루트 (없는 경우만 빈 폴더 생성)
├── .claude/                    ← claude 포함 시
│   ├── agents/mpa_pacemaker.md ← native 폴더에 직접 배치
│   └── settings.json           ← hook 등록 (SessionStart / PreToolUse / Stop)
├── .codex/                     ← codex 포함 시
│   ├── agents/mpa_pacemaker.toml ← developer_instructions 로 규칙 파일 진입
│   └── hooks.json                 ← hook 등록
└── .agents/                    ← codex 또는 antigravity 포함 시
    └── rules/mpa_pacemaker.md  ← native 폴더에 직접 배치
```

> **hook 동작:** `.mpa-workspace/hooks/` 의 스크립트가 세션 시작 시 진행 태스크·라우팅 규칙을 주입하고,
> `plan.md` 상태가 `구현 중`인 active 태스크 없이 소스코드를 수정하면 차단한다.
> 구현 승인 후에는 `plan_hash.py approve`로 `승인해시`를 갱신하며, 이후 plan.md 본문이 바뀌면 재승인이 필요하다.
> Codex는 `.codex/hooks.json`의 `PreToolUse` matcher에 `apply_patch|write_file|replace|edit` 등을 포함해 게이트 실효성을 확보한다.
> 게이트 강도는 환경변수 `MPA_GATE`(block/warn/off)로 조절한다.

기존 설치본의 Runtime 업데이트는 배포 전 `.mpa-workspace/`와 예정된 `runtime.*` 설정을 `.mpa-backups/`에 보관한 뒤 교체·추가한다. 성공한 deploy 뒤 대상 `.mpa-backups/`의 성공 Runtime backup은 최신 3개만 남기며, 실패 backup은 정리하지 않는다. 배포·rollback은 `.mpa-project/config.yaml`의 기존 project/user 값, agent 설정, `workspace/`, 루트 `docs/`, 일반 소스를 변경하지 않는다. migration으로 추가된 MPA 설정은 rollback 때 함께 복원하며, 그 밖의 설정 변경과 전체 프로젝트 백업은 Runtime 프로젝트 자체의 절차로 처리한다.
