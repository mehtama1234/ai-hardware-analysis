#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import numpy as np
import onnx
from onnx import TensorProto, helper, numpy_helper


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "transformer-mlp-block.onnx"


def matrix(name: str, in_dim: int, out_dim: int, scale: float) -> onnx.TensorProto:
    values = np.fromfunction(
        lambda row, col: np.sin((row + 1) * (col + 3)) * scale
        + np.cos((row + 4) * (col + 1)) * scale * 0.35,
        (in_dim, out_dim),
        dtype=float,
    ).astype(np.float32)
    return numpy_helper.from_array(values, name=name)


def bias(name: str, dim: int, scale: float) -> onnx.TensorProto:
    values = np.array([((idx % 5) - 2) * scale for idx in range(dim)], dtype=np.float32)
    return numpy_helper.from_array(values, name=name)


def main() -> int:
    nodes = [
        helper.make_node("MatMul", ["input", "w_gate"], ["gate_mm"], name="mlp.gate.matmul"),
        helper.make_node("Add", ["gate_mm", "b_gate"], ["gate_bias"], name="mlp.gate.bias"),
        helper.make_node("Relu", ["gate_bias"], ["gate_act"], name="mlp.gate.relu"),
        helper.make_node("MatMul", ["input", "w_up"], ["up_mm"], name="mlp.up.matmul"),
        helper.make_node("Add", ["up_mm", "b_up"], ["up_bias"], name="mlp.up.bias"),
        helper.make_node("Relu", ["up_bias"], ["up_act"], name="mlp.up.relu"),
        helper.make_node("Mul", ["gate_act", "up_act"], ["mixed"], name="mlp.elementwise.mix"),
        helper.make_node("MatMul", ["mixed", "w_down"], ["down_mm"], name="mlp.down.matmul"),
        helper.make_node("Add", ["down_mm", "b_down"], ["down_bias"], name="mlp.down.bias"),
        helper.make_node("Add", ["input", "down_bias"], ["residual_out"], name="mlp.residual.add"),
        helper.make_node("MatMul", ["residual_out", "w_out"], ["out_mm"], name="mlp.out.matmul"),
        helper.make_node("Add", ["out_mm", "b_out"], ["output"], name="mlp.out.bias"),
    ]
    graph = helper.make_graph(
        nodes,
        "transformer_mlp_block",
        [helper.make_tensor_value_info("input", TensorProto.FLOAT, [1, 16])],
        [helper.make_tensor_value_info("output", TensorProto.FLOAT, [1, 16])],
        [
            matrix("w_gate", 16, 32, 0.11),
            bias("b_gate", 32, 0.02),
            matrix("w_up", 16, 32, 0.10),
            bias("b_up", 32, 0.018),
            matrix("w_down", 32, 16, 0.12),
            bias("b_down", 16, 0.015),
            matrix("w_out", 16, 16, 0.09),
            bias("b_out", 16, 0.012),
        ],
    )
    model = helper.make_model(graph, producer_name="analog-digital-chip-design-eda")
    onnx.checker.check_model(model)
    onnx.save(model, OUT)
    print(OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
