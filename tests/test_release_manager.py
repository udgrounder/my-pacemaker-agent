import argparse
import importlib.util
import json
import os
import subprocess
import sys
import errno
import shutil
import stat
import tempfile
import unittest
import zipfile
from unittest import mock
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "release_manager.py"
SPEC = importlib.util.spec_from_file_location("release_manager", MODULE_PATH)
release_manager = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release_manager)


class ReleaseManagerTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        release_manager.ROOT = self.root
        release_manager.RUNTIME_SOURCE = self.root / ".mpa/runtime"
        release_manager.RUNTIME_DIST = self.root / "dist" / ".mpa/runtime"
        release_manager.WORKSPACE = self.root / "workspace"
        release_manager.RELEASES = release_manager.WORKSPACE / "releases"
        release_manager.MANIFESTS = release_manager.RELEASES
        release_manager.PACKAGES = release_manager.RELEASES
        release_manager.RELEASE_RECEIPTS = release_manager.RELEASES
        release_manager.LEGACY_RELEASES = release_manager.RELEASES / "legacy"
        release_manager.LEGACY_ACTIVE_MANIFESTS = release_manager.RELEASES / "manifests"
        release_manager.LEGACY_ACTIVE_PACKAGES = release_manager.RELEASES / "packages"
        release_manager.LEGACY_ACTIVE_RECEIPTS = release_manager.WORKSPACE / "receipts" / "releases"
        release_manager.DEPLOYMENT_RECEIPTS = release_manager.WORKSPACE / ".local" / "receipts" / "deployments"
        release_manager.ISSUES = release_manager.WORKSPACE / "issues"
        self.write_runtime(release_manager.RUNTIME_SOURCE, "v1")
        self.release_preflight_patch = mock.patch.object(
            release_manager,
            "run_release_preflight",
            return_value={"command": ["release-preflight"], "exit_code": 0, "steps": [], "executed_at": "test"},
        )
        self.release_preflight = self.release_preflight_patch.start()

    def tearDown(self):
        self.release_preflight_patch.stop()
        self.temp.cleanup()

    @staticmethod
    def write_runtime(path, version):
        path.mkdir(parents=True, exist_ok=True)
        (path / ".mpa-version").write_text(f"current_release: {version}\n", encoding="utf-8")
        (path / "rule.md").write_text(version, encoding="utf-8")
        hooks = path / "hooks"
        hooks.mkdir(exist_ok=True)
        for name in ("session_start.py", "code_gate.py"):
            (hooks / name).write_text(
                "import argparse\nparser = argparse.ArgumentParser()\nparser.parse_args()\n",
                encoding="utf-8",
            )

    def prepare(self, runtime_config=None, allow_version_only=False):
        release_manager.sync_runtime(argparse.Namespace())
        args = argparse.Namespace(
            verified_by="test", compatibility="compatible", breaking_change="none", migration="none",
            rollback_condition="verification failure", release_note="test release",
            validation_command=[sys.executable, "-c", "print('ok')"],
            allow_version_only=allow_version_only,
        )
        if runtime_config is not None:
            migration = self.root / "runtime-config.json"
            migration.write_text(json.dumps(runtime_config), encoding="utf-8")
            args.runtime_config_json = str(migration)
        release_manager.prepare_release(args)
        manifests = sorted(release_manager.RELEASES.glob("*/manifest_*.json"))
        self.assertTrue(manifests)
        return manifests[-1]

    def test_deploy_uses_immutable_package_not_current_dist(self):
        manifest = self.prepare()
        self.assertEqual(json.loads(manifest.read_text(encoding="utf-8"))["asset_root"], ".mpa/runtime")
        self.write_runtime(release_manager.RUNTIME_DIST, "v2")
        target_root = self.root / "target"
        self.write_runtime(target_root / ".mpa/runtime", "old")
        release_manager.deployment_dry_run(argparse.Namespace(
            manifest=str(manifest), target=str(target_root), target_ref="test-target",
        ))
        dry_run = next((release_manager.DEPLOYMENT_RECEIPTS / "test-target").glob("dry-run-*.json"))

        release_manager.deploy(argparse.Namespace(
            manifest=str(manifest), target=str(target_root), target_ref="test-target", verified_by="test",
            dry_run=str(dry_run), approved_by="test", approval_ref="unit", rollback_owner="test",
        ))

        self.assertEqual((target_root / ".mpa/runtime" / "rule.md").read_text(encoding="utf-8"), "v1")
        self.assertTrue(any((target_root / ".mpa/backups").iterdir()))
        self.assertTrue((target_root / ".mpa/runtime" / "history" / "releases" / json.loads(manifest.read_text())["release_id"]).with_suffix(".json").is_file())

    def test_deployment_receipts_redact_target_paths_and_operator_references(self):
        manifest = self.prepare()
        target = self.root / "local-target"
        self.write_runtime(target / ".mpa/runtime", "old")
        release_manager.deployment_dry_run(argparse.Namespace(
            manifest=str(manifest), target=str(target), target_ref="target",
        ))
        dry_run = next((release_manager.DEPLOYMENT_RECEIPTS / "target").glob("dry-run-*.json"))
        dry_run_data = json.loads(dry_run.read_text(encoding="utf-8"))
        self.assertNotIn("target", dry_run_data)
        self.assertEqual(dry_run_data["target_fingerprint"], release_manager.project_fingerprint(target))
        self.assertNotIn(str(target), dry_run.read_text(encoding="utf-8"))

        release_manager.deploy(argparse.Namespace(
            manifest=str(manifest), target=str(target), target_ref="target", verified_by="test",
            dry_run=str(dry_run), approved_by="test", approval_ref=f"operator request: {target}",
            rollback_owner="test",
        ))
        receipt = next((release_manager.DEPLOYMENT_RECEIPTS / "target").glob("deploy-*.json"))
        receipt_text = receipt.read_text(encoding="utf-8")
        self.assertNotIn(str(target), receipt_text)
        self.assertIn("<redacted-path>", receipt_text)

    def test_rollback_uses_local_target_registry_when_target_is_omitted(self):
        manifest = self.prepare()
        release_id = json.loads(manifest.read_text(encoding="utf-8"))["release_id"]
        target = self.root / "target"
        self.write_runtime(target / ".mpa/runtime", "old")
        release_manager.deployment_dry_run(argparse.Namespace(
            manifest=str(manifest), target=str(target), target_ref="target",
        ))
        dry_run = next((release_manager.DEPLOYMENT_RECEIPTS / "target").glob("dry-run-*.json"))
        release_manager.deploy(argparse.Namespace(
            manifest=str(manifest), target=str(target), target_ref="target", verified_by="test",
            dry_run=str(dry_run), approved_by="test", approval_ref="unit", rollback_owner="test",
        ))
        backup = next((target / ".mpa/backups").iterdir())

        release_manager.rollback(argparse.Namespace(
            target_ref="target", backup=str(backup.relative_to(target)), release_id=release_id,
            verified_by="test", approved_by="test", approval_ref="unit", rollback_owner="test",
        ))

        self.assertEqual((target / ".mpa/runtime/rule.md").read_text(encoding="utf-8"), "old")
        locator = release_manager.local_target_locator_path("target")
        self.assertTrue(locator.is_file())

    def test_rollback_rejects_stale_local_target_registry(self):
        manifest = self.prepare()
        target = self.root / "target"
        self.write_runtime(target / ".mpa/runtime", "old")
        release_manager.deployment_dry_run(argparse.Namespace(
            manifest=str(manifest), target=str(target), target_ref="target",
        ))
        locator = release_manager.local_target_locator_path("target")
        data = json.loads(locator.read_text(encoding="utf-8"))
        data["target_fingerprint"] = "stale"
        locator.write_text(json.dumps(data), encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "local deployment target registry no longer matches"):
            release_manager.rollback(argparse.Namespace(
                target_ref="target", backup=".mpa/backups/missing", release_id="release",
                verified_by="test", approved_by="test", approval_ref="unit", rollback_owner="test",
            ))

    def test_deployment_dry_run_requires_current_runtime_layout(self):
        manifest = self.prepare()
        target = self.root / "target"
        (target / ".mpa/config").mkdir(parents=True)
        with self.assertRaisesRegex(ValueError, "current MPA layout"):
            release_manager.deployment_dry_run(argparse.Namespace(
                manifest=str(manifest), target=str(target), target_ref="target"))
        self.assertFalse((release_manager.DEPLOYMENT_RECEIPTS / "target").exists())

    def test_deployment_rejects_runtime_parent_symlink(self):
        manifest = self.prepare()
        target = self.root / "target"
        external = self.root / "external-mpa"
        self.write_runtime(external / "runtime", "old")
        target.mkdir()
        os.symlink(external, target / ".mpa")

        with self.assertRaisesRegex(ValueError, "Runtime path contains an unsupported symlink"):
            release_manager.deployment_dry_run(argparse.Namespace(
                manifest=str(manifest), target=str(target), target_ref="target"))

    def test_deploy_rejects_backup_symlink_before_writing(self):
        manifest = self.prepare()
        target = self.root / "target"
        self.write_runtime(target / ".mpa/runtime", "old")
        external = self.root / "external-backups"
        external.mkdir()
        os.symlink(external, target / ".mpa/backups")
        release_manager.deployment_dry_run(argparse.Namespace(
            manifest=str(manifest), target=str(target), target_ref="target"))
        dry_run = next((release_manager.DEPLOYMENT_RECEIPTS / "target").glob("dry-run-*.json"))

        with self.assertRaisesRegex(ValueError, "Runtime backup path contains an unsupported symlink"):
            release_manager.deploy(argparse.Namespace(
                manifest=str(manifest), target=str(target), target_ref="target", verified_by="test",
                dry_run=str(dry_run), approved_by="test", approval_ref="unit", rollback_owner="test"))
        self.assertFalse(any(external.iterdir()))

    def test_deployment_dry_run_rejects_config_parent_symlink_for_migration(self):
        manifest = self.prepare({"schema_version": 2, "additive_defaults": {"runtime.enabled": True}})
        target = self.root / "target"
        self.write_runtime(target / ".mpa/runtime", "old")
        external = self.root / "external-config"
        external.mkdir()
        (target / ".mpa").mkdir(exist_ok=True)
        os.symlink(external, target / ".mpa/config")

        with self.assertRaisesRegex(ValueError, "does not follow config.yaml symlinks"):
            release_manager.deployment_dry_run(argparse.Namespace(
                manifest=str(manifest), target=str(target), target_ref="target"))

    def test_rollback_rejects_runtime_and_backup_symlinks(self):
        target = self.root / "target"
        target.mkdir()
        external_runtime = self.root / "external-runtime"
        self.write_runtime(external_runtime, "old")
        (target / ".mpa").mkdir()
        os.symlink(external_runtime, target / ".mpa/runtime")

        with self.assertRaisesRegex(ValueError, "Runtime path contains an unsupported symlink"):
            release_manager.rollback(argparse.Namespace(
                target=str(target), target_ref="target", backup=".mpa/backups/backup",
                release_id="release", verified_by="test", approved_by="test", approval_ref="unit", rollback_owner="test"))

        (target / ".mpa/runtime").unlink()
        self.write_runtime(target / ".mpa/runtime", "old")
        external_backups = self.root / "external-backups"
        external_backups.mkdir()
        os.symlink(external_backups, target / ".mpa/backups")

        with self.assertRaisesRegex(ValueError, "Runtime backup path contains an unsupported symlink"):
            release_manager.rollback(argparse.Namespace(
                target=str(target), target_ref="target", backup=".mpa/backups/backup",
                release_id="release", verified_by="test", approved_by="test", approval_ref="unit", rollback_owner="test"))

    def test_required_directories_reject_symlink(self):
        target = self.root / "target"
        external = self.root / "external-workspace"
        external.mkdir()
        target.mkdir()
        os.symlink(external, target / "workspace")

        with self.assertRaisesRegex(ValueError, "required project path contains an unsupported symlink"):
            release_manager.ensure_required_project_directories(target)

    def test_extract_runtime_rejects_special_file(self):
        archive = self.root / "special.zip"
        with zipfile.ZipFile(archive, "w") as bundle:
            info = zipfile.ZipInfo("named-pipe")
            info.external_attr = (stat.S_IFIFO | 0o644) << 16
            bundle.writestr(info, b"")

        with self.assertRaisesRegex(ValueError, "release package extraction failed"):
            release_manager._extract_runtime(archive, self.root / "staging")

    def test_extract_runtime_rejects_symlink_and_type_mismatch(self):
        cases = (
            ("link", stat.S_IFLNK | 0o777),
            ("directory-without-slash", stat.S_IFDIR | 0o755),
            ("regular-file/", stat.S_IFREG | 0o644),
        )
        for index, (name, mode) in enumerate(cases):
            with self.subTest(name=name):
                archive = self.root / f"invalid-type-{index}.zip"
                with zipfile.ZipFile(archive, "w") as bundle:
                    info = zipfile.ZipInfo(name)
                    info.external_attr = mode << 16
                    bundle.writestr(info, b"")
                with self.assertRaisesRegex(ValueError, "release package extraction failed"):
                    release_manager._extract_runtime(archive, self.root / f"staging-{index}")

    def test_prepare_release_rejects_invalid_packaged_hook(self):
        hook = release_manager.RUNTIME_SOURCE / "hooks" / "session_start.py"
        hook.write_text("def invalid(:\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "hook is not valid Python: hooks/session_start.py"):
            self.prepare()
        self.assertFalse(any(release_manager.RELEASES.glob("*/manifest_*.json")))

    def test_prepare_release_runs_standard_preflight_before_creating_artifacts(self):
        self.prepare()
        self.release_preflight.assert_called_once_with()

    def test_prepare_release_rejects_version_only_runtime_package_and_restores_dist(self):
        manifest = self.prepare()
        prior_release_id = json.loads(manifest.read_text(encoding="utf-8"))["release_id"]

        with self.assertRaisesRegex(ValueError, "refusing version-only release without --allow-version-only"):
            self.prepare()

        self.assertEqual(len(list(release_manager.RELEASES.glob("*/manifest_*.json"))), 1)
        self.assertEqual(release_manager.current_release(release_manager.RUNTIME_SOURCE), prior_release_id)
        self.assertEqual(release_manager.asset_map(release_manager.RUNTIME_SOURCE),
                         release_manager.asset_map(release_manager.RUNTIME_DIST))

    def test_prepare_release_allows_explicit_version_only_runtime_package(self):
        self.prepare()
        self.prepare(allow_version_only=True)

        self.assertEqual(len(list(release_manager.RELEASES.glob("*/manifest_*.json"))), 2)

    def test_prepare_release_rejects_retired_active_execution_reference(self):
        rule = self.root / "agent-specs" / "codex" / "files" / "AGENTS.md"
        rule.parent.mkdir(parents=True)
        rule.write_text("load .mpa-workspace/runtime", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "retired Runtime execution reference"):
            self.prepare()
        self.assertFalse(list(release_manager._release_bundle_dirs()))

    def test_prepare_release_ignores_local_agent_settings(self):
        local_settings = self.root / ".claude" / "settings.local.json"
        local_settings.parent.mkdir(parents=True)
        local_settings.write_text('{"token": "local-secret", "path": "/Users/operator/local"}', encoding="utf-8")
        self.prepare()

    def test_prepare_release_rejects_sensitive_release_metadata(self):
        release_manager.sync_runtime(argparse.Namespace())
        with self.assertRaisesRegex(ValueError, "release metadata contains"):
            release_manager.prepare_release(argparse.Namespace(
                verified_by="test", compatibility="compatible", breaking_change="none", migration="none",
                rollback_condition="verification failure", release_note="see /Users/operator/private-note",
                validation_command=[sys.executable, "-c", "print('ok')"],
            ))
        self.assertFalse(list(release_manager._release_bundle_dirs()))

    def test_packaged_runtime_validates_all_python_hooks(self):
        (release_manager.RUNTIME_SOURCE / "hooks" / "turn_end.py").write_text("def invalid(:\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "hook is not valid Python: hooks/turn_end.py"):
            self.prepare()

    def test_deploy_and_rollback_preserve_user_owned_paths(self):
        manifest = self.prepare()
        release_id = json.loads(manifest.read_text(encoding="utf-8"))["release_id"]
        target_root = self.root / "target"
        self.write_runtime(target_root / ".mpa/runtime", "old")
        (target_root / "workspace").mkdir()
        (target_root / "docs").mkdir()
        (target_root / "AGENTS.md").write_text("user config", encoding="utf-8")
        (target_root / "main.py").write_text("user source", encoding="utf-8")
        (target_root / "workspace" / "user.txt").write_text("workspace", encoding="utf-8")
        (target_root / "docs" / "user.md").write_text("docs", encoding="utf-8")
        docs_index = target_root / "docs" / "INDEX.md"
        docs_index.write_text("# operator index\n", encoding="utf-8")
        config = target_root / ".mpa/config" / "config.yaml"
        config.parent.mkdir(parents=True)
        config.write_text(
            "schema_version: 1\nproject:\n"
            "  name: \"operator-owned\"\n"
            f"  root_path: \"{target_root}\"\n"
            "  initialized_at: \"2026-08-13T00:00:00Z\"\n",
            encoding="utf-8",
        )
        config_before = config.read_text(encoding="utf-8")
        release_manager.deployment_dry_run(argparse.Namespace(manifest=str(manifest), target=str(target_root), target_ref="test-target"))
        dry_run = next((release_manager.DEPLOYMENT_RECEIPTS / "test-target").glob("dry-run-*.json"))
        release_manager.deploy(argparse.Namespace(
            manifest=str(manifest), target=str(target_root), target_ref="test-target", verified_by="test",
            dry_run=str(dry_run), approved_by="test", approval_ref="unit", rollback_owner="test"))
        backup = next((target_root / ".mpa/backups").iterdir())
        self.assertTrue(backup.is_dir())
        with zipfile.ZipFile(backup / "runtime.zip") as archive:
            self.assertIn(".mpa/runtime/.mpa-version", archive.namelist())
            self.assertNotIn("AGENTS.md", archive.namelist())
        self.assertFalse((backup / "runtime").exists())
        self.assertFalse((backup / "runtime-config/config.yaml").exists())
        release_manager.rollback(argparse.Namespace(
            target=str(target_root), target_ref="test-target", backup=str(backup.relative_to(target_root)),
            release_id=release_id, verified_by="test", approved_by="test", approval_ref="unit", rollback_owner="test"))
        self.assertEqual((target_root / ".mpa/runtime" / "rule.md").read_text(encoding="utf-8"), "old")
        self.assertEqual((target_root / "workspace" / "user.txt").read_text(encoding="utf-8"), "workspace")
        self.assertEqual((target_root / "docs" / "user.md").read_text(encoding="utf-8"), "docs")
        self.assertEqual(docs_index.read_text(encoding="utf-8"), "# operator index\n")
        self.assertEqual((target_root / "AGENTS.md").read_text(encoding="utf-8"), "user config")
        self.assertEqual((target_root / "main.py").read_text(encoding="utf-8"), "user source")
        self.assertEqual(config.read_text(encoding="utf-8"), config_before)

    def test_runtime_config_migration_is_additive_and_rolled_back_with_runtime(self):
        migration = {"schema_version": 2, "additive_defaults": {
            "runtime.resolved_name": "${project.name}",
            "runtime.root_path": "${project.root_path}",
            "runtime.new_flag": True,
        }}
        manifest = self.prepare(migration)
        release_id = json.loads(manifest.read_text(encoding="utf-8"))["release_id"]
        target = self.root / "target"
        self.write_runtime(target / ".mpa/runtime", "old")
        config = target / ".mpa/config" / "config.yaml"
        config.parent.mkdir(parents=True)
        config.write_text(
            "schema_version: 1\nproject:\n  name: \"operator\"\n"
            f"  root_path: \"{target}\"\n  initialized_at: \"2026-08-13T00:00:00Z\"\n"
            "runtime:\n  project_name: \"user-value\"\n",
            encoding="utf-8",
        )
        original = config.read_text(encoding="utf-8")
        release_manager.deployment_dry_run(argparse.Namespace(manifest=str(manifest), target=str(target), target_ref="target"))
        dry_run = next((release_manager.DEPLOYMENT_RECEIPTS / "target").glob("dry-run-*.json"))
        release_manager.deploy(argparse.Namespace(manifest=str(manifest), target=str(target), target_ref="target", verified_by="test",
                                                  dry_run=str(dry_run), approved_by="test", approval_ref="unit", rollback_owner="test"))
        updated = config.read_text(encoding="utf-8")
        self.assertIn('project_name: "user-value"', updated)
        self.assertIn(f'root_path: "{target}"', updated)
        self.assertIn('resolved_name: "operator"', updated)
        self.assertIn('new_flag: true', updated)
        manifest_data = json.loads(manifest.read_text(encoding="utf-8"))
        self.assertNotIn(str(target), json.dumps(manifest_data))
        backup = next((target / ".mpa/backups").iterdir())
        self.assertEqual((backup / "runtime-config/config.yaml").read_text(encoding="utf-8"), original)
        release_manager.rollback(argparse.Namespace(target=str(target), target_ref="target", backup=str(backup.relative_to(target)),
                                                    release_id=release_id, verified_by="test", approved_by="test", approval_ref="unit", rollback_owner="test"))
        self.assertEqual(config.read_text(encoding="utf-8"), original)
        self.assertEqual((target / ".mpa/runtime" / "rule.md").read_text(encoding="utf-8"), "old")

    def test_runtime_config_migration_bootstraps_missing_config_and_rollback_removes_it(self):
        migration = {"schema_version": 2, "additive_defaults": {
            "runtime.project_name": "${project.name}",
            "runtime.root_path": "${project.root_path}",
        }}
        manifest = self.prepare(migration)
        release_id = json.loads(manifest.read_text(encoding="utf-8"))["release_id"]
        target = self.root / "legacy-target"
        self.write_runtime(target / ".mpa/runtime", "legacy")
        config = target / ".mpa/config" / "config.yaml"
        self.assertFalse(config.exists())

        release_manager.deployment_dry_run(argparse.Namespace(
            manifest=str(manifest), target=str(target), target_ref="legacy-target"))
        dry_run = next((release_manager.DEPLOYMENT_RECEIPTS / "legacy-target").glob("dry-run-*.json"))
        release_manager.deploy(argparse.Namespace(
            manifest=str(manifest), target=str(target), target_ref="legacy-target", verified_by="test",
            dry_run=str(dry_run), approved_by="test", approval_ref="unit", rollback_owner="test"))

        self.assertTrue(config.is_file())
        self.assertIn('project_name: "legacy-target"', config.read_text(encoding="utf-8"))
        backup = next((target / ".mpa/backups").iterdir())
        metadata = json.loads((backup / "backup-metadata.json").read_text(encoding="utf-8"))
        self.assertFalse((backup / "runtime-config/config.yaml").exists())
        self.assertTrue(metadata["config_snapshot"]["included"])
        self.assertFalse(metadata["config_snapshot"]["existed"])

        release_manager.rollback(argparse.Namespace(
            target=str(target), target_ref="legacy-target", backup=str(backup.relative_to(target)),
            release_id=release_id, verified_by="test", approved_by="test", approval_ref="unit",
            rollback_owner="test"))
        self.assertFalse(config.exists())
        self.assertEqual((target / ".mpa/runtime" / "rule.md").read_text(encoding="utf-8"), "legacy")

    def test_deploy_creates_only_missing_workspace_and_docs_roots(self):
        manifest = self.prepare()
        target = self.root / "target"
        self.write_runtime(target / ".mpa/runtime", "old")
        release_manager.deployment_dry_run(argparse.Namespace(manifest=str(manifest), target=str(target), target_ref="target"))
        dry_run = next((release_manager.DEPLOYMENT_RECEIPTS / "target").glob("dry-run-*.json"))
        release_manager.deploy(argparse.Namespace(manifest=str(manifest), target=str(target), target_ref="target", verified_by="test",
                                                  dry_run=str(dry_run), approved_by="test", approval_ref="unit", rollback_owner="test"))
        self.assertTrue((target / "workspace").is_dir())
        self.assertTrue((target / "workspace" / "issues").is_dir())
        self.assertTrue((target / "docs").is_dir())
        self.assertTrue((target / "docs" / "INDEX.md").is_file())

    def test_required_directory_conflict_is_prevalidated_without_partial_creation(self):
        target = self.root / "target"
        (target / "docs").parent.mkdir(parents=True)
        (target / "docs").write_text("user file", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "docs"):
            release_manager.ensure_required_project_directories(target)
        self.assertFalse((target / "workspace").exists())
        self.assertEqual((target / "docs").read_text(encoding="utf-8"), "user file")

    def test_runtime_backup_retention_keeps_the_newest_three_runtime_zip_backups_only(self):
        target = self.root / "target"
        backups = target / ".mpa/backups"
        for index in range(4):
            backup = backups / f"backup-{index}"
            backup.mkdir(parents=True, exist_ok=True)
            (backup / release_manager.BACKUP_MARKER).write_text(json.dumps({
                "kind": "runtime_backup", "status": "successful", "release_id": f"release-{index}"
            }), encoding="utf-8")
            with zipfile.ZipFile(backup / "runtime.zip", "w") as archive:
                archive.writestr(".mpa/runtime/rule.md", "old")
            timestamp = 1_700_000_000 + index
            os.utime(backup, (timestamp, timestamp))
        note = backups / "operator-note.txt"
        note.write_text("preserve", encoding="utf-8")
        manual = backups / "operator-snapshot"
        manual.mkdir()
        (manual / "keep.txt").write_text("preserve", encoding="utf-8")

        removed = release_manager.prune_runtime_backups(target)

        self.assertEqual(removed, ["backup-0"])
        self.assertEqual(sorted(path.name for path in backups.iterdir()),
                         ["backup-1", "backup-2", "backup-3", "operator-note.txt", "operator-snapshot"])

    def test_history_cleanup_dry_run_lists_all_managed_candidates_without_writing(self):
        for index in range(11):
            bundle = release_manager.RELEASES / f"release-{index}"
            bundle.mkdir(parents=True)
            os.utime(bundle, (1_700_000_000 + index, 1_700_000_000 + index))
        target = self.root / "target"
        self.write_runtime(target / ".mpa/runtime", "old")
        release_manager.remember_local_target(target, "target")
        history = target / ".mpa/runtime/history/releases"
        receipts = release_manager.DEPLOYMENT_RECEIPTS / "target"
        backups = target / ".mpa/backups"
        for index in range(11):
            entry = history / f"release-{index}.json"
            entry.parent.mkdir(parents=True, exist_ok=True)
            entry.write_text("{}", encoding="utf-8")
            receipt = receipts / f"deploy-{index}.json"
            receipt.parent.mkdir(parents=True, exist_ok=True)
            receipt.write_text("{}", encoding="utf-8")
            timestamp = 1_700_000_000 + index
            os.utime(entry, (timestamp, timestamp)); os.utime(receipt, (timestamp, timestamp))
        for index in range(4):
            backup = backups / f"backup-{index}"
            backup.mkdir(parents=True)
            (backup / release_manager.BACKUP_MARKER).write_text(json.dumps({
                "kind": "runtime_backup", "status": "successful"
            }), encoding="utf-8")
            with zipfile.ZipFile(backup / "runtime.zip", "w") as archive:
                archive.writestr(".mpa/runtime/rule.md", "old")
            timestamp = 1_700_000_000 + index
            os.utime(backup, (timestamp, timestamp))

        result = release_manager.history_cleanup_candidates()

        self.assertEqual(result["release_bundles"], ["release-0"])
        self.assertEqual(result["targets"], [{"target_ref": "target", "deployment_history": ["release-0.json"],
                                               "deployment_receipts": ["deploy-0.json"],
                                               "runtime_backups": ["backup-0"]}])
        self.assertTrue((release_manager.RELEASES / "release-0").exists())
        self.assertTrue((history / "release-0.json").exists())
        self.assertTrue((receipts / "deploy-0.json").exists())
        self.assertTrue((backups / "backup-0").exists())

    def test_history_cleanup_apply_requires_approval_and_removes_only_reviewed_candidates(self):
        for index in range(2):
            bundle = release_manager.RELEASES / f"release-{index}"
            bundle.mkdir(parents=True)
            os.utime(bundle, (1_700_000_000 + index, 1_700_000_000 + index))
        target = self.root / "target"
        self.write_runtime(target / ".mpa/runtime", "old")
        release_manager.remember_local_target(target, "target")
        with self.assertRaisesRegex(ValueError, "approved-by, approval-ref, and rollback-owner are required"):
            release_manager.history_cleanup(argparse.Namespace(
                keep=1, backup_keep=1, apply=True, approved_by="", approval_ref="unit", rollback_owner="test"))
        with mock.patch.object(release_manager, "target_lock") as target_lock:
            release_manager.history_cleanup(argparse.Namespace(
                keep=1, backup_keep=1, apply=True, approved_by="test", approval_ref="unit", rollback_owner="test"))
        target_lock.assert_not_called()
        self.assertFalse((release_manager.RELEASES / "release-0").exists())
        self.assertTrue((release_manager.RELEASES / "release-1").exists())

    def test_successful_deploy_keeps_only_a_verified_runtime_zip_backup(self):
        manifest = self.prepare()
        target = self.root / "target"
        self.write_runtime(target / ".mpa/runtime", "old")
        release_manager.deployment_dry_run(argparse.Namespace(
            manifest=str(manifest), target=str(target), target_ref="target"))
        dry_run = next((release_manager.DEPLOYMENT_RECEIPTS / "target").glob("dry-run-*.json"))

        with mock.patch.object(release_manager, "prune_runtime_backups") as prune:
            release_manager.deploy(argparse.Namespace(
                manifest=str(manifest), target=str(target), target_ref="target", verified_by="test",
                dry_run=str(dry_run), approved_by="test", approval_ref="unit", rollback_owner="test"))
        prune.assert_not_called()

        backups = list((target / ".mpa/backups").iterdir())
        self.assertEqual(len(backups), 1)
        self.assertTrue(backups[0].is_dir())
        self.assertTrue((backups[0] / "runtime.zip").is_file())
        self.assertFalse((backups[0] / "runtime").exists())
        release_id = json.loads(manifest.read_text(encoding="utf-8"))["release_id"]
        self.assertEqual(release_manager._validate_backup(backups[0], release_id)["release_id"], release_id)

    def test_backup_archive_failure_restores_runtime_and_preserves_directory_snapshot(self):
        manifest = self.prepare()
        target = self.root / "target"
        self.write_runtime(target / ".mpa/runtime", "old")
        release_manager.deployment_dry_run(argparse.Namespace(
            manifest=str(manifest), target=str(target), target_ref="target"))
        dry_run = next((release_manager.DEPLOYMENT_RECEIPTS / "target").glob("dry-run-*.json"))

        with mock.patch.object(release_manager, "archive_backup", side_effect=OSError("archive failed")):
            with self.assertRaisesRegex(OSError, "archive failed"):
                release_manager.deploy(argparse.Namespace(
                    manifest=str(manifest), target=str(target), target_ref="target", verified_by="test",
                    dry_run=str(dry_run), approved_by="test", approval_ref="unit", rollback_owner="test"))

        self.assertEqual((target / ".mpa/runtime" / "rule.md").read_text(encoding="utf-8"), "old")
        self.assertTrue(any(path.is_dir() for path in (target / ".mpa/backups").iterdir()))
        self.assertFalse(any((path / "runtime.zip").exists() for path in (target / ".mpa/backups").iterdir() if path.is_dir()))

    def test_migrate_runtime_backups_replaces_only_legacy_runtime_tree(self):
        target = self.root / "target"
        backup = target / ".mpa/backups" / "release-1"
        self.write_runtime(backup / "runtime/.mpa/runtime", "old")
        release_manager._write_backup_marker(backup, "release-1", {})

        release_manager.migrate_runtime_backups(argparse.Namespace(
            target=str(target), approved_by="test", approval_ref="unit", rollback_owner="test"))

        self.assertFalse((backup / "runtime").exists())
        self.assertTrue((backup / "runtime.zip").is_file())
        self.assertEqual(release_manager._validate_backup(backup, "release-1")["release_id"], "release-1")
        metadata = json.loads((backup / release_manager.BACKUP_MARKER).read_text(encoding="utf-8"))
        self.assertEqual(metadata["archive_migration"]["status"], "completed")
        self.assertTrue(metadata["archive_migration"]["source_runtime_removed"])

    def test_migrate_runtime_backups_preserves_legacy_runtime_after_archive_failure(self):
        target = self.root / "target"
        backup = target / ".mpa/backups" / "release-1"
        self.write_runtime(backup / "runtime/.mpa/runtime", "old")
        release_manager._write_backup_marker(backup, "release-1", {})

        with mock.patch.object(release_manager, "archive_backup", side_effect=OSError("archive failed")):
            with self.assertRaisesRegex(ValueError, "originals were preserved"):
                release_manager.migrate_runtime_backups(argparse.Namespace(
                    target=str(target), approved_by="test", approval_ref="unit", rollback_owner="test"))

        self.assertTrue((backup / "runtime/.mpa/runtime/rule.md").is_file())
        self.assertFalse((backup / "runtime.zip").exists())
        metadata = json.loads((backup / release_manager.BACKUP_MARKER).read_text(encoding="utf-8"))
        self.assertEqual(metadata["archive_migration"]["status"], "failed")
        self.assertTrue(metadata["archive_migration"]["error"])

    def test_deployment_receipt_failure_preserves_published_zip_backup(self):
        manifest = self.prepare()
        target = self.root / "target"
        self.write_runtime(target / ".mpa/runtime", "old")
        release_manager.deployment_dry_run(argparse.Namespace(
            manifest=str(manifest), target=str(target), target_ref="target"))
        dry_run = next((release_manager.DEPLOYMENT_RECEIPTS / "target").glob("dry-run-*.json"))
        original_write = release_manager.write_safe_receipt

        def fail_deploy_receipt(path, value):
            if path.parent == release_manager.DEPLOYMENT_RECEIPTS / "target" and value.get("status") == "applied":
                raise OSError("receipt failed")
            return original_write(path, value)

        with mock.patch.object(release_manager, "write_safe_receipt", side_effect=fail_deploy_receipt):
            with self.assertRaisesRegex(OSError, "receipt failed"):
                release_manager.deploy(argparse.Namespace(
                    manifest=str(manifest), target=str(target), target_ref="target", verified_by="test",
                    dry_run=str(dry_run), approved_by="test", approval_ref="unit", rollback_owner="test"))

        self.assertEqual((target / ".mpa/runtime" / "rule.md").read_text(encoding="utf-8"), "old")
        self.assertTrue(any((path / "runtime.zip").is_file() for path in (target / ".mpa/backups").iterdir() if path.is_dir()))

    def test_rollback_rejects_legacy_runtime_directory_backup(self):
        manifest = self.prepare()
        release_id = json.loads(manifest.read_text(encoding="utf-8"))["release_id"]
        target = self.root / "target"
        self.write_runtime(target / ".mpa/runtime", "old")
        release_manager.deployment_dry_run(argparse.Namespace(
            manifest=str(manifest), target=str(target), target_ref="target"))
        dry_run = next((release_manager.DEPLOYMENT_RECEIPTS / "target").glob("dry-run-*.json"))
        release_manager.deploy(argparse.Namespace(
            manifest=str(manifest), target=str(target), target_ref="target", verified_by="test",
            dry_run=str(dry_run), approved_by="test", approval_ref="unit", rollback_owner="test"))
        backup = next((target / ".mpa/backups").iterdir())
        with release_manager.materialized_runtime_archive(backup / "runtime.zip") as extracted:
            shutil.copytree(extracted, backup / "runtime")
        (backup / "runtime.zip").unlink()

        with self.assertRaisesRegex(ValueError, "asset checksum"):
            release_manager.rollback(argparse.Namespace(
                target=str(target), target_ref="target", backup=str(backup.relative_to(target)), release_id=release_id,
                verified_by="test", approved_by="test", approval_ref="unit", rollback_owner="test"))

    def test_rollback_requires_approval_metadata(self):
        manifest = self.prepare()
        release_id = json.loads(manifest.read_text(encoding="utf-8"))["release_id"]
        target = self.root / "target"
        self.write_runtime(target / ".mpa/runtime", "old")
        release_manager.deployment_dry_run(argparse.Namespace(
            manifest=str(manifest), target=str(target), target_ref="target"))
        dry_run = next((release_manager.DEPLOYMENT_RECEIPTS / "target").glob("dry-run-*.json"))
        release_manager.deploy(argparse.Namespace(
            manifest=str(manifest), target=str(target), target_ref="target", verified_by="test",
            dry_run=str(dry_run), approved_by="test", approval_ref="unit", rollback_owner="test"))
        backup = next((target / ".mpa/backups").iterdir())

        for field in ("approved_by", "approval_ref", "rollback_owner"):
            with self.subTest(field=field):
                values = {"approved_by": "test", "approval_ref": "unit", "rollback_owner": "test"}
                values[field] = " "
                with self.assertRaisesRegex(ValueError, "approved-by, approval-ref, and rollback-owner are required"):
                    release_manager.rollback(argparse.Namespace(
                        target=str(target), target_ref="target", backup=str(backup.relative_to(target)), release_id=release_id,
                        verified_by="test", **values))

    def test_manual_backup_directory_is_not_pruned_or_accepted_for_rollback(self):
        target = self.root / "target"
        self.write_runtime(target / ".mpa/runtime", "old")
        manual = target / ".mpa/backups" / "operator-snapshot"
        manual.mkdir(parents=True)
        (manual / "rule.md").write_text("operator copy", encoding="utf-8")
        self.assertEqual(release_manager.prune_runtime_backups(target), [])
        self.assertTrue(manual.exists())

    def test_rollback_rejects_backup_marker_asset_mismatch(self):
        manifest = self.prepare()
        release_id = json.loads(manifest.read_text(encoding="utf-8"))["release_id"]
        target = self.root / "target"
        self.write_runtime(target / ".mpa/runtime", "old")
        release_manager.deployment_dry_run(argparse.Namespace(manifest=str(manifest), target=str(target), target_ref="target"))
        dry_run = next((release_manager.DEPLOYMENT_RECEIPTS / "target").glob("dry-run-*.json"))
        release_manager.deploy(argparse.Namespace(
            manifest=str(manifest), target=str(target), target_ref="target", verified_by="test",
            dry_run=str(dry_run), approved_by="test", approval_ref="unit", rollback_owner="test"))
        backup = next((target / ".mpa/backups").iterdir())
        data = json.loads((backup / release_manager.BACKUP_MARKER).read_text(encoding="utf-8"))
        data["asset_checksum"] = "0" * 64
        (backup / release_manager.BACKUP_MARKER).write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "asset checksum"):
            release_manager.rollback(argparse.Namespace(
                target=str(target), target_ref="target", backup=str(backup.relative_to(target)), release_id=release_id,
                verified_by="test", approved_by="test", approval_ref="unit", rollback_owner="test"))

    def test_rollback_receipt_failure_restores_applied_runtime(self):
        manifest = self.prepare()
        release_id = json.loads(manifest.read_text(encoding="utf-8"))["release_id"]
        target = self.root / "target"
        self.write_runtime(target / ".mpa/runtime", "old")
        release_manager.deployment_dry_run(argparse.Namespace(manifest=str(manifest), target=str(target), target_ref="target"))
        dry_run = next((release_manager.DEPLOYMENT_RECEIPTS / "target").glob("dry-run-*.json"))
        release_manager.deploy(argparse.Namespace(manifest=str(manifest), target=str(target), target_ref="target", verified_by="test",
                                                  dry_run=str(dry_run), approved_by="test", approval_ref="unit", rollback_owner="test"))
        backup = next((target / ".mpa/backups").iterdir())
        original_write = release_manager.write_json
        def fail_rollback_receipt(path, value):
            if path.parent == release_manager.DEPLOYMENT_RECEIPTS / "target" and value.get("status") == "rolled_back":
                raise OSError("receipt failed")
            return original_write(path, value)
        with mock.patch.object(release_manager, "write_json", side_effect=fail_rollback_receipt):
            with self.assertRaisesRegex(OSError, "receipt failed"):
                release_manager.rollback(argparse.Namespace(target=str(target), target_ref="target", backup=str(backup.relative_to(target)),
                                                          release_id=release_id, verified_by="test", approved_by="test", approval_ref="unit", rollback_owner="test"))
        self.assertEqual((target / ".mpa/runtime" / "rule.md").read_text(encoding="utf-8"), "v1")

    def test_deploy_rejects_repeated_release_history(self):
        manifest = self.prepare()
        target_root = self.root / "target"
        self.write_runtime(target_root / ".mpa/runtime", "old")
        release_manager.deployment_dry_run(argparse.Namespace(manifest=str(manifest), target=str(target_root), target_ref="test-target"))
        dry_run = next((release_manager.DEPLOYMENT_RECEIPTS / "test-target").glob("dry-run-*.json"))
        args = argparse.Namespace(manifest=str(manifest), target=str(target_root), target_ref="test-target", verified_by="test",
                                  dry_run=str(dry_run), approved_by="test", approval_ref="unit", rollback_owner="test")
        release_manager.deploy(args)
        release_manager.deployment_dry_run(argparse.Namespace(manifest=str(manifest), target=str(target_root), target_ref="test-target"))
        args.dry_run = str(max((release_manager.DEPLOYMENT_RECEIPTS / "test-target").glob("dry-run-*.json"), key=lambda path: path.stat().st_mtime_ns))
        with self.assertRaisesRegex(ValueError, "already contains"):
            release_manager.deploy(args)

    def test_failed_release_history_allows_a_new_dry_run_retry(self):
        manifest = self.prepare()
        target = self.root / "target"
        self.write_runtime(target / ".mpa/runtime", "old")
        release_manager.deployment_dry_run(argparse.Namespace(manifest=str(manifest), target=str(target), target_ref="target"))
        first = next((release_manager.DEPLOYMENT_RECEIPTS / "target").glob("dry-run-*.json"))
        args = argparse.Namespace(manifest=str(manifest), target=str(target), target_ref="target", verified_by="test",
                                  dry_run=str(first), approved_by="test", approval_ref="unit", rollback_owner="test")
        with mock.patch.object(release_manager, "verify_target", side_effect=[None, ValueError("verification failed")]):
            with self.assertRaisesRegex(ValueError, "verification failed"):
                release_manager.deploy(args)
        release_manager.deployment_dry_run(argparse.Namespace(manifest=str(manifest), target=str(target), target_ref="target"))
        args.dry_run = str(max((release_manager.DEPLOYMENT_RECEIPTS / "target").glob("dry-run-*.json"), key=lambda path: path.stat().st_mtime_ns))
        release_manager.deploy(args)
        applied = [json.loads(path.read_text()) for path in (release_manager.DEPLOYMENT_RECEIPTS / "target").glob("deploy-*.json")
                   if json.loads(path.read_text()).get("status") == "applied"]
        self.assertEqual(len(applied), 1)
        self.assertEqual(applied[0]["status"], "applied")

    def test_failed_deploy_restores_runtime_and_records_failed_state(self):
        manifest = self.prepare()
        release_id = json.loads(manifest.read_text(encoding="utf-8"))["release_id"]
        target_root = self.root / "target"
        self.write_runtime(target_root / ".mpa/runtime", "old")
        release_manager.deployment_dry_run(argparse.Namespace(manifest=str(manifest), target=str(target_root), target_ref="test-target"))
        dry_run = next((release_manager.DEPLOYMENT_RECEIPTS / "test-target").glob("dry-run-*.json"))
        args = argparse.Namespace(manifest=str(manifest), target=str(target_root), target_ref="test-target", verified_by="test",
                                  dry_run=str(dry_run), approved_by="test", approval_ref="unit", rollback_owner="test")
        with mock.patch.object(release_manager, "verify_target", side_effect=[None, ValueError("verification failed")]):
            with self.assertRaisesRegex(ValueError, "verification failed"):
                release_manager.deploy(args)
        self.assertEqual((target_root / ".mpa/runtime" / "rule.md").read_text(encoding="utf-8"), "old")
        history = json.loads((target_root / ".mpa/runtime" / "history" / "releases" / f"{release_id}.json").read_text(encoding="utf-8"))
        self.assertEqual(history["status"], "failed")
        self.assertTrue(list((release_manager.DEPLOYMENT_RECEIPTS / "test-target").glob("deploy-failed-*.json")))

    def test_deploy_revalidates_target_receipt_and_approval(self):
        manifest = self.prepare()
        target = self.root / "target"
        self.write_runtime(target / ".mpa/runtime", "old")
        release_manager.deployment_dry_run(argparse.Namespace(manifest=str(manifest), target=str(target), target_ref="target"))
        dry_run = next((release_manager.DEPLOYMENT_RECEIPTS / "target").glob("dry-run-*.json"))
        args = argparse.Namespace(manifest=str(manifest), target=str(target), target_ref="target", verified_by="test",
                                  dry_run=str(dry_run), approved_by="", approval_ref="", rollback_owner="")
        with self.assertRaisesRegex(ValueError, "approved-by"):
            release_manager.deploy(args)
        args.approved_by = args.approval_ref = args.rollback_owner = "test"
        data = json.loads(dry_run.read_text(encoding="utf-8"))
        data["release_receipt"] = "workspace/receipts/releases/not-the-release.json"
        dry_run.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "release receipt"):
            release_manager.deploy(args)
        release_manager.deployment_dry_run(argparse.Namespace(manifest=str(manifest), target=str(target), target_ref="target"))
        args.dry_run = str(max((release_manager.DEPLOYMENT_RECEIPTS / "target").glob("dry-run-*.json"), key=lambda path: path.stat().st_mtime_ns))
        (target / ".mpa/runtime" / "unexpected.md").write_text("changed", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "target changed"):
            release_manager.deploy(args)

    def test_sync_prunes_only_runtime_destination_and_ignores_generated_files(self):
        self.write_runtime(release_manager.RUNTIME_DIST, "stale")
        (release_manager.RUNTIME_DIST / "obsolete.md").write_text("obsolete", encoding="utf-8")
        (release_manager.RUNTIME_SOURCE / "__pycache__").mkdir()
        (release_manager.RUNTIME_SOURCE / "__pycache__" / "rule.pyc").write_bytes(b"cache")
        outside = self.root / "dist" / "workspace" / "keep.md"
        outside.parent.mkdir(parents=True)
        outside.write_text("keep", encoding="utf-8")

        release_manager.sync_runtime(argparse.Namespace())

        self.assertFalse((release_manager.RUNTIME_DIST / "obsolete.md").exists())
        self.assertFalse((release_manager.RUNTIME_DIST / "__pycache__").exists())
        self.assertEqual(outside.read_text(encoding="utf-8"), "keep")

    def test_target_ref_and_rollback_backup_scope_are_restricted(self):
        manifest = self.prepare()
        target_root = self.root / "target"
        self.write_runtime(target_root / ".mpa/runtime", "old")
        with self.assertRaisesRegex(ValueError, "target-ref"):
            release_manager.deploy(argparse.Namespace(
                manifest=str(manifest), target=str(target_root), target_ref="../escape", verified_by="test",
                dry_run="unused", approved_by="test", approval_ref="unit", rollback_owner="test",
            ))
        with self.assertRaisesRegex(ValueError, "backup must be inside"):
            release_manager.rollback(argparse.Namespace(
                target=str(target_root), target_ref="test-target", backup=".mpa/runtime",
            ))

    def test_repeated_preparation_creates_distinct_immutable_release_ids(self):
        manifest = self.prepare()
        original = json.loads(manifest.read_text(encoding="utf-8"))
        (release_manager.RUNTIME_SOURCE / "rule.md").write_text("v2", encoding="utf-8")
        self.prepare()

        manifests = list(release_manager.RELEASES.glob("*/manifest_*.json"))
        self.assertEqual(len(manifests), 2)
        self.assertNotEqual(json.loads(manifests[0].read_text(encoding="utf-8"))["release_id"],
                            json.loads(manifests[1].read_text(encoding="utf-8"))["release_id"])
        original_package = release_manager.RELEASES / original["release_id"] / f"package_{original['release_id']}.zip"
        self.assertEqual(original["release_id"], release_manager._archive_current_release(original_package))
        self.assertEqual(len(list(release_manager.RELEASES.glob("*/release-receipt_*.json"))), 2)

    def test_release_id_is_the_only_runtime_identity_and_checksum_is_evidence(self):
        manifest = self.prepare()
        data = json.loads(manifest.read_text(encoding="utf-8"))
        self.assertRegex(data["release_id"], r"^\d{14}-[0-9a-f]{8}$")
        self.assertNotIn("runtime_version", data)
        self.assertIn("asset_checksum", data)
        release_id = data["release_id"]
        self.assertEqual(manifest.name, f"manifest_{release_id}.json")
        self.assertEqual(manifest.parent.name, release_id)
        self.assertTrue((manifest.parent / f"package_{release_id}.zip").is_file())
        self.assertTrue((manifest.parent / f"note_{release_id}.md").is_file())
        self.assertTrue((manifest.parent / f"release-receipt_{release_id}.json").is_file())
        self.assertEqual(release_manager.current_release(release_manager.RUNTIME_SOURCE), data["release_id"])
        self.assertEqual(release_manager.current_release(release_manager.RUNTIME_DIST), data["release_id"])

    def test_release_audit_verifies_zip_and_bundle_inventory(self):
        manifest = self.prepare()
        release_manager.audit_releases(argparse.Namespace())
        data = json.loads(manifest.read_text(encoding="utf-8"))
        package = manifest.parent / f"package_{data['release_id']}.zip"
        package.write_bytes(package.read_bytes() + b"tampered")
        with self.assertRaisesRegex(ValueError, "invalid release artifacts"):
            release_manager.audit_releases(argparse.Namespace())

    def test_update_collects_issues_only_after_runtime_verification(self):
        manifest = self.prepare()
        target = self.root / "target"
        self.write_runtime(target / ".mpa/runtime", "old")
        issue = target / "workspace" / "issues" / "issue.md"
        issue.parent.mkdir(parents=True)
        issue.write_text(release_manager.issue_text("test", "summary", "methodology_improvement"), encoding="utf-8")
        release_manager.deployment_dry_run(argparse.Namespace(manifest=str(manifest), target=str(target), target_ref="target"))
        dry_run = next((release_manager.DEPLOYMENT_RECEIPTS / "target").glob("dry-run-*.json"))
        release_manager.deploy(argparse.Namespace(manifest=str(manifest), target=str(target), target_ref="target", verified_by="test",
                                                  dry_run=str(dry_run), approved_by="test", approval_ref="unit", rollback_owner="test"))
        self.assertFalse(issue.exists())
        self.assertTrue((release_manager.ISSUES / "inbox" / "target" / "issue.md").is_file())
        self.assertFalse((release_manager.WORKSPACE / "receipts" / "issues").exists())

    def test_update_issue_change_after_dry_run_preserves_source(self):
        manifest = self.prepare()
        target = self.root / "target"
        self.write_runtime(target / ".mpa/runtime", "old")
        issue = target / "workspace" / "issues" / "issue.md"
        issue.parent.mkdir(parents=True)
        issue.write_text(release_manager.issue_text("test", "summary", "methodology_improvement"), encoding="utf-8")
        release_manager.deployment_dry_run(argparse.Namespace(manifest=str(manifest), target=str(target), target_ref="target"))
        dry_run = next((release_manager.DEPLOYMENT_RECEIPTS / "target").glob("dry-run-*.json"))
        issue.write_text(release_manager.issue_text("changed", "summary", "methodology_improvement"), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "issues changed"):
            release_manager.deploy(argparse.Namespace(manifest=str(manifest), target=str(target), target_ref="target", verified_by="test",
                                                      dry_run=str(dry_run), approved_by="test", approval_ref="unit", rollback_owner="test"))
        self.assertTrue(issue.exists())

    def test_release_allows_scoped_dirty_or_no_git_source(self):
        release_manager.sync_runtime(argparse.Namespace())
        args = argparse.Namespace(verified_by="test", compatibility="compatible", breaking_change="none", migration="none",
                                  rollback_condition="verification failure", release_note="test release",
                                  validation_command=[sys.executable, "-c", "print('ok')"])
        with mock.patch.object(release_manager, "scoped_git", return_value={"status": "available", "head": "abc", "scoped_diff": ["M\trelease_manager.py"]}):
            release_manager.prepare_release(args)
        manifest = next(release_manager.RELEASES.glob("*/manifest_*.json"))
        self.assertEqual(json.loads(manifest.read_text(encoding="utf-8"))["source_git"]["scoped_diff"], ["M\trelease_manager.py"])
        self.assertEqual(release_manager.scoped_git()["status"], "unavailable")

    def test_failed_validation_creates_no_release_artifacts(self):
        release_manager.sync_runtime(argparse.Namespace())
        with self.assertRaisesRegex(ValueError, "validation command failed"):
            release_manager.prepare_release(argparse.Namespace(
                verified_by="test", compatibility="compatible", breaking_change="none", migration="none",
                rollback_condition="verification failure", release_note="test release",
                validation_command=[sys.executable, "-c", "raise SystemExit(1)"],
            ))
        self.assertFalse(list(release_manager._release_bundle_dirs()))

    def test_timeout_and_manifest_write_failure_leave_no_release_artifacts(self):
        release_manager.sync_runtime(argparse.Namespace())
        original_release = release_manager.current_release(release_manager.RUNTIME_SOURCE)
        arguments = argparse.Namespace(
            verified_by="test", compatibility="compatible", breaking_change="none", migration="none",
            rollback_condition="verification failure", release_note="test release",
            validation_command=[sys.executable, "-c", "print('ok')"],
        )
        with mock.patch.object(release_manager.subprocess, "run", side_effect=subprocess.TimeoutExpired(["test"], 1)):
            with self.assertRaisesRegex(ValueError, "timed out"):
                release_manager.prepare_release(arguments)
        self.assertFalse(list(release_manager._release_bundle_dirs()))
        original_write = release_manager.write_json
        def fail_manifest(path, value):
            if path.name.startswith("manifest_"):
                raise OSError("manifest write failed")
            return original_write(path, value)
        with mock.patch.object(release_manager, "write_json", side_effect=fail_manifest):
            with self.assertRaisesRegex(OSError, "manifest write failed"):
                release_manager.prepare_release(arguments)
        self.assertFalse(list(release_manager._release_bundle_dirs()))
        self.assertFalse(list(release_manager.RELEASES.glob("*/package_*.zip")))
        self.assertFalse(list(release_manager.RELEASES.glob("*/release-receipt_*.json")))
        self.assertEqual(release_manager.current_release(release_manager.RUNTIME_SOURCE), original_release)
        self.assertEqual(release_manager.current_release(release_manager.RUNTIME_DIST), original_release)

    def test_deploy_legacy_current_version_records_a_single_legacy_origin(self):
        manifest = self.prepare()
        target = self.root / "legacy-target"
        target_runtime = target / ".mpa/runtime"
        target_runtime.mkdir(parents=True)
        (target_runtime / ".mpa-version").write_text("current_version: 2026-08-12 12:06:00\n", encoding="utf-8")
        (target_runtime / "rule.md").write_text("legacy", encoding="utf-8")
        release_manager.deployment_dry_run(argparse.Namespace(manifest=str(manifest), target=str(target), target_ref="legacy-target"))
        dry_run = next((release_manager.DEPLOYMENT_RECEIPTS / "legacy-target").glob("dry-run-*.json"))
        dry_data = json.loads(dry_run.read_text(encoding="utf-8"))
        self.assertEqual(dry_data["from_release"], "legacy-2026-08-12-12-06-00")
        release_manager.deploy(argparse.Namespace(manifest=str(manifest), target=str(target), target_ref="legacy-target", verified_by="test",
                                                  dry_run=str(dry_run), approved_by="test", approval_ref="unit", rollback_owner="test"))
        self.assertEqual(release_manager.current_release(target_runtime), json.loads(manifest.read_text(encoding="utf-8"))["release_id"])

    def test_empty_metadata_creates_nothing_and_audit_rejects_missing_package(self):
        release_manager.sync_runtime(argparse.Namespace())
        args = argparse.Namespace(verified_by="test", compatibility="", breaking_change="none", migration="none",
                                  rollback_condition="verification failure", release_note="test release",
                                  validation_command=[sys.executable, "-c", "print('ok')"])
        with self.assertRaisesRegex(ValueError, "metadata"):
            release_manager.prepare_release(args)
        self.assertFalse(list(release_manager._release_bundle_dirs()))
        manifest = self.prepare()
        release_id = json.loads(manifest.read_text(encoding="utf-8"))["release_id"]
        (release_manager.RELEASES / release_id / f"package_{release_id}.zip").unlink()
        with self.assertRaisesRegex(ValueError, "invalid release artifacts"):
            release_manager.audit_releases(argparse.Namespace())

    def test_rejected_issue_records_reason_and_archives_without_a_receipt(self):
        issue = release_manager.ISSUES / "inbox" / "test-project" / "issue.md"
        issue.parent.mkdir(parents=True)
        issue.write_text(release_manager.issue_text("test", "summary", "methodology_improvement"), encoding="utf-8")
        release_manager.archive_issue(argparse.Namespace(
            issue="test-project/issue.md", decision="rejected", decided_by="user",
            reason="global rule value is too low", task=None,
        ))
        archived = next((release_manager.ISSUES / "archived").rglob("issue.md"))
        metadata, body = release_manager.read_issue(archived)
        self.assertEqual(metadata["status"], "archived")
        self.assertEqual(metadata["decision"], "rejected")
        self.assertEqual(metadata["decision_reason"], "global rule value is too low")
        self.assertIsNone(metadata["follow_up_task"])
        self.assertIn("## 처리 결과", body)
        self.assertFalse((release_manager.WORKSPACE / "receipts" / "issues").exists())

    def test_accepted_issue_requires_existing_task_plan_and_archives_with_link(self):
        issue = release_manager.ISSUES / "inbox" / "test-project" / "issue.md"
        issue.parent.mkdir(parents=True)
        issue.write_text(release_manager.issue_text("test", "summary", "methodology_improvement"), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "active workspace task plan"):
            release_manager.archive_issue(argparse.Namespace(
                issue="test-project/issue.md", decision="accepted", decided_by="user",
                reason="create a task", task="workspace/tasks/active/missing/plan.md",
            ))
        done_plan = release_manager.WORKSPACE / "tasks" / "done" / "task-0" / "plan.md"
        done_plan.parent.mkdir(parents=True)
        done_plan.write_text("# completed task\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "active workspace task plan"):
            release_manager.archive_issue(argparse.Namespace(
                issue="test-project/issue.md", decision="accepted", decided_by="user",
                reason="must create a new task", task=str(done_plan.relative_to(release_manager.ROOT)),
            ))
        plan = release_manager.WORKSPACE / "tasks" / "active" / "task-1" / "plan.md"
        plan.parent.mkdir(parents=True)
        plan.write_text("# task\n", encoding="utf-8")
        release_manager.archive_issue(argparse.Namespace(
            issue="test-project/issue.md", decision="accepted", decided_by="user",
            reason="create a task", task=str(plan.relative_to(release_manager.ROOT)),
        ))
        archived = next((release_manager.ISSUES / "archived").rglob("issue.md"))
        metadata, _ = release_manager.read_issue(archived)
        self.assertEqual(metadata["decision"], "accepted")
        self.assertEqual(metadata["follow_up_task"], str(plan.relative_to(release_manager.ROOT)))

    def test_archive_write_failure_restores_open_issue(self):
        issue = release_manager.ISSUES / "inbox" / "test-project" / "issue.md"
        issue.parent.mkdir(parents=True)
        issue.write_text(release_manager.issue_text("test", "summary", "methodology_improvement"), encoding="utf-8")
        original = issue.read_text(encoding="utf-8")
        with mock.patch.object(release_manager, "write_issue", side_effect=OSError("write failed")):
            with self.assertRaisesRegex(OSError, "write failed"):
                release_manager.archive_issue(argparse.Namespace(
                    issue="test-project/issue.md", decision="rejected", decided_by="user",
                    reason="not applicable", task=None,
                ))
        self.assertEqual(issue.read_text(encoding="utf-8"), original)
        self.assertFalse(list((release_manager.ISSUES / "archived").rglob("issue.md")))

    def test_cross_filesystem_move_keeps_source_when_unlink_fails(self):
        source = self.root / "source.md"
        destination = self.root / "destination.md"
        source.write_text("issue", encoding="utf-8")
        original_replace = Path.replace
        original_unlink = Path.unlink
        def cross_device_replace(path, target):
            if path == source:
                raise OSError(errno.EXDEV, "cross-device")
            return original_replace(path, target)
        def failing_unlink(path, *args, **kwargs):
            if path == source:
                raise OSError("unlink failed")
            return original_unlink(path, *args, **kwargs)
        with mock.patch.object(Path, "replace", new=cross_device_replace), mock.patch.object(Path, "unlink", new=failing_unlink):
            with self.assertRaisesRegex(OSError, "unlink failed"):
                release_manager.move_issue_atomically(source, destination)
        self.assertTrue(source.exists())
        self.assertFalse(destination.exists())

    def test_collect_confirms_destination_and_source_removal_without_receipt(self):
        project = self.root / "project"
        source = project / "workspace" / "issues" / "issue.md"
        source.parent.mkdir(parents=True)
        source.write_text(release_manager.issue_text("test", "summary", "methodology_improvement"), encoding="utf-8")
        release_manager.collect_issue(argparse.Namespace(project=str(project), project_ref="project", issue="issue.md"))
        self.assertFalse(source.exists())
        self.assertTrue((release_manager.ISSUES / "inbox" / "project" / "issue.md").is_file())
        self.assertFalse((release_manager.WORKSPACE / "receipts" / "issues").exists())

    def test_create_issue_rejects_sensitive_content_before_writing(self):
        project = self.root / "project"
        with self.assertRaisesRegex(ValueError, "credential-like"):
            release_manager.create_issue(argparse.Namespace(
                project=str(project), title="leak", summary="api_key: super-secret", kind="observation",
                key="sensitive", occurrence="first_observed", area="runtime",
                observed_release="unknown", collection_purpose="review"))
        self.assertFalse(list((project / "workspace" / "issues").glob("*.md")))

    def test_collect_verification_failure_restores_project_issue(self):
        project = self.root / "project"
        source = project / "workspace" / "issues" / "issue.md"
        source.parent.mkdir(parents=True)
        source.write_text(release_manager.issue_text("test", "summary", "methodology_improvement"), encoding="utf-8")
        with mock.patch.object(release_manager, "confirm_issue_move", side_effect=OSError("verification failed")):
            with self.assertRaisesRegex(OSError, "verification failed"):
                release_manager.collect_issue(argparse.Namespace(project=str(project), project_ref="project", issue=source.name))
        self.assertTrue(source.exists())
        self.assertFalse((release_manager.ISSUES / "inbox" / "project" / "issue.md").exists())

    def test_collect_source_delete_failure_removes_verified_destination(self):
        project = self.root / "project"
        source = project / "workspace" / "issues" / "issue.md"
        source.parent.mkdir(parents=True)
        source.write_text(release_manager.issue_text("test", "summary", "methodology_improvement"), encoding="utf-8")
        destination = release_manager.ISSUES / "inbox" / "project" / "issue.md"
        with mock.patch.object(release_manager, "delete_issue_source", side_effect=OSError("source deletion failed")):
            with self.assertRaisesRegex(OSError, "source deletion failed"):
                release_manager.collect_issue(argparse.Namespace(project=str(project), project_ref="project", issue=source.name))
        self.assertTrue(source.is_file())
        self.assertFalse(destination.exists())

    def test_collect_destination_race_preserves_existing_destination_and_source(self):
        project = self.root / "project"
        source = project / "workspace" / "issues" / "issue.md"
        source.parent.mkdir(parents=True)
        source.write_text(release_manager.issue_text("source", "summary", "methodology_improvement"), encoding="utf-8")
        destination = release_manager.ISSUES / "inbox" / "project" / "issue.md"
        original_link = os.link

        def create_destination_then_link(temporary, actual_destination):
            Path(actual_destination).write_text("existing destination", encoding="utf-8")
            return original_link(temporary, actual_destination)

        with mock.patch.object(release_manager.os, "link", side_effect=create_destination_then_link):
            with self.assertRaises(FileExistsError):
                release_manager.collect_issue(argparse.Namespace(project=str(project), project_ref="project", issue=source.name))
        self.assertTrue(source.is_file())
        self.assertEqual(destination.read_text(encoding="utf-8"), "existing destination")

    def test_collect_temporary_cleanup_failure_removes_destination_and_preserves_source(self):
        project = self.root / "project"
        source = project / "workspace" / "issues" / "issue.md"
        source.parent.mkdir(parents=True)
        source.write_text(release_manager.issue_text("source", "summary", "methodology_improvement"), encoding="utf-8")
        destination = release_manager.ISSUES / "inbox" / "project" / "issue.md"
        original_unlink = Path.unlink
        failed_once = False

        def fail_first_temporary_unlink(path, *args, **kwargs):
            nonlocal failed_once
            if path.name.startswith(".issue.md.new-") and not failed_once:
                failed_once = True
                raise OSError("temporary cleanup failed")
            return original_unlink(path, *args, **kwargs)

        with mock.patch.object(Path, "unlink", new=fail_first_temporary_unlink):
            with self.assertRaisesRegex(OSError, "temporary cleanup failed"):
                release_manager.collect_issue(argparse.Namespace(project=str(project), project_ref="project", issue=source.name))
        self.assertTrue(source.is_file())
        self.assertFalse(destination.exists())

    def test_collect_source_reappearance_preserves_both_files_for_reconciliation(self):
        project = self.root / "project"
        source = project / "workspace" / "issues" / "issue.md"
        source.parent.mkdir(parents=True)
        source.write_text(release_manager.issue_text("original", "summary", "methodology_improvement"), encoding="utf-8")
        destination = release_manager.ISSUES / "inbox" / "project" / "issue.md"
        original_confirm = release_manager.confirm_issue_move

        def reappear_then_confirm(actual_source, actual_destination):
            actual_source.write_text(release_manager.issue_text("new observation", "summary", "methodology_improvement"), encoding="utf-8")
            return original_confirm(actual_source, actual_destination)

        with mock.patch.object(release_manager, "confirm_issue_move", side_effect=reappear_then_confirm):
            with self.assertRaisesRegex(OSError, "source reappeared"):
                release_manager.collect_issue(argparse.Namespace(project=str(project), project_ref="project", issue=source.name))
        self.assertTrue(source.is_file())
        self.assertTrue(destination.is_file())
        self.assertIn("new observation", source.read_text(encoding="utf-8"))
        self.assertIn("original", destination.read_text(encoding="utf-8"))

    def test_deploy_collection_failure_restores_runtime_and_issue(self):
        manifest = self.prepare()
        target = self.root / "target"
        self.write_runtime(target / ".mpa/runtime", "old")
        issue = target / "workspace" / "issues" / "issue.md"
        issue.parent.mkdir(parents=True)
        issue.write_text(release_manager.issue_text("test", "summary", "methodology_improvement"), encoding="utf-8")
        release_manager.deployment_dry_run(argparse.Namespace(manifest=str(manifest), target=str(target), target_ref="target"))
        dry_run = next((release_manager.DEPLOYMENT_RECEIPTS / "target").glob("dry-run-*.json"))
        original_write = release_manager.write_json
        def fail_deploy_receipt(path, value):
            if path.parent == release_manager.DEPLOYMENT_RECEIPTS / "target" and path.name.startswith("deploy-"):
                raise OSError("deployment receipt failed")
            return original_write(path, value)
        with mock.patch.object(release_manager, "write_json", side_effect=fail_deploy_receipt):
            with self.assertRaisesRegex(OSError, "deployment receipt failed"):
                release_manager.deploy(argparse.Namespace(
                    manifest=str(manifest), target=str(target), target_ref="target", verified_by="test",
                    dry_run=str(dry_run), approved_by="test", approval_ref="unit", rollback_owner="test"))
        self.assertEqual((target / ".mpa/runtime" / "rule.md").read_text(encoding="utf-8"), "old")
        self.assertTrue(issue.exists())
        self.assertFalse((release_manager.ISSUES / "inbox" / "target" / issue.name).exists())

    def test_duplicate_archive_blocks_collection_and_preserves_project_issue(self):
        project = self.root / "project"
        source = project / "workspace" / "issues" / "issue.md"
        source.parent.mkdir(parents=True)
        source.write_text(release_manager.issue_text("test", "summary", "methodology_improvement"), encoding="utf-8")
        archived = release_manager.ISSUES / "archived" / "2026" / "08" / "project" / source.name
        archived.parent.mkdir(parents=True)
        archived.write_text(release_manager.issue_text("old", "summary", "methodology_improvement"), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "already exists"):
            release_manager.collect_issue(argparse.Namespace(project=str(project), project_ref="project", issue=source.name))
        self.assertTrue(source.exists())
        self.assertFalse((release_manager.ISSUES / "inbox" / "project" / source.name).exists())

    def test_collection_rejects_project_issue_path_escape(self):
        project = self.root / "project"
        (project / "workspace" / "issues").mkdir(parents=True)
        outside = project / "outside.md"
        outside.write_text(release_manager.issue_text("test", "summary", "methodology_improvement"), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "specified issue"):
            release_manager.collect_issue(argparse.Namespace(project=str(project), project_ref="project", issue="../../outside.md"))

    def test_audit_rejects_orphan_active_package_or_receipt(self):
        orphan = release_manager.RELEASES / "orphan"
        orphan.mkdir(parents=True)
        (orphan / "package_orphan.zip").write_bytes(b"orphan")
        with self.assertRaisesRegex(ValueError, "bundle file inventory"):
            release_manager.audit_releases(argparse.Namespace())

    def test_collection_and_accepted_task_archive_preserve_issue_identity(self):
        project = self.root / "project"
        release_manager.create_issue(argparse.Namespace(project=str(project), title="test", summary="summary", kind="methodology_improvement",
                                                        key="methodology-improvement", occurrence="first_observed", area="release",
                                                        observed_release="unknown", collection_purpose="improve"))
        source = next((project / "workspace" / "issues").glob("*.md"))
        release_manager.collect_issue(argparse.Namespace(project=str(project), project_ref="project", issue=source.name))
        issue = f"project/{source.name}"
        plan = release_manager.WORKSPACE / "tasks" / "active" / "task-1" / "plan.md"
        plan.parent.mkdir(parents=True)
        plan.write_text("# task\n", encoding="utf-8")
        release_manager.archive_issue(argparse.Namespace(
            issue=issue, decision="accepted", decided_by="user", reason="approved for implementation",
            task=str(plan.relative_to(release_manager.ROOT)),
        ))
        self.assertFalse((release_manager.ISSUES / "inbox" / issue).exists())
        archived = next((release_manager.ISSUES / "archived").rglob(source.name))
        metadata, _ = release_manager.read_issue(archived)
        self.assertEqual(metadata["source_issue_id"], source.stem)
        self.assertEqual(metadata["decision"], "accepted")


if __name__ == "__main__":
    unittest.main()
