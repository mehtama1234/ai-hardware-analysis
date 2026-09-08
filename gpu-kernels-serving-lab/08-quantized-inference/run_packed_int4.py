"""Actual packed storage and CPU unpack-plus-matmul costs on synthetic weights."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
import torch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
from common.packed_int4 import pack_int4, unpack_int4
from common.bench import sample_seconds
from common.provenance import source_provenance


def main():
    threads = torch.get_num_threads()
    torch.set_num_threads(1)
    rows = []
    try:
        for k, n in ((7, 5), (32, 32), (65, 33)):
            generator = torch.Generator().manual_seed(121)
            weights = torch.randn((k, n), generator=generator)
            inputs = torch.randn((8, k), generator=generator)
            packed = pack_int4(weights)
            reconstructed = unpack_int4(packed)
            reference = inputs @ weights
            result = inputs @ reconstructed
            # Packing correctness is distinct from acceptable task-level drift.
            bounds = packed.scales.repeat_interleave(32)[:weights.numel()].reshape_as(weights) / 2 + 1e-6
            if not bool(((reconstructed - weights).abs() <= bounds).all()):
                raise AssertionError("quantization error exceeds rounding bound")
            rows.append({"shape": [8, k, n], "seed": 121, "evidence_kind": "measured_cpu",
                "fp32_weight_storage_bytes": weights.untyped_storage().nbytes(),
                "packed_tensor_storage_bytes": packed.tensor_storage_bytes,
                "payload_bytes": packed.payload.untyped_storage().nbytes(),
                "scale_bytes": packed.scales.untyped_storage().nbytes(),
                "reconstructed_weight_bytes": reconstructed.untyped_storage().nbytes(),
                "weight_max_abs_error": float((reconstructed - weights).abs().max()),
                "output_relative_l2_error": float((result - reference).norm() / reference.norm()),
                "pack_samples_seconds": sample_seconds(lambda: pack_int4(weights), 2, 7),
                "unpack_samples_seconds": sample_seconds(lambda: unpack_int4(packed), 2, 7),
                "fp32_matmul_samples_seconds": sample_seconds(lambda: inputs @ weights, 2, 7),
                "unpack_and_matmul_samples_seconds": sample_seconds(lambda: inputs @ unpack_int4(packed), 2, 7)})
    finally:
        torch.set_num_threads(threads)
    report = {"timestamp": datetime.now(timezone.utc).isoformat(), "rows": rows,
        "torch_version": torch.__version__, "cpu_threads": 1, "warmup": 2, "repeat": 7,
        "format": "local symmetric INT4 offset nibbles, block32 FP32 scales",
        "boundary": "packed storage measured; compute unpacks to FP32; no native INT4 GEMM, task quality, process peak memory or GPU claim; storage excludes Python/shape metadata",
        "task_quality_accepted": False, "gpu_execution_accepted": False,
        "provenance": source_provenance(ROOT.parent, [Path(__file__), ROOT / "common/packed_int4.py",
            ROOT / "common/bench.py", ROOT / "common/provenance.py"])}
    output = HERE / "out_packed_int4.json"
    output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    for row in rows:
        print(row["shape"], row["fp32_weight_storage_bytes"], "->", row["packed_tensor_storage_bytes"], "bytes", row["output_relative_l2_error"], "relative output error")


if __name__ == "__main__":
    main()
