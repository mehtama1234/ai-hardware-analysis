#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import numpy as np
import onnx
from onnx import TensorProto, helper, numpy_helper


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "attention-block.onnx"


def matrix(name: str, in_dim: int, out_dim: int, scale: float) -> onnx.TensorProto:
    values = np.fromfunction(
        lambda row, col: np.sin((row + 2) * (col + 1)) * scale + np.cos((row + 1) + (col + 4)) * scale * 0.35,
        (in_dim, out_dim),
        dtype=float,
    ).astype(np.float32)
    return numpy_helper.from_array(values, name=name)


def main() -> int:
    nodes = [
        helper.make_node("MatMul", ["input", "w_q"], ["q"], name="attn.q.matmul"),
        helper.make_node("MatMul", ["input", "w_k"], ["k"], name="attn.k.matmul"),
        helper.make_node("MatMul", ["input", "w_v"], ["v"], name="attn.v.matmul"),
        helper.make_node("Transpose", ["k"], ["k_t"], name="attn.k.transpose", perm=[1, 0]),
        helper.make_node("MatMul", ["q", "k_t"], ["scores_raw"], name="attn.scores.matmul"),
        helper.make_node("Div", ["scores_raw", "scale"], ["scores"], name="attn.scale"),
        helper.make_node("Softmax", ["scores"], ["weights"], name="attn.softmax", axis=1),
        helper.make_node("MatMul", ["weights", "v"], ["context"], name="attn.value.matmul"),
        helper.make_node("MatMul", ["context", "w_o"], ["output"], name="attn.out.matmul"),
    ]
    graph = helper.make_graph(
        nodes,
        "attention_block",
        [helper.make_tensor_value_info("input", TensorProto.FLOAT, [3, 8])],
        [helper.make_tensor_value_info("output", TensorProto.FLOAT, [3, 8])],
        [
            matrix("w_q", 8, 8, 0.16),
            matrix("w_k", 8, 8, 0.13),
            matrix("w_v", 8, 8, 0.12),
            matrix("w_o", 8, 8, 0.15),
            numpy_helper.from_array(np.array(2.8284271247461903, dtype=np.float32), name="scale"),
        ],
    )
    model = helper.make_model(graph, producer_name="analog-digital-chip-design-eda")
    onnx.checker.check_model(model)
    onnx.save(model, OUT)
    print(OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
