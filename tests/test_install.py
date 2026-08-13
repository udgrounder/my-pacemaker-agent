import subprocess
import tempfile
import unittest
import json
import importlib.util
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
            self.assertFalse((target / ".mpa-workspace").exists())

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
            config = (target / ".mpa-project" / "config.yaml").read_text(encoding="utf-8")
            self.assertIn("schema_version: 1", config)
            self.assertIn('name: "' + target.name + '"', config)
            self.assertIn('root_path: "' + str(target.resolve()) + '"', config)

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

    def test_installation_refresh_requires_approved_allowlist_and_preserves_data(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            (target / ".mpa-workspace").mkdir()
            (target / "workspace").mkdir()
            (target / "docs").mkdir()
            (target / "workspace" / "keep.txt").write_text("workspace", encoding="utf-8")
            (target / "docs" / "keep.md").write_text("docs", encoding="utf-8")
            plan = {
                "schema_version": 1, "target": str(target), "agent": "codex",
                "changes": ["AGENTS.md"],
                "preserve": ["workspace/", "docs/", "general source files"],
                "backup": str(target / ".mpa-installation-backups" / "refresh-1"),
                "approval_ref": "test-approval",
            }
            plan_path = target / "refresh.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            install.run_installation_refresh(plan_path)
            self.assertTrue((target / "AGENTS.md").is_file())
            self.assertTrue((target / ".mpa-installation-backups" / "refresh-1" / "refresh-receipt.json").is_file())
            self.assertEqual((target / "workspace" / "keep.txt").read_text(encoding="utf-8"), "workspace")
            self.assertEqual((target / "docs" / "keep.md").read_text(encoding="utf-8"), "docs")

    def test_refresh_copies_only_approved_agent_spec_file(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            (target / ".mpa-workspace").mkdir()
            spec_root = ROOT / "agent-specs" / "codex" / "files"
            candidates = [path.relative_to(spec_root).as_posix() for path in spec_root.rglob("*") if path.is_file()]
            self.assertGreaterEqual(len(candidates), 2)
            plan = {"schema_version": 1, "target": str(target), "agent": "codex", "changes": [candidates[0]],
                    "preserve": ["workspace/", "docs/", "general source files"],
                    "backup": str(target / ".mpa-installation-backups" / "refresh-1"), "approval_ref": "test"}
            plan_path = target / "refresh.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            install.run_installation_refresh(plan_path)
            self.assertTrue((target / candidates[0]).is_file())
            self.assertFalse((target / candidates[1]).exists())

    def test_installation_refresh_rejects_missing_preserve_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            (target / ".mpa-workspace").mkdir()
            plan = {
                "schema_version": 1, "target": str(target), "agent": "codex", "changes": ["AGENTS.md"],
                "preserve": ["workspace/"], "backup": str(target / ".mpa-installation-backups" / "refresh-1"),
                "approval_ref": "test-approval",
            }
            plan_path = target / "refresh.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "preserve"):
                install.run_installation_refresh(plan_path)

    def test_existing_project_config_only_adds_missing_fields_and_preserves_content(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "configured-project"
            target.mkdir()
            config = target / ".mpa-project" / "config.yaml"
            config.parent.mkdir()
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
            config = target / ".mpa-project" / "config.yaml"
            config.parent.mkdir()
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
            config = target / ".mpa-project" / "config.yaml"
            config.parent.mkdir()
            invalid = "schema_version: latest\nproject:\n  name: \"owned\"\n"
            config.write_text(invalid, encoding="utf-8")

            result = project_config.ensure_project_config(target)

            self.assertEqual(result["status"], "warning")
            self.assertEqual(config.read_text(encoding="utf-8"), invalid)
            self.assertEqual(config.read_text(encoding="utf-8").count("schema_version:"), 1)

    def test_config_audit_warns_on_moved_root_without_exposing_absolute_path(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            config = target / ".mpa-project" / "config.yaml"
            config.parent.mkdir()
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

    def test_refresh_can_add_config_fields_only_when_explicitly_allowed(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            (target / ".mpa-workspace").mkdir()
            config = target / ".mpa-project" / "config.yaml"
            config.parent.mkdir()
            config.write_text("schema_version: 1\nproject:\n  name: \"owned\"\n", encoding="utf-8")
            plan = {
                "schema_version": 1, "target": str(target), "agent": "codex",
                "changes": [".mpa-project/config.yaml"],
                "preserve": ["workspace/", "docs/", "general source files"],
                "backup": str(target / ".mpa-installation-backups" / "config-refresh"),
                "approval_ref": "config-test",
            }
            plan_path = target / "refresh.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")

            install.run_installation_refresh(plan_path)

            updated = config.read_text(encoding="utf-8")
            self.assertIn('name: "owned"', updated)
            self.assertIn("root_path:", updated)
            self.assertTrue((target / ".mpa-installation-backups" / "config-refresh" / ".mpa-project" / "config.yaml").is_file())

    def test_existing_install_rejection_preserves_workspace_docs_and_agent_settings(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            (target / ".mpa-workspace").mkdir()
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

    def test_codex_hook_commands_and_scripts_smoke(self):
        block = install.build_hook_block("codex")
        commands = [entries[0]["hooks"][0]["command"] for entries in block.values()]
        for script, command in zip(("session_start.py", "code_gate.py", "turn_end.py"), commands):
            self.assertIn(f".mpa-workspace/hooks/{script}", command)
            result = subprocess.run(["python3", ".mpa-workspace/hooks/" + script, "--help"],
                                    cwd=ROOT, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
