import argparse
import importlib.util
import json
import sys
import tempfile
import unittest
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
        release_manager.RUNTIME_SOURCE = self.root / ".mpa-workspace"
        release_manager.RUNTIME_DIST = self.root / "dist" / ".mpa-workspace"
        release_manager.WORKSPACE = self.root / "workspace"
        release_manager.MANIFESTS = release_manager.WORKSPACE / "releases" / "manifests"
        release_manager.PACKAGES = release_manager.WORKSPACE / "releases" / "packages"
        release_manager.RELEASE_RECEIPTS = release_manager.WORKSPACE / "receipts" / "releases"
        release_manager.DEPLOYMENT_RECEIPTS = release_manager.WORKSPACE / "receipts" / "deployments"
        release_manager.ISSUES = release_manager.WORKSPACE / "issues"
        self.write_runtime(release_manager.RUNTIME_SOURCE, "v1")

    def tearDown(self):
        self.temp.cleanup()

    @staticmethod
    def write_runtime(path, version):
        path.mkdir(parents=True, exist_ok=True)
        (path / ".mpa-version").write_text(f"current_version: {version}\n", encoding="utf-8")
        (path / "rule.md").write_text(version, encoding="utf-8")

    def prepare(self):
        release_manager.sync_runtime(argparse.Namespace())
        release_manager.prepare_release(argparse.Namespace(
            verified_by="test", compatibility="compatible", breaking_change="none", migration="none",
            rollback_condition="verification failure", release_note="test release",
            validation_command=[sys.executable, "-c", "print('ok')"],
        ))
        manifests = list(release_manager.MANIFESTS.glob("*.json"))
        self.assertEqual(len(manifests), 1)
        return manifests[0]

    def test_deploy_uses_immutable_package_not_current_dist(self):
        manifest = self.prepare()
        self.write_runtime(release_manager.RUNTIME_DIST, "v2")
        target_root = self.root / "target"
        self.write_runtime(target_root / ".mpa-workspace", "old")
        release_manager.deployment_dry_run(argparse.Namespace(
            manifest=str(manifest), target=str(target_root), target_ref="test-target",
        ))
        dry_run = next((release_manager.DEPLOYMENT_RECEIPTS / "test-target").glob("dry-run-*.json"))

        release_manager.deploy(argparse.Namespace(
            manifest=str(manifest), target=str(target_root), target_ref="test-target", verified_by="test",
            dry_run=str(dry_run), approved_by="test", approval_ref="unit", rollback_owner="test",
        ))

        self.assertEqual((target_root / ".mpa-workspace" / "rule.md").read_text(encoding="utf-8"), "v1")
        self.assertTrue(any((target_root / ".mpa-backups").iterdir()))

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
        self.write_runtime(target_root / ".mpa-workspace", "old")
        with self.assertRaisesRegex(ValueError, "target-ref"):
            release_manager.deploy(argparse.Namespace(
                manifest=str(manifest), target=str(target_root), target_ref="../escape", verified_by="test",
                dry_run="unused", approved_by="test", approval_ref="unit", rollback_owner="test",
            ))
        with self.assertRaisesRegex(ValueError, "backup must be inside"):
            release_manager.rollback(argparse.Namespace(
                target=str(target_root), target_ref="test-target", backup=".mpa-workspace",
            ))

    def test_repeated_preparation_preserves_manifest_and_adds_receipts(self):
        manifest = self.prepare()
        original = json.loads(manifest.read_text(encoding="utf-8"))
        release_manager.prepare_release(argparse.Namespace(
            verified_by="test", compatibility="compatible", breaking_change="none", migration="none",
            rollback_condition="verification failure", release_note="test release",
            validation_command=[sys.executable, "-c", "print('ok')"],
        ))

        self.assertEqual(json.loads(manifest.read_text(encoding="utf-8")), original)
        self.assertEqual(len(list(release_manager.RELEASE_RECEIPTS.glob("*.json"))), 2)


if __name__ == "__main__":
    unittest.main()
