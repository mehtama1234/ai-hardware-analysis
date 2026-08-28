SYSTEM_BOUNDARY_SCHEMA_VERSION = "system-boundary-v0.1"


def _sum(trace, key, predicate=None):
    items = [item for item in trace if predicate is None or predicate(item)]
    return round(sum(float(item.get(key, 0) or 0) for item in items), 3)


def _percent(part, whole):
    if not whole:
        return 0
    return round((float(part) / float(whole)) * 100, 1)


def _top(trace, key, limit=4):
    return sorted(trace, key=lambda item: float(item.get(key, 0) or 0), reverse=True)[:limit]


def build_system_boundary_report(analysis, runtime_profile, package_report=None):
    trace = runtime_profile.get("trace", [])
    summary = runtime_profile.get("summary", {})
    total_energy = float(summary.get("energy_uj", 0) or 0)
    total_latency = float(summary.get("latency_ms", 0) or 0)
    analog_layers = [item for item in trace if item.get("placement") == "analog"]
    digital_layers = [item for item in trace if item.get("placement") == "digital"]
    fallback_layers = [item for item in trace if item.get("placement") in {"fallback", "unsupported"}]
    conversion_energy = _sum(trace, "conversion_energy_uj")
    memory_energy = _sum(trace, "memory_energy_uj")
    compute_energy = _sum(trace, "compute_energy_uj")
    host_energy = float(summary.get("host_overhead_uj", 0) or 0)
    idle_energy = float(summary.get("idle_energy_uj", 0) or 0)
    boundary_events = analysis.get("boundary_events", [])
    return {
        "result_type": "system_boundary_report",
        "schema_version": SYSTEM_BOUNDARY_SCHEMA_VERSION,
        "provenance": "derived from placement analysis and simulated runtime trace",
        "confidence": "low",
        "package_id": (package_report or {}).get("package_id"),
        "summary": {
            "analog_layers": len(analog_layers),
            "digital_layers": len(digital_layers),
            "fallback_layers": len(fallback_layers),
            "boundary_events": len(boundary_events),
            "total_latency_ms": round(total_latency, 3),
            "total_energy_uj": round(total_energy, 3),
            "conversion_energy_uj": conversion_energy,
            "memory_energy_uj": memory_energy,
            "host_energy_uj": round(host_energy, 3),
            "idle_energy_uj": round(idle_energy, 3),
            "conversion_energy_percent": _percent(conversion_energy, total_energy),
            "memory_energy_percent": _percent(memory_energy, total_energy),
            "host_energy_percent": _percent(host_energy, total_energy),
            "plain_reading": "The analog core is one part of the system. The final result also includes digital operators, ADC/DAC crossings, memory traffic, host control, idle energy, and proof tooling.",
        },
        "boundary_costs": [
            {
                "name": "analog compute",
                "energy_uj": _sum(trace, "compute_energy_uj", lambda item: item.get("placement") == "analog"),
                "plain_meaning": "Matrix-heavy work that is mapped to the analog path.",
            },
            {
                "name": "digital support",
                "energy_uj": _sum(trace, "energy_uj", lambda item: item.get("placement") == "digital"),
                "plain_meaning": "Operators kept digital because control, exact math, or support logic is a better fit.",
            },
            {
                "name": "fallback path",
                "energy_uj": _sum(trace, "energy_uj", lambda item: item.get("placement") in {"fallback", "unsupported"}),
                "plain_meaning": "Work that needs host, runtime, or new operator support before a clean deployment.",
            },
            {
                "name": "ADC/DAC conversion",
                "energy_uj": conversion_energy,
                "plain_meaning": "Cost paid when data crosses between analog and digital domains.",
            },
            {
                "name": "memory movement",
                "energy_uj": memory_energy,
                "plain_meaning": "Cost of moving activations, weights, and intermediate data around the system.",
            },
            {
                "name": "host and idle",
                "energy_uj": round(host_energy + idle_energy, 3),
                "plain_meaning": "Control processor and waiting energy that still count in completed inference.",
            },
        ],
        "top_boundaries": [
            {
                "layer_id": item.get("layer_id"),
                "operator": item.get("operator"),
                "placement": item.get("placement"),
                "conversion_energy_uj": item.get("conversion_energy_uj"),
                "memory_energy_uj": item.get("memory_energy_uj"),
                "energy_uj": item.get("energy_uj"),
                "note": item.get("note"),
            }
            for item in _top(trace, "conversion_energy_uj")
            if float(item.get("conversion_energy_uj", 0) or 0) > 0
        ],
        "top_memory_movers": [
            {
                "layer_id": item.get("layer_id"),
                "operator": item.get("operator"),
                "placement": item.get("placement"),
                "memory_energy_uj": item.get("memory_energy_uj"),
                "energy_uj": item.get("energy_uj"),
            }
            for item in _top(trace, "memory_energy_uj")
        ],
        "boundary_questions": [
            "Which operators are mapped into the analog array, and which stay digital?",
            "How many times does data cross ADC/DAC boundaries during one completed inference?",
            "Are conversion, memory movement, host control, idle energy, and fallback paths included in the energy number?",
            "Which layers are precision-sensitive, and how are they protected?",
            "What changes across temperature, voltage, calibration state, and chip-to-chip variation?",
            "Can the same boundary choice be reproduced by the compiler and runtime for a customer model?",
        ],
        "do_not_claim": [
            "Do not say core efficiency alone proves product efficiency.",
            "Do not ignore ADC, DAC, SRAM or DRAM movement, host control, fallback operators, idle power, or thermal behavior.",
            "Do not call a boundary estimate measured hardware behavior until board traces and power evidence are attached.",
        ],
    }
