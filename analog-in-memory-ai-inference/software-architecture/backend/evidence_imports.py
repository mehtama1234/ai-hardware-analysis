from datetime import datetime, timezone
from uuid import uuid4

from measurement_evidence import REQUIRED_SOURCES


EVIDENCE_IMPORT_SCHEMA_VERSION = "evidence-import-v0.1"


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
