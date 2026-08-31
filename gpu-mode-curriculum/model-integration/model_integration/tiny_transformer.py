from __future__ import annotations

import json
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from typing import Any

import torch
from torch import nn


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "custom-ops"))
sys.path.insert(0, str(ROOT / "autotune-db"))

from autotune_db import select_config  # noqa: E402
from custom_ops import fused_bias_gelu_residual, reference_bias_gelu_residual  # noqa: E402


AUTOTUNE_DB = ROOT / "autotune-db" / "autotune-db.json"
REPORT_JSON = ROOT / "model-integration" / "reports" / "tiny-transformer-report.json"
REPORT_MD = ROOT / "model-integration" / "reports" / "tiny-transformer-report.md"


@dataclass(frozen=True)
class ModelCase:
    name: str
    batch: int
    seq: int
    hidden: int
    heads: int


CASES = [
    ModelCase("chat-prefill-small", batch=2, seq=16, hidden=64, heads=4),
    ModelCase("decode-window-medium", batch=2, seq=32, hidden=128, heads=4),
    ModelCase("long-context-proxy", batch=1, seq=64, hidden=128, heads=4),
]


class TinyTransformerBlock(nn.Module):
    def __init__(self, hidden: int, heads: int, use_fused: bool) -> None:
        super().__init__()
        if hidden % heads != 0:
            raise ValueError("hidden must be divisible by heads")
        self.hidden = hidden
        self.heads = heads
        self.use_fused = use_fused
        self.ln1 = nn.LayerNorm(hidden)
        self.qkv = nn.Linear(hidden, hidden * 3, bias=False)
        self.proj = nn.Linear(hidden, hidden, bias=False)
        self.ln2 = nn.LayerNorm(hidden)
        self.ff = nn.Linear(hidden, hidden, bias=False)
        self.ff_bias = nn.Parameter(torch.zeros(hidden))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        batch, seq, hidden = x.shape
        head_dim = hidden // self.heads
        normed = self.ln1(x)
        qkv = self.qkv(normed).view(batch, seq, 3, self.heads, head_dim)
        q, k, v = qkv.unbind(dim=2)
        q = q.transpose(1, 2)
        k = k.transpose(1, 2)
        v = v.transpose(1, 2)
        scores = torch.matmul(q, k.transpose(-2, -1)) / (head_dim**0.5)
        mask = torch.triu(torch.ones(seq, seq, dtype=torch.bool, device=x.device), diagonal=1)
        scores = scores.masked_fill(mask, float("-inf"))
        attention = torch.softmax(scores, dim=-1)
        context = torch.matmul(attention, v).transpose(1, 2).contiguous().view(batch, seq, hidden)
        residual = x + self.proj(context)
        ff_input = self.ff(self.ln2(residual)).reshape(batch * seq, hidden)
        residual_flat = residual.reshape(batch * seq, hidden)
        if self.use_fused:
            out = fused_bias_gelu_residual(ff_input, self.ff_bias, residual_flat)
        else:
            out = reference_bias_gelu_residual(ff_input, self.ff_bias, residual_flat)
        return out.view(batch, seq, hidden)


def _load_autotune() -> dict[str, Any]:
    if not AUTOTUNE_DB.exists():
        return {"records": []}
    return json.loads(AUTOTUNE_DB.read_text(encoding="utf-8"))


def _make_pair(case: ModelCase, seed: int) -> tuple[TinyTransformerBlock, TinyTransformerBlock]:
    torch.manual_seed(seed)
    reference = TinyTransformerBlock(case.hidden, case.heads, use_fused=False)
    fused = TinyTransformerBlock(case.hidden, case.heads, use_fused=True)
    fused.load_state_dict(reference.state_dict())
    return reference, fused


def _timed_forward_backward(model: nn.Module, x: torch.Tensor, repeats: int) -> dict[str, float]:
    timings = []
    for _ in range(repeats):
        model.zero_grad(set_to_none=True)
        input_tensor = x.detach().clone().requires_grad_(True)
        start = time.perf_counter()
        out = model(input_tensor)
        loss = out.float().pow(2).mean()
        loss.backward()
        timings.append(time.perf_counter() - start)
    return {"median": median(timings), "min": min(timings), "max": max(timings)}


def _selected_tuning(database: dict[str, Any]) -> dict[str, Any]:
    selected: dict[str, Any] = {}
    for family, shape in [("matmul", "medium-square"), ("normalization", "wide"), ("custom-op", "decoder-hidden")]:
        try:
            record = select_config(database, family, shape)
            selected[family] = {
                "record_id": record["id"],
                "shape_class": record["shape_class"],
                "config_id": record["selected"]["config"]["id"],
                "estimated_speedup_vs_measured": record["selected"]["estimated_speedup_vs_measured"],
            }
        except KeyError:
            selected[family] = {"missing": True}
    return selected


def run_case(case: ModelCase, repeats: int, seed: int, database: dict[str, Any]) -> dict[str, Any]:
    reference, fused = _make_pair(case, seed)
    generator = torch.Generator(device="cpu").manual_seed(seed + 900)
    x_ref = torch.randn((case.batch, case.seq, case.hidden), generator=generator, dtype=torch.float32, requires_grad=True)
    x_fused = x_ref.detach().clone().requires_grad_(True)
    ref_out = reference(x_ref)
    fused_out = fused(x_fused)
    ref_loss = ref_out.float().pow(2).mean()
    fused_loss = fused_out.float().pow(2).mean()
    ref_loss.backward()
    fused_loss.backward()
    max_abs_error = float((ref_out - fused_out).abs().max().item())
    grad_max_abs_error = float((x_ref.grad - x_fused.grad).abs().max().item())
    reference_time = _timed_forward_backward(reference, x_ref, repeats)
    fused_time = _timed_forward_backward(fused, x_ref, repeats)
    token_count = case.batch * case.seq
    checks = {
        "output_close": bool(torch.allclose(ref_out, fused_out, atol=2e-5, rtol=2e-5)),
        "grad_close": bool(torch.allclose(x_ref.grad, x_fused.grad, atol=2e-5, rtol=2e-5)),
        "finite_output": bool(torch.isfinite(fused_out).all().item()),
        "autotune_records_selected": all(not row.get("missing") for row in _selected_tuning(database).values()),
    }
    return {
        "id": case.name,
        "shape": {"batch": case.batch, "seq": case.seq, "hidden": case.hidden, "heads": case.heads, "tokens": token_count},
        "status": "passed" if all(checks.values()) else "failed",
        "checks": checks,
        "max_abs_error": max_abs_error,
        "grad_max_abs_error": grad_max_abs_error,
        "seconds": {"reference": reference_time, "fused": fused_time},
        "tokens_per_second": round(token_count / max(fused_time["median"], 1e-9), 4),
        "selected_tuning": _selected_tuning(database),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Tiny Transformer Integration Report",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Cases: `{report['case_count']}`",
        "",
        "| case | shape | status | max abs error | grad error | fused median s | tokens/s |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    for case in report["cases"]:
        shape = case["shape"]
        shape_text = f"{shape['batch']}x{shape['seq']}x{shape['hidden']} h={shape['heads']}"
        lines.append(
            "| "
            f"{case['id']} | {shape_text} | {case['status']} | {case['max_abs_error']:.6g} | "
            f"{case['grad_max_abs_error']:.6g} | {case['seconds']['fused']['median']:.8f} | {case['tokens_per_second']} |"
        )
    lines.extend(["", "## Selected Autotune Records", ""])
    for family, selected in report["selected_tuning_summary"].items():
        lines.append(f"- `{family}`: `{selected}`")
    return "\n".join(lines).rstrip() + "\n"


def run_all(repeats: int = 3) -> dict[str, Any]:
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    database = _load_autotune()
    cases = [run_case(case, repeats=repeats, seed=2200 + index, database=database) for index, case in enumerate(CASES)]
    selected_summary = _selected_tuning(database)
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "case_count": len(cases),
        "passed": sum(1 for case in cases if case["status"] == "passed"),
        "failed": sum(1 for case in cases if case["status"] != "passed"),
        "model": "tiny-causal-transformer-block",
        "uses_custom_op": "fused_bias_gelu_residual",
        "source_reports": ["custom-ops/reports/custom-op-report.json", "autotune-db/autotune-db.json"],
        "selected_tuning_summary": selected_summary,
        "cases": cases,
    }
    REPORT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")
    return report
