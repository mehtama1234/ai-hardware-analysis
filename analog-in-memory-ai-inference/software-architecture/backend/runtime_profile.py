RUNTIME_MODES = {
    "balanced": {
        "label": "Balanced",
        "latency_factor": 1.0,
        "energy_factor": 1.0,
        "host_overhead_ms": 0.18,
        "host_overhead_uj": 1.6,
        "idle_energy_factor": 0.06,
    },
    "low_power": {
        "label": "Low power",
        "latency_factor": 1.18,
        "energy_factor": 0.82,
        "host_overhead_ms": 0.22,
        "host_overhead_uj": 1.3,
        "idle_energy_factor": 0.05,
    },
    "low_latency": {
        "label": "Low latency",
        "latency_factor": 0.82,
        "energy_factor": 1.22,
        "host_overhead_ms": 0.15,
        "host_overhead_uj": 2.0,
        "idle_energy_factor": 0.08,
    },
}


def runtime_modes():
    return {
        key: {
            "label": value["label"],
            "plain_meaning": _mode_plain_meaning(key),
        }
        for key, value in RUNTIME_MODES.items()
    }


def _mode_plain_meaning(mode):
    if mode == "low_power":
        return "Spend less energy even if the result arrives later."
    if mode == "low_latency":
        return "Finish sooner, accepting higher energy and more heat pressure."
    return "Use the middle setting for the first product comparison."


def _target_number(text_or_number):
    if isinstance(text_or_number, (int, float)):
        return float(text_or_number)
    digits = "".join(ch if ch.isdigit() or ch == "." else " " for ch in str(text_or_number)).split()
    return float(digits[0]) if digits else 0.0


def _placement_note(layer):
    placement = layer["placement"]
    if placement == "analog":
        return "Matrix-heavy work uses the analog path; count conversion and calibration around it."
    if placement == "digital":
        return "This stays in digital support logic because exact control is more important than analog speed here."
    if placement == "fallback":
        return "This needs a fallback path, so the runtime must schedule it and move data safely."
    return "This operator is not supported by the current capability profile."


def _quantization_lookup(quantization_report):
    if not quantization_report:
        return {}
    return {
        item["layer_id"]: item
        for item in quantization_report.get("layer_recommendations", [])
    }


def _trace_layer(layer, mode, quantization_by_layer):
    precision = quantization_by_layer.get(layer["id"], {}).get("recommended_precision", "not selected")
    base_latency = float(layer.get("latency_ms", 0))
    compute_energy = float(layer.get("energy_uj", 0))
    conversion_energy = float(layer.get("conversion_energy_uj", 0))
    memory_energy = float(layer.get("memory_energy_uj", 0))

    placement_multiplier = {
        "analog": 1.0,
        "digital": 1.15,
        "fallback": 1.45,
        "unsupported": 1.8,
    }.get(layer["placement"], 1.2)
    risk_multiplier = {
        "low": 1.0,
        "medium": 1.08,
        "high": 1.22,
    }.get(layer.get("risk", "low"), 1.0)

    latency_ms = base_latency * mode["latency_factor"] * placement_multiplier * risk_multiplier
    energy_uj = (compute_energy + conversion_energy + memory_energy) * mode["energy_factor"] * risk_multiplier

    return {
        "layer_id": layer["id"],
        "operator": layer["operator"],
        "block": layer.get("block", "unassigned"),
        "placement": layer["placement"],
        "precision": precision,
        "latency_ms": round(latency_ms, 3),
        "energy_uj": round(energy_uj, 3),
        "compute_energy_uj": round(compute_energy * mode["energy_factor"], 3),
        "conversion_energy_uj": round(conversion_energy * mode["energy_factor"], 3),
        "memory_energy_uj": round(memory_energy * mode["energy_factor"], 3),
        "risk": layer.get("risk", "low"),
        "note": _placement_note(layer),
    }


def _main_bottleneck(trace):
    if not trace:
        return "no executable layers found"
    conversion_total = sum(item["conversion_energy_uj"] for item in trace)
    memory_total = sum(item["memory_energy_uj"] for item in trace)
    fallback_total = sum(item["energy_uj"] for item in trace if item["placement"] in {"fallback", "unsupported"})
    slowest = max(trace, key=lambda item: item["latency_ms"])

    if fallback_total > max(conversion_total, memory_total):
        return "fallback and unsupported operators"
    if conversion_total > memory_total:
        return "analog/digital conversion overhead"
    if memory_total > 0:
        return "memory movement"
    return f"slowest layer: {slowest['layer_id']}"


def _build_bottlenecks(trace):
    top_latency = sorted(trace, key=lambda item: item["latency_ms"], reverse=True)[:3]
    top_energy = sorted(trace, key=lambda item: item["energy_uj"], reverse=True)[:3]
    fallback = [item for item in trace if item["placement"] in {"fallback", "unsupported"}]
    conversion = [item for item in trace if item["conversion_energy_uj"] > 0]

    bottlenecks = []
    for item in top_latency:
        bottlenecks.append(
            {
                "id": item["layer_id"],
                "kind": "latency",
                "severity": "medium" if item["risk"] != "high" else "high",
                "text": f"{item['layer_id']} is one of the slowest layers at {item['latency_ms']} ms.",
            }
        )
    for item in top_energy:
        bottlenecks.append(
            {
                "id": item["layer_id"],
                "kind": "energy",
                "severity": "medium" if item["risk"] != "high" else "high",
                "text": f"{item['layer_id']} is one of the largest energy contributors at {item['energy_uj']} uJ.",
            }
        )
    if fallback:
        bottlenecks.append(
            {
                "id": "fallback-path",
                "kind": "mapping",
                "severity": "high" if any(item["placement"] == "unsupported" for item in fallback) else "medium",
                "text": f"{len(fallback)} layer(s) need fallback or new operator support.",
            }
        )
    if conversion:
        bottlenecks.append(
            {
                "id": "conversion-path",
                "kind": "boundary",
                "severity": "medium",
                "text": f"{len(conversion)} layer(s) include ADC/DAC conversion energy.",
            }
        )
    return bottlenecks[:7]


def _build_recommendations(trace, meets_latency, meets_energy, quantization_report):
    recommendations = []
    if not meets_latency:
        recommendations.append(
            {
                "id": "R1",
                "tag": "latency",
                "text": "Reduce fallback work or try the low-latency runtime mode before claiming the target is met.",
            }
        )
    if not meets_energy:
        recommendations.append(
            {
                "id": "R2",
                "tag": "energy",
                "text": "Reduce conversion crossings and memory movement before claiming the energy target is met.",
            }
        )
    if any(item["placement"] == "unsupported" for item in trace):
        recommendations.append(
            {
                "id": "R3",
                "tag": "operator",
                "text": "Add operator support or rewrite unsupported model nodes before deployment packaging.",
            }
        )
    if quantization_report and quantization_report.get("protected_layers"):
        recommendations.append(
            {
                "id": "R4",
                "tag": "accuracy",
                "text": "Keep protected layers at the recommended precision while measuring task accuracy.",
            }
        )
    recommendations.append(
        {
            "id": "R5",
            "tag": "proof",
            "text": "Treat this as simulated until a reference dataset and board telemetry produce measured results.",
        }
    )
    return recommendations[:5]


def run_simulated_profile(analysis, quantization_report=None, runtime_mode="balanced"):
    mode = RUNTIME_MODES.get(runtime_mode, RUNTIME_MODES["balanced"])
    quantization_by_layer = _quantization_lookup(quantization_report)
    trace = [_trace_layer(layer, mode, quantization_by_layer) for layer in analysis.get("layers", [])]

    layer_latency = sum(item["latency_ms"] for item in trace)
    layer_energy = sum(item["energy_uj"] for item in trace)
    host_latency = mode["host_overhead_ms"] + (0.012 * len(trace))
    host_energy = mode["host_overhead_uj"] + (0.04 * len(trace))
    idle_energy = layer_energy * mode["idle_energy_factor"]

    latency_ms = round(layer_latency + host_latency, 3)
    energy_uj = round(layer_energy + host_energy + idle_energy, 3)
    latency_target = _target_number(analysis.get("targets", {}).get("latency", 0))
    energy_target = _target_number(analysis.get("targets", {}).get("energy", 0))
    meets_latency = latency_target == 0 or latency_ms <= latency_target
    meets_energy = energy_target == 0 or energy_uj <= energy_target

    return {
        "result_type": "runtime_profile",
        "provenance": "simulated",
        "confidence": "low",
        "runtime_mode": runtime_mode if runtime_mode in RUNTIME_MODES else "balanced",
        "runtime_mode_label": mode["label"],
        "summary": {
            "latency_ms": latency_ms,
            "energy_uj": energy_uj,
            "layer_latency_ms": round(layer_latency, 3),
            "layer_energy_uj": round(layer_energy, 3),
            "host_overhead_ms": round(host_latency, 3),
            "host_overhead_uj": round(host_energy, 3),
            "idle_energy_uj": round(idle_energy, 3),
            "latency_target_ms": latency_target,
            "energy_target_uj": energy_target,
            "meets_latency_target": meets_latency,
            "meets_energy_target": meets_energy,
            "main_bottleneck": _main_bottleneck(trace),
            "status": "simulated, not measured",
        },
        "trace": trace,
        "bottlenecks": _build_bottlenecks(trace),
        "recommendations": _build_recommendations(trace, meets_latency, meets_energy, quantization_report),
    }
