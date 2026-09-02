#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import numpy as np
import onnx
from onnx import TensorProto, helper, numpy_helper


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "projection-stack.onnx"


def matrix(name: str, in_dim: int, out_dim: int, scale: float) -> onnx.TensorProto:
    values = np.fromfunction(
        lambda row, col: np.sin((row + 1) * (col + 2)) * scale + np.cos((row + 3) + (col + 1)) * scale * 0.5,
        (in_dim, out_dim),
        dtype=float,
    ).astype(np.float32)
    return numpy_helper.from_array(values, name=name)


def bias(name: str, dim: int, scale: float) -> onnx.TensorProto:
    values = np.array([((idx % 3) - 1) * scale for idx in range(dim)], dtype=np.float32)
    return numpy_helper.from_array(values, name=name)


def main() -> int:
    nodes = [
        helper.make_node("MatMul", ["input", "w_q"], ["q_mm"], name="proj.q.matmul"),
        helper.make_node("Add", ["q_mm", "b_q"], ["q_add"], name="proj.q.bias"),
        helper.make_node("Relu", ["q_add"], ["q_relu"], name="proj.q.relu"),
        helper.make_node("MatMul", ["q_relu", "w_k"], ["k_mm"], name="proj.k.matmul"),
        helper.make_node("Add", ["k_mm", "b_k"], ["k_add"], name="proj.k.bias"),
        helper.make_node("Relu", ["k_add"], ["k_relu"], name="proj.k.relu"),
        helper.make_node("MatMul", ["k_relu", "w_v"], ["v_mm"], name="proj.v.matmul"),
        helper.make_node("Add", ["v_mm", "b_v"], ["v_add"], name="proj.v.bias"),
        helper.make_node("Relu", ["v_add"], ["v_relu"], name="proj.v.relu"),
        helper.make_node("MatMul", ["v_relu", "w_o"], ["o_mm"], name="proj.out.matmul"),
        helper.make_node("Add", ["o_mm", "b_o"], ["output"], name="proj.out.bias"),
    ]
    graph = helper.make_graph(
        nodes,
        "projection_stack",
        [helper.make_tensor_value_info("input", TensorProto.FLOAT, [1, 8])],
        [helper.make_tensor_value_info("output", TensorProto.FLOAT, [1, 8])],
        [
            matrix("w_q", 8, 16, 0.18),
            bias("b_q", 16, 0.03),
            matrix("w_k", 16, 16, 0.14),
            bias("b_k", 16, 0.025),
            matrix("w_v", 16, 12, 0.12),
            bias("b_v", 12, 0.02),
            matrix("w_o", 12, 8, 0.16),
            bias("b_o", 8, 0.015),
        ],
    )
    model = helper.make_model(graph, producer_name="analog-digital-chip-design-eda")
    onnx.checker.check_model(model)
    onnx.save(model, OUT)
    print(OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
