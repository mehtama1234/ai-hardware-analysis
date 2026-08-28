from copy import deepcopy

from claim_readiness import build_claim_readiness
from connection_playbook import CONNECTION_REQUIREMENTS
from evidence_imports import build_import_record, build_validation_report


ADAPTER_EVIDENCE_TEMPLATES_SCHEMA_VERSION = "adapter-evidence-templates-v0.1"


TEMPLATES_BY_SOURCE = {
    "compiler_mapping": {
        "operator_placements": [
            {"layer_id": "dense1", "operator": "MatMul", "placement": "analog", "reason": "replace with compiler placement reason"}
        ],
        "tiling_plan": [{"layer_id": "dense1", "tile_shape": [16, 16], "array": "analog-array-0"}],
        "memory_plan": {"weights": "on-chip", "activations": "local-sram", "outputs": "digital-postprocess"},
        "unsupported_operators": [],
        "provenance": {"tool": "external-compiler", "version": "replace-me", "target_profile": "replace-me"},
    },
    "analog_error_simulation": {
        "error_model": {"name": "replace-with-simulator-model", "variation": "replace-me"},
        "temperature_range": {"min_c": 0, "max_c": 70},
        "voltage_range": {"min_v": 0.75, "max_v": 0.9},
        "accuracy_impact": {"estimated_drop": 0.004, "pass": True},
        "calibration_profile": "replace-me",
        "provenance": {"tool": "external-analog-simulator", "version": "replace-me"},
    },
    "board_runtime": {
        "board_id": "board-001",
        "runtime_version": "runtime-0.1",
        "latency_ms": 2.3,
        "trace": [{"layer_id": "dense1", "operator": "MatMul", "placement": "analog", "latency_ms": 0.7}],
        "fallback_events": [],
        "provenance": {"tool": "board-runtime-service", "run_id": "replace-me"},
    },
    "power_thermal": {
        "energy_uj": 18.9,
        "power_trace": [{"time_ms": 0, "power_mw": 7.8}, {"time_ms": 1, "power_mw": 8.4}],
        "temperature_trace": [{"time_ms": 0, "temperature_c": 31.2}, {"time_ms": 2, "temperature_c": 31.6}],
        "sampling_rate": "1 kHz",
        "measurement_setup": {
            "meter": "replace-me",
            "supply_voltage": "replace-me",
            "includes_host_overhead": True,
        },
        "provenance": {"tool": "power-meter-service", "run_id": "replace-me"},
    },
    "task_accuracy": {
        "dataset_id": "replace-me",
        "metric_name": "classification_accuracy",
        "baseline_metric": 0.97,
        "candidate_metric": 0.965,
        "tolerance": 0.01,
        "pass": True,
        "provenance": {"tool": "dataset-backed-task-runner", "dataset_version": "replace-me"},
    },
}


def _source_by_category(measurement_evidence):
    sources = {}
    for source in (measurement_evidence or {}).get("required_sources", []):
        sources.setdefault(source.get("adapter_category"), source)
    return sources


def _claim_by_id(claim_readiness):
    return {claim.get("id"): claim for claim in claim_readiness.get("lab_claims", [])}


def _template_claim_preview(source_id, payload, measurement_evidence, package_report, valid):
    before = build_claim_readiness(measurement_evidence or {}, package_report=package_report)
    if not valid or not source_id:
        return {
            "before_summary": before.get("summary", {}),
            "after_summary": None,
            "claims_affected": [],
            "plain_reading": "Claim impact is not projected until the template has a valid source contract.",
        }
    after_measurement = deepcopy(measurement_evidence or {})
    proposed = build_import_record(source_id, payload, package_id=(package_report or {}).get("package_id"))
    for source in after_measurement.get("required_sources", []):
        if source.get("id") == source_id:
            source["status"] = "imported artifact"
            source["confidence"] = "medium"
            source["imported_count"] = int(source.get("imported_count") or 0) + 1
            source["latest_import"] = proposed
            break
    after = build_claim_readiness(after_measurement, package_report=package_report)
    before_by_id = _claim_by_id(before)
    after_by_id = _claim_by_id(after)
    claims = []
    for claim_id, before_claim in before_by_id.items():
        if source_id not in before_claim.get("required_sources", []):
            continue
        after_claim = after_by_id.get(claim_id, before_claim)
        if before_claim.get("status") != after_claim.get("status"):
            impact = f"Template would move this claim from {before_claim.get('status')} to {after_claim.get('status')} if filled with real evidence."
        elif after_claim.get("missing_sources"):
            impact = f"Template helps this claim, but it still needs: {', '.join(after_claim.get('missing_sources', []))}."
        else:
            impact = "Template would keep the same claim status but become the latest evidence for this source."
        claims.append({
            "id": claim_id,
            "name": before_claim.get("name"),
            "before_status": before_claim.get("status"),
            "after_status": after_claim.get("status"),
            "before_missing": before_claim.get("missing_sources", []),
            "after_missing": after_claim.get("missing_sources", []),
            "after_quality_issues": after_claim.get("quality_issues", []),
            "plain_impact": impact,
        })
    return {
        "before_summary": before.get("summary", {}),
        "after_summary": after.get("summary", {}),
        "claims_affected": claims,
        "plain_reading": "This is a forecast from the template shape. It becomes real only after a filled artifact is validated and imported.",
    }


def build_adapter_evidence_templates(adapter_report, measurement_evidence, adapter_connection_kit=None, package_report=None):
    sources = _source_by_category(measurement_evidence or {})
    connection_by_adapter = {
        item.get("adapter_id"): item
        for item in (adapter_connection_kit or {}).get("adapters", [])
    }
    templates = []
    for adapter in (adapter_report or {}).get("adapters", []):
        if adapter.get("id") not in CONNECTION_REQUIREMENTS:
            continue
        source = sources.get(adapter.get("category"), {})
        source_id = source.get("id")
        payload = deepcopy(TEMPLATES_BY_SOURCE.get(source_id, {}))
        validation = build_validation_report(source_id, payload) if source_id else None
        valid = validation.get("valid") if validation else False
        templates.append({
            "adapter_id": adapter.get("id"),
            "name": adapter.get("name"),
            "source_id": source_id,
            "artifact_name": source.get("artifact_name", "normalized-evidence.json"),
            "minimum_fields": source.get("minimum_fields", []),
            "template_payload": payload,
            "template_valid": valid,
            "validation_errors": validation.get("errors", []) if validation else ["No source contract available."],
            "claim_preview": _template_claim_preview(source_id, payload, measurement_evidence, package_report, valid),
            "validate_command": connection_by_adapter.get(adapter.get("id"), {}).get("commands", {}).get("validate"),
            "import_command": connection_by_adapter.get(adapter.get("id"), {}).get("commands", {}).get("import"),
            "handoff_note": "External adapters should fill this template from raw tool output, keep raw logs for audit, then validate before import.",
        })
    return {
        "result_type": "adapter_evidence_templates",
        "schema_version": ADAPTER_EVIDENCE_TEMPLATES_SCHEMA_VERSION,
        "provenance": "derived from measurement evidence source contracts and backend validators",
        "confidence": "medium" if templates else "low",
        "package_id": (package_report or {}).get("package_id") or (measurement_evidence or {}).get("summary", {}).get("package_id"),
        "summary": {
            "total_templates": len(templates),
            "valid_templates": sum(1 for item in templates if item["template_valid"]),
            "plain_reading": "These are the normalized JSON shapes external tools should emit before validation and import.",
        },
        "templates": templates,
        "template_rule": "Templates are examples, not proof. A filled artifact must still include real provenance and pass backend validation.",
    }
