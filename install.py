#!/usr/bin/env python3
"""
Agents Workspace 설치 스크립트
사용법: install.md 참조
"""

import shutil
import sys
import uuid
from pathlib import Path
from typing import Optional

HARNESS_ROOT = Path(__file__).parent
AGENTS_WORKSPACE_SRC = HARNESS_ROOT / ".agents-workspace"
WORKSPACE_TEMPLATE_SRC = HARNESS_ROOT / "workspace-template"
AGENT_CONFIGS_SRC = HARNESS_ROOT / "agent-configs"

AGENT_CONFIG_MAP = {
    "claude": "CLAUDE.md",
    "codex": "AGENTS.md",
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
    """agent-configs 파일에서 설치 안내 주석 블록을 제거하고 실제 내용만 반환"""
    config_file = AGENT_CONFIGS_SRC / AGENT_CONFIG_MAP[agent]
    if not config_file.exists():
        return None

    lines = config_file.read_text(encoding="utf-8").splitlines()

    # 첫 번째 ## 섹션부터 시작 (설치 안내 주석 블록 건너뜀)
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


def copy_agents_workspace(dst: Path):
    shutil.copytree(AGENTS_WORKSPACE_SRC, dst)
    print(f"  [복사] .agents-workspace/ → {dst}")


def copy_workspace_template(dst: Path):
    added = _merge_dir(WORKSPACE_TEMPLATE_SRC, dst, dst)
    if added == 0:
        print("  [확인] workspace/ 추가할 항목 없음")


def _merge_dir(src: Path, dst: Path, base: Path):
    """src 구조를 dst에 병합한다. 없는 항목만 추가하고 기존 항목은 건드리지 않는다."""
    dst.mkdir(parents=True, exist_ok=True)
    added = 0
    for item in src.iterdir():
        dst_item = dst / item.name
        if dst_item.exists():
            if item.is_dir():
                added += _merge_dir(item, dst_item, base)
        else:
            if item.is_dir():
                shutil.copytree(item, dst_item)
            else:
                shutil.copy2(item, dst_item)
            print(f"  [추가] workspace/{dst_item.relative_to(base)}")
            added += 1
    return added


def append_agent_config(agent: str, project_path: Path):
    filename = AGENT_CONFIG_MAP[agent]
    config_dst = project_path / filename
    content = read_config_content(agent)

    if content is None:
        print(f"  [경고] agent-configs/{filename} 없음, 건너뜀")
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


def run_install(project_path: Path, agents: list, upgrade: bool):
    agents_workspace_dst = project_path / ".agents-workspace"
    workspace_dst = project_path / "workspace"

    if upgrade:
        print("\n[1단계] upgrade-candidates 이동")
        migrate_upgrade_candidates(agents_workspace_dst)

        print("\n[2단계] .agents-workspace 교체")
        shutil.rmtree(agents_workspace_dst)
        copy_agents_workspace(agents_workspace_dst)
        clear_upgrade_candidates(agents_workspace_dst)

        print("\n[3단계] workspace 누락 항목 추가 (하네스 신규 구조 반영)")
        copy_workspace_template(workspace_dst)
    else:
        print("\n[1단계] .agents-workspace 설치")
        copy_agents_workspace(agents_workspace_dst)
        clear_upgrade_candidates(agents_workspace_dst)

        print("\n[2단계] workspace 초기화")
        copy_workspace_template(workspace_dst)

    print("\n[마지막] agent 설정 파일 업데이트")
    for agent in agents:
        append_agent_config(agent, project_path)


# ──────────────────────────────────────────────
# 대화형 입력
# ──────────────────────────────────────────────

def detect_agents(project_path: Path) -> list:
    """프로젝트 경로에서 사용 중인 agent를 감지한다"""
    detected = []
    if (project_path / "CLAUDE.md").exists() or (project_path / ".claude").exists():
        detected.append("claude")
    if (project_path / "AGENTS.md").exists():
        detected.append("codex")
    return detected


def prompt_agents(project_path: Path) -> list:
    detected = detect_agents(project_path)

    print("\n사용 중인 agent:")
    for i, (key, filename) in enumerate(AGENT_CONFIG_MAP.items(), 1):
        mark = "✓" if key in detected else " "
        print(f"  [{mark}] {i}. {key} ({filename})")

    print("\n설정할 agent를 입력하세요.")
    print("  예) claude / codex / claude,codex")

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


def main():
    print("=== my-pace-agent 설치 ===")

    # 1. 프로젝트 경로
    project_path = prompt_project_path()

    # 2. 신규 설치 vs 업그레이드 자동 판단
    agents_workspace_dst = project_path / ".agents-workspace"
    upgrade = agents_workspace_dst.exists()

    if upgrade:
        print(f"\n.agents-workspace/ 가 이미 존재합니다 → 업그레이드 모드")
    else:
        print(f"\n.agents-workspace/ 없음 → 신규 설치 모드")

    # 3. agent 선택
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

    if not ask_yes_no("\n진행할까요?", default=True):
        print("취소되었습니다.")
        return 0

    run_install(project_path, agents, upgrade)

    print(f"\n=== my-pace-agent {mode} 완료 ===\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
