HARDWARE_PLACEMENT_SCHEMA_VERSION = "hardware-placement-v0.1"


ANALOG_OPS = {"MatMul", "Gemm", "Conv"}
SENSITIVE_OPS = {"Softmax", "TopK", "ArgMax"}
LOGIT_OPS = {"LogSoftmax"}
NORMALIZATION_OPS = {"LayerNormalization", "BatchNormalization", "InstanceNormalization"}
CONTROL_OPS = {"If", "Loop", "Scan", "Where", "NonMaxSuppression"}


def _sensitivity_class(layer):
    op = layer.get("operator")
    layer_id = str(layer.get("id", "")).lower()
    if op in SENSITIVE_OPS or "attention" in layer_id:
        return "choice-sensitive"
    if op in LOGIT_OPS or "logit" in layer_id or "output" in layer_id:
        return "output-sensitive"
    if op in NORMALIZATION_OPS:
        return "scale-sensitive"
    if layer.get("risk") == "high":
        return "high-risk"
    if layer.get("placement") == "analog":
        return "projection-tolerant"
    return "digital-support"


def _expected_error_source(layer):
    placement = layer.get("placement")
    op = layer.get("operator")
    if placement == "analog":
        return "DAC rounding, row voltage drop, conductance error, ADC rounding, and calibration drift"
    if op in SENSITIVE_OPS:
        return "small numeric shifts can change the selected token or branch"
    if op in NORMALIZATION_OPS:
        return "scale and offset errors can move the following activation range"
    if placement in {"fallback", "unsupported"}:
        return "operator has no safe analog lowering in the current profile"
    return "ordinary digital arithmetic and memory movement"


def _governor_fields(layer):
    sensitivity = _sensitivity_class(layer)
    placement = layer.get("placement")
    residual_q8 = 6 if placement == "analog" else 0
    if sensitivity in {"choice-sensitive", "output-sensitive", "high-risk"}:
        residual_q8 = 40
    sensitivity_q8 = {
        "projection-tolerant": 96,
        "digital-support": 128,
        "scale-sensitive": 176,
        "choice-sensitive": 208,
        "output-sensitive": 224,
        "high-risk": 224,
    }.get(sensitivity, 160)
    return {
        "residual_q8": residual_q8,
        "sensitivity_q8": sensitivity_q8,
        "allow_analog": placement == "analog" and sensitivity == "projection-tolerant",
        "fallback_action": "digital_fallback" if placement != "analog" or sensitivity != "projection-tolerant" else "analog_path",
    }


def build_hardware_placement(analysis, package_report=None):
    rows = []
    analog_candidates = 0
    digital_only = 0
    fallback_points = 0
    converter_boundaries = 0
    for index, layer in enumerate(analysis.get("layers", [])):
        placement = layer.get("placement")
        op = layer.get("operator")
        analog_candidate = placement == "analog" or op in ANALOG_OPS
        sensitivity = _sensitivity_class(layer)
        fallback_required = placement != "analog" or sensitivity != "projection-tolerant"
        if analog_candidate:
            analog_candidates += 1
        if placement == "digital":
            digital_only += 1
        if fallback_required:
            fallback_points += 1
        boundary = layer.get("boundaries") or "no analog boundary"
        if "ADC" in boundary or "DAC" in boundary:
            converter_boundaries += 1
        rows.append(
            {
                "operator_id": layer.get("id") or f"operator.{index + 1}",
                "operator_kind": op,
                "shape": layer.get("shape"),
                "block": layer.get("block"),
                "placement": placement,
                "analog_candidate": analog_candidate,
                "digital_only_reason": None if analog_candidate else layer.get("reason"),
                "dac_boundary": "required before analog entry" if "DAC" in boundary else "not required here",
                "adc_boundary": "required after analog exit" if "ADC" in boundary else "not required here",
                "expected_error_source": _expected_error_source(layer),
                "model_sensitivity_class": sensitivity,
                "fallback_point": "resume digital path after this operator" if fallback_required else "not required for current local budget",
                "governor_fields": _governor_fields(layer),
                "plain_reading": (
                    "This operator can be tried on analog only if the residual budget and sensitivity class remain inside the governor limit."
                    if analog_candidate
                    else "This operator should stay digital in the current profile."
                ),
            }
        )
    return {
        "result_type": "hardware_placement",
        "schema_version": HARDWARE_PLACEMENT_SCHEMA_VERSION,
        "package_id": (package_report or {}).get("package_id"),
        "summary": {
            "operators": len(rows),
            "analog_candidates": analog_candidates,
            "digital_only": digital_only,
            "fallback_points": fallback_points,
            "converter_boundaries": converter_boundaries,
            "plain_reading": "The model graph has been translated into analog candidates, digital-only regions, converter boundaries, sensitivity classes, fallback points, and governor fields.",
        },
        "placement_rows": rows,
        "claim_boundary": {
            "allowed": "This artifact supports discussion of model-to-hardware placement for the current analyzed graph.",
            "not_allowed": "This is not a final compiler lowering, silicon placement, measured latency, measured energy, or tapeout signoff.",
        },
    }
