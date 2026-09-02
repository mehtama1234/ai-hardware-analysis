import json
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from adapter_runs import run_adapter
from adapter_connection_kit import build_adapter_connection_kit
from adapter_connection_self_test import build_adapter_connection_self_test
from adapter_evidence_templates import build_adapter_evidence_templates
from adapter_execution_plan import build_adapter_execution_plan
from adapter_integration_readiness import build_adapter_integration_readiness
from adapters import adapter_probe, adapter_registry
from baseline_comparison import compare_to_digital_baseline
from calibration import get_calibration_profile, list_calibration_profiles
from calibration_drift_readiness import build_calibration_drift_readiness
from claim_readiness import build_claim_readiness
from compiler_ecosystem_readiness import build_compiler_ecosystem_readiness
from concept_glossary import build_concept_glossary
from control_boundary import build_control_boundary
from connector_acceptance_report import build_connector_acceptance_report
from connector_acceptance_drills import build_connector_acceptance_drills
from connector_backlog import build_connector_backlog
from connector_delivery_plan import build_connector_delivery_plan
from connector_implementation_guide import build_connector_implementation_guide
from connector_risk_register import build_connector_risk_register
from connector_test_harness import build_connector_test_harness
from connection_playbook import build_connection_playbook
from decision_report import build_decision_report
from deployment_package import build_deployment_archive, build_deployment_package
from evidence_brief import build_evidence_brief
from evidence_imports import build_import_record, build_measured_readiness_report, build_tool_readiness_report, build_validation_report, validate_imported_evidence
from evidence_gates import build_evidence_gates
from external_connector_contract import build_external_connector_contract
from hardware_placement import build_hardware_placement
from hardware_profile import TARGET_PROFILES
from interview_brief import build_interview_brief
from interview_drill import build_interview_drill
from measurement_evidence import build_measurement_evidence
from model_store import ModelStore
from onnx_analyzer import analyze_model
from physical_ai_map import build_physical_ai_map
from physical_ai_roadmap import build_physical_ai_roadmap
from quantization import estimate_quantization, modality_profiles
from review_report import build_review_report
from residual_aware_placement import load_residual_aware_placement
from research_guide import build_research_guide
from rewrite_plan import build_rewrite_plan
from rewrite_suggestions import build_rewrite_suggestions
from rewrite_work_order import build_rewrite_work_order
from rewrite_whatif import build_rewrite_what_if
from runtime_profile import run_simulated_profile, runtime_modes
from roadmap_demo_package import load_demo_review_artifact, load_demo_review_package
from roadmap_journey import load_roadmap_journey
from sensor_boundary_readiness import build_sensor_boundary_readiness
from source_check_register import build_source_check_register
from system_boundary import build_system_boundary_report
from toolchain_readiness import build_toolchain_readiness
from vla_transformer_readiness import build_vla_readiness
from weight_update_readiness import build_weight_update_readiness
from workload_fit import build_workload_fit_matrix


BASE_DIR = Path(__file__).resolve().parent
STORE = ModelStore(BASE_DIR / ".data")
LOCAL_EVIDENCE_ADAPTERS = [
    ("compiler.tvm-mlir-iree", "compiler_mapping"),
    ("analog.error-simulator", "analog_error_simulation"),
    ("accuracy.local-task-check", "task_accuracy"),
    ("board.runtime", "board_runtime"),
    ("metrics.power-thermal", "power_thermal"),
]
LOCAL_EVIDENCE_TOOLS = {
    "local-placement-adapter",
    "local-analog-error-adapter",
    "local-task-accuracy-adapter",
    "local-board-runtime-adapter",
    "local-power-thermal-adapter",
}
HARDWARE_LAB_EVIDENCE_BATCH = (
    BASE_DIR.parents[3]
    / "analog-digital-chip-design-eda"
    / "evidence"
    / "aimc-hardware-lab"
    / "import-batch.json"
)
HARDWARE_LAB_STRICT_TOOL_EVIDENCE = HARDWARE_LAB_EVIDENCE_BATCH.parent / "analog_error_simulation_strict_tool.json"

app = FastAPI(title="Analog AI Model-Fit Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def project_context_or_404(project_id):
    if not project_id:
        return None
    project = STORE.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Unknown project_id.")
    return project


def validate_project_settings(target_profile, modality, calibration_profile, runtime_mode):
    if target_profile not in TARGET_PROFILES:
        raise HTTPException(status_code=400, detail=f"Unknown target_profile: {target_profile}")
    if modality not in modality_profiles():
        raise HTTPException(status_code=400, detail=f"Unknown modality: {modality}")
    if calibration_profile not in list_calibration_profiles():
        raise HTTPException(status_code=400, detail=f"Unknown calibration_profile: {calibration_profile}")
    if runtime_mode not in runtime_modes():
        raise HTTPException(status_code=400, detail=f"Unknown runtime_mode: {runtime_mode}")


def package_id_from_package_or_run(package_id=None, run_id=None):
    if package_id:
        if not STORE.get_package_metadata(package_id):
            raise HTTPException(status_code=404, detail="Unknown package_id.")
        return package_id, None
    if run_id:
        run = STORE.get_project_run(run_id)
        if not run:
            raise HTTPException(status_code=404, detail="Unknown run_id.")
        return run.get("package_id"), run
    raise HTTPException(status_code=400, detail="Provide package_id or run_id.")


def current_package_measurement_or_404(package_id):
    bundle = STORE.get_package_artifacts(package_id)
    if not bundle:
        raise HTTPException(status_code=404, detail="Unknown package_id or missing measurement evidence.")
    artifacts = bundle["artifacts"]
    imported = STORE.list_imported_evidence(package_id) or []
    measurement = build_measurement_evidence(
        artifacts["adapters"],
        runtime_profile=artifacts["runtime"],
        baseline_report=artifacts["baseline"],
        package_report=artifacts["package"],
        imported_evidence=imported,
    )
    return artifacts, measurement


def build_artifact_bundle(record, model_id, target_profile, calibration_profile, modality, runtime_mode, project_context=None):
    adapter_report = adapter_registry()
    analysis = analyze_model(record["path"], target_profile=target_profile, calibration_profile=calibration_profile)
    quantization_report = estimate_quantization(analysis, modality=modality)
    runtime_report = run_simulated_profile(
        analysis,
        quantization_report=quantization_report,
        runtime_mode=runtime_mode,
    )
    package_report = build_deployment_package(
        model_id,
        analysis,
        quantization_report,
        runtime_report,
        target_profile=target_profile,
        calibration_profile=calibration_profile,
        modality=modality,
        runtime_mode=runtime_mode,
        project_context=project_context,
    )
    baseline_report = compare_to_digital_baseline(analysis, runtime_report, target_profile=target_profile)
    hardware_placement = build_hardware_placement(analysis, package_report=package_report)
    workload_fit = build_workload_fit_matrix(
        analysis,
        quantization_report,
        runtime_report,
        target_profile=target_profile,
        modality=modality,
    )
    system_boundary = build_system_boundary_report(analysis, runtime_report, package_report=package_report)
    research_guide = build_research_guide(package_report)
    concept_glossary = build_concept_glossary(package_report)
    source_check_register = build_source_check_register(package_report)
    measurement_report = build_measurement_evidence(
        adapter_report,
        runtime_profile=runtime_report,
        baseline_report=baseline_report,
        package_report=package_report,
    )
    toolchain_report = build_toolchain_readiness(
        adapter_report,
        measurement_report,
        package_report=package_report,
    )
    physical_ai_map = build_physical_ai_map(
        package_report,
        workload_fit=workload_fit,
        system_boundary=system_boundary,
        measurement_evidence=measurement_report,
    )
    vla_readiness = build_vla_readiness(
        analysis,
        quantization_report,
        runtime_report,
        system_boundary,
        package_report=package_report,
    )
    weight_update_readiness = build_weight_update_readiness(
        package_report,
        vla_readiness=vla_readiness,
        measurement_evidence=measurement_report,
    )
    calibration_drift_readiness = build_calibration_drift_readiness(
        package_report,
        analysis,
        measurement_evidence=measurement_report,
    )
    control_boundary = build_control_boundary(
        package_report,
        physical_ai_map=physical_ai_map,
        runtime_profile=runtime_report,
        system_boundary=system_boundary,
        measurement_evidence=measurement_report,
    )
    sensor_boundary_readiness = build_sensor_boundary_readiness(
        package_report,
        physical_ai_map=physical_ai_map,
        runtime_profile=runtime_report,
        system_boundary=system_boundary,
        measurement_evidence=measurement_report,
    )
    connection_playbook = build_connection_playbook(
        adapter_report,
        measurement_report,
        toolchain_readiness=toolchain_report,
        package_report=package_report,
    )
    adapter_execution_plan = build_adapter_execution_plan(
        adapter_report,
        measurement_report,
        connection_playbook=connection_playbook,
        package_report=package_report,
    )
    adapter_connection_kit = build_adapter_connection_kit(
        adapter_report,
        measurement_report,
        adapter_execution_plan=adapter_execution_plan,
        package_report=package_report,
    )
    adapter_evidence_templates = build_adapter_evidence_templates(
        adapter_report,
        measurement_report,
        adapter_connection_kit=adapter_connection_kit,
        package_report=package_report,
    )
    adapter_connection_self_test = build_adapter_connection_self_test(
        adapter_report,
        adapter_probe,
        adapter_connection_kit=adapter_connection_kit,
        package_report=package_report,
    )
    adapter_integration_readiness = build_adapter_integration_readiness(
        adapter_execution_plan,
        adapter_connection_kit,
        adapter_evidence_templates,
        adapter_connection_self_test,
        package_report=package_report,
    )
    external_connector_contract = build_external_connector_contract(
        adapter_connection_kit,
        adapter_integration_readiness,
        package_report=package_report,
    )
    compiler_ecosystem_readiness = build_compiler_ecosystem_readiness(
        adapter_report,
        external_connector_contract,
        connection_playbook,
        analysis,
        package_report=package_report,
        toolchain_readiness=toolchain_report,
        measurement_evidence=measurement_report,
    )
    connector_implementation_guide = build_connector_implementation_guide(
        external_connector_contract,
        adapter_integration_readiness=adapter_integration_readiness,
        package_report=package_report,
    )
    connector_test_harness = build_connector_test_harness(
        connector_implementation_guide,
        package_report=package_report,
    )
    connector_acceptance_drills = build_connector_acceptance_drills(
        connector_test_harness,
        imported_evidence=[],
        package_report=package_report,
    )
    connector_acceptance_report = build_connector_acceptance_report(
        connector_test_harness,
        adapter_connection_self_test,
        measurement_report,
        connector_acceptance_drills=connector_acceptance_drills,
        package_report=package_report,
    )
    connector_backlog = build_connector_backlog(
        connector_acceptance_report,
        package_report=package_report,
    )
    connector_delivery_plan = build_connector_delivery_plan(
        connector_backlog,
        package_report=package_report,
    )
    connector_risk_register = build_connector_risk_register(
        connector_delivery_plan,
        package_report=package_report,
    )
    evidence_report = build_evidence_gates(
        analysis,
        quantization_report,
        runtime_report,
        baseline_report,
        package_report,
        adapter_report,
        measurement_report,
    )
    review = build_review_report(
        analysis,
        quantization_report,
        runtime_report,
        baseline_report,
        package_report,
        evidence_report,
        adapter_report,
    )
    decision = build_decision_report(
        analysis,
        runtime_report,
        baseline_report,
        package_report,
        evidence_report,
        adapter_report,
    )
    rewrites = build_rewrite_suggestions(
        analysis,
        quantization_report=quantization_report,
        runtime_profile=runtime_report,
        decision_report=decision,
    )
    rewrite_what_if = build_rewrite_what_if(
        analysis,
        runtime_report,
        decision,
        rewrites,
    )
    rewrite_plan = build_rewrite_plan(
        analysis,
        quantization_report,
        runtime_report,
        decision,
        rewrites,
        rewrite_what_if,
    )
    rewrite_work_order = build_rewrite_work_order(
        analysis,
        rewrite_plan,
        project_context=project_context,
    )
    return {
        "analysis": analysis,
        "quantization": quantization_report,
        "runtime": runtime_report,
        "package": package_report,
        "baseline": baseline_report,
        "hardware_placement": hardware_placement,
        "workload_fit": workload_fit,
        "system_boundary": system_boundary,
        "physical_ai_map": physical_ai_map,
        "vla_readiness": vla_readiness,
        "weight_update_readiness": weight_update_readiness,
        "calibration_drift_readiness": calibration_drift_readiness,
        "control_boundary": control_boundary,
        "sensor_boundary_readiness": sensor_boundary_readiness,
        "research": research_guide,
        "glossary": concept_glossary,
        "source_check_register": source_check_register,
        "measurement": measurement_report,
        "toolchain": toolchain_report,
        "connection_playbook": connection_playbook,
        "adapter_execution_plan": adapter_execution_plan,
        "adapter_connection_kit": adapter_connection_kit,
        "adapter_evidence_templates": adapter_evidence_templates,
        "adapter_connection_self_test": adapter_connection_self_test,
        "adapter_integration_readiness": adapter_integration_readiness,
        "external_connector_contract": external_connector_contract,
        "compiler_ecosystem_readiness": compiler_ecosystem_readiness,
        "connector_implementation_guide": connector_implementation_guide,
        "connector_test_harness": connector_test_harness,
        "connector_acceptance_drills": connector_acceptance_drills,
        "connector_acceptance_report": connector_acceptance_report,
        "connector_backlog": connector_backlog,
        "connector_delivery_plan": connector_delivery_plan,
        "connector_risk_register": connector_risk_register,
        "evidence": evidence_report,
        "review": review,
        "decision": decision,
        "rewrites": rewrites,
        "rewrite_what_if": rewrite_what_if,
        "rewrite_plan": rewrite_plan,
        "rewrite_work_order": rewrite_work_order,
        "adapters": adapter_report,
    }


def persist_artifact_bundle(record, model_id, artifacts):
    caller_artifacts = artifacts
    package_id = artifacts["package"]["package_id"]
    imported = STORE.list_imported_evidence(package_id) or []
    current_measurement = build_measurement_evidence(
        artifacts["adapters"],
        runtime_profile=artifacts["runtime"],
        baseline_report=artifacts["baseline"],
        package_report=artifacts["package"],
        imported_evidence=imported,
    )
    artifacts = {**artifacts, "measurement": current_measurement}
    current_physical_ai_map = build_physical_ai_map(
        artifacts["package"],
        workload_fit=artifacts["workload_fit"],
        system_boundary=artifacts["system_boundary"],
        measurement_evidence=current_measurement,
    )
    artifacts["physical_ai_map"] = current_physical_ai_map
    current_vla_readiness = build_vla_readiness(
        artifacts["analysis"],
        artifacts["quantization"],
        artifacts["runtime"],
        artifacts["system_boundary"],
        package_report=artifacts["package"],
    )
    artifacts["vla_readiness"] = current_vla_readiness
    current_weight_update_readiness = build_weight_update_readiness(
        artifacts["package"],
        vla_readiness=current_vla_readiness,
        measurement_evidence=current_measurement,
    )
    artifacts["weight_update_readiness"] = current_weight_update_readiness
    current_calibration_drift_readiness = build_calibration_drift_readiness(
        artifacts["package"],
        artifacts["analysis"],
        measurement_evidence=current_measurement,
    )
    artifacts["calibration_drift_readiness"] = current_calibration_drift_readiness
    current_control_boundary = build_control_boundary(
        artifacts["package"],
        physical_ai_map=current_physical_ai_map,
        runtime_profile=artifacts["runtime"],
        system_boundary=artifacts["system_boundary"],
        measurement_evidence=current_measurement,
    )
    artifacts["control_boundary"] = current_control_boundary
    current_sensor_boundary_readiness = build_sensor_boundary_readiness(
        artifacts["package"],
        physical_ai_map=current_physical_ai_map,
        runtime_profile=artifacts["runtime"],
        system_boundary=artifacts["system_boundary"],
        measurement_evidence=current_measurement,
    )
    artifacts["sensor_boundary_readiness"] = current_sensor_boundary_readiness
    current_connection_playbook = build_connection_playbook(
        artifacts["adapters"],
        current_measurement,
        toolchain_readiness=artifacts["toolchain"],
        package_report=artifacts["package"],
    )
    artifacts["connection_playbook"] = current_connection_playbook
    current_adapter_execution_plan = build_adapter_execution_plan(
        artifacts["adapters"],
        current_measurement,
        connection_playbook=current_connection_playbook,
        package_report=artifacts["package"],
    )
    artifacts["adapter_execution_plan"] = current_adapter_execution_plan
    current_adapter_connection_kit = build_adapter_connection_kit(
        artifacts["adapters"],
        current_measurement,
        adapter_execution_plan=current_adapter_execution_plan,
        package_report=artifacts["package"],
    )
    artifacts["adapter_connection_kit"] = current_adapter_connection_kit
    current_adapter_evidence_templates = build_adapter_evidence_templates(
        artifacts["adapters"],
        current_measurement,
        adapter_connection_kit=current_adapter_connection_kit,
        package_report=artifacts["package"],
    )
    artifacts["adapter_evidence_templates"] = current_adapter_evidence_templates
    current_adapter_connection_self_test = build_adapter_connection_self_test(
        artifacts["adapters"],
        adapter_probe,
        adapter_connection_kit=current_adapter_connection_kit,
        package_report=artifacts["package"],
    )
    artifacts["adapter_connection_self_test"] = current_adapter_connection_self_test
    current_adapter_integration_readiness = build_adapter_integration_readiness(
        current_adapter_execution_plan,
        current_adapter_connection_kit,
        current_adapter_evidence_templates,
        current_adapter_connection_self_test,
        package_report=artifacts["package"],
    )
    artifacts["adapter_integration_readiness"] = current_adapter_integration_readiness
    current_external_connector_contract = build_external_connector_contract(
        current_adapter_connection_kit,
        current_adapter_integration_readiness,
        package_report=artifacts["package"],
    )
    artifacts["external_connector_contract"] = current_external_connector_contract
    current_compiler_ecosystem_readiness = build_compiler_ecosystem_readiness(
        artifacts["adapters"],
        current_external_connector_contract,
        current_connection_playbook,
        artifacts["analysis"],
        package_report=artifacts["package"],
        toolchain_readiness=artifacts["toolchain"],
        measurement_evidence=current_measurement,
    )
    artifacts["compiler_ecosystem_readiness"] = current_compiler_ecosystem_readiness
    current_connector_implementation_guide = build_connector_implementation_guide(
        current_external_connector_contract,
        adapter_integration_readiness=current_adapter_integration_readiness,
        package_report=artifacts["package"],
    )
    artifacts["connector_implementation_guide"] = current_connector_implementation_guide
    current_connector_test_harness = build_connector_test_harness(
        current_connector_implementation_guide,
        package_report=artifacts["package"],
    )
    artifacts["connector_test_harness"] = current_connector_test_harness
    current_connector_acceptance_drills = build_connector_acceptance_drills(
        current_connector_test_harness,
        imported_evidence=imported,
        package_report=artifacts["package"],
    )
    artifacts["connector_acceptance_drills"] = current_connector_acceptance_drills
    current_connector_acceptance_report = build_connector_acceptance_report(
        current_connector_test_harness,
        current_adapter_connection_self_test,
        current_measurement,
        connector_acceptance_drills=current_connector_acceptance_drills,
        package_report=artifacts["package"],
    )
    artifacts["connector_acceptance_report"] = current_connector_acceptance_report
    current_connector_backlog = build_connector_backlog(
        current_connector_acceptance_report,
        package_report=artifacts["package"],
    )
    artifacts["connector_backlog"] = current_connector_backlog
    current_connector_delivery_plan = build_connector_delivery_plan(
        current_connector_backlog,
        package_report=artifacts["package"],
    )
    artifacts["connector_delivery_plan"] = current_connector_delivery_plan
    current_connector_risk_register = build_connector_risk_register(
        current_connector_delivery_plan,
        package_report=artifacts["package"],
    )
    artifacts["connector_risk_register"] = current_connector_risk_register
    claim_readiness = build_claim_readiness(current_measurement, package_report=artifacts["package"])
    evidence_audit = build_evidence_audit_from_records(package_id, current_measurement, claim_readiness, imported)
    evidence_brief = build_evidence_brief(artifacts["package"], current_measurement, claim_readiness, evidence_audit)
    current_physical_ai_roadmap = build_physical_ai_roadmap(
        artifacts["package"],
        artifacts["analysis"],
        artifacts["runtime"],
        physical_ai_map=current_physical_ai_map,
        vla_readiness=current_vla_readiness,
        weight_update_readiness=current_weight_update_readiness,
        calibration_drift_readiness=current_calibration_drift_readiness,
        control_boundary=current_control_boundary,
        sensor_boundary_readiness=current_sensor_boundary_readiness,
        compiler_ecosystem_readiness=current_compiler_ecosystem_readiness,
        measurement_evidence=current_measurement,
        claim_readiness=claim_readiness,
        evidence_audit=evidence_audit,
        source_check_register=artifacts["source_check_register"],
    )
    artifacts["physical_ai_roadmap"] = current_physical_ai_roadmap
    interview_brief = build_interview_brief(
        artifacts["package"],
        evidence_brief,
        artifacts["system_boundary"],
        artifacts["workload_fit"],
        artifacts["toolchain"],
        concept_glossary=artifacts["glossary"],
    )
    interview_drill = build_interview_drill(
        artifacts["package"],
        interview_brief,
        evidence_brief,
        artifacts["research"],
        artifacts["glossary"],
    )
    artifacts["interview_drill"] = interview_drill
    artifacts["package"]["saved_artifacts"] = {
        "package_id": package_id,
        "package_report": f"/deployment-packages/{package_id}",
        "archive": f"/deployment-packages/{package_id}/archive",
        "review_report": f"/deployment-packages/{package_id}/review-report",
        "review_markdown": f"/deployment-packages/{package_id}/review-report.md",
        "decision_report": f"/deployment-packages/{package_id}/decision-report",
        "rewrite_suggestions": f"/deployment-packages/{package_id}/rewrite-suggestions",
        "rewrite_what_if": f"/deployment-packages/{package_id}/rewrite-what-if",
        "rewrite_plan": f"/deployment-packages/{package_id}/rewrite-plan",
        "rewrite_work_order": f"/deployment-packages/{package_id}/rewrite-work-order",
        "measurement_evidence": f"/deployment-packages/{package_id}/measurement-evidence",
        "hardware_placement": f"/deployment-packages/{package_id}/hardware-placement",
        "residual_aware_placement": f"/deployment-packages/{package_id}/residual-aware-placement",
        "workload_fit": f"/deployment-packages/{package_id}/workload-fit",
        "system_boundary": f"/deployment-packages/{package_id}/system-boundary",
        "physical_ai_map": f"/deployment-packages/{package_id}/physical-ai-map",
        "physical_ai_roadmap": f"/deployment-packages/{package_id}/physical-ai-roadmap",
        "vla_readiness": f"/deployment-packages/{package_id}/vla-readiness",
        "weight_update_readiness": f"/deployment-packages/{package_id}/weight-update-readiness",
        "calibration_drift_readiness": f"/deployment-packages/{package_id}/calibration-drift-readiness",
        "control_boundary": f"/deployment-packages/{package_id}/control-boundary",
        "sensor_boundary_readiness": f"/deployment-packages/{package_id}/sensor-boundary-readiness",
        "research_guide": f"/deployment-packages/{package_id}/research-guide",
        "concept_glossary": f"/deployment-packages/{package_id}/concept-glossary",
        "source_check_register": f"/deployment-packages/{package_id}/source-check-register",
        "toolchain_readiness": f"/deployment-packages/{package_id}/toolchain-readiness",
        "connection_playbook": f"/deployment-packages/{package_id}/connection-playbook",
        "adapter_execution_plan": f"/deployment-packages/{package_id}/adapter-execution-plan",
        "adapter_connection_kit": f"/deployment-packages/{package_id}/adapter-connection-kit",
        "adapter_evidence_templates": f"/deployment-packages/{package_id}/adapter-evidence-templates",
        "adapter_connection_self_test": f"/deployment-packages/{package_id}/adapter-connection-self-test",
        "adapter_integration_readiness": f"/deployment-packages/{package_id}/adapter-integration-readiness",
        "external_connector_contract": f"/deployment-packages/{package_id}/external-connector-contract",
        "compiler_ecosystem_readiness": f"/deployment-packages/{package_id}/compiler-ecosystem-readiness",
        "connector_implementation_guide": f"/deployment-packages/{package_id}/connector-implementation-guide",
        "connector_test_harness": f"/deployment-packages/{package_id}/connector-test-harness",
        "connector_acceptance_drills": f"/deployment-packages/{package_id}/connector-acceptance-drills",
        "connector_acceptance_report": f"/deployment-packages/{package_id}/connector-acceptance-report",
        "connector_backlog": f"/deployment-packages/{package_id}/connector-backlog",
        "connector_delivery_plan": f"/deployment-packages/{package_id}/connector-delivery-plan",
        "connector_risk_register": f"/deployment-packages/{package_id}/connector-risk-register",
        "claim_readiness": f"/deployment-packages/{package_id}/claim-readiness",
        "imported_evidence": f"/deployment-packages/{package_id}/imported-evidence",
        "adapter_runs": f"/deployment-packages/{package_id}/adapter-runs",
        "evidence_audit": f"/deployment-packages/{package_id}/evidence-audit",
        "evidence_brief": f"/deployment-packages/{package_id}/evidence-brief",
        "evidence_brief_markdown": f"/deployment-packages/{package_id}/evidence-brief.md",
        "interview_brief": f"/deployment-packages/{package_id}/interview-brief",
        "interview_brief_markdown": f"/deployment-packages/{package_id}/interview-brief.md",
        "interview_drill": f"/deployment-packages/{package_id}/interview-drill",
        "local_evidence": f"/deployment-packages/{package_id}/local-evidence",
    }
    adapter_runs = STORE.list_adapter_runs(package_id) or []
    current_residual_aware_placement = load_residual_aware_placement(artifacts["hardware_placement"])
    artifacts["residual_aware_placement"] = current_residual_aware_placement
    archive, filename = build_deployment_archive(
        record["path"],
        artifacts["package"],
        artifacts["analysis"],
        artifacts["quantization"],
        artifacts["runtime"],
        baseline_comparison=artifacts["baseline"],
        hardware_placement=artifacts["hardware_placement"],
        residual_aware_placement=current_residual_aware_placement,
        workload_fit=artifacts["workload_fit"],
        system_boundary=artifacts["system_boundary"],
        physical_ai_map=current_physical_ai_map,
        physical_ai_roadmap=current_physical_ai_roadmap,
        vla_readiness=current_vla_readiness,
        weight_update_readiness=current_weight_update_readiness,
        calibration_drift_readiness=current_calibration_drift_readiness,
        control_boundary=current_control_boundary,
        sensor_boundary_readiness=current_sensor_boundary_readiness,
        research_guide=artifacts["research"],
        concept_glossary=artifacts["glossary"],
        source_check_register=artifacts["source_check_register"],
        measurement_evidence=artifacts["measurement"],
        toolchain_readiness=artifacts["toolchain"],
        connection_playbook=current_connection_playbook,
        adapter_execution_plan=current_adapter_execution_plan,
        adapter_connection_kit=current_adapter_connection_kit,
        adapter_evidence_templates=current_adapter_evidence_templates,
        adapter_connection_self_test=current_adapter_connection_self_test,
        adapter_integration_readiness=current_adapter_integration_readiness,
        external_connector_contract=current_external_connector_contract,
        compiler_ecosystem_readiness=current_compiler_ecosystem_readiness,
        connector_implementation_guide=current_connector_implementation_guide,
        connector_test_harness=current_connector_test_harness,
        connector_acceptance_drills=current_connector_acceptance_drills,
        connector_acceptance_report=current_connector_acceptance_report,
        connector_backlog=current_connector_backlog,
        connector_delivery_plan=current_connector_delivery_plan,
        connector_risk_register=current_connector_risk_register,
        evidence_gates=artifacts["evidence"],
        claim_readiness=claim_readiness,
        evidence_audit=evidence_audit,
        evidence_brief=evidence_brief,
        interview_brief=interview_brief,
        interview_drill=interview_drill,
        review_report=artifacts["review"],
        decision_report=artifacts["decision"],
        rewrite_suggestions=artifacts["rewrites"],
        rewrite_what_if=artifacts["rewrite_what_if"],
        rewrite_plan=artifacts["rewrite_plan"],
        rewrite_work_order=artifacts["rewrite_work_order"],
        adapter_registry=artifacts["adapters"],
        imported_evidence=imported,
        adapter_runs=adapter_runs,
    )
    metadata = STORE.save_package(
        model_id,
        package_id,
        artifacts,
        archive,
        filename,
    )
    caller_artifacts.clear()
    caller_artifacts.update(artifacts)
    return archive, filename, metadata


def refresh_saved_package_archive(package_id):
    bundle = STORE.get_package_artifacts(package_id)
    if not bundle:
        return None
    artifacts = bundle["artifacts"]
    model_record = STORE.get(bundle["model_id"])
    if not model_record:
        return None
    imported = STORE.list_imported_evidence(package_id) or []
    adapter_runs = STORE.list_adapter_runs(package_id) or []
    current_measurement = build_measurement_evidence(
        artifacts["adapters"],
        runtime_profile=artifacts["runtime"],
        baseline_report=artifacts["baseline"],
        package_report=artifacts["package"],
        imported_evidence=imported,
    )
    current_claims = build_claim_readiness(current_measurement, package_report=artifacts["package"])
    current_audit = build_evidence_audit_from_records(package_id, current_measurement, current_claims, imported)
    current_brief = build_evidence_brief(artifacts["package"], current_measurement, current_claims, current_audit)
    current_toolchain = build_toolchain_readiness(
        artifacts["adapters"],
        current_measurement,
        package_report=artifacts["package"],
    )
    current_connection_playbook = build_connection_playbook(
        artifacts["adapters"],
        current_measurement,
        toolchain_readiness=current_toolchain,
        package_report=artifacts["package"],
    )
    current_adapter_execution_plan = build_adapter_execution_plan(
        artifacts["adapters"],
        current_measurement,
        connection_playbook=current_connection_playbook,
        package_report=artifacts["package"],
    )
    current_adapter_connection_kit = build_adapter_connection_kit(
        artifacts["adapters"],
        current_measurement,
        adapter_execution_plan=current_adapter_execution_plan,
        package_report=artifacts["package"],
    )
    current_adapter_evidence_templates = build_adapter_evidence_templates(
        artifacts["adapters"],
        current_measurement,
        adapter_connection_kit=current_adapter_connection_kit,
        package_report=artifacts["package"],
    )
    current_adapter_connection_self_test = build_adapter_connection_self_test(
        artifacts["adapters"],
        adapter_probe,
        adapter_connection_kit=current_adapter_connection_kit,
        package_report=artifacts["package"],
    )
    current_adapter_integration_readiness = build_adapter_integration_readiness(
        current_adapter_execution_plan,
        current_adapter_connection_kit,
        current_adapter_evidence_templates,
        current_adapter_connection_self_test,
        package_report=artifacts["package"],
    )
    current_external_connector_contract = build_external_connector_contract(
        current_adapter_connection_kit,
        current_adapter_integration_readiness,
        package_report=artifacts["package"],
    )
    current_compiler_ecosystem_readiness = build_compiler_ecosystem_readiness(
        artifacts["adapters"],
        current_external_connector_contract,
        current_connection_playbook,
        artifacts["analysis"],
        package_report=artifacts["package"],
        toolchain_readiness=current_toolchain,
        measurement_evidence=current_measurement,
    )
    current_connector_implementation_guide = build_connector_implementation_guide(
        current_external_connector_contract,
        adapter_integration_readiness=current_adapter_integration_readiness,
        package_report=artifacts["package"],
    )
    current_connector_test_harness = build_connector_test_harness(
        current_connector_implementation_guide,
        package_report=artifacts["package"],
    )
    current_connector_acceptance_drills = build_connector_acceptance_drills(
        current_connector_test_harness,
        imported_evidence=imported,
        package_report=artifacts["package"],
    )
    current_connector_acceptance_report = build_connector_acceptance_report(
        current_connector_test_harness,
        current_adapter_connection_self_test,
        current_measurement,
        connector_acceptance_drills=current_connector_acceptance_drills,
        package_report=artifacts["package"],
    )
    current_connector_backlog = build_connector_backlog(
        current_connector_acceptance_report,
        package_report=artifacts["package"],
    )
    current_connector_delivery_plan = build_connector_delivery_plan(
        current_connector_backlog,
        package_report=artifacts["package"],
    )
    current_connector_risk_register = build_connector_risk_register(
        current_connector_delivery_plan,
        package_report=artifacts["package"],
    )
    package_summary = artifacts["package"].get("summary", {})
    current_workload_fit = artifacts.get("workload_fit") or build_workload_fit_matrix(
        artifacts["analysis"],
        artifacts["quantization"],
        artifacts["runtime"],
        target_profile=package_summary.get("target_profile", "wearable"),
        modality=package_summary.get("modality", "vision_classification"),
    )
    current_system_boundary = artifacts.get("system_boundary") or build_system_boundary_report(
        artifacts["analysis"],
        artifacts["runtime"],
        package_report=artifacts["package"],
    )
    current_physical_ai_map = build_physical_ai_map(
        artifacts["package"],
        workload_fit=current_workload_fit,
        system_boundary=current_system_boundary,
        measurement_evidence=current_measurement,
    )
    current_vla_readiness = build_vla_readiness(
        artifacts["analysis"],
        artifacts["quantization"],
        artifacts["runtime"],
        current_system_boundary,
        package_report=artifacts["package"],
    )
    current_weight_update_readiness = build_weight_update_readiness(
        artifacts["package"],
        vla_readiness=current_vla_readiness,
        measurement_evidence=current_measurement,
    )
    current_calibration_drift_readiness = build_calibration_drift_readiness(
        artifacts["package"],
        artifacts["analysis"],
        measurement_evidence=current_measurement,
    )
    current_control_boundary = build_control_boundary(
        artifacts["package"],
        physical_ai_map=current_physical_ai_map,
        runtime_profile=artifacts["runtime"],
        system_boundary=current_system_boundary,
        measurement_evidence=current_measurement,
    )
    current_sensor_boundary_readiness = build_sensor_boundary_readiness(
        artifacts["package"],
        physical_ai_map=current_physical_ai_map,
        runtime_profile=artifacts["runtime"],
        system_boundary=current_system_boundary,
        measurement_evidence=current_measurement,
    )
    current_research_guide = artifacts.get("research") or build_research_guide(artifacts["package"])
    current_concept_glossary = artifacts.get("glossary") or build_concept_glossary(artifacts["package"])
    current_source_check_register = artifacts.get("source_check_register") or build_source_check_register(artifacts["package"])
    current_interview_brief = build_interview_brief(
        artifacts["package"],
        current_brief,
        current_system_boundary,
        current_workload_fit,
        current_toolchain,
        concept_glossary=current_concept_glossary,
    )
    current_interview_drill = build_interview_drill(
        artifacts["package"],
        current_interview_brief,
        current_brief,
        current_research_guide,
        current_concept_glossary,
    )
    current_physical_ai_roadmap = build_physical_ai_roadmap(
        artifacts["package"],
        artifacts["analysis"],
        artifacts["runtime"],
        physical_ai_map=current_physical_ai_map,
        vla_readiness=current_vla_readiness,
        weight_update_readiness=current_weight_update_readiness,
        calibration_drift_readiness=current_calibration_drift_readiness,
        control_boundary=current_control_boundary,
        sensor_boundary_readiness=current_sensor_boundary_readiness,
        compiler_ecosystem_readiness=current_compiler_ecosystem_readiness,
        measurement_evidence=current_measurement,
        claim_readiness=current_claims,
        evidence_audit=current_audit,
        source_check_register=current_source_check_register,
    )
    current_hardware_placement = artifacts.get("hardware_placement") or build_hardware_placement(
        artifacts["analysis"],
        package_report=artifacts["package"],
    )
    artifacts["package"].setdefault("saved_artifacts", {})["hardware_placement"] = f"/deployment-packages/{package_id}/hardware-placement"
    current_residual_aware_placement = load_residual_aware_placement(current_hardware_placement)
    artifacts["residual_aware_placement"] = current_residual_aware_placement
    artifacts["package"].setdefault("saved_artifacts", {})["residual_aware_placement"] = f"/deployment-packages/{package_id}/residual-aware-placement"
    archive, filename = build_deployment_archive(
        model_record["path"],
        artifacts["package"],
        artifacts["analysis"],
        artifacts["quantization"],
        artifacts["runtime"],
        baseline_comparison=artifacts["baseline"],
        hardware_placement=current_hardware_placement,
        residual_aware_placement=current_residual_aware_placement,
        workload_fit=current_workload_fit,
        system_boundary=current_system_boundary,
        physical_ai_map=current_physical_ai_map,
        physical_ai_roadmap=current_physical_ai_roadmap,
        vla_readiness=current_vla_readiness,
        weight_update_readiness=current_weight_update_readiness,
        calibration_drift_readiness=current_calibration_drift_readiness,
        control_boundary=current_control_boundary,
        sensor_boundary_readiness=current_sensor_boundary_readiness,
        research_guide=current_research_guide,
        concept_glossary=current_concept_glossary,
        source_check_register=current_source_check_register,
        measurement_evidence=current_measurement,
        toolchain_readiness=current_toolchain,
        connection_playbook=current_connection_playbook,
        adapter_execution_plan=current_adapter_execution_plan,
        adapter_connection_kit=current_adapter_connection_kit,
        adapter_evidence_templates=current_adapter_evidence_templates,
        adapter_connection_self_test=current_adapter_connection_self_test,
        adapter_integration_readiness=current_adapter_integration_readiness,
        external_connector_contract=current_external_connector_contract,
        compiler_ecosystem_readiness=current_compiler_ecosystem_readiness,
        connector_implementation_guide=current_connector_implementation_guide,
        connector_test_harness=current_connector_test_harness,
        connector_acceptance_drills=current_connector_acceptance_drills,
        connector_acceptance_report=current_connector_acceptance_report,
        connector_backlog=current_connector_backlog,
        connector_delivery_plan=current_connector_delivery_plan,
        connector_risk_register=current_connector_risk_register,
        evidence_gates=artifacts["evidence"],
        claim_readiness=current_claims,
        evidence_audit=current_audit,
        evidence_brief=current_brief,
        interview_brief=current_interview_brief,
        interview_drill=current_interview_drill,
        review_report=artifacts["review"],
        decision_report=artifacts["decision"],
        rewrite_suggestions=artifacts["rewrites"],
        rewrite_what_if=artifacts["rewrite_what_if"],
        rewrite_plan=artifacts["rewrite_plan"],
        rewrite_work_order=artifacts["rewrite_work_order"],
        adapter_registry=artifacts["adapters"],
        imported_evidence=imported,
        adapter_runs=adapter_runs,
    )
    return STORE.save_package(
        bundle["model_id"],
        package_id,
        {
            **artifacts,
            "measurement": current_measurement,
            "hardware_placement": current_hardware_placement,
            "residual_aware_placement": current_residual_aware_placement,
            "workload_fit": current_workload_fit,
            "system_boundary": current_system_boundary,
            "physical_ai_map": current_physical_ai_map,
            "physical_ai_roadmap": current_physical_ai_roadmap,
            "vla_readiness": current_vla_readiness,
            "weight_update_readiness": current_weight_update_readiness,
            "calibration_drift_readiness": current_calibration_drift_readiness,
            "control_boundary": current_control_boundary,
            "sensor_boundary_readiness": current_sensor_boundary_readiness,
            "research": current_research_guide,
            "glossary": current_concept_glossary,
            "source_check_register": current_source_check_register,
            "toolchain": current_toolchain,
            "connection_playbook": current_connection_playbook,
            "adapter_execution_plan": current_adapter_execution_plan,
            "adapter_connection_kit": current_adapter_connection_kit,
            "adapter_evidence_templates": current_adapter_evidence_templates,
            "adapter_connection_self_test": current_adapter_connection_self_test,
            "adapter_integration_readiness": current_adapter_integration_readiness,
            "external_connector_contract": current_external_connector_contract,
            "compiler_ecosystem_readiness": current_compiler_ecosystem_readiness,
            "connector_implementation_guide": current_connector_implementation_guide,
            "connector_test_harness": current_connector_test_harness,
            "connector_acceptance_drills": current_connector_acceptance_drills,
            "connector_acceptance_report": current_connector_acceptance_report,
            "connector_backlog": current_connector_backlog,
            "connector_delivery_plan": current_connector_delivery_plan,
            "connector_risk_register": current_connector_risk_register,
            "interview_drill": current_interview_drill,
        },
        archive,
        filename,
    )


def is_local_generated_import(record):
    payload = record.get("payload") or {}
    provenance = payload.get("provenance") or {}
    if provenance.get("measurement_level") in {"calibrated_simulation", "calibrated_silicon"}:
        return False
    if provenance.get("tool") in LOCAL_EVIDENCE_TOOLS:
        return True
    if str(provenance.get("tool", "")).startswith("analog-digital-chip-design-eda."):
        return True
    if provenance.get("not_measured_silicon") is True:
        return True
    if payload.get("dataset_id", "").startswith("local-synthetic-"):
        return True
    if payload.get("dataset_id", "").startswith("local-toy-"):
        return True
    if (payload.get("measurement_setup") or {}).get("not_measured_hardware") is True:
        return True
    return False


def evidence_proof_level(record):
    if not record:
        return "missing"
    payload = record.get("payload") or {}
    provenance = payload.get("provenance") or {}
    if record.get("source_id") == "physical_flow":
        if payload.get("flow_status") == "flow completed":
            return "routed exploratory physical flow"
        if payload.get("flow_status"):
            return "physical flow attempted"
        return "physical flow evidence"
    measurement_level = provenance.get("measurement_level")
    if measurement_level == "calibrated_silicon":
        return "calibrated silicon"
    if measurement_level == "calibrated_simulation":
        return "calibrated simulation"
    if measurement_level in {"measured_board", "instrumented_runtime"}:
        return "measured board runtime"
    if measurement_level in {"measured_board_power", "instrumented_power"}:
        return "measured power"
    if is_local_generated_import(record):
        return "local simulation"
    if record.get("import_id"):
        return "external evidence"
    return "missing"


def run_and_import_local_evidence(package_id, force=False):
    bundle = STORE.get_package_artifacts(package_id)
    if not bundle:
        raise HTTPException(status_code=404, detail="Unknown package_id.")
    model_record = STORE.get(bundle["model_id"])
    if not model_record:
        raise HTTPException(status_code=404, detail="Package model record is missing.")
    package_report = bundle["artifacts"]["package"]
    summary = package_report.get("summary", {})
    target_profile = summary.get("target_profile", "wearable")
    calibration_profile = summary.get("calibration_profile", "sim-wearable-v0")
    modality = summary.get("modality", "vision_classification")
    runtime_mode = summary.get("runtime_mode", "balanced")
    existing = STORE.list_imported_evidence(package_id) or []
    existing_by_source = {}
    for record in existing:
        existing_by_source.setdefault(record.get("source_id"), []).append(record)
    runs = []
    saved_adapter_runs = []
    accepted = []
    rejected = []
    skipped = []
    for adapter_id, source_id in LOCAL_EVIDENCE_ADAPTERS:
        source_existing = existing_by_source.get(source_id, [])
        nonlocal_existing = [record for record in source_existing if not is_local_generated_import(record)]
        if nonlocal_existing and not force:
            skipped.append({
                "adapter_id": adapter_id,
                "source_id": source_id,
                "reason": "Non-local evidence already exists for this source; local refresh skipped to avoid overriding stronger evidence.",
            })
            continue
        local_import_ids = [record["import_id"] for record in source_existing if is_local_generated_import(record)]
        deleted_count = STORE.delete_imported_evidence(package_id, local_import_ids)
        if deleted_count:
            existing_by_source[source_id] = [record for record in source_existing if record.get("import_id") not in set(local_import_ids)]
        result = run_adapter(
            adapter_id,
            model_record,
            BASE_DIR / ".data" / "adapter-runs",
            target_profile=target_profile,
            calibration_profile=calibration_profile,
            modality=modality,
            runtime_mode=runtime_mode,
        )
        runs.append(result)
        if result:
            saved_run = STORE.save_adapter_run(package_id, result)
            if saved_run:
                saved_adapter_runs.append(saved_run)
        if not result or result.get("status") != "completed":
            rejected.append({"adapter_id": adapter_id, "source_id": source_id, "errors": [result.get("summary", {}).get("message", "Adapter did not complete.") if result else "Adapter did not run."]})
            continue
        payload = result.get("normalized_evidence_payload")
        actual_source = result.get("normalized_evidence_source_id")
        if actual_source != source_id or not payload:
            rejected.append({"adapter_id": adapter_id, "source_id": source_id, "errors": ["Adapter did not produce the expected normalized evidence payload."]})
            continue
        saved, errors = save_evidence_payload(source_id, payload, package_id)
        if errors:
            rejected.append({"adapter_id": adapter_id, "source_id": source_id, "errors": errors})
        else:
            accepted.append(saved)
    if accepted or saved_adapter_runs:
        refresh_saved_package_archive(package_id)
    artifacts, measurement = current_package_measurement_or_404(package_id)
    claim_readiness = build_claim_readiness(measurement, package_report=artifacts["package"])
    return {
        "result_type": "local_evidence_run",
        "package_id": package_id,
        "model_id": bundle["model_id"],
        "target_profile": target_profile,
        "calibration_profile": calibration_profile,
        "modality": modality,
        "runtime_mode": runtime_mode,
        "accepted_count": len(accepted),
        "saved_adapter_run_count": len(saved_adapter_runs),
        "rejected_count": len(rejected),
        "skipped_count": len(skipped),
        "accepted": accepted,
        "rejected": rejected,
        "skipped": skipped,
        "adapter_runs": runs,
        "measurement_summary": measurement["summary"],
        "claim_readiness_summary": claim_readiness["summary"],
    }


def import_hardware_lab_evidence(package_id, force=False):
    bundle = STORE.get_package_artifacts(package_id)
    if not bundle:
        raise HTTPException(status_code=404, detail="Unknown package_id.")
    if not HARDWARE_LAB_EVIDENCE_BATCH.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Hardware-lab evidence batch not found at {HARDWARE_LAB_EVIDENCE_BATCH}. Run scripts/export_aimc_hardware_lab_evidence.py in analog-digital-chip-design-eda first.",
        )
    try:
        payload = json.loads(HARDWARE_LAB_EVIDENCE_BATCH.read_text(encoding="utf-8"))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not read hardware-lab evidence batch: {exc}") from exc
    items = payload.get("items") if isinstance(payload, dict) else None
    if not isinstance(items, list) or not items:
        raise HTTPException(status_code=400, detail="Hardware-lab evidence batch must contain a non-empty items list.")

    existing = STORE.list_imported_evidence(package_id) or []
    existing_by_source = {}
    for record in existing:
        existing_by_source.setdefault(record.get("source_id"), []).append(record)

    accepted = []
    rejected = []
    skipped = []
    refreshed_sources = []
    for index, item in enumerate(items):
        source_id = item.get("source_id") if isinstance(item, dict) else None
        evidence_payload = item.get("payload") if isinstance(item, dict) else None
        source_existing = existing_by_source.get(source_id, [])
        nonlocal_existing = [record for record in source_existing if not is_local_generated_import(record)]
        if nonlocal_existing and not force:
            skipped.append({
                "index": index,
                "source_id": source_id,
                "reason": "Non-local evidence already exists for this source; hardware-lab import skipped to avoid overriding stronger evidence.",
            })
            continue
        local_import_ids = [record["import_id"] for record in source_existing if is_local_generated_import(record)]
        deleted_count = STORE.delete_imported_evidence(package_id, local_import_ids)
        if deleted_count:
            refreshed_sources.append({"source_id": source_id, "deleted_local_imports": deleted_count})
        saved, errors = save_evidence_payload(source_id, evidence_payload, package_id)
        if errors:
            rejected.append({"index": index, "source_id": source_id, "errors": errors})
        else:
            accepted.append(saved)

    strict_tool_import = None
    if HARDWARE_LAB_STRICT_TOOL_EVIDENCE.exists():
        try:
            strict_payload = json.loads(HARDWARE_LAB_STRICT_TOOL_EVIDENCE.read_text(encoding="utf-8"))
            readiness = build_tool_readiness_report("analog_error_simulation", strict_payload)
            if readiness["tool_ready"]:
                source_existing = STORE.list_imported_evidence(package_id) or []
                local_import_ids = [
                    record["import_id"]
                    for record in source_existing
                    if record.get("source_id") == "analog_error_simulation" and is_local_generated_import(record)
                ]
                deleted_count = STORE.delete_imported_evidence(package_id, local_import_ids)
                if deleted_count:
                    refreshed_sources.append({
                        "source_id": "analog_error_simulation",
                        "deleted_local_imports": deleted_count,
                        "reason": "strict simulator/tool evidence replaced local analog evidence",
                    })
                saved, errors = save_evidence_payload("analog_error_simulation", strict_payload, package_id)
                if errors:
                    rejected.append({
                        "index": "strict-tool",
                        "source_id": "analog_error_simulation",
                        "errors": errors,
                        "tool_readiness": readiness,
                    })
                else:
                    saved["tool_readiness"] = readiness
                    strict_tool_import = saved
                    accepted.append(saved)
            else:
                rejected.append({
                    "index": "strict-tool",
                    "source_id": "analog_error_simulation",
                    "errors": readiness["issues"],
                    "tool_readiness": readiness,
                })
        except Exception as exc:
            rejected.append({
                "index": "strict-tool",
                "source_id": "analog_error_simulation",
                "errors": [f"Could not import strict analog tool evidence: {exc}"],
            })

    if accepted or refreshed_sources:
        refresh_saved_package_archive(package_id)
    artifacts, measurement = current_package_measurement_or_404(package_id)
    claim_readiness = build_claim_readiness(measurement, package_report=artifacts["package"])
    return {
        "result_type": "hardware_lab_evidence_import",
        "package_id": package_id,
        "source_batch": str(HARDWARE_LAB_EVIDENCE_BATCH),
        "accepted_count": len(accepted),
        "rejected_count": len(rejected),
        "skipped_count": len(skipped),
        "refreshed_sources": refreshed_sources,
        "accepted": accepted,
        "rejected": rejected,
        "skipped": skipped,
        "strict_tool_evidence": {
            "source": str(HARDWARE_LAB_STRICT_TOOL_EVIDENCE),
            "imported": strict_tool_import is not None,
            "import_id": strict_tool_import.get("import_id") if strict_tool_import else None,
        },
        "measurement_summary": measurement["summary"],
        "claim_readiness_summary": claim_readiness["summary"],
    }


def build_evidence_audit_from_records(package_id, measurement, claim_readiness, records):
    claims_by_source = {}
    for claim in claim_readiness.get("lab_claims", []):
        for source_id in claim.get("required_sources", []):
            claims_by_source.setdefault(source_id, []).append({
                "claim_id": claim["id"],
                "claim_name": claim["name"],
                "claim_status": claim["status"],
                "quality_issues": claim.get("quality_issues", []),
            })
    grouped = {}
    for record in records:
        grouped.setdefault(record.get("source_id"), []).append(record)
    sources = []
    for required in measurement.get("required_sources", []):
        source_id = required["id"]
        source_records = grouped.get(source_id, [])
        latest = source_records[-1] if source_records else None
        local_count = sum(1 for record in source_records if is_local_generated_import(record))
        nonlocal_count = len(source_records) - local_count
        sources.append({
            "source_id": source_id,
            "artifact_name": required["artifact_name"],
            "required_for": required["required_for"],
            "status": required["status"],
            "imported_count": len(source_records),
            "local_generated_count": local_count,
            "nonlocal_count": nonlocal_count,
            "latest_import_id": latest.get("import_id") if latest else None,
            "latest_created_at": latest.get("created_at") if latest else None,
            "latest_is_local_generated": is_local_generated_import(latest) if latest else False,
            "latest_proof_level": evidence_proof_level(latest),
            "latest_payload_status": ((latest or {}).get("payload") or {}).get("pass"),
            "local_refresh_behavior": "skipped because non-local evidence exists" if nonlocal_count else "local refresh can replace local-generated evidence" if local_count else "local refresh can add evidence",
            "claims": claims_by_source.get(source_id, []),
        })
    return {
        "result_type": "evidence_audit",
        "package_id": package_id,
        "summary": {
            "sources": len(sources),
            "total_imports": len(records),
            "local_generated_imports": sum(item["local_generated_count"] for item in sources),
            "nonlocal_imports": sum(item["nonlocal_count"] for item in sources),
            "sources_with_nonlocal_evidence": sum(1 for item in sources if item["nonlocal_count"]),
            "sources_with_latest_local": sum(1 for item in sources if item["latest_is_local_generated"]),
        },
        "sources": sources,
    }


def build_evidence_audit(package_id):
    records = STORE.list_imported_evidence(package_id)
    if records is None:
        raise HTTPException(status_code=404, detail="Unknown package_id.")
    artifacts, measurement = current_package_measurement_or_404(package_id)
    claim_readiness = build_claim_readiness(measurement, package_report=artifacts["package"])
    return build_evidence_audit_from_records(package_id, measurement, claim_readiness, records)


def build_current_evidence_brief(package_id):
    records = STORE.list_imported_evidence(package_id)
    if records is None:
        raise HTTPException(status_code=404, detail="Unknown package_id.")
    artifacts, measurement = current_package_measurement_or_404(package_id)
    claim_readiness = build_claim_readiness(measurement, package_report=artifacts["package"])
    evidence_audit = build_evidence_audit_from_records(package_id, measurement, claim_readiness, records)
    return build_evidence_brief(artifacts["package"], measurement, claim_readiness, evidence_audit)


def build_current_interview_brief(package_id):
    bundle = STORE.get_package_artifacts(package_id)
    if not bundle:
        raise HTTPException(status_code=404, detail="Unknown package_id or missing artifact bundle.")
    evidence_brief = build_current_evidence_brief(package_id)
    system_boundary = current_package_system_boundary_or_404(package_id)
    workload_fit = current_package_workload_fit_or_404(package_id)
    toolchain = current_package_toolchain_readiness_or_404(package_id)
    glossary = current_package_concept_glossary_or_404(package_id)
    return build_interview_brief(
        bundle["artifacts"]["package"],
        evidence_brief,
        system_boundary,
        workload_fit,
        toolchain,
        concept_glossary=glossary,
    )


def build_current_interview_drill(package_id):
    bundle = STORE.get_package_artifacts(package_id)
    if not bundle:
        raise HTTPException(status_code=404, detail="Unknown package_id or missing artifact bundle.")
    interview = build_current_interview_brief(package_id)
    evidence_brief = build_current_evidence_brief(package_id)
    research = current_package_research_guide_or_404(package_id)
    glossary = current_package_concept_glossary_or_404(package_id)
    return build_interview_drill(
        bundle["artifacts"]["package"],
        interview,
        evidence_brief,
        research,
        glossary,
    )


def current_package_workload_fit_or_404(package_id):
    bundle = STORE.get_package_artifacts(package_id)
    if not bundle:
        raise HTTPException(status_code=404, detail="Unknown package_id or missing artifact bundle.")
    artifacts = bundle["artifacts"]
    if artifacts.get("workload_fit"):
        return artifacts["workload_fit"]
    summary = artifacts["package"].get("summary", {})
    return build_workload_fit_matrix(
        artifacts["analysis"],
        artifacts["quantization"],
        artifacts["runtime"],
        target_profile=summary.get("target_profile", "wearable"),
        modality=summary.get("modality", "vision_classification"),
    )


def current_package_system_boundary_or_404(package_id):
    bundle = STORE.get_package_artifacts(package_id)
    if not bundle:
        raise HTTPException(status_code=404, detail="Unknown package_id or missing artifact bundle.")
    artifacts = bundle["artifacts"]
    if artifacts.get("system_boundary"):
        return artifacts["system_boundary"]
    return build_system_boundary_report(
        artifacts["analysis"],
        artifacts["runtime"],
        package_report=artifacts["package"],
    )


def current_package_physical_ai_map_or_404(package_id):
    bundle = STORE.get_package_artifacts(package_id)
    if not bundle:
        raise HTTPException(status_code=404, detail="Unknown package_id or missing artifact bundle.")
    artifacts = bundle["artifacts"]
    if artifacts.get("physical_ai_map"):
        return artifacts["physical_ai_map"]
    _, measurement = current_package_measurement_or_404(package_id)
    return build_physical_ai_map(
        artifacts["package"],
        workload_fit=current_package_workload_fit_or_404(package_id),
        system_boundary=current_package_system_boundary_or_404(package_id),
        measurement_evidence=measurement,
    )


def current_package_vla_readiness_or_404(package_id):
    bundle = STORE.get_package_artifacts(package_id)
    if not bundle:
        raise HTTPException(status_code=404, detail="Unknown package_id or missing artifact bundle.")
    artifacts = bundle["artifacts"]
    if artifacts.get("vla_readiness"):
        return artifacts["vla_readiness"]
    return build_vla_readiness(
        artifacts["analysis"],
        artifacts["quantization"],
        artifacts["runtime"],
        current_package_system_boundary_or_404(package_id),
        package_report=artifacts["package"],
    )


def current_package_weight_update_readiness_or_404(package_id):
    bundle = STORE.get_package_artifacts(package_id)
    if not bundle:
        raise HTTPException(status_code=404, detail="Unknown package_id or missing artifact bundle.")
    artifacts = bundle["artifacts"]
    if artifacts.get("weight_update_readiness"):
        return artifacts["weight_update_readiness"]
    _, measurement = current_package_measurement_or_404(package_id)
    return build_weight_update_readiness(
        artifacts["package"],
        vla_readiness=current_package_vla_readiness_or_404(package_id),
        measurement_evidence=measurement,
    )


def current_package_calibration_drift_readiness_or_404(package_id):
    bundle = STORE.get_package_artifacts(package_id)
    if not bundle:
        raise HTTPException(status_code=404, detail="Unknown package_id or missing artifact bundle.")
    artifacts = bundle["artifacts"]
    if artifacts.get("calibration_drift_readiness"):
        return artifacts["calibration_drift_readiness"]
    _, measurement = current_package_measurement_or_404(package_id)
    return build_calibration_drift_readiness(
        artifacts["package"],
        artifacts["analysis"],
        measurement_evidence=measurement,
    )


def current_package_control_boundary_or_404(package_id):
    bundle = STORE.get_package_artifacts(package_id)
    if not bundle:
        raise HTTPException(status_code=404, detail="Unknown package_id or missing artifact bundle.")
    artifacts = bundle["artifacts"]
    if artifacts.get("control_boundary"):
        return artifacts["control_boundary"]
    _, measurement = current_package_measurement_or_404(package_id)
    return build_control_boundary(
        artifacts["package"],
        physical_ai_map=current_package_physical_ai_map_or_404(package_id),
        runtime_profile=artifacts["runtime"],
        system_boundary=current_package_system_boundary_or_404(package_id),
        measurement_evidence=measurement,
    )


def current_package_sensor_boundary_readiness_or_404(package_id):
    bundle = STORE.get_package_artifacts(package_id)
    if not bundle:
        raise HTTPException(status_code=404, detail="Unknown package_id or missing artifact bundle.")
    artifacts = bundle["artifacts"]
    if artifacts.get("sensor_boundary_readiness"):
        return artifacts["sensor_boundary_readiness"]
    _, measurement = current_package_measurement_or_404(package_id)
    return build_sensor_boundary_readiness(
        artifacts["package"],
        physical_ai_map=current_package_physical_ai_map_or_404(package_id),
        runtime_profile=artifacts["runtime"],
        system_boundary=current_package_system_boundary_or_404(package_id),
        measurement_evidence=measurement,
    )


def current_package_research_guide_or_404(package_id):
    bundle = STORE.get_package_artifacts(package_id)
    if not bundle:
        raise HTTPException(status_code=404, detail="Unknown package_id or missing artifact bundle.")
    artifacts = bundle["artifacts"]
    if artifacts.get("research"):
        return artifacts["research"]
    return build_research_guide(artifacts["package"])


def current_package_concept_glossary_or_404(package_id):
    bundle = STORE.get_package_artifacts(package_id)
    if not bundle:
        raise HTTPException(status_code=404, detail="Unknown package_id or missing artifact bundle.")
    artifacts = bundle["artifacts"]
    if artifacts.get("glossary"):
        return artifacts["glossary"]
    return build_concept_glossary(artifacts["package"])


def current_package_source_check_register_or_404(package_id):
    bundle = STORE.get_package_artifacts(package_id)
    if not bundle:
        raise HTTPException(status_code=404, detail="Unknown package_id or missing artifact bundle.")
    artifacts = bundle["artifacts"]
    if artifacts.get("source_check_register"):
        return artifacts["source_check_register"]
    return build_source_check_register(artifacts["package"])


def current_package_toolchain_readiness_or_404(package_id):
    bundle = STORE.get_package_artifacts(package_id)
    if not bundle:
        raise HTTPException(status_code=404, detail="Unknown package_id or missing artifact bundle.")
    artifacts = bundle["artifacts"]
    if artifacts.get("toolchain"):
        return artifacts["toolchain"]
    _, measurement = current_package_measurement_or_404(package_id)
    return build_toolchain_readiness(
        artifacts["adapters"],
        measurement,
        package_report=artifacts["package"],
    )


def current_package_connection_playbook_or_404(package_id):
    bundle = STORE.get_package_artifacts(package_id)
    if not bundle:
        raise HTTPException(status_code=404, detail="Unknown package_id or missing artifact bundle.")
    artifacts = bundle["artifacts"]
    if artifacts.get("connection_playbook"):
        return artifacts["connection_playbook"]
    toolchain = current_package_toolchain_readiness_or_404(package_id)
    _, measurement = current_package_measurement_or_404(package_id)
    return build_connection_playbook(
        artifacts["adapters"],
        measurement,
        toolchain_readiness=toolchain,
        package_report=artifacts["package"],
    )


def current_package_adapter_execution_plan_or_404(package_id):
    bundle = STORE.get_package_artifacts(package_id)
    if not bundle:
        raise HTTPException(status_code=404, detail="Unknown package_id or missing artifact bundle.")
    artifacts = bundle["artifacts"]
    if artifacts.get("adapter_execution_plan"):
        return artifacts["adapter_execution_plan"]
    connection_playbook = current_package_connection_playbook_or_404(package_id)
    _, measurement = current_package_measurement_or_404(package_id)
    return build_adapter_execution_plan(
        artifacts["adapters"],
        measurement,
        connection_playbook=connection_playbook,
        package_report=artifacts["package"],
    )


def current_package_adapter_connection_kit_or_404(package_id):
    bundle = STORE.get_package_artifacts(package_id)
    if not bundle:
        raise HTTPException(status_code=404, detail="Unknown package_id or missing artifact bundle.")
    artifacts = bundle["artifacts"]
    if artifacts.get("adapter_connection_kit"):
        return artifacts["adapter_connection_kit"]
    adapter_execution_plan = current_package_adapter_execution_plan_or_404(package_id)
    _, measurement = current_package_measurement_or_404(package_id)
    return build_adapter_connection_kit(
        artifacts["adapters"],
        measurement,
        adapter_execution_plan=adapter_execution_plan,
        package_report=artifacts["package"],
    )


def current_package_adapter_evidence_templates_or_404(package_id):
    bundle = STORE.get_package_artifacts(package_id)
    if not bundle:
        raise HTTPException(status_code=404, detail="Unknown package_id or missing artifact bundle.")
    artifacts = bundle["artifacts"]
    if artifacts.get("adapter_evidence_templates"):
        return artifacts["adapter_evidence_templates"]
    adapter_connection_kit = current_package_adapter_connection_kit_or_404(package_id)
    _, measurement = current_package_measurement_or_404(package_id)
    return build_adapter_evidence_templates(
        artifacts["adapters"],
        measurement,
        adapter_connection_kit=adapter_connection_kit,
        package_report=artifacts["package"],
    )


def current_package_adapter_connection_self_test_or_404(package_id):
    bundle = STORE.get_package_artifacts(package_id)
    if not bundle:
        raise HTTPException(status_code=404, detail="Unknown package_id or missing artifact bundle.")
    artifacts = bundle["artifacts"]
    if artifacts.get("adapter_connection_self_test"):
        return artifacts["adapter_connection_self_test"]
    adapter_connection_kit = current_package_adapter_connection_kit_or_404(package_id)
    return build_adapter_connection_self_test(
        artifacts["adapters"],
        adapter_probe,
        adapter_connection_kit=adapter_connection_kit,
        package_report=artifacts["package"],
    )


def current_package_adapter_integration_readiness_or_404(package_id):
    bundle = STORE.get_package_artifacts(package_id)
    if not bundle:
        raise HTTPException(status_code=404, detail="Unknown package_id or missing artifact bundle.")
    artifacts = bundle["artifacts"]
    if artifacts.get("adapter_integration_readiness"):
        return artifacts["adapter_integration_readiness"]
    adapter_execution_plan = current_package_adapter_execution_plan_or_404(package_id)
    adapter_connection_kit = current_package_adapter_connection_kit_or_404(package_id)
    adapter_evidence_templates = current_package_adapter_evidence_templates_or_404(package_id)
    adapter_connection_self_test = current_package_adapter_connection_self_test_or_404(package_id)
    return build_adapter_integration_readiness(
        adapter_execution_plan,
        adapter_connection_kit,
        adapter_evidence_templates,
        adapter_connection_self_test,
        package_report=artifacts["package"],
    )


def current_package_external_connector_contract_or_404(package_id):
    bundle = STORE.get_package_artifacts(package_id)
    if not bundle:
        raise HTTPException(status_code=404, detail="Unknown package_id or missing artifact bundle.")
    artifacts = bundle["artifacts"]
    if artifacts.get("external_connector_contract"):
        return artifacts["external_connector_contract"]
    adapter_connection_kit = current_package_adapter_connection_kit_or_404(package_id)
    adapter_integration_readiness = current_package_adapter_integration_readiness_or_404(package_id)
    return build_external_connector_contract(
        adapter_connection_kit,
        adapter_integration_readiness,
        package_report=artifacts["package"],
    )


def current_package_compiler_ecosystem_readiness_or_404(package_id):
    bundle = STORE.get_package_artifacts(package_id)
    if not bundle:
        raise HTTPException(status_code=404, detail="Unknown package_id or missing artifact bundle.")
    artifacts = bundle["artifacts"]
    if artifacts.get("compiler_ecosystem_readiness"):
        return artifacts["compiler_ecosystem_readiness"]
    _, measurement = current_package_measurement_or_404(package_id)
    return build_compiler_ecosystem_readiness(
        artifacts["adapters"],
        current_package_external_connector_contract_or_404(package_id),
        current_package_connection_playbook_or_404(package_id),
        artifacts["analysis"],
        package_report=artifacts["package"],
        toolchain_readiness=current_package_toolchain_readiness_or_404(package_id),
        measurement_evidence=measurement,
    )


def current_package_physical_ai_roadmap_or_404(package_id):
    bundle = STORE.get_package_artifacts(package_id)
    if not bundle:
        raise HTTPException(status_code=404, detail="Unknown package_id or missing artifact bundle.")
    artifacts = bundle["artifacts"]
    if artifacts.get("physical_ai_roadmap"):
        return artifacts["physical_ai_roadmap"]
    _, measurement = current_package_measurement_or_404(package_id)
    claim_readiness = build_claim_readiness(measurement, package_report=artifacts["package"])
    evidence_audit = build_evidence_audit_from_records(
        package_id,
        measurement,
        claim_readiness,
        STORE.list_imported_evidence(package_id) or [],
    )
    return build_physical_ai_roadmap(
        artifacts["package"],
        artifacts["analysis"],
        artifacts["runtime"],
        physical_ai_map=current_package_physical_ai_map_or_404(package_id),
        vla_readiness=current_package_vla_readiness_or_404(package_id),
        weight_update_readiness=current_package_weight_update_readiness_or_404(package_id),
        calibration_drift_readiness=current_package_calibration_drift_readiness_or_404(package_id),
        control_boundary=current_package_control_boundary_or_404(package_id),
        sensor_boundary_readiness=current_package_sensor_boundary_readiness_or_404(package_id),
        compiler_ecosystem_readiness=current_package_compiler_ecosystem_readiness_or_404(package_id),
        measurement_evidence=measurement,
        claim_readiness=claim_readiness,
        evidence_audit=evidence_audit,
        source_check_register=current_package_source_check_register_or_404(package_id),
    )


def current_package_connector_implementation_guide_or_404(package_id):
    bundle = STORE.get_package_artifacts(package_id)
    if not bundle:
        raise HTTPException(status_code=404, detail="Unknown package_id or missing artifact bundle.")
    artifacts = bundle["artifacts"]
    if artifacts.get("connector_implementation_guide"):
        return artifacts["connector_implementation_guide"]
    external_connector_contract = current_package_external_connector_contract_or_404(package_id)
    adapter_integration_readiness = current_package_adapter_integration_readiness_or_404(package_id)
    return build_connector_implementation_guide(
        external_connector_contract,
        adapter_integration_readiness=adapter_integration_readiness,
        package_report=artifacts["package"],
    )


def current_package_connector_test_harness_or_404(package_id):
    bundle = STORE.get_package_artifacts(package_id)
    if not bundle:
        raise HTTPException(status_code=404, detail="Unknown package_id or missing artifact bundle.")
    artifacts = bundle["artifacts"]
    if artifacts.get("connector_test_harness"):
        return artifacts["connector_test_harness"]
    connector_implementation_guide = current_package_connector_implementation_guide_or_404(package_id)
    return build_connector_test_harness(
        connector_implementation_guide,
        package_report=artifacts["package"],
    )


def current_package_connector_acceptance_report_or_404(package_id):
    bundle = STORE.get_package_artifacts(package_id)
    if not bundle:
        raise HTTPException(status_code=404, detail="Unknown package_id or missing artifact bundle.")
    artifacts = bundle["artifacts"]
    connector_test_harness = current_package_connector_test_harness_or_404(package_id)
    adapter_connection_self_test = current_package_adapter_connection_self_test_or_404(package_id)
    _, measurement = current_package_measurement_or_404(package_id)
    connector_acceptance_drills = current_package_connector_acceptance_drills_or_404(package_id)
    return build_connector_acceptance_report(
        connector_test_harness,
        adapter_connection_self_test,
        measurement,
        connector_acceptance_drills=connector_acceptance_drills,
        package_report=artifacts["package"],
    )


def current_package_connector_acceptance_drills_or_404(package_id):
    bundle = STORE.get_package_artifacts(package_id)
    if not bundle:
        raise HTTPException(status_code=404, detail="Unknown package_id or missing artifact bundle.")
    artifacts = bundle["artifacts"]
    if artifacts.get("connector_acceptance_drills"):
        return artifacts["connector_acceptance_drills"]
    connector_test_harness = current_package_connector_test_harness_or_404(package_id)
    imported = STORE.list_imported_evidence(package_id) or []
    return build_connector_acceptance_drills(
        connector_test_harness,
        imported_evidence=imported,
        package_report=artifacts["package"],
    )


def current_package_connector_backlog_or_404(package_id):
    bundle = STORE.get_package_artifacts(package_id)
    if not bundle:
        raise HTTPException(status_code=404, detail="Unknown package_id or missing artifact bundle.")
    artifacts = bundle["artifacts"]
    if artifacts.get("connector_backlog"):
        return artifacts["connector_backlog"]
    connector_acceptance_report = current_package_connector_acceptance_report_or_404(package_id)
    return build_connector_backlog(
        connector_acceptance_report,
        package_report=artifacts["package"],
    )


def current_package_connector_delivery_plan_or_404(package_id):
    bundle = STORE.get_package_artifacts(package_id)
    if not bundle:
        raise HTTPException(status_code=404, detail="Unknown package_id or missing artifact bundle.")
    artifacts = bundle["artifacts"]
    if artifacts.get("connector_delivery_plan"):
        return artifacts["connector_delivery_plan"]
    connector_backlog = current_package_connector_backlog_or_404(package_id)
    return build_connector_delivery_plan(
        connector_backlog,
        package_report=artifacts["package"],
    )


def current_package_connector_risk_register_or_404(package_id):
    bundle = STORE.get_package_artifacts(package_id)
    if not bundle:
        raise HTTPException(status_code=404, detail="Unknown package_id or missing artifact bundle.")
    artifacts = bundle["artifacts"]
    if artifacts.get("connector_risk_register"):
        return artifacts["connector_risk_register"]
    connector_delivery_plan = current_package_connector_delivery_plan_or_404(package_id)
    return build_connector_risk_register(
        connector_delivery_plan,
        package_report=artifacts["package"],
    )


def _numeric_delta(value, baseline):
    if value is None or baseline is None:
        return None
    return round(float(value) - float(baseline), 4)


def _percent_delta(value, baseline):
    if value is None or baseline in (None, 0):
        return None
    return round(((float(value) - float(baseline)) / float(baseline)) * 100, 2)


def build_run_comparison(runs):
    baseline = runs[0]
    baseline_summary = baseline.get("summary", {})
    rows = []
    for index, run in enumerate(runs):
        summary = run.get("summary", {})
        rows.append(
            {
                "run_id": run["run_id"],
                "project_id": run.get("project_id"),
                "project_name": run.get("project_name"),
                "model_id": run.get("model_id"),
                "package_id": run.get("package_id"),
                "created_at": run.get("created_at"),
                "target_profile": run.get("target_profile"),
                "modality": run.get("modality"),
                "calibration_profile": run.get("calibration_profile"),
                "runtime_mode": run.get("runtime_mode"),
                "fit": summary.get("fit"),
                "grade": summary.get("grade"),
                "overall_status": summary.get("overall_status"),
                "safe_claim": summary.get("safe_claim"),
                "readiness_stage": summary.get("readiness_stage"),
                "claim_level": summary.get("claim_level"),
                "metrics": {
                    "analog_coverage_percent": summary.get("analog_coverage_percent"),
                    "fallback_count": summary.get("fallback_count"),
                    "latency_ms": summary.get("latency_ms"),
                    "energy_uj": summary.get("energy_uj"),
                    "energy_efficiency_x": summary.get("energy_efficiency_x"),
                },
                "deltas_vs_baseline": {
                    "latency_ms": _numeric_delta(summary.get("latency_ms"), baseline_summary.get("latency_ms")),
                    "latency_percent": _percent_delta(summary.get("latency_ms"), baseline_summary.get("latency_ms")),
                    "energy_uj": _numeric_delta(summary.get("energy_uj"), baseline_summary.get("energy_uj")),
                    "energy_percent": _percent_delta(summary.get("energy_uj"), baseline_summary.get("energy_uj")),
                    "analog_coverage_points": _numeric_delta(
                        summary.get("analog_coverage_percent"),
                        baseline_summary.get("analog_coverage_percent"),
                    ),
                    "fallback_count": _numeric_delta(summary.get("fallback_count"), baseline_summary.get("fallback_count")),
                    "energy_efficiency_x": _numeric_delta(
                        summary.get("energy_efficiency_x"),
                        baseline_summary.get("energy_efficiency_x"),
                    ),
                },
                "is_baseline": index == 0,
            }
        )
    fastest = min(rows, key=lambda item: item["metrics"].get("latency_ms") or float("inf"))
    lowest_energy = min(rows, key=lambda item: item["metrics"].get("energy_uj") or float("inf"))
    best_efficiency = max(rows, key=lambda item: item["metrics"].get("energy_efficiency_x") or float("-inf"))
    strongest_claim = next(
        (row for row in rows if row["overall_status"] not in {"blocked", "missing evidence"}),
        rows[0],
    )
    return {
        "result_type": "project_run_comparison",
        "baseline_run_id": baseline["run_id"],
        "run_count": len(rows),
        "summary": {
            "fastest_run_id": fastest["run_id"],
            "lowest_energy_run_id": lowest_energy["run_id"],
            "best_efficiency_run_id": best_efficiency["run_id"],
            "strongest_claim_run_id": strongest_claim["run_id"],
            "interpretation": "Compare completed inference metrics and evidence status. Lower latency and energy are useful only when the evidence status and claim level are still acceptable.",
        },
        "rows": rows,
    }


@app.get("/health")
def health():
    return {"status": "ok", "service": "analog-ai-model-fit-backend"}


@app.get("/targets")
def targets():
    return TARGET_PROFILES


@app.get("/modalities")
def modalities():
    return modality_profiles()


@app.get("/runtime-modes")
def runtime_mode_list():
    return runtime_modes()


@app.get("/roadmap-journey")
def roadmap_journey(package_id: str | None = None):
    if package_id and not STORE.get_package_metadata(package_id):
        raise HTTPException(status_code=404, detail="Unknown package_id.")
    try:
        return load_roadmap_journey(package_id=package_id)
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/roadmap-demo-package")
def roadmap_demo_package():
    try:
        return load_demo_review_package()
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/roadmap-demo-package/artifacts/{artifact_id}")
def roadmap_demo_artifact(artifact_id: str):
    try:
        return load_demo_review_artifact(artifact_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Unknown demo artifact_id.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/adapters")
def adapters():
    return adapter_registry()


@app.get("/adapters/{adapter_id}/probe")
def probe_adapter(adapter_id: str):
    probe = adapter_probe(adapter_id)
    if not probe:
        raise HTTPException(status_code=404, detail="Unknown adapter_id.")
    return probe


@app.post("/adapters/{adapter_id}/run")
def run_adapter_endpoint(
    adapter_id: str,
    model_id: str,
    target_profile: str = "wearable",
    calibration_profile: str = "sim-wearable-v0",
    modality: str = "vision_classification",
    runtime_mode: str = "balanced",
    dataset_path: str | None = None,
    package_id: str | None = None,
):
    validate_project_settings(target_profile, modality, calibration_profile, runtime_mode)
    model_record = STORE.get(model_id)
    if not model_record:
        raise HTTPException(status_code=404, detail="Unknown model_id.")
    result = run_adapter(
        adapter_id,
        model_record,
        BASE_DIR / ".data" / "adapter-runs",
        target_profile=target_profile,
        calibration_profile=calibration_profile,
        modality=modality,
        runtime_mode=runtime_mode,
        dataset_path=dataset_path,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Adapter does not have a runnable local implementation yet.")
    if package_id:
        saved = STORE.save_adapter_run(package_id, result)
        if not saved:
            raise HTTPException(status_code=404, detail="Unknown package_id.")
        result["saved_adapter_run"] = {
            "package_id": package_id,
            "path": saved.get("path"),
            "audit_rule": saved.get("audit_rule"),
        }
        refresh_saved_package_archive(package_id)
    return result


def save_evidence_payload(source_id, payload, package_id, run_id=None):
    errors = validate_imported_evidence(source_id, payload)
    if errors:
        return None, errors
    record = build_import_record(
        source_id,
        payload,
        package_id=package_id,
        run_id=run_id,
    )
    saved = STORE.save_imported_evidence(package_id, record)
    if not saved:
        return None, ["Unknown package_id."]
    return saved, []


def _claim_by_id(claim_readiness):
    return {claim.get("id"): claim for claim in claim_readiness.get("lab_claims", [])}


def evidence_import_preview(source_id, payload=None, package_id=None, valid=False, run_id=None):
    if not package_id:
        return {
            "package_id": None,
            "existing_import_count": 0,
            "latest_import_id": None,
            "claims_affected": [],
            "before_summary": None,
            "after_summary": None,
            "plain_reading": "Validation checks artifact structure only. Build or select a package to preview claim impact.",
        }
    artifacts, before_measurement = current_package_measurement_or_404(package_id)
    before_claim_readiness = build_claim_readiness(before_measurement, package_report=artifacts["package"])
    imported = STORE.list_imported_evidence(package_id) or []
    records = [record for record in imported if record.get("source_id") == source_id]
    latest = sorted(records, key=lambda record: record.get("created_at", ""))[-1] if records else None
    after_claim_readiness = None
    if valid and isinstance(payload, dict):
        proposed = build_import_record(source_id, payload, package_id=package_id, run_id=run_id)
        after_measurement = build_measurement_evidence(
            artifacts["adapters"],
            runtime_profile=artifacts["runtime"],
            baseline_report=artifacts["baseline"],
            package_report=artifacts["package"],
            imported_evidence=imported + [proposed],
        )
        after_claim_readiness = build_claim_readiness(after_measurement, package_report=artifacts["package"])
    before_by_id = _claim_by_id(before_claim_readiness)
    after_by_id = _claim_by_id(after_claim_readiness or before_claim_readiness)
    claims = []
    for claim_id, before in before_by_id.items():
        if source_id not in before.get("required_sources", []):
            continue
        after = after_by_id.get(claim_id, before)
        before_status = before.get("status")
        after_status = after.get("status")
        after_missing = after.get("missing_sources", [])
        if not valid:
            plain_impact = "This artifact cannot change the claim until validation errors are fixed."
        elif before_status != after_status:
            plain_impact = f"This import would move the claim from {before_status} to {after_status}."
        elif after_missing:
            plain_impact = f"This import helps, but the claim still needs: {', '.join(after_missing)}."
        else:
            plain_impact = "This import would keep the claim at the same status, but it would become the latest evidence for this source."
        claims.append({
            "id": before.get("id"),
            "name": before.get("name"),
            "before_status": before_status,
            "after_status": after_status if valid else None,
            "before_missing": before.get("missing_sources", []),
            "after_missing": after_missing if valid else before.get("missing_sources", []),
            "before_quality_issues": before.get("quality_issues", []),
            "after_quality_issues": after.get("quality_issues", []) if valid else before.get("quality_issues", []),
            "safe_statement_after": after.get("safe_statement") if valid else None,
            "plain_impact": plain_impact,
        })
    before_summary = before_claim_readiness.get("summary", {})
    after_summary = after_claim_readiness.get("summary", {}) if after_claim_readiness else None
    return {
        "package_id": package_id,
        "existing_import_count": len(records),
        "latest_import_id": latest.get("import_id") if latest else None,
        "claims_affected": claims,
        "before_summary": before_summary,
        "after_summary": after_summary,
        "plain_reading": "Fix validation errors before using this artifact to forecast claim changes." if not valid else "This source already has imported evidence; a new artifact adds another record and the latest import will drive package evidence views." if records else "This source has no imported evidence for this package yet.",
    }


@app.post("/evidence/validate")
async def validate_evidence(
    request: Request,
    source_id: str,
    package_id: str | None = None,
    run_id: str | None = None,
):
    resolved_package_id = None
    run = None
    if package_id or run_id:
        resolved_package_id, run = package_id_from_package_or_run(package_id=package_id, run_id=run_id)
    try:
        payload = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Request body must be a JSON evidence artifact.") from exc
    report = build_validation_report(source_id, payload)
    report["preview"] = evidence_import_preview(
        source_id,
        payload=payload,
        package_id=resolved_package_id,
        valid=report["valid"],
        run_id=(run or {}).get("run_id") or run_id,
    )
    return report


@app.post("/evidence/import")
async def import_evidence(
    request: Request,
    source_id: str,
    package_id: str | None = None,
    run_id: str | None = None,
):
    resolved_package_id, run = package_id_from_package_or_run(package_id=package_id, run_id=run_id)
    try:
        payload = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Request body must be a JSON evidence artifact.") from exc
    saved, errors = save_evidence_payload(
        source_id,
        payload,
        resolved_package_id,
        run_id=(run or {}).get("run_id") or run_id,
    )
    if errors:
        raise HTTPException(status_code=400, detail={"message": "Evidence artifact failed validation.", "errors": errors})
    refresh_saved_package_archive(resolved_package_id)
    return saved


@app.post("/evidence/validate-measured")
async def validate_measured_evidence(
    request: Request,
    source_id: str,
    package_id: str | None = None,
    run_id: str | None = None,
):
    resolved_package_id = None
    run = None
    if package_id or run_id:
        resolved_package_id, run = package_id_from_package_or_run(package_id=package_id, run_id=run_id)
    try:
        payload = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Request body must be a JSON measured-evidence artifact.") from exc
    report = build_validation_report(source_id, payload)
    report["measured_readiness"] = build_measured_readiness_report(source_id, payload)
    report["preview"] = evidence_import_preview(
        source_id,
        payload=payload,
        package_id=resolved_package_id,
        valid=report["valid"],
        run_id=(run or {}).get("run_id") or run_id,
    )
    return report


@app.post("/evidence/validate-tool")
async def validate_tool_evidence(
    request: Request,
    source_id: str,
    package_id: str | None = None,
    run_id: str | None = None,
):
    resolved_package_id = None
    run = None
    if package_id or run_id:
        resolved_package_id, run = package_id_from_package_or_run(package_id=package_id, run_id=run_id)
    try:
        payload = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Request body must be a JSON tool-evidence artifact.") from exc
    report = build_validation_report(source_id, payload)
    report["tool_readiness"] = build_tool_readiness_report(source_id, payload)
    report["preview"] = evidence_import_preview(
        source_id,
        payload=payload,
        package_id=resolved_package_id,
        valid=report["valid"],
        run_id=(run or {}).get("run_id") or run_id,
    )
    return report


@app.post("/evidence/import-measured")
async def import_measured_evidence(
    request: Request,
    source_id: str,
    package_id: str | None = None,
    run_id: str | None = None,
):
    resolved_package_id, run = package_id_from_package_or_run(package_id=package_id, run_id=run_id)
    try:
        payload = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Request body must be a JSON measured-evidence artifact.") from exc
    readiness = build_measured_readiness_report(source_id, payload)
    if not readiness["measured_ready"]:
        raise HTTPException(status_code=400, detail={"message": "Evidence is structurally useful but not measured enough for a measured-claim import.", "measured_readiness": readiness})
    saved, errors = save_evidence_payload(
        source_id,
        payload,
        resolved_package_id,
        run_id=(run or {}).get("run_id") or run_id,
    )
    if errors:
        raise HTTPException(status_code=400, detail={"message": "Measured evidence artifact failed validation.", "errors": errors, "measured_readiness": readiness})
    refresh_saved_package_archive(resolved_package_id)
    saved["measured_readiness"] = readiness
    return saved


@app.post("/evidence/import-tool")
async def import_tool_evidence(
    request: Request,
    source_id: str,
    package_id: str | None = None,
    run_id: str | None = None,
):
    resolved_package_id, run = package_id_from_package_or_run(package_id=package_id, run_id=run_id)
    try:
        payload = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Request body must be a JSON tool-evidence artifact.") from exc
    readiness = build_tool_readiness_report(source_id, payload)
    if not readiness["tool_ready"]:
        raise HTTPException(status_code=400, detail={"message": "Evidence is structurally useful but not ready for the strict tool-evidence import path.", "tool_readiness": readiness})
    saved, errors = save_evidence_payload(
        source_id,
        payload,
        resolved_package_id,
        run_id=(run or {}).get("run_id") or run_id,
    )
    if errors:
        raise HTTPException(status_code=400, detail={"message": "Tool evidence artifact failed validation.", "errors": errors, "tool_readiness": readiness})
    refresh_saved_package_archive(resolved_package_id)
    saved["tool_readiness"] = readiness
    return saved


@app.post("/evidence/import-batch")
async def import_evidence_batch(
    request: Request,
    package_id: str | None = None,
    run_id: str | None = None,
):
    resolved_package_id, run = package_id_from_package_or_run(package_id=package_id, run_id=run_id)
    try:
        payload = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Request body must be a JSON batch artifact.") from exc
    items = payload.get("items") if isinstance(payload, dict) else None
    if not isinstance(items, list) or not items:
        raise HTTPException(status_code=400, detail="Batch body must contain a non-empty items list.")
    accepted = []
    rejected = []
    for index, item in enumerate(items):
        source_id = item.get("source_id") if isinstance(item, dict) else None
        evidence_payload = item.get("payload") if isinstance(item, dict) else None
        saved, errors = save_evidence_payload(
            source_id,
            evidence_payload,
            resolved_package_id,
            run_id=(run or {}).get("run_id") or run_id,
        )
        if errors:
            rejected.append({"index": index, "source_id": source_id, "errors": errors})
        else:
            accepted.append(saved)
    if accepted:
        refresh_saved_package_archive(resolved_package_id)
    return {
        "result_type": "imported_evidence_batch",
        "package_id": resolved_package_id,
        "accepted_count": len(accepted),
        "rejected_count": len(rejected),
        "accepted": accepted,
        "rejected": rejected,
    }


@app.post("/deployment-packages/{package_id}/local-evidence")
def run_package_local_evidence(package_id: str, force: bool = False):
    return run_and_import_local_evidence(package_id, force=force)


@app.post("/deployment-packages/{package_id}/hardware-lab-evidence")
def import_package_hardware_lab_evidence(package_id: str, force: bool = False):
    return import_hardware_lab_evidence(package_id, force=force)


@app.get("/evidence/imports")
def list_imported_evidence(package_id: str | None = None, run_id: str | None = None):
    resolved_package_id, _ = package_id_from_package_or_run(package_id=package_id, run_id=run_id)
    records = STORE.list_imported_evidence(resolved_package_id)
    if records is None:
        raise HTTPException(status_code=404, detail="Unknown package_id.")
    return {
        "result_type": "imported_evidence_list",
        "package_id": resolved_package_id,
        "count": len(records),
        "imports": records,
    }


@app.get("/calibration-profiles")
def calibration_profiles():
    return list_calibration_profiles()


@app.get("/calibration-profiles/{profile_id}")
def calibration_profile(profile_id: str):
    return get_calibration_profile(profile_id)


@app.get("/models")
def list_models():
    return {"models": STORE.list_models()}


@app.get("/projects")
def list_projects():
    return {"projects": STORE.list_projects()}


@app.get("/project-runs")
def list_all_project_runs():
    return {"runs": STORE.list_project_runs()}


@app.get("/project-runs/compare")
def compare_project_runs(run_ids: str):
    ids = [item.strip() for item in run_ids.split(",") if item.strip()]
    if len(ids) < 2:
        raise HTTPException(status_code=400, detail="Provide at least two run IDs in run_ids.")
    runs = []
    for run_id in ids:
        run = STORE.get_project_run(run_id)
        if not run:
            raise HTTPException(status_code=404, detail=f"Unknown run_id: {run_id}")
        runs.append(run)
    return build_run_comparison(runs)


@app.get("/project-runs/{run_id}")
def get_project_run(run_id: str):
    run = STORE.get_project_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Unknown run_id.")
    return run


@app.post("/projects")
def create_project(
    name: str = "Analog AI evaluation",
    target_profile: str = "wearable",
    modality: str = "audio_wake_word",
    calibration_profile: str = "sim-wearable-v0",
    runtime_mode: str = "balanced",
):
    validate_project_settings(target_profile, modality, calibration_profile, runtime_mode)
    return STORE.create_project(
        name,
        target_profile=target_profile,
        modality=modality,
        calibration_profile=calibration_profile,
        runtime_mode=runtime_mode,
    )


@app.get("/projects/{project_id}")
def get_project(project_id: str):
    project = STORE.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Unknown project_id.")
    return project


@app.patch("/projects/{project_id}")
def update_project(
    project_id: str,
    name: str | None = None,
    target_profile: str | None = None,
    modality: str | None = None,
    calibration_profile: str | None = None,
    runtime_mode: str | None = None,
):
    project = STORE.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Unknown project_id.")
    next_target = target_profile if target_profile is not None else project.get("target_profile", "wearable")
    next_modality = modality if modality is not None else project.get("modality", "vision_classification")
    next_calibration = calibration_profile if calibration_profile is not None else project.get("calibration_profile", "sim-wearable-v0")
    next_runtime = runtime_mode if runtime_mode is not None else project.get("runtime_mode", "balanced")
    validate_project_settings(next_target, next_modality, next_calibration, next_runtime)
    return STORE.update_project(
        project_id,
        name=name,
        target_profile=next_target,
        modality=next_modality,
        calibration_profile=next_calibration,
        runtime_mode=next_runtime,
    )


@app.get("/projects/{project_id}/runs")
def list_runs_for_project(project_id: str):
    project = STORE.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Unknown project_id.")
    return {"project": project, "runs": STORE.list_project_runs(project_id)}


@app.get("/projects/{project_id}/runs/compare")
def compare_runs_for_project(project_id: str, limit: int = 4):
    project = STORE.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Unknown project_id.")
    latest_runs = STORE.list_project_runs(project_id)[: max(2, min(limit, 8))]
    if len(latest_runs) < 2:
        raise HTTPException(status_code=400, detail="Project needs at least two saved runs to compare.")
    runs = list(reversed(latest_runs))
    comparison = build_run_comparison(runs)
    comparison["project"] = project
    return comparison


@app.post("/projects/{project_id}/runs")
def run_project_evaluation(project_id: str, model_id: str | None = None):
    project = STORE.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Unknown project_id.")
    selected_model_id = model_id or (project.get("model_ids") or [None])[-1]
    if not selected_model_id:
        raise HTTPException(status_code=400, detail="Project has no imported models to evaluate.")
    if selected_model_id not in project.get("model_ids", []):
        raise HTTPException(status_code=400, detail="model_id is not attached to this project.")
    record = STORE.get(selected_model_id)
    if not record:
        raise HTTPException(status_code=404, detail="Unknown model_id in this project.")
    try:
        artifacts = build_artifact_bundle(
            record,
            selected_model_id,
            project.get("target_profile", "wearable"),
            project.get("calibration_profile", "sim-wearable-v0"),
            project.get("modality", "vision_classification"),
            project.get("runtime_mode", "balanced"),
            project_context=project,
        )
        _, _, metadata = persist_artifact_bundle(record, selected_model_id, artifacts)
        run_record = STORE.save_project_run(project_id, selected_model_id, artifacts["package"]["package_id"], artifacts)
        return {
            "result_type": "project_evaluation_run",
            "project": STORE.get_project(project_id),
            "run": run_record,
            "run_id": run_record["run_id"],
            "model_id": selected_model_id,
            "package_id": artifacts["package"]["package_id"],
            "summary": run_record["summary"] | {
                "archive": artifacts["package"]["saved_artifacts"]["archive"],
                "review_markdown": artifacts["package"]["saved_artifacts"]["review_markdown"],
            },
            "artifacts": artifacts,
            "saved_artifacts": artifacts["package"]["saved_artifacts"],
            "metadata": metadata,
        }
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not run project evaluation: {exc}") from exc


@app.post("/models/import")
async def import_model(
    request: Request,
    filename: str = "model.onnx",
    target_profile: str = "wearable",
    calibration_profile: str = "sim-wearable-v0",
    project_id: str | None = None,
):
    if not filename.lower().endswith(".onnx"):
        raise HTTPException(status_code=400, detail="Only .onnx files are supported in this milestone.")
    content = await request.body()
    if not content:
        raise HTTPException(status_code=400, detail="Request body must contain ONNX model bytes.")
    record = STORE.save_upload(filename, content)
    if project_id and not STORE.attach_model_to_project(project_id, record["model_id"]):
        raise HTTPException(status_code=404, detail="Unknown project_id.")
    try:
        analysis = analyze_model(record["path"], target_profile=target_profile, calibration_profile=calibration_profile)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not parse ONNX model: {exc}") from exc
    return {"model_id": record["model_id"], "analysis": analysis}


@app.get("/models/{model_id}")
def get_model(model_id: str):
    record = STORE.get(model_id)
    if not record:
        raise HTTPException(status_code=404, detail="Unknown model_id.")
    return {
        "model_id": record["model_id"],
        "filename": record["filename"],
        "path": record["path"],
        "recovered": record.get("recovered", False),
    }


@app.get("/models/{model_id}/graph")
def get_model_graph(model_id: str, target_profile: str = "wearable", calibration_profile: str = "sim-wearable-v0"):
    record = STORE.get(model_id)
    if not record:
        raise HTTPException(status_code=404, detail="Unknown model_id in this in-memory prototype store.")
    try:
        return analyze_model(record["path"], target_profile=target_profile, calibration_profile=calibration_profile)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not parse ONNX model: {exc}") from exc


@app.post("/models/{model_id}/quantize")
def quantize_model(
    model_id: str,
    target_profile: str = "wearable",
    calibration_profile: str = "sim-wearable-v0",
    modality: str = "vision_classification",
    task_type: str | None = None,
    primary_failure_cost: str | None = None,
):
    record = STORE.get(model_id)
    if not record:
        raise HTTPException(status_code=404, detail="Unknown model_id in this in-memory prototype store.")
    try:
        analysis = analyze_model(record["path"], target_profile=target_profile, calibration_profile=calibration_profile)
        return estimate_quantization(
            analysis,
            modality=modality,
            task_type=task_type,
            primary_failure_cost=primary_failure_cost,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not estimate quantization: {exc}") from exc


@app.post("/models/{model_id}/runtime-profile")
def runtime_profile(
    model_id: str,
    target_profile: str = "wearable",
    calibration_profile: str = "sim-wearable-v0",
    modality: str = "vision_classification",
    runtime_mode: str = "balanced",
):
    record = STORE.get(model_id)
    if not record:
        raise HTTPException(status_code=404, detail="Unknown model_id in this in-memory prototype store.")
    try:
        analysis = analyze_model(record["path"], target_profile=target_profile, calibration_profile=calibration_profile)
        quantization_report = estimate_quantization(analysis, modality=modality)
        return run_simulated_profile(
            analysis,
            quantization_report=quantization_report,
            runtime_mode=runtime_mode,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not run runtime profile: {exc}") from exc


@app.post("/models/{model_id}/deployment-package")
def deployment_package(
    model_id: str,
    target_profile: str = "wearable",
    calibration_profile: str = "sim-wearable-v0",
    modality: str = "vision_classification",
    runtime_mode: str = "balanced",
    project_id: str | None = None,
):
    record = STORE.get(model_id)
    if not record:
        raise HTTPException(status_code=404, detail="Unknown model_id in this in-memory prototype store.")
    try:
        project_context = project_context_or_404(project_id)
        artifacts = build_artifact_bundle(
            record,
            model_id,
            target_profile,
            calibration_profile,
            modality,
            runtime_mode,
            project_context=project_context,
        )
        persist_artifact_bundle(record, model_id, artifacts)
        if project_id:
            STORE.attach_package_to_project(project_id, artifacts["package"]["package_id"])
        return artifacts["package"]
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not build deployment package report: {exc}") from exc


@app.post("/models/{model_id}/baseline-comparison")
def baseline_comparison(
    model_id: str,
    target_profile: str = "wearable",
    calibration_profile: str = "sim-wearable-v0",
    modality: str = "vision_classification",
    runtime_mode: str = "balanced",
):
    record = STORE.get(model_id)
    if not record:
        raise HTTPException(status_code=404, detail="Unknown model_id in this in-memory prototype store.")
    try:
        analysis = analyze_model(record["path"], target_profile=target_profile, calibration_profile=calibration_profile)
        quantization_report = estimate_quantization(analysis, modality=modality)
        runtime_report = run_simulated_profile(
            analysis,
            quantization_report=quantization_report,
            runtime_mode=runtime_mode,
        )
        return compare_to_digital_baseline(analysis, runtime_report, target_profile=target_profile)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not compare against digital baseline: {exc}") from exc


@app.post("/models/{model_id}/measurement-evidence")
def measurement_evidence(
    model_id: str,
    target_profile: str = "wearable",
    calibration_profile: str = "sim-wearable-v0",
    modality: str = "vision_classification",
    runtime_mode: str = "balanced",
    project_id: str | None = None,
):
    record = STORE.get(model_id)
    if not record:
        raise HTTPException(status_code=404, detail="Unknown model_id in this in-memory prototype store.")
    try:
        project_context = project_context_or_404(project_id)
        return build_artifact_bundle(
            record,
            model_id,
            target_profile,
            calibration_profile,
            modality,
            runtime_mode,
            project_context=project_context,
        )["measurement"]
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not build measurement evidence contract: {exc}") from exc


@app.post("/models/{model_id}/evidence-gates")
def evidence_gates(
    model_id: str,
    target_profile: str = "wearable",
    calibration_profile: str = "sim-wearable-v0",
    modality: str = "vision_classification",
    runtime_mode: str = "balanced",
    project_id: str | None = None,
):
    record = STORE.get(model_id)
    if not record:
        raise HTTPException(status_code=404, detail="Unknown model_id in this in-memory prototype store.")
    try:
        project_context = project_context_or_404(project_id)
        return build_artifact_bundle(
            record,
            model_id,
            target_profile,
            calibration_profile,
            modality,
            runtime_mode,
            project_context=project_context,
        )["evidence"]
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not build evidence gates: {exc}") from exc


@app.post("/models/{model_id}/review-report")
def review_report(
    model_id: str,
    target_profile: str = "wearable",
    calibration_profile: str = "sim-wearable-v0",
    modality: str = "vision_classification",
    runtime_mode: str = "balanced",
    project_id: str | None = None,
):
    record = STORE.get(model_id)
    if not record:
        raise HTTPException(status_code=404, detail="Unknown model_id in this in-memory prototype store.")
    try:
        project_context = project_context_or_404(project_id)
        return build_artifact_bundle(
            record,
            model_id,
            target_profile,
            calibration_profile,
            modality,
            runtime_mode,
            project_context=project_context,
        )["review"]
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not build review report: {exc}") from exc


@app.post("/models/{model_id}/decision-report")
def decision_report(
    model_id: str,
    target_profile: str = "wearable",
    calibration_profile: str = "sim-wearable-v0",
    modality: str = "vision_classification",
    runtime_mode: str = "balanced",
    project_id: str | None = None,
):
    record = STORE.get(model_id)
    if not record:
        raise HTTPException(status_code=404, detail="Unknown model_id in this in-memory prototype store.")
    try:
        project_context = project_context_or_404(project_id)
        return build_artifact_bundle(
            record,
            model_id,
            target_profile,
            calibration_profile,
            modality,
            runtime_mode,
            project_context=project_context,
        )["decision"]
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not build decision report: {exc}") from exc


@app.post("/models/{model_id}/rewrite-suggestions")
def rewrite_suggestions(
    model_id: str,
    target_profile: str = "wearable",
    calibration_profile: str = "sim-wearable-v0",
    modality: str = "vision_classification",
    runtime_mode: str = "balanced",
    project_id: str | None = None,
):
    record = STORE.get(model_id)
    if not record:
        raise HTTPException(status_code=404, detail="Unknown model_id in this in-memory prototype store.")
    try:
        project_context = project_context_or_404(project_id)
        return build_artifact_bundle(
            record,
            model_id,
            target_profile,
            calibration_profile,
            modality,
            runtime_mode,
            project_context=project_context,
        )["rewrites"]
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not build rewrite suggestions: {exc}") from exc


@app.post("/models/{model_id}/rewrite-what-if")
def rewrite_what_if(
    model_id: str,
    target_profile: str = "wearable",
    calibration_profile: str = "sim-wearable-v0",
    modality: str = "vision_classification",
    runtime_mode: str = "balanced",
    project_id: str | None = None,
    suggestion_ids: str | None = None,
):
    record = STORE.get(model_id)
    if not record:
        raise HTTPException(status_code=404, detail="Unknown model_id in this in-memory prototype store.")
    try:
        project_context = project_context_or_404(project_id)
        artifacts = build_artifact_bundle(
            record,
            model_id,
            target_profile,
            calibration_profile,
            modality,
            runtime_mode,
            project_context=project_context,
        )
        return build_rewrite_what_if(
            artifacts["analysis"],
            artifacts["runtime"],
            artifacts["decision"],
            artifacts["rewrites"],
            suggestion_ids=suggestion_ids,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not run rewrite what-if: {exc}") from exc


@app.post("/models/{model_id}/rewrite-plan")
def rewrite_plan(
    model_id: str,
    target_profile: str = "wearable",
    calibration_profile: str = "sim-wearable-v0",
    modality: str = "vision_classification",
    runtime_mode: str = "balanced",
    project_id: str | None = None,
    suggestion_ids: str | None = None,
):
    record = STORE.get(model_id)
    if not record:
        raise HTTPException(status_code=404, detail="Unknown model_id in this in-memory prototype store.")
    try:
        project_context = project_context_or_404(project_id)
        artifacts = build_artifact_bundle(
            record,
            model_id,
            target_profile,
            calibration_profile,
            modality,
            runtime_mode,
            project_context=project_context,
        )
        what_if_report = build_rewrite_what_if(
            artifacts["analysis"],
            artifacts["runtime"],
            artifacts["decision"],
            artifacts["rewrites"],
            suggestion_ids=suggestion_ids,
        )
        return build_rewrite_plan(
            artifacts["analysis"],
            artifacts["quantization"],
            artifacts["runtime"],
            artifacts["decision"],
            artifacts["rewrites"],
            what_if_report,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not build rewrite plan: {exc}") from exc


@app.post("/models/{model_id}/rewrite-work-order")
def rewrite_work_order(
    model_id: str,
    target_profile: str = "wearable",
    calibration_profile: str = "sim-wearable-v0",
    modality: str = "vision_classification",
    runtime_mode: str = "balanced",
    project_id: str | None = None,
    suggestion_ids: str | None = None,
):
    record = STORE.get(model_id)
    if not record:
        raise HTTPException(status_code=404, detail="Unknown model_id in this in-memory prototype store.")
    try:
        project_context = project_context_or_404(project_id)
        artifacts = build_artifact_bundle(
            record,
            model_id,
            target_profile,
            calibration_profile,
            modality,
            runtime_mode,
            project_context=project_context,
        )
        what_if_report = build_rewrite_what_if(
            artifacts["analysis"],
            artifacts["runtime"],
            artifacts["decision"],
            artifacts["rewrites"],
            suggestion_ids=suggestion_ids,
        )
        plan_report = build_rewrite_plan(
            artifacts["analysis"],
            artifacts["quantization"],
            artifacts["runtime"],
            artifacts["decision"],
            artifacts["rewrites"],
            what_if_report,
        )
        return build_rewrite_work_order(
            artifacts["analysis"],
            plan_report,
            project_context=project_context,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not build rewrite work order: {exc}") from exc


@app.get("/models/{model_id}/deployment-package/archive")
def deployment_package_archive(
    model_id: str,
    target_profile: str = "wearable",
    calibration_profile: str = "sim-wearable-v0",
    modality: str = "vision_classification",
    runtime_mode: str = "balanced",
    project_id: str | None = None,
):
    record = STORE.get(model_id)
    if not record:
        raise HTTPException(status_code=404, detail="Unknown model_id in this in-memory prototype store.")
    try:
        project_context = project_context_or_404(project_id)
        artifacts = build_artifact_bundle(
            record,
            model_id,
            target_profile,
            calibration_profile,
            modality,
            runtime_mode,
            project_context=project_context,
        )
        archive, filename, _ = persist_artifact_bundle(record, model_id, artifacts)
        if project_id:
            STORE.attach_package_to_project(project_id, artifacts["package"]["package_id"])
        return Response(
            archive,
            media_type="application/zip",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not build deployment archive: {exc}") from exc


@app.get("/deployment-packages/{package_id}")
def get_saved_package(package_id: str):
    package = STORE.get_package_artifact(package_id, "package")
    if not package:
        raise HTTPException(status_code=404, detail="Unknown package_id.")
    return package


@app.get("/deployment-packages")
def list_saved_packages():
    return {"packages": STORE.list_packages()}


@app.get("/deployment-packages/{package_id}/review-report")
def get_saved_review_report(package_id: str):
    review = STORE.get_package_artifact(package_id, "review")
    if not review:
        raise HTTPException(status_code=404, detail="Unknown package_id or missing review report.")
    return review


@app.get("/deployment-packages/{package_id}/artifacts")
def get_saved_package_artifacts(package_id: str):
    bundle = STORE.get_package_artifacts(package_id)
    if not bundle:
        raise HTTPException(status_code=404, detail="Unknown package_id or missing artifact bundle.")
    if (
        not bundle["artifacts"].get("physical_ai_map")
        or not bundle["artifacts"].get("vla_readiness")
        or not bundle["artifacts"].get("weight_update_readiness")
        or not bundle["artifacts"].get("calibration_drift_readiness")
        or not bundle["artifacts"].get("control_boundary")
        or not bundle["artifacts"].get("sensor_boundary_readiness")
        or not bundle["artifacts"].get("compiler_ecosystem_readiness")
        or not bundle["artifacts"].get("physical_ai_roadmap")
        or not bundle["artifacts"].get("source_check_register")
        or not bundle["artifacts"].get("hardware_placement")
        or not bundle["artifacts"].get("residual_aware_placement")
    ):
        refresh_saved_package_archive(package_id)
        bundle = STORE.get_package_artifacts(package_id)
        if not bundle:
            raise HTTPException(status_code=404, detail="Unknown package_id or missing artifact bundle.")
    if (
        not bundle["artifacts"].get("physical_ai_map")
        or not bundle["artifacts"].get("vla_readiness")
        or not bundle["artifacts"].get("weight_update_readiness")
        or not bundle["artifacts"].get("calibration_drift_readiness")
        or not bundle["artifacts"].get("control_boundary")
        or not bundle["artifacts"].get("sensor_boundary_readiness")
        or not bundle["artifacts"].get("compiler_ecosystem_readiness")
        or not bundle["artifacts"].get("physical_ai_roadmap")
        or not bundle["artifacts"].get("source_check_register")
        or not bundle["artifacts"].get("hardware_placement")
    ):
        artifacts = bundle["artifacts"]
        _, measurement = current_package_measurement_or_404(package_id)
        system_boundary = current_package_system_boundary_or_404(package_id)
        derived = {}
        if not artifacts.get("hardware_placement"):
            derived["hardware_placement"] = build_hardware_placement(
                artifacts["analysis"],
                package_report=artifacts["package"],
            )
        if not artifacts.get("physical_ai_map"):
            derived["physical_ai_map"] = build_physical_ai_map(
                artifacts["package"],
                workload_fit=current_package_workload_fit_or_404(package_id),
                system_boundary=system_boundary,
                measurement_evidence=measurement,
            )
        if not artifacts.get("vla_readiness"):
            derived["vla_readiness"] = build_vla_readiness(
                artifacts["analysis"],
                artifacts["quantization"],
                artifacts["runtime"],
                system_boundary,
                package_report=artifacts["package"],
            )
        vla_for_weight_update = artifacts.get("vla_readiness") or derived.get("vla_readiness")
        if not artifacts.get("weight_update_readiness"):
            derived["weight_update_readiness"] = build_weight_update_readiness(
                artifacts["package"],
                vla_readiness=vla_for_weight_update,
                measurement_evidence=measurement,
            )
        if not artifacts.get("calibration_drift_readiness"):
            derived["calibration_drift_readiness"] = build_calibration_drift_readiness(
                artifacts["package"],
                artifacts["analysis"],
                measurement_evidence=measurement,
            )
        physical_ai_for_control = artifacts.get("physical_ai_map") or derived.get("physical_ai_map")
        if not artifacts.get("control_boundary"):
            derived["control_boundary"] = build_control_boundary(
                artifacts["package"],
                physical_ai_map=physical_ai_for_control,
                runtime_profile=artifacts["runtime"],
                system_boundary=system_boundary,
                measurement_evidence=measurement,
            )
        if not artifacts.get("sensor_boundary_readiness"):
            derived["sensor_boundary_readiness"] = build_sensor_boundary_readiness(
                artifacts["package"],
                physical_ai_map=physical_ai_for_control,
                runtime_profile=artifacts["runtime"],
                system_boundary=system_boundary,
                measurement_evidence=measurement,
            )
        if not artifacts.get("compiler_ecosystem_readiness"):
            derived["compiler_ecosystem_readiness"] = build_compiler_ecosystem_readiness(
                artifacts["adapters"],
                current_package_external_connector_contract_or_404(package_id),
                current_package_connection_playbook_or_404(package_id),
                artifacts["analysis"],
                package_report=artifacts["package"],
                toolchain_readiness=current_package_toolchain_readiness_or_404(package_id),
                measurement_evidence=measurement,
            )
        if not artifacts.get("source_check_register"):
            derived["source_check_register"] = build_source_check_register(artifacts["package"])
        if not artifacts.get("physical_ai_roadmap"):
            claim_readiness = build_claim_readiness(measurement, package_report=artifacts["package"])
            evidence_audit = build_evidence_audit_from_records(
                package_id,
                measurement,
                claim_readiness,
                STORE.list_imported_evidence(package_id) or [],
            )
            derived["physical_ai_roadmap"] = build_physical_ai_roadmap(
                artifacts["package"],
                artifacts["analysis"],
                artifacts["runtime"],
                physical_ai_map=artifacts.get("physical_ai_map") or derived.get("physical_ai_map"),
                vla_readiness=artifacts.get("vla_readiness") or derived.get("vla_readiness"),
                weight_update_readiness=artifacts.get("weight_update_readiness") or derived.get("weight_update_readiness"),
                calibration_drift_readiness=artifacts.get("calibration_drift_readiness") or derived.get("calibration_drift_readiness"),
                control_boundary=artifacts.get("control_boundary") or derived.get("control_boundary"),
                sensor_boundary_readiness=artifacts.get("sensor_boundary_readiness") or derived.get("sensor_boundary_readiness"),
                compiler_ecosystem_readiness=artifacts.get("compiler_ecosystem_readiness") or derived.get("compiler_ecosystem_readiness"),
                measurement_evidence=measurement,
                claim_readiness=claim_readiness,
                evidence_audit=evidence_audit,
                source_check_register=artifacts.get("source_check_register") or derived.get("source_check_register"),
            )
        bundle = {
            **bundle,
            "artifacts": {
                **artifacts,
                **derived,
            },
        }
    return {"result_type": "saved_package_artifacts", **bundle}


@app.get("/deployment-packages/{package_id}/decision-report")
def get_saved_decision_report(package_id: str):
    decision = STORE.get_package_artifact(package_id, "decision")
    if not decision:
        raise HTTPException(status_code=404, detail="Unknown package_id or missing decision report.")
    return decision


@app.get("/deployment-packages/{package_id}/measurement-evidence")
def get_saved_measurement_evidence(package_id: str):
    _, measurement = current_package_measurement_or_404(package_id)
    return measurement


@app.get("/deployment-packages/{package_id}/hardware-placement")
def get_saved_hardware_placement(package_id: str):
    artifacts = get_saved_package_artifacts(package_id)["artifacts"]
    placement = artifacts.get("hardware_placement")
    if not placement:
        raise HTTPException(status_code=404, detail="Unknown package_id or missing hardware placement.")
    return placement


@app.get("/deployment-packages/{package_id}/residual-aware-placement")
def get_saved_residual_aware_placement(package_id: str):
    artifacts = get_saved_package_artifacts(package_id)["artifacts"]
    placement = artifacts.get("hardware_placement")
    if not placement:
        raise HTTPException(status_code=404, detail="Unknown package_id or missing hardware placement.")
    return load_residual_aware_placement(placement)


@app.get("/deployment-packages/{package_id}/workload-fit")
def get_saved_workload_fit(package_id: str):
    return current_package_workload_fit_or_404(package_id)


@app.get("/deployment-packages/{package_id}/system-boundary")
def get_saved_system_boundary(package_id: str):
    return current_package_system_boundary_or_404(package_id)


@app.get("/deployment-packages/{package_id}/physical-ai-map")
def get_saved_physical_ai_map(package_id: str):
    return current_package_physical_ai_map_or_404(package_id)


@app.get("/deployment-packages/{package_id}/physical-ai-roadmap")
def get_saved_physical_ai_roadmap(package_id: str):
    return current_package_physical_ai_roadmap_or_404(package_id)


@app.get("/deployment-packages/{package_id}/vla-readiness")
def get_saved_vla_readiness(package_id: str):
    return current_package_vla_readiness_or_404(package_id)


@app.get("/deployment-packages/{package_id}/weight-update-readiness")
def get_saved_weight_update_readiness(package_id: str):
    return current_package_weight_update_readiness_or_404(package_id)


@app.get("/deployment-packages/{package_id}/calibration-drift-readiness")
def get_saved_calibration_drift_readiness(package_id: str):
    return current_package_calibration_drift_readiness_or_404(package_id)


@app.get("/deployment-packages/{package_id}/control-boundary")
def get_saved_control_boundary(package_id: str):
    return current_package_control_boundary_or_404(package_id)


@app.get("/deployment-packages/{package_id}/sensor-boundary-readiness")
def get_saved_sensor_boundary_readiness(package_id: str):
    return current_package_sensor_boundary_readiness_or_404(package_id)


@app.get("/deployment-packages/{package_id}/research-guide")
def get_saved_research_guide(package_id: str):
    return current_package_research_guide_or_404(package_id)


@app.get("/deployment-packages/{package_id}/concept-glossary")
def get_saved_concept_glossary(package_id: str):
    return current_package_concept_glossary_or_404(package_id)


@app.get("/deployment-packages/{package_id}/source-check-register")
def get_saved_source_check_register(package_id: str):
    return current_package_source_check_register_or_404(package_id)


@app.get("/deployment-packages/{package_id}/toolchain-readiness")
def get_saved_toolchain_readiness(package_id: str):
    return current_package_toolchain_readiness_or_404(package_id)


@app.get("/deployment-packages/{package_id}/connection-playbook")
def get_saved_connection_playbook(package_id: str):
    return current_package_connection_playbook_or_404(package_id)


@app.get("/deployment-packages/{package_id}/adapter-execution-plan")
def get_saved_adapter_execution_plan(package_id: str):
    return current_package_adapter_execution_plan_or_404(package_id)


@app.get("/deployment-packages/{package_id}/adapter-connection-kit")
def get_saved_adapter_connection_kit(package_id: str):
    return current_package_adapter_connection_kit_or_404(package_id)


@app.get("/deployment-packages/{package_id}/adapter-evidence-templates")
def get_saved_adapter_evidence_templates(package_id: str):
    return current_package_adapter_evidence_templates_or_404(package_id)


@app.get("/deployment-packages/{package_id}/adapter-connection-self-test")
def get_saved_adapter_connection_self_test(package_id: str):
    return current_package_adapter_connection_self_test_or_404(package_id)


@app.get("/deployment-packages/{package_id}/adapter-integration-readiness")
def get_saved_adapter_integration_readiness(package_id: str):
    return current_package_adapter_integration_readiness_or_404(package_id)


@app.get("/deployment-packages/{package_id}/external-connector-contract")
def get_saved_external_connector_contract(package_id: str):
    return current_package_external_connector_contract_or_404(package_id)


@app.get("/deployment-packages/{package_id}/compiler-ecosystem-readiness")
def get_saved_compiler_ecosystem_readiness(package_id: str):
    return current_package_compiler_ecosystem_readiness_or_404(package_id)


@app.get("/deployment-packages/{package_id}/connector-implementation-guide")
def get_saved_connector_implementation_guide(package_id: str):
    return current_package_connector_implementation_guide_or_404(package_id)


@app.get("/deployment-packages/{package_id}/connector-test-harness")
def get_saved_connector_test_harness(package_id: str):
    return current_package_connector_test_harness_or_404(package_id)


@app.get("/deployment-packages/{package_id}/connector-acceptance-drills")
def get_saved_connector_acceptance_drills(package_id: str):
    return current_package_connector_acceptance_drills_or_404(package_id)


@app.get("/deployment-packages/{package_id}/connector-acceptance-report")
def get_saved_connector_acceptance_report(package_id: str):
    return current_package_connector_acceptance_report_or_404(package_id)


@app.get("/deployment-packages/{package_id}/connector-backlog")
def get_saved_connector_backlog(package_id: str):
    return current_package_connector_backlog_or_404(package_id)


@app.get("/deployment-packages/{package_id}/connector-delivery-plan")
def get_saved_connector_delivery_plan(package_id: str):
    return current_package_connector_delivery_plan_or_404(package_id)


@app.get("/deployment-packages/{package_id}/connector-risk-register")
def get_saved_connector_risk_register(package_id: str):
    return current_package_connector_risk_register_or_404(package_id)


@app.get("/deployment-packages/{package_id}/claim-readiness")
def get_saved_claim_readiness(package_id: str):
    artifacts, measurement = current_package_measurement_or_404(package_id)
    return build_claim_readiness(measurement, package_report=artifacts["package"])


@app.get("/deployment-packages/{package_id}/imported-evidence")
def get_package_imported_evidence(package_id: str):
    records = STORE.list_imported_evidence(package_id)
    if records is None:
        raise HTTPException(status_code=404, detail="Unknown package_id.")
    return {
        "result_type": "imported_evidence_list",
        "package_id": package_id,
        "count": len(records),
        "imports": records,
    }


@app.get("/deployment-packages/{package_id}/adapter-runs")
def get_package_adapter_runs(package_id: str):
    records = STORE.list_adapter_runs(package_id)
    if records is None:
        raise HTTPException(status_code=404, detail="Unknown package_id.")
    return {
        "result_type": "adapter_run_list",
        "package_id": package_id,
        "count": len(records),
        "adapter_runs": records,
    }


@app.get("/deployment-packages/{package_id}/evidence-audit")
def get_package_evidence_audit(package_id: str):
    return build_evidence_audit(package_id)


@app.get("/deployment-packages/{package_id}/evidence-brief")
def get_package_evidence_brief(package_id: str):
    return build_current_evidence_brief(package_id)


@app.get("/deployment-packages/{package_id}/evidence-brief.md")
def get_package_evidence_brief_markdown(package_id: str):
    brief = build_current_evidence_brief(package_id)
    return Response(brief["markdown"], media_type="text/markdown")


@app.get("/deployment-packages/{package_id}/interview-brief")
def get_package_interview_brief(package_id: str):
    return build_current_interview_brief(package_id)


@app.get("/deployment-packages/{package_id}/interview-brief.md")
def get_package_interview_brief_markdown(package_id: str):
    brief = build_current_interview_brief(package_id)
    return Response(brief["markdown"], media_type="text/markdown")


@app.get("/deployment-packages/{package_id}/interview-drill")
def get_package_interview_drill(package_id: str):
    return build_current_interview_drill(package_id)


@app.get("/deployment-packages/{package_id}/rewrite-suggestions")
def get_saved_rewrite_suggestions(package_id: str):
    rewrites = STORE.get_package_artifact(package_id, "rewrites")
    if not rewrites:
        raise HTTPException(status_code=404, detail="Unknown package_id or missing rewrite suggestions.")
    return rewrites


@app.get("/deployment-packages/{package_id}/rewrite-what-if")
def get_saved_rewrite_what_if(package_id: str, suggestion_ids: str | None = None):
    bundle = STORE.get_package_artifacts(package_id)
    if not bundle:
        raise HTTPException(status_code=404, detail="Unknown package_id or missing artifact bundle.")
    artifacts = bundle["artifacts"]
    if "decision" not in artifacts or "rewrites" not in artifacts:
        raise HTTPException(status_code=404, detail="Package is missing decision or rewrite artifacts.")
    return build_rewrite_what_if(
        artifacts["analysis"],
        artifacts["runtime"],
        artifacts["decision"],
        artifacts["rewrites"],
        suggestion_ids=suggestion_ids,
    )


@app.get("/deployment-packages/{package_id}/rewrite-plan")
def get_saved_rewrite_plan(package_id: str, suggestion_ids: str | None = None):
    bundle = STORE.get_package_artifacts(package_id)
    if not bundle:
        raise HTTPException(status_code=404, detail="Unknown package_id or missing artifact bundle.")
    artifacts = bundle["artifacts"]
    if "decision" not in artifacts or "rewrites" not in artifacts:
        raise HTTPException(status_code=404, detail="Package is missing decision or rewrite artifacts.")
    if not suggestion_ids and "rewrite_plan" in artifacts:
        return artifacts["rewrite_plan"]
    what_if_report = build_rewrite_what_if(
        artifacts["analysis"],
        artifacts["runtime"],
        artifacts["decision"],
        artifacts["rewrites"],
        suggestion_ids=suggestion_ids,
    )
    return build_rewrite_plan(
        artifacts["analysis"],
        artifacts["quantization"],
        artifacts["runtime"],
        artifacts["decision"],
        artifacts["rewrites"],
        what_if_report,
    )


@app.get("/deployment-packages/{package_id}/rewrite-work-order")
def get_saved_rewrite_work_order(package_id: str, suggestion_ids: str | None = None):
    bundle = STORE.get_package_artifacts(package_id)
    if not bundle:
        raise HTTPException(status_code=404, detail="Unknown package_id or missing artifact bundle.")
    artifacts = bundle["artifacts"]
    if "decision" not in artifacts or "rewrites" not in artifacts:
        raise HTTPException(status_code=404, detail="Package is missing decision or rewrite artifacts.")
    if not suggestion_ids and "rewrite_work_order" in artifacts:
        return artifacts["rewrite_work_order"]
    what_if_report = build_rewrite_what_if(
        artifacts["analysis"],
        artifacts["runtime"],
        artifacts["decision"],
        artifacts["rewrites"],
        suggestion_ids=suggestion_ids,
    )
    plan_report = build_rewrite_plan(
        artifacts["analysis"],
        artifacts["quantization"],
        artifacts["runtime"],
        artifacts["decision"],
        artifacts["rewrites"],
        what_if_report,
    )
    return build_rewrite_work_order(
        artifacts["analysis"],
        plan_report,
        project_context=artifacts["package"].get("project"),
    )


@app.get("/deployment-packages/{package_id}/review-report.md")
def get_saved_review_markdown(package_id: str):
    markdown = STORE.get_package_artifact(package_id, "review_markdown")
    if not markdown:
        raise HTTPException(status_code=404, detail="Unknown package_id or missing review markdown.")
    return Response(markdown, media_type="text/markdown")


@app.get("/deployment-packages/{package_id}/archive")
def get_saved_package_archive(package_id: str):
    saved = STORE.get_package_archive(package_id)
    if not saved:
        raise HTTPException(status_code=404, detail="Unknown package_id or missing archive.")
    metadata, archive = saved
    return Response(
        archive,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{metadata["archive_filename"]}"'},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(_, exc):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})
