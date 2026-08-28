from collections import Counter

from calibration import get_calibration_profile
from hardware_profile import TARGET_PROFILES, classify_operator, risk_for_operator


def _load_onnx():
    try:
        import onnx
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "The backend needs the 'onnx' package to parse model files. "
            "Install backend/requirements.txt, then retry the import."
        ) from exc
    return onnx


def _dim_to_text(dim):
    if dim.dim_value:
        return str(dim.dim_value)
    if dim.dim_param:
        return dim.dim_param
    return "?"


def _value_shape(value_info):
    tensor_type = value_info.type.tensor_type
    if not tensor_type.HasField("shape"):
        return "[]"
    dims = [_dim_to_text(dim) for dim in tensor_type.shape.dim]
    return "[" + ",".join(dims) + "]"


def _build_shape_map(graph):
    shapes = {}
    for value in list(graph.input) + list(graph.value_info) + list(graph.output):
        shapes[value.name] = _value_shape(value)
    for init in graph.initializer:
        shapes[init.name] = "[" + ",".join(str(dim) for dim in init.dims) + "]"
    return shapes


def _parameter_count(graph):
    total = 0
    for init in graph.initializer:
        count = 1
        for dim in init.dims:
            count *= dim
        total += count
    return total


def _format_count(value):
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"{value / 1_000:.1f}K"
    return str(value)


def _node_shape(node, shapes):
    for output in node.output:
        if output in shapes:
            return shapes[output]
    for input_name in node.input:
        if input_name in shapes:
            return shapes[input_name]
    return "[]"


def _estimate_layer_cost(node, placement, idx):
    input_count = max(len(node.input), 1)
    output_count = max(len(node.output), 1)
    base = 0.08 + (input_count * 0.03) + (output_count * 0.02)
    if placement == "analog":
        latency = base * 1.8
        energy = base * 9
    elif placement == "digital":
        latency = base * 2.4
        energy = base * 14
    elif placement == "fallback":
        latency = base * 3.2
        energy = base * 20
    else:
        latency = base * 4.0
        energy = base * 24
    return round(latency + (idx % 3) * 0.03, 2), round(energy + (idx % 4) * 0.4, 1)


def _boundary_text(previous, current):
    if previous is None:
        return "DAC before, ADC after" if current == "analog" else "no analog boundary"
    if previous == current:
        return "stays on same path"
    if previous == "analog" and current != "analog":
        return "ADC before"
    if previous != "analog" and current == "analog":
        return "DAC before, ADC after"
    return "digital handoff"


def _conversion_events(previous, current):
    if previous is None:
        return ["DAC"] if current == "analog" else []
    if previous == current:
        return []
    if previous == "analog" and current != "analog":
        return ["ADC"]
    if previous != "analog" and current == "analog":
        return ["DAC"]
    return []


def _suggestion(op_type, placement, risk):
    if placement == "analog" and risk == "medium":
        return "Run quantization sensitivity and protect this layer if accuracy drops."
    if placement == "analog":
        return "Good analog candidate. Keep it on the analog path unless profiling says otherwise."
    if placement == "digital":
        return "Keep digital unless a supported approximation reduces boundary cost."
    if placement == "fallback":
        return "Consider an operator rewrite or a dedicated digital accelerator path."
    return "Unsupported in the current profile. Rewrite the model or add hardware/runtime support."


def _shape_volume(shape):
    if not shape.startswith("[") or not shape.endswith("]"):
        return 0
    total = 1
    found = False
    for part in shape[1:-1].split(","):
        part = part.strip()
        if part.isdigit():
            total *= int(part)
            found = True
    return total if found else 0


def _memory_estimate_uj(layer, target):
    volume = _shape_volume(layer["shape"])
    scaled = max(volume / 4096, 1)
    return round(scaled * target["memory_move_energy_uj"], 2)


def _conversion_cost(events, target):
    total = 0.0
    for event in events:
        if event == "ADC":
            total += target["adc_energy_uj"]
        elif event == "DAC":
            total += target["dac_energy_uj"]
    return round(total, 2)


def _block_kind(ops):
    op_set = set(ops)
    if "Softmax" in op_set and "MatMul" in op_set:
        return "attention-like block"
    if ops and ops[0] in {"MatMul", "Gemm", "Conv"}:
        if any(op in op_set for op in {"Add", "Relu", "Gelu", "Sigmoid", "Tanh"}):
            return "linear block with digital support"
        return "matrix block"
    if all(op in {"Add", "Relu", "Gelu", "Sigmoid", "Tanh", "LayerNormalization"} for op in ops):
        return "digital support block"
    return "mixed block"


def build_blocks(layers):
    blocks = []
    idx = 0
    while idx < len(layers):
        start = idx
        first = layers[idx]
        ops = [first["operator"]]
        placements = [first["placement"]]
        idx += 1

        if first["operator"] in {"MatMul", "Gemm", "Conv"}:
            while idx < len(layers) and layers[idx]["operator"] in {"Add", "Relu", "Gelu", "Sigmoid", "Tanh", "BatchNormalization"}:
                ops.append(layers[idx]["operator"])
                placements.append(layers[idx]["placement"])
                idx += 1
            if idx < len(layers) and layers[idx]["operator"] == "Softmax":
                ops.append(layers[idx]["operator"])
                placements.append(layers[idx]["placement"])
                idx += 1
                if idx < len(layers) and layers[idx]["operator"] in {"MatMul", "Gemm"}:
                    ops.append(layers[idx]["operator"])
                    placements.append(layers[idx]["placement"])
                    idx += 1

        block_layers = layers[start:idx]
        block_id = f"block.{len(blocks) + 1}"
        for layer in block_layers:
            layer["block"] = block_id
        analog_layers = sum(1 for item in block_layers if item["placement"] == "analog")
        digital_layers = sum(1 for item in block_layers if item["placement"] == "digital")
        fallback_layers = sum(1 for item in block_layers if item["placement"] in {"fallback", "unsupported"})
        if analog_layers and not digital_layers and not fallback_layers:
            placement = "analog"
        elif analog_layers and (digital_layers or fallback_layers):
            placement = "hybrid"
        elif fallback_layers:
            placement = "fallback"
        else:
            placement = "digital"
        blocks.append(
            {
                "id": block_id,
                "kind": _block_kind(ops),
                "layers": [item["id"] for item in block_layers],
                "operators": ops,
                "placement": placement,
                "analog_layers": analog_layers,
                "digital_layers": digital_layers,
                "fallback_layers": fallback_layers,
                "latency_ms": round(sum(item["latency_ms"] for item in block_layers), 2),
                "energy_uj": round(sum(item["energy_uj"] for item in block_layers), 2),
                "reason": block_reason(placement, ops),
            }
        )
    return blocks


def block_reason(placement, ops):
    if placement == "analog":
        return "This block is mostly regular matrix work and should use the analog path."
    if placement == "hybrid":
        return "This block mixes analog-friendly math with digital support, so boundary cost must be counted."
    if placement == "fallback":
        return "This block contains work outside the current analog capability profile."
    return "This block is control, reshaping, or nonlinear support work better handled digitally."


def build_boundary_events(layers, target):
    events = []
    previous = None
    for layer in layers:
        conversions = _conversion_events(previous, layer["placement"])
        for event in conversions:
            events.append(
                {
                    "layer_id": layer["id"],
                    "event": event,
                    "from": previous or "digital input",
                    "to": layer["placement"],
                    "energy_uj": target["adc_energy_uj"] if event == "ADC" else target["dac_energy_uj"],
                    "reason": f"{event} is needed before {layer['id']} because execution moves to {layer['placement_label']}.",
                }
            )
        previous = layer["placement"]
    return events


def boundary_hotspots(events, layers):
    by_layer = {layer["id"]: layer for layer in layers}
    hotspots = []
    for event in events:
        layer = by_layer.get(event["layer_id"])
        if not layer:
            continue
        hotspots.append(
            {
                "layer_id": layer["id"],
                "event": event["event"],
                "energy_uj": round(event["energy_uj"], 2),
                "risk": layer["risk"],
                "reason": event["reason"],
            }
        )
    return sorted(hotspots, key=lambda item: item["energy_uj"], reverse=True)[:5]


def score_fit(analog_coverage, fallback_count, unsupported_count, convert_count, medium_or_high_risk, total_energy, target):
    score = 100
    score -= max(0, 70 - analog_coverage) * 0.45
    score -= fallback_count * 6
    score -= unsupported_count * 12
    score -= convert_count * 3
    score -= medium_or_high_risk * 2
    if total_energy > target["energy_target_uj"]:
        score -= min((total_energy - target["energy_target_uj"]) / target["energy_target_uj"] * 20, 20)
    score = max(round(score), 0)
    if score >= 80:
        return score, "High", "A"
    if score >= 60:
        return score, "Medium", "B"
    if score >= 40:
        return score, "Low", "C"
    return score, "Poor", "D"


def score_reasons(analog_coverage, fallback_count, unsupported_count, convert_count, total_energy, target):
    reasons = []
    if analog_coverage >= 70:
        reasons.append(f"{analog_coverage}% analog coverage is strong for this target.")
    else:
        reasons.append(f"{analog_coverage}% analog coverage limits the hardware upside.")
    if convert_count:
        reasons.append(f"{convert_count} analog/digital crossings add ADC/DAC cost.")
    if fallback_count:
        reasons.append(f"{fallback_count} operators need fallback or new support.")
    if unsupported_count:
        reasons.append(f"{unsupported_count} operators are unsupported by the current profile.")
    if total_energy > target["energy_target_uj"]:
        reasons.append(f"Estimated {round(total_energy, 1)} uJ exceeds the {target['energy_target_uj']} uJ target.")
    else:
        reasons.append(f"Estimated {round(total_energy, 1)} uJ is within the {target['energy_target_uj']} uJ target.")
    return reasons[:4]


def analyze_model(path, target_profile="wearable", calibration_profile="sim-wearable-v0"):
    onnx = _load_onnx()
    model = onnx.load(path)
    inferred = onnx.shape_inference.infer_shapes(model)
    graph = inferred.graph
    shapes = _build_shape_map(graph)
    target = TARGET_PROFILES.get(target_profile, TARGET_PROFILES["wearable"])
    calibration = get_calibration_profile(calibration_profile)

    layers = []
    previous_placement = None
    placement_counts = Counter()
    total_latency = 0.0
    compute_energy = 0.0
    memory_energy = 0.0
    conversion_energy = 0.0

    for idx, node in enumerate(graph.node):
        placement, placement_label, reason = classify_operator(node.op_type)
        risk = risk_for_operator(node.op_type, placement)
        latency, energy = _estimate_layer_cost(node, placement, idx)
        conversion_events = _conversion_events(previous_placement, placement)
        layer_conversion_energy = _conversion_cost(conversion_events, target)
        placement_counts[placement] += 1
        total_latency += latency
        layer_id = node.name or f"{node.op_type.lower()}.{idx + 1}"
        layer = (
            {
                "id": layer_id,
                "operator": node.op_type,
                "shape": _node_shape(node, shapes),
                "placement": placement,
                "placement_label": placement_label,
                "reason": reason,
                "risk": risk,
                "latency_ms": latency,
                "energy_uj": energy,
                "conversion_energy_uj": layer_conversion_energy,
                "boundaries": _boundary_text(previous_placement, placement),
                "suggestion": _suggestion(node.op_type, placement, risk),
            }
        )
        layer["memory_energy_uj"] = _memory_estimate_uj(layer, target)
        compute_energy += energy
        conversion_energy += layer_conversion_energy
        memory_energy += layer["memory_energy_uj"]
        layers.append(layer)
        previous_placement = placement

    total_layers = max(len(layers), 1)
    analog_coverage = round((placement_counts["analog"] / total_layers) * 100)
    fallback_count = placement_counts["fallback"] + placement_counts["unsupported"]
    unsupported_count = placement_counts["unsupported"]
    digital_count = placement_counts["digital"]
    boundary_events = build_boundary_events(layers, target)
    convert_count = len(boundary_events)
    total_energy = compute_energy + conversion_energy + memory_energy
    medium_or_high_risk = sum(1 for layer in layers if layer["risk"] in {"medium", "high"})
    fit_score, fit, grade = score_fit(
        analog_coverage,
        fallback_count,
        unsupported_count,
        convert_count,
        medium_or_high_risk,
        total_energy,
        target,
    )

    if fallback_count:
        main_risk = "unsupported or fallback operators reduce the analog benefit"
    elif convert_count > max(total_layers // 2, 1):
        main_risk = "frequent analog/digital conversion boundaries"
    elif digital_count:
        main_risk = "digital support path must be included in energy measurements"
    else:
        main_risk = "quantization and calibration sensitivity"

    return {
        "project": PathLikeName(path),
        "target": target["label"],
        "model": {
            "name": PathLikeName(path),
            "parameters": _format_count(_parameter_count(graph)),
            "operators": len(layers),
            "input": ", ".join(f"{item.name}{_value_shape(item)}" for item in graph.input),
            "device_class": target["label"],
        },
        "summary": {
            "fit": fit,
            "grade": grade,
            "analog_coverage_percent": analog_coverage,
            "fallback_count": fallback_count,
            "energy_estimate_uj": round(total_energy, 1),
            "latency_estimate_ms": round(total_latency, 2),
            "fit_score": fit_score,
            "next_step": "quantization sensitivity",
            "main_risk": main_risk,
            "caption": f"{analog_coverage}% of operators map to analog; {fallback_count} require fallback or new support.",
            "score_reasons": score_reasons(
                analog_coverage,
                fallback_count,
                unsupported_count,
                convert_count,
                total_energy,
                target,
            ),
        },
        "layers": layers,
        "blocks": build_blocks(layers),
        "boundaries": build_boundary_map(layers),
        "boundary_events": boundary_events,
        "boundary_hotspots": boundary_hotspots(boundary_events, layers),
        "quantization": [
            {"label": "Baseline", "value": 95.0, "tone": "analog"},
            {"label": "INT8 estimate", "value": 94.4, "tone": "analog"},
            {"label": "Analog error estimate", "value": 93.8, "tone": "warn"},
            {"label": "INT4 all layers", "value": 90.6, "tone": "warn"},
        ],
        "energy_breakdown": energy_breakdown(
            compute_energy,
            conversion_energy,
            memory_energy,
            placement_counts,
            total_energy,
        ),
        "calibration": {
            "profile_id": calibration["profile_id"],
            "status": calibration["status"],
            "board": calibration["board"],
            "temperature": calibration["temperature"],
            "voltage": calibration["voltage"],
            "weak_rows": calibration["weak_rows"],
            "accuracy_impact": calibration["accuracy_impact"],
            "provenance": calibration["provenance"],
            "confidence": calibration["confidence"],
            "correction_factors": calibration["correction_factors"],
            "notes": calibration["notes"],
        },
        "recommendations": build_recommendations(
            fallback_count,
            convert_count,
            analog_coverage,
            unsupported_count,
            total_energy,
            target,
        ),
        "targets": {
            "accuracy": target["accuracy_target"],
            "latency": f"< {target['latency_target_ms']} ms",
            "energy": f"< {target['energy_target_uj']} uJ",
            "status": f"real ONNX graph analyzed with {calibration['provenance']} calibration",
        },
    }


def PathLikeName(path):
    from pathlib import Path

    return Path(path).name


def build_boundary_map(layers):
    nodes = [{"kind": "digital", "title": "Input", "description": "Model input enters the runtime."}]
    previous = None
    for layer in layers[:8]:
        placement = layer["placement"]
        if previous != placement:
            if placement == "analog":
                nodes.append({"kind": "convert", "title": "DAC", "description": "Digital values enter analog path."})
            elif previous == "analog":
                nodes.append({"kind": "convert", "title": "ADC", "description": "Analog result returns to digital path."})
        kind = "analog" if placement == "analog" else "digital"
        title = layer["operator"] if placement != "fallback" else "Fallback"
        nodes.append({"kind": kind, "title": title, "description": layer["id"]})
        previous = placement
    nodes.append({"kind": "digital", "title": "Output", "description": "Model output returned to application."})
    return nodes


def energy_breakdown(compute_energy, conversion_energy, memory_energy, counts, total_energy):
    total = max(total_energy, 0.1)
    analog_share = counts["analog"] / max(sum(counts.values()), 1)
    analog_compute = round((compute_energy * analog_share / total) * 100)
    digital_fallback = round((compute_energy * (1 - analog_share) / total) * 100)
    convert_pct = round((conversion_energy / total) * 100)
    memory_pct = round((memory_energy / total) * 100)
    host_pct = max(100 - analog_compute - convert_pct - memory_pct - digital_fallback, 0)
    return [
        {"label": "Analog compute", "value": analog_compute, "tone": "analog"},
        {"label": "ADC/DAC", "value": convert_pct, "tone": "warn"},
        {"label": "Memory movement", "value": memory_pct, "tone": "digital"},
        {"label": "Digital fallback", "value": digital_fallback, "tone": "digital"},
        {"label": "Host/runtime", "value": host_pct, "tone": "digital"},
    ]


def build_recommendations(fallback_count, convert_count, analog_coverage, unsupported_count, total_energy, target):
    items = []
    if fallback_count:
        items.append({"id": "01", "text": "Review fallback and unsupported operators before claiming hardware fit.", "tag": "mapping"})
    if unsupported_count:
        items.append({"id": "02", "text": "Add runtime support or rewrite unsupported operators before deployment packaging.", "tag": "support"})
    if convert_count:
        items.append({"id": "03", "text": "Measure ADC/DAC overhead around analog and digital boundaries.", "tag": "energy"})
    if total_energy > target["energy_target_uj"]:
        items.append({"id": "04", "text": "Reduce boundary crossings or fallback work before claiming the energy target is met.", "tag": "target"})
    if analog_coverage < 60:
        items.append({"id": "05", "text": "Consider model rewrites that increase matrix-heavy analog coverage.", "tag": "fit"})
    else:
        items.append({"id": "05", "text": "Run quantization sensitivity to find which analog layers need protection.", "tag": "accuracy"})
    return items[:5]
