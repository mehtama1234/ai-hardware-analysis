WHATIF_SCHEMA_VERSION = "rewrite-what-if-v0.1"


def _round(value):
    return round(float(value), 3)


def _energy_hint_uj(suggestion):
    text = suggestion.get("expected_impact", {}).get("energy", "")
    marker = "about "
    if marker not in text:
        return None
    after = text.split(marker, 1)[1].split(" ", 1)[0]
    try:
        return float(after)
    except ValueError:
        return None


def _decision_after(coverage, fallback_count, baseline_decision):
    if fallback_count > 0:
        return "needs rewrite"
    if coverage < 45:
        return "needs rewrite"
    if baseline_decision in {"needs rewrite", "not a fit yet"}:
        return "needs measurement"
    return baseline_decision


def _apply_suggestion(state, suggestion):
    suggestion_id = suggestion.get("id", "")
    state["applied_suggestion_ids"].append(suggestion_id)
    state["notes"].append(f"Applied {suggestion_id}: {suggestion.get('rewrite_pattern', 'rewrite pattern unavailable')}")

    if suggestion_id.startswith("rewrite.boundary"):
        avoided = _energy_hint_uj(suggestion) or 0.6
        state["boundary_count"] = max(state["boundary_count"] - 1, 0)
        state["energy_uj"] = max(state["energy_uj"] - avoided, 0.1)
        state["latency_ms"] = max(state["latency_ms"] - 0.04, 0.1)
        state["estimated_changes"].append(f"Removed one estimated crossing and about {avoided} uJ of conversion energy.")
    elif suggestion_id.startswith("rewrite.coverage"):
        state["analog_coverage_percent"] = min(state["analog_coverage_percent"] + 15, 95)
        state["energy_uj"] *= 0.92
        state["latency_ms"] *= 0.95
        state["estimated_changes"].append("Raised analog coverage by estimating more matrix-heavy work stays on the analog path.")
    elif suggestion_id.startswith("rewrite.fallback") or suggestion_id.startswith("rewrite.unsupported"):
        state["fallback_count"] = max(state["fallback_count"] - 1, 0)
        state["analog_coverage_percent"] = min(state["analog_coverage_percent"] + 8, 95)
        state["energy_uj"] *= 0.9
        state["latency_ms"] *= 0.92
        state["estimated_changes"].append("Removed one fallback or unsupported item in the planning estimate.")
    elif suggestion_id.startswith("rewrite.digital-support"):
        state["boundary_count"] = max(state["boundary_count"] - 1, 0)
        state["energy_uj"] = max(state["energy_uj"] - 0.4, 0.1)
        state["latency_ms"] = max(state["latency_ms"] - 0.03, 0.1)
        state["estimated_changes"].append("Fused or rescheduled a digital support operator near the analog path.")
    elif suggestion_id.startswith("rewrite.protect-analog"):
        state["energy_uj"] *= 1.02
        state["latency_ms"] *= 1.01
        state["accuracy_risk"] = "lower after validation"
        state["estimated_changes"].append("Protected one analog layer, trading a small cost for lower numeric risk.")
    else:
        state["estimated_changes"].append("No numeric rule matched this suggestion; kept metrics unchanged.")


def build_rewrite_what_if(analysis, runtime_profile, decision_report, rewrite_report, suggestion_ids=None):
    suggestions = rewrite_report.get("suggestions", [])
    if suggestion_ids:
        wanted = {item.strip() for item in suggestion_ids.split(",") if item.strip()}
        selected = [item for item in suggestions if item.get("id") in wanted]
    else:
        selected = suggestions[:3]

    baseline = {
        "analog_coverage_percent": analysis.get("summary", {}).get("analog_coverage_percent", 0),
        "fallback_count": analysis.get("summary", {}).get("fallback_count", 0),
        "boundary_count": len(analysis.get("boundary_events", [])),
        "latency_ms": runtime_profile.get("summary", {}).get("latency_ms", 0),
        "energy_uj": runtime_profile.get("summary", {}).get("energy_uj", 0),
        "decision": decision_report.get("decision", "not available"),
    }
    state = {
        **baseline,
        "accuracy_risk": "unchanged",
        "applied_suggestion_ids": [],
        "estimated_changes": [],
        "notes": [],
    }
    for suggestion in selected:
        _apply_suggestion(state, suggestion)

    after_decision = _decision_after(
        state["analog_coverage_percent"],
        state["fallback_count"],
        baseline["decision"],
    )
    simulated = {
        "analog_coverage_percent": min(round(state["analog_coverage_percent"]), 100),
        "fallback_count": state["fallback_count"],
        "boundary_count": state["boundary_count"],
        "latency_ms": _round(state["latency_ms"]),
        "energy_uj": _round(state["energy_uj"]),
        "decision": after_decision,
        "accuracy_risk": state["accuracy_risk"],
    }
    return {
        "result_type": "rewrite_what_if",
        "schema_version": WHATIF_SCHEMA_VERSION,
        "provenance": "estimated from rewrite suggestions; no model file was changed",
        "confidence": "low",
        "selected_suggestion_ids": state["applied_suggestion_ids"],
        "baseline": baseline,
        "simulated": simulated,
        "deltas": {
            "analog_coverage_points": simulated["analog_coverage_percent"] - baseline["analog_coverage_percent"],
            "fallback_count": simulated["fallback_count"] - baseline["fallback_count"],
            "boundary_count": simulated["boundary_count"] - baseline["boundary_count"],
            "latency_ms": _round(simulated["latency_ms"] - baseline["latency_ms"]),
            "energy_uj": _round(simulated["energy_uj"] - baseline["energy_uj"]),
        },
        "estimated_changes": state["estimated_changes"],
        "notes": state["notes"],
        "warning": "This is a planning estimate only. It does not modify ONNX, run a compiler, measure accuracy, or measure board power.",
    }
