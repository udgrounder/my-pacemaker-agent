import argparse
import importlib.util
import json
import os
import subprocess
import sys
import errno
import shutil
import tempfile
import unittest
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
        release_manager.RUNTIME_SOURCE = self.root / ".mpa-workspace"
        release_manager.RUNTIME_DIST = self.root / "dist" / ".mpa-workspace"
        release_manager.WORKSPACE = self.root / "workspace"
        release_manager.MANIFESTS = release_manager.WORKSPACE / "releases" / "manifests"
        release_manager.PACKAGES = release_manager.WORKSPACE / "releases" / "packages"
        release_manager.RELEASE_RECEIPTS = release_manager.WORKSPACE / "receipts" / "releases"
        release_manager.DEPLOYMENT_RECEIPTS = release_manager.WORKSPACE / "receipts" / "deployments"
        release_manager.ISSUE_RECEIPTS = release_manager.WORKSPACE / "receipts" / "issues"
        release_manager.ISSUES = release_manager.WORKSPACE / "issues"
        self.write_runtime(release_manager.RUNTIME_SOURCE, "v1")

    def tearDown(self):
        self.temp.cleanup()

    @staticmethod
    def write_runtime(path, version):
        path.mkdir(parents=True, exist_ok=True)
        (path / ".mpa-version").write_text(f"current_release: {version}\n", encoding="utf-8")
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
        self.assertTrue((target_root / ".mpa-workspace" / "history" / "releases" / json.loads(manifest.read_text())["release_id"]).with_suffix(".json").is_file())

    def test_deploy_and_rollback_preserve_user_owned_paths(self):
        manifest = self.prepare()
        release_id = json.loads(manifest.read_text(encoding="utf-8"))["release_id"]
        target_root = self.root / "target"
        self.write_runtime(target_root / ".mpa-workspace", "old")
        (target_root / "workspace").mkdir()
        (target_root / "docs").mkdir()
        (target_root / "AGENTS.md").write_text("user config", encoding="utf-8")
        (target_root / "main.py").write_text("user source", encoding="utf-8")
        (target_root / "workspace" / "user.txt").write_text("workspace", encoding="utf-8")
        (target_root / "docs" / "user.md").write_text("docs", encoding="utf-8")
        docs_index = target_root / "docs" / "INDEX.md"
        docs_index.write_text("# operator index\n", encoding="utf-8")
        config = target_root / ".mpa-project" / "config.yaml"
        config.parent.mkdir()
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
        backup = next((target_root / ".mpa-backups").iterdir())
        release_manager.rollback(argparse.Namespace(
            target=str(target_root), target_ref="test-target", backup=str(backup.relative_to(target_root)),
            release_id=release_id, verified_by="test", approved_by="test", approval_ref="unit", rollback_owner="test"))
        self.assertEqual((target_root / ".mpa-workspace" / "rule.md").read_text(encoding="utf-8"), "old")
        self.assertEqual((target_root / "workspace" / "user.txt").read_text(encoding="utf-8"), "workspace")
        self.assertEqual((target_root / "docs" / "user.md").read_text(encoding="utf-8"), "docs")
        self.assertEqual(docs_index.read_text(encoding="utf-8"), "# operator index\n")
        self.assertEqual((target_root / "AGENTS.md").read_text(encoding="utf-8"), "user config")
        self.assertEqual((target_root / "main.py").read_text(encoding="utf-8"), "user source")
        self.assertEqual(config.read_text(encoding="utf-8"), config_before)

    def test_deploy_creates_only_missing_workspace_and_docs_roots(self):
        manifest = self.prepare()
        target = self.root / "target"
        self.write_runtime(target / ".mpa-workspace", "old")
        release_manager.deployment_dry_run(argparse.Namespace(manifest=str(manifest), target=str(target), target_ref="target"))
        dry_run = next((release_manager.DEPLOYMENT_RECEIPTS / "target").glob("dry-run-*.json"))
        release_manager.deploy(argparse.Namespace(manifest=str(manifest), target=str(target), target_ref="target", verified_by="test",
                                                  dry_run=str(dry_run), approved_by="test", approval_ref="unit", rollback_owner="test"))
        self.assertTrue((target / "workspace").is_dir())
        self.assertTrue((target / "workspace" / "issues").is_dir())
        self.assertTrue((target / "docs").is_dir())
        self.assertTrue((target / "docs" / "INDEX.md").is_file())

    def test_runtime_backup_retention_keeps_the_newest_three_directories_only(self):
        target = self.root / "target"
        backups = target / ".mpa-backups"
        for index in range(4):
            backup = backups / f"backup-{index}"
            backup.mkdir(parents=True)
            timestamp = 1_700_000_000 + index
            os.utime(backup, (timestamp, timestamp))
        note = backups / "operator-note.txt"
        note.write_text("preserve", encoding="utf-8")

        removed = release_manager.prune_runtime_backups(target)

        self.assertEqual(removed, ["backup-0"])
        self.assertEqual(sorted(path.name for path in backups.iterdir()),
                         ["backup-1", "backup-2", "backup-3", "operator-note.txt"])

    def test_rollback_receipt_failure_restores_applied_runtime(self):
        manifest = self.prepare()
        release_id = json.loads(manifest.read_text(encoding="utf-8"))["release_id"]
        target = self.root / "target"
        self.write_runtime(target / ".mpa-workspace", "old")
        release_manager.deployment_dry_run(argparse.Namespace(manifest=str(manifest), target=str(target), target_ref="target"))
        dry_run = next((release_manager.DEPLOYMENT_RECEIPTS / "target").glob("dry-run-*.json"))
        release_manager.deploy(argparse.Namespace(manifest=str(manifest), target=str(target), target_ref="target", verified_by="test",
                                                  dry_run=str(dry_run), approved_by="test", approval_ref="unit", rollback_owner="test"))
        backup = next((target / ".mpa-backups").iterdir())
        original_write = release_manager.write_json
        def fail_rollback_receipt(path, value):
            if path.parent == release_manager.DEPLOYMENT_RECEIPTS / "target" and value.get("status") == "rolled_back":
                raise OSError("receipt failed")
            return original_write(path, value)
        with mock.patch.object(release_manager, "write_json", side_effect=fail_rollback_receipt):
            with self.assertRaisesRegex(OSError, "receipt failed"):
                release_manager.rollback(argparse.Namespace(target=str(target), target_ref="target", backup=str(backup.relative_to(target)),
                                                          release_id=release_id, verified_by="test", approved_by="test", approval_ref="unit", rollback_owner="test"))
        self.assertEqual((target / ".mpa-workspace" / "rule.md").read_text(encoding="utf-8"), "v1")

    def test_deploy_rejects_repeated_release_history(self):
        manifest = self.prepare()
        target_root = self.root / "target"
        self.write_runtime(target_root / ".mpa-workspace", "old")
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
        self.write_runtime(target / ".mpa-workspace", "old")
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
        self.write_runtime(target_root / ".mpa-workspace", "old")
        release_manager.deployment_dry_run(argparse.Namespace(manifest=str(manifest), target=str(target_root), target_ref="test-target"))
        dry_run = next((release_manager.DEPLOYMENT_RECEIPTS / "test-target").glob("dry-run-*.json"))
        args = argparse.Namespace(manifest=str(manifest), target=str(target_root), target_ref="test-target", verified_by="test",
                                  dry_run=str(dry_run), approved_by="test", approval_ref="unit", rollback_owner="test")
        with mock.patch.object(release_manager, "verify_target", side_effect=[None, ValueError("verification failed")]):
            with self.assertRaisesRegex(ValueError, "verification failed"):
                release_manager.deploy(args)
        self.assertEqual((target_root / ".mpa-workspace" / "rule.md").read_text(encoding="utf-8"), "old")
        history = json.loads((target_root / ".mpa-workspace" / "history" / "releases" / f"{release_id}.json").read_text(encoding="utf-8"))
        self.assertEqual(history["status"], "failed")
        self.assertTrue(list((release_manager.DEPLOYMENT_RECEIPTS / "test-target").glob("deploy-failed-*.json")))

    def test_deploy_revalidates_target_receipt_and_approval(self):
        manifest = self.prepare()
        target = self.root / "target"
        self.write_runtime(target / ".mpa-workspace", "old")
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
        (target / ".mpa-workspace" / "unexpected.md").write_text("changed", encoding="utf-8")
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

    def test_repeated_preparation_creates_distinct_immutable_release_ids(self):
        manifest = self.prepare()
        original = json.loads(manifest.read_text(encoding="utf-8"))
        release_manager.prepare_release(argparse.Namespace(
            verified_by="test", compatibility="compatible", breaking_change="none", migration="none",
            rollback_condition="verification failure", release_note="test release",
            validation_command=[sys.executable, "-c", "print('ok')"],
        ))

        manifests = list(release_manager.MANIFESTS.glob("*.json"))
        self.assertEqual(len(manifests), 2)
        self.assertNotEqual(json.loads(manifests[0].read_text(encoding="utf-8"))["release_id"],
                            json.loads(manifests[1].read_text(encoding="utf-8"))["release_id"])
        self.assertEqual(original["release_id"], release_manager.current_release(release_manager.PACKAGES / original["release_id"]))
        self.assertEqual(len(list(release_manager.RELEASE_RECEIPTS.glob("*.json"))), 2)

    def test_release_id_is_the_only_runtime_identity_and_checksum_is_evidence(self):
        manifest = self.prepare()
        data = json.loads(manifest.read_text(encoding="utf-8"))
        self.assertRegex(data["release_id"], r"^\d{14}-[0-9a-f]{8}$")
        self.assertNotIn("runtime_version", data)
        self.assertIn("asset_checksum", data)
        self.assertEqual(release_manager.current_release(release_manager.RUNTIME_SOURCE), data["release_id"])
        self.assertEqual(release_manager.current_release(release_manager.RUNTIME_DIST), data["release_id"])

    def test_update_collects_issues_only_after_runtime_verification(self):
        manifest = self.prepare()
        target = self.root / "target"
        self.write_runtime(target / ".mpa-workspace", "old")
        issue = target / "workspace" / "issues" / "issue.md"
        issue.parent.mkdir(parents=True)
        issue.write_text(release_manager.issue_text("test", "summary", "methodology_improvement"), encoding="utf-8")
        release_manager.deployment_dry_run(argparse.Namespace(manifest=str(manifest), target=str(target), target_ref="target"))
        dry_run = next((release_manager.DEPLOYMENT_RECEIPTS / "target").glob("dry-run-*.json"))
        release_manager.deploy(argparse.Namespace(manifest=str(manifest), target=str(target), target_ref="target", verified_by="test",
                                                  dry_run=str(dry_run), approved_by="test", approval_ref="unit", rollback_owner="test"))
        self.assertFalse(issue.exists())
        self.assertTrue((release_manager.ISSUES / "inbox" / "target" / "issue.md").is_file())

    def test_update_issue_change_after_dry_run_preserves_source(self):
        manifest = self.prepare()
        target = self.root / "target"
        self.write_runtime(target / ".mpa-workspace", "old")
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
        manifest = next(release_manager.MANIFESTS.glob("*.json"))
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
        self.assertFalse(release_manager.MANIFESTS.exists())

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
        self.assertFalse(release_manager.MANIFESTS.exists())
        original_write = release_manager.write_json
        def fail_manifest(path, value):
            if path.parent == release_manager.MANIFESTS:
                raise OSError("manifest write failed")
            return original_write(path, value)
        with mock.patch.object(release_manager, "write_json", side_effect=fail_manifest):
            with self.assertRaisesRegex(OSError, "manifest write failed"):
                release_manager.prepare_release(arguments)
        self.assertFalse(release_manager.MANIFESTS.exists())
        self.assertFalse(list(release_manager.PACKAGES.glob("*")))
        self.assertFalse(list(release_manager.RELEASE_RECEIPTS.glob("*")))
        self.assertEqual(release_manager.current_release(release_manager.RUNTIME_SOURCE), original_release)
        self.assertEqual(release_manager.current_release(release_manager.RUNTIME_DIST), original_release)

    def test_deploy_legacy_current_version_records_a_single_legacy_origin(self):
        manifest = self.prepare()
        target = self.root / "legacy-target"
        target_runtime = target / ".mpa-workspace"
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
        self.assertFalse(release_manager.MANIFESTS.exists())
        manifest = self.prepare()
        release_id = json.loads(manifest.read_text(encoding="utf-8"))["release_id"]
        shutil.rmtree(release_manager.PACKAGES / release_id)
        with self.assertRaisesRegex(ValueError, "invalid release artifacts"):
            release_manager.audit_releases(argparse.Namespace())

    def test_issue_requires_review_and_keeps_needs_information_in_inbox(self):
        issue = release_manager.ISSUES / "inbox" / "test-project" / "issue.md"
        issue.parent.mkdir(parents=True)
        issue.write_text(release_manager.issue_text("test", "summary", "methodology_improvement"), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "accepted review"):
            release_manager.triage_issue(argparse.Namespace(
                issue="test-project/issue.md", classification="methodology_improvement", triaged_by="test",
                status="needs_information", reproduction="unknown", impact="unknown", priority="low",
                relationship="undetermined", follow_up_task="none",
            ))
        release_manager.review_issue(argparse.Namespace(issue="test-project/issue.md", reviewed_by="test", approval_ref="unit", decision="accepted"))
        release_manager.triage_issue(argparse.Namespace(
            issue="test-project/issue.md", classification="methodology_improvement", triaged_by="test",
            status="needs_information", reproduction="unknown", impact="unknown", priority="low",
            relationship="undetermined", follow_up_task="none",
        ))
        metadata, _ = release_manager.read_issue(issue)
        self.assertEqual(metadata["status"], "needs_information")

    def test_archive_rejects_deployment_evidence_for_another_release(self):
        issue = release_manager.ISSUES / "inbox" / "test-project" / "resolved.md"
        issue.parent.mkdir(parents=True)
        deployment = release_manager.DEPLOYMENT_RECEIPTS / "test-project" / "deploy.json"
        deployment.parent.mkdir(parents=True)
        deployment.write_text(json.dumps({"release_id": "other-release"}), encoding="utf-8")
        release_manager.MANIFESTS.mkdir(parents=True)
        (release_manager.MANIFESTS / "expected-release.json").write_text("{}", encoding="utf-8")
        issue.write_text(release_manager.issue_text("test", "summary", "methodology_improvement"), encoding="utf-8")
        metadata, body = release_manager.read_issue(issue)
        metadata.update({"status": "resolved", "release": "expected-release",
                         "deployment": str(deployment.relative_to(release_manager.ROOT)), "verification": "test"})
        release_manager.write_issue(issue, metadata, body)
        with self.assertRaisesRegex(ValueError, "does not match"):
            release_manager.archive_issue(argparse.Namespace(issue="test-project/resolved.md", archived_by="test"))
        self.assertTrue(issue.exists())

    def test_issue_receipt_failure_restores_issue_and_rejected_review_blocks_triage(self):
        issue = release_manager.ISSUES / "inbox" / "test-project" / "issue.md"
        issue.parent.mkdir(parents=True)
        issue.write_text(release_manager.issue_text("test", "summary", "methodology_improvement"), encoding="utf-8")
        original = issue.read_text(encoding="utf-8")
        original_receipt = release_manager.issue_receipt
        release_manager.issue_receipt = lambda *_: (_ for _ in ()).throw(OSError("receipt write failed"))
        try:
            with self.assertRaisesRegex(OSError, "receipt"):
                release_manager.review_issue(argparse.Namespace(
                    issue="test-project/issue.md", reviewed_by="test", approval_ref="unit", decision="accepted"))
        finally:
            release_manager.issue_receipt = original_receipt
        self.assertEqual(issue.read_text(encoding="utf-8"), original)
        release_manager.review_issue(argparse.Namespace(
            issue="test-project/issue.md", reviewed_by="test", approval_ref="unit", decision="rejected"))
        with self.assertRaisesRegex(ValueError, "accepted review"):
            release_manager.triage_issue(argparse.Namespace(
                issue="test-project/issue.md", classification="methodology_improvement", triaged_by="test",
                status="triaged", reproduction="yes", impact="low", priority="low",
                relationship="new", follow_up_task="none"))

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

    def test_collect_receipt_failure_returns_issue_to_project(self):
        project = self.root / "project"
        source = project / "workspace" / "issues" / "issue.md"
        source.parent.mkdir(parents=True)
        source.write_text(release_manager.issue_text("test", "summary", "methodology_improvement"), encoding="utf-8")
        with mock.patch.object(release_manager, "issue_receipt", side_effect=OSError("receipt failed")):
            with self.assertRaisesRegex(OSError, "receipt failed"):
                release_manager.collect_issue(argparse.Namespace(project=str(project), project_ref="project", issue="issue.md"))
        self.assertTrue(source.exists())
        self.assertFalse((release_manager.ISSUES / "inbox" / "project" / "issue.md").exists())

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
        release_manager.MANIFESTS.mkdir(parents=True)
        (release_manager.PACKAGES / "orphan").mkdir(parents=True)
        with self.assertRaisesRegex(ValueError, "inventory"):
            release_manager.audit_releases(argparse.Namespace())

    def test_issue_full_lifecycle_links_release_and_deployment_evidence(self):
        manifest = self.prepare()
        release_id = json.loads(manifest.read_text(encoding="utf-8"))["release_id"]
        target = self.root / "target"
        self.write_runtime(target / ".mpa-workspace", "old")
        release_manager.deployment_dry_run(argparse.Namespace(manifest=str(manifest), target=str(target), target_ref="target"))
        dry_run = next((release_manager.DEPLOYMENT_RECEIPTS / "target").glob("dry-run-*.json"))
        release_manager.deploy(argparse.Namespace(manifest=str(manifest), target=str(target), target_ref="target", verified_by="test",
                                                  dry_run=str(dry_run), approved_by="test", approval_ref="unit", rollback_owner="test"))
        deployment = next((release_manager.DEPLOYMENT_RECEIPTS / "target").glob("deploy-*.json"))
        project = self.root / "project"
        release_manager.create_issue(argparse.Namespace(project=str(project), title="test", summary="summary", kind="methodology_improvement",
                                                        key="methodology-improvement", occurrence="first_observed", area="release",
                                                        observed_release=release_id, collection_purpose="improve"))
        source = next((project / "workspace" / "issues").glob("*.md"))
        release_manager.collect_issue(argparse.Namespace(project=str(project), project_ref="project", issue=source.name))
        issue = f"project/{source.name}"
        release_manager.review_issue(argparse.Namespace(issue=issue, reviewed_by="test", approval_ref="unit", decision="accepted"))
        release_manager.triage_issue(argparse.Namespace(issue=issue, classification="methodology_improvement", triaged_by="test",
                                                        status="triaged", reproduction="yes", impact="low", priority="low",
                                                        relationship="new", follow_up_task="task-1"))
        release_manager.resolve_issue(argparse.Namespace(issue=issue, task="task-1", release=release_id,
                                                         deployment=str(deployment.relative_to(release_manager.ROOT)), verification="unit",
                                                         resolved_by="test"))
        release_manager.archive_issue(argparse.Namespace(issue=issue, archived_by="test"))
        self.assertFalse((release_manager.ISSUES / "inbox" / issue).exists())
        self.assertTrue(list((release_manager.ISSUES / "archived").rglob(source.name)))


if __name__ == "__main__":
    unittest.main()
