#!/usr/bin/env python3
"""Create a small causal language-model fixture for token-level experiments."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import onnx
from onnx import TensorProto, helper, numpy_helper


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "tiny-causal-lm.onnx"
VOCAB = 16
HIDDEN = 8
CONTEXT = 6


def tensor(name: str, values: np.ndarray) -> onnx.TensorProto:
    return numpy_helper.from_array(values.astype(np.float32), name=name)


def main() -> int:
    token_ids = np.arange(VOCAB, dtype=np.float32)[:, None]
    dimensions = np.arange(HIDDEN, dtype=np.float32)[None, :]
    embedding = (np.sin((token_ids + 1.0) * (dimensions + 2.0)) * 0.20).astype(np.float32)
    # A deterministic output head keeps token decisions non-degenerate while
    # still requiring the attention path to transform the embedding.
    lm_head = (embedding.T * 0.42 + np.cos((dimensions.T + 1.0) * (token_ids.T + 2.0)) * 0.025).astype(np.float32)
    lm_bias = np.array([((index * 5) % 11 - 5) * 0.006 for index in range(VOCAB)], dtype=np.float32)
    mask = np.triu(np.full((CONTEXT, CONTEXT), -1.0e4, dtype=np.float32), k=1)
    nodes = [
        helper.make_node("Gather", ["embedding", "token_ids"], ["x"], name="embed.gather", axis=0),
        helper.make_node("MatMul", ["x", "w_q"], ["q"], name="attn.q.matmul"),
        helper.make_node("MatMul", ["x", "w_k"], ["k"], name="attn.k.matmul"),
        helper.make_node("MatMul", ["x", "w_v"], ["v"], name="attn.v.matmul"),
        helper.make_node("Transpose", ["k"], ["k_t"], name="attn.k.transpose", perm=[1, 0]),
        helper.make_node("MatMul", ["q", "k_t"], ["scores_raw"], name="attn.scores.matmul"),
        helper.make_node("Div", ["scores_raw", "scale"], ["scores_scaled"], name="attn.scale"),
        helper.make_node("Add", ["scores_scaled", "causal_mask"], ["scores"], name="attn.causal.mask"),
        helper.make_node("Softmax", ["scores"], ["weights"], name="attn.softmax", axis=1),
        helper.make_node("MatMul", ["weights", "v"], ["context"], name="attn.value.matmul"),
        helper.make_node("MatMul", ["context", "w_o"], ["attn_out"], name="attn.out.matmul"),
        helper.make_node("Add", ["x", "attn_out"], ["hidden"], name="residual.add"),
        helper.make_node("MatMul", ["hidden", "lm_head"], ["logits_raw"], name="lm_head.matmul"),
        helper.make_node("Add", ["logits_raw", "lm_bias"], ["logits"], name="lm_head.bias"),
    ]
    graph = helper.make_graph(
        nodes,
        "tiny_causal_language_model",
        [helper.make_tensor_value_info("token_ids", TensorProto.INT64, [CONTEXT])],
        [helper.make_tensor_value_info("logits", TensorProto.FLOAT, [CONTEXT, VOCAB])],
        [
            numpy_helper.from_array(embedding.astype(np.float32), name="embedding"),
            tensor("w_q", np.eye(HIDDEN, dtype=np.float32) * 0.44),
            tensor("w_k", np.eye(HIDDEN, dtype=np.float32) * 0.39),
            tensor("w_v", np.eye(HIDDEN, dtype=np.float32) * 0.47),
            tensor("w_o", np.eye(HIDDEN, dtype=np.float32) * 0.41),
            numpy_helper.from_array(np.array(2.8284271247461903, dtype=np.float32), name="scale"),
            tensor("causal_mask", mask),
            tensor("lm_head", lm_head),
            tensor("lm_bias", lm_bias),
        ],
    )
    model = helper.make_model(
        graph,
        producer_name="analog-digital-chip-design-eda",
        opset_imports=[helper.make_opsetid("", 13)],
    )
    onnx.checker.check_model(model)
    onnx.save(model, OUT)
    print(OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
