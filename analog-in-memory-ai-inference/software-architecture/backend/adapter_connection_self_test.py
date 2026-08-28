from connection_playbook import CONNECTION_REQUIREMENTS


ADAPTER_CONNECTION_SELF_TEST_SCHEMA_VERSION = "adapter-connection-self-test-v0.1"


def build_adapter_connection_self_test(adapter_report, probe_fn, adapter_connection_kit=None, package_report=None):
    kit_by_adapter = {
        item.get("adapter_id"): item
        for item in (adapter_connection_kit or {}).get("adapters", [])
    }
    results = []
    for adapter in (adapter_report or {}).get("adapters", []):
        adapter_id = adapter.get("id")
        if adapter_id not in CONNECTION_REQUIREMENTS:
            continue
        probe = probe_fn(adapter_id)
        checks = (probe or {}).get("checks", [])
        summary = (probe or {}).get("summary", {})
        result_status = (probe or {}).get("status", "blocked")
        kit = kit_by_adapter.get(adapter_id, {})
        results.append({
            "adapter_id": adapter_id,
            "name": adapter.get("name"),
            "connection_type": CONNECTION_REQUIREMENTS[adapter_id]["connection_type"],
            "adapter_status": adapter.get("status"),
            "probe_status": result_status,
            "checks": checks,
            "summary": summary,
            "env_vars": kit.get("env_vars", []),
            "expected_artifact": kit.get("normalized_artifact"),
            "next_action": adapter.get("next_step"),
            "plain_reading": "Ready to run external evidence path." if result_status == "ready" else "Connection is not fully ready; inspect missing or failed checks.",
        })
    return {
        "result_type": "adapter_connection_self_test",
        "schema_version": ADAPTER_CONNECTION_SELF_TEST_SCHEMA_VERSION,
        "provenance": "derived from adapter probes at report build time",
        "confidence": "medium" if results else "low",
        "package_id": (package_report or {}).get("package_id"),
        "summary": {
            "total_adapters": len(results),
            "ready": sum(1 for item in results if item["probe_status"] == "ready"),
            "blocked": sum(1 for item in results if item["probe_status"] == "blocked"),
            "informational": sum(1 for item in results if item["probe_status"] == "informational"),
            "failed_checks": sum(int(item["summary"].get("failed") or 0) for item in results),
            "missing_checks": sum(int(item["summary"].get("missing") or 0) for item in results),
            "plain_reading": "This self-test shows whether external tool paths are configured before evidence is run or imported.",
        },
        "results": results,
        "self_test_rule": "A passed probe is not evidence. It only means the connection path is ready to produce a normalized artifact.",
    }
