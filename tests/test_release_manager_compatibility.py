"""Compatibility contracts that must survive release_manager internal extraction."""

import importlib.util
import os
import argparse
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from typing import Optional
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "release_manager.py"


def load_release_manager(name: str):
    spec = importlib.util.spec_from_file_location(name, MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ReleaseManagerCompatibilityTest(unittest.TestCase):
    @staticmethod
    def write_runtime(path: Path, version: str) -> None:
        path.mkdir(parents=True, exist_ok=True)
        (path / ".mpa-version").write_text(f"current_release: {version}\n", encoding="utf-8")
        (path / "rule.md").write_text(version, encoding="utf-8")
        hooks = path / "hooks"
        hooks.mkdir(exist_ok=True)
        for name in ("session_start.py", "code_gate.py"):
            (hooks / name).write_text("import argparse\nargparse.ArgumentParser()\n", encoding="utf-8")

    def prepare_isolated_release(self, module, root: Path, runtime_config: Optional[dict] = None) -> Path:
        """Build one small immutable package without touching the workspace."""
        module.ROOT = root
        module.RUNTIME_SOURCE = root / ".mpa/runtime"
        module.RUNTIME_DIST = root / "dist/.mpa/runtime"
        module.WORKSPACE = root / "workspace"
        module.RELEASES = module.WORKSPACE / "releases"
        module.MANIFESTS = module.RELEASES
        module.PACKAGES = module.RELEASES
        module.RELEASE_RECEIPTS = module.RELEASES
        module.LEGACY_RELEASES = module.RELEASES / "legacy"
        module.LEGACY_ACTIVE_MANIFESTS = module.RELEASES / "manifests"
        module.LEGACY_ACTIVE_PACKAGES = module.RELEASES / "packages"
        module.LEGACY_ACTIVE_RECEIPTS = module.WORKSPACE / "receipts/releases"
        module.DEPLOYMENT_RECEIPTS = module.WORKSPACE / ".local/receipts/deployments"
        module.ISSUES = module.WORKSPACE / "issues"
        self.write_runtime(module.RUNTIME_SOURCE, "v1")
        with mock.patch.object(
            module,
            "run_release_preflight",
            return_value={"command": ["release-preflight"], "exit_code": 0, "steps": [], "executed_at": "test"},
        ):
            module.sync_runtime(argparse.Namespace())
            arguments = argparse.Namespace(
                verified_by="test", compatibility="compatible", breaking_change="none", migration="none",
                rollback_condition="verification failure", release_note="test release",
                validation_command=[sys.executable, "-c", "print('ok')"], allow_version_only=False,
            )
            if runtime_config is not None:
                migration = root / "runtime-config.json"
                migration.write_text(json.dumps(runtime_config), encoding="utf-8")
                arguments.runtime_config_json = str(migration)
            module.prepare_release(arguments)
        return next(module.RELEASES.glob("*/manifest_*.json"))

    def test_source_root_spec_loader_and_cli_help_work_outside_repository(self):
        """Keep the established source-root import contract outside the repository cwd.

        ``release_manager.py`` has always imported ``project_config`` from this
        source tree; loading it by path is supported when that source root is on
        Python's import path.  This subprocess also proves the new source-only
        ``mpa_ops`` package resolves under that same public contract.
        """
        loader = """
import importlib.util
import pathlib
import sys
path = pathlib.Path(sys.argv[1])
spec = importlib.util.spec_from_file_location('legacy_release_manager', path)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)
assert module.ROOT == path.parent
"""
        with tempfile.TemporaryDirectory() as directory:
            environment = os.environ.copy()
            environment["PYTHONPATH"] = str(ROOT)
            loaded = subprocess.run(
                [sys.executable, "-c", loader, str(MODULE_PATH)],
                cwd=directory,
                text=True,
                capture_output=True,
                env=environment,
                check=False,
            )
            self.assertEqual(loaded.returncode, 0, loaded.stderr)
            result = subprocess.run(
                [sys.executable, str(MODULE_PATH), "--help"],
                cwd=directory,
                text=True,
                capture_output=True,
                env=environment,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("prepare-release", result.stdout)
        self.assertIn("deployment-dry-run", result.stdout)

    def test_archive_extraction_keeps_facade_member_validator_patchable(self):
        module = load_release_manager("release_manager_archive_patch")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = root / "runtime.zip"
            destination = root / "staging"
            with zipfile.ZipFile(archive, "w") as output:
                output.writestr("rule.md", "rule")
            with mock.patch.object(module, "_validate_zip_member", side_effect=ValueError("injected")) as validator:
                with self.assertRaisesRegex(ValueError, "extraction failed"):
                    module._extract_runtime(archive, destination)
            validator.assert_called_once_with("rule.md")
            self.assertFalse(destination.exists())

    def test_issue_rendering_keeps_facade_parser_patchable(self):
        module = load_release_manager("release_manager_issue_patch")
        source = Path("issue.md")
        text = "**타입**: 방법론 개선\n내용"
        with mock.patch.object(
            module,
            "_parse_issue_candidate",
            return_value=(module.METHODOLOGY_KIND, {"type": "issue"}, "내용"),
        ) as parser:
            self.assertEqual(module.render_collected_issue(source, text, Path("project")), text)
        parser.assert_called_once_with(text)

    def test_all_legacy_facades_dispatch_to_source_only_helpers(self):
        """Keep every extracted helper name patchable on release_manager."""
        module = load_release_manager("release_manager_all_facades")
        source = Path("source")
        destination = Path("destination.zip")
        text = "text"
        project_root = Path("project")
        metadata = {"source_issue_id": "source"}
        cases = (
            ("_zip_runtime", module.archive_io, "zip_runtime", (source, destination), False),
            ("_write_backup_archive", module.archive_io, "write_backup_archive", (source, destination), False),
            ("_zip_entries", module.archive_io, "zip_entries", (destination,), True),
            ("_validate_zip_member", module.archive_io, "validate_zip_member", ("rule.md",), False),
            ("_archive_current_release", module.archive_io, "archive_current_release", (destination,), True),
            ("_extract_runtime", module.archive_io, "extract_runtime", (destination, source), False),
            ("_parse_issue_candidate", module.issue_format, "parse_issue_candidate", (text,), True),
            ("_candidate_metadata_is_complete", module.issue_format, "candidate_metadata_is_complete", (metadata,), True),
            ("normalize_issue_machine_paths", module.issue_format, "normalize_machine_paths", (text, project_root), True),
            ("normalize_issue_identity_paths", module.issue_format, "normalize_identity_paths", (text,), True),
            ("_metadata_identity", module.issue_format, "metadata_identity", (metadata,), True),
        )
        for facade, helper_module, helper_name, arguments, returns_value in cases:
            with self.subTest(facade=facade):
                sentinel = object()
                with mock.patch.object(helper_module, helper_name, return_value=sentinel) as helper:
                    result = getattr(module, facade)(*arguments)
                if returns_value:
                    self.assertIs(result, sentinel)
                else:
                    self.assertIsNone(result)
                self.assertEqual(helper.call_args.args, arguments)

        # Facades supply the policy values that keep existing patches meaningful.
        with mock.patch.object(module.archive_io, "zip_runtime") as helper:
            module._zip_runtime(source, destination)
        self.assertIs(helper.call_args.kwargs["validate_tree"], module.assert_safe_runtime_tree)
        self.assertEqual(helper.call_args.kwargs["ignored_names"], module.IGNORED_RUNTIME_NAMES)
        with mock.patch.object(module.archive_io, "extract_runtime") as helper:
            module._extract_runtime(destination, source)
        self.assertIs(helper.call_args.kwargs["validate_member"], module._validate_zip_member)

    def test_prepared_runtime_artifact_excludes_source_only_operations_package(self):
        module = load_release_manager("release_manager_package_boundary")
        with tempfile.TemporaryDirectory() as directory:
            manifest = self.prepare_isolated_release(module, Path(directory))
            data = json.loads(manifest.read_text(encoding="utf-8"))
            package = module.ROOT / data["package"]
            with zipfile.ZipFile(package) as archive:
                members = archive.namelist()
            self.assertFalse(any(name.startswith("mpa_ops/") for name in members))
            self.assertFalse(any(name.startswith("workspace/") for name in members))
            self.assertFalse(any("MAP_PRODUCT_RULES" in name for name in members))
            self.assertTrue(all(not name.startswith("mpa_ops/") for name in data["assets"]))

    def test_deploy_recovers_when_backup_zip_leaf_fails(self):
        module = load_release_manager("release_manager_deploy_leaf_failure")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = self.prepare_isolated_release(module, root)
            target = root / "target"
            self.write_runtime(target / ".mpa/runtime", "old")
            issue = target / "workspace/issues/issue.md"
            issue.parent.mkdir(parents=True)
            issue.write_text(module.issue_text("issue", "body", module.METHODOLOGY_KIND), encoding="utf-8")
            module.deployment_dry_run(argparse.Namespace(manifest=str(manifest), target=str(target), target_ref="target"))
            dry_run = next((module.DEPLOYMENT_RECEIPTS / "target").glob("dry-run-*.json"))
            with mock.patch.object(module.archive_io, "write_backup_archive", side_effect=OSError("zip leaf failed")):
                with self.assertRaisesRegex(OSError, "zip leaf failed"):
                    module.deploy(argparse.Namespace(
                        manifest=str(manifest), target=str(target), target_ref="target", verified_by="test",
                        dry_run=str(dry_run), approved_by="test", approval_ref="unit", operator="test",
                    ))
            self.assertEqual((target / ".mpa/runtime/rule.md").read_text(encoding="utf-8"), "old")
            self.assertTrue(issue.is_file())
            self.assertTrue(list((module.DEPLOYMENT_RECEIPTS / "target").glob("deploy-failed-*.json")))

    def test_deploy_leaf_failure_restores_runtime_config_snapshot(self):
        module = load_release_manager("release_manager_deploy_config_leaf_failure")
        migration = {"schema_version": 2, "additive_defaults": {"runtime.root_path": "${project.root_path}"}}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = self.prepare_isolated_release(module, root, migration)
            target = root / "target"
            self.write_runtime(target / ".mpa/runtime", "old")
            config = target / ".mpa/config/config.yaml"
            config.parent.mkdir(parents=True)
            config.write_text('runtime:\n  project_name: "kept"\n', encoding="utf-8")
            original_config = config.read_text(encoding="utf-8")
            module.deployment_dry_run(argparse.Namespace(manifest=str(manifest), target=str(target), target_ref="target"))
            dry_run = next((module.DEPLOYMENT_RECEIPTS / "target").glob("dry-run-*.json"))
            with mock.patch.object(module.archive_io, "write_backup_archive", side_effect=OSError("zip leaf failed")):
                with self.assertRaisesRegex(OSError, "zip leaf failed"):
                    module.deploy(argparse.Namespace(
                        manifest=str(manifest), target=str(target), target_ref="target", verified_by="test",
                        dry_run=str(dry_run), approved_by="test", approval_ref="unit", operator="test",
                    ))
            self.assertEqual((target / ".mpa/runtime/rule.md").read_text(encoding="utf-8"), "old")
            self.assertEqual(config.read_text(encoding="utf-8"), original_config)
            self.assertTrue(list((module.DEPLOYMENT_RECEIPTS / "target").glob("deploy-failed-*.json")))

    def test_rollback_recovers_when_backup_extraction_leaf_fails(self):
        module = load_release_manager("release_manager_rollback_leaf_failure")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = self.prepare_isolated_release(module, root)
            release_id = json.loads(manifest.read_text(encoding="utf-8"))["release_id"]
            target = root / "target"
            self.write_runtime(target / ".mpa/runtime", "old")
            module.deployment_dry_run(argparse.Namespace(manifest=str(manifest), target=str(target), target_ref="target"))
            dry_run = next((module.DEPLOYMENT_RECEIPTS / "target").glob("dry-run-*.json"))
            module.deploy(argparse.Namespace(
                manifest=str(manifest), target=str(target), target_ref="target", verified_by="test",
                dry_run=str(dry_run), approved_by="test", approval_ref="unit", operator="test",
            ))
            backup = next((target / ".mpa/backups").iterdir())
            with mock.patch.object(module.archive_io, "extract_runtime", side_effect=OSError("extract leaf failed")):
                with self.assertRaisesRegex(OSError, "extract leaf failed"):
                    module.rollback(argparse.Namespace(
                        target=str(target), target_ref="target", backup=str(backup.relative_to(target)),
                        release_id=release_id, verified_by="test", approved_by="test", approval_ref="unit", operator="test",
                    ))
            self.assertEqual((target / ".mpa/runtime/rule.md").read_text(encoding="utf-8"), "v1")
            self.assertTrue(list((module.DEPLOYMENT_RECEIPTS / "target").glob("rollback-failed-*.json")))


if __name__ == "__main__":
    unittest.main()
