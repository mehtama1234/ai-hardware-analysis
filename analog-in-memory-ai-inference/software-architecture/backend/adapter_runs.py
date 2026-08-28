from datetime import datetime, timezone
from importlib.util import find_spec
import csv
import json
from pathlib import Path
from uuid import uuid4

import onnx

from calibration import get_calibration_profile
from external_service_adapter import ExternalAdapterError, call_external_service
from onnx_analyzer import analyze_model
from quantization import estimate_quantization
from runtime_profile import run_simulated_profile
from external_replay import write_replay_artifacts
from simulated_lab_profiles import simulated_lab_metadata


ADAPTER_RUN_SCHEMA_VERSION = "adapter-run-v0.1"


def _utc_now():
    return datetime.now(timezone.utc).isoformat()


def _blocked_run(adapter_id, model_id, reason, next_step, run_id=None, artifacts=None):
    return {
        "result_type": "adapter_run",
        "schema_version": ADAPTER_RUN_SCHEMA_VERSION,
        "adapter_id": adapter_id,
        "model_id": model_id,
        "run_id": run_id or str(uuid4()),
        "created_at": _utc_now(),
        "status": "blocked",
        "provenance": "local adapter runner",
        "confidence": "low",
        "summary": {
            "message": reason,
            "next_step": next_step,
        },
        "artifacts": artifacts or [],
        "claim_rule": "This run does not support measured claims until it produces a normalized evidence artifact with task data, provenance, metrics, and confidence.",
    }


def _external_failure_artifacts(exc):
    paths = getattr(exc, "artifact_paths", {}) or {}
    artifacts = []
    if paths.get("raw_request_path"):
        artifacts.append({
            "name": "external-service-request",
            "path": paths["raw_request_path"],
            "format": "json",
            "description": "Raw request that was sent to the configured external service before the run failed.",
        })
    if paths.get("raw_response_path"):
        artifacts.append({
            "name": "external-service-response",
            "path": paths["raw_response_path"],
            "format": "json",
            "description": "Raw response returned by the configured external service before contract validation failed.",
        })
    if paths.get("failure_path"):
        artifacts.append({
            "name": "external-service-failure",
            "path": paths["failure_path"],
            "format": "json",
            "description": "Saved failure envelope for the configured external service run.",
        })
    return artifacts


def _model_summary(path):
    model = onnx.load(str(path))
    graph = model.graph
    initializers = list(graph.initializer)
    return {
        "node_count": len(graph.node),
        "initializer_count": len(initializers),
        "operator_histogram": _operator_histogram(graph.node),
        "file_size_bytes": Path(path).stat().st_size,
    }


def _operator_histogram(nodes):
    histogram = {}
    for node in nodes:
        histogram[node.op_type] = histogram.get(node.op_type, 0) + 1
    return histogram


def run_onnxruntime_quantization(model_record, output_root):
    adapter_id = "quantization.onnxruntime"
    model_id = model_record["model_id"]
    if find_spec("onnxruntime") is None:
        return _blocked_run(
            adapter_id,
            model_id,
            "ONNX Runtime is not installed in the backend environment.",
            "Install onnxruntime and rerun this adapter after a calibration or reference dataset path is available.",
        )

    try:
        from onnxruntime.quantization import QuantType, quantize_dynamic
    except Exception as exc:
        return _blocked_run(
            adapter_id,
            model_id,
            f"ONNX Runtime quantization import failed: {exc}",
            "Check the installed onnxruntime package and quantization extras.",
        )

    run_id = str(uuid4())
    run_dir = Path(output_root) / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    input_path = Path(model_record["path"])
    output_path = run_dir / f"{input_path.stem}.dynamic-int8.onnx"

    before = _model_summary(input_path)
    quantize_dynamic(str(input_path), str(output_path), weight_type=QuantType.QInt8)
    after = _model_summary(output_path)

    size_delta = after["file_size_bytes"] - before["file_size_bytes"]
    size_delta_percent = round((size_delta / before["file_size_bytes"]) * 100, 2) if before["file_size_bytes"] else None

    return {
        "result_type": "adapter_run",
        "schema_version": ADAPTER_RUN_SCHEMA_VERSION,
        "adapter_id": adapter_id,
        "model_id": model_id,
        "run_id": run_id,
        "created_at": _utc_now(),
        "status": "completed",
        "provenance": "onnxruntime.quantization.quantize_dynamic",
        "confidence": "medium",
        "summary": {
            "message": "Dynamic INT8 quantization completed locally.",
            "input_file_size_bytes": before["file_size_bytes"],
            "output_file_size_bytes": after["file_size_bytes"],
            "size_delta_percent": size_delta_percent,
            "node_count_before": before["node_count"],
            "node_count_after": after["node_count"],
            "next_step": "Run a task dataset through the baseline and quantized model before treating accuracy as supported evidence.",
        },
        "artifacts": [
            {
                "name": "quantized_model",
                "path": str(output_path),
                "format": "onnx",
                "description": "Dynamically quantized INT8 ONNX model produced by ONNX Runtime.",
            }
        ],
        "model_before": before,
        "model_after": after,
        "normalized_artifact_contract": {
            "source_id": "task_accuracy",
            "artifact_name": "task-accuracy-report.json",
            "minimum_fields": ["dataset_id", "metric_name", "baseline_metric", "candidate_metric", "tolerance", "pass"],
            "claim_use": "Accuracy is not supported by quantization alone. It needs a task accuracy report from a real dataset.",
        },
        "claim_rule": "Quantization success proves the tool could transform the model. It does not prove accuracy, latency, energy, or production readiness.",
    }


def _tile_shape_for_layer(layer):
    shape = layer.get("shape") or []
    numeric = [int(value) for value in shape if isinstance(value, int) and value > 0]
    if len(numeric) >= 2:
        return [min(numeric[-2], 64), min(numeric[-1], 64)]
    return [16, 16]


def _compiler_memory_plan(analysis):
    summary = analysis.get("summary", {})
    return {
        "weights": "analog_array_for_analog_layers",
        "activations": "local_sram_between_supported_layers",
        "outputs": "digital_postprocess_after_analog_or_fallback_boundaries",
        "fallback": "host_or_digital_path_for_unsupported_and_control_operators",
        "counted_costs": [
            "analog compute",
            "digital fallback",
            "ADC/DAC boundary conversion",
            "memory movement",
            "host/runtime overhead in later runtime profile",
        ],
        "analog_coverage_percent": summary.get("analog_coverage_percent"),
    }


def run_compiler_mapping(model_record, output_root, target_profile="wearable", calibration_profile="sim-wearable-v0"):
    adapter_id = "compiler.tvm-mlir-iree"
    model_id = model_record["model_id"]
    run_id = str(uuid4())
    run_dir = Path(output_root) / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    input_path = Path(model_record["path"])

    try:
        external = call_external_service(
            adapter_id,
            "compiler_mapping",
            "compiler-placement.json",
            {
                "model_id": model_id,
                "model_path": str(input_path),
                "model_filename": model_record.get("filename"),
                "target_profile": target_profile,
                "calibration_profile": calibration_profile,
            },
            run_dir,
            timeout_seconds=60,
        )
    except ExternalAdapterError as exc:
        return _blocked_run(
            adapter_id,
            model_id,
            f"Configured compiler service failed: {exc}",
            "Check ANALOG_AI_COMPILER_API_URL, service /run behavior, and normalized compiler-placement evidence contract.",
            run_id=run_id,
            artifacts=_external_failure_artifacts(exc),
        )
    if external:
        evidence_payload = external["payload"]
        output_path = run_dir / "compiler-placement.json"
        output_path.write_text(_json_dumps(evidence_payload), encoding="utf-8")
        return {
            "result_type": "adapter_run",
            "schema_version": ADAPTER_RUN_SCHEMA_VERSION,
            "adapter_id": adapter_id,
            "model_id": model_id,
            "run_id": run_id,
            "created_at": _utc_now(),
            "status": "completed",
            "provenance": "configured external compiler service",
            "confidence": "medium",
            "summary": {
                "message": "Compiler-placement artifact returned by configured external service.",
                "analog_layers": sum(1 for item in evidence_payload.get("operator_placements", []) if item.get("placement") == "analog"),
                "fallback_or_unsupported_layers": len(evidence_payload.get("unsupported_operators") or []),
                "target_profile": target_profile,
                "calibration_profile": calibration_profile,
                "service_url": external["service_url"],
                "next_step": "Validate and import this compiler artifact, then keep raw request and response files with the package.",
            },
            "artifacts": [
                {
                    "name": "compiler-placement",
                    "path": str(output_path),
                    "format": "json",
                    "description": "Normalized compiler-placement evidence returned by the configured external service.",
                },
                {
                    "name": "external-service-request",
                    "path": external["raw_request_path"],
                    "format": "json",
                    "description": "Raw request sent to the configured compiler service.",
                },
                {
                    "name": "external-service-response",
                    "path": external["raw_response_path"],
                    "format": "json",
                    "description": "Raw response returned by the configured compiler service.",
                },
            ],
            "normalized_artifact_contract": {
                "source_id": "compiler_mapping",
                "artifact_name": "compiler-placement.json",
                "minimum_fields": ["operator_placements", "tiling_plan", "memory_plan", "unsupported_operators", "provenance"],
                "claim_use": "Supports compiler-produced placement discussion when the external service provenance matches the target setup.",
            },
            "normalized_evidence_source_id": "compiler_mapping",
            "normalized_evidence_payload": evidence_payload,
            "claim_rule": "This artifact came from a configured compiler service. It supports placement discussion, not latency, energy, accuracy, or production readiness by itself.",
        }

    analysis = analyze_model(
        model_record["path"],
        target_profile=target_profile,
        calibration_profile=calibration_profile,
    )
    lab = simulated_lab_metadata(target_profile)
    layers = analysis.get("layers", [])
    unsupported = [
        {
            "layer_id": layer["id"],
            "operator": layer["operator"],
            "reason": layer.get("reason", "Not supported by the current local placement rules."),
        }
        for layer in layers
        if layer.get("placement") in {"unsupported", "fallback"}
    ]
    evidence_payload = {
        "operator_placements": [
            {
                "layer_id": layer["id"],
                "operator": layer["operator"],
                "placement": layer["placement"],
                "reason": layer.get("reason"),
            }
            for layer in layers
        ],
        "tiling_plan": [
            {
                "layer_id": layer["id"],
                "tile_shape": _tile_shape_for_layer(layer),
                "boundary": layer.get("boundaries"),
            }
            for layer in layers
            if layer.get("placement") == "analog"
        ],
        "memory_plan": _compiler_memory_plan(analysis),
        "unsupported_operators": unsupported,
        "simulation_profile": lab,
        "provenance": {
            "tool": "local-placement-adapter",
            "version": ADAPTER_RUN_SCHEMA_VERSION,
            "target_profile": target_profile,
            "calibration_profile": calibration_profile,
            "simulation_profile_id": lab["scenario_id"],
            "source": "onnx_analyzer placement rules plus scenario-based simulated lab profile",
            "model_id": model_id,
        },
    }
    output_path = run_dir / "compiler-placement.json"
    output_path.write_text(_json_dumps(evidence_payload), encoding="utf-8")

    analog_count = sum(1 for layer in layers if layer.get("placement") == "analog")
    digital_count = sum(1 for layer in layers if layer.get("placement") == "digital")
    fallback_count = len(unsupported)

    return {
        "result_type": "adapter_run",
        "schema_version": ADAPTER_RUN_SCHEMA_VERSION,
        "adapter_id": adapter_id,
        "model_id": model_id,
        "run_id": run_id,
        "created_at": _utc_now(),
        "status": "completed",
        "provenance": "local analyzer placement adapter",
        "confidence": "low",
        "summary": {
            "message": "Compiler-placement artifact generated from local placement rules.",
            "analog_layers": analog_count,
            "digital_layers": digital_count,
            "fallback_or_unsupported_layers": fallback_count,
            "target_profile": target_profile,
            "calibration_profile": calibration_profile,
            "simulation_profile": lab["label"],
            "next_step": "Replace this with a real compiler report before claiming compiler-produced placement.",
        },
        "artifacts": [
            {
                "name": "compiler-placement",
                "path": str(output_path),
                "format": "json",
                "description": "Normalized compiler-placement evidence generated from local analyzer rules.",
            }
        ],
        "normalized_artifact_contract": {
            "source_id": "compiler_mapping",
            "artifact_name": "compiler-placement.json",
            "minimum_fields": ["operator_placements", "tiling_plan", "memory_plan", "unsupported_operators", "provenance"],
            "claim_use": "Supports local placement discussion. It is not proof from a production compiler.",
        },
        "normalized_evidence_source_id": "compiler_mapping",
        "normalized_evidence_payload": evidence_payload,
        "claim_rule": "This artifact supports placement discussion only. It does not prove measured latency, energy, accuracy, or production readiness.",
    }


def _range_from_text(text, unit):
    import re

    values = [float(item) for item in re.findall(r"-?\d+(?:\.\d+)?", text or "")]
    if len(values) >= 2:
        low, high = min(values[0], values[1]), max(values[0], values[1])
    elif len(values) == 1:
        low, high = values[0], values[0]
    else:
        low, high = (0.0, 70.0) if unit == "c" else (0.72, 0.88)
    if unit == "c":
        return {"min_c": int(low), "max_c": int(high)}
    return {"min_v": round(low, 3), "max_v": round(high, 3)}


def _estimated_accuracy_drop(analysis, calibration):
    summary = analysis.get("summary", {})
    analog_coverage = float(summary.get("analog_coverage_percent") or 0)
    boundary_count = len(analysis.get("boundary_events", []))
    fallback_count = int(summary.get("fallback_count") or 0)
    correction = calibration.get("correction_factors", {})
    gain_error = abs(float(correction.get("gain", 1.0)) - 1.0)
    offset_error = abs(float(correction.get("offset", 0.0)))
    weak_rows_text = calibration.get("weak_rows", "")
    weak_rows = 0
    for token in str(weak_rows_text).split():
        if token.isdigit():
            weak_rows = int(token)
            break
    drop = 0.0015 + (analog_coverage / 100.0 * 0.003) + (boundary_count * 0.0004) + (fallback_count * 0.0005)
    drop += gain_error * 0.03 + offset_error * 0.01 + min(weak_rows, 64) * 0.00004
    return round(drop, 4)


def run_analog_error_simulation(model_record, output_root, target_profile="wearable", calibration_profile="sim-wearable-v0"):
    adapter_id = "analog.error-simulator"
    model_id = model_record["model_id"]
    run_id = str(uuid4())
    run_dir = Path(output_root) / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    input_path = Path(model_record["path"])

    try:
        external = call_external_service(
            adapter_id,
            "analog_error_simulation",
            "analog-error-simulation.json",
            {
                "model_id": model_id,
                "model_path": str(input_path),
                "model_filename": model_record.get("filename"),
                "target_profile": target_profile,
                "calibration_profile": calibration_profile,
            },
            run_dir,
            timeout_seconds=60,
        )
    except ExternalAdapterError as exc:
        return _blocked_run(
            adapter_id,
            model_id,
            f"Configured analog error service failed: {exc}",
            "Check ANALOG_AI_ERROR_SIM_URL, service /run behavior, and normalized analog-error evidence contract.",
            run_id=run_id,
            artifacts=_external_failure_artifacts(exc),
        )
    if external:
        evidence_payload = external["payload"]
        output_path = run_dir / "analog-error-simulation.json"
        output_path.write_text(_json_dumps(evidence_payload), encoding="utf-8")
        impact = evidence_payload.get("accuracy_impact") or {}
        return {
            "result_type": "adapter_run",
            "schema_version": ADAPTER_RUN_SCHEMA_VERSION,
            "adapter_id": adapter_id,
            "model_id": model_id,
            "run_id": run_id,
            "created_at": _utc_now(),
            "status": "completed",
            "provenance": "configured external analog error service",
            "confidence": "medium",
            "summary": {
                "message": "Analog error artifact returned by configured external service.",
                "estimated_accuracy_drop": impact.get("estimated_drop"),
                "temperature_range": evidence_payload.get("temperature_range"),
                "voltage_range": evidence_payload.get("voltage_range"),
                "target_profile": target_profile,
                "calibration_profile": calibration_profile,
                "service_url": external["service_url"],
                "next_step": "Validate and import this analog error artifact, then pair it with task accuracy evidence.",
            },
            "artifacts": [
                {
                    "name": "analog-error-simulation",
                    "path": str(output_path),
                    "format": "json",
                    "description": "Normalized analog-error evidence returned by the configured external service.",
                },
                {
                    "name": "external-service-request",
                    "path": external["raw_request_path"],
                    "format": "json",
                    "description": "Raw request sent to the configured analog error service.",
                },
                {
                    "name": "external-service-response",
                    "path": external["raw_response_path"],
                    "format": "json",
                    "description": "Raw response returned by the configured analog error service.",
                },
            ],
            "normalized_artifact_contract": {
                "source_id": "analog_error_simulation",
                "artifact_name": "analog-error-simulation.json",
                "minimum_fields": ["error_model", "temperature_range", "voltage_range", "accuracy_impact", "calibration_profile"],
                "claim_use": "Supports analog numeric-behavior discussion when paired with task accuracy evidence.",
            },
            "normalized_evidence_source_id": "analog_error_simulation",
            "normalized_evidence_payload": evidence_payload,
            "claim_rule": "This artifact came from a configured analog error service. It does not prove task accuracy without a matching task-accuracy report.",
        }

    analysis = analyze_model(
        model_record["path"],
        target_profile=target_profile,
        calibration_profile=calibration_profile,
    )
    calibration = get_calibration_profile(calibration_profile)
    lab = simulated_lab_metadata(target_profile)
    correction = calibration.get("correction_factors", {})
    estimated_drop = _estimated_accuracy_drop(analysis, calibration)
    array = lab["profile"].get("analog_array", {})
    evidence_payload = {
        "error_model": {
            "model": "local-static-variation-estimate",
            "weight_noise_stddev": round(0.008 + estimated_drop, 4),
            "adc_bits": array.get("adc_bits", 8),
            "dac_bits": array.get("dac_bits", 8),
            "gain_correction": correction.get("gain"),
            "offset_correction": correction.get("offset"),
            "adc_reference": correction.get("adc_reference"),
            "drift_model": "calibration-profile-derived",
        },
        "temperature_range": _range_from_text(calibration.get("temperature"), "c"),
        "voltage_range": _range_from_text(calibration.get("voltage"), "v"),
        "accuracy_impact": {
            "metric_name": "task_metric_proxy",
            "estimated_drop": estimated_drop,
            "pass": estimated_drop <= 0.01,
            "reason": "Local estimate from analog coverage, boundary count, fallback count, and calibration correction factors.",
        },
        "calibration_profile": calibration_profile,
        "simulation_profile": lab,
        "provenance": {
            "tool": "local-analog-error-adapter",
            "version": ADAPTER_RUN_SCHEMA_VERSION,
            "target_profile": target_profile,
            "calibration_profile": calibration_profile,
            "simulation_profile_id": lab["scenario_id"],
            "source": "calibration profile, onnx_analyzer placement summary, and scenario-based simulated lab profile",
            "model_id": model_id,
        },
    }
    output_path = run_dir / "analog-error-simulation.json"
    output_path.write_text(_json_dumps(evidence_payload), encoding="utf-8")

    return {
        "result_type": "adapter_run",
        "schema_version": ADAPTER_RUN_SCHEMA_VERSION,
        "adapter_id": adapter_id,
        "model_id": model_id,
        "run_id": run_id,
        "created_at": _utc_now(),
        "status": "completed",
        "provenance": "local analog error estimate",
        "confidence": "low",
        "summary": {
            "message": "Analog error artifact generated from local calibration and placement estimates.",
            "estimated_accuracy_drop": estimated_drop,
            "temperature_range": evidence_payload["temperature_range"],
            "voltage_range": evidence_payload["voltage_range"],
            "target_profile": target_profile,
            "calibration_profile": calibration_profile,
            "simulation_profile": lab["label"],
            "next_step": "Replace this with circuit simulation, silicon characterization, or board-measured numeric error before making strong analog tolerance claims.",
        },
        "artifacts": [
            {
                "name": "analog-error-simulation",
                "path": str(output_path),
                "format": "json",
                "description": "Normalized analog-error evidence generated from local calibration and placement estimates.",
            }
        ],
        "normalized_artifact_contract": {
            "source_id": "analog_error_simulation",
            "artifact_name": "analog-error-simulation.json",
            "minimum_fields": ["error_model", "temperature_range", "voltage_range", "accuracy_impact", "calibration_profile"],
            "claim_use": "Supports analog numeric-behavior discussion only when paired with task accuracy evidence.",
        },
        "normalized_evidence_source_id": "analog_error_simulation",
        "normalized_evidence_payload": evidence_payload,
        "claim_rule": "This artifact is an estimated analog error model. It does not prove task accuracy without a matching task-accuracy report.",
    }


def run_aihwkit_simulation(model_record, output_root, target_profile="wearable", calibration_profile="sim-wearable-v0"):
    adapter_id = "sim.aihwkit"
    model_id = model_record["model_id"]
    run_id = str(uuid4())
    run_dir = Path(output_root) / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    if not find_spec("aihwkit"):
        return _blocked_run(
            adapter_id,
            model_id,
            "AIHWKIT is not installed in the backend Python environment.",
            "Install AIHWKIT or configure ANALOG_AI_AIHWKIT_API_URL, then rerun the adapter.",
            run_id=run_id,
        )

    try:
        import torch
        import aihwkit
        from aihwkit.nn import AnalogLinear
        from aihwkit.simulator.configs import TorchInferenceRPUConfig

        torch.manual_seed(7)
        layer = AnalogLinear(4, 2, rpu_config=TorchInferenceRPUConfig())
        sample_input = torch.tensor([[1.0, -0.5, 0.25, 2.0]], dtype=torch.float32)
        analog_output = layer(sample_input).detach()
        output_sum = round(float(analog_output.sum()), 6)
        output_shape = list(analog_output.shape)
    except Exception as exc:
        return _blocked_run(
            adapter_id,
            model_id,
            f"AIHWKIT import or analog-layer smoke failed: {exc}",
            "Check AIHWKIT, PyTorch, and CPU-compatible RPU config behavior, then rerun the adapter.",
            run_id=run_id,
        )

    calibration = get_calibration_profile(calibration_profile)
    correction = calibration.get("correction_factors", {})
    analysis = analyze_model(
        model_record["path"],
        target_profile=target_profile,
        calibration_profile=calibration_profile,
    )
    estimated_drop = _estimated_accuracy_drop(analysis, calibration)
    evidence_payload = {
        "error_model": {
            "model": "aihwkit-torch-inference-smoke",
            "library": "aihwkit",
            "library_version": getattr(aihwkit, "__version__", "unknown"),
            "torch_version": getattr(torch, "__version__", "unknown"),
            "rpu_config": "TorchInferenceRPUConfig",
            "analog_forward_shape": output_shape,
            "analog_forward_sum": output_sum,
            "gain_correction": correction.get("gain"),
            "offset_correction": correction.get("offset"),
            "drift_model": "not swept in smoke run",
        },
        "temperature_range": _range_from_text(calibration.get("temperature"), "c"),
        "voltage_range": _range_from_text(calibration.get("voltage"), "v"),
        "accuracy_impact": {
            "metric_name": "library_smoke_plus_task_metric_proxy",
            "estimated_drop": estimated_drop,
            "pass": estimated_drop <= 0.01,
            "reason": "AIHWKIT executed a real analog layer smoke. Accuracy impact remains a package-level estimate until a customer task dataset is run through an AIHWKIT-converted model.",
        },
        "calibration_profile": calibration_profile,
        "provenance": {
            "tool": "aihwkit",
            "version": getattr(aihwkit, "__version__", "unknown"),
            "target_profile": target_profile,
            "calibration_profile": calibration_profile,
            "source": "local AIHWKIT Python package smoke plus package analyzer summary",
            "model_id": model_id,
        },
    }
    output_path = run_dir / "analog-error-simulation.json"
    output_path.write_text(_json_dumps(evidence_payload), encoding="utf-8")
    return {
        "result_type": "adapter_run",
        "schema_version": ADAPTER_RUN_SCHEMA_VERSION,
        "adapter_id": adapter_id,
        "model_id": model_id,
        "run_id": run_id,
        "created_at": _utc_now(),
        "status": "completed",
        "provenance": "local AIHWKIT library run",
        "confidence": "medium",
        "summary": {
            "message": "AIHWKIT analog-layer smoke completed and normalized analog-error evidence was generated.",
            "aihwkit_version": getattr(aihwkit, "__version__", "unknown"),
            "torch_version": getattr(torch, "__version__", "unknown"),
            "analog_forward_shape": output_shape,
            "analog_forward_sum": output_sum,
            "estimated_accuracy_drop": estimated_drop,
            "next_step": "Convert the selected model layers into AIHWKIT analog modules and run a real task dataset before using this as task-accuracy support.",
        },
        "artifacts": [
            {
                "name": "analog-error-simulation",
                "path": str(output_path),
                "format": "json",
                "description": "Normalized analog-error evidence generated by a local AIHWKIT smoke run.",
            }
        ],
        "normalized_artifact_contract": {
            "source_id": "analog_error_simulation",
            "artifact_name": "analog-error-simulation.json",
            "minimum_fields": ["error_model", "temperature_range", "voltage_range", "accuracy_impact", "calibration_profile"],
            "claim_use": "Supports AIHWKIT availability and analog-behavior discussion; task claims need dataset-backed accuracy evidence.",
        },
        "normalized_evidence_source_id": "analog_error_simulation",
        "normalized_evidence_payload": evidence_payload,
        "claim_rule": "This is a real AIHWKIT library run, but it is a smoke run. It does not prove customer-task accuracy or measured hardware behavior.",
    }


def run_crosssim_simulation(model_record, output_root, target_profile="wearable", calibration_profile="sim-wearable-v0"):
    adapter_id = "sim.crosssim"
    model_id = model_record["model_id"]
    run_id = str(uuid4())
    run_dir = Path(output_root) / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    if not find_spec("simulator"):
        return _blocked_run(
            adapter_id,
            model_id,
            "CrossSim is not installed in the backend Python environment.",
            "Install CrossSim or configure ANALOG_AI_CROSSSIM_API_URL, then rerun the adapter.",
            run_id=run_id,
        )

    try:
        import numpy as np
        from simulator import AnalogCore, CrossSimParameters

        params = CrossSimParameters()
        weights = np.array([[1.0, -0.5], [0.25, 0.75]], dtype=float)
        vector = np.array([2.0, 4.0], dtype=float)
        core = AnalogCore(weights, params=params)
        analog_output = core @ vector
        ideal_output = weights @ vector
        max_abs_error = round(float(np.max(np.abs(analog_output - ideal_output))), 10)
    except Exception as exc:
        return _blocked_run(
            adapter_id,
            model_id,
            f"CrossSim import or AnalogCore smoke failed: {exc}",
            "Check CrossSim installation and run a minimal AnalogCore example, then rerun the adapter.",
            run_id=run_id,
        )

    calibration = get_calibration_profile(calibration_profile)
    correction = calibration.get("correction_factors", {})
    analysis = analyze_model(
        model_record["path"],
        target_profile=target_profile,
        calibration_profile=calibration_profile,
    )
    estimated_drop = _estimated_accuracy_drop(analysis, calibration)
    evidence_payload = {
        "error_model": {
            "model": "crosssim-analogcore-smoke",
            "library": "CrossSim",
            "library_version": "3.2.1",
            "matrix_shape": [2, 2],
            "vector_length": 2,
            "analog_output": [round(float(item), 6) for item in analog_output.tolist()],
            "ideal_output": [round(float(item), 6) for item in ideal_output.tolist()],
            "max_abs_error": max_abs_error,
            "gain_correction": correction.get("gain"),
            "offset_correction": correction.get("offset"),
            "drift_model": "not swept in smoke run",
        },
        "temperature_range": _range_from_text(calibration.get("temperature"), "c"),
        "voltage_range": _range_from_text(calibration.get("voltage"), "v"),
        "accuracy_impact": {
            "metric_name": "library_smoke_plus_task_metric_proxy",
            "estimated_drop": estimated_drop,
            "pass": estimated_drop <= 0.01,
            "reason": "CrossSim executed a real AnalogCore matrix-vector multiply. Accuracy impact remains a package-level estimate until the selected model or layer set is converted and evaluated.",
        },
        "calibration_profile": calibration_profile,
        "provenance": {
            "tool": "CrossSim",
            "version": "3.2.1",
            "target_profile": target_profile,
            "calibration_profile": calibration_profile,
            "source": "local CrossSim AnalogCore smoke plus package analyzer summary",
            "model_id": model_id,
        },
    }
    output_path = run_dir / "analog-error-simulation.json"
    output_path.write_text(_json_dumps(evidence_payload), encoding="utf-8")
    return {
        "result_type": "adapter_run",
        "schema_version": ADAPTER_RUN_SCHEMA_VERSION,
        "adapter_id": adapter_id,
        "model_id": model_id,
        "run_id": run_id,
        "created_at": _utc_now(),
        "status": "completed",
        "provenance": "local CrossSim library run",
        "confidence": "medium",
        "summary": {
            "message": "CrossSim AnalogCore smoke completed and normalized analog-error evidence was generated.",
            "crosssim_version": "3.2.1",
            "matrix_shape": [2, 2],
            "max_abs_error": max_abs_error,
            "estimated_accuracy_drop": estimated_drop,
            "next_step": "Map selected customer model layers into CrossSim AnalogCore or PyTorch layers and run task data before using this as workload accuracy evidence.",
        },
        "artifacts": [
            {
                "name": "analog-error-simulation",
                "path": str(output_path),
                "format": "json",
                "description": "Normalized analog-error evidence generated by a local CrossSim AnalogCore smoke run.",
            }
        ],
        "normalized_artifact_contract": {
            "source_id": "analog_error_simulation",
            "artifact_name": "analog-error-simulation.json",
            "minimum_fields": ["error_model", "temperature_range", "voltage_range", "accuracy_impact", "calibration_profile"],
            "claim_use": "Supports CrossSim availability and crossbar-behavior discussion; task claims need dataset-backed accuracy evidence.",
        },
        "normalized_evidence_source_id": "analog_error_simulation",
        "normalized_evidence_payload": evidence_payload,
        "claim_rule": "This is a real CrossSim library run, but it is a smoke run. It does not prove customer-task accuracy or measured hardware behavior.",
    }


def _metric_name(task_metric):
    metric = (task_metric or "task_metric").split("/")[0].strip().lower()
    return metric.replace(" ", "_").replace("-", "_")


def _load_accuracy_dataset(dataset_path):
    path = Path(dataset_path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset path does not exist: {dataset_path}")
    if path.suffix.lower() == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        records = payload.get("records", payload if isinstance(payload, list) else [])
        dataset_id = payload.get("dataset_id", path.stem) if isinstance(payload, dict) else path.stem
        metric_name = payload.get("metric_name", "accuracy") if isinstance(payload, dict) else "accuracy"
        tolerance = float(payload.get("tolerance", 0.01)) if isinstance(payload, dict) else 0.01
    elif path.suffix.lower() == ".jsonl":
        records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        dataset_id = path.stem
        metric_name = "accuracy"
        tolerance = 0.01
    elif path.suffix.lower() == ".csv":
        with path.open(newline="", encoding="utf-8") as handle:
            records = list(csv.DictReader(handle))
        dataset_id = path.stem
        metric_name = "accuracy"
        tolerance = 0.01
    else:
        raise ValueError("Dataset must be .json, .jsonl, or .csv.")
    if not records:
        raise ValueError("Dataset contains no records.")
    return {
        "path": path,
        "dataset_id": dataset_id,
        "metric_name": metric_name,
        "tolerance": tolerance,
        "records": records,
    }


def _record_label(record, *names):
    for name in names:
        if name in record:
            return str(record[name])
    return None


def _classification_accuracy(records, prediction_field):
    total = 0
    correct = 0
    failures = []
    for index, record in enumerate(records):
        expected = _record_label(record, "expected_label", "label", "expected")
        predicted = _record_label(record, prediction_field)
        if expected is None or predicted is None:
            continue
        total += 1
        if expected == predicted:
            correct += 1
        elif len(failures) < 5:
            failures.append({
                "index": index,
                "expected": expected,
                "predicted": predicted,
            })
    if total == 0:
        raise ValueError(f"Dataset has no comparable expected_label and {prediction_field} fields.")
    return round(correct / total, 4), total, failures


def _run_dataset_task_accuracy(
    model_record,
    output_root,
    dataset_path,
    target_profile,
    calibration_profile,
    modality,
):
    adapter_id = "accuracy.local-task-check"
    model_id = model_record["model_id"]
    run_id = str(uuid4())
    run_dir = Path(output_root) / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    dataset = _load_accuracy_dataset(dataset_path)
    baseline_metric, evaluated_records, baseline_failures = _classification_accuracy(dataset["records"], "baseline_prediction")
    candidate_metric, _, candidate_failures = _classification_accuracy(dataset["records"], "candidate_prediction")
    tolerance = dataset["tolerance"]
    metric_delta = round(baseline_metric - candidate_metric, 4)
    lab = simulated_lab_metadata(target_profile, modality=modality)
    evidence_payload = {
        "dataset_id": dataset["dataset_id"],
        "metric_name": dataset["metric_name"],
        "baseline_metric": baseline_metric,
        "candidate_metric": candidate_metric,
        "tolerance": tolerance,
        "pass": metric_delta <= tolerance,
        "provenance": {
            "tool": "dataset-backed-task-accuracy-adapter",
            "version": ADAPTER_RUN_SCHEMA_VERSION,
            "target_profile": target_profile,
            "calibration_profile": calibration_profile,
            "modality": modality,
            "simulation_profile_id": lab["scenario_id"],
            "source": "local dataset file with expected labels, baseline predictions, and candidate predictions",
            "dataset_path": str(dataset["path"]),
            "model_id": model_id,
        },
        "simulation_profile": lab,
        "record_count": evaluated_records,
        "metric_delta": metric_delta,
        "failure_examples": {
            "baseline": baseline_failures,
            "candidate": candidate_failures,
        },
        "notes": "Dataset-backed local evidence. It supports task-accuracy discussion only for this dataset, metric, model, target profile, calibration profile, and candidate prediction source.",
    }
    output_path = run_dir / "task-accuracy-report.json"
    output_path.write_text(_json_dumps(evidence_payload), encoding="utf-8")
    return {
        "result_type": "adapter_run",
        "schema_version": ADAPTER_RUN_SCHEMA_VERSION,
        "adapter_id": adapter_id,
        "model_id": model_id,
        "run_id": run_id,
        "created_at": _utc_now(),
        "status": "completed",
        "provenance": "dataset-backed local task accuracy evaluation",
        "confidence": "medium",
        "summary": {
            "message": "Task-accuracy artifact generated from a local dataset file.",
            "dataset_id": dataset["dataset_id"],
            "record_count": evaluated_records,
            "metric_name": evidence_payload["metric_name"],
            "baseline_metric": baseline_metric,
            "candidate_metric": candidate_metric,
            "metric_delta": metric_delta,
            "tolerance": tolerance,
            "pass": evidence_payload["pass"],
            "target_profile": target_profile,
            "calibration_profile": calibration_profile,
            "modality": modality,
            "simulation_profile": lab["label"],
            "next_step": "Use the real task dataset and prediction outputs from the mapped candidate model before customer claims.",
        },
        "artifacts": [
            {
                "name": "task-accuracy-report",
                "path": str(output_path),
                "format": "json",
                "description": "Normalized task-accuracy evidence generated from a local dataset file.",
            }
        ],
        "normalized_artifact_contract": {
            "source_id": "task_accuracy",
            "artifact_name": "task-accuracy-report.json",
            "minimum_fields": ["dataset_id", "metric_name", "baseline_metric", "candidate_metric", "tolerance", "pass"],
            "claim_use": "Supports task accuracy discussion for this dataset and candidate prediction source.",
        },
        "normalized_evidence_source_id": "task_accuracy",
        "normalized_evidence_payload": evidence_payload,
        "claim_rule": "This artifact can support task-accuracy discussion for the stated dataset, but it is still not production readiness.",
    }


def run_task_accuracy(model_record, output_root, target_profile="wearable", calibration_profile="sim-wearable-v0", modality="vision_classification", dataset_path=None):
    adapter_id = "accuracy.local-task-check"
    model_id = model_record["model_id"]
    run_id = str(uuid4())
    run_dir = Path(output_root) / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    input_path = Path(model_record["path"])

    try:
        external = call_external_service(
            adapter_id,
            "task_accuracy",
            "task-accuracy-report.json",
            {
                "model_id": model_id,
                "model_path": str(input_path),
                "model_filename": model_record.get("filename"),
                "target_profile": target_profile,
                "calibration_profile": calibration_profile,
                "modality": modality,
                "dataset_path": str(dataset_path) if dataset_path else None,
            },
            run_dir,
            timeout_seconds=60,
        )
    except ExternalAdapterError as exc:
        return _blocked_run(
            adapter_id,
            model_id,
            f"Configured accuracy service failed: {exc}",
            "Check ANALOG_AI_ACCURACY_API_URL, service /run behavior, dataset access, and normalized task-accuracy evidence contract.",
            run_id=run_id,
            artifacts=_external_failure_artifacts(exc),
        )
    if external:
        evidence_payload = external["payload"]
        output_path = run_dir / "task-accuracy-report.json"
        output_path.write_text(_json_dumps(evidence_payload), encoding="utf-8")
        return {
            "result_type": "adapter_run",
            "schema_version": ADAPTER_RUN_SCHEMA_VERSION,
            "adapter_id": adapter_id,
            "model_id": model_id,
            "run_id": run_id,
            "created_at": _utc_now(),
            "status": "completed",
            "provenance": "configured external task accuracy service",
            "confidence": "medium",
            "summary": {
                "message": "Task-accuracy artifact returned by configured external service.",
                "dataset_id": evidence_payload.get("dataset_id"),
                "metric_name": evidence_payload.get("metric_name"),
                "baseline_metric": evidence_payload.get("baseline_metric"),
                "candidate_metric": evidence_payload.get("candidate_metric"),
                "tolerance": evidence_payload.get("tolerance"),
                "pass": evidence_payload.get("pass"),
                "target_profile": target_profile,
                "calibration_profile": calibration_profile,
                "modality": modality,
                "service_url": external["service_url"],
                "next_step": "Validate and import this task-accuracy artifact, then pair it with analog error evidence.",
            },
            "artifacts": [
                {
                    "name": "task-accuracy-report",
                    "path": str(output_path),
                    "format": "json",
                    "description": "Normalized task-accuracy evidence returned by the configured external service.",
                },
                {
                    "name": "external-service-request",
                    "path": external["raw_request_path"],
                    "format": "json",
                    "description": "Raw request sent to the configured task accuracy service.",
                },
                {
                    "name": "external-service-response",
                    "path": external["raw_response_path"],
                    "format": "json",
                    "description": "Raw response returned by the configured task accuracy service.",
                },
            ],
            "normalized_artifact_contract": {
                "source_id": "task_accuracy",
                "artifact_name": "task-accuracy-report.json",
                "minimum_fields": ["dataset_id", "metric_name", "baseline_metric", "candidate_metric", "tolerance", "pass"],
                "claim_use": "Supports task accuracy discussion for the dataset, metric, target setup, and candidate source in the artifact.",
            },
            "normalized_evidence_source_id": "task_accuracy",
            "normalized_evidence_payload": evidence_payload,
            "claim_rule": "This artifact came from a configured task accuracy service. It supports accuracy discussion only for the stated dataset, metric, and candidate source.",
        }

    if dataset_path:
        return _run_dataset_task_accuracy(
            model_record,
            output_root,
            dataset_path,
            target_profile,
            calibration_profile,
            modality,
        )

    analysis = analyze_model(
        model_record["path"],
        target_profile=target_profile,
        calibration_profile=calibration_profile,
    )
    quantization = estimate_quantization(analysis, modality=modality)
    calibration = get_calibration_profile(calibration_profile)
    lab = simulated_lab_metadata(target_profile, modality=modality)
    analog_drop = _estimated_accuracy_drop(analysis, calibration)
    baseline_trial = next((item for item in quantization.get("trials", []) if item.get("precision") == "baseline"), {})
    candidate_trial = next((item for item in quantization.get("trials", []) if item.get("precision") == "INT4 selective"), None)
    if not candidate_trial:
        candidate_trial = next((item for item in quantization.get("trials", []) if item.get("precision") == "INT8"), {})
    baseline_metric = round(float(baseline_trial.get("metric_value", 95.0)) / 100.0, 4)
    candidate_metric = round(max((float(candidate_trial.get("metric_value", 93.0)) / 100.0) - analog_drop, 0.0), 4)
    tolerance = 0.02 if modality in {"robotics_perception", "edge_llm", "industrial_anomaly"} else 0.01
    metric_delta = round(baseline_metric - candidate_metric, 4)
    evidence_payload = {
        "dataset_id": f"local-synthetic-{modality}",
        "metric_name": _metric_name(quantization.get("task_metric")),
        "baseline_metric": baseline_metric,
        "candidate_metric": candidate_metric,
        "tolerance": tolerance,
        "pass": metric_delta <= tolerance,
        "provenance": {
            "tool": "local-task-accuracy-adapter",
            "version": ADAPTER_RUN_SCHEMA_VERSION,
            "target_profile": target_profile,
            "calibration_profile": calibration_profile,
            "modality": modality,
            "simulation_profile_id": lab["scenario_id"],
            "source": "quantization estimate plus local analog error estimate",
            "model_id": model_id,
        },
        "simulation_profile": lab,
        "notes": "Synthetic local estimate for workflow validation. Replace with dataset-backed evaluation before using in customer or benchmark claims.",
    }
    output_path = run_dir / "task-accuracy-report.json"
    output_path.write_text(_json_dumps(evidence_payload), encoding="utf-8")

    return {
        "result_type": "adapter_run",
        "schema_version": ADAPTER_RUN_SCHEMA_VERSION,
        "adapter_id": adapter_id,
        "model_id": model_id,
        "run_id": run_id,
        "created_at": _utc_now(),
        "status": "completed",
        "provenance": "local synthetic task accuracy estimate",
        "confidence": "low",
        "summary": {
            "message": "Task-accuracy artifact generated from local quantization and analog-error estimates.",
            "metric_name": evidence_payload["metric_name"],
            "baseline_metric": baseline_metric,
            "candidate_metric": candidate_metric,
            "metric_delta": metric_delta,
            "tolerance": tolerance,
            "pass": evidence_payload["pass"],
            "target_profile": target_profile,
            "calibration_profile": calibration_profile,
            "modality": modality,
            "simulation_profile": lab["label"],
            "next_step": "Replace this with a real dataset run before claiming task accuracy is preserved.",
        },
        "artifacts": [
            {
                "name": "task-accuracy-report",
                "path": str(output_path),
                "format": "json",
                "description": "Normalized task-accuracy evidence generated from local quantization and analog-error estimates.",
            }
        ],
        "normalized_artifact_contract": {
            "source_id": "task_accuracy",
            "artifact_name": "task-accuracy-report.json",
            "minimum_fields": ["dataset_id", "metric_name", "baseline_metric", "candidate_metric", "tolerance", "pass"],
            "claim_use": "Supports task accuracy discussion for this synthetic dataset placeholder only; replace with real dataset evidence.",
        },
        "normalized_evidence_source_id": "task_accuracy",
        "normalized_evidence_payload": evidence_payload,
        "claim_rule": "This artifact is a local estimate. It should not be used as customer accuracy proof until replaced by a dataset-backed evaluation.",
    }


def run_board_runtime(model_record, output_root, target_profile="wearable", calibration_profile="sim-wearable-v0", modality="vision_classification", runtime_mode="balanced"):
    adapter_id = "board.runtime"
    model_id = model_record["model_id"]
    run_id = str(uuid4())
    run_dir = Path(output_root) / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    input_path = Path(model_record["path"])

    try:
        external = call_external_service(
            adapter_id,
            "board_runtime",
            "board-runtime-trace.json",
            {
                "model_id": model_id,
                "model_path": str(input_path),
                "model_filename": model_record.get("filename"),
                "target_profile": target_profile,
                "calibration_profile": calibration_profile,
                "modality": modality,
                "runtime_mode": runtime_mode,
            },
            run_dir,
        )
    except ExternalAdapterError as exc:
        return _blocked_run(
            adapter_id,
            model_id,
            f"Configured board runtime service failed: {exc}",
            "Check ANALOG_AI_BOARD_API_URL, service /run behavior, and normalized board-runtime evidence contract.",
            run_id=run_id,
            artifacts=_external_failure_artifacts(exc),
        )
    if external:
        evidence_payload = external["payload"]
        output_path = run_dir / "board-runtime-trace.json"
        output_path.write_text(_json_dumps(evidence_payload), encoding="utf-8")
        return {
            "result_type": "adapter_run",
            "schema_version": ADAPTER_RUN_SCHEMA_VERSION,
            "adapter_id": adapter_id,
            "model_id": model_id,
            "run_id": run_id,
            "created_at": _utc_now(),
            "status": "completed",
            "provenance": "configured external board runtime service",
            "confidence": "medium",
            "summary": {
                "message": "Board-runtime artifact returned by configured external service.",
                "latency_ms": evidence_payload.get("latency_ms"),
                "trace_layers": len(evidence_payload.get("trace") or []),
                "fallback_events": len(evidence_payload.get("fallback_events") or []),
                "target_profile": target_profile,
                "calibration_profile": calibration_profile,
                "runtime_mode": runtime_mode,
                "service_url": external["service_url"],
                "next_step": "Validate and import this external service artifact, then keep raw request and response files with the package.",
            },
            "artifacts": [
                {
                    "name": "board-runtime-trace",
                    "path": str(output_path),
                    "format": "json",
                    "description": "Normalized board-runtime evidence returned by the configured external service.",
                },
                {
                    "name": "external-service-request",
                    "path": external["raw_request_path"],
                    "format": "json",
                    "description": "Raw request sent to the configured board runtime service.",
                },
                {
                    "name": "external-service-response",
                    "path": external["raw_response_path"],
                    "format": "json",
                    "description": "Raw response returned by the configured board runtime service.",
                },
            ],
            "normalized_artifact_contract": {
                "source_id": "board_runtime",
                "artifact_name": "board-runtime-trace.json",
                "minimum_fields": ["board_id", "runtime_version", "latency_ms", "trace", "fallback_events", "provenance"],
                "claim_use": "Supports latency discussion when the external service provenance matches the target setup.",
            },
            "normalized_evidence_source_id": "board_runtime",
            "normalized_evidence_payload": evidence_payload,
            "claim_rule": "This artifact came from a configured external service. It still needs validation, import, and matching power/accuracy evidence before broader claims.",
        }

    analysis = analyze_model(
        model_record["path"],
        target_profile=target_profile,
        calibration_profile=calibration_profile,
    )
    quantization = estimate_quantization(analysis, modality=modality)
    runtime = run_simulated_profile(analysis, quantization_report=quantization, runtime_mode=runtime_mode)
    lab = simulated_lab_metadata(target_profile, modality=modality, runtime_mode=runtime_mode)
    fallback_events = [
        {
            "layer_id": item["layer_id"],
            "operator": item.get("operator"),
            "placement": item.get("placement"),
            "reason": item.get("note"),
        }
        for item in runtime.get("trace", [])
        if item.get("placement") in {"fallback", "unsupported"}
    ]
    evidence_payload = {
        "board_id": f"{lab['scenario_id']}-board-sim",
        "runtime_version": f"local-runtime-{runtime_mode}-{lab['scenario_id']}-{ADAPTER_RUN_SCHEMA_VERSION}",
        "latency_ms": runtime.get("summary", {}).get("latency_ms"),
        "trace": [
            {
                "layer_id": item["layer_id"],
                "operator": item.get("operator"),
                "placement": item.get("placement"),
                "latency_ms": item.get("latency_ms"),
                "energy_uj": item.get("energy_uj"),
            }
            for item in runtime.get("trace", [])
        ],
        "fallback_events": fallback_events,
        "simulation_profile": lab,
        "provenance": {
            "tool": "local-board-runtime-adapter",
            "version": ADAPTER_RUN_SCHEMA_VERSION,
            "target_profile": target_profile,
            "calibration_profile": calibration_profile,
            "runtime_mode": runtime_mode,
            "simulation_profile_id": lab["scenario_id"],
            "source": "runtime_profile.run_simulated_profile plus scenario-based simulated lab profile",
            "model_id": model_id,
        },
    }
    replay = write_replay_artifacts(
        run_dir,
        adapter_id,
        {
            "model_id": model_id,
            "target_profile": target_profile,
            "calibration_profile": calibration_profile,
            "modality": modality,
            "runtime_mode": runtime_mode,
            "expected_artifact": "board-runtime-trace.json",
        },
        evidence_payload,
        target_profile,
        calibration_profile,
        modality=modality,
        runtime_mode=runtime_mode,
    )
    if replay:
        evidence_payload["external_replay_fixture"] = replay
        evidence_payload["provenance"]["external_replay_fixture"] = True
    output_path = run_dir / "board-runtime-trace.json"
    output_path.write_text(_json_dumps(evidence_payload), encoding="utf-8")

    return {
        "result_type": "adapter_run",
        "schema_version": ADAPTER_RUN_SCHEMA_VERSION,
        "adapter_id": adapter_id,
        "model_id": model_id,
        "run_id": run_id,
        "created_at": _utc_now(),
        "status": "completed",
        "provenance": "local simulated board runtime",
        "confidence": "low",
        "summary": {
            "message": "Board-runtime artifact generated from the local runtime simulator.",
            "latency_ms": evidence_payload["latency_ms"],
            "trace_layers": len(evidence_payload["trace"]),
            "fallback_events": len(fallback_events),
            "target_profile": target_profile,
            "calibration_profile": calibration_profile,
            "runtime_mode": runtime_mode,
            "simulation_profile": lab["label"],
            "next_step": "Replace this with a real board or simulator trace before claiming measured latency.",
        },
        "artifacts": [
            {
                "name": "board-runtime-trace",
                "path": str(output_path),
                "format": "json",
                "description": "Normalized board-runtime evidence generated from the local runtime simulator.",
            }
        ] + ([
            {
                "name": "external-replay-request",
                "path": replay["raw_request_path"],
                "format": "json",
                "description": "Replay fixture request shaped like an external board runtime service call.",
            },
            {
                "name": "external-replay-response",
                "path": replay["raw_response_path"],
                "format": "json",
                "description": "Replay fixture response carrying the normalized board-runtime payload.",
            },
        ] if replay else []),
        "normalized_artifact_contract": {
            "source_id": "board_runtime",
            "artifact_name": "board-runtime-trace.json",
            "minimum_fields": ["board_id", "runtime_version", "latency_ms", "trace", "fallback_events", "provenance"],
            "claim_use": "Supports local latency-flow testing. Replace with board or simulator evidence for measured latency claims.",
        },
        "normalized_evidence_source_id": "board_runtime",
        "normalized_evidence_payload": evidence_payload,
        "claim_rule": "This artifact is a simulated runtime trace. It does not prove measured board latency.",
    }


def _power_trace(energy_uj, latency_ms):
    latency = max(float(latency_ms or 1.0), 0.1)
    avg_power_mw = energy_uj / latency
    return [
        {"time_ms": 0, "power_mw": round(avg_power_mw * 0.92, 3)},
        {"time_ms": round(latency / 2, 3), "power_mw": round(avg_power_mw * 1.08, 3)},
        {"time_ms": round(latency, 3), "power_mw": round(avg_power_mw * 0.97, 3)},
    ]


def run_power_thermal(model_record, output_root, target_profile="wearable", calibration_profile="sim-wearable-v0", modality="vision_classification", runtime_mode="balanced"):
    adapter_id = "metrics.power-thermal"
    model_id = model_record["model_id"]
    run_id = str(uuid4())
    run_dir = Path(output_root) / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    input_path = Path(model_record["path"])

    try:
        external = call_external_service(
            adapter_id,
            "power_thermal",
            "power-thermal-report.json",
            {
                "model_id": model_id,
                "model_path": str(input_path),
                "model_filename": model_record.get("filename"),
                "target_profile": target_profile,
                "calibration_profile": calibration_profile,
                "modality": modality,
                "runtime_mode": runtime_mode,
            },
            run_dir,
        )
    except ExternalAdapterError as exc:
        return _blocked_run(
            adapter_id,
            model_id,
            f"Configured power/thermal service failed: {exc}",
            "Check ANALOG_AI_POWER_METER_URL, service /run behavior, and normalized power-thermal evidence contract.",
            run_id=run_id,
            artifacts=_external_failure_artifacts(exc),
        )
    if external:
        evidence_payload = external["payload"]
        output_path = run_dir / "power-thermal-report.json"
        output_path.write_text(_json_dumps(evidence_payload), encoding="utf-8")
        return {
            "result_type": "adapter_run",
            "schema_version": ADAPTER_RUN_SCHEMA_VERSION,
            "adapter_id": adapter_id,
            "model_id": model_id,
            "run_id": run_id,
            "created_at": _utc_now(),
            "status": "completed",
            "provenance": "configured external power and thermal service",
            "confidence": "medium",
            "summary": {
                "message": "Power/thermal artifact returned by configured external service.",
                "energy_uj": evidence_payload.get("energy_uj"),
                "power_samples": len(evidence_payload.get("power_trace") or []),
                "temperature_samples": len(evidence_payload.get("temperature_trace") or []),
                "target_profile": target_profile,
                "calibration_profile": calibration_profile,
                "runtime_mode": runtime_mode,
                "service_url": external["service_url"],
                "next_step": "Validate and import this external service artifact, then keep raw request and response files with the package.",
            },
            "artifacts": [
                {
                    "name": "power-thermal-report",
                    "path": str(output_path),
                    "format": "json",
                    "description": "Normalized power/thermal evidence returned by the configured external service.",
                },
                {
                    "name": "external-service-request",
                    "path": external["raw_request_path"],
                    "format": "json",
                    "description": "Raw request sent to the configured power/thermal service.",
                },
                {
                    "name": "external-service-response",
                    "path": external["raw_response_path"],
                    "format": "json",
                    "description": "Raw response returned by the configured power/thermal service.",
                },
            ],
            "normalized_artifact_contract": {
                "source_id": "power_thermal",
                "artifact_name": "power-thermal-report.json",
                "minimum_fields": ["energy_uj", "power_trace", "temperature_trace", "sampling_rate", "measurement_setup"],
                "claim_use": "Supports energy and thermal discussion when the external service provenance matches the runtime setup.",
            },
            "normalized_evidence_source_id": "power_thermal",
            "normalized_evidence_payload": evidence_payload,
            "claim_rule": "This artifact came from a configured external service. It still needs validation, import, and matching runtime/accuracy evidence before broader claims.",
        }

    analysis = analyze_model(
        model_record["path"],
        target_profile=target_profile,
        calibration_profile=calibration_profile,
    )
    quantization = estimate_quantization(analysis, modality=modality)
    runtime = run_simulated_profile(analysis, quantization_report=quantization, runtime_mode=runtime_mode)
    lab = simulated_lab_metadata(target_profile, modality=modality, runtime_mode=runtime_mode)
    summary = runtime.get("summary", {})
    energy_model = lab["profile"].get("energy_model", {})
    host_overhead_uj = float(energy_model.get("host_overhead_uj") or 0.0)
    energy_uj = float(summary.get("energy_uj") or 0.0) + host_overhead_uj
    latency_ms = float(summary.get("latency_ms") or 1.0)
    calibration = get_calibration_profile(calibration_profile)
    voltage = _range_from_text(calibration.get("voltage"), "v")
    supply_voltage = round((voltage["min_v"] + voltage["max_v"]) / 2, 3)
    temp = _range_from_text(calibration.get("temperature"), "c")
    base_temp = min(max(temp["min_c"] + 25, 25), temp["max_c"])
    thermal_rise = round(max(energy_uj / 100.0, 0.1), 2)
    evidence_payload = {
        "energy_uj": round(energy_uj, 3),
        "power_trace": _power_trace(energy_uj, latency_ms),
        "temperature_trace": [
            {"time_ms": 0, "temperature_c": round(base_temp, 2)},
            {"time_ms": round(latency_ms, 3), "temperature_c": round(base_temp + thermal_rise, 2)},
        ],
        "sampling_rate": "local simulated 1 kHz",
        "measurement_setup": {
            "meter": "local-power-thermal-adapter",
            "supply_voltage": supply_voltage,
            "includes_host_overhead": True,
            "runtime_mode": runtime_mode,
            "source": "runtime_profile.run_simulated_profile",
            "not_measured_hardware": True,
            "simulation_profile_id": lab["scenario_id"],
            "host_overhead_uj": host_overhead_uj,
        },
        "simulation_profile": lab,
        "provenance": {
            "tool": "local-power-thermal-adapter",
            "version": ADAPTER_RUN_SCHEMA_VERSION,
            "target_profile": target_profile,
            "calibration_profile": calibration_profile,
            "runtime_mode": runtime_mode,
            "simulation_profile_id": lab["scenario_id"],
            "model_id": model_id,
        },
    }
    replay = write_replay_artifacts(
        run_dir,
        adapter_id,
        {
            "model_id": model_id,
            "target_profile": target_profile,
            "calibration_profile": calibration_profile,
            "modality": modality,
            "runtime_mode": runtime_mode,
            "expected_artifact": "power-thermal-report.json",
            "synchronized_runtime_source": "local simulated runtime trace",
        },
        evidence_payload,
        target_profile,
        calibration_profile,
        modality=modality,
        runtime_mode=runtime_mode,
    )
    if replay:
        evidence_payload["external_replay_fixture"] = replay
        evidence_payload["measurement_setup"]["external_replay_fixture"] = True
        evidence_payload["provenance"]["external_replay_fixture"] = True
    output_path = run_dir / "power-thermal-report.json"
    output_path.write_text(_json_dumps(evidence_payload), encoding="utf-8")

    return {
        "result_type": "adapter_run",
        "schema_version": ADAPTER_RUN_SCHEMA_VERSION,
        "adapter_id": adapter_id,
        "model_id": model_id,
        "run_id": run_id,
        "created_at": _utc_now(),
        "status": "completed",
        "provenance": "local simulated power and thermal estimate",
        "confidence": "low",
        "summary": {
            "message": "Power/thermal artifact generated from the local runtime simulator.",
            "energy_uj": evidence_payload["energy_uj"],
            "peak_power_mw": max(item["power_mw"] for item in evidence_payload["power_trace"]),
            "temperature_rise_c": thermal_rise,
            "target_profile": target_profile,
            "calibration_profile": calibration_profile,
            "runtime_mode": runtime_mode,
            "simulation_profile": lab["label"],
            "next_step": "Replace this with a synchronized power-meter and temperature trace before claiming measured energy.",
        },
        "artifacts": [
            {
                "name": "power-thermal-report",
                "path": str(output_path),
                "format": "json",
                "description": "Normalized power/thermal evidence generated from the local runtime simulator.",
            }
        ] + ([
            {
                "name": "external-replay-request",
                "path": replay["raw_request_path"],
                "format": "json",
                "description": "Replay fixture request shaped like an external power/thermal service call.",
            },
            {
                "name": "external-replay-response",
                "path": replay["raw_response_path"],
                "format": "json",
                "description": "Replay fixture response carrying the normalized power/thermal payload.",
            },
        ] if replay else []),
        "normalized_artifact_contract": {
            "source_id": "power_thermal",
            "artifact_name": "power-thermal-report.json",
            "minimum_fields": ["energy_uj", "power_trace", "temperature_trace", "sampling_rate", "measurement_setup"],
            "claim_use": "Supports local energy-flow testing. Replace with measured power and thermal evidence for energy claims.",
        },
        "normalized_evidence_source_id": "power_thermal",
        "normalized_evidence_payload": evidence_payload,
        "claim_rule": "This artifact is a simulated power and thermal report. It does not prove measured hardware energy.",
    }


def _json_dumps(payload):
    import json

    return json.dumps(payload, indent=2, sort_keys=True)


def run_adapter(
    adapter_id,
    model_record,
    output_root,
    target_profile="wearable",
    calibration_profile="sim-wearable-v0",
    modality="vision_classification",
    runtime_mode="balanced",
    dataset_path=None,
):
    if adapter_id == "quantization.onnxruntime":
        return run_onnxruntime_quantization(model_record, output_root)
    if adapter_id == "compiler.tvm-mlir-iree":
        return run_compiler_mapping(
            model_record,
            output_root,
            target_profile=target_profile,
            calibration_profile=calibration_profile,
        )
    if adapter_id == "analog.error-simulator":
        return run_analog_error_simulation(
            model_record,
            output_root,
            target_profile=target_profile,
            calibration_profile=calibration_profile,
        )
    if adapter_id == "sim.aihwkit":
        return run_aihwkit_simulation(
            model_record,
            output_root,
            target_profile=target_profile,
            calibration_profile=calibration_profile,
        )
    if adapter_id == "sim.crosssim":
        return run_crosssim_simulation(
            model_record,
            output_root,
            target_profile=target_profile,
            calibration_profile=calibration_profile,
        )
    if adapter_id == "accuracy.local-task-check":
        return run_task_accuracy(
            model_record,
            output_root,
            target_profile=target_profile,
            calibration_profile=calibration_profile,
            modality=modality,
            dataset_path=dataset_path,
        )
    if adapter_id == "board.runtime":
        return run_board_runtime(
            model_record,
            output_root,
            target_profile=target_profile,
            calibration_profile=calibration_profile,
            modality=modality,
            runtime_mode=runtime_mode,
        )
    if adapter_id == "metrics.power-thermal":
        return run_power_thermal(
            model_record,
            output_root,
            target_profile=target_profile,
            calibration_profile=calibration_profile,
            modality=modality,
            runtime_mode=runtime_mode,
        )
    return None
