import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "evaluations/summarize.py"
SPEC = importlib.util.spec_from_file_location("evaluation_summary", MODULE_PATH)
summary = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(summary)


class EvaluationSummaryTest(unittest.TestCase):
    def valid_data(self):
        return json.loads((ROOT / "evaluations/fixtures/valid-study.json").read_text(encoding="utf-8"))

    def test_summary_includes_failed_runs_and_missing_values(self):
        report = summary.summarize(self.valid_data())
        self.assertEqual(report["conditions"]["mpa"]["runs"], 2)
        self.assertEqual(report["conditions"]["mpa"]["successes"], 1)
        self.assertEqual(report["conditions"]["mpa"]["missing"]["active_seconds"], 1)
        self.assertEqual(report["conditions"]["baseline"]["token_count"]["count"], 0)
        self.assertEqual(report["conditions"]["baseline"]["missing"]["token_count"], 1)
        self.assertEqual(report["paired_successful_active_seconds_delta"]["median"], -30)
        self.assertIn("Descriptive", summary.render_markdown(report))

    def test_rejects_duplicate_ids_time_inversion_and_invalid_units(self):
        cases = []
        duplicate = self.valid_data()
        duplicate["runs"][1]["run_id"] = duplicate["runs"][0]["run_id"]
        cases.append((duplicate, "duplicate run_id"))
        inverted = self.valid_data()
        inverted["runs"][0]["ended_at"] = "2026-09-09T23:59:59Z"
        cases.append((inverted, "end before"))
        invalid_unit = self.valid_data()
        invalid_unit["runs"][0]["active_seconds"] = 1.5
        cases.append((invalid_unit, "non-negative integer"))
        for data, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(summary.StudyValidationError, message):
                    summary.summarize(data)

    def test_rejects_pair_with_different_comparison_conditions(self):
        data = self.valid_data()
        data["runs"][1]["condition_manifest"]["model_version"] = "other"
        with self.assertRaisesRegex(summary.StudyValidationError, "condition manifest"):
            summary.summarize(data)

    def test_rejects_missing_required_measurement_field(self):
        data = self.valid_data()
        del data["runs"][0]["active_seconds"]
        with self.assertRaisesRegex(summary.StudyValidationError, "active_seconds is required"):
            summary.summarize(data)

    def test_rejects_naive_timestamp_as_validation_error(self):
        data = self.valid_data()
        data["runs"][0]["started_at"] = "2026-09-10T00:00:00"
        with self.assertRaisesRegex(summary.StudyValidationError, "UTC ISO-8601"):
            summary.summarize(data)

    def test_stopped_and_session_resume_contract(self):
        data = self.valid_data()
        stopped = data["runs"][2]
        stopped["status"] = "stopped"
        stopped["quality"] = "unverified"
        stopped["stop_reason"] = "fixture acceptance criteria conflict"
        resumed = data["runs"][0]
        resumed["scenario_id"] = "session_resume"
        resumed["pair_id"] = None
        data["runs"][1]["pair_id"] = None
        resumed["resume_requested_at"] = "2026-09-10T00:00:30Z"
        resumed["first_acceptance_action_at"] = "2026-09-10T00:01:10Z"

        report = summary.summarize(data)
        self.assertEqual(report["conditions"]["mpa"]["status_counts"]["stopped"], 1)
        self.assertEqual(report["conditions"]["baseline"]["resume_seconds"]["median"], 40)

        stopped["stop_reason"] = None
        with self.assertRaisesRegex(summary.StudyValidationError, "stop_reason is required"):
            summary.summarize(data)

    def test_scenario_event_summary_and_schema_contract(self):
        data = self.valid_data()
        report = summary.summarize(data)
        self.assertEqual(
            report["conditions"]["mpa"]["scenario_events"]["wording_edit"]["by_kind"]["duplicate_intent_request"],
            1,
        )
        self.assertEqual(report["conditions"]["mpa"]["scenario_events"]["bug_fix"]["by_kind"]["defect"], 1)
        schema = json.loads((ROOT / "evaluations/schema.json").read_text(encoding="utf-8"))
        run_schema = schema["$defs"]["run"]
        self.assertEqual(set(run_schema["required"]), set(summary.RUN_FIELDS))
        self.assertEqual(set(run_schema["properties"]), set(summary.RUN_FIELDS))
        self.assertFalse(run_schema["additionalProperties"])
        self.assertEqual(schema["$defs"]["utcTimestamp"]["pattern"], summary.UTC_TIMESTAMP_PATTERN)
        self.assertEqual(schema["$defs"]["nonblankString"]["pattern"], "\\S")
        self.assertIn("duplicate_intent_request", summary.render_markdown(report))
        self.assertIn("wording_edit", summary.render_markdown(report))

    def test_schema_and_python_reject_same_invalid_timestamp_corpus(self):
        try:
            from jsonschema import Draft202012Validator, FormatChecker
        except ImportError:
            self.skipTest("jsonschema is optional outside schema contract verification")
        schema = json.loads((ROOT / "evaluations/schema.json").read_text(encoding="utf-8"))
        for timestamp in ("not-a-timeZ", "2026-02-30T00:00:00Z", "0000-01-01T00:00:00Z", "2026-09-10T00:00:00", "2026-09-10 00:00:00Z"):
            with self.subTest(timestamp=timestamp):
                data = self.valid_data()
                data["runs"][0]["started_at"] = timestamp
                self.assertTrue(list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(data)))
                with self.assertRaises(summary.StudyValidationError):
                    summary.summarize(data)

    def test_cli_reports_output_path_error_without_traceback(self):
        with tempfile.TemporaryDirectory() as directory:
            missing_parent = Path(directory) / "missing" / "report.json"
            markdown_out = Path(directory) / "report.md"
            result = subprocess.run(
                [sys.executable, str(MODULE_PATH), str(ROOT / "evaluations/fixtures/valid-study.json"),
                 "--json-out", str(missing_parent), "--markdown-out", str(markdown_out)],
                text=True, capture_output=True, check=False,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("No such file", result.stderr)
            self.assertNotIn("Traceback", result.stderr)

    def test_cli_writes_matching_json_and_markdown_reports(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            json_out = folder / "report.json"
            markdown_out = folder / "report.md"
            result = subprocess.run(
                [sys.executable, str(MODULE_PATH), str(ROOT / "evaluations/fixtures/valid-study.json"),
                 "--json-out", str(json_out), "--markdown-out", str(markdown_out)],
                text=True, capture_output=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(json_out.read_text(encoding="utf-8"))["study_id"], "synthetic-pilot")
            self.assertIn("MPA 효과 측정 요약", markdown_out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
