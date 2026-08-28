import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


EXTERNAL_SERVICE_ADAPTER_SCHEMA_VERSION = "external-service-adapter-v0.1"


SERVICE_ENV_BY_ADAPTER = {
    "compiler.tvm-mlir-iree": "ANALOG_AI_COMPILER_API_URL",
    "analog.error-simulator": "ANALOG_AI_ERROR_SIM_URL",
    "accuracy.local-task-check": "ANALOG_AI_ACCURACY_API_URL",
    "board.runtime": "ANALOG_AI_BOARD_API_URL",
    "metrics.power-thermal": "ANALOG_AI_POWER_METER_URL",
}


class ExternalAdapterError(RuntimeError):
    def __init__(self, message, artifact_paths=None):
        super().__init__(message)
        self.artifact_paths = artifact_paths or {}


def external_service_url(adapter_id):
    env_name = SERVICE_ENV_BY_ADAPTER.get(adapter_id)
    if not env_name:
        return None
    return os.environ.get(env_name, "").strip() or None


def _json_dumps(payload):
    return json.dumps(payload, indent=2, sort_keys=True)


def _post_json(url, payload, timeout_seconds=30):
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            body = response.read().decode("utf-8")
            return response.status, json.loads(body) if body else {}
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise ExternalAdapterError(f"HTTP {exc.code} from {url}: {detail}") from exc
    except URLError as exc:
        raise ExternalAdapterError(f"Could not reach {url}: {exc.reason}") from exc
    except json.JSONDecodeError as exc:
        raise ExternalAdapterError(f"External service returned non-JSON response from {url}.") from exc


def _direct_payload_fields(source_id):
    if source_id == "compiler_mapping":
        return {"operator_placements", "tiling_plan", "memory_plan", "unsupported_operators", "provenance"}
    if source_id == "analog_error_simulation":
        return {"error_model", "temperature_range", "voltage_range", "accuracy_impact", "calibration_profile"}
    if source_id == "board_runtime":
        return {"board_id", "runtime_version", "latency_ms", "trace", "fallback_events", "provenance"}
    if source_id == "power_thermal":
        return {"energy_uj", "power_trace", "temperature_trace", "sampling_rate", "measurement_setup"}
    if source_id == "task_accuracy":
        return {"dataset_id", "metric_name", "baseline_metric", "candidate_metric", "tolerance", "pass"}
    return set()


def _normalized_payload(response_payload, source_id):
    if not isinstance(response_payload, dict):
        raise ExternalAdapterError("External service response must be a JSON object.")
    payload = response_payload.get("normalized_evidence_payload")
    if payload is None:
        payload = response_payload.get("payload")
    if payload is None:
        direct_fields = _direct_payload_fields(source_id)
        if direct_fields and direct_fields.intersection(response_payload):
            payload = response_payload
    if not isinstance(payload, dict):
        raise ExternalAdapterError("External service response did not contain a normalized evidence payload.")
    return payload


def call_external_service(
    adapter_id,
    source_id,
    artifact_name,
    request_payload,
    run_dir,
    timeout_seconds=30,
):
    base_url = external_service_url(adapter_id)
    if not base_url:
        return None
    run_dir.mkdir(parents=True, exist_ok=True)
    run_url = base_url.rstrip("/") + "/run"
    raw_request_path = run_dir / "external-service-request.json"
    raw_response_path = run_dir / "external-service-response.json"
    failure_path = run_dir / "external-service-failure.json"
    request_envelope = {
        "schema_version": EXTERNAL_SERVICE_ADAPTER_SCHEMA_VERSION,
        "adapter_id": adapter_id,
        "source_id": source_id,
        "artifact_name": artifact_name,
        "request": request_payload,
    }
    raw_request_path.write_text(_json_dumps(request_envelope), encoding="utf-8")
    try:
        status_code, response_payload = _post_json(run_url, request_envelope, timeout_seconds=timeout_seconds)
    except ExternalAdapterError as exc:
        failure_envelope = {
            "schema_version": EXTERNAL_SERVICE_ADAPTER_SCHEMA_VERSION,
            "adapter_id": adapter_id,
            "source_id": source_id,
            "artifact_name": artifact_name,
            "service_url": base_url,
            "run_url": run_url,
            "error_type": type(exc.__cause__).__name__ if exc.__cause__ else type(exc).__name__,
            "error": str(exc),
            "request_artifact": str(raw_request_path),
            "next_step": "Fix the configured service or normalized evidence contract, then rerun this adapter. Local fallback is intentionally not used when an external service is configured.",
        }
        failure_path.write_text(_json_dumps(failure_envelope), encoding="utf-8")
        exc.artifact_paths = {
            "raw_request_path": str(raw_request_path),
            "failure_path": str(failure_path),
        }
        raise
    raw_response_path.write_text(_json_dumps({
        "schema_version": EXTERNAL_SERVICE_ADAPTER_SCHEMA_VERSION,
        "adapter_id": adapter_id,
        "source_id": source_id,
        "artifact_name": artifact_name,
        "status_code": status_code,
        "response": response_payload,
    }), encoding="utf-8")
    try:
        payload = _normalized_payload(response_payload, source_id)
    except ExternalAdapterError as exc:
        failure_envelope = {
            "schema_version": EXTERNAL_SERVICE_ADAPTER_SCHEMA_VERSION,
            "adapter_id": adapter_id,
            "source_id": source_id,
            "artifact_name": artifact_name,
            "service_url": base_url,
            "run_url": run_url,
            "status_code": status_code,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "request_artifact": str(raw_request_path),
            "response_artifact": str(raw_response_path),
            "next_step": "Fix the configured service or normalized evidence contract, then rerun this adapter. Local fallback is intentionally not used when an external service is configured.",
        }
        failure_path.write_text(_json_dumps(failure_envelope), encoding="utf-8")
        exc.artifact_paths = {
            "raw_request_path": str(raw_request_path),
            "raw_response_path": str(raw_response_path),
            "failure_path": str(failure_path),
        }
        raise
    provenance = payload.setdefault("provenance", {})
    if isinstance(provenance, dict):
        provenance.setdefault("external_service_url", base_url)
        provenance.setdefault("external_service_adapter", True)
    return {
        "payload": payload,
        "raw_request_path": str(raw_request_path),
        "raw_response_path": str(raw_response_path),
        "status_code": status_code,
        "service_url": base_url,
        "response": response_payload,
    }
