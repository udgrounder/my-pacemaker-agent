# MPA TOML Reference Profile V1

agent_reference.toml is an experimental, inspect-only Runtime reference contract. External consumers may discover, read, and validate it only. Its authority value is not-invokable: it grants no hook execution, file mutation, approval, or deployment authority. The validator CLI is a supported read-only validation tool, not an agent-control API.

## Discovery and failure

Discover only .mpa/runtime/contracts/agent_reference.toml from the project root. If the file, Runtime root, or a reference has a symlink, is missing, or is invalid, consumers report the result and stop. They must not approve, modify, deploy, or execute hooks.

The validator emits one JSON line with code, field_id, path, and message.

| Code | Meaning |
|---|---|
| 0 | valid V1 contract |
| 20 | unsupported protocol or version |
| 21 | profile or schema failure |
| 22 | unsafe or unresolved reference |
| 23 | semantic drift from a Markdown binding |

## V1 syntax

The file is UTF-8 without BOM. Blank lines and full-line comments beginning with # are permitted. Tables are limited to [contract], [paths], [[lifecycle]], and [[references]]. Keys use lowercase ASCII letters, digits, and underscore.

Values are one-line double-quoted strings, non-negative integers, and arrays of double-quoted strings. JSON-compatible string escapes are allowed; trailing array commas are not. Inline comments, dotted or quoted keys, multiline strings, dates, floats, booleans, inline tables, table redeclaration, and unknown keys or tables are rejected.

This is a deliberate standard-TOML subset, not a general TOML parser. Valid fixtures must also parse with an independent standard parser during development. Extending the profile requires a new contract_version and compatibility review.

## Schema and provenance

[contract] has protocol, contract_version, profile, maturity, usage, authority, and discovery_path. V1 accepts mpa-agent-reference, 1, mpa-toml-v1, experimental, inspect-only, and not-invokable only.

[paths] has tasks_root and docs_root. Their literals must match these markers in core/agent_rules.md:

    <!-- mpa-contract:paths.tasks_root=workspace/tasks -->
    <!-- mpa-contract:paths.docs_root=docs -->

Each [[lifecycle]] has field_id, track, owner_path, owner_anchor, usage, authority, state_ids, labels_ko, and transitions. Its marker preserves each id|label pair and transition order. An id change or transition removal is breaking; a label change also needs external-consumer compatibility review.

Each [[references]] has field_id, owner_kind, owner_path, owner_anchor, usage, and authority. V1 only permits markdown_file and markdown_section owners. The owner must be a regular Markdown file below the Runtime root and its anchor must be an explicit <a id="..."></a> marker. All references use inspect-only and not-invokable.

V1 rejects unknown keys and tables. It also fixes the V1 path values, lifecycle, and reference field sets, so a producer that adds a field or changes a meaning publishes a new contract_version; older consumers stop safely with code 20. A repeated Markdown binding marker is semantic drift. The JSON diagnostic guarantee applies to contract discovery and validation input, not invalid command-line syntax rejected by argparse.
