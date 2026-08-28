REWRITE_PLAN_SCHEMA_VERSION = "rewrite-plan-v0.1"


def _suggestion_map(rewrite_report):
    return {item.get("id"): item for item in rewrite_report.get("suggestions", [])}


def _operator_action(suggestion):
    suggestion_id = suggestion.get("id", "")
    layer_id = suggestion.get("layer_id")
    operator = suggestion.get("operator")
    base = {
        "suggestion_id": suggestion_id,
        "layer_id": layer_id,
        "operator": operator,
        "reason": suggestion.get("problem"),
        "rewrite_pattern": suggestion.get("rewrite_pattern"),
        "expected_impact": suggestion.get("expected_impact", {}),
        "verification": suggestion.get("verification"),
    }
    if suggestion_id.startswith("rewrite.unsupported"):
        base.update(
            {
                "action_type": "operator_replacement",
                "planned_change": "Replace this operator with supported ONNX primitives or keep it on an explicit measured digital path.",
                "model_change": "ONNX graph edit required unless the hardware runtime adds direct support.",
                "compiler_expectation": "Compiler must stop marking this node unsupported.",
            }
        )
    elif suggestion_id.startswith("rewrite.fallback"):
        base.update(
            {
                "action_type": "fallback_removal",
                "planned_change": "Rewrite or implement the fallback operator so it has a known analog or digital placement.",
                "model_change": "ONNX graph edit or runtime kernel implementation required.",
                "compiler_expectation": "Compiler must produce a placement with measured cost instead of host fallback.",
            }
        )
    elif suggestion_id.startswith("rewrite.boundary"):
        base.update(
            {
                "action_type": "boundary_reduction",
                "planned_change": "Fuse, fold, or reschedule nearby work so one analog/digital crossing is removed.",
                "model_change": "May be a graph optimization rather than a new model architecture.",
                "compiler_expectation": "Compiler or runtime should show fewer ADC/DAC boundary events.",
            }
        )
    elif suggestion_id.startswith("rewrite.digital-support"):
        base.update(
            {
                "action_type": "digital_support_fusion",
                "planned_change": "Fuse exact support math or schedule it next to other digital work.",
                "model_change": "Graph optimization if mathematically exact; otherwise treat as an approximation and validate accuracy.",
                "compiler_expectation": "Compiler should reduce fragmented analog and digital blocks.",
            }
        )
    elif suggestion_id.startswith("rewrite.protect-analog"):
        base.update(
            {
                "action_type": "precision_protection",
                "planned_change": "Keep this layer or selected channels at protected precision.",
                "model_change": "Quantization policy change; original topology can remain unchanged.",
                "compiler_expectation": "Compiler must preserve mixed-precision placement and account for extra movement or storage.",
            }
        )
    elif suggestion_id.startswith("rewrite.coverage"):
        base.update(
            {
                "action_type": "model_shape_change",
                "planned_change": "Try a model variant with more work expressed as matrix-heavy supported operators.",
                "model_change": "Architecture-level model change likely required.",
                "compiler_expectation": "Compiler should map a larger share of completed inference to analog-capable arrays.",
            }
        )
    else:
        base.update(
            {
                "action_type": "manual_review",
                "planned_change": "Review this suggestion manually before changing the model.",
                "model_change": "Unknown.",
                "compiler_expectation": "Unknown until the rewrite is specified.",
            }
        )
    return base


def _validation_steps(analysis, quantization_report, runtime_profile, selected_actions):
    steps = [
        {
            "id": "V1",
            "name": "Re-import rewritten ONNX",
            "purpose": "Confirm the graph still parses and the changed operators are visible.",
            "passes_when": "Model import succeeds and the changed layer IDs or replacement nodes are present.",
        },
        {
            "id": "V2",
            "name": "Rerun model-fit analysis",
            "purpose": "Check placement, fallback count, unsupported count, analog coverage, and boundary events.",
            "passes_when": "Unsupported count is zero for deployable claims, fallback count decreases, and boundary count does not increase unexpectedly.",
        },
        {
            "id": "V3",
            "name": "Rerun quantization on the target task",
            "purpose": "Make sure protected layers and approximations still meet the task metric.",
            "passes_when": "Task metric stays inside the project tolerance, not just generic accuracy.",
        },
        {
            "id": "V4",
            "name": "Rerun runtime and baseline comparison",
            "purpose": "Compare completed-inference latency and energy after conversion, memory, host, and digital support costs are counted.",
            "passes_when": "Energy and latency improve against the saved baseline without losing required accuracy.",
        },
        {
            "id": "V5",
            "name": "Move from estimate to measured evidence",
            "purpose": "Replace local estimates with simulator, compiler, board, and power artifacts when adapters are connected.",
            "passes_when": "Evidence gates show configured or measured provenance for the claims being made.",
        },
    ]
    if any(action["action_type"] == "precision_protection" for action in selected_actions):
        steps.insert(
            3,
            {
                "id": "VQ",
                "name": "Check mixed-precision cost",
                "purpose": "Protected precision can save accuracy but may add storage, conversion, or scheduling cost.",
                "passes_when": "The protected path improves accuracy risk enough to justify its measured energy and latency cost.",
            },
        )
    if any(action["action_type"] in {"operator_replacement", "model_shape_change"} for action in selected_actions):
        steps.insert(
            3,
            {
                "id": "VA",
                "name": "Run task-dataset accuracy",
                "purpose": "Operator replacement and model-shape changes can alter the learned function.",
                "passes_when": "The target task metric remains within tolerance for the selected modality.",
            },
        )
    return steps


def _evidence_delta(what_if_report):
    deltas = what_if_report.get("deltas", {})
    return [
        {
            "metric": "analog_coverage_percent",
            "planned_delta": deltas.get("analog_coverage_points"),
            "proof_needed": "New model-fit analysis and compiler placement report.",
        },
        {
            "metric": "fallback_count",
            "planned_delta": deltas.get("fallback_count"),
            "proof_needed": "Compiler/runtime artifact showing the fallback path was removed or measured.",
        },
        {
            "metric": "boundary_count",
            "planned_delta": deltas.get("boundary_count"),
            "proof_needed": "Boundary map with fewer ADC/DAC crossings.",
        },
        {
            "metric": "latency_ms",
            "planned_delta": deltas.get("latency_ms"),
            "proof_needed": "Simulator or board trace at the same runtime mode.",
        },
        {
            "metric": "energy_uj",
            "planned_delta": deltas.get("energy_uj"),
            "proof_needed": "Power model, simulator, or board measurement that includes conversion, memory, host, and idle cost.",
        },
    ]


def build_rewrite_plan(analysis, quantization_report, runtime_profile, decision_report, rewrite_report, what_if_report):
    selected_ids = what_if_report.get("selected_suggestion_ids", [])
    suggestions = _suggestion_map(rewrite_report)
    selected_actions = [_operator_action(suggestions[item]) for item in selected_ids if item in suggestions]
    if not selected_actions:
        selected_actions = [_operator_action(item) for item in rewrite_report.get("suggestions", [])[:3]]

    return {
        "result_type": "rewrite_plan",
        "schema_version": REWRITE_PLAN_SCHEMA_VERSION,
        "provenance": "planned from rewrite suggestions and what-if estimates; source model was not changed",
        "confidence": "low",
        "decision_before": decision_report.get("decision"),
        "decision_after_estimate": what_if_report.get("simulated", {}).get("decision"),
        "summary": {
            "model_name": analysis.get("model", {}).get("name"),
            "selected_action_count": len(selected_actions),
            "baseline_latency_ms": runtime_profile.get("summary", {}).get("latency_ms"),
            "baseline_energy_uj": runtime_profile.get("summary", {}).get("energy_uj"),
            "estimated_latency_delta_ms": what_if_report.get("deltas", {}).get("latency_ms"),
            "estimated_energy_delta_uj": what_if_report.get("deltas", {}).get("energy_uj"),
            "protected_layers": quantization_report.get("summary", {}).get("protected_layers"),
        },
        "selected_actions": selected_actions,
        "evidence_delta": _evidence_delta(what_if_report),
        "validation_steps": _validation_steps(analysis, quantization_report, runtime_profile, selected_actions),
        "compiler_questions": [
            "Which planned actions are graph rewrites, and which are runtime or compiler scheduling changes?",
            "Which operators would map to analog arrays after the rewrite?",
            "Which operators remain digital, and what measured cost do they add?",
            "How many ADC/DAC crossings remain after placement?",
            "Which weights, activations, or channels need protected precision?",
        ],
        "do_not_claim": [
            "Do not claim the rewrite improved accuracy until the task dataset has been rerun.",
            "Do not claim measured energy or latency from this plan. It is still an estimate.",
            "Do not claim deployability until unsupported and fallback paths are either removed or explicitly implemented.",
        ],
    }
