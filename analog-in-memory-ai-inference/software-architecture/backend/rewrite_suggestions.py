REWRITE_SCHEMA_VERSION = "rewrite-suggestions-v0.1"


ANALOG_FRIENDLY_OPERATORS = {"MatMul", "Gemm", "Conv"}
DIGITAL_SUPPORT_OPERATORS = {"Add", "Relu", "Gelu", "Sigmoid", "Tanh", "BatchNormalization", "LayerNormalization", "Softmax"}


def _priority(severity):
    return {"high": 0, "medium": 1, "low": 2}.get(severity, 3)


def _boundary_suggestion(event, layer):
    if event.get("event") == "ADC":
        pattern = "Keep the following bias, activation, or normalization close to the analog result, or fuse it into the post-processing path."
    else:
        pattern = "Group adjacent matrix-heavy work so the runtime does not repeatedly move values from digital into analog."
    return {
        "id": f"rewrite.boundary.{event.get('layer_id')}.{event.get('event')}".lower().replace(" ", "-"),
        "severity": "medium",
        "layer_id": event.get("layer_id"),
        "operator": layer.get("operator") if layer else "unknown",
        "problem": event.get("reason"),
        "rewrite_pattern": pattern,
        "why_it_helps": "Each analog/digital crossing spends conversion energy and adds scheduling overhead. Fewer crossings make the analog core's compute savings easier to keep at the full-system level.",
        "expected_impact": {
            "analog_coverage": "unchanged",
            "latency": "small to medium improvement if repeated crossings are removed",
            "energy": f"could avoid about {event.get('energy_uj', 'n/a')} uJ for this crossing in the current estimate",
            "accuracy_risk": "low if the mathematical result is preserved",
        },
        "verification": "Rerun model-fit analysis and check that boundary event count and conversion energy decrease.",
    }


def _layer_suggestion(layer):
    placement = layer.get("placement")
    operator = layer.get("operator")
    if placement == "unsupported":
        return {
            "id": f"rewrite.unsupported.{layer.get('id')}",
            "severity": "high",
            "layer_id": layer.get("id"),
            "operator": operator,
            "problem": "This operator is not supported by the current target profile.",
            "rewrite_pattern": "Replace it with supported ONNX operators, approximate it with supported math, or keep it outside the analog path with an explicit measured digital path.",
            "why_it_helps": "Unsupported operators block a deployable package because the runtime cannot execute the full graph safely.",
            "expected_impact": {
                "analog_coverage": "may improve if the replacement uses MatMul, Gemm, or Conv",
                "latency": "depends on replacement cost",
                "energy": "could improve if fallback movement is removed",
                "accuracy_risk": "medium to high; replacement must be checked on the task dataset",
            },
            "verification": "Rerun import and confirm unsupported operator count reaches zero before comparing performance.",
        }
    if placement == "fallback":
        return {
            "id": f"rewrite.fallback.{layer.get('id')}",
            "severity": "high",
            "layer_id": layer.get("id"),
            "operator": operator,
            "problem": "This operator needs fallback or special runtime support.",
            "rewrite_pattern": "Rewrite the layer into supported primitive operators or add a dedicated digital-support implementation with measured cost.",
            "why_it_helps": "Fallback work can erase analog energy gains because values leave the fast path and must be scheduled by the host or digital support logic.",
            "expected_impact": {
                "analog_coverage": "may improve if rewritten into analog-friendly primitives",
                "latency": "medium improvement if host fallback is removed",
                "energy": "medium improvement if data movement and fallback compute are reduced",
                "accuracy_risk": "medium; verify task metric after rewrite",
            },
            "verification": "Rerun the project and compare fallback count, latency, energy, and evidence gates.",
        }
    if placement == "digital" and operator in DIGITAL_SUPPORT_OPERATORS:
        return {
            "id": f"rewrite.digital-support.{layer.get('id')}",
            "severity": "low",
            "layer_id": layer.get("id"),
            "operator": operator,
            "problem": "This support operator stays digital and may create conversion boundaries near analog layers.",
            "rewrite_pattern": "Try operator fusion, scheduling it next to other digital work, or folding constants such as bias into the adjacent matrix operation when mathematically valid.",
            "why_it_helps": "The operator may be cheap by itself, but placing it between analog-heavy layers can force extra ADC/DAC movement.",
            "expected_impact": {
                "analog_coverage": "usually unchanged",
                "latency": "small improvement",
                "energy": "small to medium improvement if a boundary is removed",
                "accuracy_risk": "low for exact fusion; medium for approximations",
            },
            "verification": "Rerun analysis and check whether block placement is less fragmented.",
        }
    if placement == "analog" and layer.get("risk") in {"medium", "high"}:
        return {
            "id": f"rewrite.protect-analog.{layer.get('id')}",
            "severity": "medium",
            "layer_id": layer.get("id"),
            "operator": operator,
            "problem": "This analog-friendly layer may be sensitive to quantization or analog numeric error.",
            "rewrite_pattern": "Keep this layer at protected precision, split very sensitive weights into a protected path, or use mixed precision for high-impact channels.",
            "why_it_helps": "Analog compute saves energy only if accuracy survives the numeric behavior of the analog path.",
            "expected_impact": {
                "analog_coverage": "unchanged",
                "latency": "small cost if protection adds work",
                "energy": "small cost, but safer accuracy",
                "accuracy_risk": "reduced after task-dataset validation",
            },
            "verification": "Run quantization sensitivity and compare the task metric before and after protection.",
        }
    return None


def _coverage_suggestion(analysis):
    summary = analysis.get("summary", {})
    if summary.get("analog_coverage_percent", 0) >= 60:
        return None
    blocks = analysis.get("blocks", [])
    digital_blocks = [block for block in blocks if block.get("placement") in {"digital", "hybrid"}]
    return {
        "id": "rewrite.coverage.increase-matrix-work",
        "severity": "medium",
        "layer_id": "model",
        "operator": "graph",
        "problem": f"Only {summary.get('analog_coverage_percent', 0)}% of operators map to the analog path.",
        "rewrite_pattern": "Look for model variants that express more work as MatMul, Gemm, or Conv blocks and avoid interleaving small digital operators between analog-heavy layers.",
        "why_it_helps": "Analog hardware helps most when repeated matrix math dominates the completed inference and data can stay near the compute array.",
        "expected_impact": {
            "analog_coverage": "medium to high improvement if model structure changes",
            "latency": "medium improvement if more work stays on the analog path",
            "energy": "medium improvement if conversion and digital support share drop",
            "accuracy_risk": "depends on model rewrite; validate with the target dataset",
        },
        "verification": f"Rerun analysis and compare analog coverage and block placement. Current hybrid/digital blocks: {len(digital_blocks)}.",
    }


def build_rewrite_suggestions(analysis, quantization_report=None, runtime_profile=None, decision_report=None):
    layers = analysis.get("layers", [])
    layers_by_id = {layer.get("id"): layer for layer in layers}
    suggestions = []
    for layer in layers:
        suggestion = _layer_suggestion(layer)
        if suggestion:
            suggestions.append(suggestion)
    for event in analysis.get("boundary_events", []):
        suggestion = _boundary_suggestion(event, layers_by_id.get(event.get("layer_id")))
        suggestions.append(suggestion)
    coverage = _coverage_suggestion(analysis)
    if coverage:
        suggestions.append(coverage)

    suggestions = sorted(suggestions, key=lambda item: (_priority(item["severity"]), item["id"]))[:10]
    focus = "increase analog coverage"
    if any(item["severity"] == "high" for item in suggestions):
        focus = "remove unsupported or fallback work"
    elif any(item["id"].startswith("rewrite.boundary") for item in suggestions):
        focus = "reduce analog/digital crossings"
    return {
        "result_type": "rewrite_suggestions",
        "schema_version": REWRITE_SCHEMA_VERSION,
        "provenance": "derived from model-fit analysis",
        "confidence": "low",
        "focus": focus,
        "summary": {
            "suggestion_count": len(suggestions),
            "analog_coverage_percent": analysis.get("summary", {}).get("analog_coverage_percent"),
            "fallback_count": analysis.get("summary", {}).get("fallback_count"),
            "boundary_count": len(analysis.get("boundary_events", [])),
            "decision": (decision_report or {}).get("decision"),
        },
        "suggestions": suggestions,
        "how_to_use": [
            "Apply one rewrite at a time and rerun the same project settings.",
            "Compare completed-inference energy and latency, not only operator coverage.",
            "Check task accuracy after any approximation, fusion, or precision change.",
        ],
    }
