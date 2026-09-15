import json
from pathlib import Path

import pytest

from verification_platform.protocol import augment_protocol_plan, generate_protocol_sequence, load_protocol_plan


def _plan(tmp_path: Path) -> Path:
    path = tmp_path / "plan.json"
    path.write_text(json.dumps({
        "schema_version": "protocol-plan-v1", "name": "peripheral", "addr_width": 8, "data_width": 32,
        "steps": [
            {"operation": "write", "address": 4, "data": 1},
            {"operation": "read", "address": 4, "expected": 1},
        ],
    }), encoding="utf-8")
    return path


def test_protocol_plan_generates_handshake_safe_sequence(tmp_path):
    plan = load_protocol_plan(_plan(tmp_path))
    output = generate_protocol_sequence(plan)
    assert "while (!req_ready && timeout < 16)" in output
    assert "peripheral_sequence" in output
    assert plan.digest() in output
    assert "PROTOCOL_SEQUENCE_COVERAGE covered=%0d total=2" in output
    assert "PROTOCOL_SEQUENCE_RESULT status=passed" in output


def test_protocol_plan_rejects_invalid_operation(tmp_path):
    path = _plan(tmp_path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["steps"][0]["operation"] = "delay"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="unsupported protocol operation"):
        load_protocol_plan(path)


def test_protocol_plan_rejects_out_of_range_address(tmp_path):
    path = _plan(tmp_path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["steps"][0]["address"] = 256
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="address is out of range"):
        load_protocol_plan(path)


def test_protocol_gap_augmentation_is_deterministic_and_deduplicated(tmp_path):
    plan = load_protocol_plan(_plan(tmp_path))
    augmented = augment_protocol_plan(plan, [
        {"operation": "read", "address": 12, "expected": 0},
        {"operation": "read", "address": 8, "expected": 0},
        {"operation": "write", "address": 4, "data": 1},
    ])
    assert [(step.operation, step.address) for step in augmented.steps] == [
        ("write", 4), ("read", 4), ("read", 8), ("read", 12)
    ]
