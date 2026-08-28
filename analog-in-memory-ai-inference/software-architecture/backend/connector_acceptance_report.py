CONNECTOR_ACCEPTANCE_REPORT_SCHEMA_VERSION = "connector-acceptance-report-v0.1"


def _by_adapter(report, key):
    return {
        item.get("adapter_id"): item
        for item in (report or {}).get(key, [])
        if item.get("adapter_id")
    }


def _sources_by_id(measurement_evidence):
    return {
        item.get("id"): item
        for item in (measurement_evidence or {}).get("required_sources", [])
        if item.get("id")
    }


def _drills_by_adapter(connector_acceptance_drills):
    return {
        item.get("adapter_id"): item
        for item in (connector_acceptance_drills or {}).get("drills", [])
        if item.get("adapter_id")
    }


def _latest_payload(source):
    return ((source or {}).get("latest_import") or {}).get("payload") or {}


def _is_replay_fixture(source):
    payload = _latest_payload(source)
    provenance = payload.get("provenance") or {}
    return bool(
        (payload.get("external_replay_fixture") or {}).get("enabled")
        or provenance.get("external_replay_fixture") is True
        or ((payload.get("measurement_setup") or {}).get("external_replay_fixture") is True)
    )


def _case_status(test_case, probe, source, drill=None):
    kind = test_case.get("kind")
    source_status = (source or {}).get("status")
    probe_status = (probe or {}).get("probe_status")
    replay_fixture = _is_replay_fixture(source)
    if kind == "probe":
        if probe_status == "ready":
            return "passed by replay fixture" if replay_fixture else "passed"
        if probe_status == "informational":
            return "informational"
        return "blocked"
    if kind in {"run", "positive validation", "import"}:
        if source_status == "imported artifact":
            return "passed by replay fixture" if replay_fixture else "passed"
        if source_status in {"configured", "local estimate"}:
            return "pending evidence"
        return "blocked"
    if kind == "negative validation":
        negative = (drill or {}).get("negative_validation") or {}
        if negative.get("status") == "passed":
            return "passed"
        if negative.get("status") == "failed":
            return "failed"
        return "pending explicit negative test"
    if kind == "safety":
        safety = (drill or {}).get("failure_safety") or {}
        if safety.get("status") == "passed":
            return "passed"
        if safety.get("status") == "failed":
            return "failed"
        return "covered by rule, needs failure drill"
    return "pending"


def _overall_status(case_results):
    statuses = {item["status"] for item in case_results}
    if "blocked" in statuses or "failed" in statuses:
        return "blocked"
    if "passed by replay fixture" in statuses:
        return "replay accepted"
    if "pending evidence" in statuses or "pending explicit negative test" in statuses:
        return "pending"
    if "covered by rule, needs failure drill" in statuses:
        return "needs failure drill"
    return "accepted"


def _acceptance_mode(source):
    if _is_replay_fixture(source):
        return "replay fixture"
    if (source or {}).get("status") == "imported artifact":
        return "imported evidence"
    if (source or {}).get("status") == "configured":
        return "configured only"
    return (source or {}).get("status", "not connected")


def _next_action(overall, replay_fixture):
    if overall == "blocked":
        return "Fix blocked probe checks before calling this an external connector."
    if overall == "replay accepted":
        return "Replay has proven the request, response, validation, import, and archive shape. Replace it with real service output before external acceptance."
    if overall != "accepted":
        return "Run the pending negative and failure-safety drills before final acceptance."
    if replay_fixture:
        return "Replay is complete, but measured claims still need real service output."
    return "Keep raw references and versions with the accepted evidence."


def build_connector_acceptance_report(
    connector_test_harness,
    adapter_connection_self_test,
    measurement_evidence,
    connector_acceptance_drills=None,
    package_report=None,
):
    probes = _by_adapter(adapter_connection_self_test, "results")
    sources = _sources_by_id(measurement_evidence)
    drills = _drills_by_adapter(connector_acceptance_drills)
    connectors = []
    for harness in (connector_test_harness or {}).get("harnesses", []):
        source = sources.get(harness.get("source_id"), {})
        probe = probes.get(harness.get("adapter_id"), {})
        drill = drills.get(harness.get("adapter_id"), {})
        replay_fixture = _is_replay_fixture(source)
        case_results = []
        for test_case in harness.get("test_cases", []):
            status = _case_status(test_case, probe, source, drill=drill)
            case_results.append({
                "name": test_case.get("name"),
                "kind": test_case.get("kind"),
                "status": status,
                "command": test_case.get("command"),
                "expected": test_case.get("expected"),
                "failure_means": test_case.get("failure_means"),
            })
        overall = _overall_status(case_results)
        connectors.append({
            "adapter_id": harness.get("adapter_id"),
            "name": harness.get("name"),
            "source_id": harness.get("source_id"),
            "artifact_name": harness.get("artifact_name"),
            "acceptance_status": overall,
            "acceptance_mode": _acceptance_mode(source),
            "external_acceptance": overall == "accepted" and not replay_fixture,
            "replay_fixture": replay_fixture,
            "drill_status": drill.get("status", "not run"),
            "probe_status": probe.get("probe_status", "not checked"),
            "evidence_status": source.get("status", "not connected"),
            "imported_count": source.get("imported_count", 0),
            "case_results": case_results,
            "next_action": _next_action(overall, replay_fixture),
        })
    return {
        "result_type": "connector_acceptance_report",
        "schema_version": CONNECTOR_ACCEPTANCE_REPORT_SCHEMA_VERSION,
        "provenance": "derived from connector test harness, adapter self-test, and measurement evidence",
        "confidence": "medium" if connectors else "low",
        "package_id": (package_report or {}).get("package_id") or (connector_test_harness or {}).get("package_id"),
        "summary": {
            "total_connectors": len(connectors),
            "accepted": sum(1 for item in connectors if item["acceptance_status"] == "accepted"),
            "replay_accepted": sum(1 for item in connectors if item["acceptance_status"] == "replay accepted"),
            "blocked": sum(1 for item in connectors if item["acceptance_status"] == "blocked"),
            "pending": sum(1 for item in connectors if item["acceptance_status"] in {"pending", "needs failure drill", "replay accepted"}),
            "drills_passed": sum(1 for item in connectors if item.get("drill_status") == "passed"),
            "plain_reading": "This report compares the connector test harness with current probes and imported evidence. Replay fixtures can prove connector workflow shape, but only non-replay service output counts as external connector acceptance.",
        },
        "connectors": connectors,
        "acceptance_rule": "Acceptance needs both a working connection path and importable evidence. Replay fixtures test request, response, validation, import, and archive behavior; they do not prove the external service, board, meter, or hardware measurement is connected.",
    }
