#!/usr/bin/env python3
"""
Agents Workspace 설치 스크립트
사용법: install.md 참조
"""

import argparse
import datetime
import shutil
import sys
import uuid
from pathlib import Path
from typing import Optional

HARNESS_ROOT = Path(__file__).parent
DIST_ROOT = HARNESS_ROOT / "dist"
AGENTS_WORKSPACE_SRC = DIST_ROOT / ".mpa-workspace"
WORKSPACE_TEMPLATE_SRC = DIST_ROOT / "workspace"
AGENT_SPECS_SRC = HARNESS_ROOT / "agent-specs"
AGENT_CONFIGS_SRC = HARNESS_ROOT / "agent-configs"  # 레거시 fallback

AGENT_CONFIG_MAP = {
    "claude":       "CLAUDE.md",
    "codex":        "AGENTS.md",
    "antigravity":  "GEMINI.md",
    "openagent":    None,   # spec.md 질의로 결정 — 파일 주입은 AI agent가 처리
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

def migrate_upgrade_candidates(agents_workspace_dst: Path) -> int:
    """프로젝트의 upgrade-candidates 파일을 harness로 이동한다.
    동일 파일명이 이미 존재하면 UUID suffix를 붙여 보존한다.
    반환값: 이동된 파일 수
    """
    candidates_src = agents_workspace_dst / "upgrade-candidates"
    candidates_dst = AGENTS_WORKSPACE_SRC / "upgrade-candidates"

    if not candidates_src.exists():
        print("  [확인] upgrade-candidates/ 폴더 없음, 건너뜀")
        return 0

    candidates_dst.mkdir(parents=True, exist_ok=True)

    moved = 0
    for f in sorted(candidates_src.iterdir()):
        if f.name == ".gitkeep":
            continue

        dest = candidates_dst / f.name
        if dest.exists():
            uid = uuid.uuid4().hex[:8]
            dest = candidates_dst / f"{f.stem}_{uid}{f.suffix}"
            print(f"  [이동] {f.name} → harness/upgrade-candidates/{dest.name} (충돌 해결)")
        else:
            print(f"  [이동] {f.name} → harness/upgrade-candidates/")

        shutil.move(str(f), dest)
        moved += 1

    if moved == 0:
        print("  [확인] upgrade-candidates/ 이동할 파일 없음")

    return moved


def clear_upgrade_candidates(agents_workspace_dst: Path):
    """복사된 upgrade-candidates/ 를 비운다 (.gitkeep 유지)"""
    candidates = agents_workspace_dst / "upgrade-candidates"
    if not candidates.exists():
        return
    for f in candidates.iterdir():
        if f.name == ".gitkeep":
            continue
        f.unlink() if f.is_file() else shutil.rmtree(f)
    print("  [초기화] upgrade-candidates/ 비움")


_IGNORE = shutil.ignore_patterns(".DS_Store", ".gitkeep")


def write_version(agents_workspace_dst: Path, mode: str):
    """설치/업그레이드 날짜를 .mpa-version에 기록한다."""
    version_src = agents_workspace_dst / ".mpa-version"
    if not version_src.exists():
        return
    harness_date = ""
    for line in version_src.read_text(encoding="utf-8").splitlines():
        if line.startswith("harness_date:"):
            harness_date = line
            break
    today = datetime.date.today().isoformat()
    version_src.write_text(
        f"{harness_date}\n{mode}_at: {today}\n",
        encoding="utf-8"
    )


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
            print(f"  [건너뜀] {filename} — Agents Workspace 섹션 이미 존재")
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


def copy_workspace_template(dst: Path, upgrade: bool = False):
    added = _merge_dir(WORKSPACE_TEMPLATE_SRC, dst, dst, label="workspace", upgrade=upgrade)
    if added == 0:
        print("  [확인] workspace/ 추가할 항목 없음")


def run_install(project_path: Path, agents: list, upgrade: bool):
    agents_workspace_dst = project_path / ".mpa-workspace"
    workspace_dst = project_path / "workspace"

    if upgrade:
        print("\n[1단계] upgrade-candidates 이동")
        migrate_upgrade_candidates(agents_workspace_dst)

        print("\n[2단계] .mpa-workspace 교체")
        shutil.rmtree(agents_workspace_dst)
        copy_agents_workspace(agents_workspace_dst)
        clear_upgrade_candidates(agents_workspace_dst)
        write_version(agents_workspace_dst, "upgraded")

        print("\n[3단계] workspace 템플릿 업데이트 및 누락 항목 추가")
        copy_workspace_template(workspace_dst, upgrade=True)
    else:
        print("\n[1단계] .mpa-workspace 설치")
        copy_agents_workspace(agents_workspace_dst)
        clear_upgrade_candidates(agents_workspace_dst)
        write_version(agents_workspace_dst, "installed")

        print("\n[2단계] workspace 초기화")
        copy_workspace_template(workspace_dst)

    print("\n[마지막] agent 설정 적용")
    for agent in agents:
        print(f"\n  ── {agent} ──")
        append_agent_config(agent, project_path)
        copy_agent_spec_files(agent, project_path)


# ──────────────────────────────────────────────
# 대화형 입력
# ──────────────────────────────────────────────

def detect_agents(project_path: Path) -> list:
    """프로젝트 경로에서 사용 중인 agent를 감지한다."""
    detected = []
    if (project_path / "CLAUDE.md").exists() or (project_path / ".claude").exists():
        detected.append("claude")
    if (project_path / "AGENTS.md").exists():
        detected.append("codex")
    if (project_path / "GEMINI.md").exists() or (project_path / ".gemini").exists():
        detected.append("antigravity")
    return detected


def prompt_agents(project_path: Path) -> list:
    detected = detect_agents(project_path)

    print("\n사용 중인 agent:")
    for i, (key, filename) in enumerate(AGENT_CONFIG_MAP.items(), 1):
        mark = "✓" if key in detected else " "
        label = filename if filename else "spec.md 질의"
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
    parser.add_argument("--agents", help="사용 중인 agent (claude, codex, antigravity, openagent 또는 조합)")
    parser.add_argument("--upgrade", action="store_true", help="업그레이드 모드로 실행")
    return parser.parse_args()


def main():
    print("=== my-pacemaker-agent 설치 ===")

    cli = parse_args()

    # 1. 프로젝트 경로
    if cli.project:
        project_path = Path(cli.project).resolve()
        if not project_path.exists():
            print(f"오류: 경로가 존재하지 않습니다: {project_path}")
            return 1
        print(f"\n프로젝트 경로: {project_path}")
    else:
        project_path = prompt_project_path()

    # 2. 신규 설치 vs 업그레이드 자동 판단
    agents_workspace_dst = project_path / ".mpa-workspace"
    upgrade = cli.upgrade or agents_workspace_dst.exists()

    if upgrade:
        print(f"\n.mpa-workspace/ 가 이미 존재합니다 → 업그레이드 모드")
    else:
        print(f"\n.mpa-workspace/ 없음 → 신규 설치 모드")

    # 3. agent 선택
    if cli.agents:
        agents = [a.strip().lower() for a in cli.agents.split(",") if a.strip()]
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

    # 4. 최종 확인
    mode = "업그레이드" if upgrade else "신규 설치"
    print(f"\n─────────────────────────────")
    print(f"  모드    : {mode}")
    print(f"  경로    : {project_path}")
    print(f"  agents  : {', '.join(agents)}")
    print(f"─────────────────────────────")

    if not cli.project and not ask_yes_no("\n진행할까요?", default=True):
        print("취소되었습니다.")
        return 0

    run_install(project_path, agents, upgrade)

    print(f"\n=== my-pacemaker-agent {mode} 완료 ===\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
