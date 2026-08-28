ANALOG_FRIENDLY_OPS = {
    "MatMul",
    "Gemm",
    "Conv",
}

DIGITAL_REQUIRED_OPS = {
    "Add",
    "BatchNormalization",
    "Cast",
    "Concat",
    "Div",
    "Dropout",
    "Erf",
    "Exp",
    "Flatten",
    "Gather",
    "Gelu",
    "GlobalAveragePool",
    "LayerNormalization",
    "Log",
    "MaxPool",
    "Mul",
    "Pow",
    "ReduceMean",
    "Relu",
    "Reshape",
    "Sigmoid",
    "Softmax",
    "Sqrt",
    "Sub",
    "Tanh",
    "Transpose",
}

FALLBACK_OPS = {
    "DepthwiseConv",
    "NonMaxSuppression",
    "Resize",
    "ScatterND",
    "TopK",
}

SENSITIVE_OPS = {
    "MatMul",
    "Gemm",
    "Softmax",
    "LayerNormalization",
}


TARGET_PROFILES = {
    "wearable": {
        "label": "AS-EDGE wearable profile",
        "energy_target_uj": 50,
        "latency_target_ms": 6,
        "accuracy_target": "94.0%",
        "temperature": "0C to 70C",
        "voltage": "0.72V to 0.88V",
        "memory_limit_kb": 512,
        "precision_modes": ["INT8", "INT4 selective"],
        "adc_energy_uj": 0.9,
        "dac_energy_uj": 0.7,
        "memory_move_energy_uj": 0.35,
    },
    "camera": {
        "label": "AS-EDGE camera profile",
        "energy_target_uj": 90,
        "latency_target_ms": 12,
        "accuracy_target": "95.0%",
        "temperature": "-10C to 80C",
        "voltage": "0.76V to 0.90V",
        "memory_limit_kb": 2048,
        "precision_modes": ["INT8", "INT4 selective", "ternary weights"],
        "adc_energy_uj": 1.1,
        "dac_energy_uj": 0.8,
        "memory_move_energy_uj": 0.45,
    },
    "robotics": {
        "label": "AS-EDGE robotics profile",
        "energy_target_uj": 150,
        "latency_target_ms": 8,
        "accuracy_target": "90.0%",
        "temperature": "-20C to 60C",
        "voltage": "0.74V to 0.88V",
        "memory_limit_kb": 4096,
        "precision_modes": ["INT8", "INT4 selective"],
        "adc_energy_uj": 1.4,
        "dac_energy_uj": 1.0,
        "memory_move_energy_uj": 0.6,
    },
}


def classify_operator(op_type):
    if op_type in ANALOG_FRIENDLY_OPS:
        return "analog", "analog core", "matrix-heavy operator with reusable weights"
    if op_type in FALLBACK_OPS:
        return "fallback", "fallback", "operator needs a non-analog execution path"
    if op_type in DIGITAL_REQUIRED_OPS:
        return "digital", "digital path", "operator is better handled in digital support logic"
    return "unsupported", "unsupported", "operator is not in the current hardware capability profile"


def risk_for_operator(op_type, placement):
    if placement == "unsupported":
        return "high"
    if placement == "fallback":
        return "medium"
    if op_type in SENSITIVE_OPS:
        return "medium"
    return "low"
