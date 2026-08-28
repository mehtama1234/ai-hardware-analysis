CONNECTION_PLAYBOOK_SCHEMA_VERSION = "connection-playbook-v0.1"


CONNECTION_REQUIREMENTS = {
    "quantization.onnxruntime": {
        "connection_type": "software library",
        "configuration": ["onnxruntime Python package", "calibration or reference dataset path"],
        "proves": "A model can be quantized by a real tool, but accuracy still needs task evidence.",
        "do_not_claim": "Do not say quantization preserves accuracy until a task-accuracy artifact passes.",
    },
    "compiler.tvm-mlir-iree": {
        "connection_type": "compiler toolchain",
        "configuration": ["ANALOG_AI_COMPILER_API_URL or TVM, MLIR, IREE, or custom compiler entrypoint", "target hardware description"],
        "proves": "Compiler-produced placement, tiling, memory, and unsupported-operator evidence.",
        "do_not_claim": "Do not use compiler mapping as latency, energy, or accuracy proof.",
    },
    "compiler.analog-mlir-golem": {
        "connection_type": "simulation-to-silicon compiler bridge",
        "configuration": ["ANALOG_AI_ANALOG_MLIR_API_URL", "target array description", "supported tensor/linalg lowering rules", "runtime graph output path"],
        "proves": "Analog/digital outlining, static-weight isolation, task graph construction, and Golem/SST runtime graph generation.",
        "do_not_claim": "Do not say a lowered runtime graph proves silicon behavior until simulator and measurement evidence are attached.",
    },
    "analog.error-simulator": {
        "connection_type": "analog behavior simulator",
        "configuration": ["variation model", "ADC/DAC model", "temperature and voltage range", "calibration profile"],
        "proves": "The expected numeric behavior of the analog path under stated conditions.",
        "do_not_claim": "Do not say the model is accurate from analog simulation alone.",
    },
    "sim.aihwkit": {
        "connection_type": "differentiable hardware-aware simulator",
        "configuration": ["AIHWKIT package or ANALOG_AI_AIHWKIT_API_URL", "device model", "ADC/DAC precision", "IR-drop settings", "drift/programming-noise settings"],
        "proves": "Hardware-aware sensitivity of mapped layers to analog noise, drift, converter limits, IR drop, and write/update non-idealities.",
        "do_not_claim": "Do not treat AIHWKIT simulation as board measurement or as proof that the compiler can place the graph.",
    },
    "sim.crosssim": {
        "connection_type": "crossbar accuracy simulator",
        "configuration": ["CrossSim package or ANALOG_AI_CROSSSIM_API_URL", "array dimensions", "bit slicing", "parasitic resistance model", "ADC range policy"],
        "proves": "Crossbar-level accuracy impact from programming errors, read noise, wire parasitics, bit slicing, and ADC choices.",
        "do_not_claim": "Do not use CrossSim accuracy output as full-system latency, power, or board-runtime evidence.",
    },
    "system.sst-golem": {
        "connection_type": "cycle-level hardware/software co-simulation",
        "configuration": ["ANALOG_AI_SST_GOLEM_API_URL", "compiled runtime graph", "CPU/core model", "custom dispatch interface", "CrossSim or ideal-array backend"],
        "proves": "Cycle/runtime behavior for CPU dispatch, synchronization, memory bottlenecks, and simulated analog array execution.",
        "do_not_claim": "Do not call SST/Golem output measured board evidence; label it as cycle-level co-simulation.",
    },
    "system.alpine-gem5x": {
        "connection_type": "full-system AIMC simulation",
        "configuration": ["ANALOG_AI_ALPINE_GEM5X_API_URL", "model dispatch library", "custom ISA/runtime settings", "memory hierarchy", "OS/runtime configuration"],
        "proves": "Full-stack overheads from CPU integration, custom ISA/library dispatch, memory hierarchy, and runtime execution.",
        "do_not_claim": "Do not use full-system simulation as silicon power or production readiness evidence without measured corroboration.",
    },
    "compiler.attention-partitioner": {
        "connection_type": "transformer/VLA partitioning pass",
        "configuration": ["ANALOG_AI_ATTENTION_PARTITION_API_URL", "transformer graph", "static projection mapping rules", "digital attention/Softmax target", "rewrite policy"],
        "proves": "Which transformer regions are weight-stationary analog candidates, digital attention/Softmax work, analog-pruning candidates, or blocked.",
        "do_not_claim": "Do not imply full transformer or VLA support from projection-layer mapping alone.",
    },
    "accuracy.local-task-check": {
        "connection_type": "dataset metric runner",
        "configuration": ["ANALOG_AI_ACCURACY_API_URL or dataset_path with expected labels", "baseline predictions", "candidate predictions", "metric definition", "acceptance tolerance"],
        "proves": "The model still meets the selected workload metric after quantization and analog effects.",
        "do_not_claim": "Do not use generic accuracy when the workload needs false rejects, mAP, jitter, sensitivity, or token latency.",
    },
    "board.runtime": {
        "connection_type": "board or simulator service",
        "configuration": ["ANALOG_AI_BOARD_API_URL", "board ID", "runtime version", "model package reference"],
        "proves": "Latency, fallback behavior, and runtime stability for a specific setup.",
        "do_not_claim": "Do not call local simulated runtime measured board latency.",
    },
    "metrics.power-thermal": {
        "connection_type": "power and thermal measurement service",
        "configuration": ["ANALOG_AI_POWER_METER_URL", "sampling setup", "synchronized runtime trace", "temperature sensor path"],
        "proves": "Energy, power, and thermal behavior under a counted measurement setup.",
        "do_not_claim": "Do not quote TOPS/W as the full answer when energy per completed inference is what matters.",
    },
}


def _source_by_category(measurement_evidence):
    sources = {}
    for source in (measurement_evidence or {}).get("required_sources", []):
        sources.setdefault(source.get("adapter_category"), source)
    return sources


def _connection_status(adapter, source):
    if source and source.get("status") == "imported artifact":
        return "evidence attached"
    if adapter.get("status") == "configured":
        return "configured, needs evidence"
    if adapter.get("status") in {"available", "available dependency"}:
        return "local path available"
    if adapter.get("status") == "missing dependency":
        return "dependency missing"
    return "not connected"


def _next_action(status, adapter, source, requirement):
    if status == "evidence attached":
        return "Keep raw output references, versions, target settings, and counted-cost notes with the package."
    if status == "configured, needs evidence":
        return f"Run the configured adapter and import {source.get('artifact_name') if source else 'the normalized artifact'}."
    if status == "local path available":
        return f"Use the local runner for workflow testing, then replace it with {requirement['connection_type']} evidence."
    if status == "dependency missing":
        return f"Install or configure the dependency for {adapter.get('name')}."
    return adapter.get("next_step") or f"Connect a {requirement['connection_type']}."


def build_connection_playbook(adapter_report, measurement_evidence, toolchain_readiness=None, package_report=None):
    sources = _source_by_category(measurement_evidence or {})
    targets = []
    for adapter in (adapter_report or {}).get("adapters", []):
        requirement = CONNECTION_REQUIREMENTS.get(adapter.get("id"))
        if not requirement:
            continue
        source = sources.get(adapter.get("category"), {})
        status = _connection_status(adapter, source)
        targets.append({
            "adapter_id": adapter.get("id"),
            "name": adapter.get("name"),
            "category": adapter.get("category"),
            "connection_type": requirement["connection_type"],
            "status": status,
            "current_adapter_status": adapter.get("status"),
            "provenance": adapter.get("provenance"),
            "confidence": adapter.get("confidence"),
            "configuration_needed": requirement["configuration"],
            "normalized_artifact": source.get("artifact_name", "not required"),
            "minimum_fields": source.get("minimum_fields", []),
            "claim_boundary": requirement["proves"],
            "do_not_claim": requirement["do_not_claim"],
            "next_action": _next_action(status, adapter, source, requirement),
        })
    status_counts = {
        "evidence_attached": sum(1 for item in targets if item["status"] == "evidence attached"),
        "configured_needs_evidence": sum(1 for item in targets if item["status"] == "configured, needs evidence"),
        "local_path_available": sum(1 for item in targets if item["status"] == "local path available"),
        "dependency_missing": sum(1 for item in targets if item["status"] == "dependency missing"),
        "not_connected": sum(1 for item in targets if item["status"] == "not connected"),
    }
    return {
        "result_type": "connection_playbook",
        "schema_version": CONNECTION_PLAYBOOK_SCHEMA_VERSION,
        "provenance": "derived from adapter registry, measurement evidence contract, and toolchain readiness",
        "confidence": "low" if status_counts["not_connected"] or status_counts["dependency_missing"] else "medium",
        "package_id": (package_report or {}).get("package_id") or (measurement_evidence or {}).get("summary", {}).get("package_id"),
        "summary": {
            **status_counts,
            "total_targets": len(targets),
            "toolchain_blocked_steps": (toolchain_readiness or {}).get("summary", {}).get("blocked", 0),
            "plain_reading": "This is the wiring checklist for replacing local estimates with real compiler, simulator, board, power, and accuracy evidence.",
        },
        "connection_targets": targets,
        "integration_rule": "A connection is useful only after it produces a normalized artifact that can be imported, audited, archived, and tied to a safe claim.",
        "first_real_connections": [
            "dataset-backed task accuracy runner",
            "compiler-produced placement artifact",
            "board or simulator runtime trace",
            "synchronized power and thermal measurement",
        ],
    }
