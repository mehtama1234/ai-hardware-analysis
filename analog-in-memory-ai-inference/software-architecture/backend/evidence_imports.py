from datetime import datetime, timezone
from uuid import uuid4

from measurement_evidence import REQUIRED_SOURCES


EVIDENCE_IMPORT_SCHEMA_VERSION = "evidence-import-v0.1"
MEASURED_EVIDENCE_READINESS_VERSION = "measured-evidence-readiness-v0.1"
TOOL_EVIDENCE_READINESS_VERSION = "tool-evidence-readiness-v0.1"


REQUIRED_BY_ID = {source["id"]: source for source in REQUIRED_SOURCES}


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _require_type(errors, payload, field, expected_type, label):
    if field in payload and not isinstance(payload[field], expected_type):
        errors.append(f"{field} must be {label}.")


def _require_number(errors, payload, field, minimum=None, maximum=None):
    if field not in payload:
        return
    value = payload[field]
    if not _is_number(value):
        errors.append(f"{field} must be a number.")
        return
    if minimum is not None and value < minimum:
        errors.append(f"{field} must be >= {minimum}.")
    if maximum is not None and value > maximum:
        errors.append(f"{field} must be <= {maximum}.")


def _validate_compiler_mapping(payload):
    errors = []
    _require_type(errors, payload, "operator_placements", list, "a list")
    _require_type(errors, payload, "tiling_plan", list, "a list")
    _require_type(errors, payload, "memory_plan", dict, "an object")
    _require_type(errors, payload, "unsupported_operators", list, "a list")
    _require_type(errors, payload, "provenance", dict, "an object")
    for index, item in enumerate(payload.get("operator_placements", []) if isinstance(payload.get("operator_placements"), list) else []):
        if not isinstance(item, dict):
            errors.append(f"operator_placements[{index}] must be an object.")
            continue
        for field in ["layer_id", "operator", "placement"]:
            if field not in item:
                errors.append(f"operator_placements[{index}] missing {field}.")
    return errors


def _validate_analog_error(payload):
    errors = []
    _require_type(errors, payload, "error_model", dict, "an object")
    _require_type(errors, payload, "temperature_range", (dict, str), "an object or string")
    _require_type(errors, payload, "voltage_range", (dict, str), "an object or string")
    _require_type(errors, payload, "accuracy_impact", dict, "an object")
    if isinstance(payload.get("accuracy_impact"), dict):
        impact = payload["accuracy_impact"]
        _require_number(errors, impact, "estimated_drop", minimum=0)
        if "pass" in impact and not isinstance(impact["pass"], bool):
            errors.append("accuracy_impact.pass must be a boolean when provided.")
    return errors


def _validate_board_runtime(payload):
    errors = []
    _require_number(errors, payload, "latency_ms", minimum=0)
    _require_type(errors, payload, "trace", list, "a list")
    _require_type(errors, payload, "fallback_events", list, "a list")
    _require_type(errors, payload, "provenance", dict, "an object")
    for index, item in enumerate(payload.get("trace", []) if isinstance(payload.get("trace"), list) else []):
        if not isinstance(item, dict):
            errors.append(f"trace[{index}] must be an object.")
            continue
        if "layer_id" not in item:
            errors.append(f"trace[{index}] missing layer_id.")
        if "latency_ms" in item and not _is_number(item["latency_ms"]):
            errors.append(f"trace[{index}].latency_ms must be a number.")
    return errors


def _validate_power_thermal(payload):
    errors = []
    _require_number(errors, payload, "energy_uj", minimum=0)
    _require_type(errors, payload, "power_trace", list, "a list")
    _require_type(errors, payload, "temperature_trace", list, "a list")
    _require_type(errors, payload, "measurement_setup", dict, "an object")
    for field, key in [("power_trace", "power_mw"), ("temperature_trace", "temperature_c")]:
        values = payload.get(field, []) if isinstance(payload.get(field), list) else []
        for index, item in enumerate(values):
            if not isinstance(item, dict):
                errors.append(f"{field}[{index}] must be an object.")
                continue
            if key in item and not _is_number(item[key]):
                errors.append(f"{field}[{index}].{key} must be a number.")
    setup = payload.get("measurement_setup")
    if isinstance(setup, dict) and "includes_host_overhead" in setup and not isinstance(setup["includes_host_overhead"], bool):
        errors.append("measurement_setup.includes_host_overhead must be a boolean when provided.")
    return errors


def _validate_physical_flow(payload):
    errors = []
    _require_type(errors, payload, "design_name", str, "a string")
    _require_type(errors, payload, "flow_name", str, "a string")
    _require_type(errors, payload, "flow_status", str, "a string")
    _require_type(errors, payload, "artifacts", dict, "an object")
    _require_type(errors, payload, "checks", dict, "an object")
    _require_type(errors, payload, "timing", dict, "an object")
    _require_type(errors, payload, "claim_boundary", dict, "an object")
    _require_type(errors, payload, "provenance", dict, "an object")
    if isinstance(payload.get("checks"), dict):
        for field in ["drc_violations", "lvs_errors", "antenna_violations"]:
            _require_number(errors, payload["checks"], field, minimum=0)
    if isinstance(payload.get("timing"), dict):
        for field in ["critical_path_ns", "suggested_clock_period_ns", "suggested_clock_frequency_mhz", "wns", "tns"]:
            _require_number(errors, payload["timing"], field)
    return errors


def _non_empty_string(value):
    return isinstance(value, str) and bool(value.strip())


def _has_numeric_samples(items, required_fields):
    if not isinstance(items, list) or not items:
        return False
    for item in items:
        if not isinstance(item, dict):
            return False
        for field in required_fields:
            if not _is_number(item.get(field)):
                return False
    return True


def measured_runtime_readiness(payload):
    issues = validate_imported_evidence("board_runtime", payload)
    if not isinstance(payload, dict):
        return issues
    provenance = payload.get("provenance") or {}
    required_strings = [
        "package_id",
        "workload_id",
        "board_id",
        "board_revision",
        "runtime_version",
        "runtime_trace_id",
        "start_timestamp",
        "end_timestamp",
    ]
    for field in required_strings:
        if not _non_empty_string(payload.get(field)):
            issues.append(f"{field} is required for measured board runtime.")
    if str(payload.get("board_id", "")).startswith("local-") or payload.get("board_id") == "local-rtl-simulation-not-board":
        issues.append("board_id must name a real board or instrumented runtime source, not a local simulation.")
    if provenance.get("not_measured_silicon") is True or provenance.get("tool") == "local-board-runtime-adapter":
        issues.append("provenance marks this runtime as local or not measured hardware.")
    if provenance.get("measurement_level") not in {"measured_board", "instrumented_runtime"}:
        issues.append("provenance.measurement_level must be measured_board or instrumented_runtime.")
    if not isinstance(payload.get("trace"), list) or not payload["trace"]:
        issues.append("trace must contain at least one measured runtime event.")
    if not _is_number(payload.get("p50_latency_ms")):
        issues.append("p50_latency_ms is required for measured board runtime.")
    if not _is_number(payload.get("p95_latency_ms")):
        issues.append("p95_latency_ms is required for measured board runtime.")
    if not isinstance(payload.get("repetition_count"), int) or payload.get("repetition_count", 0) < 2:
        issues.append("repetition_count must be an integer >= 2 for measured board runtime.")
    if payload.get("host_overhead_boundary") not in {"included", "excluded", "reported_separately"}:
        issues.append("host_overhead_boundary must be included, excluded, or reported_separately.")
    return issues


def measured_power_readiness(payload):
    issues = validate_imported_evidence("power_thermal", payload)
    if not isinstance(payload, dict):
        return issues
    setup = payload.get("measurement_setup") or {}
    provenance = payload.get("provenance") or {}
    required_strings = [
        "package_id",
        "workload_id",
        "board_id",
        "runtime_trace_id",
        "integration_start_timestamp",
        "integration_end_timestamp",
    ]
    for field in required_strings:
        if not _non_empty_string(payload.get(field)):
            issues.append(f"{field} is required for measured power and thermal evidence.")
    if not _non_empty_string(setup.get("meter")) or str(setup.get("meter")).lower() == "none":
        issues.append("measurement_setup.meter must name the meter or instrument source.")
    if not _non_empty_string(setup.get("measured_rail")):
        issues.append("measurement_setup.measured_rail is required.")
    if setup.get("not_measured_hardware") is True or provenance.get("tool") == "local-power-thermal-adapter":
        issues.append("payload marks power/thermal as local estimate or not measured hardware.")
    if provenance.get("measurement_level") not in {"measured_board_power", "instrumented_power"}:
        issues.append("provenance.measurement_level must be measured_board_power or instrumented_power.")
    if not _is_number(payload.get("average_power_mw")):
        issues.append("average_power_mw is required.")
    if not _is_number(payload.get("peak_power_mw")):
        issues.append("peak_power_mw is required.")
    if not _has_numeric_samples(payload.get("power_trace"), ["time_ms", "voltage_v", "current_a"]):
        issues.append("power_trace must contain numeric time_ms, voltage_v, and current_a samples.")
    if not _has_numeric_samples(payload.get("temperature_trace"), ["time_ms", "temperature_c"]):
        issues.append("temperature_trace must contain numeric time_ms and temperature_c samples.")
    if payload.get("host_overhead_boundary") not in {"included", "excluded", "reported_separately"}:
        issues.append("host_overhead_boundary must be included, excluded, or reported_separately.")
    return issues


def analog_simulator_readiness(payload):
    issues = validate_imported_evidence("analog_error_simulation", payload)
    if not isinstance(payload, dict):
        return issues
    provenance = payload.get("provenance") or {}
    error_model = payload.get("error_model") or {}
    impact = payload.get("accuracy_impact") or {}
    accepted_tools = {"aihwkit", "crosssim", "spice", "ngspice", "xyce", "aimc-calibrated-simulator"}
    tool_name = str(provenance.get("tool", "")).lower()
    if not any(name in tool_name for name in accepted_tools):
        issues.append("provenance.tool must name a real analog simulator or calibrated analog evidence source.")
    if provenance.get("not_measured_silicon") is not True and provenance.get("measurement_level") != "calibrated_silicon":
        issues.append("analog simulator evidence must either mark not_measured_silicon=true or carry calibrated_silicon provenance.")
    if not _non_empty_string(payload.get("calibration_profile")):
        issues.append("calibration_profile is required so simulator assumptions are visible.")
    if not isinstance(error_model, dict) or not _non_empty_string(error_model.get("name")):
        issues.append("error_model.name is required.")
    if not _is_number(error_model.get("adc_bits")):
        issues.append("error_model.adc_bits is required.")
    if not _is_number(error_model.get("dac_bits")):
        issues.append("error_model.dac_bits is required.")
    if "final_residual_relative" in error_model and not _is_number(error_model.get("final_residual_relative")):
        issues.append("error_model.final_residual_relative must be numeric when provided.")
    if "estimated_drop" not in impact or not _is_number(impact.get("estimated_drop")):
        issues.append("accuracy_impact.estimated_drop is required.")
    if impact.get("pass") is not True:
        issues.append("accuracy_impact.pass must be true before analog simulator evidence can support a positive simulator claim.")
    temperature_range = payload.get("temperature_range")
    if temperature_range is None or temperature_range == "" or temperature_range == "not swept; local room-temperature educational model":
        issues.append("temperature_range must describe a real sweep or a named fixed-condition boundary.")
    voltage_range = payload.get("voltage_range")
    if voltage_range is None or voltage_range == "" or voltage_range == "not swept; row-voltage assumptions from local tile model":
        issues.append("voltage_range must describe a real sweep or a named fixed-condition boundary.")
    return issues


def build_measured_readiness_report(source_id, payload):
    if source_id == "board_runtime":
        issues = measured_runtime_readiness(payload)
        claim = "C2 measured latency"
    elif source_id == "power_thermal":
        issues = measured_power_readiness(payload)
        claim = "C3 measured energy"
    else:
        issues = [f"Measured-readiness checks are only defined for board_runtime and power_thermal, not {source_id}."]
        claim = None
    return {
        "result_type": "measured_evidence_readiness",
        "schema_version": MEASURED_EVIDENCE_READINESS_VERSION,
        "source_id": source_id,
        "claim": claim,
        "measured_ready": not issues,
        "issues": issues,
        "plain_reading": "This payload has the fields needed for a measured claim upgrade path." if not issues else "This payload can remain estimate or needs-review evidence, but it is not measured enough to upgrade the claim.",
    }


def build_tool_readiness_report(source_id, payload):
    if source_id == "analog_error_simulation":
        issues = analog_simulator_readiness(payload)
        claim = "C4 analog simulator evidence"
    else:
        issues = [f"Tool-readiness checks are only defined for analog_error_simulation, not {source_id}."]
        claim = None
    return {
        "result_type": "tool_evidence_readiness",
        "schema_version": TOOL_EVIDENCE_READINESS_VERSION,
        "source_id": source_id,
        "claim": claim,
        "tool_ready": not issues,
        "issues": issues,
        "plain_reading": "This payload has enough simulator detail to support a bounded analog-simulation claim." if not issues else "This payload can remain local evidence, but it is not detailed enough for a real analog-simulator claim.",
    }


def _validate_task_accuracy(payload):
    errors = []
    _require_number(errors, payload, "baseline_metric", minimum=0)
    _require_number(errors, payload, "candidate_metric", minimum=0)
    _require_number(errors, payload, "tolerance", minimum=0)
    if "pass" in payload and not isinstance(payload["pass"], bool):
        errors.append("pass must be a boolean.")
    return errors


SOURCE_VALIDATORS = {
    "compiler_mapping": _validate_compiler_mapping,
    "analog_error_simulation": _validate_analog_error,
    "board_runtime": _validate_board_runtime,
    "power_thermal": _validate_power_thermal,
    "task_accuracy": _validate_task_accuracy,
    "physical_flow": _validate_physical_flow,
}


def validate_imported_evidence(source_id, payload):
    if source_id not in REQUIRED_BY_ID:
        return [f"Unknown source_id: {source_id}"]
    if not isinstance(payload, dict):
        return ["Evidence payload must be a JSON object."]
    missing = [field for field in REQUIRED_BY_ID[source_id]["minimum_fields"] if field not in payload]
    errors = [f"Missing required field: {field}" for field in missing]
    if "provenance" in payload and not payload.get("provenance"):
        errors.append("provenance must not be empty when provided.")
    validator = SOURCE_VALIDATORS.get(source_id)
    if validator:
        errors.extend(validator(payload))
    return errors


def build_validation_report(source_id, payload):
    source = REQUIRED_BY_ID.get(source_id)
    errors = validate_imported_evidence(source_id, payload)
    minimum_fields = source.get("minimum_fields", []) if source else []
    present_fields = sorted(payload.keys()) if isinstance(payload, dict) else []
    missing_fields = [field for field in minimum_fields if field not in present_fields]
    return {
        "result_type": "evidence_validation",
        "schema_version": EVIDENCE_IMPORT_SCHEMA_VERSION,
        "source_id": source_id,
        "valid": not errors,
        "errors": errors,
        "artifact_name": source.get("artifact_name") if source else None,
        "required_for": source.get("required_for", []) if source else [],
        "required_fields": minimum_fields,
        "present_fields": present_fields,
        "missing_fields": missing_fields,
        "summary": {
            "status": "valid" if not errors else "invalid",
            "field_count": len(present_fields),
            "required_field_count": len(minimum_fields),
            "missing_field_count": len(missing_fields),
        },
    }


def build_import_record(source_id, payload, package_id=None, run_id=None):
    return {
        "result_type": "imported_evidence",
        "schema_version": EVIDENCE_IMPORT_SCHEMA_VERSION,
        "import_id": str(uuid4()),
        "source_id": source_id,
        "package_id": package_id,
        "run_id": run_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "artifact_name": REQUIRED_BY_ID[source_id]["artifact_name"],
        "required_for": REQUIRED_BY_ID[source_id]["required_for"],
        "payload": payload,
        "summary": {
            "field_count": len(payload),
            "required_field_count": len(REQUIRED_BY_ID[source_id]["minimum_fields"]),
            "status": "accepted",
        },
    }
