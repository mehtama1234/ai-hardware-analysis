CALIBRATION_DRIFT_SCHEMA_VERSION = "calibration-drift-readiness-v0.1"


def _source_status(measurement_evidence, source_id):
    for source in (measurement_evidence or {}).get("required_sources", []):
        if source.get("id") == source_id:
            return source.get("status", "missing")
    return "missing"


def _has_imported(measurement_evidence, source_id):
    return _source_status(measurement_evidence, source_id) == "imported artifact"


def _risk_level(calibration, target_profile, measurement_evidence, lab_profile=None):
    provenance = calibration.get("provenance", "unknown")
    confidence = calibration.get("confidence", "low")
    analog_error = _has_imported(measurement_evidence, "analog_error_simulation")
    power_thermal = _has_imported(measurement_evidence, "power_thermal")
    if provenance == "estimated":
        return "high"
    if target_profile == "robotics" and confidence != "high":
        return "high"
    if not analog_error or not power_thermal:
        return "medium"
    return "medium" if confidence == "medium" else "low"


def _readiness(calibration, target_profile, measurement_evidence):
    provenance = calibration.get("provenance", "unknown")
    analog_error = _has_imported(measurement_evidence, "analog_error_simulation")
    power_thermal = _has_imported(measurement_evidence, "power_thermal")
    if provenance == "estimated":
        return "blocked_for_measured_claims"
    if not analog_error:
        return "needs_analog_error_sweep"
    if not power_thermal:
        return "needs_power_thermal_sweep"
    if target_profile == "robotics":
        return "needs_tail_condition_sweep"
    return "prototype_review_only"


def _claim_boundary(readiness):
    if readiness == "blocked_for_measured_claims":
        return "analysis only: calibration is estimated, so measured hardware, safety, and production drift claims are blocked"
    if readiness == "needs_analog_error_sweep":
        return "prototype calibration only: analog error evidence across temperature and voltage is still missing"
    if readiness == "needs_power_thermal_sweep":
        return "prototype calibration only: thermal behavior and power evidence under operating conditions are still missing"
    if readiness == "needs_tail_condition_sweep":
        return "prototype calibration only: robotics-style tail conditions, jitter, drift, and recovery still need wider sweeps"
    return "prototype review only: production readiness still needs long-term drift, yield, repeatability, and customer integration evidence"


def build_calibration_drift_readiness(package_report, analysis, measurement_evidence=None, lab_profile=None):
    summary = package_report.get("summary", {})
    target_profile = summary.get("target_profile", "wearable")
    calibration = analysis.get("calibration", {})
    lab = ((lab_profile or {}).get("profile") or {})
    lab_environment = lab.get("environment", {})
    readiness = _readiness(calibration, target_profile, measurement_evidence)
    risk = _risk_level(calibration, target_profile, measurement_evidence, lab_profile=lab_profile)
    analog_error_status = _source_status(measurement_evidence, "analog_error_simulation")
    power_thermal_status = _source_status(measurement_evidence, "power_thermal")
    board_status = _source_status(measurement_evidence, "board_runtime")
    return {
        "result_type": "calibration_drift_readiness",
        "schema_version": CALIBRATION_DRIFT_SCHEMA_VERSION,
        "provenance": "derived from calibration profile, measurement evidence state, target profile, and simulated lab assumptions",
        "confidence": "low",
        "package_id": package_report.get("package_id"),
        "target_profile": target_profile,
        "calibration_profile": calibration.get("profile_id", summary.get("calibration_profile")),
        "readiness": readiness,
        "risk": risk,
        "summary": {
            "plain_reading": (
                "Analog calibration is part of reliability. The package must show behavior across temperature, voltage, drift, aging, "
                "and recalibration before it supports measured safety or production claims."
            ),
            "claim_boundary": _claim_boundary(readiness),
            "profile_status": calibration.get("status", "unknown"),
            "profile_provenance": calibration.get("provenance", "unknown"),
            "profile_confidence": calibration.get("confidence", "low"),
            "temperature_range": calibration.get("temperature", "unknown"),
            "voltage_range": calibration.get("voltage", "unknown"),
            "weak_rows": calibration.get("weak_rows", "unknown"),
            "accuracy_impact": calibration.get("accuracy_impact", "unknown"),
            "lab_temperature_c": lab_environment.get("temperature_c", "not attached"),
            "lab_voltage_v": lab_environment.get("voltage_v", "not attached"),
            "analog_error_status": analog_error_status,
            "power_thermal_status": power_thermal_status,
            "board_runtime_status": board_status,
        },
        "gates": [
            {
                "name": "calibration profile",
                "status": "estimated" if calibration.get("provenance") == "estimated" else "prototype profile",
                "evidence": calibration.get("notes", "No calibration notes attached."),
                "required_next": "Attach board-specific calibration with versioned correction factors before measured claims.",
            },
            {
                "name": "temperature and voltage sweep",
                "status": analog_error_status,
                "evidence": "Analog error simulation source status.",
                "required_next": "Run analog error sweep across the target temperature and voltage range.",
            },
            {
                "name": "thermal behavior",
                "status": power_thermal_status,
                "evidence": "Power and thermal source status.",
                "required_next": "Attach power and thermal traces under the real duty cycle.",
            },
            {
                "name": "board runtime stability",
                "status": board_status,
                "evidence": "Board runtime source status.",
                "required_next": "Attach board traces with fallback events and runtime version.",
            },
            {
                "name": "long-term drift and aging",
                "status": "missing measured evidence",
                "evidence": "No aging, repeated calibration, or long-duration drift artifact exists in this prototype.",
                "required_next": "Measure accuracy and calibration stability after aging, repeated operation, and recalibration cycles.",
            },
            {
                "name": "failure behavior",
                "status": "missing workflow evidence",
                "evidence": "No artifact describes what happens when calibration fails or moves out of range.",
                "required_next": "Define fallback, disable, alert, or safe-mode behavior for failed calibration.",
            },
        ],
        "hard_parts": [
            "Analog values can shift with temperature, voltage, process variation, noise, aging, and calibration state.",
            "A profile that works for one board or range does not prove every chip or deployment condition.",
            "Physical AI systems need failure behavior when calibration goes out of range.",
            "Drift evidence must be tied to the task metric, not only circuit-level measurements.",
        ],
        "evidence_needed": [
            "analog error sweep across target temperature and voltage",
            "board runtime trace across operating conditions",
            "power and thermal traces under realistic duty cycle",
            "accuracy before and after recalibration",
            "long-duration drift or aging test",
            "weak-cell or weak-row handling evidence",
            "safe fallback behavior when calibration fails",
        ],
        "what_not_to_claim": [
            "Do not claim production readiness from one calibration profile.",
            "Do not claim safety readiness until drift, recalibration, and failure behavior are tested under target conditions.",
            "Do not treat analog error simulation alone as measured board behavior.",
            "Do not hide temperature, voltage, weak-row, aging, or recalibration limits.",
        ],
    }
