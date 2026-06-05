#!/usr/bin/env python3
"""
dist_sync.py — .mpa-workspace/ 수정 시 dist/ 자동 동기화 (PostToolUse)

Edit/Write 도구로 .mpa-workspace/ 파일이 저장되면 즉시 dist/.mpa-workspace/ 에 복사한다.
성공은 조용히 처리 (Zone 3). 실패 시에만 stderr 경고.
"""

import json
import os
import shutil
import sys


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        sys.exit(0)

    cwd = (data.get("cwd") or os.getcwd())
    tool_input = (data.get("tool_input") or data.get("toolInput") or
                  data.get("input") or {})
    if not isinstance(tool_input, dict):
        sys.exit(0)

    file_path = (tool_input.get("file_path") or tool_input.get("path") or
                 tool_input.get("filePath") or "")
    if not file_path:
        sys.exit(0)

    if not os.path.isabs(file_path):
        file_path = os.path.join(cwd, file_path)
    file_path = os.path.normpath(file_path)

    mpa_src = os.path.normpath(os.path.join(cwd, ".mpa-workspace"))
    if not file_path.startswith(mpa_src + os.sep):
        sys.exit(0)

    # 프로젝트 로컬 피드백 폴더는 dist/ 배포본에 포함하지 않는다
    SYNC_EXCLUDE = ("upgrade-candidates" + os.sep,)
    rel_from_mpa = os.path.relpath(file_path, mpa_src)
    if any(rel_from_mpa.startswith(ex) for ex in SYNC_EXCLUDE):
        sys.exit(0)

    # dist/ 대상 경로 계산
    rel = os.path.relpath(file_path, cwd)
    dist_path = os.path.normpath(os.path.join(cwd, "dist", rel))

    if not os.path.exists(file_path):
        sys.exit(0)  # 삭제된 파일은 동기화하지 않는다

    dist_dir = os.path.normpath(os.path.join(cwd, "dist"))
    if not os.path.isdir(dist_dir):
        sys.exit(0)  # dist/ 없는 환경(target projects)에서는 동작하지 않는다

    try:
        os.makedirs(os.path.dirname(dist_path), exist_ok=True)
        shutil.copy2(file_path, dist_path)
    except Exception as e:
        sys.stderr.write(f"⚠️ dist/ 동기화 실패: {rel} → {e}\n")

    sys.exit(0)


if __name__ == "__main__":
    main()
