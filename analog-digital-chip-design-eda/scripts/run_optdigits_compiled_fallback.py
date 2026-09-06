#!/usr/bin/env python3
"""Lower the real workload through the shared compiler and execute SRAM fallback."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import numpy as np
import onnx
from onnx import numpy_helper
from onnx.reference import ReferenceEvaluator

from compile_hybrid_transformer_execution_package import main as compile_package
from run_target_bytecode_reference import main as verify_encoding, decode

ROOT = Path(__file__).resolve().parents[1]
PHYSICAL = ROOT / "evidence/aimc-simulator-adapters/isolated-latch-v2-transient/20260906T195143370541Z/result.json"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prepared_run", type=Path)
    args = parser.parse_args()
    run = args.prepared_run.resolve()
    manifest = json.loads((run / "result.json").read_text())
    for filename, expected_hash in {"model.onnx": manifest["model_sha256"], "contract.json": manifest["contract_sha256"], "split.json": manifest["split_sha256"], "optdigits.tra": manifest["dataset_sha256"]["optdigits.tra"]}.items():
        if hashlib.sha256((run / filename).read_bytes()).hexdigest() != expected_hash:
            raise ValueError(f"Input hash mismatch: {filename}")
    output = ROOT / "evidence/aimc-hardware-lab/optdigits-compiled-fallback" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    output.mkdir(parents=True, exist_ok=False)
    physical = json.loads(PHYSICAL.read_text())
    gate = {"analog_execution_allowed": False, "source": str(PHYSICAL.relative_to(ROOT)),
            "source_sha256": hashlib.sha256(PHYSICAL.read_bytes()).hexdigest(),
            "measured_cases": sum(row.get("measured", False) for row in physical["rows"]),
            "passing_cases": sum(row.get("pass", False) for row in physical["rows"]),
            "reason": "Extracted latch polarity/voltage failures; no qualified converter/array operating profile"}
    model = onnx.load(run / "model.onnx")
    nodes = list(model.graph.node)
    if [node.op_type for node in nodes] != ["MatMul", "Add", "Relu", "MatMul", "Add"]:
        raise ValueError("Frozen workload graph changed")
    weights = {value.name: numpy_helper.to_array(value) for value in model.graph.initializer}
    dimensions = [(64, 32), (32, 32), (32, 32), (32, 10), (10, 10)]
    rows = [{"operator_id": node.name or f"{node.op_type}.{i}", "operator": node.op_type,
             "activation_shape": [1, sizes[0]], "output_shape": [1, sizes[1]],
             "analog_candidate": i == 0, "placement": "digital_support",
             "reason": gate["reason"] if i == 0 else "Contract requires exact digital support/output",
             "onnx_node_index": i, "onnx_inputs": list(node.input), "onnx_outputs": list(node.output)}
            for i, (node, sizes) in enumerate(zip(nodes, dimensions))]
    plan_path = output / "execution_plan.json"
    plan_path.write_text(json.dumps({"operator_placements": rows, "physical_gate": gate,
                                   "model_sha256": manifest["model_sha256"]}, indent=2) + "\n")
    source = {"target_package_id": "optdigits_compiled_fallback_v1", "physical_gate_status": "blocked_extracted_latch_polarity_voltage",
              "models": [{"model_id": "optdigits-mlp-64-32-10-v1", "operator_count": len(rows),
                           "source_plan": str(plan_path.relative_to(ROOT))}]}
    source_path = output / "compiler_source.json"
    source_path.write_text(json.dumps(source, indent=2) + "\n")
    compile_package(source_path, output)
    if verify_encoding(output):
        raise ValueError("Shared review bytecode verification failed")
    commands = json.loads((output / "runtime_commands.json").read_text())["commands"]
    compiled = json.loads((output / "compiled_target_execution_package.json").read_text())
    allocations = compiled["sram_memory_maps"][0]["allocations"]
    if len(commands) != len(nodes) or len(allocations) != len(nodes):
        raise ValueError("Compiler did not cover every model operator exactly once")
    raw = np.loadtxt(run / "optdigits.tra", delimiter=",")
    split = json.loads((run / "split.json").read_text())
    calibration = split["calibration"]
    x = (raw[calibration, :64] / 16).astype(np.float32)
    expected = ReferenceEvaluator(model).run(None, {"input": x})[0]
    outputs, trace = [], []
    for sample_index, sample in enumerate(x):
        memory = bytearray(compiled["sram_memory_maps"][0]["sram_bytes_used"])
        current = sample.reshape(1, 64)
        for index, (command, node, allocation) in enumerate(zip(commands, nodes, allocations)):
            decoded = decode(command["encoding"])
            if decoded["command"] != "RUN_DIGITAL_SUPPORT" or decoded["operator_index"] != index:
                raise ValueError("Unexpected/unauthorized instruction")
            offset = decoded["activation_offset_bytes"]
            if current.nbytes > allocation["activation_size_bytes"] or offset != allocation["activation_offset_bytes"]:
                raise ValueError("Activation SRAM overflow or address mismatch")
            memory[offset:offset + current.nbytes] = current.tobytes()
            a = np.frombuffer(memory, dtype=np.float32, count=current.size, offset=offset).reshape(current.shape)
            if node.op_type == "MatMul":
                value = a @ weights[node.input[1]]
            elif node.op_type == "Add":
                value = a + weights[node.input[1]]
            elif node.op_type == "Relu":
                value = np.maximum(a, 0)
            else:
                raise ValueError("Unsupported operation")
            partial = allocation["partial_sum_offset_bytes"]
            if value.nbytes > allocation["partial_sum_size_bytes"]:
                raise ValueError("Output SRAM overflow")
            memory[partial:partial + value.nbytes] = value.tobytes()
            current = np.frombuffer(memory, dtype=np.float32, count=value.size, offset=partial).reshape(value.shape).copy()
            if sample_index == 0:
                trace.append({"command": command["sequence"], "operator": rows[index]["operator_id"],
                              "input_bytes": a.nbytes, "output_bytes": value.nbytes, "input_offset": offset,
                              "output_offset": partial, "route": "digital_fallback" if index == 0 else "digital_support"})
        outputs.append(current[0])
    actual = np.asarray(outputs)
    np.testing.assert_allclose(actual, expected, rtol=1e-4, atol=1e-4)
    if not np.array_equal(actual.argmax(axis=1), expected.argmax(axis=1)):
        raise ValueError("Compiled fallback changed classification")
    report = {"status": "compiled_software_fallback_pass", "model_sha256": manifest["model_sha256"],
              "prepared_run": str(run), "contract_sha256": manifest["contract_sha256"],
              "split_sha256": manifest["split_sha256"],
              "source_sha256": {name: hashlib.sha256((ROOT / "scripts" / name).read_bytes()).hexdigest()
                                for name in (Path(__file__).name, "compile_hybrid_transformer_execution_package.py",
                                             "run_target_bytecode_reference.py")},
              "package_sha256": {name: hashlib.sha256((output / name).read_bytes()).hexdigest()
                                 for name in ("execution_plan.json", "compiler_source.json", "runtime_commands.json",
                                              "compiled_target_execution_package.json")},
              "physical_gate": gate, "samples": len(x), "commands_per_sample": len(commands),
              "sram_bytes": len(memory), "calibration_accuracy": float(np.mean(actual.argmax(axis=1) == raw[calibration, 64])),
              "max_logit_difference": float(np.max(np.abs(actual - expected))), "first_sample_trace": trace,
              "fallback_fraction": 1.0, "test_evaluated": False,
              "boundary": "Actual software execution of shared review commands and SRAM offsets; weights reside in host memory. No firmware, physical analog execution or measured hardware cost."}
    (output / "execution_result.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({key: value for key, value in report.items() if key != "first_sample_trace"}, indent=2))
    print(output)


if __name__ == "__main__":
    main()
