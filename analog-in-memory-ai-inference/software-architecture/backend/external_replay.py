import json
import os


EXTERNAL_REPLAY_SCHEMA_VERSION = "external-replay-fixture-v0.1"
REPLAY_FIXTURE_ENV = "ANALOG_AI_REPLAY_FIXTURE_MODE"


def replay_fixture_enabled():
    return os.environ.get(REPLAY_FIXTURE_ENV, "").strip().lower() in {"1", "true", "yes", "on"}


def replay_fixture_probe():
    enabled = replay_fixture_enabled()
    return {
        "name": f"replay fixture mode: {REPLAY_FIXTURE_ENV}",
        "status": "passed" if enabled else "skipped",
        "detail": (
            "enabled; connector probes and runs can exercise raw request/response replay behavior"
            if enabled
            else "not enabled; set to 1 to exercise connector replay behavior without lab services"
        ),
    }


def replay_fixture_metadata(adapter_id, target_profile, calibration_profile, modality=None, runtime_mode=None):
    return {
        "schema_version": EXTERNAL_REPLAY_SCHEMA_VERSION,
        "enabled": replay_fixture_enabled(),
        "adapter_id": adapter_id,
        "target_profile": target_profile,
        "calibration_profile": calibration_profile,
        "modality": modality,
        "runtime_mode": runtime_mode,
        "replay_source": "local deterministic fixture generated from the normalized adapter contract",
        "not_measured_hardware": True,
        "plain_reading": (
            "Replay fixture mode mimics the shape of an external tool call. It stores raw request and raw response files "
            "beside the normalized artifact so the evidence path can be tested like a real connector. It is still not "
            "measured hardware, a real compiler run, or a lab instrument result."
        ),
    }


def write_replay_artifacts(run_dir, adapter_id, request_payload, normalized_payload, target_profile, calibration_profile, modality=None, runtime_mode=None):
    if not replay_fixture_enabled():
        return None
    metadata = replay_fixture_metadata(
        adapter_id,
        target_profile,
        calibration_profile,
        modality=modality,
        runtime_mode=runtime_mode,
    )
    raw_request_path = run_dir / "external-replay-request.json"
    raw_response_path = run_dir / "external-replay-response.json"
    raw_request_path.write_text(json.dumps({
        "metadata": metadata,
        "request": request_payload,
    }, indent=2, sort_keys=True), encoding="utf-8")
    raw_response_path.write_text(json.dumps({
        "metadata": metadata,
        "normalized_payload_preview": normalized_payload,
    }, indent=2, sort_keys=True), encoding="utf-8")
    return {
        **metadata,
        "raw_request_path": str(raw_request_path),
        "raw_response_path": str(raw_response_path),
    }
