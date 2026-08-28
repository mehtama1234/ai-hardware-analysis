CONTROL_BOUNDARY_SCHEMA_VERSION = "control-boundary-v0.1"


PHYSICAL_CONTROL_DOMAINS = {
    "robotics_vla",
    "mobility_transportation",
    "precision_agriculture",
    "defense_aerospace",
}

SUPERVISORY_DOMAINS = {
    "industrial_ai_engineering",
    "smart_infrastructure",
}


def _source_status(measurement_evidence, source_id):
    for source in (measurement_evidence or {}).get("required_sources", []):
        if source.get("id") == source_id:
            return source.get("status", "missing")
    return "missing"


def _summary_value(report, key, default="unknown"):
    return ((report or {}).get("summary") or {}).get(key, default)


def _selected_domain(physical_ai_map, target_profile, modality):
    if physical_ai_map and physical_ai_map.get("selected_domain"):
        return physical_ai_map["selected_domain"]
    if target_profile == "robotics":
        return "robotics_vla"
    if modality in {"vision_object_detection", "vision_classification"}:
        return "smart_infrastructure"
    if modality == "audio_wake_word":
        return "ambient_home"
    return "sensory_hardware"


def _readiness(selected_domain, target_profile, modality, measurement_evidence):
    board_status = _source_status(measurement_evidence, "board_runtime")
    task_status = _source_status(measurement_evidence, "task_accuracy")
    if selected_domain in PHYSICAL_CONTROL_DOMAINS or target_profile == "robotics":
        if board_status != "imported artifact":
            return "control_boundary_required"
        return "needs_jitter_and_safety_evidence"
    if selected_domain in SUPERVISORY_DOMAINS:
        return "supervisory_boundary_required"
    if modality in {"vision_object_detection", "vision_classification"} and task_status != "imported artifact":
        return "needs_task_evidence_before_action_claims"
    return "low_control_risk"


def _risk(selected_domain, target_profile, readiness):
    if selected_domain in PHYSICAL_CONTROL_DOMAINS or target_profile == "robotics":
        return "high"
    if readiness in {"supervisory_boundary_required", "needs_task_evidence_before_action_claims"}:
        return "medium"
    return "low"


def _claim_boundary(readiness):
    if readiness == "control_boundary_required":
        return "inference-only claim: the chip may support perception or action scoring, but real-time control and safety handoff are not proven"
    if readiness == "needs_jitter_and_safety_evidence":
        return "prototype control-boundary review: board runtime exists, but worst-case jitter, timeout, fallback, and safety-controller behavior still need proof"
    if readiness == "supervisory_boundary_required":
        return "supervisory claim only: use the AI output to inform decisions, alerts, or planning, not to bypass equipment control limits"
    if readiness == "needs_task_evidence_before_action_claims":
        return "perception claim only: task accuracy and action handoff must be measured before claiming closed-loop behavior"
    return "low control-boundary risk for this profile, while production claims still need target-device evidence"


def _latency_target_ms(selected_domain, target_profile, modality):
    if selected_domain in {"robotics_vla", "mobility_transportation", "defense_aerospace"} or target_profile == "robotics":
        return "set by external real-time controller, often tighter than model average latency"
    if selected_domain == "precision_agriculture":
        return "set by implement speed, sensor rate, and actuator response"
    if modality == "audio_wake_word":
        return "set by always-on response budget and battery duty cycle"
    return "set by product workflow, sensor rate, and user-visible delay"


def build_control_boundary(
    package_report,
    physical_ai_map=None,
    runtime_profile=None,
    system_boundary=None,
    measurement_evidence=None,
):
    summary = package_report.get("summary", {})
    target_profile = summary.get("target_profile", "wearable")
    modality = summary.get("modality", "vision_classification")
    selected_domain = _selected_domain(physical_ai_map, target_profile, modality)
    readiness = _readiness(selected_domain, target_profile, modality, measurement_evidence)
    risk = _risk(selected_domain, target_profile, readiness)
    board_status = _source_status(measurement_evidence, "board_runtime")
    task_status = _source_status(measurement_evidence, "task_accuracy")
    power_status = _source_status(measurement_evidence, "power_thermal")
    latency_ms = _summary_value(runtime_profile, "latency_ms", "not profiled")
    boundary_events = _summary_value(system_boundary, "boundary_events", "unknown")
    fallback_layers = _summary_value(system_boundary, "fallback_layers", "unknown")
    analog_layers = _summary_value(system_boundary, "analog_layers", "unknown")
    digital_layers = _summary_value(system_boundary, "digital_layers", "unknown")

    return {
        "result_type": "control_boundary",
        "schema_version": CONTROL_BOUNDARY_SCHEMA_VERSION,
        "provenance": "derived from package target, Physical AI domain map, runtime profile, system boundary, and measurement evidence state",
        "confidence": "low",
        "package_id": package_report.get("package_id"),
        "target_profile": target_profile,
        "modality": modality,
        "selected_domain": selected_domain,
        "readiness": readiness,
        "risk": risk,
        "inference_role": "Run model math that turns sensor or state input into scores, classifications, embeddings, plans, or action proposals.",
        "deterministic_control_role": "Deterministic control owns actuator timing, motor commands, force limits, interlocks, and hard real-time behavior outside the analog inference core.",
        "safety_monitor_role": "Check neural outputs before they affect physical motion, enforce limits, handle timeouts, and move the device to a known safe state.",
        "host_runtime_role": "Move data, call the accelerator, schedule digital fallback, collect traces, and expose debugging and profiling signals.",
        "expected_handoff_signal": "A bounded digital result such as class scores, detected objects, state estimates, waypoints, grasp proposals, or action candidates.",
        "summary": {
            "plain_reading": (
                "Physical AI is not only model inference. The analog chip can help with the repeated AI math, but a separate real-time control "
                "and safety path must decide when and how physical movement is allowed."
            ),
            "claim_boundary": _claim_boundary(readiness),
            "latency_ms": latency_ms,
            "latency_target_ms": _latency_target_ms(selected_domain, target_profile, modality),
            "analog_layers": analog_layers,
            "digital_layers": digital_layers,
            "boundary_events": boundary_events,
            "fallback_layers": fallback_layers,
            "board_runtime_status": board_status,
            "task_accuracy_status": task_status,
            "power_thermal_status": power_status,
        },
        "handoff_layers": [
            {
                "name": "sensor and host input",
                "owner": "device host and sensor stack",
                "plain_role": "Collect camera, audio, tactile, inertial, or state data and present it in the format the model expects.",
                "evidence_status": "interface contract needed",
            },
            {
                "name": "analog inference core",
                "owner": "AI accelerator",
                "plain_role": "Run the energy-heavy matrix math for layers that tolerate the analog numeric behavior.",
                "evidence_status": board_status,
            },
            {
                "name": "digital companion path",
                "owner": "SoC digital logic or host runtime",
                "plain_role": "Handle unsupported operators, control logic, memory movement, conversion, and fallback layers.",
                "evidence_status": f"{digital_layers} digital layers, {fallback_layers} fallback layers",
            },
            {
                "name": "safety and deterministic controller",
                "owner": "real-time controller outside the inference core",
                "plain_role": "Accept, reject, clamp, or time out AI outputs before they can move hardware.",
                "evidence_status": "missing integration evidence",
            },
        ],
        "evidence_status": [
            {
                "name": "average inference latency",
                "status": "simulated profile" if board_status != "imported artifact" else "board evidence attached",
                "why_it_matters": "Average latency says how long a normal inference takes. It does not prove the worst case.",
            },
            {
                "name": "tail latency and jitter",
                "status": "missing measured evidence",
                "why_it_matters": "Physical systems care about late responses, timing spread, and missed deadlines.",
            },
            {
                "name": "controller handoff",
                "status": "missing integration evidence",
                "why_it_matters": "The product must show which controller receives AI output and how unsafe output is rejected.",
            },
            {
                "name": "safety fallback",
                "status": "missing workflow evidence",
                "why_it_matters": "The system needs a known behavior when inference is slow, uncertain, out of range, or unavailable.",
            },
            {
                "name": "task accuracy",
                "status": task_status,
                "why_it_matters": "A control claim needs model quality on the target task, not only circuit speed.",
            },
        ],
        "boundary_questions": [
            "What exactly leaves the analog core: scores, embeddings, waypoints, torques, or action tokens?",
            "Which controller owns the timing deadline after inference finishes?",
            "What is the worst allowed delay, not just the average model latency?",
            "What happens when the model is uncertain, late, overheated, or outside calibration range?",
            "Can the neural result move an actuator directly, or must a safety monitor approve it first?",
        ],
        "evidence_needed": [
            "board runtime trace with worst-case latency and jitter",
            "controller integration trace showing handoff timing",
            "timeout, fallback, and safe-state behavior",
            "task accuracy or success rate on the target body and environment",
            "thermal and power behavior during the control-loop duty cycle",
            "clear API contract for what the accelerator returns to the host or controller",
        ],
        "what_not_to_claim": [
            "Do not claim the AI accelerator replaces deterministic control.",
            "Do not claim robot, mobility, or actuator readiness from inference latency alone.",
            "Do not treat average latency as proof of bounded jitter.",
            "Do not let neural output bypass safety monitors, controller limits, or interlocks.",
            "Do not describe Physical AI readiness without naming the handoff between inference, control, and safety.",
        ],
    }
