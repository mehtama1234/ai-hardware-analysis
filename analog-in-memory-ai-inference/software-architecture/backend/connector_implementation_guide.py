CONNECTOR_IMPLEMENTATION_GUIDE_SCHEMA_VERSION = "connector-implementation-guide-v0.1"


PHASE_ORDER = {
    "accuracy.local-task-check": 1,
    "compiler.tvm-mlir-iree": 2,
    "board.runtime": 3,
    "metrics.power-thermal": 4,
    "analog.error-simulator": 5,
    "quantization.onnxruntime": 6,
}


def _phase_name(priority):
    return {
        1: "prove the metric path",
        2: "replace placement estimates",
        3: "run on target hardware or simulator",
        4: "count energy and heat",
        5: "model analog numeric behavior",
        6: "replace quantization estimates",
    }.get(priority, "connect remaining tool")


def _done_criteria(connector):
    artifact = (connector.get("response_shape") or {}).get("artifact_name")
    source_id = (connector.get("response_shape") or {}).get("source_id")
    return [
        f"The connector health check is deterministic: {connector.get('health_check')}.",
        f"The run path returns {artifact} for source {source_id}.",
        "The normalized payload passes backend validation before import.",
        "The raw logs, run IDs, tool versions, and target settings are preserved for audit.",
        "A failed run does not import partial evidence or upgrade any claim.",
    ]


def _implementation_steps(connector):
    request = connector.get("request_shape") or {}
    response = connector.get("response_shape") or {}
    return [
        {
            "name": "wrap the real tool",
            "detail": f"Create a thin adapter around {connector.get('mode')} that accepts package, model, target, calibration, modality, and runtime settings.",
        },
        {
            "name": "normalize the output",
            "detail": f"Translate raw output into {response.get('artifact_name')} with fields {', '.join((response.get('normalized_evidence_payload') or {}).keys())}.",
        },
        {
            "name": "validate before import",
            "detail": f"Call {connector.get('validation_endpoint')} and show validation errors before saving evidence.",
        },
        {
            "name": "import only complete evidence",
            "detail": f"Call {connector.get('import_endpoint')} only when status is completed and raw references are available.",
        },
        {
            "name": "surface failure plainly",
            "detail": (connector.get("failure_contract") or {}).get("safe_behavior", "Leave claims blocked when the connector fails."),
        },
    ]


def build_connector_implementation_guide(external_connector_contract, adapter_integration_readiness=None, package_report=None):
    connectors = []
    for connector in (external_connector_contract or {}).get("connectors", []):
        adapter_id = connector.get("adapter_id")
        priority = PHASE_ORDER.get(adapter_id, 99)
        connectors.append({
            "adapter_id": adapter_id,
            "name": connector.get("name"),
            "phase": priority,
            "phase_name": _phase_name(priority),
            "readiness_status": connector.get("readiness_status"),
            "build_first": priority <= 4,
            "why_this_order": "This connector moves the system from estimates toward checked evidence." if priority <= 4 else "This connector improves fidelity after the core evidence loop works.",
            "input_contract": connector.get("request_shape"),
            "output_contract": connector.get("response_shape"),
            "implementation_steps": _implementation_steps(connector),
            "done_criteria": _done_criteria(connector),
            "claim_boundary": connector.get("claim_boundary"),
            "do_not_claim": connector.get("do_not_claim"),
        })
    connectors = sorted(connectors, key=lambda item: (item["phase"], item["adapter_id"] or ""))
    first_four = [item["name"] for item in connectors if item["build_first"]][:4]
    return {
        "result_type": "connector_implementation_guide",
        "schema_version": CONNECTOR_IMPLEMENTATION_GUIDE_SCHEMA_VERSION,
        "provenance": "derived from external connector contract and adapter integration readiness",
        "confidence": "medium" if connectors else "low",
        "package_id": (package_report or {}).get("package_id") or (external_connector_contract or {}).get("package_id"),
        "summary": {
            "total_connectors": len(connectors),
            "build_first_count": sum(1 for item in connectors if item["build_first"]),
            "first_build_targets": first_four,
            "plain_reading": "This guide turns connector contracts into an implementation order with done criteria for real compiler, simulator, board, meter, and accuracy integrations.",
        },
        "connectors": connectors,
        "rollout_rule": "Build the smallest evidence loop first: task metric, compiler placement, board runtime, and synchronized power. Add deeper analog simulation and quantization automation after that loop is reliable.",
    }
