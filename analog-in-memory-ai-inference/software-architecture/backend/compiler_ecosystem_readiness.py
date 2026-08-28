COMPILER_ECOSYSTEM_SCHEMA_VERSION = "compiler-ecosystem-readiness-v0.1"


def _adapter_by_id(adapter_report):
    return {
        item.get("id"): item
        for item in (adapter_report or {}).get("adapters", [])
        if item.get("id")
    }


def _connector_by_id(external_connector_contract):
    return {
        item.get("adapter_id"): item
        for item in (external_connector_contract or {}).get("connectors", [])
        if item.get("adapter_id")
    }


def _playbook_by_id(connection_playbook):
    return {
        item.get("adapter_id"): item
        for item in (connection_playbook or {}).get("connection_targets", [])
        if item.get("adapter_id")
    }


def _source_status(measurement_evidence, source_id):
    for source in (measurement_evidence or {}).get("required_sources", []):
        if source.get("id") == source_id:
            return source.get("status", "missing")
    return "missing"


def _operator_counts(analysis):
    counts = {}
    unsupported = 0
    fallback = 0
    analog = 0
    digital = 0
    for layer in (analysis or {}).get("layers", []):
        op = layer.get("operator") or layer.get("op_type") or "unknown"
        counts[op] = counts.get(op, 0) + 1
        placement = layer.get("placement") or layer.get("mapping") or ""
        risk = layer.get("risk") or ""
        if placement == "fallback" or risk == "high":
            unsupported += 1
            fallback += 1 if placement == "fallback" else 0
        elif placement == "analog":
            analog += 1
        elif placement == "digital":
            digital += 1
    return {
        "total_layers": len((analysis or {}).get("layers", [])),
        "operator_counts": counts,
        "unsupported_or_high_risk": unsupported,
        "analog_layers": analog,
        "digital_layers": digital,
        "fallback_layers": fallback,
    }


def _path_status(name, status, evidence, reason, next_step, risk):
    return {
        "name": name,
        "status": status,
        "evidence_status": evidence,
        "plain_reading": reason,
        "next_step": next_step,
        "adoption_risk": risk,
    }


def _zero_touch_score(paths, compiler_status, profiling_status, rewrite_status):
    score = 20
    score += 15 if paths["onnx"]["status"] in {"current first path", "available"} else 0
    score += 10 if paths["pytorch"]["status"] == "implemented" else 0
    score += 10 if paths["jax_xla"]["status"] == "implemented" else 0
    score += 15 if compiler_status == "imported artifact" else 6 if compiler_status in {"configured", "runner available, evidence missing"} else 0
    score += 15 if profiling_status == "evidence attached" else 6 if profiling_status == "workflow available" else 0
    score += 10 if rewrite_status == "available" else 0
    return min(score, 100)


def build_compiler_ecosystem_readiness(
    adapter_report,
    external_connector_contract,
    connection_playbook,
    analysis,
    package_report=None,
    toolchain_readiness=None,
    measurement_evidence=None,
):
    adapters = _adapter_by_id(adapter_report)
    connectors = _connector_by_id(external_connector_contract)
    playbook = _playbook_by_id(connection_playbook)
    operator_summary = _operator_counts(analysis)
    onnx_adapter = adapters.get("model-import.onnx", {})
    compiler_adapter = adapters.get("compiler.tvm-mlir-iree", {})
    compiler_connector = connectors.get("compiler.tvm-mlir-iree", {})
    compiler_target = playbook.get("compiler.tvm-mlir-iree", {})
    compiler_evidence = _source_status(measurement_evidence, "compiler_mapping")
    board_evidence = _source_status(measurement_evidence, "board_runtime")
    power_evidence = _source_status(measurement_evidence, "power_thermal")
    accuracy_evidence = _source_status(measurement_evidence, "task_accuracy")
    analog_evidence = _source_status(measurement_evidence, "analog_error_simulation")
    toolchain_steps = {
        step.get("id"): step
        for step in (toolchain_readiness or {}).get("steps", [])
        if step.get("id")
    }
    profiling_step = toolchain_steps.get("profiling_debug", {})
    rewrite_status = "available" if (analysis or {}).get("layers") else "not built"

    paths = {
        "onnx": _path_status(
            "ONNX",
            "current first path" if onnx_adapter.get("status") in {"available", "configured"} else "dependency missing",
            "local importer available" if onnx_adapter.get("status") in {"available", "configured"} else onnx_adapter.get("status", "missing"),
            "ONNX is the first practical interchange path in this prototype because the backend imports ONNX and extracts operators, shapes, and parameters.",
            "Keep ONNX as the first supported model format and publish clear operator limits.",
            "low" if onnx_adapter.get("status") in {"available", "configured"} else "high",
        ),
        "pytorch": _path_status(
            "PyTorch",
            "roadmap connector",
            "not implemented",
            "PyTorch support should mean exporting or lowering real PyTorch models into the supported compiler path, not merely saying developers can convert manually.",
            "Add a tested torch export path, record supported ops, and attach conversion failures as evidence.",
            "medium",
        ),
        "jax_xla": _path_status(
            "JAX/XLA",
            "roadmap connector",
            "not implemented",
            "JAX/XLA matters for VLA and robotics teams, but this app has no real XLA lowering or JAX graph capture path yet.",
            "Define an XLA, StableHLO, MLIR, or ONNX bridge and prove it on target transformer-style graphs.",
            "high",
        ),
        "onnxruntime_quantization": _path_status(
            "ONNX Runtime quantization",
            "available" if adapters.get("quantization.onnxruntime", {}).get("status") in {"available", "configured"} else "not connected",
            adapters.get("quantization.onnxruntime", {}).get("status", "missing"),
            "Quantization can be local, but adoption still depends on dataset-backed accuracy and clear protected-layer rules.",
            "Run quantization against calibration data and import task-accuracy evidence.",
            "medium" if accuracy_evidence != "imported artifact" else "low",
        ),
    }
    compiler_mapping_status = compiler_evidence if compiler_evidence == "imported artifact" else compiler_adapter.get("status", "not connected")
    zero_touch_score = _zero_touch_score(
        paths,
        compiler_mapping_status,
        profiling_step.get("status", "blocked"),
        rewrite_status,
    )
    explainable_mapping_score = 70 if compiler_evidence == "imported artifact" else 45 if compiler_adapter.get("status") in {"configured", "available dependency"} else 25
    readiness = (
        "prototype_onnx_path"
        if paths["onnx"]["status"] == "current first path" and compiler_evidence != "imported artifact"
        else "evidence_backed_mapping"
        if compiler_evidence == "imported artifact"
        else "blocked_by_model_path"
    )
    return {
        "result_type": "compiler_ecosystem_readiness",
        "schema_version": COMPILER_ECOSYSTEM_SCHEMA_VERSION,
        "provenance": "derived from adapter registry, connector contract, connection playbook, operator analysis, toolchain readiness, and measurement evidence",
        "confidence": "low",
        "package_id": (package_report or {}).get("package_id"),
        "readiness": readiness,
        "summary": {
            "plain_reading": (
                "The chip needs a boring, repeatable software path. ONNX is the current first path here. PyTorch and JAX/XLA are still connector work "
                "until real export, lowering, mapping, profiling, and error reporting are implemented."
            ),
            "onnx_status": paths["onnx"]["status"],
            "pytorch_status": paths["pytorch"]["status"],
            "jax_xla_status": paths["jax_xla"]["status"],
            "compiler_mapping_status": compiler_mapping_status,
            "simulator_status": adapters.get("analog.error-simulator", {}).get("status", "not connected"),
            "profiling_status": profiling_step.get("status", "not built"),
            "rewrite_support": rewrite_status,
            "evidence_import_support": "implemented",
            "zero_touch_score": zero_touch_score,
            "explainable_mapping_score": explainable_mapping_score,
            "unsupported_or_high_risk_layers": operator_summary["unsupported_or_high_risk"],
        },
        "model_paths": list(paths.values()),
        "compiler_mapping": {
            "status": compiler_mapping_status,
            "connector_status": compiler_connector.get("readiness_status", "not connected"),
            "connection_status": compiler_target.get("status", "not connected"),
            "what_it_must_return": [
                "operator support table",
                "analog versus digital placement",
                "tiling and array mapping",
                "memory movement",
                "unsupported operators",
                "conversion points",
                "runtime contract",
            ],
            "why_it_matters": "A developer needs to know why a graph mapped or failed. A black-box compiler is hard to trust when accuracy, latency, and fallback behavior matter.",
        },
        "operator_visibility": {
            **operator_summary,
            "reporting_rule": "Unsupported operators should be reported before runtime. Fallback is acceptable only when latency, energy, and accuracy costs are shown.",
        },
        "profiling_and_debug": {
            "status": profiling_step.get("status", "not built"),
            "board_runtime_evidence": board_evidence,
            "power_thermal_evidence": power_evidence,
            "task_accuracy_evidence": accuracy_evidence,
            "analog_error_evidence": analog_evidence,
            "needed_view": "Show model layer, placement, latency, energy, fallback, analog error, and task metric in one trace.",
        },
        "adoption_risks": [
            "Manual PyTorch or JAX conversion creates friction for robotics and VLA teams.",
            "A compiler that maps layers without explaining unsupported operators will be hard to debug.",
            "A fast analog core is not enough if the runtime cannot profile completed inference.",
            "Zero-touch deployment is the goal, but explainable mapping is required before customers can trust failures and limits.",
        ],
        "evidence_needed": [
            "tested PyTorch export or lowering path",
            "tested JAX/XLA, StableHLO, MLIR, or ONNX bridge for transformer-style graphs",
            "compiler-produced mapping artifact with unsupported operators",
            "runtime profiler tying layers to latency, energy, fallback, and memory movement",
            "dataset-backed accuracy after quantization and analog effects",
            "clear customer-facing supported-operator table",
        ],
        "what_not_to_claim": [
            "Do not claim PyTorch support unless a real PyTorch model can move through export, mapping, runtime, and evidence import.",
            "Do not claim JAX/XLA support unless the lowering path is implemented and tested.",
            "Do not call the path zero-touch when developers still need manual graph surgery.",
            "Do not hide unsupported operators, fallback layers, conversion costs, or profiling gaps.",
            "Do not treat compiler mapping as proof of latency, energy, or accuracy.",
        ],
    }
