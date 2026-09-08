#!/usr/bin/env python3
"""Execute blocked and XOR-swizzled layout mappings in Triton CUDA."""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import torch

from layout_algebra import blocked_2d, xor_swizzled_2d

try:
    import triton
    import triton.language as tl
except ImportError:  # pragma: no cover - exercised by unavailable hosts
    triton = None
    tl = None

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "layout-algebra/reports/triton-layout-cuda.json"


if triton is not None:
    @triton.jit
    def layout_offsets_kernel(out, n_elements, cols, TILE_ROWS: tl.constexpr, TILE_COLS: tl.constexpr, MODE: tl.constexpr, BLOCK: tl.constexpr):
        pid = tl.program_id(0)
        offsets = pid * BLOCK + tl.arange(0, BLOCK)
        mask = offsets < n_elements
        row = offsets // cols
        col = offsets % cols
        tiles_per_row = cols // TILE_COLS
        tile = (row // TILE_ROWS) * tiles_per_row + (col // TILE_COLS)
        local_row = row % TILE_ROWS
        local_col = col % TILE_COLS
        if MODE == 0:
            mapped_col = local_col
        else:
            mapped_col = local_col ^ (local_row & (TILE_COLS - 1))
        result = tile * TILE_ROWS * TILE_COLS + local_row * TILE_COLS + mapped_col
        tl.store(out + offsets, result, mask=mask)


def source_hashes():
    return {str(path.relative_to(ROOT.parent.parent)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (Path(__file__), Path(__file__).with_name("layout_algebra.py"))}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", default="cuda", choices=("cpu", "cuda"))
    parser.add_argument("--repeats", type=int, default=7)
    args = parser.parse_args(argv)
    report = {
        "experiment": "triton_layout_mapping_cuda",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "requested_device": args.device,
        "repeats": args.repeats,
        "source_sha256": source_hashes(),
        "python": sys.version,
        "platform": platform.platform(),
        "measured": False,
        "gpu_execution_accepted": False,
    }
    if args.device == "cuda" and (not torch.cuda.is_available() or triton is None):
        report.update({"status": "unavailable", "reason": "cuda-runtime-or-triton", "scope": "requested Triton CUDA; runtime unavailable"})
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report, indent=2))
        return 2
    if args.device != "cuda":
        report.update({"status": "unavailable", "reason": "triton-layout-runner-requires-cuda", "scope": "Triton mapping runner is CUDA-only"})
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report, indent=2))
        return 2
    rows = 8
    cols = 16
    tile_rows = tile_cols = 4
    n_elements = rows * cols
    results = []
    for mode, layout in ((0, blocked_2d(rows, cols, tile_rows, tile_cols)), (1, xor_swizzled_2d(rows, cols, tile_rows, tile_cols))):
        output = torch.empty(n_elements, device="cuda", dtype=torch.int32)
        grid = (triton.cdiv(n_elements, 128),)
        layout_offsets_kernel[grid](output, n_elements, cols, tile_rows, tile_cols, mode, BLOCK=128)
        torch.cuda.synchronize()
        expected = torch.tensor(layout.offsets(), device="cuda", dtype=torch.int32)
        exact = bool(torch.equal(output, expected))
        start = torch.cuda.Event(enable_timing=True)
        end = torch.cuda.Event(enable_timing=True)
        samples = []
        for _ in range(args.repeats):
            start.record()
            layout_offsets_kernel[grid](output, n_elements, cols, tile_rows, tile_cols, mode, BLOCK=128)
            end.record()
            end.synchronize()
            samples.append(start.elapsed_time(end) / 1000.0)
        results.append({"layout": layout.name, "exact": exact, "median_seconds": sorted(samples)[len(samples) // 2], "samples_seconds": samples})
    passed = all(row["exact"] for row in results)
    report.update({
        "status": "passed" if passed else "failed",
        "device": "cuda",
        "device_name": torch.cuda.get_device_name(),
        "torch_version": torch.__version__,
        "triton_version": getattr(triton, "__version__", "unknown"),
        "shape": [rows, cols],
        "tile": [tile_rows, tile_cols],
        "rows": results,
        "timing_scope": "single Triton mapping kernel; CUDA-event synchronized",
        "measured": True,
        "gpu_execution_accepted": passed,
        "scope": "Triton mapping correctness and launch timing; no CuTe, bank-conflict, or occupancy claim",
    })
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps(report, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
