ADAPTER_INTEGRATION_READINESS_SCHEMA_VERSION = "adapter-integration-readiness-v0.1"


def _by_adapter(report, key):
    return {
        item.get("adapter_id"): item
        for item in (report or {}).get(key, [])
        if item.get("adapter_id")
    }


def _status(execution, template, self_test):
    execution_status = execution.get("status") or "needs setup"
    probe_status = self_test.get("probe_status")
    template_valid = template.get("template_valid")
    if execution_status == "complete":
        return "complete"
    if probe_status == "ready" and template_valid:
        return "ready to produce evidence"
    if execution_status == "ready to run local" and template_valid:
        return "local workflow ready"
    if probe_status == "blocked":
        return "blocked by connection"
    if template and not template_valid:
        return "blocked by evidence template"
    return execution_status


def _priority(status):
    return {
        "ready to produce evidence": 1,
        "local workflow ready": 2,
        "blocked by connection": 3,
        "blocked by evidence template": 4,
        "complete": 99,
    }.get(status, 5)


def _reason(status, execution, template, self_test):
    if status == "complete":
        return "The adapter already has imported evidence in the package."
    if status == "ready to produce evidence":
        return "The connection probe is ready and the normalized evidence payload shape is valid."
    if status == "local workflow ready":
        return "The local adapter path can run and emit a valid normalized evidence payload."
    if status == "blocked by connection":
        missing = int((self_test.get("summary") or {}).get("missing") or 0)
        failed = int((self_test.get("summary") or {}).get("failed") or 0)
        return f"The evidence template is useful, but the tool path still has {missing} missing and {failed} failed probe checks."
    if status == "blocked by evidence template":
        errors = template.get("validation_errors") or []
        return "The adapter needs a valid normalized evidence payload before import. " + " ".join(errors)
    return execution.get("next_action") or "Check the adapter execution plan and connection kit."


def build_adapter_integration_readiness(
    adapter_execution_plan,
    adapter_connection_kit,
    adapter_evidence_templates,
    adapter_connection_self_test,
    package_report=None,
):
    execution_by_adapter = _by_adapter(adapter_execution_plan, "execution_targets")
    kit_by_adapter = _by_adapter(adapter_connection_kit, "adapters")
    template_by_adapter = _by_adapter(adapter_evidence_templates, "templates")
    self_test_by_adapter = _by_adapter(adapter_connection_self_test, "results")
    adapter_ids = sorted(
        set(execution_by_adapter)
        | set(kit_by_adapter)
        | set(template_by_adapter)
        | set(self_test_by_adapter)
    )
    targets = []
    for adapter_id in adapter_ids:
        execution = execution_by_adapter.get(adapter_id, {})
        kit = kit_by_adapter.get(adapter_id, {})
        template = template_by_adapter.get(adapter_id, {})
        self_test = self_test_by_adapter.get(adapter_id, {})
        status = _status(execution, template, self_test)
        checks = self_test.get("summary") or {}
        target = {
            "adapter_id": adapter_id,
            "name": execution.get("name") or kit.get("name") or template.get("name") or self_test.get("name"),
            "status": status,
            "priority": _priority(status),
            "connection_type": kit.get("connection_type") or execution.get("connection_type") or self_test.get("connection_type"),
            "expected_artifact": kit.get("normalized_artifact") or template.get("artifact_name") or self_test.get("expected_artifact"),
            "source_id": template.get("source_id") or execution.get("normalized_source_id"),
            "probe_status": self_test.get("probe_status"),
            "execution_status": execution.get("status"),
            "template_valid": template.get("template_valid"),
            "missing_checks": int(checks.get("missing") or 0),
            "failed_checks": int(checks.get("failed") or 0),
            "env_vars": kit.get("env_vars", []),
            "next_action": execution.get("next_action") or self_test.get("next_action") or kit.get("handoff_note"),
            "reason": _reason(status, execution, template, self_test),
        }
        targets.append(target)

    active_targets = [item for item in targets if item["status"] != "complete"]
    next_priorities = sorted(active_targets, key=lambda item: (item["priority"], item["adapter_id"]))[:4]
    summary = {
        "total_adapters": len(targets),
        "complete": sum(1 for item in targets if item["status"] == "complete"),
        "ready": sum(1 for item in targets if item["status"] == "ready to produce evidence"),
        "local_ready": sum(1 for item in targets if item["status"] == "local workflow ready"),
        "blocked": sum(1 for item in targets if item["status"].startswith("blocked")),
        "first_priority": next_priorities[0]["name"] if next_priorities else "none",
        "plain_reading": "This report combines adapter plans, connection setup, evidence templates, and probe checks into the next concrete connection work.",
    }
    return {
        "result_type": "adapter_integration_readiness",
        "schema_version": ADAPTER_INTEGRATION_READINESS_SCHEMA_VERSION,
        "provenance": "derived from adapter execution plan, connection kit, evidence templates, and connection self-test",
        "confidence": "medium" if targets else "low",
        "package_id": (package_report or {}).get("package_id"),
        "summary": summary,
        "readiness_targets": targets,
        "next_priorities": next_priorities,
        "readiness_rule": "Ready means the path can produce normalized evidence. It does not mean the hardware claim is proven.",
    }
