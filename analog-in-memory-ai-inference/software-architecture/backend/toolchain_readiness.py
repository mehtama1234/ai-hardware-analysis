TOOLCHAIN_READINESS_SCHEMA_VERSION = "toolchain-readiness-v0.1"


TOOLCHAIN_STEPS = [
    {
        "id": "model_import",
        "name": "Model import",
        "adapter_categories": ["model import"],
        "source_ids": [],
        "customer_need": "Load a model, inspect graph structure, and show unsupported operators before deeper work starts.",
        "hard_part": "A model can import successfully and still be a poor hardware fit if shapes, operators, or memory movement do not match the architecture.",
    },
    {
        "id": "quantization",
        "name": "Quantization and sensitivity",
        "adapter_categories": ["quantization"],
        "source_ids": ["task_accuracy"],
        "customer_need": "Choose a number format the hardware can run while preserving the task metric that matters for the workload.",
        "hard_part": "The right precision depends on layer sensitivity, dataset coverage, and the cost of a wrong output.",
    },
    {
        "id": "compiler_mapping",
        "name": "Compiler mapping",
        "adapter_categories": ["compiler"],
        "source_ids": ["compiler_mapping"],
        "customer_need": "Map operators, tiles, weights, memory movement, and analog/digital boundaries into a plan the runtime can execute.",
        "hard_part": "The useful boundary is rarely all-analog. The compiler must decide what runs on analog arrays and what stays digital.",
    },
    {
        "id": "analog_simulation",
        "name": "Analog behavior simulation",
        "adapter_categories": ["analog simulation"],
        "source_ids": ["analog_error_simulation"],
        "customer_need": "Predict how variation, temperature, voltage, ADC/DAC behavior, and calibration affect accuracy.",
        "hard_part": "Analog numeric error is workload-dependent. A small signal shift can be harmless for one model and damaging for another.",
    },
    {
        "id": "runtime_execution",
        "name": "Runtime and board execution",
        "adapter_categories": ["runtime", "hardware"],
        "source_ids": ["board_runtime"],
        "customer_need": "Run the mapped model, capture traces, and show latency, fallback behavior, and stability.",
        "hard_part": "A fast core is not enough if host control, memory traffic, conversion, or fallback paths dominate completed inference.",
    },
    {
        "id": "power_thermal",
        "name": "Power and thermal measurement",
        "adapter_categories": ["measurement"],
        "source_ids": ["power_thermal"],
        "customer_need": "Measure energy, power, and temperature under the same setup used for latency and accuracy claims.",
        "hard_part": "Peak efficiency is not the same as energy per completed inference, and measurement must say what was counted.",
    },
    {
        "id": "accuracy_validation",
        "name": "Task accuracy validation",
        "adapter_categories": ["accuracy"],
        "source_ids": ["task_accuracy", "analog_error_simulation"],
        "customer_need": "Run a dataset or task check that proves the model still meets the selected workload metric.",
        "hard_part": "Average accuracy can hide rare failures, class-specific drops, false triggers, jitter, or missed events.",
    },
    {
        "id": "profiling_debug",
        "name": "Profiling and debugging",
        "adapter_categories": ["runtime", "compiler", "measurement"],
        "source_ids": ["compiler_mapping", "board_runtime", "power_thermal"],
        "customer_need": "Explain why a run missed latency, energy, accuracy, or memory targets and what to change next.",
        "hard_part": "Debugging needs synchronized model, compiler, runtime, power, and accuracy views rather than isolated logs.",
    },
    {
        "id": "customer_handoff",
        "name": "Customer handoff",
        "adapter_categories": [],
        "source_ids": ["compiler_mapping", "analog_error_simulation", "board_runtime", "power_thermal", "task_accuracy"],
        "customer_need": "Package the model, limits, evidence, safe claims, and next steps so a customer can repeat the result.",
        "hard_part": "Adoption depends on a predictable software path, not only a strong circuit or TOPS/W number.",
    },
]


def _adapters_by_category(adapter_report):
    grouped = {}
    for adapter in adapter_report.get("adapters", []):
        grouped.setdefault(adapter.get("category"), []).append(adapter)
    return grouped


def _sources_by_id(measurement_evidence):
    return {source.get("id"): source for source in measurement_evidence.get("required_sources", [])}


def _adapter_state(categories, required_categories):
    adapters = [adapter for category in required_categories for adapter in categories.get(category, [])]
    if not required_categories:
        return "derived"
    if any(adapter.get("status") == "configured" for adapter in adapters):
        return "configured"
    if any(adapter.get("status") in {"available", "available dependency"} for adapter in adapters):
        return "local or available"
    if adapters:
        return "not connected"
    return "missing"


def _evidence_state(sources, source_ids):
    if not source_ids:
        return "not required yet"
    selected = [sources.get(source_id, {}) for source_id in source_ids]
    imported = [source for source in selected if source.get("status") == "imported artifact"]
    if len(imported) == len(source_ids):
        return "evidence attached"
    if imported:
        return "partial evidence"
    if any(source.get("status") in {"configured", "local estimate"} for source in selected):
        return "runner available, evidence missing"
    return "evidence missing"


def _step_status(adapter_state, evidence_state):
    if evidence_state == "evidence attached":
        return "evidence attached"
    if adapter_state in {"configured", "local or available", "derived"}:
        return "workflow available"
    if evidence_state == "partial evidence":
        return "partial"
    return "blocked"


def _next_step(status, step):
    if status == "evidence attached":
        return "Keep provenance and counted-cost details with the package."
    if status == "workflow available":
        return "Run or connect the tool and attach its normalized evidence artifact."
    if status == "partial":
        return "Attach the remaining normalized artifacts for this step."
    return f"Connect a tool for {step['name']} and define its normalized output contract."


def build_toolchain_readiness(adapter_report, measurement_evidence, package_report=None):
    categories = _adapters_by_category(adapter_report or {})
    sources = _sources_by_id(measurement_evidence or {})
    steps = []
    for step in TOOLCHAIN_STEPS:
        adapter_state = _adapter_state(categories, step["adapter_categories"])
        evidence_state = _evidence_state(sources, step["source_ids"])
        status = _step_status(adapter_state, evidence_state)
        steps.append({
            "id": step["id"],
            "name": step["name"],
            "status": status,
            "adapter_state": adapter_state,
            "evidence_state": evidence_state,
            "customer_need": step["customer_need"],
            "hard_part": step["hard_part"],
            "required_sources": step["source_ids"],
            "next_step": _next_step(status, step),
        })
    status_counts = {
        "evidence_attached": sum(1 for step in steps if step["status"] == "evidence attached"),
        "workflow_available": sum(1 for step in steps if step["status"] == "workflow available"),
        "partial": sum(1 for step in steps if step["status"] == "partial"),
        "blocked": sum(1 for step in steps if step["status"] == "blocked"),
    }
    return {
        "result_type": "toolchain_readiness",
        "schema_version": TOOLCHAIN_READINESS_SCHEMA_VERSION,
        "provenance": "derived from adapter registry and measurement evidence contract",
        "confidence": "low" if status_counts["blocked"] else "medium",
        "package_id": (package_report or {}).get("package_id") or (measurement_evidence or {}).get("summary", {}).get("package_id"),
        "summary": {
            **status_counts,
            "total_steps": len(steps),
            "plain_reading": "Customers need a repeatable path from model import to evidence-backed handoff. The analog core is only one part of that path.",
        },
        "steps": steps,
        "customer_handoff": [
            "supported model format and operator limits",
            "quantization policy and calibration dataset expectations",
            "compiler mapping and analog/digital boundary report",
            "runtime trace with latency, fallback, and memory behavior",
            "power and thermal measurement setup",
            "task accuracy result for the selected workload metric",
            "claim readiness, evidence audit, and evidence brief",
        ],
        "do_not_claim": [
            "Do not say customers can adopt the chip easily unless model conversion, compiler mapping, runtime execution, debugging, and evidence export are usable.",
            "Do not treat a connected tool as proof; only normalized evidence artifacts should move claims forward.",
            "Do not separate software support from hardware value. A hardware advantage is hard to adopt without a clear software path.",
        ],
    }
