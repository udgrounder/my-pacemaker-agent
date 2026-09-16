import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_RUNTIME = ROOT / ".mpa/runtime"
DIST_RUNTIME = ROOT / "dist/.mpa/runtime"
MODULE_PATH = SOURCE_RUNTIME / "hooks/contract_reference.py"
SPEC = importlib.util.spec_from_file_location("contract_reference", MODULE_PATH)
contract_reference = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(contract_reference)


class ContractReferenceTest(unittest.TestCase):
    def copy_runtime(self, folder):
        target = Path(folder) / "runtime"
        shutil.copytree(SOURCE_RUNTIME, target)
        return target

    def test_source_contract_validates_and_matches_standard_toml_oracle(self):
        self.assertEqual(contract_reference.validate(SOURCE_RUNTIME)["references"], 3)
        try:
            import tomli
        except ImportError:
            self.skipTest("tomli is required only for the independent development oracle")
        text = (SOURCE_RUNTIME / "contracts/agent_reference.toml").read_text(encoding="utf-8")
        parsed = tomli.loads(text)
        self.assertEqual(parsed["contract"]["contract_version"], 1)
    def test_distribution_contract_validates(self):
        self.assertEqual(contract_reference.validate(DIST_RUNTIME)["contract_version"], 1)
        for relative in (
            "contracts/agent_reference.toml",
            "contracts/agent_reference_profile.md",
            "hooks/contract_reference.py",
        ):
            self.assertEqual((SOURCE_RUNTIME / relative).read_bytes(), (DIST_RUNTIME / relative).read_bytes())
        result = subprocess.run(
            [sys.executable, str(DIST_RUNTIME / "hooks/contract_reference.py"), "--runtime-root", str(DIST_RUNTIME)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"code": 0', result.stdout)

    def test_source_validator_cli_reports_success(self):
        result = subprocess.run(
            [sys.executable, str(MODULE_PATH), "--runtime-root", str(SOURCE_RUNTIME)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"code": 0', result.stdout)

    def test_project_root_discovery_reads_without_executing_or_mutating_runtime(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "project"
            runtime = project / ".mpa/runtime"
            runtime.parent.mkdir(parents=True)
            shutil.copytree(SOURCE_RUNTIME, runtime)
            before = {path.relative_to(runtime): path.read_bytes() for path in runtime.rglob("*") if path.is_file()}
            result = subprocess.run(
                [sys.executable, str(MODULE_PATH), "--project-root", str(project)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('"code": 0', result.stdout)
            after = {path.relative_to(runtime): path.read_bytes() for path in runtime.rglob("*") if path.is_file()}
            self.assertEqual(before, after)

    def test_profile_rejects_bom_inline_comment_and_unknown_key(self):
        for text in (
            "\ufeff[contract]\n",
            "[contract]\nprotocol = \"value\" # rejected\n",
            "[contract]\nquoted-key = \"value\"\n",
        ):
            with self.subTest(text=text):
                with self.assertRaisesRegex(contract_reference.ContractError, "BOM|inline|invalid key"):
                    contract_reference.parse_profile(text)

    def test_profile_rejects_json_only_escape(self):
        with self.assertRaisesRegex(contract_reference.ContractError, "non-TOML escape"):
            contract_reference.parse_profile('[contract]\nprotocol = "bad\\\\/escape"\n')
        with self.assertRaisesRegex(contract_reference.ContractError, "non-TOML escape"):
            contract_reference.parse_profile('[contract]\nprotocol = ["bad\\\\/escape"]\n')

    def test_unsupported_version_is_a_safe_version_error(self):
        with tempfile.TemporaryDirectory() as directory:
            runtime = self.copy_runtime(directory)
            contract = runtime / "contracts/agent_reference.toml"
            contract.write_text(
                contract.read_text(encoding="utf-8").replace("contract_version = 1", "contract_version = 2"),
                encoding="utf-8",
            )
            with self.assertRaises(contract_reference.ContractError) as raised:
                contract_reference.validate(runtime)
            self.assertEqual(raised.exception.code, contract_reference.EXIT_VERSION)

    def test_new_reference_and_lifecycle_change_require_new_version(self):
        with tempfile.TemporaryDirectory() as directory:
            runtime = self.copy_runtime(directory)
            contract = runtime / "contracts/agent_reference.toml"
            text = contract.read_text(encoding="utf-8")
            contract.write_text(text + '\n[[references]]\nfield_id = "entry.future"\nowner_kind = "markdown_file"\nowner_path = "core/agent_rules.md"\nowner_anchor = "agent-behavior-rules"\nusage = "inspect-only"\nauthority = "not-invokable"\n', encoding="utf-8")
            with self.assertRaises(contract_reference.ContractError) as raised:
                contract_reference.validate(runtime)
            self.assertEqual(raised.exception.code, contract_reference.EXIT_VERSION)

            contract.write_text(text.replace('"designing"', '"designing_v2"', 1), encoding="utf-8")
            with self.assertRaises(contract_reference.ContractError) as raised:
                contract_reference.validate(runtime)
            self.assertEqual(raised.exception.code, contract_reference.EXIT_VERSION)

            contract.write_text(text.replace('docs_root = "docs"', 'docs_root = "workspace/docs"', 1), encoding="utf-8")
            rules = runtime / "core/agent_rules.md"
            rules.write_text(
                rules.read_text(encoding="utf-8").replace(
                    "mpa-contract:paths.docs_root=docs", "mpa-contract:paths.docs_root=workspace/docs"
                ),
                encoding="utf-8",
            )
            with self.assertRaises(contract_reference.ContractError) as raised:
                contract_reference.validate(runtime)
            self.assertEqual(raised.exception.code, contract_reference.EXIT_VERSION)

    def test_markdown_binding_drift_is_detected_by_value(self):
        with tempfile.TemporaryDirectory() as directory:
            runtime = self.copy_runtime(directory)
            rules = runtime / "core/agent_rules.md"
            rules.write_text(
                rules.read_text(encoding="utf-8").replace(
                    "mpa-contract:paths.docs_root=docs", "mpa-contract:paths.docs_root=workspace/docs"
                ),
                encoding="utf-8",
            )
            with self.assertRaises(contract_reference.ContractError) as raised:
                contract_reference.validate(runtime)
            self.assertEqual(raised.exception.code, contract_reference.EXIT_DRIFT)
            self.assertEqual(raised.exception.field_id, "paths.docs_root")

    def test_duplicate_markdown_binding_marker_is_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            runtime = self.copy_runtime(directory)
            rules = runtime / "core/agent_rules.md"
            rules.write_text(rules.read_text(encoding="utf-8") + "\n<!-- mpa-contract:paths.docs_root=docs -->\n", encoding="utf-8")
            with self.assertRaises(contract_reference.ContractError) as raised:
                contract_reference.validate(runtime)
            self.assertEqual(raised.exception.code, contract_reference.EXIT_DRIFT)

    def test_missing_anchor_and_path_escape_are_reference_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            runtime = self.copy_runtime(directory)
            contract = runtime / "contracts/agent_reference.toml"
            text = contract.read_text(encoding="utf-8")
            contract.write_text(text.replace('owner_anchor = "agent-behavior-rules"', 'owner_anchor = "missing-anchor"', 1), encoding="utf-8")
            with self.assertRaises(contract_reference.ContractError) as raised:
                contract_reference.validate(runtime)
            self.assertEqual(raised.exception.code, contract_reference.EXIT_REFERENCE)

            contract.write_text(text.replace('owner_path = "core/agent_rules.md"', 'owner_path = "../outside.md"', 1), encoding="utf-8")
            with self.assertRaises(contract_reference.ContractError) as raised:
                contract_reference.validate(runtime)
            self.assertEqual(raised.exception.code, contract_reference.EXIT_REFERENCE)

    def test_symlinked_reference_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            runtime = self.copy_runtime(directory)
            rules = runtime / "core/agent_rules.md"
            external = Path(directory) / "external.md"
            external.write_text(rules.read_text(encoding="utf-8"), encoding="utf-8")
            rules.unlink()
            os.symlink(external, rules)
            with self.assertRaises(contract_reference.ContractError) as raised:
                contract_reference.validate(runtime)
            self.assertEqual(raised.exception.code, contract_reference.EXIT_REFERENCE)

    def test_corrupt_contract_cli_returns_json_schema_diagnostic(self):
        with tempfile.TemporaryDirectory() as directory:
            runtime = self.copy_runtime(directory)
            contract = runtime / "contracts/agent_reference.toml"
            contract.write_bytes(contract.read_bytes().replace(b'docs_root = "docs"', b"docs_root = 4"))
            result = subprocess.run(
                [sys.executable, str(MODULE_PATH), "--runtime-root", str(runtime)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, contract_reference.EXIT_SCHEMA)
            self.assertIn('"code": 21', result.stdout)
            self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
