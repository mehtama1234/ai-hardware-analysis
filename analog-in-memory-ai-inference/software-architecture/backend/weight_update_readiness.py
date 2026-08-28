WEIGHT_UPDATE_READINESS_SCHEMA_VERSION = "weight-update-readiness-v0.1"


UPDATE_PATTERNS = {
    "audio_wake_word": {
        "pattern": "occasional",
        "reason": "Wake-word models are usually updated by release or customer configuration, not continuously on the device.",
    },
    "vision_classification": {
        "pattern": "occasional",
        "reason": "Vision classifiers may update with new classes or environments, but many deployments can run fixed release weights.",
    },
    "object_detection": {
        "pattern": "per-customer",
        "reason": "Detection models often need customer, site, or object-set tuning.",
    },
    "robotics_perception": {
        "pattern": "frequent",
        "reason": "Robotics and embodied systems may adapt to sensors, bodies, workspaces, and tasks.",
    },
    "industrial_anomaly": {
        "pattern": "per-device",
        "reason": "Industrial models may need tuning per machine, site, sensor, or operating condition.",
    },
    "health_wearable": {
        "pattern": "per-device",
        "reason": "Health and wearable signals can be user-dependent, so personalization or calibration updates may matter.",
    },
    "edge_llm": {
        "pattern": "frequent",
        "reason": "Language and VLA-adjacent deployments may use adapters, task updates, or frequent model refreshes.",
    },
}


PATTERN_RISK = {
    "static": "low",
    "occasional": "medium",
    "per-customer": "medium",
    "per-device": "high",
    "frequent": "high",
}


def _update_pattern(modality, target_profile, vla_readiness=None):
    base = UPDATE_PATTERNS.get(modality, {
        "pattern": "occasional",
        "reason": "No specific update pattern is known for this modality, so the report assumes occasional model refresh.",
    }).copy()
    if target_profile == "robotics" or (vla_readiness or {}).get("model_family") in {"transformer-like", "attention-like hybrid"}:
        if base["pattern"] in {"static", "occasional", "per-customer"}:
            base["pattern"] = "frequent"
            base["reason"] = "Robotics, transformer-like, or VLA-like systems can require adaptation across bodies, sensors, tasks, or environments."
    return base


def _claim_boundary(pattern, has_write_evidence):
    if has_write_evidence:
        return "update evidence attached: review write energy, latency, endurance, and recalibration before adaptive claims"
    if pattern in {"frequent", "per-device"}:
        return "fixed-weight inference only: adaptive Physical AI readiness is not proven"
    if pattern in {"per-customer", "occasional"}:
        return "fixed or offline-updated model only: on-chip update support is not measured"
    return "static-weight inference only"


def _readiness(pattern, has_write_evidence):
    if has_write_evidence and pattern in {"static", "occasional", "per-customer"}:
        return "review_required"
    if has_write_evidence:
        return "early_update_candidate"
    if pattern in {"frequent", "per-device"}:
        return "blocked_for_adaptive_claims"
    return "not_measured_for_updates"


def _risk(pattern, vla_readiness=None):
    risk = PATTERN_RISK.get(pattern, "medium")
    claim_level = (vla_readiness or {}).get("claim_level", "")
    if "vla" in claim_level or "transformer" in claim_level:
        return "high"
    return risk


def build_weight_update_readiness(package_report, vla_readiness=None, measurement_evidence=None, lab_profile=None):
    summary = package_report.get("summary", {})
    modality = summary.get("modality", "vision_classification")
    target_profile = summary.get("target_profile", "wearable")
    update = _update_pattern(modality, target_profile, vla_readiness=vla_readiness)
    pattern = update["pattern"]
    required_sources = (measurement_evidence or {}).get("required_sources", [])
    has_write_evidence = any(item.get("id") == "weight_update" and item.get("status") == "evidence attached" for item in required_sources)
    lab = ((lab_profile or {}).get("profile") or {})
    memory = lab.get("memory", {})
    analog_array = lab.get("analog_array", {})
    readiness = _readiness(pattern, has_write_evidence)
    risk = _risk(pattern, vla_readiness=vla_readiness)
    return {
        "result_type": "weight_update_readiness",
        "schema_version": WEIGHT_UPDATE_READINESS_SCHEMA_VERSION,
        "provenance": "derived from package modality, target profile, VLA readiness, measurement evidence state, and simulated lab assumptions",
        "confidence": "low",
        "package_id": package_report.get("package_id"),
        "target_profile": target_profile,
        "modality": modality,
        "assumed_update_pattern": pattern,
        "readiness": readiness,
        "risk": risk,
        "summary": {
            "plain_reading": (
                f"This package assumes a {pattern} update pattern. "
                "Inference efficiency does not prove update readiness; write latency, write energy, endurance, and recalibration still need evidence."
            ),
            "update_pattern_reason": update["reason"],
            "claim_boundary": _claim_boundary(pattern, has_write_evidence),
            "write_evidence_attached": has_write_evidence,
            "memory_assumption": memory.get("external_dram", "memory update path not described"),
            "weight_precision_bits": analog_array.get("weight_precision_bits", "unknown"),
        },
        "evidence_status": [
            {
                "name": "write latency",
                "status": "missing measured evidence",
                "why_it_matters": "Frequent adaptation is only practical if writing weights does not take too long.",
            },
            {
                "name": "write energy",
                "status": "missing measured evidence",
                "why_it_matters": "A low-energy inference chip can still be a poor adaptive fit if updates cost too much energy.",
            },
            {
                "name": "endurance",
                "status": "missing measured evidence",
                "why_it_matters": "Memory cells must survive the expected number of updates over the product life.",
            },
            {
                "name": "post-write calibration",
                "status": "missing measured evidence",
                "why_it_matters": "Analog weights may need calibration after programming before accuracy is trustworthy.",
            },
            {
                "name": "rollback",
                "status": "missing workflow evidence",
                "why_it_matters": "Adaptive systems need a way to recover if an update hurts accuracy or reliability.",
            },
        ],
        "hard_parts": [
            "A chip that is efficient for fixed weights is not automatically good for models that update in the field.",
            "Weight programming must count latency, energy, endurance, voltage requirements, calibration, and rollback.",
            "Adaptive robotics and VLA workloads are higher risk because the model may change with body, sensor, task, or environment.",
            "Offline model replacement is easier than frequent on-device learning or fine-tuning.",
        ],
        "evidence_needed": [
            "measured weight write latency",
            "measured weight write energy",
            "memory endurance over expected update count",
            "accuracy before and after repeated write and recalibration cycles",
            "rollback or safe-version workflow",
            "clear statement of whether updates happen on chip, off chip, or through small digital adapters",
        ],
        "what_not_to_claim": [
            "Do not claim adaptive Physical AI readiness from fixed-weight inference efficiency.",
            "Do not claim frequent on-chip updates until write latency, write energy, endurance, and recalibration are measured.",
            "Do not assume VLA or robotics adaptation is solved by the analog core alone.",
            "Do not hide whether updates require high voltage, long programming time, off-chip tools, or full recalibration.",
        ],
    }
