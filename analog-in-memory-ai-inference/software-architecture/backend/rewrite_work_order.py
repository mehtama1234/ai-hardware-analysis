REWRITE_WORK_ORDER_SCHEMA_VERSION = "rewrite-work-order-v0.1"


def _layer_lookup(analysis):
    return {layer.get("id"): layer for layer in analysis.get("layers", [])}


def _owner_for_action(action_type):
    if action_type in {"operator_replacement", "model_shape_change"}:
        return "model engineer"
    if action_type in {"boundary_reduction", "digital_support_fusion"}:
        return "compiler/runtime engineer"
    if action_type == "precision_protection":
        return "quantization engineer"
    if action_type == "fallback_removal":
        return "runtime engineer"
    return "technical lead"


def _target_after(action):
    action_type = action.get("action_type")
    if action_type == "operator_replacement":
        return "The layer is expressed as supported ONNX primitives or has an explicit measured digital path."
    if action_type == "fallback_removal":
        return "The layer no longer uses unmeasured host fallback; placement is analog, digital, or hybrid with known cost."
    if action_type == "boundary_reduction":
        return "The adjacent graph region has one fewer analog/digital conversion boundary."
    if action_type == "digital_support_fusion":
        return "The support operator is fused or scheduled so it does not split analog-heavy work unnecessarily."
    if action_type == "precision_protection":
        return "The layer keeps protected precision or mixed precision where the task metric needs it."
    if action_type == "model_shape_change":
        return "The model variant exposes more repeated matrix work to analog-capable arrays."
    return "The proposed change is specified enough for model-fit analysis to verify it."


def _task(action, layer):
    layer_id = action.get("layer_id")
    return {
        "id": f"WO-{action.get('suggestion_id', 'manual').replace('.', '-').replace('_', '-')}",
        "owner": _owner_for_action(action.get("action_type")),
        "action_type": action.get("action_type"),
        "layer_id": layer_id,
        "operator": action.get("operator"),
        "before": {
            "placement": (layer or {}).get("placement", "model-level"),
            "risk": (layer or {}).get("risk", "unknown"),
            "reason": action.get("reason"),
        },
        "after_target": _target_after(action),
        "implementation_notes": [
            action.get("planned_change"),
            action.get("model_change"),
            action.get("compiler_expectation"),
        ],
        "done_when": [
            "The rewritten model or runtime path is checked into the candidate branch.",
            "The same target profile, modality, calibration profile, and runtime mode are rerun.",
            "The linked validation gates in this work order pass or record a clear blocker.",
        ],
        "blocked_by": [
            "Missing calibration or task dataset for accuracy validation.",
            "No compiler/simulator/board adapter if the claim requires measured evidence.",
        ],
    }


def _acceptance_gates(rewrite_plan):
    gates = []
    for step in rewrite_plan.get("validation_steps", []):
        gates.append(
            {
                "id": f"AG-{step.get('id')}",
                "name": step.get("name"),
                "evidence_required": step.get("purpose"),
                "passes_when": step.get("passes_when"),
                "status": "not started",
            }
        )
    return gates


def _handoff_summary(analysis, rewrite_plan):
    summary = analysis.get("summary", {})
    plan_summary = rewrite_plan.get("summary", {})
    return {
        "model_name": analysis.get("model", {}).get("name"),
        "baseline_fit": summary.get("fit"),
        "baseline_grade": summary.get("grade"),
        "baseline_analog_coverage_percent": summary.get("analog_coverage_percent"),
        "baseline_fallback_count": summary.get("fallback_count"),
        "baseline_boundary_count": len(analysis.get("boundary_events", [])),
        "planned_action_count": plan_summary.get("selected_action_count", 0),
        "estimated_latency_delta_ms": plan_summary.get("estimated_latency_delta_ms"),
        "estimated_energy_delta_uj": plan_summary.get("estimated_energy_delta_uj"),
        "decision_before": rewrite_plan.get("decision_before"),
        "decision_after_estimate": rewrite_plan.get("decision_after_estimate"),
    }


def build_rewrite_work_order(analysis, rewrite_plan, project_context=None):
    layers = _layer_lookup(analysis)
    tasks = [_task(action, layers.get(action.get("layer_id"))) for action in rewrite_plan.get("selected_actions", [])]
    return {
        "result_type": "rewrite_work_order",
        "schema_version": REWRITE_WORK_ORDER_SCHEMA_VERSION,
        "provenance": "derived from rewrite plan; no source model or runtime was changed",
        "confidence": "low",
        "project": project_context,
        "summary": _handoff_summary(analysis, rewrite_plan),
        "tasks": tasks,
        "acceptance_gates": _acceptance_gates(rewrite_plan),
        "evidence_to_attach": [
            "rewritten ONNX or model commit",
            "model-fit analysis after rewrite",
            "quantization report after rewrite",
            "runtime profile after rewrite",
            "baseline comparison after rewrite",
            "task-dataset accuracy report",
            "compiler placement report when available",
            "simulator or board measurement when claims require measured data",
        ],
        "review_questions": [
            "Did the rewrite change the learned function or only the graph schedule?",
            "Did analog coverage improve without adding new high-risk numeric behavior?",
            "Did boundary count, fallback count, latency, or energy improve at completed-inference level?",
            "Which evidence is still estimated, and which evidence came from a configured adapter?",
        ],
        "claim_rule": "After this work order is executed, update claims only from the rerun evidence. Do not use this work order itself as proof of accuracy, latency, energy, or deployability.",
    }
