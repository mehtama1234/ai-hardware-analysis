from connection_playbook import CONNECTION_REQUIREMENTS


ADAPTER_CONNECTION_KIT_SCHEMA_VERSION = "adapter-connection-kit-v0.1"


ENV_VARS = {
    "quantization.onnxruntime": ["PYTHONPATH", "ORT_CALIBRATION_DATASET"],
    "compiler.tvm-mlir-iree": ["ANALOG_AI_COMPILER_API_URL", "TVM_HOME", "MLIR_OPT", "IREE_COMPILE", "ANALOG_AI_TARGET_DESC"],
    "analog.error-simulator": ["ANALOG_AI_ERROR_SIM_URL", "ANALOG_AI_DEVICE_MODEL_PATH"],
    "accuracy.local-task-check": ["ANALOG_AI_ACCURACY_API_URL", "ANALOG_AI_DATASET_PATH"],
    "board.runtime": ["ANALOG_AI_BOARD_API_URL", "ANALOG_AI_BOARD_ID", "ANALOG_AI_RUNTIME_VERSION"],
    "metrics.power-thermal": ["ANALOG_AI_POWER_METER_URL", "ANALOG_AI_POWER_CHANNEL", "ANALOG_AI_TEMP_SENSOR"],
}


RAW_INPUTS = {
    "quantization.onnxruntime": ["source ONNX model", "calibration or reference dataset", "target precision policy"],
    "compiler.tvm-mlir-iree": ["source ONNX model", "hardware target description", "supported operator list", "memory and tiling constraints"],
    "analog.error-simulator": ["compiler placement artifact", "device variation model", "ADC/DAC model", "temperature and voltage sweep"],
    "accuracy.local-task-check": ["task dataset", "baseline predictions", "candidate predictions", "metric and tolerance"],
    "board.runtime": ["deployment package", "board identifier", "runtime version", "input vectors or replay trace"],
    "metrics.power-thermal": ["runtime trace", "power meter channel", "sampling rate", "temperature sensor path"],
}


RAW_OUTPUTS = {
    "quantization.onnxruntime": ["quantized model", "calibration log", "layer sensitivity report"],
    "compiler.tvm-mlir-iree": ["placement log", "tiling plan", "memory plan", "unsupported operator report"],
    "analog.error-simulator": ["numeric error samples", "calibration sweep", "accuracy impact summary"],
    "accuracy.local-task-check": ["metric report", "per-record failures", "baseline and candidate score summary"],
    "board.runtime": ["runtime trace", "latency samples", "fallback events", "board status"],
    "metrics.power-thermal": ["power samples", "temperature samples", "energy integration report"],
}


def _source_by_category(measurement_evidence):
    sources = {}
    for source in (measurement_evidence or {}).get("required_sources", []):
        sources.setdefault(source.get("adapter_category"), source)
    return sources


def _command_examples(adapter_id, source_id, artifact):
    return {
        "probe": f"GET /adapters/{adapter_id}/probe",
        "run": f"POST /adapters/{adapter_id}/run?model_id={{model_id}}&target_profile={{target_profile}}&calibration_profile={{calibration_profile}}&modality={{modality}}&runtime_mode={{runtime_mode}}",
        "validate": f"POST /evidence/validate?package_id={{package_id}}&source_id={source_id}",
        "import": f"POST /evidence/import?package_id={{package_id}}&source_id={source_id}",
        "expected_artifact": artifact,
    }


def build_adapter_connection_kit(adapter_report, measurement_evidence, adapter_execution_plan=None, package_report=None):
    sources = _source_by_category(measurement_evidence or {})
    execution_by_adapter = {
        item.get("adapter_id"): item
        for item in (adapter_execution_plan or {}).get("execution_targets", [])
    }
    adapters = []
    for adapter in (adapter_report or {}).get("adapters", []):
        requirement = CONNECTION_REQUIREMENTS.get(adapter.get("id"))
        if not requirement:
            continue
        source = sources.get(adapter.get("category"), {})
        source_id = source.get("id", "unknown_source")
        artifact = source.get("artifact_name", "normalized-evidence.json")
        adapters.append({
            "adapter_id": adapter.get("id"),
            "name": adapter.get("name"),
            "connection_type": requirement["connection_type"],
            "current_status": adapter.get("status"),
            "env_vars": ENV_VARS.get(adapter.get("id"), []),
            "configuration_needed": requirement["configuration"],
            "raw_inputs": RAW_INPUTS.get(adapter.get("id"), []),
            "raw_outputs": RAW_OUTPUTS.get(adapter.get("id"), []),
            "normalized_source_id": source_id,
            "normalized_artifact": artifact,
            "minimum_fields": source.get("minimum_fields", []),
            "commands": _command_examples(adapter.get("id"), source_id, artifact),
            "claim_boundary": requirement["proves"],
            "do_not_claim": requirement["do_not_claim"],
            "execution_status": execution_by_adapter.get(adapter.get("id"), {}).get("status", "not planned"),
            "handoff_note": "Keep raw outputs for audit, but only the normalized artifact should move claim readiness.",
        })
    return {
        "result_type": "adapter_connection_kit",
        "schema_version": ADAPTER_CONNECTION_KIT_SCHEMA_VERSION,
        "provenance": "derived from adapter registry, measurement evidence contract, and execution plan",
        "confidence": "medium" if adapters else "low",
        "package_id": (package_report or {}).get("package_id") or (measurement_evidence or {}).get("summary", {}).get("package_id"),
        "summary": {
            "total_adapters": len(adapters),
            "configured_or_available": sum(1 for item in adapters if item["current_status"] in {"configured", "available", "available dependency"}),
            "blocked": sum(1 for item in adapters if item["current_status"] in {"not connected", "missing dependency"}),
            "plain_reading": "This is the external-tool wiring kit: env vars, inputs, outputs, normalized artifacts, and API calls.",
        },
        "adapters": adapters,
        "integration_rule": "A real tool is connected only when it can produce a normalized artifact that passes validation and can be archived with raw-output references.",
    }
