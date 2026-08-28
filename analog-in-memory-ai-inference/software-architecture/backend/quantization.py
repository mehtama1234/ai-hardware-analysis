MODALITY_PROFILES = {
    "audio_wake_word": {
        "label": "Audio wake-word",
        "task_metric": "false reject / false accept",
        "primary_failure_cost": "missed keyword or false trigger",
        "sensitive_ops": {"Conv", "MatMul", "Gemm"},
        "sensitive_name_terms": {"input", "feature", "classifier", "output", "logit"},
        "base_metric": 95.0,
        "int8_drop": 0.4,
        "selective_drop": 0.9,
        "all_int4_drop": 3.8,
        "plain_risk": "Small signal shifts can create missed wake words or false triggers, especially under noise.",
    },
    "vision_classification": {
        "label": "Vision classification",
        "task_metric": "top-1 accuracy / per-class drop",
        "primary_failure_cost": "wrong class",
        "sensitive_ops": {"Conv", "Gemm", "MatMul"},
        "sensitive_name_terms": {"stem", "first", "classifier", "head", "output", "logit"},
        "base_metric": 96.0,
        "int8_drop": 0.3,
        "selective_drop": 1.0,
        "all_int4_drop": 3.0,
        "plain_risk": "Average accuracy can hide a class-specific drop, especially in early feature extraction or the classifier head.",
    },
    "object_detection": {
        "label": "Object detection",
        "task_metric": "mAP / recall / box quality",
        "primary_failure_cost": "missed object",
        "sensitive_ops": {"Conv", "Gemm", "MatMul"},
        "sensitive_name_terms": {"detect", "box", "head", "confidence", "score", "logit"},
        "base_metric": 92.0,
        "int8_drop": 0.6,
        "selective_drop": 1.6,
        "all_int4_drop": 5.4,
        "plain_risk": "A small numeric shift can move boxes, lower confidence, or reduce recall on small objects.",
    },
    "robotics_perception": {
        "label": "Robotics perception",
        "task_metric": "latency / jitter / worst-case error",
        "primary_failure_cost": "unstable or late output",
        "sensitive_ops": {"MatMul", "Gemm", "Softmax", "LayerNormalization"},
        "sensitive_name_terms": {"fusion", "gate", "attention", "planner", "control", "output"},
        "base_metric": 91.0,
        "int8_drop": 0.7,
        "selective_drop": 1.9,
        "all_int4_drop": 6.0,
        "plain_risk": "Average accuracy can look fine while rare outputs become unstable or too late for the control loop.",
    },
    "industrial_anomaly": {
        "label": "Industrial anomaly",
        "task_metric": "anomaly recall / false negative rate",
        "primary_failure_cost": "missed fault",
        "sensitive_ops": {"MatMul", "Gemm", "Conv"},
        "sensitive_name_terms": {"anomaly", "score", "bottleneck", "reconstruct", "output", "fault"},
        "base_metric": 93.0,
        "int8_drop": 0.5,
        "selective_drop": 1.8,
        "all_int4_drop": 6.4,
        "plain_risk": "Rare faults can be underrepresented in calibration data, so average accuracy is not enough.",
    },
    "health_wearable": {
        "label": "Health wearable",
        "task_metric": "sensitivity / specificity / missed events",
        "primary_failure_cost": "missed health event",
        "sensitive_ops": {"Conv", "MatMul", "Gemm"},
        "sensitive_name_terms": {"input", "signal", "temporal", "event", "classifier", "output"},
        "base_metric": 94.0,
        "int8_drop": 0.5,
        "selective_drop": 1.4,
        "all_int4_drop": 5.2,
        "plain_risk": "Physiological signals can be small, noisy, and user-dependent, so first signal layers and event heads need protection.",
    },
    "edge_llm": {
        "label": "Edge LLM",
        "task_metric": "perplexity / task score / token latency",
        "primary_failure_cost": "quality degradation",
        "sensitive_ops": {"MatMul", "Gemm", "Softmax", "LayerNormalization"},
        "sensitive_name_terms": {"attention", "qkv", "query", "key", "value", "logit", "lm_head", "output"},
        "base_metric": 88.0,
        "int8_drop": 0.8,
        "selective_drop": 2.1,
        "all_int4_drop": 7.0,
        "plain_risk": "Attention, normalization-adjacent layers, and output logits can change token quality even when matrix coverage looks good.",
    },
}


def modality_profiles():
    return {
        key: {
            "label": value["label"],
            "task_metric": value["task_metric"],
            "primary_failure_cost": value["primary_failure_cost"],
            "plain_risk": value["plain_risk"],
        }
        for key, value in MODALITY_PROFILES.items()
    }


def _is_first_or_last(index, count):
    return index == 0 or index == count - 1


def _is_sensitive(layer, index, count, profile):
    name = layer["id"].lower()
    if layer["operator"] in profile["sensitive_ops"]:
        if _is_first_or_last(index, count):
            return True
        if any(term in name for term in profile["sensitive_name_terms"]):
            return True
        if layer["risk"] in {"medium", "high"}:
            return True
    if layer["placement"] in {"fallback", "unsupported"}:
        return True
    return False


def _recommend_precision(layer, sensitive):
    if layer["placement"] in {"digital", "fallback", "unsupported"}:
        return "keep digital"
    if sensitive:
        return "INT8 protected"
    if layer["operator"] in {"MatMul", "Gemm", "Conv"}:
        return "INT4 candidate"
    return "INT8"


def _precision_reason(layer, sensitive, profile):
    if layer["placement"] in {"digital", "fallback", "unsupported"}:
        return "This layer is not on the analog path, so lower analog precision is not the main decision."
    if sensitive:
        return f"Protect this layer because {profile['task_metric']} can be affected by errors here."
    return "This analog-friendly layer is a candidate for lower precision because it is not marked as task-sensitive."


def _risk_level(recommendation, layer):
    if layer["placement"] == "unsupported":
        return "high"
    if recommendation == "keep digital":
        return "medium" if layer["placement"] == "fallback" else "low"
    if recommendation == "INT8 protected":
        return "medium"
    return "low"


def _metric_value(base, drop):
    return round(max(base - drop, 0), 2)


def estimate_quantization(analysis, modality="vision_classification", task_type=None, primary_failure_cost=None):
    profile = MODALITY_PROFILES.get(modality, MODALITY_PROFILES["vision_classification"])
    layers = analysis["layers"]
    count = len(layers)
    layer_recommendations = []
    protected = []
    int4_candidates = []

    for index, layer in enumerate(layers):
        sensitive = _is_sensitive(layer, index, count, profile)
        recommendation = _recommend_precision(layer, sensitive)
        item = {
            "layer_id": layer["id"],
            "operator": layer["operator"],
            "placement": layer["placement"],
            "recommended_precision": recommendation,
            "risk": _risk_level(recommendation, layer),
            "reason": _precision_reason(layer, sensitive, profile),
        }
        layer_recommendations.append(item)
        if recommendation == "INT8 protected":
            protected.append(item)
        if recommendation == "INT4 candidate":
            int4_candidates.append(item)

    sensitive_count = len(protected)
    fallback_count = sum(1 for layer in layers if layer["placement"] in {"fallback", "unsupported"})
    boundary_count = len(analysis.get("boundary_events", []))
    analog_coverage = analysis["summary"].get("analog_coverage_percent", 0)

    int8_drop = profile["int8_drop"] + (fallback_count * 0.1)
    selective_drop = profile["selective_drop"] + (sensitive_count * 0.12) + (boundary_count * 0.05)
    all_int4_drop = profile["all_int4_drop"] + (sensitive_count * 0.22) + (fallback_count * 0.2)
    if analog_coverage < 50:
        selective_drop += 0.4
        all_int4_drop += 0.7

    base = profile["base_metric"]
    trials = [
        {"precision": "baseline", "metric_value": base, "risk": "reference", "drop": 0.0},
        {"precision": "INT8", "metric_value": _metric_value(base, int8_drop), "risk": "low", "drop": round(int8_drop, 2)},
        {
            "precision": "INT4 selective",
            "metric_value": _metric_value(base, selective_drop),
            "risk": "medium" if sensitive_count else "low",
            "drop": round(selective_drop, 2),
        },
        {"precision": "INT4 all layers", "metric_value": _metric_value(base, all_int4_drop), "risk": "high", "drop": round(all_int4_drop, 2)},
    ]

    recommendations = []
    if protected:
        recommendations.append(
            {
                "id": "Q1",
                "text": f"Keep {len(protected)} sensitive analog layer(s) at INT8 or a protected path.",
                "tag": "precision",
            }
        )
    if int4_candidates:
        recommendations.append(
            {
                "id": "Q2",
                "text": f"Try INT4 on {len(int4_candidates)} lower-risk analog layer(s) first.",
                "tag": "efficiency",
            }
        )
    recommendations.append(
        {
            "id": "Q3",
            "text": "Treat this as estimated until a calibration dataset is run through the quantized model.",
            "tag": "provenance",
        }
    )

    return {
        "result_type": "quantization_report",
        "provenance": "estimated",
        "confidence": "low",
        "modality": modality,
        "modality_label": profile["label"],
        "task_type": task_type or profile["label"].lower().replace(" ", "_"),
        "task_metric": profile["task_metric"],
        "primary_failure_cost": primary_failure_cost or profile["primary_failure_cost"],
        "plain_risk": profile["plain_risk"],
        "summary": {
            "protected_layers": len(protected),
            "int4_candidates": len(int4_candidates),
            "sensitive_layers": sensitive_count,
            "recommended_policy": "INT8 protected + INT4 selective" if int4_candidates else "INT8 protected",
            "status": "estimated, not measured",
        },
        "trials": trials,
        "protected_layers": protected,
        "layer_recommendations": layer_recommendations,
        "recommendations": recommendations,
    }

