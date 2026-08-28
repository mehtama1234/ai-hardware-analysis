#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import json
import os
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request


ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = Path(__file__).resolve().parents[1]
SAMPLE_MODEL = ROOT / "samples" / "tiny-mlp.onnx"
TARGET_PROFILE = "wearable"
CALIBRATION_PROFILE = "proto-audio-0237"
MODALITY = "audio_wake_word"
RUNTIME_MODE = "balanced"


def _free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _payload_for(source_id):
    if source_id == "compiler_mapping":
        return {
            "operator_placements": [
                {"layer_id": "dense1", "operator": "MatMul", "placement": "analog"},
                {"layer_id": "relu1", "operator": "Relu", "placement": "digital"},
            ],
            "tiling_plan": [{"layer_id": "dense1", "tile_shape": [16, 16]}],
            "memory_plan": {"weights": "analog_array", "activations": "sram", "outputs": "digital"},
            "unsupported_operators": [],
            "provenance": {"tool": "fake-compiler-service", "version": "0.1"},
        }
    if source_id == "analog_error_simulation":
        return {
            "error_model": {"model": "fake-variation-model", "adc_bits": 6, "dac_bits": 6},
            "temperature_range": {"min_c": 0, "max_c": 70},
            "voltage_range": {"min_v": 0.8, "max_v": 0.9},
            "accuracy_impact": {"metric_name": "wake_word_f1", "estimated_drop": 0.003, "pass": True},
            "calibration_profile": CALIBRATION_PROFILE,
            "provenance": {"tool": "fake-analog-service", "version": "0.1"},
        }
    if source_id == "task_accuracy":
        return {
            "dataset_id": "fake-wake-word-set",
            "metric_name": "wake_word_f1",
            "baseline_metric": 0.96,
            "candidate_metric": 0.955,
            "tolerance": 0.01,
            "pass": True,
            "record_count": 25,
            "provenance": {"tool": "fake-accuracy-service", "version": "0.1"},
        }
    if source_id == "board_runtime":
        return {
            "board_id": "fake-board-001",
            "runtime_version": "fake-runtime-0.1",
            "latency_ms": 1.25,
            "trace": [{"layer_id": "dense1", "placement": "analog", "latency_ms": 1.25}],
            "fallback_events": [],
            "provenance": {"tool": "fake-board-service", "version": "0.1", "runtime_mode": RUNTIME_MODE},
        }
    if source_id == "power_thermal":
        return {
            "energy_uj": 12.5,
            "power_trace": [{"time_ms": 0, "power_mw": 9.8}, {"time_ms": 1.25, "power_mw": 10.1}],
            "temperature_trace": [{"time_ms": 0, "temperature_c": 31.0}, {"time_ms": 1.25, "temperature_c": 31.2}],
            "sampling_rate": "fake 2 kHz",
            "measurement_setup": {
                "meter": "fake-power-meter",
                "supply_voltage": 0.82,
                "includes_host_overhead": True,
                "runtime_mode": RUNTIME_MODE,
            },
            "provenance": {"tool": "fake-power-service", "version": "0.1"},
        }
    raise KeyError(source_id)


class FakeConnectorHandler(BaseHTTPRequestHandler):
    compiler_call_count = 0

    def do_GET(self):
        if self.path != "/health":
            self.send_response(404)
            self.end_headers()
            return
        self._send_json({"status": "ok", "service": "fake-connector-service"})

    def do_POST(self):
        if self.path != "/run":
            self.send_response(404)
            self.end_headers()
            return
        length = int(self.headers.get("Content-Length", "0"))
        request = json.loads(self.rfile.read(length).decode("utf-8"))
        source_id = request.get("source_id")
        if source_id == "compiler_mapping":
            type(self).compiler_call_count += 1
        if source_id == "compiler_mapping" and type(self).compiler_call_count >= 2:
            self._send_json({"raw_output_references": ["fake-compiler-bad-contract"], "message": "missing normalized payload"})
            return
        payload = _payload_for(source_id)
        if source_id in {"compiler_mapping", "board_runtime"}:
            response = {"normalized_evidence_payload": payload, "raw_output_references": [f"fake-{source_id}-run"]}
        elif source_id in {"analog_error_simulation", "power_thermal"}:
            response = {"payload": payload, "raw_output_references": [f"fake-{source_id}-run"]}
        else:
            response = payload
        self._send_json(response)

    def _send_json(self, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_):
        pass


def request_json(base_url, path, method="GET", data=None):
    request = urllib.request.Request(base_url + path, data=data, method=method)
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {path} failed with HTTP {exc.code}: {detail}") from exc


def wait_for_backend(base_url, process):
    for _ in range(80):
        if process.poll() is not None:
            raise RuntimeError(f"Backend exited early with code {process.returncode}")
        try:
            health = request_json(base_url, "/health")
            if health.get("status") == "ok":
                return
        except Exception:
            time.sleep(0.25)
    raise RuntimeError("Timed out waiting for backend health.")


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    assert_true(SAMPLE_MODEL.exists(), f"Missing sample model: {SAMPLE_MODEL}")
    fake_server = HTTPServer(("127.0.0.1", 0), FakeConnectorHandler)
    fake_thread = threading.Thread(target=fake_server.serve_forever, daemon=True)
    fake_thread.start()
    fake_url = f"http://127.0.0.1:{fake_server.server_port}"
    backend_port = _free_port()
    backend_url = f"http://127.0.0.1:{backend_port}"
    env = {
        **os.environ,
        "ANALOG_AI_COMPILER_API_URL": fake_url,
        "ANALOG_AI_ERROR_SIM_URL": fake_url,
        "ANALOG_AI_ACCURACY_API_URL": fake_url,
        "ANALOG_AI_BOARD_API_URL": fake_url,
        "ANALOG_AI_POWER_METER_URL": fake_url,
    }
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", str(backend_port)],
        cwd=BACKEND_DIR,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        wait_for_backend(backend_url, process)
        imported = request_json(
            backend_url,
            f"/models/import?filename={SAMPLE_MODEL.name}&target_profile={TARGET_PROFILE}&calibration_profile={CALIBRATION_PROFILE}",
            method="POST",
            data=SAMPLE_MODEL.read_bytes(),
        )
        model_id = imported["model_id"]
        package = request_json(
            backend_url,
            f"/models/{urllib.parse.quote(model_id)}/deployment-package?target_profile={TARGET_PROFILE}&calibration_profile={CALIBRATION_PROFILE}&modality={MODALITY}&runtime_mode={RUNTIME_MODE}",
            method="POST",
            data=b"",
        )
        query = (
            f"?model_id={urllib.parse.quote(model_id)}"
            f"&target_profile={TARGET_PROFILE}"
            f"&calibration_profile={CALIBRATION_PROFILE}"
            f"&modality={MODALITY}"
            f"&runtime_mode={RUNTIME_MODE}"
        )
        expected = {
            "compiler.tvm-mlir-iree": ("compiler_mapping", "fake-compiler-service"),
            "analog.error-simulator": ("analog_error_simulation", "fake-analog-service"),
            "accuracy.local-task-check": ("task_accuracy", "fake-accuracy-service"),
            "board.runtime": ("board_runtime", "fake-board-service"),
            "metrics.power-thermal": ("power_thermal", "fake-power-service"),
        }
        results = {}
        for adapter_id, (source_id, tool) in expected.items():
            run = request_json(backend_url, f"/adapters/{adapter_id}/run{query}", method="POST", data=b"")
            payload = run.get("normalized_evidence_payload") or {}
            provenance = payload.get("provenance") or {}
            assert_true(run["status"] == "completed", f"{adapter_id} did not complete")
            assert_true(run["provenance"].startswith("configured external"), f"{adapter_id} did not use configured external path")
            assert_true(run["normalized_evidence_source_id"] == source_id, f"{adapter_id} source mismatch")
            assert_true(provenance.get("tool") == tool, f"{adapter_id} tool provenance mismatch")
            assert_true(provenance.get("external_service_adapter") is True, f"{adapter_id} missing external marker")
            artifact_names = {item["name"] for item in run.get("artifacts", [])}
            assert_true("external-service-request" in artifact_names, f"{adapter_id} missing raw request artifact")
            assert_true("external-service-response" in artifact_names, f"{adapter_id} missing raw response artifact")
            validation = request_json(
                backend_url,
                f"/evidence/validate?package_id={package['package_id']}&source_id={source_id}",
                method="POST",
                data=json.dumps(payload).encode("utf-8"),
            )
            assert_true(validation["valid"] is True, f"{adapter_id} external payload did not validate")
            results[adapter_id] = {"source_id": source_id, "tool": tool}
        bad_query = (
            f"?model_id={urllib.parse.quote(model_id)}"
            f"&target_profile={TARGET_PROFILE}"
            f"&calibration_profile={CALIBRATION_PROFILE}"
            f"&modality={MODALITY}"
            f"&runtime_mode={RUNTIME_MODE}"
        )
        failed_run = request_json(backend_url, f"/adapters/compiler.tvm-mlir-iree/run{bad_query}", method="POST", data=b"")
        failed_artifacts = {item["name"] for item in failed_run.get("artifacts", [])}
        assert_true(failed_run["status"] == "blocked", "bad compiler contract should block the adapter run")
        assert_true("external-service-request" in failed_artifacts, "bad compiler contract missing saved request artifact")
        assert_true("external-service-response" in failed_artifacts, "bad compiler contract missing saved response artifact")
        assert_true("external-service-failure" in failed_artifacts, "bad compiler contract missing saved failure artifact")
        print(json.dumps({
            "status": "external-smoke-ok",
            "package_id": package["package_id"],
            "backend_url": backend_url,
            "fake_service_url": fake_url,
            "adapters": results,
            "failure_path_checked": True,
        }, indent=2, sort_keys=True))
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
        fake_server.shutdown()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"external-smoke-failed {exc}", file=sys.stderr)
        raise
