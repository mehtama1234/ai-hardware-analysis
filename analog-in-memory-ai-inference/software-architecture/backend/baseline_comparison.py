DIGITAL_BASELINES = {
    "wearable": {
        "label": "low-power digital MCU/NPU estimate",
        "analog_op_latency_factor": 2.4,
        "analog_op_energy_factor": 4.2,
        "digital_op_latency_factor": 1.0,
        "digital_op_energy_factor": 1.0,
        "fallback_latency_factor": 0.95,
        "fallback_energy_factor": 0.95,
        "host_overhead_ms": 0.22,
        "host_overhead_uj": 1.8,
        "idle_energy_factor": 0.08,
    },
    "camera": {
        "label": "embedded digital vision accelerator estimate",
        "analog_op_latency_factor": 1.9,
        "analog_op_energy_factor": 3.1,
        "digital_op_latency_factor": 0.95,
        "digital_op_energy_factor": 0.95,
        "fallback_latency_factor": 0.9,
        "fallback_energy_factor": 0.9,
        "host_overhead_ms": 0.28,
        "host_overhead_uj": 2.6,
        "idle_energy_factor": 0.1,
    },
    "robotics": {
        "label": "thermally limited digital edge accelerator estimate",
        "analog_op_latency_factor": 2.1,
        "analog_op_energy_factor": 3.6,
        "digital_op_latency_factor": 1.05,
        "digital_op_energy_factor": 1.05,
        "fallback_latency_factor": 1.0,
        "fallback_energy_factor": 1.0,
        "host_overhead_ms": 0.35,
        "host_overhead_uj": 3.2,
        "idle_energy_factor": 0.12,
    },
}


def _factor_for_layer(layer, baseline):
    placement = layer["placement"]
    if placement == "analog":
        return baseline["analog_op_latency_factor"], baseline["analog_op_energy_factor"]
    if placement == "digital":
        return baseline["digital_op_latency_factor"], baseline["digital_op_energy_factor"]
    return baseline["fallback_latency_factor"], baseline["fallback_energy_factor"]


def _safe_ratio(numerator, denominator):
    if denominator <= 0:
        return 0.0
    return numerator / denominator


def compare_to_digital_baseline(analysis, runtime_profile, target_profile="wearable"):
    baseline = DIGITAL_BASELINES.get(target_profile, DIGITAL_BASELINES["wearable"])
    digital_trace = []

    for layer in analysis.get("layers", []):
        latency_factor, energy_factor = _factor_for_layer(layer, baseline)
        compute_energy = float(layer.get("energy_uj", 0))
        memory_energy = float(layer.get("memory_energy_uj", 0))
        base_latency = float(layer.get("latency_ms", 0))
        digital_trace.append(
            {
                "layer_id": layer["id"],
                "operator": layer["operator"],
                "baseline_placement": "digital",
                "source_placement": layer["placement"],
                "latency_ms": round(base_latency * latency_factor, 3),
                "energy_uj": round((compute_energy + memory_energy) * energy_factor, 3),
                "note": "Digital baseline keeps values digital and avoids ADC/DAC crossings, but matrix-heavy work is less energy efficient in this estimate.",
            }
        )

    layer_latency = sum(item["latency_ms"] for item in digital_trace)
    layer_energy = sum(item["energy_uj"] for item in digital_trace)
    host_latency = baseline["host_overhead_ms"] + (0.01 * len(digital_trace))
    host_energy = baseline["host_overhead_uj"] + (0.05 * len(digital_trace))
    idle_energy = layer_energy * baseline["idle_energy_factor"]

    digital_latency = round(layer_latency + host_latency, 3)
    digital_energy = round(layer_energy + host_energy + idle_energy, 3)
    analog_latency = float(runtime_profile.get("summary", {}).get("latency_ms", 0))
    analog_energy = float(runtime_profile.get("summary", {}).get("energy_uj", 0))
    speedup = round(_safe_ratio(digital_latency, analog_latency), 2)
    energy_ratio = round(_safe_ratio(digital_energy, analog_energy), 2)
    energy_reduction_percent = round(max(0.0, (1 - _safe_ratio(analog_energy, digital_energy)) * 100), 1)
    latency_reduction_percent = round(max(0.0, (1 - _safe_ratio(analog_latency, digital_latency)) * 100), 1)

    if energy_ratio >= 2 and speedup >= 1:
        interpretation = "The analog path looks promising in this estimate, but it still needs measured accuracy and hardware energy."
    elif energy_ratio > 1:
        interpretation = "The analog path may save energy, but latency, accuracy, or integration risk still needs review."
    else:
        interpretation = "This estimate does not show a clear energy win after full-system costs are counted."

    return {
        "result_type": "digital_baseline_comparison",
        "provenance": "estimated",
        "confidence": "low",
        "baseline": {
            "target_profile": target_profile,
            "label": baseline["label"],
            "status": "not measured",
        },
        "summary": {
            "analog_latency_ms": analog_latency,
            "digital_latency_ms": digital_latency,
            "latency_speedup_x": speedup,
            "latency_reduction_percent": latency_reduction_percent,
            "analog_energy_uj": analog_energy,
            "digital_energy_uj": digital_energy,
            "energy_efficiency_x": energy_ratio,
            "energy_reduction_percent": energy_reduction_percent,
            "interpretation": interpretation,
        },
        "counted": [
            "layer compute estimate",
            "memory movement estimate",
            "analog ADC/DAC conversion from runtime profile",
            "host/runtime overhead estimate",
            "idle energy estimate",
        ],
        "excluded": [
            "real board power measurement",
            "thermal throttling measurement",
            "compiler scheduling effects",
            "batching effects",
            "accuracy measured on a task dataset",
        ],
        "trace": digital_trace,
        "warnings": [
            "Do not compare this estimate to a vendor TOPS/W headline.",
            "Use measured energy per completed inference before making a hardware performance claim.",
            "Keep the same accuracy and latency target when comparing analog and digital results.",
        ],
    }
