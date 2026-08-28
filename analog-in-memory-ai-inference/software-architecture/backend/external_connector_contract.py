EXTERNAL_CONNECTOR_CONTRACT_SCHEMA_VERSION = "external-connector-contract-v0.1"


CONNECTOR_ENDPOINTS = {
    "quantization.onnxruntime": {
        "mode": "local library or worker service",
        "health": "import onnxruntime or GET /health on a quantization worker",
        "run": "quantize model with calibration data and return a quantized model reference plus calibration metrics",
        "timeout_seconds": 600,
    },
    "compiler.tvm-mlir-iree": {
        "mode": "compiler CLI, library, or compile service",
        "health": "GET ${ANALOG_AI_COMPILER_API_URL}/health or verify compiler binary, target description, and supported operator table",
        "run": "compile or map the model and return placement, tiling, memory, and unsupported-operator reports",
        "timeout_seconds": 900,
    },
    "analog.error-simulator": {
        "mode": "behavioral simulator, SPICE-backed service, or calibrated lookup model",
        "health": "verify device model, ADC/DAC model, temperature range, voltage range, and calibration profile",
        "run": "simulate analog numeric error for mapped operators and return accuracy-impact evidence",
        "timeout_seconds": 1200,
    },
    "accuracy.local-task-check": {
        "mode": "dataset metric runner",
        "health": "GET ${ANALOG_AI_ACCURACY_API_URL}/health or verify dataset path, labels, metric definition, baseline outputs, and candidate outputs",
        "run": "compute the workload metric and return baseline, candidate, delta, tolerance, and pass/fail",
        "timeout_seconds": 900,
    },
    "board.runtime": {
        "mode": "board runtime service or prototype-control service",
        "health": "GET ${ANALOG_AI_BOARD_API_URL}/health with board ID and runtime version available",
        "run": "load the package, execute replay inputs, and return latency samples, fallback events, and trace metadata",
        "timeout_seconds": 900,
    },
    "metrics.power-thermal": {
        "mode": "power meter and temperature collector service",
        "health": "GET ${ANALOG_AI_POWER_METER_URL}/health with channel and temperature sensor configured",
        "run": "capture synchronized power, energy, and temperature data for the board-runtime trace window",
        "timeout_seconds": 900,
    },
}


def _by_adapter(report, key):
    return {
        item.get("adapter_id"): item
        for item in (report or {}).get(key, [])
        if item.get("adapter_id")
    }


def _request_shape(adapter_id, kit, readiness):
    return {
        "package_id": "{package_id}",
        "model_id": "{model_id}",
        "adapter_id": adapter_id,
        "target_profile": "{target_profile}",
        "calibration_profile": "{calibration_profile}",
        "modality": "{modality}",
        "runtime_mode": "{runtime_mode}",
        "raw_inputs": kit.get("raw_inputs", []),
        "env_vars": kit.get("env_vars", []),
        "expected_artifact": readiness.get("expected_artifact") or kit.get("normalized_artifact"),
    }


def _response_shape(kit, readiness):
    return {
        "status": "completed | failed | skipped",
        "source_id": readiness.get("source_id") or kit.get("normalized_source_id"),
        "artifact_name": readiness.get("expected_artifact") or kit.get("normalized_artifact"),
        "normalized_evidence_payload": {
            field: "<required>"
            for field in kit.get("minimum_fields", [])
        },
        "raw_output_references": [
            "path, URI, run ID, board trace ID, compiler log ID, or measurement capture ID"
        ],
        "provenance": {
            "tool_name": "<tool or service name>",
            "tool_version": "<version>",
            "operator": "<person, lab, or automation>",
            "run_started_at": "<ISO-8601 timestamp>",
            "run_finished_at": "<ISO-8601 timestamp>",
        },
    }


def _failure_contract(adapter_id):
    return {
        "adapter_id": adapter_id,
        "status": "failed",
        "errors": ["plain reason the connector could not produce a normalized artifact"],
        "safe_behavior": "Do not import partial evidence. Keep the raw logs, report the failure, and leave related claims blocked or needs review.",
    }


def build_external_connector_contract(
    adapter_connection_kit,
    adapter_integration_readiness,
    package_report=None,
):
    kit_by_adapter = _by_adapter(adapter_connection_kit, "adapters")
    readiness_by_adapter = _by_adapter(adapter_integration_readiness, "readiness_targets")
    connectors = []
    for adapter_id in sorted(kit_by_adapter):
        kit = kit_by_adapter[adapter_id]
        readiness = readiness_by_adapter.get(adapter_id, {})
        endpoint = CONNECTOR_ENDPOINTS.get(adapter_id, {})
        connectors.append({
            "adapter_id": adapter_id,
            "name": kit.get("name"),
            "connection_type": kit.get("connection_type"),
            "mode": endpoint.get("mode", "external tool or service"),
            "health_check": endpoint.get("health", "verify the tool can be reached and configured"),
            "run_contract": endpoint.get("run", "produce a normalized evidence artifact"),
            "timeout_seconds": endpoint.get("timeout_seconds", 900),
            "readiness_status": readiness.get("status", "needs setup"),
            "request_shape": _request_shape(adapter_id, kit, readiness),
            "response_shape": _response_shape(kit, readiness),
            "failure_contract": _failure_contract(adapter_id),
            "validation_endpoint": (kit.get("commands") or {}).get("validate"),
            "import_endpoint": (kit.get("commands") or {}).get("import"),
            "claim_boundary": kit.get("claim_boundary"),
            "do_not_claim": kit.get("do_not_claim"),
        })
    return {
        "result_type": "external_connector_contract",
        "schema_version": EXTERNAL_CONNECTOR_CONTRACT_SCHEMA_VERSION,
        "provenance": "derived from adapter connection kit and adapter integration readiness",
        "confidence": "medium" if connectors else "low",
        "package_id": (package_report or {}).get("package_id"),
        "summary": {
            "total_connectors": len(connectors),
            "ready_or_local": sum(1 for item in connectors if item["readiness_status"] in {"ready to produce evidence", "local workflow ready"}),
            "blocked": sum(1 for item in connectors if item["readiness_status"].startswith("blocked")),
            "plain_reading": "This is the contract an external compiler, simulator, board service, meter, or accuracy runner must satisfy before its output can affect claims.",
        },
        "connectors": connectors,
        "contract_rule": "A connector is accepted only when it returns a normalized artifact that validates, imports, archives, and keeps raw-output references for audit.",
    }
