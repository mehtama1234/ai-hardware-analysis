from connection_playbook import CONNECTION_REQUIREMENTS


ADAPTER_EXECUTION_PLAN_SCHEMA_VERSION = "adapter-execution-plan-v0.1"


def _source_by_category(measurement_evidence):
    sources = {}
    for source in (measurement_evidence or {}).get("required_sources", []):
        sources.setdefault(source.get("adapter_category"), source)
    return sources


def _step_status(adapter, source):
    if source.get("status") == "imported artifact":
        return "complete"
    if adapter.get("status") == "configured":
        return "ready to run external"
    if adapter.get("status") in {"available", "available dependency"}:
        return "ready to run local"
    if adapter.get("status") == "missing dependency":
        return "blocked by dependency"
    return "blocked by connection"


def _execution_steps(adapter, source, requirement):
    artifact = source.get("artifact_name", "normalized-evidence.json")
    source_id = source.get("id")
    return [
        {
            "name": "configure",
            "action": "Set the tool path, service URL, dataset, target profile, and version information needed by this adapter.",
            "done_when": "The adapter probe reports configured or locally available.",
            "configuration": requirement["configuration"],
        },
        {
            "name": "run",
            "action": f"Run {adapter.get('name')} for the current package and model.",
            "done_when": "The adapter returns status=completed or a concrete blocker.",
            "local_or_external": "external" if adapter.get("status") == "configured" else "local workflow test" if adapter.get("status") in {"available", "available dependency"} else "not runnable yet",
        },
        {
            "name": "normalize",
            "action": f"Convert raw tool output into {artifact}.",
            "done_when": f"The JSON payload has source_id={source_id} and all required fields.",
            "minimum_fields": source.get("minimum_fields", []),
        },
        {
            "name": "validate_preview",
            "action": "Call POST /evidence/validate and inspect before/after claim readiness.",
            "done_when": "Validation passes and the preview shows exactly which claims move, remain blocked, or need review.",
        },
        {
            "name": "import_archive",
            "action": "Call POST /evidence/import only after validation passes, then refresh package evidence panels and archive.",
            "done_when": "The artifact appears under imported evidence and claim readiness reflects the new latest evidence.",
        },
    ]


def build_adapter_execution_plan(adapter_report, measurement_evidence, connection_playbook=None, package_report=None):
    sources = _source_by_category(measurement_evidence or {})
    connection_by_adapter = {
        item.get("adapter_id"): item
        for item in (connection_playbook or {}).get("connection_targets", [])
    }
    rows = []
    for adapter in (adapter_report or {}).get("adapters", []):
        requirement = CONNECTION_REQUIREMENTS.get(adapter.get("id"))
        if not requirement:
            continue
        source = sources.get(adapter.get("category"), {})
        status = _step_status(adapter, source)
        rows.append({
            "adapter_id": adapter.get("id"),
            "name": adapter.get("name"),
            "category": adapter.get("category"),
            "status": status,
            "adapter_status": adapter.get("status"),
            "connection_type": requirement["connection_type"],
            "normalized_source_id": source.get("id"),
            "normalized_artifact": source.get("artifact_name", "not required"),
            "claim_boundary": requirement["proves"],
            "do_not_claim": requirement["do_not_claim"],
            "next_action": connection_by_adapter.get(adapter.get("id"), {}).get("next_action") or adapter.get("next_step"),
            "steps": _execution_steps(adapter, source, requirement),
        })
    return {
        "result_type": "adapter_execution_plan",
        "schema_version": ADAPTER_EXECUTION_PLAN_SCHEMA_VERSION,
        "provenance": "derived from adapter registry, connection playbook, and measurement evidence contract",
        "confidence": "medium" if rows else "low",
        "package_id": (package_report or {}).get("package_id") or (measurement_evidence or {}).get("summary", {}).get("package_id"),
        "summary": {
            "total_adapters": len(rows),
            "complete": sum(1 for item in rows if item["status"] == "complete"),
            "ready_to_run": sum(1 for item in rows if item["status"] in {"ready to run local", "ready to run external"}),
            "blocked": sum(1 for item in rows if item["status"].startswith("blocked")),
            "plain_reading": "This is the operating sequence for turning an adapter connection into claim-safe evidence.",
        },
        "execution_targets": rows,
        "pipeline_rule": "Every adapter must finish the same path: configure, run, normalize, validate preview, import, archive.",
    }
