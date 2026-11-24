"""Read-only validation and selection from caller-supplied delegation evidence."""

import argparse
from datetime import datetime
import json
import sys


class PolicyError(ValueError):
    pass


def fields(value, required, optional=()):
    if not isinstance(value, dict) or not set(required) <= value.keys() <= set(required) | set(optional):
        raise PolicyError("unexpected or missing object fields")
    return value


def identifier(value):
    if not isinstance(value, str) or not value or any(c.isspace() or not c.isprintable() for c in value):
        raise PolicyError("invalid identifier")
    return value


def note(value):
    if not isinstance(value, str) or not value.strip():
        raise PolicyError("missing evidence detail")
    return value


def timestamp(value):
    try:
        time = datetime.fromisoformat(note(value).replace("Z", "+00:00"))
        if time.utcoffset() is not None:
            return time
    except ValueError:
        pass
    raise PolicyError("evidence time must include a timezone")


def identifiers(values):
    if not isinstance(values, list):
        raise PolicyError("expected identifier list")
    result = {identifier(value) for value in values}
    if len(result) != len(values):
        raise PolicyError("duplicate identifier")
    return result


def count(value):
    if type(value) is not int or value < 0:
        raise PolicyError("invalid count")
    return value


def boolean(value):
    if type(value) is not bool:
        raise PolicyError("expected boolean")
    return value


def check_policy(policy, host, as_of=None):
    if policy is None:
        return {}
    fields(policy, ("schema_version", "host", "allowed_lower_models"))
    if type(policy["schema_version"]) is not int or policy["schema_version"] != 1:
        raise PolicyError("unsupported policy schema")
    if identifier(policy["host"]) != host:
        raise PolicyError("policy host mismatch")
    records = policy["allowed_lower_models"]
    if not isinstance(records, dict):
        raise PolicyError("expected model relationship map")
    lower = {}
    for parent, record in records.items():
        fields(record, ("models", "approval_source", "basis", "confirmed_at"))
        if record["approval_source"] not in ("user", "approved_project_policy"):
            raise PolicyError("unapproved model relationship")
        note(record["basis"])
        confirmed = timestamp(record["confirmed_at"])
        if as_of is not None and confirmed > as_of:
            raise PolicyError("model relationship confirmation is in the future")
        lower[identifier(parent)] = identifiers(record["models"])

    # Traverse only to reject cycles. A reachable model is not necessarily allowed.
    visited, visiting = set(), set()

    def visit(model):
        if model in visiting:
            raise PolicyError("cyclic or self-referential model relationship")
        if model not in visited:
            visiting.add(model)
            for child in lower.get(model, ()):
                visit(child)
            visiting.remove(model)
            visited.add(model)

    for model in lower:
        visit(model)
    return lower


def evidence(record, sources, expected, latest, earliest=None):
    if record is None:
        return None
    fields(record, ("source", "observed_at", "host", "session", "role", "revision", "value"))
    observed = timestamp(record["observed_at"])
    for key in ("source", "host", "session", "role", "revision"):
        identifier(record[key])
    if (record["source"] not in sources or any(record[k] != v for k, v in expected.items())
            or observed > latest or (earliest is not None and observed < earliest)):
        return None
    return record["value"]


def resolve(request):
    fields(request, ("context", "evidence", "call", "budget"), ("policy", "running"))
    context = fields(request["context"],
                     ("host", "session", "role", "initial_revision", "started_at",
                      "revision", "revision_since", "as_of"))
    common = {key: identifier(context[key]) for key in ("host", "session")}
    current = dict(common, revision=identifier(context["revision"]))
    role = identifier(context["role"])
    since, now = timestamp(context["revision_since"]), timestamp(context["as_of"])
    started = timestamp(context["started_at"])
    original = identifier(context["initial_revision"])
    if not started <= since <= now:
        raise PolicyError("invalid session or revision time")
    if original == current["revision"] and started != since:
        raise PolicyError("initial revision must begin at session start")
    lower = check_policy(request.get("policy"), common["host"], as_of=now)

    proofs = fields(request["evidence"], (), ("initial", "current", "available", "resolution"))
    main_sources = ("host_session", "user_window")

    def read(key, sources, expected, earliest=since):
        return evidence(proofs.get(key), sources, expected, now, earliest)

    # Only the original ceiling survives configuration changes within this session.
    initial_latest = now if original == current["revision"] else since
    initial = evidence(proofs.get("initial"), main_sources, dict(common, role="main", revision=original),
                       initial_latest, started)
    main = read("current", main_sources, dict(current, role="main"))
    target = dict(current, role=role)
    available = read("available", ("host_inventory", "tool_inventory"), target)
    resolution = read("resolution", ("effective_host_config", "guaranteed_inheritance"), target)
    initial = identifier(initial) if initial is not None else None
    main = identifier(main) if main is not None else None
    if original == current["revision"] and initial and main and initial != main:
        raise PolicyError("main model changed without a revision change")
    available = identifiers(available) if available is not None else set()
    allowed = ({initial} | lower.get(initial, set())) & ({main} | lower.get(main, set())) if initial and main else set()
    candidates = allowed & available

    call = fields(request["call"], ("kind", "mode", "requested", "permitted", "by_main"),
                  ("isolated", "independent", "worthwhile", "sole_writer", "simple", "recovery", "reasoning_effort"))
    kind, mode = call["kind"], call["mode"]
    if kind not in ("critique", "review", "read", "design", "implement") or mode not in ("explicit", "inherit"):
        raise PolicyError("unknown task or call mode")
    requested = identifier(call["requested"]) if mode == "explicit" else None
    if mode == "inherit" and call["requested"] is not None:
        raise PolicyError("inheritance must omit a model override")
    effort = call.get("reasoning_effort")
    if effort is not None:
        identifier(effort)
    for key in call.keys() - {"kind", "mode", "requested", "reasoning_effort"}:
        boolean(call[key])
    budget = fields(request["budget"], ("active_optional", "free_slots", "retries_used"))
    for value in budget.values():
        count(value)

    stop = []
    running = request.get("running", [])
    if not isinstance(running, list):
        raise PolicyError("invalid running agents")
    seen = set()
    for agent in running:
        fields(agent, ("id", "model"))
        agent_id = identifier(agent["id"])
        if agent_id in seen:
            raise PolicyError("duplicate running agent")
        seen.add(agent_id)
        actual = identifier(agent["model"]) if agent["model"] is not None else None
        if not allowed or actual not in allowed:
            stop.append(agent_id)

    required = kind in ("critique", "review")
    unknown = [name for name, value in (("initial", initial), ("current", main),
                                       ("available", available), ("resolution", resolution)) if not value]
    result = {"action": "direct", "reason": None, "selected": None, "allowed": sorted(allowed),
              "candidates": sorted(candidates), "unconfirmed": unknown,
              "stop_and_mark_unconfirmed": stop}
    preferred = [main] if main in candidates else []
    if not required and kind == "read" and call.get("simple") and not call.get("recovery"):
        preferred = sorted(candidates - {main}) + preferred
    result["preferred"] = preferred

    def deny(reason, wait=False):
        action = ("wait" if wait else
                  {"critique": "critique_incomplete", "review": "review_self_check"}.get(kind, "direct"))
        return dict(result, action=action, reason=reason)

    # Validate any supplied, current resolution even if an earlier gate denies the call.
    if resolution is not None:
        fields(resolution, ("mode", "requested", "model", "settings_supported", "within_main_effort"),
               ("reasoning_effort",))
        if resolution.get("reasoning_effort") is not None:
            identifier(resolution["reasoning_effort"])
        identifier(resolution["model"])
        boolean(resolution["settings_supported"])
        boolean(resolution["within_main_effort"])
        if resolution["mode"] not in ("explicit", "inherit"):
            raise PolicyError("invalid resolved mode")
        if resolution["mode"] == "explicit":
            identifier(resolution["requested"])
        elif resolution["requested"] is not None:
            raise PolicyError("invalid resolved inheritance request")

    if not call["permitted"] or not call["by_main"]:
        return deny("authority")
    if required and not call.get("isolated"):
        return deny("isolation_unconfirmed")
    if not required and not (call.get("independent") and call.get("worthwhile")):
        return deny("direct_work_preferred")
    if kind == "implement" and not call.get("sole_writer"):
        return deny("single_writer_unconfirmed")
    if stop:
        return deny("running_agents_need_stop")
    if budget["retries_used"]:
        return deny("recovery_budget")
    if unknown:
        return deny("evidence_missing_or_stale")
    if (resolution["mode"] != mode or resolution["requested"] != requested
            or resolution.get("reasoning_effort") != effort
            or (proofs["resolution"]["source"] == "guaranteed_inheritance" and mode != "inherit")):
        return deny("resolution_does_not_match_request")
    model = resolution["model"]
    expected = main if mode == "inherit" else requested
    if model != expected:
        return deny("host_override")
    if model not in candidates:
        return deny("model_not_allowed_or_available")
    if call.get("recovery") and model != main and not required:
        return deny("recovery_requires_main_model")
    if request.get("policy") is None and mode != "inherit":
        return deny("no_local_policy_use_safe_inheritance")
    if not resolution["settings_supported"] or not resolution["within_main_effort"]:
        return deny("settings_unconfirmed")
    if not budget["free_slots"] or (not required and budget["active_optional"] >= 2):
        return deny("no_slot", wait=True)
    return dict(result, action="inherit" if mode == "inherit" else "select",
                selected=model, reason="within_confirmed_ceiling")


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise PolicyError("duplicate JSON field")
        result[key] = value
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("inspect", "resolve"))
    args = parser.parse_args(argv)
    try:
        request = json.load(sys.stdin, object_pairs_hook=unique_object)
        if args.command == "inspect":
            fields(request, ("host", "policy"))
            lower = check_policy(request["policy"], identifier(request["host"]))
            output = {"configured": request["policy"] is not None,
                      "direct_relationships": {parent: sorted(children) for parent, children in lower.items()}}
        else:
            output = resolve(request)
    except (ValueError, TypeError, RecursionError) as error:
        print(json.dumps({"action": "invalid", "reason": str(error)}))
        return 2
    print(json.dumps(output, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
