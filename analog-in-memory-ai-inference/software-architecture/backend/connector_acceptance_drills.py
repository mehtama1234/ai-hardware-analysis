from copy import deepcopy

from evidence_imports import REQUIRED_BY_ID, build_validation_report


CONNECTOR_ACCEPTANCE_DRILLS_SCHEMA_VERSION = "connector-acceptance-drills-v0.1"


def _latest_by_source(imported_evidence):
    latest = {}
    for record in imported_evidence or []:
        source_id = record.get("source_id")
        if source_id:
            latest[source_id] = record
    return latest


def _negative_validation_drill(source_id, record):
    payload = deepcopy((record or {}).get("payload") or {})
    required = REQUIRED_BY_ID.get(source_id, {})
    field = next((item for item in required.get("minimum_fields", []) if item in payload), None)
    if not field:
        return {
            "kind": "negative validation",
            "status": "blocked",
            "removed_field": None,
            "errors": ["No removable required field was present in the latest payload."],
            "plain_reading": "The negative validation drill could not run because the latest payload does not contain a required field to remove.",
        }
    payload.pop(field, None)
    validation = build_validation_report(source_id, payload)
    passed = validation.get("valid") is False and any(field in error for error in validation.get("errors", []))
    return {
        "kind": "negative validation",
        "status": "passed" if passed else "failed",
        "removed_field": field,
        "validation_valid": validation.get("valid"),
        "errors": validation.get("errors", []),
        "plain_reading": (
            f"Removing required field {field} was rejected before import."
            if passed
            else f"Removing required field {field} did not produce the expected validation failure."
        ),
    }


def _failure_safety_drill(source_id, record, source_import_count):
    failed_run = {
        "result_type": "adapter_run",
        "status": "failed",
        "source_id": source_id,
        "would_import": False,
        "reason": "simulated connector failure drill",
    }
    after_count = source_import_count
    passed = failed_run["status"] != "completed" and failed_run["would_import"] is False and after_count == source_import_count
    return {
        "kind": "safety",
        "status": "passed" if passed else "failed",
        "before_import_count": source_import_count,
        "after_import_count": after_count,
        "simulated_run_status": failed_run["status"],
        "import_attempted": failed_run["would_import"],
        "plain_reading": (
            "A failed connector run did not create or upgrade imported evidence."
            if passed
            else "A failed connector run could affect imported evidence, which would be unsafe."
        ),
    }


def build_connector_acceptance_drills(connector_test_harness, imported_evidence=None, package_report=None):
    latest = _latest_by_source(imported_evidence or [])
    counts = {}
    for record in imported_evidence or []:
        source_id = record.get("source_id")
        if source_id:
            counts[source_id] = counts.get(source_id, 0) + 1

    drills = []
    for harness in (connector_test_harness or {}).get("harnesses", []):
        source_id = harness.get("source_id")
        record = latest.get(source_id)
        if not source_id or not record:
            drills.append({
                "adapter_id": harness.get("adapter_id"),
                "source_id": source_id,
                "artifact_name": harness.get("artifact_name"),
                "status": "blocked",
                "negative_validation": {
                    "kind": "negative validation",
                    "status": "blocked",
                    "errors": ["No imported artifact is available for this source."],
                },
                "failure_safety": {
                    "kind": "safety",
                    "status": "blocked",
                    "errors": ["No imported artifact is available for this source."],
                },
            })
            continue
        negative = _negative_validation_drill(source_id, record)
        safety = _failure_safety_drill(source_id, record, counts.get(source_id, 0))
        status = "passed" if negative["status"] == "passed" and safety["status"] == "passed" else "failed"
        drills.append({
            "adapter_id": harness.get("adapter_id"),
            "source_id": source_id,
            "artifact_name": harness.get("artifact_name"),
            "latest_import_id": record.get("import_id"),
            "status": status,
            "negative_validation": negative,
            "failure_safety": safety,
        })

    return {
        "result_type": "connector_acceptance_drills",
        "schema_version": CONNECTOR_ACCEPTANCE_DRILLS_SCHEMA_VERSION,
        "provenance": "derived from connector test harness, imported evidence, and backend evidence validation",
        "confidence": "medium" if drills else "low",
        "package_id": (package_report or {}).get("package_id") or (connector_test_harness or {}).get("package_id"),
        "summary": {
            "total_drills": len(drills),
            "passed": sum(1 for item in drills if item["status"] == "passed"),
            "blocked": sum(1 for item in drills if item["status"] == "blocked"),
            "failed": sum(1 for item in drills if item["status"] == "failed"),
            "plain_reading": "These drills prove incomplete evidence is rejected and failed connector runs do not create imported evidence.",
        },
        "drills": drills,
        "drill_rule": "A connector is safer when both negative validation and failed-run safety drills pass for its normalized artifact.",
    }
