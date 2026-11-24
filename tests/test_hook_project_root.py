"""Exercise installed hooks and generated shell commands in real temporary projects."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

import install


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / ".mpa/runtime"


class HookProjectRootTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name) / "project space"
        self.runtime = self.root / ".mpa/runtime"
        shutil.copytree(RUNTIME, self.runtime, ignore=shutil.ignore_patterns("__pycache__"))
        self.nested = self.root / "workspace/tasks"
        self.nested.mkdir(parents=True)

    def run_hook(self, script="code_gate.py", data=None, mode="block", cwd=None,
                 agent="codex", generated=False, env=None, runtime=None):
        environment = {**os.environ, "MPA_GATE": mode, "CLAUDE_PROJECT_DIR": str(self.root)}
        environment.update(env or {})
        command = (install._hook_cmd(script, agent) if generated else
                   ["python3", str((runtime or self.runtime) / "hooks" / script), "--agent", agent])
        return subprocess.run(command, shell=generated, cwd=cwd or self.root,
                              input=json.dumps(data or {}), text=True, capture_output=True,
                              env=environment)

    def request(self, path, cwd=None, tool="Edit"):
        return {"cwd": str(cwd or self.root), "tool_name": tool,
                "tool_input": {"file_path": str(path)}}

    def active_plan(self, status="설계 완료", critical=True):
        plan = self.nested / "active/example/plan.md"
        plan.parent.mkdir(parents=True, exist_ok=True)
        plan.write_text(
            "---\n태스크: example\n생성일: 2026-11-24\n타입: major\n"
            f"실패비용: {'critical' if critical else 'major'}\n상태: 설계 완료\n"
            '승인해시: ""\n승인대상: 요구사항 명세\n---\n'
            "## 요구사항 명세\n목적: 결과를 만든다.\n## 실행 계획\n구현한다.\n",
            encoding="utf-8")
        if status == "구현 중":
            result = subprocess.run(["python3", str(self.runtime / "hooks/plan_hash.py"),
                                     "approve", str(plan)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
        elif status != "설계 완료":
            plan.write_text(plan.read_text().replace("상태: 설계 완료", "상태: " + status))
        (self.nested / "CURRENT_TASK").write_text("example\n")
        return plan

    def test_workspace_and_source_decisions_at_root_and_nested_cwd(self):
        for mode in ("warn", "block", "off"):
            for path in (self.nested / "INDEX.md", self.root / "src.py"):
                results = [self.run_hook(data=self.request(path, cwd), mode=mode, cwd=cwd)
                           for cwd in (self.root, self.nested)]
                self.assertEqual([(r.returncode, r.stdout, r.stderr) for r in results][0],
                                 [(r.returncode, r.stdout, r.stderr) for r in results][1])
                expected = 2 if mode == "block" and path.name == "src.py" else 0
                self.assertEqual(results[0].returncode, expected)

    def test_generated_commands_preserve_relative_file_when_json_cwd_missing(self):
        for agent in ("claude", "codex"):
            # At workspace/tasks, "workspace/file" is allowed, "../../src.py" is source.
            for relative, absolute, expected in (
                    ("workspace/file", self.nested / "workspace/file", 0),
                    ("../../src.py", self.root / "src.py", 2)):
                data = {"tool_name": "Edit", "tool_input": {"file_path": relative}}
                actual = self.run_hook(data=data, cwd=self.nested, agent=agent, generated=True)
                reference = self.run_hook(data=self.request(absolute), agent=agent)
                self.assertEqual(actual.returncode, expected, actual.stderr)
                self.assertEqual((actual.returncode, actual.stdout, actual.stderr),
                                 (reference.returncode, reference.stdout, reference.stderr))

    def test_relative_source_named_workspace_does_not_bypass_gate(self):
        sub = self.root / "src/sub"
        sub.mkdir(parents=True)
        result = self.run_hook(data=self.request("workspace/file", sub), cwd=sub)
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertIn("src/sub/workspace/file", result.stderr)

    def test_foreign_cwd_and_env_do_not_choose_foreign_state(self):
        foreign = Path(self.directory.name) / "foreign"
        foreign.mkdir()
        result = self.run_hook(data=self.request(self.root / "src.py", foreign), cwd=foreign,
                               env={"CLAUDE_PROJECT_DIR": str(foreign)})
        self.assertEqual(result.returncode, 2)
        self.assertIn("active 태스크가 없습니다", result.stderr)

    def test_selected_critical_hash_is_checked_from_nested_directory(self):
        plan = self.active_plan("구현 중")
        for cwd in (self.root, self.nested):
            result = self.run_hook(data=self.request(self.root / "src.py", cwd), mode="warn", cwd=cwd)
            self.assertEqual(result.returncode, 0, result.stderr)
        plan.write_text(plan.read_text().replace("목적: 결과", "목적: 변경된 결과"))
        for mode in ("warn", "block"):
            result = self.run_hook(data=self.request(self.root / "src.py", self.nested),
                                   mode=mode, cwd=self.nested)
            self.assertEqual(result.returncode, 2)
            self.assertIn("승인", result.stderr)
        self.assertEqual(self.run_hook(data=self.request(self.root / "src.py"), mode="off").returncode, 0)

    def test_unapproved_critical_still_blocks_external_source_request(self):
        self.active_plan()
        outside = Path(self.directory.name) / "workspace/file.py"
        result = self.run_hook(data=self.request(outside, self.nested), mode="warn", cwd=self.nested)
        self.assertEqual(result.returncode, 2)
        self.assertIn("critical", result.stderr)

    def test_symlink_escape_does_not_match_workspace_prefix(self):
        foreign = Path(self.directory.name) / "foreign"
        foreign.mkdir()
        (self.root / "workspace/link").symlink_to(foreign, target_is_directory=True)
        result = self.run_hook(data=self.request(self.root / "workspace/link/file.py"))
        self.assertEqual(result.returncode, 2)

    def test_symlinked_hook_uses_physical_runtime_owner(self):
        link = Path(self.directory.name) / "alias.py"
        link.symlink_to(self.runtime / "hooks/code_gate.py")
        # Python's script import path follows the script's physical location.
        result = subprocess.run(["python3", str(link)], input=json.dumps(self.request(self.root / "src.py")),
                                text=True, capture_output=True, env={**os.environ, "MPA_GATE": "block"})
        self.assertEqual(result.returncode, 2)
        self.assertIn("active 태스크가 없습니다", result.stderr)

    def test_start_and_stop_use_same_state_with_nested_or_foreign_input(self):
        self.active_plan()
        for script in ("session_start.py", "turn_end.py"):
            results = [self.run_hook(script, data={"cwd": str(cwd)}, cwd=self.nested)
                       for cwd in (self.root, self.nested, Path(self.directory.name))]
            self.assertEqual(len({(r.returncode, r.stdout, r.stderr) for r in results}), 1)
            self.assertIn("진행 중", results[0].stdout + results[0].stderr)
            self.assertEqual(results[0].returncode, 0)

    def test_generated_commands_work_in_nested_git_and_non_git_projects(self):
        inner = self.nested / "inner repo"
        inner.mkdir()
        for repository in (self.root, inner):
            subprocess.run(["git", "init", "-q", str(repository)], check=True, capture_output=True)
        self.active_plan()
        for agent in ("claude", "codex"):
            for cwd in (self.nested, inner):
                for script in ("session_start.py", "turn_end.py"):
                    result = self.run_hook(script, data={"cwd": str(cwd)}, cwd=cwd,
                                           agent=agent, generated=True,
                                           env={"CLAUDE_PROJECT_DIR": "/nonexistent"})
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn("진행 중", result.stdout + result.stderr)

    def test_unknown_runtime_root_modes_and_nonblocking_session_hooks(self):
        broken = Path(self.directory.name) / "broken"
        shutil.copytree(self.runtime / "hooks", broken / "hooks", ignore=shutil.ignore_patterns("__pycache__"))
        for mode, expected in (("warn", 0), ("block", 2), ("off", 0)):
            result = self.run_hook(data=self.request("src.py"), runtime=broken, mode=mode)
            self.assertEqual(result.returncode, expected)
            if mode != "off":
                self.assertIn("미확인", result.stdout + result.stderr)
        for script in ("session_start.py", "turn_end.py"):
            result = self.run_hook(script, runtime=broken)
            self.assertEqual(result.returncode, 0)
            self.assertIn("소유 프로젝트", result.stderr)

    def test_generated_wrapper_missing_runtime_respects_gate_and_session_modes(self):
        for agent in ("claude", "codex"):
            for script in ("code_gate.py", "session_start.py", "turn_end.py"):
                for mode in ("warn", "block", "off", " OFF ", " BLOCK "):
                    with self.subTest(agent=agent, script=script, mode=mode):
                        result = self.run_hook(script, cwd=Path(self.directory.name), generated=True,
                                               agent=agent, mode=mode)
                        expected = 2 if script == "code_gate.py" and mode.strip().lower() == "block" else 0
                        self.assertEqual(result.returncode, expected, result.stderr)
                        if script == "code_gate.py" and mode.strip().lower() == "off":
                            self.assertEqual(result.stdout + result.stderr, "")
                        else:
                            self.assertIn("미확인", result.stdout + result.stderr)

    def test_done_write_warning_uses_owner_root(self):
        self.active_plan()
        request = self.request("done/example/plan.md", self.nested)
        result = self.run_hook(data=request, cwd=self.nested)
        self.assertEqual(result.returncode, 0)
        self.assertIn("완료 절차 확인", result.stdout)

    def test_generated_wrapper_missing_script_is_also_nonblocking_except_strict_gate(self):
        for script in ("code_gate.py", "session_start.py", "turn_end.py"):
            (self.runtime / "hooks" / script).unlink()
            for mode in ("warn", "block", "off"):
                result = self.run_hook(script, generated=True, mode=mode)
                expected = 2 if script == "code_gate.py" and mode == "block" else 0
                self.assertEqual(result.returncode, expected, result.stderr)

    def test_relative_and_quoted_mv_checks_owner_task_state(self):
        plan = self.active_plan()
        for mode, expected in (("warn", 0), ("block", 2), ("off", 0)):
            for command in ('mv "active/example" "done/"',
                            f'mv "{plan.parent}" "{self.nested}/done/"'):
                data = {"cwd": str(self.nested), "tool_name": "Bash", "tool_input": {"command": command}}
                result = self.run_hook(data=data, cwd=self.nested, mode=mode)
                self.assertEqual(result.returncode, expected, result.stderr)
                if mode != "off":
                    self.assertIn("완료 처리 차단", result.stdout + result.stderr)
        plan.write_text(plan.read_text().replace("상태: 설계 완료", "상태: 완료 승인"))
        result = self.run_hook(data={"cwd": str(self.nested), "tool_name": "Bash",
                                    "tool_input": {"command": "mv active/example done/"}}, cwd=self.nested)
        self.assertEqual(result.returncode, 0, result.stderr)



    def test_direct_mv_guard_in_generated_hooks(self):
        self.active_plan()
        for agent in ("claude", "codex"):
            for cwd, command in (
                (self.root, "mv workspace/tasks/active/example workspace/tasks/done/"),
                (self.nested, "mv -n active/example done/"),
                (self.nested, "true; mv active/example done/"),
                (self.nested, "true && mv active/example done/"),
                (self.nested, "false || mv active/example done/"),
                (self.nested, "mv active/example done/ # comment"),
                (self.nested, "mv active/example done/ >/dev/null"),
            ):
                for mode, expected in (("warn", 0), ("block", 2), ("off", 0)):
                    with self.subTest(agent=agent, cwd=cwd, mode=mode):
                        data = {"tool_name": "Bash", "tool_input": {"command": command}}
                        result = self.run_hook(data=data, cwd=cwd, mode=mode, agent=agent, generated=True)
                        self.assertEqual(result.returncode, expected, result.stderr)
                        if mode == "off":
                            self.assertEqual(result.stdout + result.stderr, "")
                        else:
                            self.assertIn("완료 처리 차단", result.stdout + result.stderr)
        for command in ("mv active/example hold/", "  # note; mv active/example done/"):
            with self.subTest(command=command):
                data = {"tool_name": "Bash", "tool_input": {"command": command}}
                result = self.run_hook(data=data, cwd=self.nested, mode="block")
                self.assertEqual((result.returncode, result.stdout, result.stderr), (0, "", ""))


if __name__ == "__main__":
    unittest.main()
