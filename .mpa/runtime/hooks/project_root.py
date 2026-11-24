"""Resolve the executing Runtime's owner separately from the tool's working directory."""

import os
from pathlib import Path


class ProjectRootError(ValueError):
    pass


def project_root(script):
    """The physical hook location owns state; cwd/env must not select another project."""
    try:
        path = Path(script).resolve(strict=True)
        hooks = path.parent
        if (hooks.name == "hooks" and hooks.parent.name == "runtime"
                and hooks.parent.parent.name == ".mpa"
                and (hooks.parent / "core/agent_rules.md").is_file()):
            return str(hooks.parent.parent.parent)
    except (OSError, RuntimeError, ValueError):
        pass
    raise ProjectRootError("MPA Runtime 소유 프로젝트를 확인할 수 없습니다. critical 승인 검사는 미확인입니다.")


def execution_cwd(value=None):
    try:
        if value is not None and (not isinstance(value, str) or not value.strip()):
            raise ValueError("invalid cwd")
        return str(Path(value or os.getcwd()).resolve())
    except (OSError, RuntimeError, ValueError) as error:
        raise ProjectRootError("hook 실행 작업 폴더를 확인할 수 없습니다.") from error


def relative_path(path, root, cwd=None):
    """Interpret relative tool paths at execution cwd, then compare to the Runtime owner."""
    if not path:
        return None
    try:
        target = Path(path)
        if not target.is_absolute():
            target = Path(execution_cwd(cwd)) / target
        return os.path.relpath(str(target.resolve()), root)
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        raise ProjectRootError("hook 대상 파일의 경로를 확인할 수 없습니다.") from error
