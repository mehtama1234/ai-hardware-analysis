#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import numpy as np
import onnx
from onnx import TensorProto, helper, numpy_helper


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "deep-transformer-mlp-stack.onnx"
DIM = 32
HIDDEN = 64
BLOCKS = 3


def matrix(name: str, in_dim: int, out_dim: int, scale: float, phase: int) -> onnx.TensorProto:
    values = np.fromfunction(
        lambda row, col: np.sin((row + 1 + phase) * (col + 3)) * scale
        + np.cos((row + 4) * (col + 1 + phase)) * scale * 0.31,
        (in_dim, out_dim),
        dtype=float,
    ).astype(np.float32)
    return numpy_helper.from_array(values, name=name)


def bias(name: str, dim: int, scale: float, phase: int) -> onnx.TensorProto:
    values = np.array([(((idx + phase) % 7) - 3) * scale for idx in range(dim)], dtype=np.float32)
    return numpy_helper.from_array(values, name=name)


def main() -> int:
    nodes = []
    initializers = []
    current = "input"
    for block in range(BLOCKS):
        prefix = f"block{block}"
        gate_mm = f"{prefix}_gate_mm"
        gate_bias = f"{prefix}_gate_bias"
        gate_act = f"{prefix}_gate_act"
        up_mm = f"{prefix}_up_mm"
        up_bias = f"{prefix}_up_bias"
        up_act = f"{prefix}_up_act"
        mixed = f"{prefix}_mixed"
        down_mm = f"{prefix}_down_mm"
        down_bias = f"{prefix}_down_bias"
        residual = f"{prefix}_residual"
        out_mm = f"{prefix}_out_mm"
        out_bias = f"{prefix}_out_bias"
        output = f"{prefix}_output"
        nodes.extend(
            [
                helper.make_node("MatMul", [current, f"{prefix}_w_gate"], [gate_mm], name=f"{prefix}.gate.matmul"),
                helper.make_node("Add", [gate_mm, f"{prefix}_b_gate"], [gate_bias], name=f"{prefix}.gate.bias"),
                helper.make_node("Relu", [gate_bias], [gate_act], name=f"{prefix}.gate.relu"),
                helper.make_node("MatMul", [current, f"{prefix}_w_up"], [up_mm], name=f"{prefix}.up.matmul"),
                helper.make_node("Add", [up_mm, f"{prefix}_b_up"], [up_bias], name=f"{prefix}.up.bias"),
                helper.make_node("Relu", [up_bias], [up_act], name=f"{prefix}.up.relu"),
                helper.make_node("Mul", [gate_act, up_act], [mixed], name=f"{prefix}.elementwise.mix"),
                helper.make_node("MatMul", [mixed, f"{prefix}_w_down"], [down_mm], name=f"{prefix}.down.matmul"),
                helper.make_node("Add", [down_mm, f"{prefix}_b_down"], [down_bias], name=f"{prefix}.down.bias"),
                helper.make_node("Add", [current, down_bias], [residual], name=f"{prefix}.residual.add"),
                helper.make_node("MatMul", [residual, f"{prefix}_w_out"], [out_mm], name=f"{prefix}.out.matmul"),
                helper.make_node("Add", [out_mm, f"{prefix}_b_out"], [output], name=f"{prefix}.out.bias"),
            ]
        )
        phase = block * 11
        initializers.extend(
            [
                matrix(f"{prefix}_w_gate", DIM, HIDDEN, 0.055, phase),
                bias(f"{prefix}_b_gate", HIDDEN, 0.010, phase),
                matrix(f"{prefix}_w_up", DIM, HIDDEN, 0.052, phase + 1),
                bias(f"{prefix}_b_up", HIDDEN, 0.009, phase + 1),
                matrix(f"{prefix}_w_down", HIDDEN, DIM, 0.058, phase + 2),
                bias(f"{prefix}_b_down", DIM, 0.008, phase + 2),
                matrix(f"{prefix}_w_out", DIM, DIM, 0.047, phase + 3),
                bias(f"{prefix}_b_out", DIM, 0.007, phase + 3),
            ]
        )
        current = output
    graph = helper.make_graph(
        nodes,
        "deep_transformer_mlp_stack",
        [helper.make_tensor_value_info("input", TensorProto.FLOAT, [1, DIM])],
        [helper.make_tensor_value_info(current, TensorProto.FLOAT, [1, DIM])],
        initializers,
    )
    model = helper.make_model(graph, producer_name="analog-digital-chip-design-eda")
    onnx.checker.check_model(model)
    onnx.save(model, OUT)
    print(OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
