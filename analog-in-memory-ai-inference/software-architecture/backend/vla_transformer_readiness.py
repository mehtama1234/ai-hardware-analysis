VLA_READINESS_SCHEMA_VERSION = "vla-readiness-v0.1"

MATRIX_OPS = {"MatMul", "Gemm", "Conv"}
ATTENTION_OPS = {"Attention", "MultiHeadAttention", "Softmax"}
NORMALIZATION_OPS = {"LayerNormalization", "LayerNorm", "BatchNormalization"}
NONLINEAR_OPS = {"Softmax", "Gelu", "Relu", "Sigmoid", "Tanh"}
MOVEMENT_OPS = {"Reshape", "Transpose", "Concat", "Slice", "Gather", "Unsqueeze", "Squeeze", "Flatten"}


def _operators(analysis):
    return [layer.get("operator", "") for layer in analysis.get("layers", [])]


def _count(layers, predicate):
    return sum(1 for layer in layers if predicate(layer))


def _ids(layers, predicate, limit=8):
    return [layer.get("id") for layer in layers if predicate(layer)][:limit]


def _model_family(op_counts, blocks):
    has_attention = any(op in op_counts for op in ATTENTION_OPS) or any("attention" in block.get("kind", "") for block in blocks)
    has_norm = any(op in op_counts for op in NORMALIZATION_OPS)
    has_movement = any(op in op_counts for op in MOVEMENT_OPS)
    matrix_count = sum(op_counts.get(op, 0) for op in MATRIX_OPS)
    conv_count = op_counts.get("Conv", 0)
    if has_attention and has_norm:
        return "transformer-like"
    if has_attention:
        return "attention-like hybrid"
    if matrix_count >= 3 and has_movement:
        return "sequence-or-MLP-like"
    if conv_count >= max(1, matrix_count):
        return "CNN-like"
    if matrix_count:
        return "MLP-like"
    return "unknown"


def _claim_level(model_family, attention_count, digital_required_count, fallback_count, boundary_events, memory_percent):
    if fallback_count:
        return "not_vla_ready: fallback or unsupported operators remain"
    if attention_count and (boundary_events > 4 or memory_percent > 30):
        return "early_transformer_fit: attention and memory movement need measured proof"
    if model_family in {"transformer-like", "attention-like hybrid"} and digital_required_count:
        return "hybrid_vla_candidate: analog matrix work plus digital transformer support required"
    if model_family in {"MLP-like", "CNN-like", "sequence-or-MLP-like"}:
        return "not_vla_proof: simpler model fit does not prove VLA readiness"
    return "analysis_only: model family unclear"


def _plain_reading(model_family, claim_level):
    if claim_level.startswith("hybrid_vla_candidate"):
        return (
            "This looks like a hybrid transformer/VLA candidate. The analog path may help with matrix-heavy blocks, "
            "but digital support is still needed for attention control, nonlinear operators, movement, and safety glue."
        )
    if claim_level.startswith("early_transformer_fit"):
        return (
            "This has transformer-like signals, but memory movement or analog/digital crossings are still major proof gaps."
        )
    if claim_level.startswith("not_vla_ready"):
        return "This package is not VLA-ready yet because fallback or unsupported operators remain."
    if claim_level.startswith("not_vla_proof"):
        return (
            f"This model is {model_family}. It can be useful for edge inference analysis, but it does not prove readiness for full VLA workloads."
        )
    return "The model family is unclear, so VLA readiness should stay at analysis-only confidence."


def build_vla_readiness(analysis, quantization_report, runtime_profile, system_boundary, package_report=None):
    layers = analysis.get("layers", [])
    blocks = analysis.get("blocks", [])
    op_counts = {}
    for op in _operators(analysis):
        op_counts[op] = op_counts.get(op, 0) + 1
    model_family = _model_family(op_counts, blocks)
    matrix_layers = [layer for layer in layers if layer.get("operator") in MATRIX_OPS]
    analog_matrix_layers = [layer for layer in matrix_layers if layer.get("placement") == "analog"]
    attention_layers = [
        layer for layer in layers
        if layer.get("operator") in ATTENTION_OPS or "attention" in layer.get("id", "").lower()
    ]
    digital_required_layers = [
        layer for layer in layers
        if layer.get("operator") in ATTENTION_OPS | NORMALIZATION_OPS | NONLINEAR_OPS | MOVEMENT_OPS
        and layer.get("placement") != "analog"
    ]
    fallback_layers = [layer for layer in layers if layer.get("placement") in {"fallback", "unsupported"}]
    boundary_summary = (system_boundary or {}).get("summary", {})
    boundary_events = int(boundary_summary.get("boundary_events", 0) or 0)
    memory_percent = float(boundary_summary.get("memory_energy_percent", 0) or 0)
    conversion_percent = float(boundary_summary.get("conversion_energy_percent", 0) or 0)
    protected_layers = int((quantization_report.get("summary") or {}).get("protected_layers", 0) or 0)
    claim_level = _claim_level(
        model_family,
        len(attention_layers),
        len(digital_required_layers),
        len(fallback_layers),
        boundary_events,
        memory_percent,
    )
    matrix_coverage = round((len(analog_matrix_layers) / len(matrix_layers)) * 100, 1) if matrix_layers else 0
    readiness_score = 35
    readiness_score += min(25, matrix_coverage / 4)
    readiness_score -= len(fallback_layers) * 12
    readiness_score -= min(18, boundary_events * 2)
    readiness_score -= min(12, memory_percent / 3)
    readiness_score -= min(8, protected_layers * 2)
    if model_family in {"transformer-like", "attention-like hybrid"}:
        readiness_score += 8
    readiness_score = round(max(0, min(100, readiness_score)), 1)
    return {
        "result_type": "vla_readiness",
        "schema_version": VLA_READINESS_SCHEMA_VERSION,
        "provenance": "derived from operator analysis, quantization report, runtime profile, and system boundary",
        "confidence": "low",
        "package_id": (package_report or {}).get("package_id"),
        "model_family": model_family,
        "claim_level": claim_level,
        "summary": {
            "plain_reading": _plain_reading(model_family, claim_level),
            "readiness_score": readiness_score,
            "matrix_layer_count": len(matrix_layers),
            "analog_matrix_layer_count": len(analog_matrix_layers),
            "analog_matrix_coverage_percent": matrix_coverage,
            "attention_or_softmax_layers": len(attention_layers),
            "digital_transformer_support_layers": len(digital_required_layers),
            "fallback_or_unsupported_layers": len(fallback_layers),
            "boundary_events": boundary_events,
            "memory_energy_percent": memory_percent,
            "conversion_energy_percent": conversion_percent,
            "protected_layers": protected_layers,
        },
        "analog_opportunity": {
            "plain_reading": "Analog is most plausible for repeated matrix-heavy blocks, not for the whole VLA stack.",
            "layer_ids": _ids(layers, lambda layer: layer.get("operator") in MATRIX_OPS and layer.get("placement") == "analog"),
            "operators": sorted({layer.get("operator") for layer in analog_matrix_layers}),
        },
        "digital_required_work": {
            "plain_reading": "Transformer-class models need digital support for attention control, nonlinear functions, normalization, reshaping, and glue logic.",
            "layer_ids": _ids(digital_required_layers, lambda layer: True),
            "operators": sorted({layer.get("operator") for layer in digital_required_layers}),
        },
        "memory_and_boundary_risks": {
            "plain_reading": "VLA readiness depends on memory movement and boundary crossings, not only analog MAC efficiency.",
            "boundary_events": boundary_events,
            "memory_energy_percent": memory_percent,
            "conversion_energy_percent": conversion_percent,
            "top_memory_movers": (system_boundary or {}).get("top_memory_movers", [])[:5],
            "top_boundaries": (system_boundary or {}).get("top_boundaries", [])[:5],
        },
        "evidence_needed": [
            "compiler-produced analog/digital placement for a transformer or VLA graph",
            "task accuracy on the target modality after quantization and analog-error injection",
            "completed inference latency and energy with memory movement and ADC/DAC counted",
            "worst-case latency and jitter if the result feeds a physical control loop",
            "proof that digital attention, normalization, movement, and fallback paths do not erase the analog gain",
        ],
        "what_not_to_claim": [
            "Do not say analog MAC efficiency proves VLA readiness.",
            "Do not say a CNN or MLP fit proves support for vision-language-action models.",
            "Do not hide attention, softmax, layer normalization, reshape, transpose, memory movement, or fallback costs.",
            "Do not claim robotic action readiness from inference metrics alone.",
        ],
    }
