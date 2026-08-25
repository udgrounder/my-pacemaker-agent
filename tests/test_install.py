import subprocess
import tempfile
import unittest
import json
import importlib.util
import os
from pathlib import Path

import project_config


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("install", ROOT / "install.py")
install = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(install)


class InstallDryRunTest(unittest.TestCase):
    def test_dry_run_checks_templates_without_writing_target(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            result = subprocess.run(
                ["python3", "install.py", "--project", str(target), "--agents", "codex", "--dry-run"],
                cwd=ROOT, text=True, capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("설치 dry-run 통과", result.stdout)
            self.assertFalse((target / ".mpa/runtime").exists())

    def test_new_install_creates_root_docs_but_not_workspace_docs(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            result = subprocess.run(
                ["python3", "install.py", "--project", str(target), "--agents", "codex"],
                cwd=ROOT, text=True, capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse((target / "workspace" / "docs").exists())
            self.assertTrue((target / "docs").is_dir())
            self.assertTrue((target / "docs" / "INDEX.md").is_file())
            config = (target / ".mpa/config" / "config.yaml").read_text(encoding="utf-8")
            self.assertIn("schema_version: 1", config)
            self.assertIn('name: "' + target.name + '"', config)
            self.assertIn('root_path: "' + str(target.resolve()) + '"', config)

    def test_new_install_applies_runtime_config_defaults_and_project_references(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "runtime-project"
            migration = Path(directory) / "runtime-config.json"
            migration.write_text(json.dumps({"schema_version": 2, "additive_defaults": {
                "runtime.project_name": "${project.name}",
                "runtime.root_path": "${project.root_path}",
                "runtime.enabled": True,
            }}), encoding="utf-8")
            result = subprocess.run(
                ["python3", "install.py", "--project", str(target), "--agents", "codex",
                 "--runtime-config-json", str(migration)],
                cwd=ROOT, text=True, capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            config = (target / ".mpa/config" / "config.yaml").read_text(encoding="utf-8")
            self.assertIn(f'project_name: "{target.name}"', config)
            self.assertIn(f'root_path: "{target.resolve()}"', config)
            self.assertIn("enabled: true", config)

    def test_new_install_creates_missing_explicit_project_root(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "new-project"
            dry_run = subprocess.run(
                ["python3", "install.py", "--project", str(target), "--agents", "codex", "--dry-run", "--json"],
                cwd=ROOT, text=True, capture_output=True,
            )
            self.assertEqual(dry_run.returncode, 0, dry_run.stderr)
            self.assertFalse(target.exists())
            self.assertIn("project root/", json.loads(dry_run.stdout.strip().splitlines()[-1])["create"])
            result = subprocess.run(["python3", "install.py", "--project", str(target), "--agents", "codex"],
                                    cwd=ROOT, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((target / "workspace" / "issues").is_dir())

    def test_dry_run_json_describes_changes_and_preserves_target(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            marker = target / "keep.txt"
            marker.write_text("user data", encoding="utf-8")
            result = subprocess.run(
                ["python3", "install.py", "--project", str(target), "--agents", "codex", "--dry-run", "--json"],
                cwd=ROOT, text=True, capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            plan = json.loads(result.stdout.strip().splitlines()[-1])
            self.assertEqual(plan["status"], "ready")
            self.assertEqual(plan["target"], str(target.resolve()))
            self.assertIn("docs/", plan["preserve"])
            self.assertEqual(marker.read_text(encoding="utf-8"), "user data")

    def test_removed_installation_refresh_cli_is_not_available(self):
        result = subprocess.run(
            ["python3", "install.py", "--installation-refresh", "--plan", "refresh.json"],
            cwd=ROOT, text=True, capture_output=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unrecognized arguments", result.stderr)

    def test_existing_project_config_only_adds_missing_fields_and_preserves_content(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "configured-project"
            target.mkdir()
            config = target / ".mpa/config" / "config.yaml"
            config.parent.mkdir(parents=True)
            original = (
                "# operator-owned\n"
                "schema_version: 1\n"
                "project:\n"
                "  name: \"custom-name\"\n"
                "  owner_defined: \"keep-me\"\n"
            )
            config.write_text(original, encoding="utf-8")

            result = project_config.ensure_project_config(target)

            updated = config.read_text(encoding="utf-8")
            self.assertEqual(result["status"], "updated")
            self.assertIn(original, updated)
            self.assertIn('name: "custom-name"', updated)
            self.assertIn('owner_defined: "keep-me"', updated)
            self.assertIn("root_path:", updated)
            self.assertIn("initialized_at:", updated)
            self.assertNotIn("custom-name", result.get("warnings", []))

    def test_missing_schema_is_added_but_future_schema_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            config = target / ".mpa/config" / "config.yaml"
            config.parent.mkdir(parents=True)
            config.write_text("project:\n  name: \"legacy\"\n", encoding="utf-8")
            result = project_config.ensure_project_config(target)
            self.assertEqual(result["status"], "updated")
            self.assertTrue(config.read_text(encoding="utf-8").startswith("schema_version: 1\n"))

            future = "schema_version: 99\nproject:\n  name: \"future\"\n"
            config.write_text(future, encoding="utf-8")
            result = project_config.ensure_project_config(target)
            self.assertEqual(result["status"], "warning")
            self.assertEqual(config.read_text(encoding="utf-8"), future)

    def test_invalid_schema_is_preserved_without_duplicate_schema_key(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            config = target / ".mpa/config" / "config.yaml"
            config.parent.mkdir(parents=True)
            invalid = "schema_version: latest\nproject:\n  name: \"owned\"\n"
            config.write_text(invalid, encoding="utf-8")

            result = project_config.ensure_project_config(target)

            self.assertEqual(result["status"], "warning")
            self.assertEqual(config.read_text(encoding="utf-8"), invalid)
            self.assertEqual(config.read_text(encoding="utf-8").count("schema_version:"), 1)

    def test_config_audit_warns_on_moved_root_without_exposing_absolute_path(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            config = target / ".mpa/config" / "config.yaml"
            config.parent.mkdir(parents=True)
            config.write_text(
                "schema_version: 1\nproject:\n"
                "  name: \"project\"\n"
                "  root_path: \"/old/private/project\"\n"
                "  initialized_at: \"2026-08-13T00:00:00Z\"\n",
                encoding="utf-8",
            )
            result = project_config.audit_project_config(target)
            rendered = json.dumps(result, ensure_ascii=False)
            self.assertIn("differs from configured root_path", rendered)
            self.assertNotIn("/old/private/project", rendered)

    def test_config_symlink_is_warning_instead_of_internal_error(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "target"
            target.mkdir()
            external = Path(directory) / "external.yaml"
            external.write_text("schema_version: 1\nproject: {}\n", encoding="utf-8")
            config = target / ".mpa/config/config.yaml"
            config.parent.mkdir(parents=True)
            os.symlink(external, config)

            result = project_config.inspect_project_config(target)

            self.assertEqual(result["status"], "warning")
            self.assertIn("unsupported symlink", result["warnings"][0])
            audit = project_config.audit_project_config(target)
            self.assertEqual(audit["status"], "warning")
            self.assertNotIn("semantic_checksum", audit)

    def test_config_parent_symlink_is_warning_without_reading_external_config(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "target"
            target.mkdir()
            external = Path(directory) / "external-config"
            external.mkdir()
            (external / "config.yaml").write_text("schema_version: 1\nproject: {}\n", encoding="utf-8")
            (target / ".mpa").mkdir()
            os.symlink(external, target / ".mpa/config")

            result = project_config.inspect_project_config(target)
            audit = project_config.audit_project_config(target)

            self.assertEqual(result["status"], "warning")
            self.assertIn("unsupported symlink", result["warnings"][0])
            self.assertEqual(audit["status"], "warning")
            self.assertNotIn("semantic_checksum", audit)

    def test_existing_install_rejection_preserves_workspace_docs_and_agent_settings(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            (target / ".mpa/runtime").mkdir(parents=True)
            (target / "workspace").mkdir()
            (target / "docs").mkdir()
            (target / "AGENTS.md").write_text("agent config", encoding="utf-8")
            (target / "workspace" / "keep.txt").write_text("workspace", encoding="utf-8")
            (target / "docs" / "keep.md").write_text("docs", encoding="utf-8")
            result = subprocess.run(
                ["python3", "install.py", "--project", str(target), "--agents", "codex", "--dry-run"],
                cwd=ROOT, text=True, capture_output=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("release_manager.py deploy", result.stdout)
            self.assertEqual((target / "AGENTS.md").read_text(encoding="utf-8"), "agent config")
            self.assertEqual((target / "workspace" / "keep.txt").read_text(encoding="utf-8"), "workspace")
            self.assertEqual((target / "docs" / "keep.md").read_text(encoding="utf-8"), "docs")

    def test_openagent_install_discloses_manual_wiring(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            result = subprocess.run(
                ["python3", "install.py", "--project", str(target), "--agents", "openagent"],
                cwd=ROOT, text=True, capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("실험적·수동 설정 지원", result.stdout)
            self.assertIn("자동 진입점·규칙 파일·hook 연결은 수행하지 않습니다", result.stdout)
            self.assertFalse((target / "OPENAGENT.md").exists())

    def test_clean_install_wires_native_agent_files_to_current_runtime(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            result = subprocess.run(
                ["python3", "install.py", "--project", str(target),
                 "--agents", "claude,codex,antigravity"],
                cwd=ROOT, text=True, capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            for path in (
                target / "CLAUDE.md",
                target / "AGENTS.md",
                target / "GEMINI.md",
                target / ".claude/agents/mpa_pacemaker.md",
                target / ".codex/agents/mpa_pacemaker.toml",
                target / ".agents/rules/mpa_pacemaker.md",
            ):
                content = path.read_text(encoding="utf-8")
                self.assertIn(".mpa/runtime/core/agent_rules.md", content, path)
                self.assertNotIn(".mpa-workspace", content, path)

            for settings, scripts in (
                (target / ".claude/settings.json", ("session_start.py", "code_gate.py", "turn_end.py")),
                (target / ".codex/hooks.json", ("session_start.py", "code_gate.py", "turn_end.py")),
            ):
                rendered = settings.read_text(encoding="utf-8")
                self.assertIn(".mpa/runtime/hooks", rendered, settings)
                self.assertNotIn(".mpa-workspace", rendered, settings)
                for script in scripts:
                    self.assertTrue((target / ".mpa/runtime/hooks" / script).is_file(), script)

    def test_current_hook_marker_recognizes_current_runtime_command(self):
        entries = [{"hooks": [{"command": "python3 .mpa/runtime/hooks/code_gate.py --agent codex"}]}]
        self.assertTrue(install._block_already_registered(entries))

    def test_codex_hook_commands_and_scripts_smoke(self):
        block = install.build_hook_block("codex")
        commands = [entries[0]["hooks"][0]["command"] for entries in block.values()]
        for script, command in zip(("session_start.py", "code_gate.py", "turn_end.py"), commands):
            self.assertIn(f".mpa/runtime/hooks/{script}", command)
            result = subprocess.run(["python3", ".mpa/runtime/hooks/" + script, "--help"],
                                    cwd=ROOT, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
