#!/usr/bin/env python3
from pathlib import Path
import io
import json
import sys
import urllib.error
import urllib.request
import zipfile


BASE_URL = "http://127.0.0.1:8020"
ROOT = Path(__file__).resolve().parents[2]
SAMPLE_MODEL = ROOT / "samples" / "tiny-mlp.onnx"
SAMPLE_EVIDENCE_DIR = ROOT / "samples" / "evidence"
SAMPLE_ACCURACY_DATASET = ROOT / "samples" / "datasets" / "wake-word-mini.json"
TARGET_PROFILE = "wearable"
CALIBRATION_PROFILE = "proto-audio-0237"
MODALITY = "audio_wake_word"
RUNTIME_MODE = "balanced"
UPDATED_TARGET_PROFILE = "camera"
UPDATED_MODALITY = "vision_classification"
UPDATED_CALIBRATION_PROFILE = "proto-camera-011"
UPDATED_RUNTIME_MODE = "low_latency"


def request_json(url, method="GET", data=None):
    request = urllib.request.Request(url, data=data, method=method)
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {url} failed with HTTP {exc.code}: {detail}") from exc


def request_error(url, method="GET", data=None):
    request = urllib.request.Request(url, data=data, method=method)
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")


def request_bytes(url):
    with urllib.request.urlopen(url, timeout=10) as response:
        return response.read()


def endpoint(path):
    return f"{BASE_URL}{path}"


def model_query(model_id, path):
    return (
        f"/models/{model_id}{path}"
        f"?target_profile={TARGET_PROFILE}"
        f"&calibration_profile={CALIBRATION_PROFILE}"
        f"&modality={MODALITY}"
        f"&runtime_mode={RUNTIME_MODE}"
    )


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def sample_evidence_items():
    files = {
        "compiler_mapping": "compiler-placement.json",
        "analog_error_simulation": "analog-error-simulation.json",
        "board_runtime": "board-runtime-trace.json",
        "power_thermal": "power-thermal-report.json",
        "task_accuracy": "task-accuracy-report.json",
    }
    return [
        {
            "source_id": source_id,
            "payload": json.loads((SAMPLE_EVIDENCE_DIR / filename).read_text()),
        }
        for source_id, filename in files.items()
    ]


def main():
    assert_true(SAMPLE_MODEL.exists(), f"Missing sample model: {SAMPLE_MODEL}")
    assert_true(SAMPLE_ACCURACY_DATASET.exists(), f"Missing sample accuracy dataset: {SAMPLE_ACCURACY_DATASET}")
    index_html = (ROOT / "index.html").read_text()
    assert_true("evidenceBriefSummary" in index_html, "Frontend evidence brief panel missing")
    assert_true("/evidence-brief" in index_html, "Frontend evidence brief fetch/link missing")
    assert_true("interviewBriefSummary" in index_html, "Frontend interview brief panel missing")
    assert_true("/interview-brief" in index_html, "Frontend interview brief fetch/link missing")
    assert_true("interviewDrillSummary" in index_html, "Frontend interview drill panel missing")
    assert_true("/interview-drill" in index_html, "Frontend interview drill fetch/link missing")
    assert_true("researchGuideSummary" in index_html, "Frontend research guide panel missing")
    assert_true("/research-guide" in index_html, "Frontend research guide fetch/link missing")
    assert_true("conceptGlossarySummary" in index_html, "Frontend concept glossary panel missing")
    assert_true("/concept-glossary" in index_html, "Frontend concept glossary fetch/link missing")
    assert_true("workloadFitSummary" in index_html, "Frontend workload fit panel missing")
    assert_true("/workload-fit" in index_html, "Frontend workload fit fetch/link missing")
    assert_true("systemBoundarySummary" in index_html, "Frontend system boundary panel missing")
    assert_true("/system-boundary" in index_html, "Frontend system boundary fetch/link missing")
    assert_true("physicalAiMapSummary" in index_html, "Frontend Physical AI map panel missing")
    assert_true("/physical-ai-map" in index_html, "Frontend Physical AI map fetch/link missing")
    assert_true("physicalAiRoadmapSummary" in index_html, "Frontend Physical AI roadmap panel missing")
    assert_true("/physical-ai-roadmap" in index_html, "Frontend Physical AI roadmap fetch/link missing")
    assert_true("credibilitySummary" in index_html, "Frontend workload credibility answer panel missing")
    assert_true("renderCredibilityAnswer" in index_html, "Frontend workload credibility answer renderer missing")
    assert_true("capabilityNarrative" in index_html, "Frontend investor/customer capability panel missing")
    assert_true("renderCapabilityMap" in index_html, "Frontend investor/customer capability renderer missing")
    assert_true("toolkitContributionGrid" in index_html, "Frontend external toolkit contribution panel missing")
    assert_true("renderToolkitContributions" in index_html, "Frontend external toolkit contribution renderer missing")
    assert_true("vlaReadinessSummary" in index_html, "Frontend VLA readiness panel missing")
    assert_true("/vla-readiness" in index_html, "Frontend VLA readiness fetch/link missing")
    assert_true("weightUpdateSummary" in index_html, "Frontend weight update panel missing")
    assert_true("/weight-update-readiness" in index_html, "Frontend weight update fetch/link missing")
    assert_true("calibrationDriftSummary" in index_html, "Frontend calibration drift panel missing")
    assert_true("/calibration-drift-readiness" in index_html, "Frontend calibration drift fetch/link missing")
    assert_true("controlBoundarySummary" in index_html, "Frontend control boundary panel missing")
    assert_true("/control-boundary" in index_html, "Frontend control boundary fetch/link missing")
    assert_true("sensorBoundarySummary" in index_html, "Frontend sensor boundary panel missing")
    assert_true("/sensor-boundary-readiness" in index_html, "Frontend sensor boundary fetch/link missing")
    assert_true("toolchainSummary" in index_html, "Frontend toolchain panel missing")
    assert_true("/toolchain-readiness" in index_html, "Frontend toolchain fetch/link missing")
    assert_true("compilerEcosystemSummary" in index_html, "Frontend compiler ecosystem panel missing")
    assert_true("/compiler-ecosystem-readiness" in index_html, "Frontend compiler ecosystem fetch/link missing")
    assert_true("sourceCheckSummary" in index_html, "Frontend source-check panel missing")
    assert_true("/source-check-register" in index_html, "Frontend source-check fetch/link missing")
    assert_true("connectionPlaybookSummary" in index_html, "Frontend connection playbook panel missing")
    assert_true("/connection-playbook" in index_html, "Frontend connection playbook fetch/link missing")
    assert_true("adapterExecutionSummary" in index_html, "Frontend adapter execution plan panel missing")
    assert_true("/adapter-execution-plan" in index_html, "Frontend adapter execution plan fetch/link missing")
    assert_true("adapterConnectionKitSummary" in index_html, "Frontend adapter connection kit panel missing")
    assert_true("/adapter-connection-kit" in index_html, "Frontend adapter connection kit fetch/link missing")
    assert_true("adapterEvidenceTemplateSummary" in index_html, "Frontend adapter evidence template panel missing")
    assert_true("/adapter-evidence-templates" in index_html, "Frontend adapter evidence template fetch/link missing")
    assert_true("adapterSelfTestSummary" in index_html, "Frontend adapter connection self-test panel missing")
    assert_true("/adapter-connection-self-test" in index_html, "Frontend adapter connection self-test fetch/link missing")
    assert_true("adapterIntegrationSummary" in index_html, "Frontend adapter integration readiness panel missing")
    assert_true("/adapter-integration-readiness" in index_html, "Frontend adapter integration readiness fetch/link missing")
    assert_true("externalConnectorSummary" in index_html, "Frontend external connector contract panel missing")
    assert_true("/external-connector-contract" in index_html, "Frontend external connector contract fetch/link missing")
    assert_true("connectorGuideSummary" in index_html, "Frontend connector implementation guide panel missing")
    assert_true("/connector-implementation-guide" in index_html, "Frontend connector implementation guide fetch/link missing")
    assert_true("connectorHarnessSummary" in index_html, "Frontend connector test harness panel missing")
    assert_true("/connector-test-harness" in index_html, "Frontend connector test harness fetch/link missing")
    assert_true("connectorAcceptanceSummary" in index_html, "Frontend connector acceptance report panel missing")
    assert_true("/connector-acceptance-report" in index_html, "Frontend connector acceptance report fetch/link missing")
    assert_true("connectorBacklogSummary" in index_html, "Frontend connector backlog panel missing")
    assert_true("/connector-backlog" in index_html, "Frontend connector backlog fetch/link missing")
    assert_true("connectorDeliverySummary" in index_html, "Frontend connector delivery plan panel missing")
    assert_true("/connector-delivery-plan" in index_html, "Frontend connector delivery plan fetch/link missing")
    assert_true("connectorRiskSummary" in index_html, "Frontend connector risk register panel missing")
    assert_true("/connector-risk-register" in index_html, "Frontend connector risk register fetch/link missing")
    assert_true("accuracyDatasetPath" in index_html, "Frontend accuracy dataset path input missing")
    assert_true("dataset_path=" in index_html, "Frontend dataset-backed accuracy adapter wiring missing")
    assert_true("adapter-accuracy-metrics" in index_html, "Frontend accuracy adapter metrics display missing")
    assert_true("baseline_metric" in index_html and "candidate_metric" in index_html, "Frontend accuracy metrics fields missing")
    assert_true("claim-evidence-details" in index_html, "Frontend claim evidence details display missing")
    assert_true("Measure state" in index_html and "Host counted" in index_html, "Frontend runtime and power evidence detail fields missing")
    assert_true("customEvidenceSource" in index_html, "Frontend custom evidence source selector missing")
    assert_true("customEvidenceJson" in index_html, "Frontend custom evidence JSON input missing")
    assert_true("importCustomEvidence" in index_html, "Frontend custom evidence import handler missing")
    assert_true("loadEvidenceTemplate" in index_html, "Frontend evidence template loader missing")
    assert_true("evidenceTemplates" in index_html and "operator_placements" in index_html, "Frontend evidence templates missing")
    assert_true("customEvidenceValidation" in index_html, "Frontend custom evidence validation status missing")
    assert_true("evidenceRequiredFields" in index_html, "Frontend evidence required-field map missing")
    assert_true("validateCustomEvidence" in index_html, "Frontend custom evidence validation function missing")
    assert_true("customEvidenceFile" in index_html, "Frontend custom evidence file input missing")
    assert_true("loadCustomEvidenceFile" in index_html, "Frontend custom evidence file loader missing")
    assert_true("validateCustomEvidenceBackend" in index_html and "/evidence/validate" in index_html, "Frontend backend evidence validation wiring missing")
    assert_true("customEvidencePreview" in index_html and "renderCustomEvidencePreview" in index_html, "Frontend evidence validation preview missing")
    assert_true("previewAdapterEvidence" in index_html and "data-preview-adapter-evidence" in index_html, "Frontend adapter evidence preview wiring missing")
    assert_true("adapterEvidencePreviewCache" in index_html and "renderAdapterEvidencePreview" in index_html, "Frontend adapter evidence preview display missing")

    health = request_json(endpoint("/health"))
    assert_true(health.get("status") == "ok", f"Backend health failed: {health}")
    adapters = request_json(endpoint("/adapters"))
    assert_true(adapters["result_type"] == "adapter_registry", "Adapter registry result type mismatch")
    assert_true(any(item["id"] == "model-import.onnx" for item in adapters["adapters"]), "ONNX adapter missing")
    compiler_probe = request_json(endpoint("/adapters/compiler.tvm-mlir-iree/probe"))
    assert_true(compiler_probe["result_type"] == "adapter_probe", "Adapter probe result type mismatch")
    assert_true(
        compiler_probe["normalized_artifact_contract"]["source_id"] == "compiler_mapping",
        "Compiler probe should expose compiler_mapping evidence contract",
    )
    project = request_json(
        endpoint(
            "/projects"
            f"?name=Smoke%20Project"
            f"&target_profile={TARGET_PROFILE}"
            f"&modality={MODALITY}"
            f"&calibration_profile={CALIBRATION_PROFILE}"
            f"&runtime_mode={RUNTIME_MODE}"
        ),
        method="POST",
        data=b"",
    )
    project_id = project["project_id"]

    import_path = (
        f"/models/import?filename={SAMPLE_MODEL.name}"
        f"&target_profile={TARGET_PROFILE}"
        f"&calibration_profile={CALIBRATION_PROFILE}"
        f"&project_id={project_id}"
    )
    imported = request_json(endpoint(import_path), method="POST", data=SAMPLE_MODEL.read_bytes())
    model_id = imported["model_id"]
    analysis = imported["analysis"]
    adapter_run_query = f"?model_id={model_id}&target_profile={TARGET_PROFILE}&calibration_profile={CALIBRATION_PROFILE}&modality={MODALITY}&runtime_mode={RUNTIME_MODE}"
    ort_run = request_json(endpoint(f"/adapters/quantization.onnxruntime/run{adapter_run_query}"), method="POST", data=b"")
    assert_true(ort_run["result_type"] == "adapter_run", "Adapter run result type mismatch")
    assert_true(ort_run["status"] in {"completed", "blocked"}, "ONNX Runtime adapter run should complete or explain its blocker")
    assert_true(ort_run["adapter_id"] == "quantization.onnxruntime", "Adapter run id mismatch")
    compiler_run = request_json(endpoint(f"/adapters/compiler.tvm-mlir-iree/run{adapter_run_query}"), method="POST", data=b"")
    assert_true(compiler_run["result_type"] == "adapter_run", "Compiler adapter run result type mismatch")
    assert_true(compiler_run["status"] == "completed", "Compiler adapter run should complete from local analysis")
    assert_true(compiler_run["normalized_evidence_source_id"] == "compiler_mapping", "Compiler adapter evidence source mismatch")
    assert_true(compiler_run["normalized_evidence_payload"]["operator_placements"], "Compiler adapter produced no placements")
    assert_true(compiler_run["normalized_evidence_payload"]["simulation_profile"]["not_measured_hardware"] is True, "Compiler adapter should label simulated lab profile")
    analog_run = request_json(endpoint(f"/adapters/analog.error-simulator/run{adapter_run_query}"), method="POST", data=b"")
    assert_true(analog_run["result_type"] == "adapter_run", "Analog adapter run result type mismatch")
    assert_true(analog_run["status"] == "completed", "Analog adapter run should complete from local calibration")
    assert_true(analog_run["normalized_evidence_source_id"] == "analog_error_simulation", "Analog adapter evidence source mismatch")
    assert_true(analog_run["normalized_evidence_payload"]["accuracy_impact"]["estimated_drop"] >= 0, "Analog adapter produced invalid accuracy impact")
    assert_true(analog_run["normalized_evidence_payload"]["simulation_profile"]["scenario_id"], "Analog adapter should include simulation scenario id")
    accuracy_run = request_json(endpoint(f"/adapters/accuracy.local-task-check/run{adapter_run_query}"), method="POST", data=b"")
    assert_true(accuracy_run["result_type"] == "adapter_run", "Accuracy adapter run result type mismatch")
    assert_true(accuracy_run["status"] == "completed", "Accuracy adapter run should complete from local estimates")
    assert_true(accuracy_run["normalized_evidence_source_id"] == "task_accuracy", "Accuracy adapter evidence source mismatch")
    assert_true(accuracy_run["normalized_evidence_payload"]["dataset_id"], "Accuracy adapter produced no dataset id")
    assert_true(accuracy_run["normalized_evidence_payload"]["simulation_profile"]["scenario_id"], "Accuracy adapter should include simulation scenario id")
    dataset_accuracy_run = request_json(
        endpoint(f"/adapters/accuracy.local-task-check/run{adapter_run_query}&dataset_path={SAMPLE_ACCURACY_DATASET}"),
        method="POST",
        data=b"",
    )
    assert_true(dataset_accuracy_run["result_type"] == "adapter_run", "Dataset accuracy adapter run result type mismatch")
    assert_true(dataset_accuracy_run["status"] == "completed", "Dataset accuracy adapter run should complete")
    assert_true(dataset_accuracy_run["provenance"] == "dataset-backed local task accuracy evaluation", "Dataset accuracy provenance mismatch")
    assert_true(dataset_accuracy_run["normalized_evidence_payload"]["dataset_id"] == "wake-word-mini-v0", "Dataset accuracy dataset id mismatch")
    assert_true(dataset_accuracy_run["normalized_evidence_payload"]["record_count"] == 5, "Dataset accuracy record count mismatch")
    assert_true(dataset_accuracy_run["normalized_evidence_payload"]["pass"] is True, "Dataset accuracy should pass sample tolerance")
    board_run = request_json(endpoint(f"/adapters/board.runtime/run{adapter_run_query}"), method="POST", data=b"")
    assert_true(board_run["result_type"] == "adapter_run", "Board adapter run result type mismatch")
    assert_true(board_run["status"] == "completed", "Board adapter run should complete from local runtime")
    assert_true(board_run["normalized_evidence_source_id"] == "board_runtime", "Board adapter evidence source mismatch")
    assert_true(board_run["normalized_evidence_payload"]["latency_ms"] > 0, "Board adapter produced invalid latency")
    assert_true(board_run["normalized_evidence_payload"]["simulation_profile"]["scenario_id"], "Board adapter should include simulation scenario id")
    power_run = request_json(endpoint(f"/adapters/metrics.power-thermal/run{adapter_run_query}"), method="POST", data=b"")
    assert_true(power_run["result_type"] == "adapter_run", "Power adapter run result type mismatch")
    assert_true(power_run["status"] == "completed", "Power adapter run should complete from local runtime")
    assert_true(power_run["normalized_evidence_source_id"] == "power_thermal", "Power adapter evidence source mismatch")
    assert_true(power_run["normalized_evidence_payload"]["energy_uj"] > 0, "Power adapter produced invalid energy")
    assert_true(power_run["normalized_evidence_payload"]["measurement_setup"]["not_measured_hardware"] is True, "Power adapter should label evidence as not measured hardware")
    assert_true(power_run["normalized_evidence_payload"]["measurement_setup"]["simulation_profile_id"], "Power adapter should include simulation profile id")

    assert_true(analysis["result_type"] if "result_type" in analysis else True, "Analysis response malformed")
    assert_true(analysis["layers"], "Analysis returned no layers")
    assert_true(analysis["calibration"]["profile_id"] == CALIBRATION_PROFILE, "Calibration profile mismatch")
    model_record = request_json(endpoint(f"/models/{model_id}"))
    assert_true(model_record["model_id"] == model_id, "Model metadata retrieval mismatch")
    models = request_json(endpoint("/models"))["models"]
    assert_true(any(item["model_id"] == model_id for item in models), "Imported model missing from model list")
    saved_project = request_json(endpoint(f"/projects/{project_id}"))
    assert_true(model_id in saved_project["model_ids"], "Imported model missing from project")

    quantization = request_json(endpoint(model_query(model_id, "/quantize")), method="POST", data=b"")
    assert_true(quantization["result_type"] == "quantization_report", "Quantization result type mismatch")
    assert_true(quantization["layer_recommendations"], "Quantization returned no layer recommendations")

    runtime = request_json(endpoint(model_query(model_id, "/runtime-profile")), method="POST", data=b"")
    assert_true(runtime["result_type"] == "runtime_profile", "Runtime result type mismatch")
    assert_true(runtime["summary"]["latency_ms"] > 0, "Runtime latency must be positive")
    assert_true(runtime["summary"]["energy_uj"] > 0, "Runtime energy must be positive")

    baseline = request_json(endpoint(model_query(model_id, "/baseline-comparison")), method="POST", data=b"")
    assert_true(baseline["result_type"] == "digital_baseline_comparison", "Baseline result type mismatch")
    assert_true(baseline["summary"]["energy_efficiency_x"] > 0, "Baseline energy ratio must be positive")

    package = request_json(endpoint(model_query(model_id, "/deployment-package") + f"&project_id={project_id}"), method="POST", data=b"")
    assert_true(package["result_type"] == "deployment_package_readiness", "Package result type mismatch")
    assert_true(package["manifest"], "Package manifest missing")
    assert_true(package["summary"]["project_id"] == project_id, "Package project context missing")
    saved = package.get("saved_artifacts", {})
    assert_true(saved.get("package_id") == package["package_id"], "Saved package ID mismatch")
    for link_name in ["workload_fit", "system_boundary", "research_guide", "concept_glossary", "source_check_register", "toolchain_readiness", "compiler_ecosystem_readiness", "connection_playbook", "adapter_execution_plan", "adapter_connection_kit", "adapter_evidence_templates", "adapter_connection_self_test", "adapter_integration_readiness", "external_connector_contract", "connector_implementation_guide", "connector_test_harness", "connector_acceptance_drills", "connector_acceptance_report", "connector_backlog", "connector_delivery_plan", "connector_risk_register", "claim_readiness", "imported_evidence", "adapter_runs", "evidence_audit", "evidence_brief", "evidence_brief_markdown", "interview_brief", "interview_brief_markdown", "interview_drill", "local_evidence", "sensor_boundary_readiness", "physical_ai_roadmap"]:
        assert_true(saved.get(link_name), f"Saved package missing {link_name} link")
    valid_evidence_preview = request_json(
        endpoint(f"/evidence/validate?package_id={package['package_id']}&source_id=task_accuracy"),
        method="POST",
        data=json.dumps(json.loads((SAMPLE_EVIDENCE_DIR / "task-accuracy-report.json").read_text())).encode("utf-8"),
    )
    assert_true(valid_evidence_preview["result_type"] == "evidence_validation", "Evidence validation result type mismatch")
    assert_true(valid_evidence_preview["valid"] is True, "Valid task accuracy evidence should pass validation")
    assert_true(valid_evidence_preview["preview"]["claims_affected"], "Evidence validation should preview affected claims")
    accuracy_preview_claim = next(claim for claim in valid_evidence_preview["preview"]["claims_affected"] if claim["id"] == "C4")
    assert_true(accuracy_preview_claim["before_status"] == "blocked", "Accuracy preview before status mismatch")
    assert_true(accuracy_preview_claim["after_status"] == "blocked", "Task accuracy alone should not support full accuracy claim")
    assert_true("analog_error_simulation" in accuracy_preview_claim["after_missing"], "Accuracy preview should still require analog error evidence")
    board_evidence_preview = request_json(
        endpoint(f"/evidence/validate?package_id={package['package_id']}&source_id=board_runtime"),
        method="POST",
        data=json.dumps(json.loads((SAMPLE_EVIDENCE_DIR / "board-runtime-trace.json").read_text())).encode("utf-8"),
    )
    assert_true(board_evidence_preview["valid"] is True, "Valid board runtime evidence should pass validation")
    latency_preview_claim = next(claim for claim in board_evidence_preview["preview"]["claims_affected"] if claim["id"] == "C2")
    assert_true(latency_preview_claim["before_status"] == "blocked", "Latency preview before status mismatch")
    assert_true(latency_preview_claim["after_status"] == "supported", "Board runtime preview should support latency claim")
    assert_true(board_evidence_preview["preview"]["before_summary"]["supported_lab_claims"] == 0, "Validation preview before summary should start with no supported claims")
    assert_true(board_evidence_preview["preview"]["after_summary"]["supported_lab_claims"] == 1, "Validation preview after summary should show one supported claim")
    preview_imported_list = request_json(endpoint(f"/deployment-packages/{package['package_id']}/imported-evidence"))
    assert_true(preview_imported_list["count"] == 0, "Evidence validation preview must not save imported evidence")
    adapter_payload_preview = request_json(
        endpoint(f"/evidence/validate?package_id={package['package_id']}&source_id={board_run['normalized_evidence_source_id']}"),
        method="POST",
        data=json.dumps(board_run["normalized_evidence_payload"]).encode("utf-8"),
    )
    assert_true(adapter_payload_preview["valid"] is True, "Adapter-generated evidence should validate before import")
    adapter_latency_preview = next(claim for claim in adapter_payload_preview["preview"]["claims_affected"] if claim["id"] == "C2")
    assert_true(adapter_latency_preview["after_status"] == "needs review", "Local board adapter evidence should preview as needs review, not supported")
    invalid_evidence_preview = request_json(
        endpoint(f"/evidence/validate?package_id={package['package_id']}&source_id=task_accuracy"),
        method="POST",
        data=json.dumps({
            "dataset_id": "bad-dataset",
            "metric_name": "accuracy",
            "baseline_metric": "not-a-number",
            "candidate_metric": 0.9,
            "tolerance": 0.01,
            "pass": "yes",
        }).encode("utf-8"),
    )
    assert_true(invalid_evidence_preview["valid"] is False, "Invalid task accuracy evidence should fail validation preview")
    assert_true("baseline_metric must be a number" in " ".join(invalid_evidence_preview["errors"]), "Invalid evidence preview should include structural errors")
    assert_true(invalid_evidence_preview["preview"]["after_summary"] is None, "Invalid evidence should not project after-import readiness")
    bad_status, bad_detail = request_error(
        endpoint(f"/evidence/import?package_id={package['package_id']}&source_id=task_accuracy"),
        method="POST",
        data=json.dumps({
            "dataset_id": "bad-dataset",
            "metric_name": "accuracy",
            "baseline_metric": "not-a-number",
            "candidate_metric": 0.9,
            "tolerance": 0.01,
            "pass": "yes",
        }).encode("utf-8"),
    )
    assert_true(bad_status == 400, "Bad task accuracy evidence should be rejected")
    assert_true("baseline_metric must be a number" in bad_detail and "pass must be a boolean" in bad_detail, "Bad task accuracy validation detail missing")
    bad_batch = request_json(
        endpoint(f"/evidence/import-batch?package_id={package['package_id']}"),
        method="POST",
        data=json.dumps({
            "items": [
                {
                    "source_id": "board_runtime",
                    "payload": {
                        "board_id": "bad-board",
                        "runtime_version": "runtime",
                        "latency_ms": "slow",
                        "trace": "not-a-list",
                        "fallback_events": [],
                        "provenance": {"tool": "bad-runner"},
                    },
                }
            ]
        }).encode("utf-8"),
    )
    assert_true(bad_batch["accepted_count"] == 0 and bad_batch["rejected_count"] == 1, "Bad batch evidence should be rejected")
    assert_true(any("latency_ms must be a number" in " ".join(item["errors"]) for item in bad_batch["rejected"]), "Bad batch validation detail missing")
    workload_fit = request_json(endpoint(f"/deployment-packages/{package['package_id']}/workload-fit"))
    assert_true(workload_fit["result_type"] == "workload_fit_matrix", "Workload fit result type mismatch")
    assert_true(len(workload_fit["rows"]) >= 7, "Workload fit should include all modality rows")
    assert_true(workload_fit["selected_modality"] == MODALITY, "Workload fit selected modality mismatch")
    system_boundary = request_json(endpoint(f"/deployment-packages/{package['package_id']}/system-boundary"))
    assert_true(system_boundary["result_type"] == "system_boundary_report", "System boundary result type mismatch")
    assert_true(system_boundary["summary"]["total_energy_uj"] > 0, "System boundary total energy missing")
    assert_true(system_boundary["boundary_questions"], "System boundary questions missing")
    physical_ai_map = request_json(endpoint(f"/deployment-packages/{package['package_id']}/physical-ai-map"))
    assert_true(physical_ai_map["result_type"] == "physical_ai_map", "Physical AI map result type mismatch")
    assert_true(physical_ai_map["selected_domain"], "Physical AI map selected domain missing")
    assert_true(len(physical_ai_map["domains"]) >= 8, "Physical AI map missing domain rows")
    assert_true("Keep current vendor" in " ".join(physical_ai_map["cross_domain_rules"]), "Physical AI map source-check guardrail missing")
    physical_ai_roadmap = request_json(endpoint(f"/deployment-packages/{package['package_id']}/physical-ai-roadmap"))
    assert_true(physical_ai_roadmap["result_type"] == "physical_ai_roadmap", "Physical AI roadmap result type mismatch")
    assert_true(physical_ai_roadmap["summary"]["gate_count"] >= 10, "Physical AI roadmap gate count mismatch")
    assert_true(any(gate["id"] == "weight_update_fit" for gate in physical_ai_roadmap["gates"]), "Physical AI roadmap missing weight update gate")
    assert_true(physical_ai_roadmap["gap_table"], "Physical AI roadmap gap table missing")
    assert_true("fixed-weight inference efficiency" in " ".join(physical_ai_roadmap["what_not_to_claim"]), "Physical AI roadmap overclaim guardrail missing")
    vla_readiness = request_json(endpoint(f"/deployment-packages/{package['package_id']}/vla-readiness"))
    assert_true(vla_readiness["result_type"] == "vla_readiness", "VLA readiness result type mismatch")
    assert_true(vla_readiness["model_family"], "VLA readiness model family missing")
    assert_true("analog mac efficiency" in " ".join(vla_readiness["what_not_to_claim"]).lower(), "VLA readiness overclaim guardrail missing")
    weight_update = request_json(endpoint(f"/deployment-packages/{package['package_id']}/weight-update-readiness"))
    assert_true(weight_update["result_type"] == "weight_update_readiness", "Weight update readiness result type mismatch")
    assert_true(weight_update["assumed_update_pattern"], "Weight update pattern missing")
    assert_true(not weight_update["summary"]["write_evidence_attached"], "Weight update should default to missing write evidence")
    assert_true("on-chip update support is not measured" in weight_update["summary"]["claim_boundary"], "Weight update claim boundary missing")
    calibration_drift = request_json(endpoint(f"/deployment-packages/{package['package_id']}/calibration-drift-readiness"))
    assert_true(calibration_drift["result_type"] == "calibration_drift_readiness", "Calibration drift readiness result type mismatch")
    assert_true(calibration_drift["calibration_profile"], "Calibration drift profile missing")
    assert_true("production readiness" in " ".join(calibration_drift["what_not_to_claim"]).lower(), "Calibration drift production guardrail missing")
    control_boundary = request_json(endpoint(f"/deployment-packages/{package['package_id']}/control-boundary"))
    assert_true(control_boundary["result_type"] == "control_boundary", "Control boundary result type mismatch")
    assert_true(control_boundary["inference_role"], "Control boundary inference role missing")
    assert_true("deterministic control" in control_boundary["deterministic_control_role"].lower(), "Control boundary deterministic control role missing")
    assert_true("inference" in " ".join(control_boundary["what_not_to_claim"]).lower(), "Control boundary inference guardrail missing")
    sensor_boundary = request_json(endpoint(f"/deployment-packages/{package['package_id']}/sensor-boundary-readiness"))
    assert_true(sensor_boundary["result_type"] == "sensor_boundary_readiness", "Sensor boundary result type mismatch")
    assert_true(sensor_boundary["summary"]["expected_sensors"], "Sensor boundary expected sensors missing")
    assert_true(len(sensor_boundary["boundary_choices"]) == 2, "Sensor boundary should show two boundary choices")
    assert_true("inference-only energy" in " ".join(sensor_boundary["what_not_to_claim"]).lower(), "Sensor boundary energy guardrail missing")
    assert_true("digital-tensor accelerator" in " ".join(choice["name"] for choice in sensor_boundary["boundary_choices"]), "Sensor boundary digital tensor choice missing")
    research = request_json(endpoint(f"/deployment-packages/{package['package_id']}/research-guide"))
    assert_true(research["result_type"] == "research_guide", "Research guide result type mismatch")
    assert_true(research["summary"]["paper_count"] >= 10, "Research guide paper count mismatch")
    assert_true(research["questions_to_ask"], "Research guide questions missing")
    glossary = request_json(endpoint(f"/deployment-packages/{package['package_id']}/concept-glossary"))
    assert_true(glossary["result_type"] == "concept_glossary", "Concept glossary result type mismatch")
    assert_true(glossary["summary"]["term_count"] >= 10, "Concept glossary term count mismatch")
    assert_true(any(item["term"] == "TOPS/W" for item in glossary["terms"]), "Concept glossary missing TOPS/W")
    source_check = request_json(endpoint(f"/deployment-packages/{package['package_id']}/source-check-register"))
    assert_true(source_check["result_type"] == "source_check_register", "Source-check register result type mismatch")
    assert_true(source_check["summary"]["checked_items"] >= 7, "Source-check register checked count mismatch")
    assert_true(any(item["id"] == "aspirare_semi" for item in source_check["checked_items"]), "Source-check register missing Aspirare")
    assert_true(any(item["id"] == "gemini_robotics_on_device_2" for item in source_check["checked_items"]), "Source-check register missing Gemini Robotics On-Device 2")
    assert_true("measured support" in " ".join(source_check["use_rules"]).lower(), "Source-check measured-support rule missing")
    connection_playbook = request_json(endpoint(f"/deployment-packages/{package['package_id']}/connection-playbook"))
    assert_true(connection_playbook["result_type"] == "connection_playbook", "Connection playbook result type mismatch")
    assert_true(connection_playbook["summary"]["total_targets"] >= 6, "Connection playbook target count mismatch")
    assert_true(any(item["adapter_id"] == "board.runtime" for item in connection_playbook["connection_targets"]), "Connection playbook missing board runtime")
    adapter_execution_plan = request_json(endpoint(f"/deployment-packages/{package['package_id']}/adapter-execution-plan"))
    assert_true(adapter_execution_plan["result_type"] == "adapter_execution_plan", "Adapter execution plan result type mismatch")
    assert_true(adapter_execution_plan["summary"]["total_adapters"] >= 6, "Adapter execution plan target count mismatch")
    board_execution = next(item for item in adapter_execution_plan["execution_targets"] if item["adapter_id"] == "board.runtime")
    assert_true([step["name"] for step in board_execution["steps"]] == ["configure", "run", "normalize", "validate_preview", "import_archive"], "Adapter execution steps mismatch")
    assert_true(board_execution["normalized_artifact"] == "board-runtime-trace.json", "Adapter execution artifact mismatch")
    adapter_connection_kit = request_json(endpoint(f"/deployment-packages/{package['package_id']}/adapter-connection-kit"))
    assert_true(adapter_connection_kit["result_type"] == "adapter_connection_kit", "Adapter connection kit result type mismatch")
    board_connection = next(item for item in adapter_connection_kit["adapters"] if item["adapter_id"] == "board.runtime")
    assert_true("ANALOG_AI_BOARD_API_URL" in board_connection["env_vars"], "Board connection kit env var missing")
    assert_true(board_connection["commands"]["validate"].endswith("source_id=board_runtime"), "Board connection kit validate command mismatch")
    adapter_evidence_templates = request_json(endpoint(f"/deployment-packages/{package['package_id']}/adapter-evidence-templates"))
    assert_true(adapter_evidence_templates["result_type"] == "adapter_evidence_templates", "Adapter evidence templates result type mismatch")
    board_template = next(item for item in adapter_evidence_templates["templates"] if item["source_id"] == "board_runtime")
    assert_true(board_template["template_valid"] is True, "Board evidence template should validate")
    assert_true("latency_ms" in board_template["template_payload"], "Board evidence template latency missing")
    template_latency_claim = next(claim for claim in board_template["claim_preview"]["claims_affected"] if claim["id"] == "C2")
    assert_true(template_latency_claim["before_status"] == "blocked", "Template claim preview before status mismatch")
    assert_true(template_latency_claim["after_status"] == "supported", "External board runtime template should preview supported latency")
    adapter_connection_self_test = request_json(endpoint(f"/deployment-packages/{package['package_id']}/adapter-connection-self-test"))
    assert_true(adapter_connection_self_test["result_type"] == "adapter_connection_self_test", "Adapter connection self-test result type mismatch")
    board_self_test = next(item for item in adapter_connection_self_test["results"] if item["adapter_id"] == "board.runtime")
    assert_true(any(check["name"] == "environment variable: ANALOG_AI_BOARD_API_URL" for check in board_self_test["checks"]), "Board self-test env check missing")
    adapter_integration = request_json(endpoint(f"/deployment-packages/{package['package_id']}/adapter-integration-readiness"))
    assert_true(adapter_integration["result_type"] == "adapter_integration_readiness", "Adapter integration readiness result type mismatch")
    assert_true(adapter_integration["summary"]["total_adapters"] >= 6, "Adapter integration readiness should cover configured adapters")
    assert_true(adapter_integration["next_priorities"], "Adapter integration readiness next priorities missing")
    board_integration = next(item for item in adapter_integration["readiness_targets"] if item["adapter_id"] == "board.runtime")
    assert_true(board_integration["expected_artifact"] == "board-runtime-trace.json", "Adapter integration board artifact mismatch")
    external_connector = request_json(endpoint(f"/deployment-packages/{package['package_id']}/external-connector-contract"))
    assert_true(external_connector["result_type"] == "external_connector_contract", "External connector contract result type mismatch")
    board_contract = next(item for item in external_connector["connectors"] if item["adapter_id"] == "board.runtime")
    assert_true(board_contract["response_shape"]["artifact_name"] == "board-runtime-trace.json", "Board connector response artifact mismatch")
    assert_true("ANALOG_AI_BOARD_API_URL" in board_contract["request_shape"]["env_vars"], "Board connector request env var missing")
    connector_guide = request_json(endpoint(f"/deployment-packages/{package['package_id']}/connector-implementation-guide"))
    assert_true(connector_guide["result_type"] == "connector_implementation_guide", "Connector implementation guide result type mismatch")
    board_guide = next(item for item in connector_guide["connectors"] if item["adapter_id"] == "board.runtime")
    assert_true(board_guide["build_first"] is True, "Board connector should be in first evidence loop")
    assert_true(any("normalized payload passes" in item for item in board_guide["done_criteria"]), "Board connector done criteria missing validation")
    connector_harness = request_json(endpoint(f"/deployment-packages/{package['package_id']}/connector-test-harness"))
    assert_true(connector_harness["result_type"] == "connector_test_harness", "Connector test harness result type mismatch")
    board_harness = next(item for item in connector_harness["harnesses"] if item["adapter_id"] == "board.runtime")
    assert_true(len(board_harness["test_cases"]) >= 6, "Board connector test harness should include safety checks")
    assert_true(any(item["kind"] == "safety" for item in board_harness["test_cases"]), "Board connector harness missing failure safety test")
    connector_drills = request_json(endpoint(f"/deployment-packages/{package['package_id']}/connector-acceptance-drills"))
    assert_true(connector_drills["result_type"] == "connector_acceptance_drills", "Connector acceptance drills result type mismatch")
    board_drill = next(item for item in connector_drills["drills"] if item["adapter_id"] == "board.runtime")
    assert_true(board_drill["status"] == "blocked", "Board drill should be blocked before evidence import")
    connector_acceptance = request_json(endpoint(f"/deployment-packages/{package['package_id']}/connector-acceptance-report"))
    assert_true(connector_acceptance["result_type"] == "connector_acceptance_report", "Connector acceptance report result type mismatch")
    board_acceptance = next(item for item in connector_acceptance["connectors"] if item["adapter_id"] == "board.runtime")
    assert_true(board_acceptance["artifact_name"] == "board-runtime-trace.json", "Board connector acceptance artifact mismatch")
    assert_true(any(item["kind"] == "probe" for item in board_acceptance["case_results"]), "Board connector acceptance missing probe result")
    assert_true(board_acceptance["drill_status"] in {"blocked", "not run"}, "Board connector acceptance should not show passed drills before evidence import")
    if board_acceptance.get("replay_fixture"):
        assert_true(board_acceptance["acceptance_status"] == "replay accepted", "Board replay connector should be replay accepted")
        assert_true(board_acceptance["external_acceptance"] is False, "Board replay connector should not count as external acceptance")
        assert_true(any(item["status"] == "passed by replay fixture" for item in board_acceptance["case_results"]), "Board replay connector should label replay-passed cases")
    power_acceptance = next(item for item in connector_acceptance["connectors"] if item["adapter_id"] == "metrics.power-thermal")
    if power_acceptance.get("replay_fixture"):
        assert_true(power_acceptance["acceptance_status"] == "replay accepted", "Power replay connector should be replay accepted")
        assert_true(power_acceptance["external_acceptance"] is False, "Power replay connector should not count as external acceptance")
    connector_backlog = request_json(endpoint(f"/deployment-packages/{package['package_id']}/connector-backlog"))
    assert_true(connector_backlog["result_type"] == "connector_backlog", "Connector backlog result type mismatch")
    assert_true(connector_backlog["summary"]["total_tasks"] >= 1, "Connector backlog should contain actionable tasks")
    assert_true(any(task["adapter_id"] == "board.runtime" for task in connector_backlog["tasks"]), "Connector backlog missing board runtime task")
    connector_delivery = request_json(endpoint(f"/deployment-packages/{package['package_id']}/connector-delivery-plan"))
    assert_true(connector_delivery["result_type"] == "connector_delivery_plan", "Connector delivery plan result type mismatch")
    assert_true(connector_delivery["summary"]["total_tasks"] == connector_backlog["summary"]["total_tasks"], "Connector delivery task count mismatch")
    assert_true(any(item["id"] == "M1" for item in connector_delivery["milestones"]), "Connector delivery missing M1 milestone")
    connector_risk = request_json(endpoint(f"/deployment-packages/{package['package_id']}/connector-risk-register"))
    assert_true(connector_risk["result_type"] == "connector_risk_register", "Connector risk register result type mismatch")
    assert_true(connector_risk["summary"]["total_risks"] >= 4, "Connector risk register should include delivery risks")
    assert_true(any(item["id"] == "CR-1" for item in connector_risk["risks"]), "Connector risk register missing probe risk")
    toolchain = request_json(endpoint(f"/deployment-packages/{package['package_id']}/toolchain-readiness"))
    assert_true(toolchain["result_type"] == "toolchain_readiness", "Toolchain readiness result type mismatch")
    assert_true(toolchain["summary"]["total_steps"] == 9, "Toolchain readiness step count mismatch")
    assert_true(any(step["id"] == "customer_handoff" for step in toolchain["steps"]), "Toolchain readiness missing customer handoff")
    compiler_ecosystem = request_json(endpoint(f"/deployment-packages/{package['package_id']}/compiler-ecosystem-readiness"))
    assert_true(compiler_ecosystem["result_type"] == "compiler_ecosystem_readiness", "Compiler ecosystem result type mismatch")
    assert_true(compiler_ecosystem["summary"]["onnx_status"] == "current first path", "Compiler ecosystem ONNX status mismatch")
    assert_true(compiler_ecosystem["summary"]["pytorch_status"] == "roadmap connector", "Compiler ecosystem PyTorch should be roadmap")
    assert_true(compiler_ecosystem["summary"]["jax_xla_status"] == "roadmap connector", "Compiler ecosystem JAX/XLA should be roadmap")
    assert_true("zero-touch" in " ".join(compiler_ecosystem["adoption_risks"]).lower(), "Compiler ecosystem zero-touch risk missing")
    assert_true("PyTorch support" in " ".join(compiler_ecosystem["what_not_to_claim"]), "Compiler ecosystem PyTorch overclaim guardrail missing")

    measurement = request_json(endpoint(model_query(model_id, "/measurement-evidence") + f"&project_id={project_id}"), method="POST", data=b"")
    assert_true(measurement["result_type"] == "measurement_evidence", "Measurement evidence result type mismatch")
    assert_true(len(measurement["required_sources"]) == 5, "Measurement evidence source count mismatch")
    assert_true(any(source["id"] == "power_thermal" for source in measurement["required_sources"]), "Power/thermal evidence source missing")
    assert_true(measurement["summary"]["claim_status"] == "measurement blocked", "Measurement evidence should block measured claims in local mode")
    local_evidence = request_json(endpoint(f"/deployment-packages/{package['package_id']}/local-evidence"), method="POST", data=b"")
    assert_true(local_evidence["result_type"] == "local_evidence_run", "Local evidence workflow result type mismatch")
    assert_true(local_evidence["accepted_count"] == 5, "Local evidence workflow should import five artifacts")
    assert_true(local_evidence["saved_adapter_run_count"] == 5, "Local evidence workflow should save five adapter run audit records")
    assert_true(local_evidence["skipped_count"] == 0, "Initial local evidence workflow should not skip artifacts")
    assert_true(local_evidence["rejected_count"] == 0, "Local evidence workflow should not reject local artifacts")
    adapter_run_list = request_json(endpoint(f"/deployment-packages/{package['package_id']}/adapter-runs"))
    assert_true(adapter_run_list["result_type"] == "adapter_run_list", "Adapter run list result type mismatch")
    assert_true(adapter_run_list["count"] == 5, "Adapter run audit record count mismatch")
    assert_true(all(item["audit_rule"].startswith("Adapter run records are audit trail only") for item in adapter_run_list["adapter_runs"]), "Adapter run audit rule missing")
    assert_true(all(item.get("path") for item in adapter_run_list["adapter_runs"]), "Adapter run record paths missing")
    imported_list = request_json(endpoint(f"/deployment-packages/{package['package_id']}/imported-evidence"))
    assert_true(imported_list["count"] == 5, "Local evidence imported evidence count mismatch")
    local_connector_drills = request_json(endpoint(f"/deployment-packages/{package['package_id']}/connector-acceptance-drills"))
    local_board_drill = next(item for item in local_connector_drills["drills"] if item["adapter_id"] == "board.runtime")
    assert_true(local_board_drill["negative_validation"]["status"] == "passed", "Local board negative validation drill should pass")
    assert_true(local_board_drill["failure_safety"]["status"] == "passed", "Local board failure safety drill should pass")
    local_connector_acceptance = request_json(endpoint(f"/deployment-packages/{package['package_id']}/connector-acceptance-report"))
    local_board_acceptance = next(item for item in local_connector_acceptance["connectors"] if item["adapter_id"] == "board.runtime")
    assert_true(local_board_acceptance["drill_status"] == "passed", "Local board connector acceptance should include passed drill status")
    if local_board_acceptance.get("replay_fixture"):
        assert_true(local_board_acceptance["acceptance_status"] == "replay accepted", "Local board replay connector should be replay accepted")
        assert_true(local_board_acceptance["external_acceptance"] is False, "Local board replay connector should not count as external acceptance")
    local_audit = request_json(endpoint(f"/deployment-packages/{package['package_id']}/evidence-audit"))
    assert_true(local_audit["result_type"] == "evidence_audit", "Evidence audit result type mismatch")
    assert_true(local_audit["summary"]["local_generated_imports"] == 5, "Local audit should count five local imports")
    assert_true(local_audit["summary"]["nonlocal_imports"] == 0, "Local audit should not count non-local imports yet")
    local_refresh = request_json(endpoint(f"/deployment-packages/{package['package_id']}/local-evidence"), method="POST", data=b"")
    assert_true(local_refresh["accepted_count"] == 5, "Local evidence refresh should replace and import five local artifacts")
    assert_true(local_refresh["saved_adapter_run_count"] == 5, "Local evidence refresh should save five adapter run audit records")
    assert_true(local_refresh["skipped_count"] == 0, "Local evidence refresh should not skip before non-local evidence exists")
    refreshed_imported_list = request_json(endpoint(f"/deployment-packages/{package['package_id']}/imported-evidence"))
    assert_true(refreshed_imported_list["count"] == 5, "Local evidence refresh should not add duplicate local evidence")
    refreshed_adapter_run_list = request_json(endpoint(f"/deployment-packages/{package['package_id']}/adapter-runs"))
    assert_true(refreshed_adapter_run_list["count"] == 10, "Local evidence refresh should preserve adapter run audit history")
    readiness_with_runtime = request_json(endpoint(f"/deployment-packages/{package['package_id']}/claim-readiness"))
    assert_true(readiness_with_runtime["result_type"] == "claim_readiness", "Claim readiness result type mismatch")
    assert_true(readiness_with_runtime["summary"]["supported_lab_claims"] == 1, "Only compiler should be supported from local simulated evidence")
    assert_true(readiness_with_runtime["summary"]["needs_review_lab_claims"] == 3, "Local latency, energy, and failed accuracy should need review")
    assert_true(readiness_with_runtime["production_claim"]["status"] == "blocked", "Production claim must stay blocked")
    failed_accuracy_claim = next(item for item in readiness_with_runtime["lab_claims"] if item["id"] == "C4")
    assert_true(failed_accuracy_claim["evidence_details"], "Failed accuracy claim should include evidence details")
    assert_true(any(detail.get("metric_name") for detail in failed_accuracy_claim["evidence_details"]), "Failed accuracy claim should include task metric details")
    local_latency_claim = next(item for item in readiness_with_runtime["lab_claims"] if item["id"] == "C2")
    local_latency_detail = next(detail for detail in local_latency_claim["evidence_details"] if detail["source_id"] == "board_runtime")
    assert_true(local_latency_detail["measurement_status"] == "local simulation", "Local latency evidence should be marked as local simulation")
    local_energy_claim = next(item for item in readiness_with_runtime["lab_claims"] if item["id"] == "C3")
    local_power_detail = next(detail for detail in local_energy_claim["evidence_details"] if detail["source_id"] == "power_thermal")
    assert_true(local_power_detail["not_measured_hardware"] is True, "Local power evidence should preserve not_measured_hardware")
    assert_true(
        any(claim["name"] == "Compiler placement is evidence-backed" and claim["status"] == "supported" for claim in readiness_with_runtime["lab_claims"]),
        "Compiler placement claim should be supported after local evidence import",
    )
    batch_import = request_json(
        endpoint(f"/evidence/import-batch?package_id={package['package_id']}"),
        method="POST",
        data=json.dumps({"items": sample_evidence_items()}).encode("utf-8"),
    )
    assert_true(batch_import["result_type"] == "imported_evidence_batch", "Batch import result type mismatch")
    assert_true(batch_import["accepted_count"] == 5, "Batch import accepted count mismatch")
    assert_true(batch_import["rejected_count"] == 0, "Batch import should not reject sample evidence")
    full_measurement = request_json(endpoint(f"/deployment-packages/{package['package_id']}/measurement-evidence"))
    assert_true(full_measurement["summary"]["imported_sources"] == 5, "Full measurement evidence source count mismatch")
    full_imported_list = request_json(endpoint(f"/deployment-packages/{package['package_id']}/imported-evidence"))
    assert_true(full_imported_list["count"] == 10, "Full imported evidence file count mismatch")
    full_audit = request_json(endpoint(f"/deployment-packages/{package['package_id']}/evidence-audit"))
    assert_true(full_audit["summary"]["local_generated_imports"] == 5, "Full audit local import count mismatch")
    assert_true(full_audit["summary"]["nonlocal_imports"] == 5, "Full audit non-local import count mismatch")
    assert_true(full_audit["summary"]["sources_with_nonlocal_evidence"] == 5, "Full audit should protect all sources")
    local_after_sample = request_json(endpoint(f"/deployment-packages/{package['package_id']}/local-evidence"), method="POST", data=b"")
    assert_true(local_after_sample["accepted_count"] == 0, "Local evidence should not override non-local evidence by default")
    assert_true(local_after_sample["saved_adapter_run_count"] == 0, "Skipped local evidence should not save adapter runs")
    assert_true(local_after_sample["skipped_count"] == 5, "Local evidence should skip all sources after sample evidence import")
    skipped_imported_list = request_json(endpoint(f"/deployment-packages/{package['package_id']}/imported-evidence"))
    assert_true(skipped_imported_list["count"] == 10, "Skipped local evidence should not change imported evidence count")
    full_claim_readiness = request_json(endpoint(f"/deployment-packages/{package['package_id']}/claim-readiness"))
    assert_true(full_claim_readiness["summary"]["supported_lab_claims"] == 4, "Full lab claim support count mismatch")
    assert_true(full_claim_readiness["production_claim"]["status"] == "blocked", "Production claim must stay blocked after full sample evidence")
    accuracy_claim = next(item for item in full_claim_readiness["lab_claims"] if item["id"] == "C4")
    assert_true(accuracy_claim["status"] == "supported", "Accuracy claim should be supported after passing sample evidence")
    accuracy_details = [detail for detail in accuracy_claim["evidence_details"] if detail["source_id"] == "task_accuracy"]
    assert_true(accuracy_details and accuracy_details[0]["dataset_id"], "Supported accuracy claim missing dataset detail")
    assert_true(accuracy_details[0]["pass"] is True, "Supported accuracy claim should show pass=true")
    latency_claim = next(item for item in full_claim_readiness["lab_claims"] if item["id"] == "C2")
    latency_detail = next(detail for detail in latency_claim["evidence_details"] if detail["source_id"] == "board_runtime")
    assert_true(latency_detail["measurement_status"] == "external or measured artifact", "Sample board evidence should be marked external or measured")
    energy_claim = next(item for item in full_claim_readiness["lab_claims"] if item["id"] == "C3")
    power_detail = next(detail for detail in energy_claim["evidence_details"] if detail["source_id"] == "power_thermal")
    assert_true(power_detail["includes_host_overhead"] is True, "Sample power evidence should show host overhead counted")
    evidence_brief = request_json(endpoint(f"/deployment-packages/{package['package_id']}/evidence-brief"))
    assert_true(evidence_brief["result_type"] == "evidence_brief", "Evidence brief result type mismatch")
    assert_true(evidence_brief["summary"]["supported_lab_claims"] == 4, "Evidence brief support count mismatch")
    assert_true(evidence_brief["summary"]["production_readiness"] == "blocked", "Evidence brief must keep production blocked")
    assert_true(len(evidence_brief["readiness_ladder"]) == 5, "Evidence brief readiness ladder length mismatch")
    assert_true(evidence_brief["readiness_ladder"][-1]["status"] == "blocked", "Evidence brief production ladder must stay blocked")
    evidence_brief_markdown = request_bytes(endpoint(f"/deployment-packages/{package['package_id']}/evidence-brief.md")).decode("utf-8")
    assert_true("What Not To Claim" in evidence_brief_markdown, "Evidence brief markdown missing overclaim section")
    assert_true("Readiness Ladder" in evidence_brief_markdown, "Evidence brief markdown missing readiness ladder")
    interview_brief = request_json(endpoint(f"/deployment-packages/{package['package_id']}/interview-brief"))
    assert_true(interview_brief["result_type"] == "interview_brief", "Interview brief result type mismatch")
    assert_true(interview_brief["summary"]["production_readiness"] == "blocked", "Interview brief must keep production blocked")
    assert_true(interview_brief["questions_to_ask"], "Interview brief questions missing")
    interview_brief_markdown = request_bytes(endpoint(f"/deployment-packages/{package['package_id']}/interview-brief.md")).decode("utf-8")
    assert_true("First Principles" in interview_brief_markdown, "Interview brief markdown missing first principles")
    interview_drill = request_json(endpoint(f"/deployment-packages/{package['package_id']}/interview-drill"))
    assert_true(interview_drill["result_type"] == "interview_drill", "Interview drill result type mismatch")
    assert_true(interview_drill["summary"]["question_count"] >= 8, "Interview drill question count mismatch")
    assert_true(interview_drill["summary"]["production_readiness"] == "blocked", "Interview drill must keep production blocked")

    gates = request_json(endpoint(model_query(model_id, "/evidence-gates") + f"&project_id={project_id}"), method="POST", data=b"")
    assert_true(gates["result_type"] == "evidence_gate_report", "Evidence gates result type mismatch")
    assert_true(len(gates["gates"]) == 12, "Expected 12 evidence gates")
    assert_true(any(gate["name"] == "External tool connections" for gate in gates["gates"]), "Adapter evidence gate missing")
    assert_true(any(gate["name"] == "Measurement evidence contract" for gate in gates["gates"]), "Measurement evidence gate missing")

    review = request_json(endpoint(model_query(model_id, "/review-report") + f"&project_id={project_id}"), method="POST", data=b"")
    assert_true(review["result_type"] == "plain_language_review_report", "Review result type mismatch")
    assert_true("What To Say Clearly" in review["markdown"], "Review markdown missing expected section")
    assert_true(review["summary"]["project_id"] == project_id, "Review project context missing")

    decision = request_json(endpoint(model_query(model_id, "/decision-report") + f"&project_id={project_id}"), method="POST", data=b"")
    assert_true(decision["result_type"] == "decision_report", "Decision report result type mismatch")
    assert_true(decision["decision"] in {"good fit", "needs rewrite", "needs measurement", "not a fit yet"}, "Unexpected decision label")
    assert_true(decision["reasons"], "Decision report missing reasons")
    assert_true(decision["next_actions"], "Decision report missing next actions")

    rewrites = request_json(endpoint(model_query(model_id, "/rewrite-suggestions") + f"&project_id={project_id}"), method="POST", data=b"")
    assert_true(rewrites["result_type"] == "rewrite_suggestions", "Rewrite suggestions result type mismatch")
    assert_true(rewrites["suggestions"], "Rewrite suggestions missing suggestions")
    assert_true(rewrites["summary"]["boundary_count"] >= 0, "Rewrite suggestions missing boundary count")
    first_rewrite_id = rewrites["suggestions"][0]["id"]
    what_if = request_json(endpoint(model_query(model_id, "/rewrite-what-if") + f"&project_id={project_id}&suggestion_ids={first_rewrite_id}"), method="POST", data=b"")
    assert_true(what_if["result_type"] == "rewrite_what_if", "Rewrite what-if result type mismatch")
    assert_true(what_if["confidence"] == "low", "Rewrite what-if confidence should be low")
    assert_true(first_rewrite_id in what_if["selected_suggestion_ids"], "Rewrite what-if selected suggestion mismatch")
    assert_true(
        what_if["deltas"]["energy_uj"] != 0 or what_if["deltas"]["latency_ms"] != 0 or what_if["deltas"]["analog_coverage_points"] != 0,
        "Rewrite what-if did not change any metric",
    )
    rewrite_plan = request_json(endpoint(model_query(model_id, "/rewrite-plan") + f"&project_id={project_id}&suggestion_ids={first_rewrite_id}"), method="POST", data=b"")
    assert_true(rewrite_plan["result_type"] == "rewrite_plan", "Rewrite plan result type mismatch")
    assert_true(rewrite_plan["selected_actions"], "Rewrite plan missing selected actions")
    assert_true(rewrite_plan["validation_steps"], "Rewrite plan missing validation steps")
    assert_true(rewrite_plan["evidence_delta"], "Rewrite plan missing evidence delta")
    assert_true(rewrite_plan["selected_actions"][0]["suggestion_id"] == first_rewrite_id, "Rewrite plan selected suggestion mismatch")
    work_order = request_json(endpoint(model_query(model_id, "/rewrite-work-order") + f"&project_id={project_id}&suggestion_ids={first_rewrite_id}"), method="POST", data=b"")
    assert_true(work_order["result_type"] == "rewrite_work_order", "Rewrite work order result type mismatch")
    assert_true(work_order["tasks"], "Rewrite work order missing tasks")
    assert_true(work_order["acceptance_gates"], "Rewrite work order missing acceptance gates")
    assert_true(work_order["evidence_to_attach"], "Rewrite work order missing evidence attachments")
    assert_true(work_order["tasks"][0]["layer_id"] == rewrite_plan["selected_actions"][0]["layer_id"], "Rewrite work order task layer mismatch")

    project_run = request_json(
        endpoint(f"/projects/{project_id}/runs?model_id={model_id}"),
        method="POST",
        data=b"",
    )
    assert_true(project_run["result_type"] == "project_evaluation_run", "Project run result type mismatch")
    assert_true(project_run["run_id"], "Project run ID missing")
    assert_true(project_run["run"]["run_id"] == project_run["run_id"], "Nested project run ID mismatch")
    assert_true(project_run["project"]["project_id"] == project_id, "Project run context mismatch")
    assert_true(project_run["model_id"] == model_id, "Project run model mismatch")
    assert_true(project_run["summary"]["latency_ms"] > 0, "Project run latency must be positive")
    assert_true(project_run["summary"]["energy_uj"] > 0, "Project run energy must be positive")
    assert_true(project_run["summary"]["overall_status"] == project_run["artifacts"]["evidence"]["overall_status"], "Project run evidence summary mismatch")
    assert_true(project_run["artifacts"]["package"]["summary"]["project_id"] == project_id, "Project run package project context missing")
    assert_true(project_run["artifacts"]["review"]["summary"]["project_id"] == project_id, "Project run review project context missing")
    assert_true(project_run["artifacts"]["decision"]["result_type"] == "decision_report", "Project run decision report missing")
    assert_true(project_run["artifacts"]["measurement"]["result_type"] == "measurement_evidence", "Project run measurement evidence missing")
    assert_true(project_run["artifacts"]["physical_ai_map"]["result_type"] == "physical_ai_map", "Project run Physical AI map missing")
    assert_true(project_run["artifacts"]["physical_ai_roadmap"]["result_type"] == "physical_ai_roadmap", "Project run Physical AI roadmap missing")
    assert_true(project_run["artifacts"]["vla_readiness"]["result_type"] == "vla_readiness", "Project run VLA readiness missing")
    assert_true(project_run["artifacts"]["weight_update_readiness"]["result_type"] == "weight_update_readiness", "Project run weight update readiness missing")
    assert_true(project_run["artifacts"]["calibration_drift_readiness"]["result_type"] == "calibration_drift_readiness", "Project run calibration drift readiness missing")
    assert_true(project_run["artifacts"]["control_boundary"]["result_type"] == "control_boundary", "Project run control boundary missing")
    assert_true(project_run["artifacts"]["sensor_boundary_readiness"]["result_type"] == "sensor_boundary_readiness", "Project run sensor boundary missing")
    assert_true(project_run["artifacts"]["compiler_ecosystem_readiness"]["result_type"] == "compiler_ecosystem_readiness", "Project run compiler ecosystem missing")
    assert_true(project_run["artifacts"]["source_check_register"]["result_type"] == "source_check_register", "Project run source-check register missing")
    assert_true(project_run["artifacts"]["rewrites"]["result_type"] == "rewrite_suggestions", "Project run rewrite suggestions missing")
    assert_true(project_run["artifacts"]["rewrite_what_if"]["result_type"] == "rewrite_what_if", "Project run rewrite what-if missing")
    assert_true(project_run["artifacts"]["rewrite_plan"]["result_type"] == "rewrite_plan", "Project run rewrite plan missing")
    assert_true(project_run["artifacts"]["rewrite_work_order"]["result_type"] == "rewrite_work_order", "Project run rewrite work order missing")
    assert_true(project_run["saved_artifacts"]["package_id"] == project_run["package_id"], "Project run saved package ID mismatch")
    assert_true(project_run["saved_artifacts"]["workload_fit"].endswith("/workload-fit"), "Project run workload fit link missing")
    assert_true(project_run["saved_artifacts"]["system_boundary"].endswith("/system-boundary"), "Project run system boundary link missing")
    assert_true(project_run["saved_artifacts"]["physical_ai_map"].endswith("/physical-ai-map"), "Project run Physical AI map link missing")
    assert_true(project_run["saved_artifacts"]["physical_ai_roadmap"].endswith("/physical-ai-roadmap"), "Project run Physical AI roadmap link missing")
    assert_true(project_run["saved_artifacts"]["vla_readiness"].endswith("/vla-readiness"), "Project run VLA readiness link missing")
    assert_true(project_run["saved_artifacts"]["weight_update_readiness"].endswith("/weight-update-readiness"), "Project run weight update readiness link missing")
    assert_true(project_run["saved_artifacts"]["calibration_drift_readiness"].endswith("/calibration-drift-readiness"), "Project run calibration drift readiness link missing")
    assert_true(project_run["saved_artifacts"]["control_boundary"].endswith("/control-boundary"), "Project run control boundary link missing")
    assert_true(project_run["saved_artifacts"]["sensor_boundary_readiness"].endswith("/sensor-boundary-readiness"), "Project run sensor boundary link missing")
    assert_true(project_run["saved_artifacts"]["research_guide"].endswith("/research-guide"), "Project run research guide link missing")
    assert_true(project_run["saved_artifacts"]["concept_glossary"].endswith("/concept-glossary"), "Project run concept glossary link missing")
    assert_true(project_run["saved_artifacts"]["source_check_register"].endswith("/source-check-register"), "Project run source-check link missing")
    assert_true(project_run["saved_artifacts"]["toolchain_readiness"].endswith("/toolchain-readiness"), "Project run toolchain readiness link missing")
    assert_true(project_run["saved_artifacts"]["compiler_ecosystem_readiness"].endswith("/compiler-ecosystem-readiness"), "Project run compiler ecosystem link missing")
    assert_true(project_run["saved_artifacts"]["connection_playbook"].endswith("/connection-playbook"), "Project run connection playbook link missing")
    assert_true(project_run["saved_artifacts"]["evidence_audit"].endswith("/evidence-audit"), "Project run evidence audit link missing")
    assert_true(project_run["saved_artifacts"]["evidence_brief_markdown"].endswith("/evidence-brief.md"), "Project run evidence brief link missing")
    assert_true(project_run["saved_artifacts"]["interview_brief_markdown"].endswith("/interview-brief.md"), "Project run interview brief link missing")
    assert_true(project_run["saved_artifacts"]["interview_drill"].endswith("/interview-drill"), "Project run interview drill link missing")
    project_run_record = request_json(endpoint(f"/project-runs/{project_run['run_id']}"))
    assert_true(project_run_record["run_id"] == project_run["run_id"], "Project run record retrieval mismatch")
    assert_true(project_run_record["package_id"] == project_run["package_id"], "Project run package retrieval mismatch")
    all_runs = request_json(endpoint("/project-runs"))["runs"]
    assert_true(any(item["run_id"] == project_run["run_id"] for item in all_runs), "Project run missing from global run list")
    project_runs = request_json(endpoint(f"/projects/{project_id}/runs"))
    assert_true(project_runs["project"]["project_id"] == project_id, "Project run list project mismatch")
    assert_true(any(item["run_id"] == project_run["run_id"] for item in project_runs["runs"]), "Project run missing from project run list")

    project_run_2 = request_json(
        endpoint(f"/projects/{project_id}/runs?model_id={model_id}"),
        method="POST",
        data=b"",
    )
    assert_true(project_run_2["result_type"] == "project_evaluation_run", "Second project run result type mismatch")
    assert_true(project_run_2["run_id"] != project_run["run_id"], "Second project run did not create a new run ID")
    compare_ids = f"{project_run['run_id']},{project_run_2['run_id']}"
    comparison = request_json(endpoint(f"/project-runs/compare?run_ids={compare_ids}"))
    assert_true(comparison["result_type"] == "project_run_comparison", "Run comparison result type mismatch")
    assert_true(comparison["run_count"] == 2, "Run comparison count mismatch")
    assert_true(comparison["baseline_run_id"] == project_run["run_id"], "Run comparison baseline mismatch")
    assert_true(comparison["rows"][1]["deltas_vs_baseline"]["latency_ms"] == 0, "Expected matching smoke runs to have zero latency delta")
    project_comparison = request_json(endpoint(f"/projects/{project_id}/runs/compare"))
    assert_true(project_comparison["result_type"] == "project_run_comparison", "Project run comparison result type mismatch")
    assert_true(project_comparison["project"]["project_id"] == project_id, "Project comparison context mismatch")
    assert_true(project_comparison["run_count"] >= 2, "Project comparison did not include at least two runs")

    updated_project = request_json(
        endpoint(
            f"/projects/{project_id}"
            f"?name=Smoke%20Project%20Camera"
            f"&target_profile={UPDATED_TARGET_PROFILE}"
            f"&modality={UPDATED_MODALITY}"
            f"&calibration_profile={UPDATED_CALIBRATION_PROFILE}"
            f"&runtime_mode={UPDATED_RUNTIME_MODE}"
        ),
        method="PATCH",
        data=b"",
    )
    assert_true(updated_project["project_id"] == project_id, "Updated project ID mismatch")
    assert_true(updated_project["target_profile"] == UPDATED_TARGET_PROFILE, "Project target update mismatch")
    assert_true(updated_project["modality"] == UPDATED_MODALITY, "Project modality update mismatch")
    assert_true(updated_project["calibration_profile"] == UPDATED_CALIBRATION_PROFILE, "Project calibration update mismatch")
    assert_true(updated_project["runtime_mode"] == UPDATED_RUNTIME_MODE, "Project runtime update mismatch")
    project_run_3 = request_json(
        endpoint(f"/projects/{project_id}/runs?model_id={model_id}"),
        method="POST",
        data=b"",
    )
    assert_true(project_run_3["project"]["target_profile"] == UPDATED_TARGET_PROFILE, "Updated project run target mismatch")
    assert_true(project_run_3["run"]["target_profile"] == UPDATED_TARGET_PROFILE, "Updated run target mismatch")
    assert_true(project_run_3["run"]["modality"] == UPDATED_MODALITY, "Updated run modality mismatch")
    assert_true(project_run_3["run"]["runtime_mode"] == UPDATED_RUNTIME_MODE, "Updated run runtime mode mismatch")
    updated_comparison = request_json(endpoint(f"/projects/{project_id}/runs/compare"))
    assert_true(any(item["run_id"] == project_run_3["run_id"] for item in updated_comparison["rows"]), "Updated run missing from comparison")
    assert_true(any(item["target_profile"] == UPDATED_TARGET_PROFILE for item in updated_comparison["rows"]), "Updated target missing from comparison")

    archive_data = request_bytes(endpoint(model_query(model_id, "/deployment-package/archive") + f"&project_id={project_id}"))
    archive = zipfile.ZipFile(io.BytesIO(archive_data))
    names = set(archive.namelist())
    required = {
        "README.txt",
        "manifest.json",
        "package-readiness.json",
        "analysis.json",
        "quantization-report.json",
        "runtime-profile.json",
        "baseline-comparison.json",
        "workload-fit.json",
        "system-boundary.json",
        "physical-ai-map.json",
        "physical-ai-roadmap.json",
        "vla-readiness.json",
        "weight-update-readiness.json",
        "calibration-drift-readiness.json",
        "control-boundary.json",
        "sensor-boundary-readiness.json",
        "research-guide.json",
        "concept-glossary.json",
        "source-check-register.json",
        "measurement-evidence.json",
        "toolchain-readiness.json",
        "compiler-ecosystem-readiness.json",
        "connection-playbook.json",
        "adapter-execution-plan.json",
        "adapter-connection-kit.json",
        "adapter-evidence-templates.json",
        "adapter-connection-self-test.json",
        "adapter-integration-readiness.json",
        "external-connector-contract.json",
        "connector-implementation-guide.json",
        "connector-test-harness.json",
        "connector-acceptance-drills.json",
        "connector-acceptance-report.json",
        "connector-backlog.json",
        "connector-delivery-plan.json",
        "connector-risk-register.json",
        "adapter-registry.json",
        "evidence-gates.json",
        "claim-readiness.json",
        "evidence-audit.json",
        "evidence-brief.json",
        "evidence-brief.md",
        "interview-brief.json",
        "interview-brief.md",
        "interview-drill.json",
        "decision-report.json",
        "rewrite-suggestions.json",
        "rewrite-what-if.json",
        "rewrite-plan.json",
        "rewrite-work-order.json",
        "review-report.json",
        "review-report.md",
        "imported-evidence/index.json",
        "adapter-runs/index.json",
        "source-model.onnx",
    }
    missing = sorted(required - names)
    assert_true(not missing, f"Archive missing files: {missing}")
    imported_archive_files = [
        name for name in names
        if name.startswith("imported-evidence/") and name.endswith(".json") and name != "imported-evidence/index.json"
    ]
    assert_true(len(imported_archive_files) == full_imported_list["count"], "Archive imported evidence file count mismatch")
    imported_index = json.loads(archive.read("imported-evidence/index.json"))
    assert_true(len(imported_index) == full_imported_list["count"], "Archive imported evidence index count mismatch")
    adapter_run_archive_files = [
        name for name in names
        if name.startswith("adapter-runs/") and name.endswith(".json") and name != "adapter-runs/index.json"
    ]
    assert_true(len(adapter_run_archive_files) == refreshed_adapter_run_list["count"], "Archive adapter run file count mismatch")
    adapter_run_index = json.loads(archive.read("adapter-runs/index.json"))
    assert_true(len(adapter_run_index) == refreshed_adapter_run_list["count"], "Archive adapter run index count mismatch")
    assert_true(any(item["adapter_id"] == "board.runtime" for item in adapter_run_index), "Archive adapter run index missing board runtime")
    archived_audit = json.loads(archive.read("evidence-audit.json"))
    assert_true(archived_audit["summary"]["total_imports"] == full_imported_list["count"], "Archive evidence audit import count mismatch")
    archived_workload = json.loads(archive.read("workload-fit.json"))
    assert_true(archived_workload["result_type"] == "workload_fit_matrix", "Archive workload fit result type mismatch")
    archived_boundary = json.loads(archive.read("system-boundary.json"))
    assert_true(archived_boundary["result_type"] == "system_boundary_report", "Archive system boundary result type mismatch")
    archived_physical_ai = json.loads(archive.read("physical-ai-map.json"))
    assert_true(archived_physical_ai["result_type"] == "physical_ai_map", "Archive Physical AI map result type mismatch")
    assert_true(archived_physical_ai["source_check_policy"]["status"] == "conceptual_map_only", "Archive Physical AI source policy mismatch")
    archived_physical_ai_roadmap = json.loads(archive.read("physical-ai-roadmap.json"))
    assert_true(archived_physical_ai_roadmap["result_type"] == "physical_ai_roadmap", "Archive Physical AI roadmap result type mismatch")
    assert_true(any(gate["id"] == "compiler_fit" for gate in archived_physical_ai_roadmap["gates"]), "Archive Physical AI roadmap missing compiler gate")
    archived_vla = json.loads(archive.read("vla-readiness.json"))
    assert_true(archived_vla["result_type"] == "vla_readiness", "Archive VLA readiness result type mismatch")
    archived_weight_update = json.loads(archive.read("weight-update-readiness.json"))
    assert_true(archived_weight_update["result_type"] == "weight_update_readiness", "Archive weight update readiness result type mismatch")
    archived_calibration_drift = json.loads(archive.read("calibration-drift-readiness.json"))
    assert_true(archived_calibration_drift["result_type"] == "calibration_drift_readiness", "Archive calibration drift readiness result type mismatch")
    archived_control_boundary = json.loads(archive.read("control-boundary.json"))
    assert_true(archived_control_boundary["result_type"] == "control_boundary", "Archive control boundary result type mismatch")
    archived_sensor_boundary = json.loads(archive.read("sensor-boundary-readiness.json"))
    assert_true(archived_sensor_boundary["result_type"] == "sensor_boundary_readiness", "Archive sensor boundary result type mismatch")
    archived_research = json.loads(archive.read("research-guide.json"))
    assert_true(archived_research["result_type"] == "research_guide", "Archive research guide result type mismatch")
    archived_glossary = json.loads(archive.read("concept-glossary.json"))
    assert_true(archived_glossary["result_type"] == "concept_glossary", "Archive concept glossary result type mismatch")
    archived_source_check = json.loads(archive.read("source-check-register.json"))
    assert_true(archived_source_check["result_type"] == "source_check_register", "Archive source-check register result type mismatch")
    archived_toolchain = json.loads(archive.read("toolchain-readiness.json"))
    assert_true(archived_toolchain["result_type"] == "toolchain_readiness", "Archive toolchain readiness result type mismatch")
    archived_compiler_ecosystem = json.loads(archive.read("compiler-ecosystem-readiness.json"))
    assert_true(archived_compiler_ecosystem["result_type"] == "compiler_ecosystem_readiness", "Archive compiler ecosystem result type mismatch")
    archived_connection = json.loads(archive.read("connection-playbook.json"))
    assert_true(archived_connection["result_type"] == "connection_playbook", "Archive connection playbook result type mismatch")
    archived_adapter_execution = json.loads(archive.read("adapter-execution-plan.json"))
    assert_true(archived_adapter_execution["result_type"] == "adapter_execution_plan", "Archive adapter execution plan result type mismatch")
    archived_adapter_connection_kit = json.loads(archive.read("adapter-connection-kit.json"))
    assert_true(archived_adapter_connection_kit["result_type"] == "adapter_connection_kit", "Archive adapter connection kit result type mismatch")
    archived_adapter_templates = json.loads(archive.read("adapter-evidence-templates.json"))
    assert_true(archived_adapter_templates["result_type"] == "adapter_evidence_templates", "Archive adapter evidence templates result type mismatch")
    archived_adapter_self_test = json.loads(archive.read("adapter-connection-self-test.json"))
    assert_true(archived_adapter_self_test["result_type"] == "adapter_connection_self_test", "Archive adapter connection self-test result type mismatch")
    archived_adapter_integration = json.loads(archive.read("adapter-integration-readiness.json"))
    assert_true(archived_adapter_integration["result_type"] == "adapter_integration_readiness", "Archive adapter integration readiness result type mismatch")
    archived_external_connector = json.loads(archive.read("external-connector-contract.json"))
    assert_true(archived_external_connector["result_type"] == "external_connector_contract", "Archive external connector contract result type mismatch")
    archived_connector_guide = json.loads(archive.read("connector-implementation-guide.json"))
    assert_true(archived_connector_guide["result_type"] == "connector_implementation_guide", "Archive connector implementation guide result type mismatch")
    archived_connector_harness = json.loads(archive.read("connector-test-harness.json"))
    assert_true(archived_connector_harness["result_type"] == "connector_test_harness", "Archive connector test harness result type mismatch")
    archived_connector_acceptance = json.loads(archive.read("connector-acceptance-report.json"))
    assert_true(archived_connector_acceptance["result_type"] == "connector_acceptance_report", "Archive connector acceptance report result type mismatch")
    archived_connector_drills = json.loads(archive.read("connector-acceptance-drills.json"))
    assert_true(archived_connector_drills["result_type"] == "connector_acceptance_drills", "Archive connector acceptance drills result type mismatch")
    archived_connector_backlog = json.loads(archive.read("connector-backlog.json"))
    assert_true(archived_connector_backlog["result_type"] == "connector_backlog", "Archive connector backlog result type mismatch")
    archived_connector_delivery = json.loads(archive.read("connector-delivery-plan.json"))
    assert_true(archived_connector_delivery["result_type"] == "connector_delivery_plan", "Archive connector delivery plan result type mismatch")
    archived_connector_risk = json.loads(archive.read("connector-risk-register.json"))
    assert_true(archived_connector_risk["result_type"] == "connector_risk_register", "Archive connector risk register result type mismatch")
    archived_brief = json.loads(archive.read("evidence-brief.json"))
    assert_true(archived_brief["result_type"] == "evidence_brief", "Archive evidence brief result type mismatch")
    assert_true("Production readiness remains blocked" in archive.read("evidence-brief.md").decode("utf-8"), "Archive evidence brief markdown missing production warning")
    archived_interview = json.loads(archive.read("interview-brief.json"))
    assert_true(archived_interview["result_type"] == "interview_brief", "Archive interview brief result type mismatch")
    assert_true("Questions To Ask" in archive.read("interview-brief.md").decode("utf-8"), "Archive interview brief markdown missing questions")
    archived_drill = json.loads(archive.read("interview-drill.json"))
    assert_true(archived_drill["result_type"] == "interview_drill", "Archive interview drill result type mismatch")
    manifest = json.loads(archive.read("manifest.json"))
    assert_true(manifest["summary"]["project_id"] == project_id, "Archive manifest project context missing")

    saved_package = request_json(endpoint(saved["package_report"]))
    assert_true(saved_package["package_id"] == package["package_id"], "Saved package retrieval mismatch")
    saved_artifact_bundle = request_json(endpoint(f"/deployment-packages/{package['package_id']}/artifacts"))
    assert_true(saved_artifact_bundle["result_type"] == "saved_package_artifacts", "Saved artifact bundle result type mismatch")
    assert_true(saved_artifact_bundle["artifacts"]["analysis"]["layers"], "Saved artifact bundle missing analysis")
    assert_true(saved_artifact_bundle["artifacts"]["runtime"]["summary"]["latency_ms"] > 0, "Saved artifact bundle missing runtime")
    assert_true(saved_artifact_bundle["artifacts"]["workload_fit"]["result_type"] == "workload_fit_matrix", "Saved artifact bundle missing workload fit")
    assert_true(saved_artifact_bundle["artifacts"]["physical_ai_map"]["result_type"] == "physical_ai_map", "Saved artifact bundle missing Physical AI map")
    assert_true(saved_artifact_bundle["artifacts"]["vla_readiness"]["result_type"] == "vla_readiness", "Saved artifact bundle missing VLA readiness")
    assert_true(saved_artifact_bundle["artifacts"]["weight_update_readiness"]["result_type"] == "weight_update_readiness", "Saved artifact bundle missing weight update readiness")
    assert_true(saved_artifact_bundle["artifacts"]["calibration_drift_readiness"]["result_type"] == "calibration_drift_readiness", "Saved artifact bundle missing calibration drift readiness")
    assert_true(saved_artifact_bundle["artifacts"]["control_boundary"]["result_type"] == "control_boundary", "Saved artifact bundle missing control boundary")
    assert_true(saved_artifact_bundle["artifacts"]["sensor_boundary_readiness"]["result_type"] == "sensor_boundary_readiness", "Saved artifact bundle missing sensor boundary")
    assert_true(saved_artifact_bundle["artifacts"]["adapter_execution_plan"]["result_type"] == "adapter_execution_plan", "Saved artifact bundle missing adapter execution plan")
    assert_true(saved_artifact_bundle["artifacts"]["adapter_connection_kit"]["result_type"] == "adapter_connection_kit", "Saved artifact bundle missing adapter connection kit")
    assert_true(saved_artifact_bundle["artifacts"]["adapter_evidence_templates"]["result_type"] == "adapter_evidence_templates", "Saved artifact bundle missing adapter evidence templates")
    assert_true(saved_artifact_bundle["artifacts"]["adapter_connection_self_test"]["result_type"] == "adapter_connection_self_test", "Saved artifact bundle missing adapter connection self-test")
    assert_true(saved_artifact_bundle["artifacts"]["adapter_integration_readiness"]["result_type"] == "adapter_integration_readiness", "Saved artifact bundle missing adapter integration readiness")
    assert_true(saved_artifact_bundle["artifacts"]["external_connector_contract"]["result_type"] == "external_connector_contract", "Saved artifact bundle missing external connector contract")
    assert_true(saved_artifact_bundle["artifacts"]["connector_implementation_guide"]["result_type"] == "connector_implementation_guide", "Saved artifact bundle missing connector implementation guide")
    assert_true(saved_artifact_bundle["artifacts"]["connector_test_harness"]["result_type"] == "connector_test_harness", "Saved artifact bundle missing connector test harness")
    assert_true(saved_artifact_bundle["artifacts"]["connector_acceptance_report"]["result_type"] == "connector_acceptance_report", "Saved artifact bundle missing connector acceptance report")
    assert_true(saved_artifact_bundle["artifacts"]["connector_acceptance_drills"]["result_type"] == "connector_acceptance_drills", "Saved artifact bundle missing connector acceptance drills")
    assert_true(saved_artifact_bundle["artifacts"]["connector_backlog"]["result_type"] == "connector_backlog", "Saved artifact bundle missing connector backlog")
    assert_true(saved_artifact_bundle["artifacts"]["connector_delivery_plan"]["result_type"] == "connector_delivery_plan", "Saved artifact bundle missing connector delivery plan")
    assert_true(saved_artifact_bundle["artifacts"]["connector_risk_register"]["result_type"] == "connector_risk_register", "Saved artifact bundle missing connector risk register")
    assert_true(saved_artifact_bundle["artifacts"]["system_boundary"]["result_type"] == "system_boundary_report", "Saved artifact bundle missing system boundary")
    assert_true(saved_artifact_bundle["artifacts"]["research"]["result_type"] == "research_guide", "Saved artifact bundle missing research guide")
    assert_true(saved_artifact_bundle["artifacts"]["glossary"]["result_type"] == "concept_glossary", "Saved artifact bundle missing concept glossary")
    assert_true(saved_artifact_bundle["artifacts"]["source_check_register"]["result_type"] == "source_check_register", "Saved artifact bundle missing source-check register")
    assert_true(saved_artifact_bundle["artifacts"]["physical_ai_roadmap"]["result_type"] == "physical_ai_roadmap", "Saved artifact bundle missing Physical AI roadmap")
    assert_true(saved_artifact_bundle["artifacts"]["toolchain"]["result_type"] == "toolchain_readiness", "Saved artifact bundle missing toolchain readiness")
    assert_true(saved_artifact_bundle["artifacts"]["compiler_ecosystem_readiness"]["result_type"] == "compiler_ecosystem_readiness", "Saved artifact bundle missing compiler ecosystem")
    assert_true(saved_artifact_bundle["artifacts"]["connection_playbook"]["result_type"] == "connection_playbook", "Saved artifact bundle missing connection playbook")
    assert_true(saved_artifact_bundle["artifacts"]["measurement"]["result_type"] == "measurement_evidence", "Saved artifact bundle missing measurement evidence")
    assert_true(saved_artifact_bundle["artifacts"]["decision"]["result_type"] == "decision_report", "Saved artifact bundle missing decision")
    assert_true(saved_artifact_bundle["artifacts"]["rewrites"]["result_type"] == "rewrite_suggestions", "Saved artifact bundle missing rewrites")
    assert_true(saved_artifact_bundle["artifacts"]["rewrite_what_if"]["result_type"] == "rewrite_what_if", "Saved artifact bundle missing rewrite what-if")
    assert_true(saved_artifact_bundle["artifacts"]["rewrite_plan"]["result_type"] == "rewrite_plan", "Saved artifact bundle missing rewrite plan")
    assert_true(saved_artifact_bundle["artifacts"]["rewrite_work_order"]["result_type"] == "rewrite_work_order", "Saved artifact bundle missing rewrite work order")
    assert_true(saved_artifact_bundle["artifacts"]["interview_drill"]["result_type"] == "interview_drill", "Saved artifact bundle missing interview drill")
    saved_decision = request_json(endpoint(f"/deployment-packages/{package['package_id']}/decision-report"))
    assert_true(saved_decision["decision"] == saved_artifact_bundle["artifacts"]["decision"]["decision"], "Saved decision retrieval mismatch")
    saved_measurement = request_json(endpoint(f"/deployment-packages/{package['package_id']}/measurement-evidence"))
    assert_true(saved_measurement["summary"]["imported_sources"] == 5, "Saved measurement evidence retrieval mismatch")
    saved_physical_ai = request_json(endpoint(f"/deployment-packages/{package['package_id']}/physical-ai-map"))
    assert_true(saved_physical_ai["selected_domain"] == saved_artifact_bundle["artifacts"]["physical_ai_map"]["selected_domain"], "Saved Physical AI map retrieval mismatch")
    saved_physical_ai_roadmap = request_json(endpoint(f"/deployment-packages/{package['package_id']}/physical-ai-roadmap"))
    assert_true(saved_physical_ai_roadmap["result_type"] == "physical_ai_roadmap", "Saved Physical AI roadmap retrieval mismatch")
    saved_vla = request_json(endpoint(f"/deployment-packages/{package['package_id']}/vla-readiness"))
    assert_true(saved_vla["claim_level"] == saved_artifact_bundle["artifacts"]["vla_readiness"]["claim_level"], "Saved VLA readiness retrieval mismatch")
    saved_weight_update = request_json(endpoint(f"/deployment-packages/{package['package_id']}/weight-update-readiness"))
    assert_true(saved_weight_update["readiness"] == saved_artifact_bundle["artifacts"]["weight_update_readiness"]["readiness"], "Saved weight update readiness retrieval mismatch")
    saved_calibration_drift = request_json(endpoint(f"/deployment-packages/{package['package_id']}/calibration-drift-readiness"))
    assert_true(saved_calibration_drift["readiness"] == saved_artifact_bundle["artifacts"]["calibration_drift_readiness"]["readiness"], "Saved calibration drift readiness retrieval mismatch")
    saved_control_boundary = request_json(endpoint(f"/deployment-packages/{package['package_id']}/control-boundary"))
    assert_true(saved_control_boundary["readiness"] == saved_artifact_bundle["artifacts"]["control_boundary"]["readiness"], "Saved control boundary retrieval mismatch")
    saved_sensor_boundary = request_json(endpoint(f"/deployment-packages/{package['package_id']}/sensor-boundary-readiness"))
    assert_true(saved_sensor_boundary["readiness"] == saved_artifact_bundle["artifacts"]["sensor_boundary_readiness"]["readiness"], "Saved sensor boundary retrieval mismatch")
    saved_compiler_ecosystem = request_json(endpoint(f"/deployment-packages/{package['package_id']}/compiler-ecosystem-readiness"))
    assert_true(saved_compiler_ecosystem["readiness"] == saved_artifact_bundle["artifacts"]["compiler_ecosystem_readiness"]["readiness"], "Saved compiler ecosystem retrieval mismatch")
    saved_source_check = request_json(endpoint(f"/deployment-packages/{package['package_id']}/source-check-register"))
    assert_true(saved_source_check["summary"]["checked_items"] == saved_artifact_bundle["artifacts"]["source_check_register"]["summary"]["checked_items"], "Saved source-check retrieval mismatch")
    saved_claim_readiness = request_json(endpoint(f"/deployment-packages/{package['package_id']}/claim-readiness"))
    assert_true(saved_claim_readiness["summary"]["supported_lab_claims"] == 4, "Saved claim readiness retrieval mismatch")
    saved_brief = request_json(endpoint(f"/deployment-packages/{package['package_id']}/evidence-brief"))
    assert_true(saved_brief["summary"]["production_readiness"] == "blocked", "Saved evidence brief retrieval mismatch")
    saved_interview = request_json(endpoint(f"/deployment-packages/{package['package_id']}/interview-brief"))
    assert_true(saved_interview["summary"]["production_readiness"] == "blocked", "Saved interview brief retrieval mismatch")
    saved_rewrites = request_json(endpoint(f"/deployment-packages/{package['package_id']}/rewrite-suggestions"))
    assert_true(saved_rewrites["focus"] == saved_artifact_bundle["artifacts"]["rewrites"]["focus"], "Saved rewrites retrieval mismatch")
    saved_what_if = request_json(endpoint(f"/deployment-packages/{package['package_id']}/rewrite-what-if?suggestion_ids={first_rewrite_id}"))
    assert_true(saved_what_if["result_type"] == "rewrite_what_if", "Saved rewrite what-if result type mismatch")
    assert_true(saved_what_if["selected_suggestion_ids"] == what_if["selected_suggestion_ids"], "Saved rewrite what-if selected suggestion mismatch")
    saved_rewrite_plan = request_json(endpoint(f"/deployment-packages/{package['package_id']}/rewrite-plan?suggestion_ids={first_rewrite_id}"))
    assert_true(saved_rewrite_plan["result_type"] == "rewrite_plan", "Saved rewrite plan result type mismatch")
    assert_true(saved_rewrite_plan["selected_actions"][0]["suggestion_id"] == first_rewrite_id, "Saved rewrite plan selected suggestion mismatch")
    saved_work_order = request_json(endpoint(f"/deployment-packages/{package['package_id']}/rewrite-work-order?suggestion_ids={first_rewrite_id}"))
    assert_true(saved_work_order["result_type"] == "rewrite_work_order", "Saved rewrite work order result type mismatch")
    assert_true(saved_work_order["tasks"][0]["layer_id"] == work_order["tasks"][0]["layer_id"], "Saved rewrite work order task mismatch")
    packages = request_json(endpoint("/deployment-packages"))["packages"]
    assert_true(any(item["package_id"] == package["package_id"] for item in packages), "Saved package missing from package list")
    saved_project = request_json(endpoint(f"/projects/{project_id}"))
    assert_true(package["package_id"] in saved_project["package_ids"], "Saved package missing from project")
    assert_true(project_run["package_id"] in saved_project["package_ids"], "Project run package missing from project")
    assert_true(project_run_2["package_id"] in saved_project["package_ids"], "Second project run package missing from project")
    assert_true(project_run_3["package_id"] in saved_project["package_ids"], "Updated project run package missing from project")
    assert_true(project_run["run_id"] in saved_project["run_ids"], "Project run ID missing from project")
    assert_true(project_run_2["run_id"] in saved_project["run_ids"], "Second project run ID missing from project")
    assert_true(project_run_3["run_id"] in saved_project["run_ids"], "Updated project run ID missing from project")
    saved_review_md = request_bytes(endpoint(saved["review_markdown"])).decode("utf-8")
    assert_true("What To Say Clearly" in saved_review_md, "Saved review markdown missing expected section")
    assert_true(f"Project ID: {project_id}" in saved_review_md, "Saved review markdown missing project ID")
    saved_archive_data = request_bytes(endpoint(saved["archive"]))
    saved_archive = zipfile.ZipFile(io.BytesIO(saved_archive_data))
    assert_true(set(saved_archive.namelist()) == names, "Saved archive contents differ from generated archive")

    print(
        "smoke-ok",
        project_id,
        model_id,
        package["package_id"],
        f"project_run={project_run['package_id']}",
        f"run_id={project_run['run_id']}",
        f"compare_runs={comparison['run_count']}",
        f"updated_run={project_run_3['run_id']}",
        f"decision={decision['decision']}",
        f"rewrites={rewrites['summary']['suggestion_count']}",
        f"what_if_energy_delta={what_if['deltas']['energy_uj']}",
        f"rewrite_plan_actions={rewrite_plan['summary']['selected_action_count']}",
        f"work_order_tasks={len(work_order['tasks'])}",
        f"measurement_sources={len(measurement['required_sources'])}",
        f"imported_sources={full_measurement['summary']['imported_sources']}",
        f"supported_claims={full_claim_readiness['summary']['supported_lab_claims']}",
        f"layers={len(analysis['layers'])}",
        f"latency_ms={runtime['summary']['latency_ms']}",
        f"energy_uj={runtime['summary']['energy_uj']}",
        f"gates={gates['summary']}",
        f"archive_files={len(names)}",
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"smoke-failed {exc}", file=sys.stderr)
        raise
