CONNECTOR_TEST_HARNESS_SCHEMA_VERSION = "connector-test-harness-v0.1"


def _test_cases(connector):
    adapter_id = connector.get("adapter_id")
    output = connector.get("output_contract") or {}
    input_contract = connector.get("input_contract") or {}
    artifact = output.get("artifact_name")
    source_id = output.get("source_id")
    fields = list((output.get("normalized_evidence_payload") or {}).keys())
    return [
        {
            "name": "health check is deterministic",
            "kind": "probe",
            "command": f"GET /adapters/{adapter_id}/probe",
            "expected": "Probe returns passed, missing, failed, or skipped checks with plain details.",
            "failure_means": "The connector is not ready to run evidence.",
        },
        {
            "name": "run returns a complete normalized artifact",
            "kind": "run",
            "command": f"POST /adapters/{adapter_id}/run?model_id={{model_id}}&target_profile={{target_profile}}&calibration_profile={{calibration_profile}}&modality={{modality}}&runtime_mode={{runtime_mode}}",
            "expected": f"Run status is completed and response includes {artifact} for source {source_id}.",
            "required_fields": fields,
            "failure_means": "The connector may have raw output, but it has not produced importable evidence.",
        },
        {
            "name": "validation rejects incomplete payloads",
            "kind": "negative validation",
            "command": f"POST /evidence/validate?package_id={{package_id}}&source_id={source_id}",
            "expected": "Deleting any required field produces validation errors and no import.",
            "required_fields": fields,
            "failure_means": "The connector contract is too weak to protect claims.",
        },
        {
            "name": "validation accepts complete payloads",
            "kind": "positive validation",
            "command": f"POST /evidence/validate?package_id={{package_id}}&source_id={source_id}",
            "expected": "A complete normalized payload validates and previews claim impact before import.",
            "required_fields": fields,
            "failure_means": "The connector output shape does not match the backend evidence schema.",
        },
        {
            "name": "import is explicit and auditable",
            "kind": "import",
            "command": f"POST /evidence/import?package_id={{package_id}}&source_id={source_id}",
            "expected": "Import stores the artifact, raw references, provenance, and refreshed claim readiness.",
            "failure_means": "The evidence path is not ready for review or archive.",
        },
        {
            "name": "failed runs do not upgrade claims",
            "kind": "safety",
            "command": "simulate connector status=failed",
            "expected": "Failed or partial connector output is not imported and related claims stay blocked or needs review.",
            "failure_means": "The system can overclaim from incomplete evidence.",
        },
    ]


def build_connector_test_harness(connector_implementation_guide, package_report=None):
    harnesses = []
    for connector in (connector_implementation_guide or {}).get("connectors", []):
        test_cases = _test_cases(connector)
        harnesses.append({
            "adapter_id": connector.get("adapter_id"),
            "name": connector.get("name"),
            "phase": connector.get("phase"),
            "build_first": connector.get("build_first"),
            "readiness_status": connector.get("readiness_status"),
            "source_id": (connector.get("output_contract") or {}).get("source_id"),
            "artifact_name": (connector.get("output_contract") or {}).get("artifact_name"),
            "request_env_vars": (connector.get("input_contract") or {}).get("env_vars", []),
            "test_cases": test_cases,
            "pass_rule": "All probe, run, validation, import, and failure-safety tests must pass before connector output can be used in claim readiness.",
        })
    build_first = [item for item in harnesses if item["build_first"]]
    return {
        "result_type": "connector_test_harness",
        "schema_version": CONNECTOR_TEST_HARNESS_SCHEMA_VERSION,
        "provenance": "derived from connector implementation guide",
        "confidence": "medium" if harnesses else "low",
        "package_id": (package_report or {}).get("package_id") or (connector_implementation_guide or {}).get("package_id"),
        "summary": {
            "total_harnesses": len(harnesses),
            "build_first_harnesses": len(build_first),
            "total_test_cases": sum(len(item["test_cases"]) for item in harnesses),
            "plain_reading": "This harness lists the checks an external connector must pass before its evidence can safely affect claims.",
        },
        "harnesses": harnesses,
        "harness_rule": "A connector can be connected, useful, and still not evidence until its normalized artifact validates, imports, archives, and preserves failure safety.",
    }
