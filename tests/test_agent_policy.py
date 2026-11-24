import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".mpa/runtime/hooks/agent_policy.py"
spec = importlib.util.spec_from_file_location("agent_policy", SCRIPT)
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)
TIME = "2026-11-23T08:05:00Z"


def proof(value, source, role="main", revision="v2", observed=TIME):
    return dict(value=value, source=source, role=role, revision=revision,
                observed_at=observed, host="codex", session="s1")


def relation(*models):
    return dict(models=list(models), approval_source="user", basis="approved for this installation",
                confirmed_at="2026-11-23T08:00:00Z")


def request():
    return {
        "context": dict(host="codex", session="s1", role="reader", revision="v2",
                        initial_revision="v1", started_at="2026-11-23T08:00:00Z",
                        revision_since="2026-11-23T08:04:00Z", as_of=TIME),
        "evidence": {
            "initial": proof("main", "host_session", revision="v1", observed="2026-11-23T08:00:00Z"),
            "current": proof("main", "host_session"),
            "available": proof(["main", "lower", "unlisted"], "tool_inventory", role="reader"),
            "resolution": proof(dict(mode="explicit", requested="lower", model="lower",
                                     settings_supported=True, within_main_effort=True),
                                "effective_host_config", role="reader"),
        },
        "policy": dict(schema_version=1, host="codex",
                       allowed_lower_models={"main": relation("lower"), "lower": relation("unlisted")}),
        "call": dict(kind="read", mode="explicit", requested="lower", permitted=True, by_main=True,
                     simple=True, independent=True, worthwhile=True),
        "budget": dict(active_optional=0, free_slots=1, retries_used=0),
    }


def choose(req, model, mode="explicit"):
    requested = model if mode == "explicit" else None
    req["call"].update(mode=mode, requested=requested)
    req["evidence"]["resolution"]["value"].update(mode=mode, requested=requested, model=model)


class AgentPolicyTest(unittest.TestCase):
    def test_direct_relationship_and_task_preference(self):
        req = request()
        result = policy.resolve(req)
        self.assertEqual((result["action"], result["selected"]), ("select", "lower"))
        self.assertEqual(result["preferred"], ["lower", "main"])
        req["call"].update(kind="design")
        self.assertEqual(policy.resolve(req)["preferred"], ["main"])
        choose(req, "unlisted")
        self.assertEqual(policy.resolve(req)["reason"], "model_not_allowed_or_available")

    def test_original_ceiling_and_new_lower_ceiling(self):
        req = request()
        req["policy"]["allowed_lower_models"]["higher"] = relation("main", "lower")
        req["evidence"]["current"]["value"] = "higher"
        req["evidence"]["available"]["value"].append("higher")
        choose(req, "higher")
        self.assertEqual(policy.resolve(req)["allowed"], ["lower", "main"])
        self.assertEqual(policy.resolve(req)["action"], "direct")

        req["evidence"]["current"]["value"] = "lower"
        choose(req, "lower")
        req["running"] = [{"id": "old", "model": "main"}, {"id": "unknown", "model": None}]
        result = policy.resolve(req)
        self.assertEqual(result["allowed"], ["lower"])
        self.assertEqual(result["stop_and_mark_unconfirmed"], ["old", "unknown"])
        self.assertEqual(result["action"], "direct")

    def test_current_evidence_cannot_replace_the_original_revision(self):
        req = request()
        req["evidence"]["current"]["value"] = "higher"
        req["evidence"]["initial"] = copy.deepcopy(req["evidence"]["current"])
        req["evidence"]["available"]["value"].append("higher")
        choose(req, "higher")
        self.assertIn("initial", policy.resolve(req)["unconfirmed"])
        self.assertEqual(policy.resolve(req)["action"], "direct")

    def test_future_approval_and_different_effort_are_rejected(self):
        req = request()
        req["call"]["reasoning_effort"] = "high"
        self.assertEqual(policy.resolve(req)["reason"], "resolution_does_not_match_request")
        req["evidence"]["resolution"]["value"]["reasoning_effort"] = "high"
        self.assertEqual(policy.resolve(req)["action"], "select")
        req["policy"]["allowed_lower_models"]["main"]["confirmed_at"] = "2026-12-01T00:00:00Z"
        with self.assertRaisesRegex(policy.PolicyError, "future"):
            policy.resolve(req)

    def test_incomparable_switch_blocks_new_calls(self):
        req = request()
        req["evidence"]["current"]["value"] = "incomparable"
        choose(req, "incomparable", "inherit")
        self.assertEqual(policy.resolve(req)["allowed"], [])
        self.assertEqual(policy.resolve(req)["action"], "direct")

    def test_safe_inheritance_without_local_policy(self):
        req = request()
        del req["policy"]
        self.assertEqual(policy.resolve(req)["action"], "direct")
        choose(req, "main", "inherit")
        req["evidence"]["resolution"]["source"] = "guaranteed_inheritance"
        self.assertEqual(policy.resolve(req)["action"], "inherit")
        req["evidence"]["resolution"]["value"]["model"] = "higher"
        self.assertEqual(policy.resolve(req)["reason"], "host_override")

    def test_stale_invented_or_mismatched_evidence(self):
        changes = (("source", "documentation"), ("role", "other"), ("revision", "v1"),
                   ("session", "old"), ("observed_at", "2026-11-23T08:01:00Z"))
        for key, value in changes:
            with self.subTest(key=key):
                req = request()
                req["evidence"]["resolution"][key] = value
                self.assertIn("resolution", policy.resolve(req)["unconfirmed"])
                self.assertEqual(policy.resolve(req)["action"], "direct")
        for field in ("initial", "current", "available", "resolution"):
            req = request()
            del req["evidence"][field]
            self.assertIn(field, policy.resolve(req)["unconfirmed"])

    def test_override_availability_and_reasoning(self):
        req = request()
        req["evidence"]["resolution"]["value"]["model"] = "main"
        self.assertEqual(policy.resolve(req)["reason"], "host_override")
        choose(req, "lower")
        req["evidence"]["available"]["value"].remove("lower")
        self.assertEqual(policy.resolve(req)["reason"], "model_not_allowed_or_available")
        req["evidence"]["available"]["value"].append("lower")
        for key in ("settings_supported", "within_main_effort"):
            invalid = copy.deepcopy(req)
            invalid["evidence"]["resolution"]["value"][key] = False
            self.assertEqual(policy.resolve(invalid)["reason"], "settings_unconfirmed")

    def test_authority_small_work_single_writer_and_budget(self):
        for key, reason in (("permitted", "authority"), ("by_main", "authority"),
                            ("independent", "direct_work_preferred"),
                            ("worthwhile", "direct_work_preferred")):
            req = request()
            req["call"][key] = False
            self.assertEqual(policy.resolve(req)["reason"], reason)
        req = request()
        req["call"]["kind"] = "implement"
        self.assertEqual(policy.resolve(req)["reason"], "single_writer_unconfirmed")
        req["call"]["sole_writer"] = True
        self.assertEqual(policy.resolve(req)["action"], "select")
        req["budget"]["active_optional"] = 2
        self.assertEqual(policy.resolve(req)["action"], "wait")
        req["budget"]["active_optional"], req["budget"]["free_slots"] = 1, 0
        self.assertEqual(policy.resolve(req)["action"], "wait")

    def test_recovery_uses_same_logical_budget_and_main_model(self):
        req = request()
        req["call"]["recovery"] = True
        self.assertEqual(policy.resolve(req)["reason"], "recovery_requires_main_model")
        choose(req, "main")
        self.assertEqual(policy.resolve(req)["selected"], "main")
        req["budget"]["retries_used"] = 1
        self.assertEqual(policy.resolve(req)["reason"], "recovery_budget")

    def test_model_validation_precedes_slot_wait(self):
        for kind, action in (("read", "direct"), ("review", "review_self_check"),
                             ("critique", "critique_incomplete")):
            with self.subTest(kind=kind):
                req = request()
                req["call"].update(kind=kind, isolated=True)
                req["budget"]["free_slots"] = 0
                self.assertEqual(policy.resolve(req)["action"], "wait")
                del req["evidence"]["current"]
                result = policy.resolve(req)
                self.assertEqual((result["action"], result["reason"]),
                                 (action, "evidence_missing_or_stale"))
                req["evidence"]["current"] = proof("main", "host_session")
                req["evidence"]["resolution"]["value"]["model"] = "unlisted"
                self.assertEqual(policy.resolve(req)["reason"], "host_override")

    def test_required_failure_routing_and_isolation(self):
        for kind, action in (("critique", "critique_incomplete"), ("review", "review_self_check")):
            req = request()
            req["call"].update(kind=kind, worthwhile=False)
            self.assertEqual(policy.resolve(req)["reason"], "isolation_unconfirmed")
            req["call"]["isolated"] = True
            choose(req, "main")
            self.assertEqual(policy.resolve(req)["action"], "select")
            del req["evidence"]["current"]
            self.assertEqual(policy.resolve(req)["action"], action)

    def test_malformed_policies_and_cli(self):
        for models in (("main",), ("lower", "lower"), ("",)):
            req = request()
            req["policy"]["allowed_lower_models"]["main"] = relation(*models)
            with self.assertRaises(policy.PolicyError):
                policy.resolve(req)
        req = request()
        req["policy"]["allowed_lower_models"]["unlisted"] = relation("main")
        with self.assertRaises(policy.PolicyError):
            policy.resolve(req)
        req["policy"]["schema_version"] = 2
        with self.assertRaises(policy.PolicyError):
            policy.resolve(req)
        for command, payload, code in (
            ("inspect", '{"host":"codex","policy":null}', 0),
            ("inspect", '{"host":"codex","host":"codex","policy":null}', 2),
            ("resolve", json.dumps(request()), 0),
            ("resolve", "[]", 2),
        ):
            result = subprocess.run([sys.executable, str(SCRIPT), command], input=payload, text=True,
                                    capture_output=True)
            self.assertEqual(result.returncode, code, result.stderr)
            self.assertIsInstance(json.loads(result.stdout), dict)
