from __future__ import annotations

from . import (
    compiler_autotune,
    distributed_collectives,
    memory_hierarchy,
    portability_rocm_hip,
    profiler_evidence,
    quantization_formats,
    serving_kv_cache,
    tiled_attention,
)


LABS = [
    memory_hierarchy,
    tiled_attention,
    compiler_autotune,
    quantization_formats,
    serving_kv_cache,
    portability_rocm_hip,
    distributed_collectives,
    profiler_evidence,
]


def main() -> int:
    failures = 0
    for lab in LABS:
        failures += lab.main()
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
