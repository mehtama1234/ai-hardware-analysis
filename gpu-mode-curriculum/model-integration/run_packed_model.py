"""Packed-weight inference integration on the existing untrained transformer."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
import torch

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "gpu-kernels-serving-lab"))
from common.bench import sample_seconds
from common.packed_linear import converted_copy, tensor_storage_bytes, PackedInt4Linear
from common.provenance import source_provenance
from model_integration.tiny_transformer import TinyTransformerBlock


def main():
    threads = torch.get_num_threads()
    torch.set_num_threads(1)
    try:
        with torch.random.fork_rng(devices=[]):
            torch.manual_seed(131)
            model = TinyTransformerBlock(32, 4, False, "sdpa").eval()
        packed = converted_copy(model)
        layers = [name for name, layer in packed.named_modules() if isinstance(layer, PackedInt4Linear)]
        if any(isinstance(layer, torch.nn.Linear) for layer in packed.modules()):
            raise AssertionError("unconverted linear layer")
        generator = torch.Generator().manual_seed(132)
        rows = []
        with torch.no_grad():
            for sequence in (1, 17, 33):
                x = torch.randn((2, sequence, 32), generator=generator)
                reference, output = model(x), packed(x)
                if not bool(torch.isfinite(output).all()):
                    raise AssertionError("nonfinite packed model output")
                # Validate cache integration against the quantized full forward,
                # not against FP32 weights which intentionally differ.
                prefill, cache = packed.forward_cached(x[:, :1])
                outputs = [prefill]
                for position in range(1, sequence):
                    token, cache = packed.forward_cached(x[:, position:position + 1], cache)
                    outputs.append(token)
                torch.testing.assert_close(torch.cat(outputs, dim=1), output, atol=2e-6, rtol=2e-5)
                rows.append({"sequence": sequence, "evidence_kind": "measured_cpu",
                    "output_max_abs_error": float((output - reference).abs().max()),
                    "output_relative_l2_error": float((output - reference).norm() / reference.norm()),
                    "cached_vs_full": "passed",
                    "fp32_samples_seconds": sample_seconds(lambda: model(x), 2, 7),
                    "packed_samples_seconds": sample_seconds(lambda: packed(x), 2, 7)})
        report = {"timestamp": datetime.now(timezone.utc).isoformat(), "rows": rows,
            "model_seed": 131, "data_seed": 132, "warmup": 2, "repeat": 7,
            "torch_version": torch.__version__, "cpu_threads": 1, "converted_layers": layers,
            "fp32_model_storage_bytes": tensor_storage_bytes(model),
            "packed_model_storage_bytes": tensor_storage_bytes(packed),
            "quality_accepted": False, "gpu_execution_accepted": False,
            "scope": "untrained block, synthetic inputs, inference-only; packed linear buffers unpack to FP32 per call; timings include unpack and allocation; storage counts unique parameter/buffer allocations, not runtime peak or Python metadata",
            "provenance": source_provenance(REPO, [Path(__file__), HERE / "model_integration/tiny_transformer.py",
                REPO / "gpu-kernels-serving-lab/common/packed_int4.py", REPO / "gpu-kernels-serving-lab/common/packed_linear.py",
                REPO / "gpu-kernels-serving-lab/common/bench.py", REPO / "gpu-kernels-serving-lab/common/provenance.py"])}
    finally:
        torch.set_num_threads(threads)
    (HERE / "reports/packed-model-cpu.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(report["fp32_model_storage_bytes"], "->", report["packed_model_storage_bytes"], "model tensor bytes")
    for row in rows:
        print(row["sequence"], row["output_relative_l2_error"], "relative output error", row["cached_vs_full"])


if __name__ == "__main__":
    main()
