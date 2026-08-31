from __future__ import annotations

import re

from .common import Check, emit


LAB_ID = "comp-lab-06-portability-rocm-hip"


CUDA_SAMPLE = r"""
#include <cuda_runtime.h>
#include <mma.h>
__global__ void saxpy(float* y, const float* x, float a, int n) {
  int i = blockIdx.x * blockDim.x + threadIdx.x;
  if (i < n) y[i] = a * x[i] + y[i];
}
int main() {
  cudaStream_t stream;
  cudaStreamCreate(&stream);
  saxpy<<<128, 256, 0, stream>>>(nullptr, nullptr, 1.0f, 0);
}
"""


REWRITE_RULES = {
    "#include <cuda_runtime.h>": "#include <hip/hip_runtime.h>",
    "cudaStream_t": "hipStream_t",
    "cudaStreamCreate": "hipStreamCreate",
}


def migrate_source(source: str) -> str:
    migrated = source
    for old, new in REWRITE_RULES.items():
        migrated = migrated.replace(old, new)
    return migrated


def portability_findings(source: str) -> list[dict[str, str]]:
    findings = []
    if "#include <mma.h>" in source:
        findings.append({"severity": "manual", "issue": "wmma header requires backend-specific replacement or abstraction"})
    if re.search(r"<<<.*>>>", source, flags=re.S):
        findings.append({"severity": "check", "issue": "kernel launch syntax is HIP-compatible after hipify but still needs compile validation"})
    if "cuda" in source.lower():
        findings.append({"severity": "rewrite", "issue": "CUDA runtime symbol remains after automatic rewrite"})
    return findings


def run() -> dict[str, object]:
    migrated = migrate_source(CUDA_SAMPLE)
    before = portability_findings(CUDA_SAMPLE)
    after = portability_findings(migrated)
    checks = [
        Check("runtime_header_rewritten", "#include <hip/hip_runtime.h>" in migrated, "header migrated").__dict__,
        Check("stream_symbol_rewritten", "hipStream_t" in migrated and "hipStreamCreate" in migrated, "stream migrated").__dict__,
        Check("manual_wmma_finding_retained", any(row["severity"] == "manual" for row in after), str(after)).__dict__,
        Check("findings_do_not_disappear", len(after) >= 1 and len(before) >= len(after), f"{len(before)}->{len(after)}").__dict__,
    ]
    return {
        "summary": "Implements a CUDA-to-HIP portability scanner, rewriter, and manual-risk report.",
        "results": {"findings_before": before, "findings_after": after, "migrated_excerpt": migrated.splitlines()[:8]},
        "checks": checks,
    }


def main() -> int:
    return emit(LAB_ID, run())


if __name__ == "__main__":
    raise SystemExit(main())
