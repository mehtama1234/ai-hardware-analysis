MEASUREMENT_EVIDENCE_SCHEMA_VERSION = "measurement-evidence-v0.1"


REQUIRED_SOURCES = [
    {
        "id": "compiler_mapping",
        "adapter_category": "compiler",
        "required_for": "supported placement, tiling, memory movement, and unsupported operator claims",
        "artifact_name": "compiler-placement.json",
        "minimum_fields": ["operator_placements", "tiling_plan", "memory_plan", "unsupported_operators", "provenance"],
    },
    {
        "id": "analog_error_simulation",
        "adapter_category": "analog simulation",
        "required_for": "analog numeric tolerance and calibration claims",
        "artifact_name": "analog-error-simulation.json",
        "minimum_fields": ["error_model", "temperature_range", "voltage_range", "accuracy_impact", "calibration_profile"],
    },
    {
        "id": "board_runtime",
        "adapter_category": "hardware",
        "required_for": "measured latency, fallback behavior, and board runtime stability claims",
        "artifact_name": "board-runtime-trace.json",
        "minimum_fields": ["board_id", "runtime_version", "latency_ms", "trace", "fallback_events", "provenance"],
    },
    {
        "id": "power_thermal",
        "adapter_category": "measurement",
        "required_for": "measured energy, power, and thermal claims",
        "artifact_name": "power-thermal-report.json",
        "minimum_fields": ["energy_uj", "power_trace", "temperature_trace", "sampling_rate", "measurement_setup"],
    },
    {
        "id": "task_accuracy",
        "adapter_category": "accuracy",
        "required_for": "task quality and quantization tolerance claims",
        "artifact_name": "task-accuracy-report.json",
        "minimum_fields": ["dataset_id", "metric_name", "baseline_metric", "candidate_metric", "tolerance", "pass"],
    },
    {
        "id": "physical_flow",
        "adapter_category": "physical design",
        "required_for": "bounded digital controller physical-flow claims",
        "artifact_name": "physical-flow-report.json",
        "minimum_fields": ["design_name", "flow_name", "flow_status", "artifacts", "checks", "timing", "claim_boundary", "provenance"],
    },
]


def _adapters_by_category(adapter_report):
    categories = {}
    for adapter in adapter_report.get("adapters", []):
        categories.setdefault(adapter.get("category"), []).append(adapter)
    return categories


def _imported_by_source(imported_evidence):
    grouped = {}
    for item in imported_evidence or []:
        grouped.setdefault(item.get("source_id"), []).append(item)
    return grouped


def _source_status(required, categories, imported):
    imported_items = imported.get(required["id"], [])
    adapters = categories.get(required["adapter_category"], [])
    configured = [item for item in adapters if item.get("status") == "configured"]
    available = [item for item in adapters if item.get("status") in {"available", "available dependency"}]
    if imported_items:
        status = "imported artifact"
        source = configured[0] if configured else available[0] if available else adapters[0] if adapters else {}
    elif configured:
        status = "configured"
        source = configured[0]
    elif available:
        status = "local estimate"
        source = available[0]
    else:
        status = "not connected"
        source = adapters[0] if adapters else {}
    return {
        **required,
        "status": status,
        "adapter_id": source.get("id", "not registered"),
        "adapter_name": source.get("name", "not registered"),
        "adapter_provenance": source.get("provenance", "missing"),
        "confidence": "medium" if status in {"configured", "imported artifact"} else "low",
        "imported_count": len(imported_items),
        "latest_import": imported_items[-1] if imported_items else None,
        "current_evidence": source.get("evidence", []),
        "next_step": source.get("next_step", "Register and connect an adapter for this evidence source."),
    }


def _claim_status(sources):
    source_by_id = {source["id"]: source for source in sources}

    def imported(source_id):
        return source_by_id.get(source_id, {}).get("status") == "imported artifact"

    claims = [
        {
            "claim": "Compiler placement is real",
            "status": "supported" if imported("compiler_mapping") else "blocked",
            "required_sources": ["compiler_mapping"],
            "plain_rule": "Do not say placement is compiler-produced until a compiler mapping artifact is attached.",
        },
        {
            "claim": "Latency is measured on hardware",
            "status": "supported" if imported("board_runtime") else "blocked",
            "required_sources": ["board_runtime"],
            "plain_rule": "Do not say latency is measured unless it came from a simulator or board trace with provenance.",
        },
        {
            "claim": "Energy is measured on hardware",
            "status": "supported" if imported("board_runtime") and imported("power_thermal") else "blocked",
            "required_sources": ["board_runtime", "power_thermal"],
            "plain_rule": "Do not say energy is measured unless board runtime and power or thermal measurement artifacts are both attached.",
        },
        {
            "claim": "Accuracy survives analog and quantization behavior",
            "status": "supported" if imported("analog_error_simulation") and imported("task_accuracy") else "blocked",
            "required_sources": ["analog_error_simulation", "task_accuracy"],
            "plain_rule": "Do not say accuracy is preserved until task accuracy and analog error evidence are attached.",
        },
        {
            "claim": "Digital controller physical flow is evidence-backed",
            "status": "supported" if imported("physical_flow") else "blocked",
            "required_sources": ["physical_flow"],
            "plain_rule": "Do not say physical flow is backed until a routed OpenLane or equivalent physical-flow artifact is attached.",
        },
        {
            "claim": "Ready for production comparison",
            "status": "blocked",
            "required_sources": [source["id"] for source in sources],
            "plain_rule": "Even complete lab evidence is not production readiness; yield, drift, calibration cost, packaging, and customer integration still remain.",
        },
    ]
    return claims


def build_measurement_evidence(adapter_report, runtime_profile=None, baseline_report=None, package_report=None, imported_evidence=None):
    categories = _adapters_by_category(adapter_report or {})
    imported = _imported_by_source(imported_evidence or [])
    sources = [_source_status(required, categories, imported) for required in REQUIRED_SOURCES]
    imported_count = sum(1 for source in sources if source["status"] == "imported artifact")
    configured_count = sum(1 for source in sources if source["status"] == "configured")
    local_count = sum(1 for source in sources if source["status"] == "local estimate")
    missing_count = sum(1 for source in sources if source["status"] == "not connected")
    claims = _claim_status(sources)
    return {
        "result_type": "measurement_evidence",
        "schema_version": MEASUREMENT_EVIDENCE_SCHEMA_VERSION,
        "provenance": "normalized adapter contract; no external measurement was run",
        "confidence": "low" if imported_count < len(sources) else "medium",
        "summary": {
            "imported_sources": imported_count,
            "configured_sources": configured_count,
            "local_estimate_sources": local_count,
            "missing_sources": missing_count,
            "runtime_provenance": (runtime_profile or {}).get("provenance", "not attached"),
            "baseline_provenance": (baseline_report or {}).get("provenance", "not attached"),
            "package_id": (package_report or {}).get("package_id"),
            "claim_status": "measurement blocked" if imported_count < len(sources) else "measurement evidence attached",
        },
        "required_sources": sources,
        "claim_status": claims,
        "normalization_contract": {
            "rule": "Every external tool must return a normalized artifact with provenance, source version, target settings, metrics, and confidence before the frontend treats it as evidence.",
            "raw_outputs": "Raw compiler logs, simulator files, board traces, and power-meter dumps should be stored for audit, but the UI should render only normalized artifacts.",
            "comparison_unit": "Compare energy per completed inference at a fixed accuracy, latency, target profile, calibration profile, and runtime mode.",
        },
        "do_not_claim": [
            "Do not treat a configured URL or installed dependency as a measurement result.",
            "Do not mix estimated runtime with measured power and call the final number measured hardware energy.",
            "Do not compare against a digital baseline unless accuracy, latency target, and counted system costs match.",
        ],
    }
