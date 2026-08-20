#!/usr/bin/env python3
"""
Agents Workspace 설치 스크립트
사용법: install.md 참조
"""

import argparse
import datetime
import json
import shutil
import stat
import sys
from pathlib import Path
from typing import Optional

from project_config import (CONFIG_RELATIVE, apply_runtime_config_migration,
                            ensure_project_config, inspect_project_config,
                            preview_runtime_config_migration, validate_runtime_config_migration)

HARNESS_ROOT = Path(__file__).parent
DIST_ROOT = HARNESS_ROOT / "dist"
AGENTS_WORKSPACE_SRC = DIST_ROOT / ".mpa-workspace"
WORKSPACE_TEMPLATE_SRC = DIST_ROOT / "workspace"
AGENT_SPECS_SRC = HARNESS_ROOT / "agent-specs"
AGENT_CONFIGS_SRC = HARNESS_ROOT / "agent-configs"  # 레거시 fallback
DOCS_INDEX_TEMPLATE = "# 문서 색인\n\n> 이 파일은 agent가 문서 산출물의 위치와 요약을 관리합니다. 일반 문서 내용은 프로젝트 사용자가 소유합니다.\n\n"

AGENT_CONFIG_MAP = {
    "claude":       "CLAUDE.md",
    "codex":        "AGENTS.md",
    "antigravity":  "GEMINI.md",
    "openagent":    None,   # 실험적·수동 설정 지원 — 자동 진입점 주입 없음
}

# hook 자동 와이어링이 확인된 agent와 설정 파일 경로 (프로젝트 루트 기준)
# antigravity는 hook 지원 확인이 필요하고, openagent는 실험적·수동 설정 지원이다.
HOOK_SETTINGS_PATH = {
    "claude": (".claude", "settings.json"),
    "codex":  (".codex", "hooks.json"),
}

HOOK_DIR_REL = ".mpa-workspace/hooks"
HOOK_MARKER = "mpa-workspace/hooks"  # 멱등성 판별용 (이미 등록됐는지)


def _hook_cmd(script: str, agent: str) -> str:
    """훅 커맨드 문자열을 만든다.

    상대경로(`.mpa-workspace/hooks/...`)만 쓰면 에이전트가 Bash에서 cd한 뒤
    cwd가 바뀐 상태로 훅이 실행될 때 파일을 못 찾아 크래시한다
    (`workspace/issues/`로 이관된 hook path robustness issue 참조).
    agent별로 cwd에 의존하지 않는 방식을 쓴다 — 둘 다 절대경로를 파일에
    박아넣지 않으므로 settings.json/hooks.json을 git으로 공유해도 안전하다.
    """
    if agent == "claude":
        # Claude Code 공식 지원 변수 (code.claude.com/docs/en/hooks.md)
        return f"python3 ${{CLAUDE_PROJECT_DIR}}/{HOOK_DIR_REL}/{script} --agent {agent}"
    if agent == "codex":
        # 환경변수 지원 여부가 불확실해 git 저장소 루트를 직접 탐색한다
        return (
            'bash -c \'cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)" '
            f"&& python3 {HOOK_DIR_REL}/{script} --agent {agent}'"
        )
    # 그 외 agent(hook 자동 배선 미지원) — 기존 방식 유지, 회귀 없음
    return f"python3 {HOOK_DIR_REL}/{script} --agent {agent}"


def build_hook_block(agent: str) -> dict:
    """agent별 settings 구조의 hooks 블록을 만든다."""
    matcher = "Edit|Write"
    if agent == "codex":
        matcher = "Edit|Write|MultiEdit|apply_patch|write_file|replace|edit"
    return {
        "SessionStart": [
            {"hooks": [{"type": "command", "command": _hook_cmd("session_start.py", agent)}]}
        ],
        "PreToolUse": [
            {"matcher": matcher,
             "hooks": [{"type": "command", "command": _hook_cmd("code_gate.py", agent)}]}
        ],
        "Stop": [
            {"hooks": [{"type": "command", "command": _hook_cmd("turn_end.py", agent)}]}
        ],
    }


# ──────────────────────────────────────────────
# 유틸
# ──────────────────────────────────────────────

def ask(prompt: str, default: str = "") -> str:
    display = f"{prompt} [{default}]: " if default else f"{prompt}: "
    answer = input(display).strip()
    return answer if answer else default


def ask_yes_no(prompt: str, default: bool = True) -> bool:
    hint = "Y/n" if default else "y/N"
    answer = input(f"{prompt} ({hint}): ").strip().lower()
    if not answer:
        return default
    return answer in ("y", "yes")


def read_config_content(agent: str) -> Optional[str]:
    """agent-specs/{agent}/inject/ 에서 진입점 파일 내용을 읽어 반환.
    없으면 레거시 agent-configs/ 에서 fallback."""
    filename = AGENT_CONFIG_MAP.get(agent)
    if not filename:
        return None

    # agent-specs 우선
    inject_file = AGENT_SPECS_SRC / agent / "inject" / filename
    if inject_file.exists():
        lines = inject_file.read_text(encoding="utf-8").splitlines()
        for i, line in enumerate(lines):
            if line.startswith("## "):
                return "\n".join(lines[i:]).strip()
        return None

    # 레거시 fallback
    legacy_file = AGENT_CONFIGS_SRC / filename
    if legacy_file.exists():
        lines = legacy_file.read_text(encoding="utf-8").splitlines()
        for i, line in enumerate(lines):
            if line.startswith("## "):
                return "\n".join(lines[i:]).strip()

    return None


# ──────────────────────────────────────────────
# 설치 로직
# ──────────────────────────────────────────────

_IGNORE = shutil.ignore_patterns(".DS_Store", ".gitkeep")


def read_legacy_installed(agents_workspace_dst: Path) -> str:
    """업그레이드 시 .mpa-workspace 교체 전에 호출한다.
    구버전 .mpa-workspace/.mpa-version에서 설치일(installed_at 또는 레거시
    harness_date)을 읽어 마이그레이션용으로 반환한다. 없으면 빈 문자열.
    (방법론 release ID는 `current_release`로 분리되며 install.py가 다루지 않는다.)
    """
    legacy = agents_workspace_dst / ".mpa-version"
    if not legacy.exists():
        return ""
    installed = harness = ""
    for line in legacy.read_text(encoding="utf-8").splitlines():
        if line.startswith("installed_at:"):
            installed = line.split(":", 1)[1].strip()
        elif line.startswith("harness_date:"):
            harness = line.split(":", 1)[1].strip()
    return installed or harness


def write_version(workspace_dst: Path, mode: str, legacy_installed: str = ""):
    """프로젝트 설치 이력을 workspace/.mpa-version-info에 기록한다.

    방법론 release ID(current_release)는 .mpa-workspace/.mpa-version에 있고 통째 교체로
    갱신되므로 여기서 다루지 않는다. 이력은 workspace에 있어 업그레이드 시 보존된다.

    - installed_at: 기존 history 값 보존 > 레거시 승계(마이그레이션) > 설치 당일
    - upgraded_at: 업그레이드할 때마다 갱신
    """
    vf = workspace_dst / ".mpa-version-info"

    installed_at = ""
    upgraded_at = ""
    if vf.exists():
        for line in vf.read_text(encoding="utf-8").splitlines():
            if line.startswith("installed_at:"):
                installed_at = line.split(":", 1)[1].strip()
            elif line.startswith("upgraded_at:"):
                upgraded_at = line.split(":", 1)[1].strip()

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 최초 설치 시각 확정: 기존 history > 레거시 승계 > 설치 시각
    if not installed_at:
        installed_at = legacy_installed or now_str

    if mode == "upgraded":
        upgraded_at = now_str

    lines = [f"installed_at: {installed_at}"]
    if upgraded_at:
        lines.append(f"upgraded_at: {upgraded_at}")
    workspace_dst.mkdir(parents=True, exist_ok=True)
    vf.write_text("\n".join(lines) + "\n", encoding="utf-8")


def copy_agents_workspace(dst: Path):
    shutil.copytree(AGENTS_WORKSPACE_SRC, dst, ignore=_IGNORE)
    print(f"  [복사] .mpa-workspace/ → {dst}")



def _is_harness_managed(name: str) -> bool:
    """하네스가 관리하는 파일 여부 — upgrade 시 항상 최신으로 교체한다."""
    return name == "README.md"


def _merge_dir(src: Path, dst: Path, base: Path, label: str = "", upgrade: bool = False):
    """src 구조를 dst에 병합한다.
    - 신규: 없는 항목만 추가
    - 업그레이드: 하네스 관리 파일(README.md, *_template.md)은 항상 교체, 나머지는 없는 것만 추가
    """
    dst.mkdir(parents=True, exist_ok=True)
    added = 0
    for item in src.iterdir():
        if item.name in (".DS_Store", ".gitkeep"):
            continue
        # docs/는 프로젝트 사용자가 루트에 소유·생성한다. 과거 템플릿의 빈
        # 문서 디렉터리는 별도 루트 정책으로 관리하므로 Runtime 골격에 복사하지 않는다.
        if src == WORKSPACE_TEMPLATE_SRC and item.name == "docs":
            continue
        dst_item = dst / item.name
        rel = dst_item.relative_to(base)
        prefix = f"{label}/" if label else ""

        if item.is_dir():
            added += _merge_dir(item, dst_item, base, label, upgrade)
        elif upgrade and _is_harness_managed(item.name) and dst_item.exists():
            shutil.copy2(item, dst_item)
            print(f"  [업데이트] {prefix}{rel}")
            added += 1
        elif not dst_item.exists():
            shutil.copy2(item, dst_item)
            print(f"  [추가] {prefix}{rel}")
            added += 1
    return added


def _extract_mpa_section(text: str) -> Optional[str]:
    """CLAUDE.md 등에서 '## Agents Workspace' 섹션만 추출한다."""
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.strip() == "## Agents Workspace":
            start = i
            break
    if start is None:
        return None
    # 다음 ## 섹션 또는 파일 끝까지
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("## "):
            return "\n".join(lines[start:j]).strip()
    return "\n".join(lines[start:]).strip()


def _replace_mpa_section(text: str, new_section: str) -> str:
    """MPA 섹션만 교체한다. 섹션 외부는 문자 단위로 일절 변경하지 않는다."""
    import re
    marker = "## Agents Workspace"
    start = text.find(marker)
    if start == -1:
        sep = "\n\n" if text.strip() else ""
        return text.rstrip("\n") + sep + new_section + "\n"
    after_marker = text[start + len(marker):]
    next_sep = re.search(r'\n\n(## )', after_marker)
    if next_sep:
        section_end = start + len(marker) + next_sep.start()
        return text[:start] + new_section + text[section_end:]
    else:
        return text[:start] + new_section + "\n"


def append_agent_config(agent: str, project_path: Path):
    """진입점 파일(CLAUDE.md 등)에 Agents Workspace 섹션을 추가한다."""
    filename = AGENT_CONFIG_MAP.get(agent)
    if not filename:
        print(f"  [건너뜀] {agent} — 진입점 파일 없음 (AI agent가 처리)")
        return

    config_dst = project_path / filename
    content = read_config_content(agent)

    if content is None:
        print(f"  [경고] {agent} inject 파일 없음, 건너뜀")
        return

    if config_dst.exists():
        existing = config_dst.read_text(encoding="utf-8")
        if "Agents Workspace" in existing:
            existing_section = _extract_mpa_section(existing)
            if existing_section and existing_section.strip() != content.strip():
                updated = _replace_mpa_section(existing, content)
                config_dst.write_text(updated, encoding="utf-8")
                print(f"  [업데이트] {filename} — Agents Workspace 섹션 갱신")
            else:
                print(f"  [확인] {filename} — Agents Workspace 섹션 최신")
            return
        with open(config_dst, "a", encoding="utf-8") as f:
            f.write("\n\n" + content + "\n")
        print(f"  [추가] {filename}")
    else:
        config_dst.write_text(content + "\n", encoding="utf-8")
        print(f"  [생성] {filename}")


def copy_agent_spec_files(agent: str, project_path: Path):
    """agent-specs/{agent}/files/ 의 파일을 프로젝트에 복사한다 (없는 경우만)."""
    files_src = AGENT_SPECS_SRC / agent / "files"
    if not files_src.exists():
        return
    added = _merge_dir(files_src, project_path, project_path, label="")
    if added == 0:
        print(f"  [확인] {agent} spec 파일 추가할 항목 없음")


# workspace/README.md 단일본으로 통합되면서 폐기된 폴더별 README.
# 업그레이드 시 기존 설치본에서 제거한다. _merge_dir 은 추가/교체만 하므로
# 삭제는 이 고정 경로 목록으로만 수행한다 — 사용자 생성 README 는 건드리지 않는다.
_OBSOLETE_WORKSPACE_README = (
    "tasks/README.md",
    "memory/README.md",
    "docs/README.md",
)


def remove_obsolete_readmes(dst: Path):
    """과거 버전의 폴더별 README 를 제거한다 (workspace/README.md 로 통합됨).
    명시된 고정 경로만 삭제하며, 그 외 파일은 일절 건드리지 않는다."""
    for rel in _OBSOLETE_WORKSPACE_README:
        target = dst / rel
        if target.exists():
            target.unlink()
            print(f"  [정리] workspace/{rel} 제거 (workspace/README.md 로 통합)")


def copy_workspace_template(dst: Path, upgrade: bool = False):
    added = _merge_dir(WORKSPACE_TEMPLATE_SRC, dst, dst, label="workspace", upgrade=upgrade)
    if upgrade:
        remove_obsolete_readmes(dst)
    if added == 0:
        print("  [확인] workspace/ 추가할 항목 없음")


def make_hooks_executable(project_path: Path):
    """설치된 hook 스크립트에 실행 권한을 부여한다."""
    hooks_dir = project_path / ".mpa-workspace" / "hooks"
    if not hooks_dir.exists():
        return
    for f in hooks_dir.glob("*.py"):
        mode = f.stat().st_mode
        f.chmod(mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)


def _block_already_registered(arr: list) -> bool:
    """이벤트 배열에 이미 mpa hook이 등록돼 있는지 검사 (멱등성)."""
    for entry in arr:
        for h in entry.get("hooks", []) if isinstance(entry, dict) else []:
            if HOOK_MARKER in str(h.get("command", "")):
                return True
    return False


def wire_hooks(agent: str, project_path: Path):
    """claude/codex 의 settings 파일에 hook 블록을 안전 병합한다.
    - 기존 설정을 보존한다 (덮어쓰지 않음)
    - 이미 등록돼 있으면 건너뛴다 (멱등)
    - 파일이 손상된 JSON이면 건드리지 않고 경고만 출력한다
    """
    rel = HOOK_SETTINGS_PATH.get(agent)
    if rel is None:
        return
    settings_path = project_path / rel[0] / rel[1]

    data: dict = {}
    if settings_path.exists():
        text = settings_path.read_text(encoding="utf-8").strip()
        if text:
            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                print(f"  [경고] {settings_path.name} 파싱 실패 — hook 등록 건너뜀 (수동 등록 필요)")
                return
        if not isinstance(data, dict):
            print(f"  [경고] {settings_path.name} 형식이 예상과 다름 — hook 등록 건너뜀")
            return

    hooks = data.setdefault("hooks", {})
    added = 0
    for event, entries in build_hook_block(agent).items():
        arr = hooks.setdefault(event, [])
        if not isinstance(arr, list):
            print(f"  [경고] {settings_path.name} hooks.{event} 형식 이상 — 건너뜀")
            continue
        if _block_already_registered(arr):
            continue
        arr.extend(entries)
        added += 1

    if added == 0:
        print(f"  [확인] {rel[0]}/{rel[1]} hook 이미 등록됨")
        return

    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"  [등록] {rel[0]}/{rel[1]} — hook {added}개 이벤트")


def run_install(project_path: Path, agents: list, upgrade: bool, runtime_config=None):
    agents_workspace_dst = project_path / ".mpa-workspace"
    workspace_dst = project_path / "workspace"

    if upgrade:
        raise ValueError("install.py는 기존 설치본의 update를 지원하지 않습니다")

    config_result = ensure_project_config(project_path)
    if config_result["status"] in {"warning", "unchanged"}:
        print(f"  [확인] {CONFIG_RELATIVE} — {config_result['status']}")
    else:
        print(f"  [생성/보강] {CONFIG_RELATIVE} — {', '.join(config_result.get('add', []))}")
    if runtime_config is not None:
        migration_result = apply_runtime_config_migration(project_path, runtime_config)
        print(f"  [Runtime config] {migration_result['status']} — 추가: {', '.join(migration_result.get('add', [])) or '없음'}")

    print("\n[1단계] .mpa-workspace 설치")
    copy_agents_workspace(agents_workspace_dst)
    print("\n[2단계] workspace 초기화")
    copy_workspace_template(workspace_dst)
    (workspace_dst / "issues").mkdir(parents=True, exist_ok=True)
    print("  [생성] workspace/issues/ (로컬 issue 수집함, 빈 폴더)")
    write_version(workspace_dst, "installed")
    docs_dst = project_path / "docs"
    if not docs_dst.exists():
        docs_dst.mkdir(parents=True)
        print("  [생성] docs/ (사용자 문서 루트, 빈 폴더)")
    docs_index = docs_dst / "INDEX.md"
    if not docs_index.exists():
        docs_index.write_text(DOCS_INDEX_TEMPLATE, encoding="utf-8")
        print("  [생성] docs/INDEX.md (agent 관리 문서 색인)")

    print("\n[hook] 스크립트 실행 권한 부여")
    make_hooks_executable(project_path)

    print("\n[마지막] agent 설정 적용")
    for agent in agents:
        print(f"\n  ── {agent} ──")
        append_agent_config(agent, project_path)
        copy_agent_spec_files(agent, project_path)
        if agent in HOOK_SETTINGS_PATH:
            wire_hooks(agent, project_path)
        elif agent == "antigravity":
            print(f"  [안내] {agent} — hook 지원 확인 필요. "
                  f"agent-specs/{agent}/spec.md 질의 절차에 따라 설정하세요.")
        elif agent == "openagent":
            print("  [제한] openagent — 실험적·수동 설정 지원입니다. "
                  "자동 진입점·규칙 파일·hook 연결은 수행하지 않습니다. "
                  "agent-specs/openagent/spec.md의 확인 절차를 따라 별도로 설정하세요.")


# ──────────────────────────────────────────────
# 대화형 입력
# ──────────────────────────────────────────────

def detect_agents(project_path: Path) -> list:
    """프로젝트 경로에서 사용 중인 agent를 감지한다."""
    detected = []
    if (project_path / "CLAUDE.md").exists() or (project_path / ".claude").exists():
        detected.append("claude")
    if (project_path / "AGENTS.md").exists() or (project_path / ".codex").exists():
        detected.append("codex")
    if (project_path / "GEMINI.md").exists() or (project_path / ".gemini").exists():
        detected.append("antigravity")
    return detected


def prompt_agents(project_path: Path) -> list:
    detected = detect_agents(project_path)

    print("\n사용 중인 agent:")
    for i, (key, filename) in enumerate(AGENT_CONFIG_MAP.items(), 1):
        mark = "✓" if key in detected else " "
        label = filename if filename else "실험적·수동 설정 (spec.md)"
        print(f"  [{mark}] {i}. {key} ({label})")

    print("\n설정할 agent를 입력하세요.")
    print("  예) claude / codex / claude,codex / claude,codex,antigravity")

    default = ",".join(detected) if detected else ""
    answer = ask("agent", default)

    agents = [a.strip().lower() for a in answer.split(",") if a.strip()]

    invalid = [a for a in agents if a not in AGENT_CONFIG_MAP]
    if invalid:
        print(f"오류: 지원하지 않는 agent: {', '.join(invalid)}")
        return prompt_agents(project_path)

    return agents


def prompt_project_path() -> Path:
    default = str(Path.cwd())
    answer = ask("\n프로젝트 경로", default)
    project_path = Path(answer).resolve()

    if not project_path.exists():
        print(f"오류: 경로가 존재하지 않습니다: {project_path}")
        return prompt_project_path()

    return project_path


def parse_args():
    parser = argparse.ArgumentParser(description="my-pacemaker-agent 설치 스크립트")
    parser.add_argument("--project", help="설치 대상 프로젝트 경로")
    parser.add_argument(
        "--agents",
        nargs="+",
        help="사용 중인 agent (claude, codex, antigravity, openagent[실험적·수동 설정]). "
        "공백 또는 콤마로 여러 개 지정: --agents claude codex 또는 --agents claude,codex",
    )
    parser.add_argument(
        "--upgrade", action="store_true",
        help="더 이상 지원하지 않음: Runtime 업데이트는 release_manager.py deploy를 사용",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="신규 설치 가능 여부와 변경 범위만 확인하고 파일은 변경하지 않음",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="dry-run 결과를 machine-readable JSON으로 출력",
    )
    parser.add_argument(
        "--runtime-config-json",
        help="신규 Runtime config의 runtime.* additive defaults JSON 파일",
    )
    return parser.parse_args()


def main():
    print("=== my-pacemaker-agent 설치 ===")

    cli = parse_args()

    # 1. 프로젝트 경로
    if cli.project:
        project_path = Path(cli.project).resolve()
        if project_path.exists() and not project_path.is_dir():
            print(f"오류: 프로젝트 경로가 디렉터리가 아닙니다: {project_path}")
            return 1
        print(f"\n프로젝트 경로: {project_path}")
    else:
        project_path = prompt_project_path()

    # 2. 최초 설치만 담당한다. Runtime 업데이트는 release_manager.py deploy로
    # .mpa-workspace만 교체해야 하므로 여기서 workspace/설정을 다시 건드리지 않는다.
    agents_workspace_dst = project_path / ".mpa-workspace"
    if cli.upgrade or agents_workspace_dst.exists():
        print("오류: 기존 설치본 업데이트는 release_manager.py deploy를 사용하세요.")
        return 1
    upgrade = False
    print(f"\n.mpa-workspace/ 없음 → 신규 설치 모드")

    # 3. agent 선택
    if cli.agents:
        # --agents는 공백·콤마 구분을 모두 허용한다.
        # nargs='+'로 받은 토큰 리스트의 각 항목을 콤마로 한 번 더 분리한다.
        raw = ",".join(cli.agents)
        agents = [a.strip().lower() for a in raw.split(",") if a.strip()]
        invalid = [a for a in agents if a not in AGENT_CONFIG_MAP]
        if invalid:
            print(f"오류: 지원하지 않는 agent: {', '.join(invalid)}")
            return 1
        print(f"\nagents: {', '.join(agents)}")
    else:
        agents = prompt_agents(project_path)

    if not agents:
        print("오류: agent를 하나 이상 선택해야 합니다.")
        return 1

    # 신규 설치 전에 source·Python·agent spec의 최소 실행 조건과 변경 범위를 확인한다.
    missing = [str(path) for path in (DIST_ROOT / ".mpa-workspace", DIST_ROOT / "workspace") if not path.is_dir()]
    missing.extend(str(AGENT_SPECS_SRC / agent / "spec.md") for agent in agents
                   if not (AGENT_SPECS_SRC / agent / "spec.md").is_file())
    for agent in agents:
        if agent in HOOK_SETTINGS_PATH:
            try:
                if not build_hook_block(agent):
                    missing.append(f"{agent} hook configuration")
            except (KeyError, ValueError):
                missing.append(f"{agent} hook configuration")
    if sys.version_info < (3, 8):
        missing.append("python>=3.8")
    config_plan = inspect_project_config(project_path)
    runtime_config = None
    runtime_config_plan = {"status": "none", "add": [], "skipped": []}
    if cli.runtime_config_json:
        migration_path = Path(cli.runtime_config_json)
        if not migration_path.is_absolute():
            migration_path = HARNESS_ROOT / migration_path
        try:
            runtime_config = validate_runtime_config_migration(
                json.loads(migration_path.read_text(encoding="utf-8")))
            runtime_config_plan = preview_runtime_config_migration(project_path, runtime_config)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            runtime_config_plan = {"status": "warning", "add": [], "skipped": [], "warnings": [str(error)]}
    plan = {
        "schema_version": 1,
        "mode": "install",
        "target": str(project_path),
        "agents": agents,
        "create": (["project root/"] if not project_path.exists() else []) + [".mpa-workspace/", "workspace/ initial skeleton", "docs/ empty user document root", "selected agent entry settings"] + ([CONFIG_RELATIVE] if config_plan["status"] == "create" else []),
        "add": {CONFIG_RELATIVE: config_plan.get("add", [])},
        "preserve": ["workspace/ existing data", "docs/", CONFIG_RELATIVE, "existing agent settings", "general source files"],
        "project_config": config_plan,
        "runtime_config": runtime_config_plan,
        "checks": {"python": f"{sys.version_info.major}.{sys.version_info.minor}", "missing": missing},
        "status": "failed" if missing or runtime_config_plan.get("status") == "warning" else "ready",
    }
    if runtime_config_plan.get("status") == "warning":
        missing.append("runtime config migration validation")
    if missing:
        if cli.json:
            print(json.dumps(plan, ensure_ascii=False))
        else:
            print("오류: 설치 dry-run 실패: " + ", ".join(missing))
        return 1

    # 4. 최종 확인
    mode = "업그레이드" if upgrade else "신규 설치"
    print(f"\n─────────────────────────────")
    print(f"  모드    : {mode}")
    print(f"  경로    : {project_path}")
    print(f"  agents  : {', '.join(agents)}")
    print(f"  변경    : .mpa-workspace/, workspace/ 초기 골격, 빈 docs/, {CONFIG_RELATIVE} 보강, 선택 agent 진입 설정")
    print(f"─────────────────────────────")

    if cli.dry_run:
        if cli.json:
            print(json.dumps(plan, ensure_ascii=False))
        else:
            print("\n설치 dry-run 통과: 파일을 변경하지 않았습니다.")
        return 0

    if not project_path.exists():
        project_path.mkdir(parents=True)
        print("  [생성] project root/")

    if not cli.project and not ask_yes_no("\n진행할까요?", default=True):
        print("취소되었습니다.")
        return 0

    run_install(project_path, agents, upgrade, runtime_config)

    print(f"\n=== my-pacemaker-agent {mode} 완료 ===\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
