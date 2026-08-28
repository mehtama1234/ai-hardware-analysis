from importlib.util import find_spec
import os
from urllib.error import URLError
from urllib.request import Request, urlopen

from external_replay import replay_fixture_enabled, replay_fixture_probe


ADAPTER_SCHEMA_VERSION = "adapter-registry-v0.1"
ADAPTER_PROBE_SCHEMA_VERSION = "adapter-probe-v0.1"


def _python_package_available(package):
    return find_spec(package) is not None


def _env_configured(name):
    return bool(os.environ.get(name))


def _env_value(name):
    return os.environ.get(name, "").strip()


def _adapter(
    adapter_id,
    name,
    category,
    status,
    provenance,
    confidence,
    purpose,
    normalized_outputs,
    next_step,
    evidence=None,
):
    return {
        "id": adapter_id,
        "name": name,
        "category": category,
        "status": status,
        "provenance": provenance,
        "confidence": confidence,
        "purpose": purpose,
        "normalized_outputs": normalized_outputs,
        "next_step": next_step,
        "evidence": evidence or [],
    }


def adapter_registry():
    onnx_available = _python_package_available("onnx")
    onnxruntime_available = _python_package_available("onnxruntime")
    tvm_available = _python_package_available("tvm")
    iree_available = _python_package_available("iree")
    aihwkit_available = _python_package_available("aihwkit")
    crosssim_available = _python_package_available("simulator") or _python_package_available("cross_sim")
    compiler_api_configured = _env_configured("ANALOG_AI_COMPILER_API_URL")
    analog_mlir_configured = _env_configured("ANALOG_AI_ANALOG_MLIR_API_URL")
    analog_sim_configured = _env_configured("ANALOG_AI_ERROR_SIM_URL")
    aihwkit_configured = _env_configured("ANALOG_AI_AIHWKIT_API_URL")
    crosssim_configured = _env_configured("ANALOG_AI_CROSSSIM_API_URL")
    sst_golem_configured = _env_configured("ANALOG_AI_SST_GOLEM_API_URL")
    alpine_configured = _env_configured("ANALOG_AI_ALPINE_GEM5X_API_URL")
    attention_partition_configured = _env_configured("ANALOG_AI_ATTENTION_PARTITION_API_URL")
    accuracy_api_configured = _env_configured("ANALOG_AI_ACCURACY_API_URL")
    board_api_configured = _env_configured("ANALOG_AI_BOARD_API_URL")
    power_meter_configured = _env_configured("ANALOG_AI_POWER_METER_URL")
    replay_enabled = replay_fixture_enabled()

    adapters = [
        _adapter(
            "model-import.onnx",
            "ONNX importer",
            "model import",
            "available" if onnx_available else "missing dependency",
            "local package check",
            "medium" if onnx_available else "low",
            "Load an ONNX model and extract graph, shape, operator, and parameter information.",
            ["model graph", "operator list", "shape summary", "parameter count"],
            "Keep ONNX as the first supported interchange format.",
            [f"onnx package available: {onnx_available}"],
        ),
        _adapter(
            "quantization.local-estimate",
            "Local quantization estimator",
            "quantization",
            "available",
            "local rule-based estimate",
            "low",
            "Mark sensitive layers and propose protected INT8 or lower precision candidates by modality.",
            ["precision policy", "protected layers", "estimated task metric", "risk labels"],
            "Replace estimates with dataset-backed quantization runs.",
        ),
        _adapter(
            "runtime.local-simulator",
            "Local runtime estimator",
            "runtime",
            "available",
            "local simulation",
            "low",
            "Estimate completed-inference latency and energy from mapped layers, conversion costs, memory cost, host overhead, and idle energy.",
            ["runtime trace", "latency estimate", "energy estimate", "bottlenecks", "target pass/fail"],
            "Connect an operator-level simulator or board runtime adapter.",
        ),
        _adapter(
            "baseline.digital-estimate",
            "Digital baseline estimator",
            "baseline",
            "available",
            "local estimate",
            "low",
            "Compare the analog path with an estimated all-digital completed-inference path.",
            ["digital latency estimate", "digital energy estimate", "counted costs", "excluded costs"],
            "Replace with measured digital baseline under the same accuracy and latency target.",
        ),
        _adapter(
            "quantization.onnxruntime",
            "ONNX Runtime quantization",
            "quantization",
            "available" if onnxruntime_available else "not connected",
            "dependency check",
            "medium" if onnxruntime_available else "low",
            "Run real ONNX quantization and compare model outputs on calibration data.",
            ["quantized model", "calibration metrics", "per-layer sensitivity"],
            "Install and connect ONNX Runtime quantization when calibration datasets are available.",
            [f"onnxruntime package available: {onnxruntime_available}"],
        ),
        _adapter(
            "compiler.tvm-mlir-iree",
            "Compiler mapping adapter",
            "compiler",
            "configured" if compiler_api_configured else "available dependency" if tvm_available or iree_available else "not connected",
            "environment check plus dependency check",
            "medium" if compiler_api_configured else "low",
            "Replace rule-based placement with compiler-produced tiling, memory, and operator mapping artifacts.",
            ["placement plan", "tiling plan", "memory plan", "unsupported operators"],
            "Set ANALOG_AI_COMPILER_API_URL for a compiler service, or connect TVM, MLIR, IREE, or a custom hardware compiler behind this normalized interface.",
            [f"ANALOG_AI_COMPILER_API_URL configured: {compiler_api_configured}", f"tvm available: {tvm_available}", f"iree available: {iree_available}"],
        ),
        _adapter(
            "compiler.analog-mlir-golem",
            "analog-mlir to SST/Golem compiler bridge",
            "compiler",
            "configured" if analog_mlir_configured else "not connected",
            "environment check",
            "medium" if analog_mlir_configured else "low",
            "Lower supported tensor/linalg graph regions into analog execution IR, isolate static weights, build task graphs, and emit a runtime graph for Golem/SST co-simulation.",
            ["analog/digital task graph", "weight isolation plan", "runtime graph", "custom instruction or dispatch plan"],
            "Set ANALOG_AI_ANALOG_MLIR_API_URL for an analog-mlir service and import its compiler-placement artifact before using compiler-fit claims.",
            [f"ANALOG_AI_ANALOG_MLIR_API_URL configured: {analog_mlir_configured}"],
        ),
        _adapter(
            "analog.error-simulator",
            "Analog error simulator",
            "analog simulation",
            "configured" if analog_sim_configured else "not connected",
            "environment check plus local estimate",
            "medium" if analog_sim_configured else "low",
            "Model analog numeric error from device variation, ADC/DAC behavior, temperature, voltage, and calibration settings.",
            ["error model", "variation sensitivity", "expected accuracy impact", "confidence level"],
            "Set ANALOG_AI_ERROR_SIM_URL for an analog simulation service, or connect SPICE, memory-cell variation models, or a calibrated behavioral simulator.",
            [f"ANALOG_AI_ERROR_SIM_URL configured: {analog_sim_configured}"],
        ),
        _adapter(
            "sim.aihwkit",
            "IBM AIHWKIT hardware-aware simulator",
            "analog simulation",
            "configured" if aihwkit_configured else "available dependency" if aihwkit_available else "not connected",
            "environment check plus dependency check",
            "medium" if aihwkit_configured or aihwkit_available else "low",
            "Run PyTorch-based AIMC hardware-aware simulation for DAC/ADC precision, programming noise, conductance drift, IR drop, and write/update non-idealities.",
            ["analog error report", "device noise settings", "drift settings", "IR-drop parameters", "post-mapping accuracy impact"],
            "Run the local AIHWKIT adapter when the package is available, or set ANALOG_AI_AIHWKIT_API_URL for a stronger model-level simulation service.",
            [f"ANALOG_AI_AIHWKIT_API_URL configured: {aihwkit_configured}", f"aihwkit package available: {aihwkit_available}"],
        ),
        _adapter(
            "sim.crosssim",
            "Sandia CrossSim crossbar simulator",
            "analog simulation",
            "configured" if crosssim_configured else "available dependency" if crosssim_available else "not connected",
            "environment check plus dependency check",
            "medium" if crosssim_configured or crosssim_available else "low",
            "Run GPU-accelerated crossbar accuracy simulation for bit slicing, programming errors, read noise, parasitic wire resistance, ADC ranges, and algorithm-level accuracy impact.",
            ["analog error report", "crossbar array settings", "wire parasitic settings", "ADC configuration", "task accuracy impact"],
            "Run the local CrossSim adapter when the package is available, or set ANALOG_AI_CROSSSIM_API_URL for a stronger model-level simulation service.",
            [f"ANALOG_AI_CROSSSIM_API_URL configured: {crosssim_configured}", f"crosssim package available: {crosssim_available}"],
        ),
        _adapter(
            "system.sst-golem",
            "SST/Golem cycle co-simulation",
            "hardware",
            "configured" if sst_golem_configured else "not connected",
            "environment check",
            "medium" if sst_golem_configured else "low",
            "Run cycle/system-level co-simulation of analog array execution with CPU dispatch, custom instructions, RoCC-style handoff, synchronization, memory movement, and CrossSim-backed non-idealities.",
            ["runtime trace", "cycle count", "dispatch overhead", "memory bottlenecks", "synchronization behavior"],
            "Set ANALOG_AI_SST_GOLEM_API_URL and connect the runtime output to the board-runtime evidence contract.",
            [f"ANALOG_AI_SST_GOLEM_API_URL configured: {sst_golem_configured}"],
        ),
        _adapter(
            "system.alpine-gem5x",
            "ALPINE/gem5-X full-system simulator",
            "hardware",
            "configured" if alpine_configured else "not connected",
            "environment check",
            "medium" if alpine_configured else "low",
            "Run full-system AIMC simulation with CPU integration, custom ISA/library dispatch, memory hierarchy effects, Linux/runtime overhead, and end-to-end model execution.",
            ["runtime trace", "CPU overhead", "memory hierarchy effects", "custom ISA dispatch", "system bottlenecks"],
            "Set ANALOG_AI_ALPINE_GEM5X_API_URL and normalize full-system output into board-runtime evidence.",
            [f"ANALOG_AI_ALPINE_GEM5X_API_URL configured: {alpine_configured}"],
        ),
        _adapter(
            "compiler.attention-partitioner",
            "Transformer attention partitioner",
            "compiler",
            "configured" if attention_partition_configured else "not connected",
            "environment check",
            "medium" if attention_partition_configured else "low",
            "Partition transformer workloads into static weight-stationary projections, dynamic attention/Softmax digital work, analog pruning candidates, and unsupported update-heavy regions.",
            ["attention partition plan", "static projection mapping", "digital softmax boundary", "dynamic activation matmul boundary", "rewrite candidates"],
            "Set ANALOG_AI_ATTENTION_PARTITION_API_URL or implement a local pass that emits compiler-placement evidence for transformer/VLA workloads.",
            [f"ANALOG_AI_ATTENTION_PARTITION_API_URL configured: {attention_partition_configured}"],
        ),
        _adapter(
            "accuracy.local-task-check",
            "Local task accuracy estimator",
            "accuracy",
            "configured" if accuracy_api_configured else "available",
            "environment check, local synthetic estimate, or dataset file",
            "medium",
            "Generate a normalized task-accuracy artifact from a configured metric service, a local dataset file, or quantization and analog-error estimates for workflow testing.",
            ["dataset-backed task metric", "baseline metric", "candidate metric", "tolerance check"],
            "Set ANALOG_AI_ACCURACY_API_URL for a metric service, or pass dataset_path to run a local dataset-backed evaluation.",
            [f"ANALOG_AI_ACCURACY_API_URL configured: {accuracy_api_configured}"],
        ),
        _adapter(
            "board.runtime",
            "Board runtime adapter",
            "hardware",
            "configured" if board_api_configured or replay_enabled else "available",
            "environment check, replay fixture, plus local simulator",
            "medium" if board_api_configured or replay_enabled else "low",
            "Run prepared models on a board or prototype chip and collect traces; locally, generate a simulated runtime trace for evidence-flow testing.",
            ["measured latency", "runtime trace", "fallback trace", "board status"],
            "Use local simulation now; set ANALOG_AI_REPLAY_FIXTURE_MODE=1 for connector replay, or set ANALOG_AI_BOARD_API_URL when a board runtime service exists.",
            [f"ANALOG_AI_BOARD_API_URL configured: {board_api_configured}", f"replay fixture mode enabled: {replay_enabled}"],
        ),
        _adapter(
            "metrics.power-thermal",
            "Power and thermal metrics adapter",
            "measurement",
            "configured" if power_meter_configured or replay_enabled else "available",
            "environment check, replay fixture, plus local simulator",
            "medium" if power_meter_configured or replay_enabled else "low",
            "Attach measured energy, power, temperature, and thermal behavior to runtime reports; locally, generate a simulated power and thermal report for evidence-flow testing.",
            ["measured energy", "power trace", "temperature trace", "thermal warnings"],
            "Use local simulation now; set ANALOG_AI_REPLAY_FIXTURE_MODE=1 for connector replay, or set ANALOG_AI_POWER_METER_URL when a lab measurement service exists.",
            [f"ANALOG_AI_POWER_METER_URL configured: {power_meter_configured}", f"replay fixture mode enabled: {replay_enabled}"],
        ),
    ]
    summary = {
        "available": sum(1 for item in adapters if item["status"] == "available"),
        "configured": sum(1 for item in adapters if item["status"] == "configured"),
        "not_connected": sum(1 for item in adapters if item["status"] == "not connected"),
        "missing_dependency": sum(1 for item in adapters if item["status"] == "missing dependency"),
    }
    return {
        "result_type": "adapter_registry",
        "schema_version": ADAPTER_SCHEMA_VERSION,
        "provenance": "local backend inspection",
        "confidence": "medium",
        "summary": summary,
        "adapters": adapters,
    }


def _registered_adapters_by_id():
    return {item["id"]: item for item in adapter_registry()["adapters"]}


def _dependency_probe(package_name):
    available = _python_package_available(package_name)
    return {
        "name": f"python package: {package_name}",
        "status": "passed" if available else "missing",
        "detail": f"{package_name} import discovery {'succeeded' if available else 'failed'}",
    }


def _env_probe(name):
    value = _env_value(name)
    return {
        "name": f"environment variable: {name}",
        "status": "passed" if value else "missing",
        "detail": "configured" if value else "not configured",
    }


def _skipped_env_probe(name, reason):
    return {
        "name": f"environment variable: {name}",
        "status": "skipped",
        "detail": reason,
    }


def _http_health_probe(name, base_url):
    if not base_url:
        return {
            "name": name,
            "status": "skipped",
            "detail": "No URL configured.",
        }
    health_url = base_url.rstrip("/") + "/health"
    request = Request(health_url, method="GET")
    try:
        with urlopen(request, timeout=2) as response:
            return {
                "name": name,
                "status": "passed" if 200 <= response.status < 500 else "failed",
                "detail": f"GET {health_url} returned HTTP {response.status}",
            }
    except URLError as exc:
        return {
            "name": name,
            "status": "failed",
            "detail": f"GET {health_url} failed: {exc.reason}",
        }
    except Exception as exc:
        return {
            "name": name,
            "status": "failed",
            "detail": f"GET {health_url} failed: {exc}",
        }


def _artifact_contract(source_id, artifact_name, minimum_fields, claim_use):
    return {
        "source_id": source_id,
        "artifact_name": artifact_name,
        "minimum_fields": minimum_fields,
        "claim_use": claim_use,
        "rule": "The frontend may show this as evidence only after the backend imports a normalized artifact with provenance, target settings, metrics, and confidence.",
    }


def adapter_probe(adapter_id):
    adapters = _registered_adapters_by_id()
    adapter = adapters.get(adapter_id)
    if not adapter:
        return None

    checks = []
    contract = None
    sample_output = None

    if adapter_id == "model-import.onnx":
        checks.append(_dependency_probe("onnx"))
        sample_output = {
            "result_type": "model_import_probe",
            "outputs": ["graph nodes", "operator histogram", "shape summary", "parameter estimate"],
            "provenance": "local dependency check",
            "confidence": "medium" if checks[0]["status"] == "passed" else "low",
        }
    elif adapter_id == "quantization.onnxruntime":
        checks.append(_dependency_probe("onnxruntime"))
        contract = _artifact_contract(
            "task_accuracy",
            "task-accuracy-report.json",
            ["dataset_id", "metric_name", "baseline_metric", "candidate_metric", "tolerance", "pass"],
            "Supports task accuracy discussion only for the dataset and metric in the artifact.",
        )
    elif adapter_id == "compiler.tvm-mlir-iree":
        compiler_url = _env_value("ANALOG_AI_COMPILER_API_URL")
        if compiler_url:
            checks.append(_env_probe("ANALOG_AI_COMPILER_API_URL"))
            checks.append(_http_health_probe("compiler service health", compiler_url))
        else:
            checks.extend([_dependency_probe("tvm"), _dependency_probe("iree")])
        contract = _artifact_contract(
            "compiler_mapping",
            "compiler-placement.json",
            ["operator_placements", "tiling_plan", "memory_plan", "unsupported_operators", "provenance"],
            "Supports placement discussion; it does not prove latency, energy, or accuracy.",
        )
    elif adapter_id == "compiler.analog-mlir-golem":
        analog_mlir_url = _env_value("ANALOG_AI_ANALOG_MLIR_API_URL")
        checks.append(_env_probe("ANALOG_AI_ANALOG_MLIR_API_URL"))
        checks.append(_http_health_probe("analog-mlir service health", analog_mlir_url))
        contract = _artifact_contract(
            "compiler_mapping",
            "compiler-placement.json",
            ["operator_placements", "tiling_plan", "memory_plan", "unsupported_operators", "provenance"],
            "Supports analog/digital placement, weight isolation, and runtime graph discussion; it does not prove measured latency or accuracy.",
        )
    elif adapter_id == "analog.error-simulator":
        analog_url = _env_value("ANALOG_AI_ERROR_SIM_URL")
        checks.append({
            "name": "local analog error estimate",
            "status": "passed",
            "detail": "Local calibration-profile estimate is available.",
        })
        if analog_url:
            checks.append(_env_probe("ANALOG_AI_ERROR_SIM_URL"))
            checks.append(_http_health_probe("analog simulator health", analog_url))
        contract = _artifact_contract(
            "analog_error_simulation",
            "analog-error-simulation.json",
            ["error_model", "temperature_range", "voltage_range", "accuracy_impact", "calibration_profile"],
            "Supports analog numeric-behavior discussion when paired with task accuracy evidence.",
        )
    elif adapter_id == "sim.aihwkit":
        aihwkit_url = _env_value("ANALOG_AI_AIHWKIT_API_URL")
        checks.append(_dependency_probe("aihwkit"))
        if aihwkit_url:
            checks.append(_env_probe("ANALOG_AI_AIHWKIT_API_URL"))
            checks.append(_http_health_probe("AIHWKIT service health", aihwkit_url))
        contract = _artifact_contract(
            "analog_error_simulation",
            "analog-error-simulation.json",
            ["error_model", "temperature_range", "voltage_range", "accuracy_impact", "calibration_profile"],
            "Supports hardware-aware analog error and drift discussion when paired with task accuracy evidence.",
        )
    elif adapter_id == "sim.crosssim":
        crosssim_url = _env_value("ANALOG_AI_CROSSSIM_API_URL")
        checks.append({
            "name": "python package: simulator or cross_sim",
            "status": "passed" if _python_package_available("simulator") or _python_package_available("cross_sim") else "missing",
            "detail": "CrossSim import discovery checked common local module names.",
        })
        if crosssim_url:
            checks.append(_env_probe("ANALOG_AI_CROSSSIM_API_URL"))
            checks.append(_http_health_probe("CrossSim service health", crosssim_url))
        contract = _artifact_contract(
            "analog_error_simulation",
            "analog-error-simulation.json",
            ["error_model", "temperature_range", "voltage_range", "accuracy_impact", "calibration_profile"],
            "Supports crossbar parasitic, ADC, bit-slicing, and programming-error discussion when paired with task accuracy evidence.",
        )
    elif adapter_id == "system.sst-golem":
        sst_url = _env_value("ANALOG_AI_SST_GOLEM_API_URL")
        checks.append(_env_probe("ANALOG_AI_SST_GOLEM_API_URL"))
        checks.append(_http_health_probe("SST/Golem service health", sst_url))
        contract = _artifact_contract(
            "board_runtime",
            "board-runtime-trace.json",
            ["board_id", "runtime_version", "latency_ms", "trace", "fallback_events", "provenance"],
            "Supports simulated cycle/runtime discussion for a specific compiled runtime graph; it is not measured board evidence.",
        )
    elif adapter_id == "system.alpine-gem5x":
        alpine_url = _env_value("ANALOG_AI_ALPINE_GEM5X_API_URL")
        checks.append(_env_probe("ANALOG_AI_ALPINE_GEM5X_API_URL"))
        checks.append(_http_health_probe("ALPINE/gem5-X service health", alpine_url))
        contract = _artifact_contract(
            "board_runtime",
            "board-runtime-trace.json",
            ["board_id", "runtime_version", "latency_ms", "trace", "fallback_events", "provenance"],
            "Supports full-system simulated runtime discussion; it is not measured board evidence.",
        )
    elif adapter_id == "compiler.attention-partitioner":
        attention_url = _env_value("ANALOG_AI_ATTENTION_PARTITION_API_URL")
        checks.append(_env_probe("ANALOG_AI_ATTENTION_PARTITION_API_URL"))
        checks.append(_http_health_probe("attention partitioner health", attention_url))
        contract = _artifact_contract(
            "compiler_mapping",
            "compiler-placement.json",
            ["operator_placements", "tiling_plan", "memory_plan", "unsupported_operators", "provenance"],
            "Supports transformer partitioning discussion; latency, energy, and task accuracy still need separate evidence.",
        )
    elif adapter_id == "accuracy.local-task-check":
        accuracy_url = _env_value("ANALOG_AI_ACCURACY_API_URL")
        checks.append({
            "name": "local task metric estimate",
            "status": "passed",
            "detail": "Local dataset-backed task-accuracy generation is available when dataset_path is provided; synthetic generation remains available for workflow testing.",
        })
        if accuracy_url:
            checks.append(_env_probe("ANALOG_AI_ACCURACY_API_URL"))
            checks.append(_http_health_probe("accuracy service health", accuracy_url))
        contract = _artifact_contract(
            "task_accuracy",
            "task-accuracy-report.json",
            ["dataset_id", "metric_name", "baseline_metric", "candidate_metric", "tolerance", "pass"],
            "Supports task-accuracy flow testing; replace with real dataset evidence before customer claims.",
        )
    elif adapter_id == "board.runtime":
        board_url = _env_value("ANALOG_AI_BOARD_API_URL")
        checks.append({
            "name": "local board runtime simulation",
            "status": "passed",
            "detail": "Local runtime trace generation is available. Real board service is optional.",
        })
        if replay_fixture_enabled():
            checks.append(_skipped_env_probe("ANALOG_AI_BOARD_API_URL", "not required because replay fixture mode is enabled"))
            checks.append(replay_fixture_probe())
        else:
            checks.append(_env_probe("ANALOG_AI_BOARD_API_URL"))
            checks.append(_http_health_probe("board runtime health", board_url))
        contract = _artifact_contract(
            "board_runtime",
            "board-runtime-trace.json",
            ["board_id", "runtime_version", "latency_ms", "trace", "fallback_events", "provenance"],
            "Supports measured latency discussion for the exact board, runtime, model, and settings.",
        )
    elif adapter_id == "metrics.power-thermal":
        meter_url = _env_value("ANALOG_AI_POWER_METER_URL")
        checks.append({
            "name": "local power and thermal simulation",
            "status": "passed",
            "detail": "Local power/thermal report generation is available. Real meter service is optional.",
        })
        if replay_fixture_enabled():
            checks.append(_skipped_env_probe("ANALOG_AI_POWER_METER_URL", "not required because replay fixture mode is enabled"))
            checks.append(replay_fixture_probe())
        else:
            checks.append(_env_probe("ANALOG_AI_POWER_METER_URL"))
            checks.append(_http_health_probe("power meter health", meter_url))
        contract = _artifact_contract(
            "power_thermal",
            "power-thermal-report.json",
            ["energy_uj", "power_trace", "temperature_trace", "sampling_rate", "measurement_setup"],
            "Supports measured energy or thermal discussion only when paired with a matching runtime trace.",
        )
    else:
        checks.append({
            "name": "local adapter",
            "status": "passed" if adapter["status"] == "available" else "skipped",
            "detail": adapter["next_step"],
        })

    passed = sum(1 for item in checks if item["status"] == "passed")
    failed = sum(1 for item in checks if item["status"] == "failed")
    missing = sum(1 for item in checks if item["status"] == "missing")
    status = "ready" if checks and passed > 0 and not failed and not missing else "blocked" if failed or missing else "informational"

    return {
        "result_type": "adapter_probe",
        "schema_version": ADAPTER_PROBE_SCHEMA_VERSION,
        "adapter": adapter,
        "status": status,
        "summary": {
            "checks": len(checks),
            "passed": passed,
            "failed": failed,
            "missing": missing,
        },
        "checks": checks,
        "normalized_artifact_contract": contract,
        "sample_output": sample_output,
        "next_step": adapter["next_step"],
    }
