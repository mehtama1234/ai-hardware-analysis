from datetime import datetime, timezone
from hashlib import sha256
from io import BytesIO
import json
from zipfile import ZIP_DEFLATED, ZipFile


PACKAGE_SCHEMA_VERSION = "package-readiness-v0.1"


def _artifact_hash(*parts):
    digest = sha256()
    for part in parts:
        digest.update(str(part).encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest()[:16]


def _claim_level(analysis, quantization_report, runtime_profile):
    unsupported = sum(1 for layer in analysis.get("layers", []) if layer["placement"] == "unsupported")
    fallback = sum(1 for layer in analysis.get("layers", []) if layer["placement"] == "fallback")
    runtime_summary = runtime_profile.get("summary", {})
    misses_target = not runtime_summary.get("meets_latency_target", False) or not runtime_summary.get("meets_energy_target", False)
    high_quant_risk = any(trial.get("risk") == "high" for trial in quantization_report.get("trials", []))

    if unsupported:
        return "not package-ready: unsupported operators remain"
    if fallback or misses_target or high_quant_risk:
        return "analysis package only: needs rewrite, measurement, or risk reduction"
    if runtime_profile.get("provenance") == "simulated":
        return "simulated evaluation package: ready for simulator review, not hardware proof"
    if runtime_profile.get("provenance") == "prototype_board":
        return "prototype evidence package: useful for lab review, not production proof"
    return "deployment candidate: still requires production validation"


def _readiness_stage(claim_level):
    if claim_level.startswith("not package-ready"):
        return "blocked"
    if claim_level.startswith("analysis package"):
        return "needs work"
    if claim_level.startswith("simulated"):
        return "simulator-ready"
    if claim_level.startswith("prototype"):
        return "prototype-ready"
    return "candidate"


def _blockers(analysis, quantization_report, runtime_profile):
    blockers = []
    unsupported = [layer for layer in analysis.get("layers", []) if layer["placement"] == "unsupported"]
    fallback = [layer for layer in analysis.get("layers", []) if layer["placement"] == "fallback"]
    if unsupported:
        blockers.append(
            {
                "id": "B1",
                "severity": "high",
                "text": f"{len(unsupported)} unsupported operator(s) must be rewritten or implemented before a deployable package exists.",
            }
        )
    if fallback:
        blockers.append(
            {
                "id": "B2",
                "severity": "medium",
                "text": f"{len(fallback)} fallback operator(s) need a supported digital path and measured cost.",
            }
        )

    summary = runtime_profile.get("summary", {})
    if not summary.get("meets_latency_target", False):
        blockers.append(
            {
                "id": "B3",
                "severity": "medium",
                "text": "The simulated run misses the latency target, so packaging should stay in evaluation mode.",
            }
        )
    if not summary.get("meets_energy_target", False):
        blockers.append(
            {
                "id": "B4",
                "severity": "medium",
                "text": "The simulated run misses the energy target after full-system costs are counted.",
            }
        )

    protected = quantization_report.get("protected_layers", [])
    if protected:
        blockers.append(
            {
                "id": "B5",
                "severity": "low",
                "text": f"{len(protected)} protected layer(s) need accuracy validation on the task dataset.",
            }
        )

    if runtime_profile.get("provenance") != "measured":
        blockers.append(
            {
                "id": "B6",
                "severity": "low",
                "text": "Runtime numbers are not measured on hardware yet, so the package cannot support production performance claims.",
            }
        )
    return blockers[:6]


def _manifest(analysis, quantization_report, runtime_profile, target_profile, calibration_profile, modality, runtime_mode):
    model = analysis.get("model", {})
    calibration = analysis.get("calibration", {})
    return [
        {
            "name": "model_graph",
            "status": "included",
            "detail": f"{model.get('name', 'model')} with {model.get('operators', 0)} operators.",
        },
        {
            "name": "operator_mapping",
            "status": "included",
            "detail": f"{analysis.get('summary', {}).get('analog_coverage_percent', 0)}% analog coverage for target {target_profile}.",
        },
        {
            "name": "quantization_policy",
            "status": "estimated",
            "detail": f"{quantization_report.get('summary', {}).get('recommended_policy', 'policy unavailable')} for {modality}.",
        },
        {
            "name": "calibration_profile",
            "status": calibration.get("provenance", "unknown"),
            "detail": f"{calibration_profile}: {calibration.get('temperature', 'temperature unknown')}, {calibration.get('voltage', 'voltage unknown')}.",
        },
        {
            "name": "runtime_config",
            "status": "included",
            "detail": f"{runtime_mode} mode with {runtime_profile.get('summary', {}).get('host_overhead_ms', 0)} ms host overhead estimate.",
        },
        {
            "name": "profiling_report",
            "status": runtime_profile.get("provenance", "unknown"),
            "detail": f"{runtime_profile.get('summary', {}).get('latency_ms', 0)} ms, {runtime_profile.get('summary', {}).get('energy_uj', 0)} uJ per completed inference.",
        },
        {
            "name": "digital_baseline_comparison",
            "status": "estimated",
            "detail": "Included when an archive is exported; compare completed inference, not TOPS/W headlines.",
        },
        {
            "name": "adapter_registry",
            "status": "included",
            "detail": "Lists local estimators, configured external tools, and missing compiler, simulator, board, or measurement connections.",
        },
    ]


def _next_actions(blockers, runtime_profile):
    actions = []
    if any(item["id"] in {"B1", "B2"} for item in blockers):
        actions.append({"id": "A1", "text": "Fix unsupported and fallback operators before producing a deployable binary."})
    if any(item["id"] in {"B3", "B4"} for item in blockers):
        actions.append({"id": "A2", "text": "Try alternate runtime modes and reduce high-cost boundaries before comparing against a digital baseline."})
    if any(item["id"] == "B5" for item in blockers):
        actions.append({"id": "A3", "text": "Run the task dataset through the protected precision policy and compare the task metric."})
    if runtime_profile.get("provenance") == "simulated":
        actions.append({"id": "A4", "text": "Connect a simulator or board adapter before using the result as hardware evidence."})
    actions.append({"id": "A5", "text": "Export this report with provenance so reviewers know exactly what was estimated and what was measured."})
    return actions[:5]


def build_deployment_package(
    model_id,
    analysis,
    quantization_report,
    runtime_profile,
    target_profile="wearable",
    calibration_profile="sim-wearable-v0",
    modality="vision_classification",
    runtime_mode="balanced",
    project_context=None,
):
    package_id = "pkg-" + _artifact_hash(
        model_id,
        analysis.get("model", {}).get("name", ""),
        target_profile,
        calibration_profile,
        modality,
        runtime_mode,
        runtime_profile.get("summary", {}).get("latency_ms", ""),
        runtime_profile.get("summary", {}).get("energy_uj", ""),
    )
    claim_level = _claim_level(analysis, quantization_report, runtime_profile)
    blockers = _blockers(analysis, quantization_report, runtime_profile)

    return {
        "result_type": "deployment_package_readiness",
        "schema_version": PACKAGE_SCHEMA_VERSION,
        "package_id": package_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "provenance": "assembled from local analysis artifacts",
        "confidence": "low",
        "readiness_stage": _readiness_stage(claim_level),
        "claim_level": claim_level,
        "summary": {
            "project_id": (project_context or {}).get("project_id"),
            "project_name": (project_context or {}).get("name"),
            "model_id": model_id,
            "model_name": analysis.get("model", {}).get("name", "model"),
            "target_profile": target_profile,
            "calibration_profile": calibration_profile,
            "modality": modality,
            "runtime_mode": runtime_mode,
            "latency_ms": runtime_profile.get("summary", {}).get("latency_ms"),
            "energy_uj": runtime_profile.get("summary", {}).get("energy_uj"),
            "analog_coverage_percent": analysis.get("summary", {}).get("analog_coverage_percent"),
            "protected_layers": quantization_report.get("summary", {}).get("protected_layers"),
            "status": "readiness report generated; no hardware executable binary emitted in this prototype",
        },
        "project": project_context,
        "manifest": _manifest(
            analysis,
            quantization_report,
            runtime_profile,
            target_profile,
            calibration_profile,
            modality,
            runtime_mode,
        ),
        "blockers": blockers,
        "next_actions": _next_actions(blockers, runtime_profile),
    }


def _write_json(zip_file, name, payload):
    zip_file.writestr(name, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def build_deployment_archive(
    model_path,
    package_report,
    analysis,
    quantization_report,
    runtime_profile,
    baseline_comparison=None,
    hardware_placement=None,
    residual_aware_placement=None,
    workload_fit=None,
    system_boundary=None,
    physical_ai_map=None,
    physical_ai_roadmap=None,
    vla_readiness=None,
    weight_update_readiness=None,
    calibration_drift_readiness=None,
    control_boundary=None,
    sensor_boundary_readiness=None,
    research_guide=None,
    concept_glossary=None,
    source_check_register=None,
    measurement_evidence=None,
    toolchain_readiness=None,
    connection_playbook=None,
    adapter_execution_plan=None,
    adapter_connection_kit=None,
    adapter_evidence_templates=None,
    adapter_connection_self_test=None,
    adapter_integration_readiness=None,
    external_connector_contract=None,
    compiler_ecosystem_readiness=None,
    connector_implementation_guide=None,
    connector_test_harness=None,
    connector_acceptance_drills=None,
    connector_acceptance_report=None,
    connector_backlog=None,
    connector_delivery_plan=None,
    connector_risk_register=None,
    evidence_gates=None,
    claim_readiness=None,
    evidence_audit=None,
    evidence_brief=None,
    interview_brief=None,
    interview_drill=None,
    review_report=None,
    decision_report=None,
    rewrite_suggestions=None,
    rewrite_what_if=None,
    rewrite_plan=None,
    rewrite_work_order=None,
    adapter_registry=None,
    imported_evidence=None,
    adapter_runs=None,
):
    package_id = package_report["package_id"]
    readme = f"""Analog In-Memory AI Inference Evaluation Archive

Package ID: {package_id}
Project: {package_report.get('summary', {}).get('project_name') or 'not attached'}
Readiness: {package_report['readiness_stage']}
Claim level: {package_report['claim_level']}

This archive is a prototype evaluation package. It contains the source ONNX model and the analysis artifacts needed for review. It is not a compiled hardware binary and it is not proof of measured hardware performance.

Contents:
- manifest.json: package manifest and safe claim level
- package-readiness.json: blockers and next evidence steps
- analysis.json: operator fit, mapping, boundary, calibration, and energy estimate
- quantization-report.json: estimated precision policy and protected layers
- runtime-profile.json: simulated runtime trace, latency, energy, and bottlenecks
- baseline-comparison.json: estimated analog result compared with an estimated digital baseline
- hardware-placement.json: model graph translated into analog candidates, digital-only regions, converter boundaries, sensitivity classes, fallback points, and governor fields
- residual-aware-placement.json: structural placement filtered through calibrated simulator residual evidence when available
- workload-fit.json: workload and modality fit matrix for edge use cases
- system-boundary.json: analog, digital, conversion, memory, host, and fallback boundary report
- physical-ai-map.json: Physical AI domain map, edge-compute fit, evidence gaps, and claim boundaries
- physical-ai-roadmap.json: single Physical AI roadmap view across domain, model, VLA, weight update, drift, control, sensor, compiler, runtime, accuracy, and evidence gates
- vla-readiness.json: transformer and VLA readiness report with analog opportunity, digital support, memory, and boundary risks
- weight-update-readiness.json: fixed-weight versus adaptive-update readiness report with write evidence gaps
- calibration-drift-readiness.json: calibration, temperature, voltage, drift, aging, recalibration, and failure-behavior gate
- control-boundary.json: inference, real-time control, safety handoff, latency, jitter, and deterministic-controller evidence gaps
- sensor-boundary-readiness.json: sensor-to-tensor boundary, preprocessing owner, AFE/event/tactile/sync status, and sensor-to-output evidence gaps
- research-guide.json: analog and in-memory AI paper reading guide
- concept-glossary.json: plain-language glossary for analog and in-memory AI terms
- source-check-register.json: checked examples, source links, allowed-use rules, and do-not-claim boundaries
- measurement-evidence.json: normalized compiler, simulator, board, power, and accuracy evidence contract
- toolchain-readiness.json: model-to-handoff software support readiness report
- connection-playbook.json: real tool wiring checklist and proof artifact map
- adapter-execution-plan.json: adapter configure, run, normalize, validate, import, and archive steps
- adapter-connection-kit.json: env vars, raw inputs, raw outputs, normalized artifacts, and API calls for each adapter
- adapter-evidence-templates.json: example normalized JSON payloads each external adapter should emit
- adapter-connection-self-test.json: probe results showing which external tool paths are configured or blocked
- adapter-integration-readiness.json: synthesized adapter readiness, blockers, and next connection priorities
- external-connector-contract.json: request, response, health, failure, validation, and import contract for real tools
- compiler-ecosystem-readiness.json: ONNX, PyTorch, JAX/XLA, compiler mapping, profiling, rewrite, and adoption-risk readiness
- connector-implementation-guide.json: rollout order, implementation steps, and done criteria for external connectors
- connector-test-harness.json: probe, run, validation, import, and failure-safety checks for connectors
- connector-acceptance-drills.json: executed negative-validation and failed-run safety drills
- connector-acceptance-report.json: current pass, blocked, and pending connector acceptance status
- connector-backlog.json: owner-facing tasks generated from connector acceptance gaps
- connector-delivery-plan.json: milestone order for closing connector backlog tasks
- connector-risk-register.json: connector delivery risks, triggers, mitigations, and evidence needed
- adapter-registry.json: local and external tool connection status
- evidence-gates.json: consolidated pass, estimated, blocked, and missing checks
- claim-readiness.json: lab claim support recalculated from imported evidence
- evidence-audit.json: active imported evidence, local/non-local counts, and refresh behavior
- evidence-brief.json: plain-language evidence handoff derived from claim readiness and audit
- evidence-brief.md: readable version of the same evidence handoff
- interview-brief.json: interview explanation guide derived from package evidence
- interview-brief.md: readable version of the same interview explanation guide
- interview-drill.json: interview question and answer rehearsal guide
- decision-report.json: product-level fit decision, reasons, and next actions
- rewrite-suggestions.json: concrete model and operator changes to try next
- rewrite-what-if.json: low-confidence estimate for selected rewrite effects
- rewrite-plan.json: concrete planned graph/runtime changes and validation steps
- rewrite-work-order.json: owner-facing rewrite tasks, gates, and evidence handoff
- review-report.md: plain-language review report for interview or customer discussion
- review-report.json: structured version of the same report
- imported-evidence/index.json: list of normalized external evidence artifacts attached to this package
- imported-evidence/*.json: imported compiler, simulator, board, power, thermal, or accuracy artifacts
- adapter-runs/index.json: adapter attempts attached to this package, including blocked connector runs
- adapter-runs/*.json: full adapter run audit records; these are not claim evidence unless separately imported
- source-model.onnx: original uploaded ONNX model
"""
    buffer = BytesIO()
    with ZipFile(buffer, "w", compression=ZIP_DEFLATED) as zip_file:
        zip_file.writestr("README.txt", readme)
        _write_json(zip_file, "manifest.json", {
            "package_id": package_id,
            "schema_version": package_report["schema_version"],
            "created_at": package_report["created_at"],
            "provenance": package_report["provenance"],
            "confidence": package_report["confidence"],
            "readiness_stage": package_report["readiness_stage"],
            "claim_level": package_report["claim_level"],
            "summary": package_report["summary"],
            "project": package_report.get("project"),
            "manifest": package_report["manifest"],
        })
        _write_json(zip_file, "package-readiness.json", package_report)
        _write_json(zip_file, "analysis.json", analysis)
        _write_json(zip_file, "quantization-report.json", quantization_report)
        _write_json(zip_file, "runtime-profile.json", runtime_profile)
        if baseline_comparison:
            _write_json(zip_file, "baseline-comparison.json", baseline_comparison)
        if hardware_placement:
            _write_json(zip_file, "hardware-placement.json", hardware_placement)
        if residual_aware_placement:
            _write_json(zip_file, "residual-aware-placement.json", residual_aware_placement)
        if workload_fit:
            _write_json(zip_file, "workload-fit.json", workload_fit)
        if system_boundary:
            _write_json(zip_file, "system-boundary.json", system_boundary)
        if physical_ai_map:
            _write_json(zip_file, "physical-ai-map.json", physical_ai_map)
        if physical_ai_roadmap:
            _write_json(zip_file, "physical-ai-roadmap.json", physical_ai_roadmap)
        if vla_readiness:
            _write_json(zip_file, "vla-readiness.json", vla_readiness)
        if weight_update_readiness:
            _write_json(zip_file, "weight-update-readiness.json", weight_update_readiness)
        if calibration_drift_readiness:
            _write_json(zip_file, "calibration-drift-readiness.json", calibration_drift_readiness)
        if control_boundary:
            _write_json(zip_file, "control-boundary.json", control_boundary)
        if sensor_boundary_readiness:
            _write_json(zip_file, "sensor-boundary-readiness.json", sensor_boundary_readiness)
        if research_guide:
            _write_json(zip_file, "research-guide.json", research_guide)
        if concept_glossary:
            _write_json(zip_file, "concept-glossary.json", concept_glossary)
        if source_check_register:
            _write_json(zip_file, "source-check-register.json", source_check_register)
        if measurement_evidence:
            _write_json(zip_file, "measurement-evidence.json", measurement_evidence)
        if toolchain_readiness:
            _write_json(zip_file, "toolchain-readiness.json", toolchain_readiness)
        if connection_playbook:
            _write_json(zip_file, "connection-playbook.json", connection_playbook)
        if adapter_execution_plan:
            _write_json(zip_file, "adapter-execution-plan.json", adapter_execution_plan)
        if adapter_connection_kit:
            _write_json(zip_file, "adapter-connection-kit.json", adapter_connection_kit)
        if adapter_evidence_templates:
            _write_json(zip_file, "adapter-evidence-templates.json", adapter_evidence_templates)
        if adapter_connection_self_test:
            _write_json(zip_file, "adapter-connection-self-test.json", adapter_connection_self_test)
        if adapter_integration_readiness:
            _write_json(zip_file, "adapter-integration-readiness.json", adapter_integration_readiness)
        if external_connector_contract:
            _write_json(zip_file, "external-connector-contract.json", external_connector_contract)
        if compiler_ecosystem_readiness:
            _write_json(zip_file, "compiler-ecosystem-readiness.json", compiler_ecosystem_readiness)
        if connector_implementation_guide:
            _write_json(zip_file, "connector-implementation-guide.json", connector_implementation_guide)
        if connector_test_harness:
            _write_json(zip_file, "connector-test-harness.json", connector_test_harness)
        if connector_acceptance_drills:
            _write_json(zip_file, "connector-acceptance-drills.json", connector_acceptance_drills)
        if connector_acceptance_report:
            _write_json(zip_file, "connector-acceptance-report.json", connector_acceptance_report)
        if connector_backlog:
            _write_json(zip_file, "connector-backlog.json", connector_backlog)
        if connector_delivery_plan:
            _write_json(zip_file, "connector-delivery-plan.json", connector_delivery_plan)
        if connector_risk_register:
            _write_json(zip_file, "connector-risk-register.json", connector_risk_register)
        if adapter_registry:
            _write_json(zip_file, "adapter-registry.json", adapter_registry)
        if evidence_gates:
            _write_json(zip_file, "evidence-gates.json", evidence_gates)
        if claim_readiness:
            _write_json(zip_file, "claim-readiness.json", claim_readiness)
        if evidence_audit:
            _write_json(zip_file, "evidence-audit.json", evidence_audit)
        if evidence_brief:
            _write_json(zip_file, "evidence-brief.json", evidence_brief)
            zip_file.writestr("evidence-brief.md", evidence_brief["markdown"])
        if interview_brief:
            _write_json(zip_file, "interview-brief.json", interview_brief)
            zip_file.writestr("interview-brief.md", interview_brief["markdown"])
        if interview_drill:
            _write_json(zip_file, "interview-drill.json", interview_drill)
        if decision_report:
            _write_json(zip_file, "decision-report.json", decision_report)
        if rewrite_suggestions:
            _write_json(zip_file, "rewrite-suggestions.json", rewrite_suggestions)
        if rewrite_what_if:
            _write_json(zip_file, "rewrite-what-if.json", rewrite_what_if)
        if rewrite_plan:
            _write_json(zip_file, "rewrite-plan.json", rewrite_plan)
        if rewrite_work_order:
            _write_json(zip_file, "rewrite-work-order.json", rewrite_work_order)
        if review_report:
            _write_json(zip_file, "review-report.json", review_report)
            zip_file.writestr("review-report.md", review_report["markdown"])
        if imported_evidence:
            imported_index = [
                {
                    "import_id": item.get("import_id"),
                    "source_id": item.get("source_id"),
                    "artifact_name": item.get("artifact_name"),
                    "created_at": item.get("created_at"),
                    "package_id": item.get("package_id"),
                    "run_id": item.get("run_id"),
                }
                for item in imported_evidence
            ]
            _write_json(zip_file, "imported-evidence/index.json", imported_index)
            for item in imported_evidence:
                safe_source = "".join(char if char.isalnum() or char in {"-", "_"} else "-" for char in item.get("source_id", "evidence"))
                import_id = item.get("import_id", "unknown")
                _write_json(zip_file, f"imported-evidence/{safe_source}-{import_id}.json", item)
        if adapter_runs:
            run_index = [
                {
                    "run_id": item.get("run_id"),
                    "adapter_id": item.get("adapter_id"),
                    "status": item.get("status"),
                    "created_at": item.get("created_at"),
                    "provenance": item.get("provenance"),
                    "confidence": item.get("confidence"),
                    "artifact_names": [artifact.get("name") for artifact in item.get("artifacts", [])],
                    "has_normalized_evidence": bool(item.get("normalized_evidence_payload")),
                }
                for item in adapter_runs
            ]
            _write_json(zip_file, "adapter-runs/index.json", run_index)
            for item in adapter_runs:
                safe_adapter = "".join(char if char.isalnum() or char in {"-", "_"} else "-" for char in item.get("adapter_id", "adapter"))
                run_id = item.get("run_id", "unknown")
                _write_json(zip_file, f"adapter-runs/{safe_adapter}-{run_id}.json", item)
        zip_file.write(model_path, "source-model.onnx")
    buffer.seek(0)
    return buffer.getvalue(), f"{package_id}.zip"
