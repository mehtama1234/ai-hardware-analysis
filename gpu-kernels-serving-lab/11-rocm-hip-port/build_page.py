"""Build Session 11 from HIP portability JSON."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.report import esc, load_json, page


HERE = Path(__file__).resolve().parent
DATA = load_json(HERE / "out_rocm_hip_port.json")
R = DATA["result"]


body = f"""
<header>
  <div class="kick">GPU kernels and LLM serving lab - Session 11</div>
  <h1>Portability has to be tested, not assumed.</h1>
  <p class="dek">HIP deliberately resembles CUDA, but the compiler, profiler, runtime, and
  hardware behavior are still vendor-specific. This session starts with a minimal HIP vector
  kernel and records whether the AMD path is available.</p>
</header>

<section>
  <div class="eye">Compile/run result</div>
  <h2>{esc(R["status"])}</h2>
  <div class="card" style="overflow-x:auto">
    <table>
      <tr><th>source</th><td><span class="mono">vector_add.hip.cpp</span></td></tr>
      <tr><th>reason</th><td>{esc(R.get("reason") or R.get("stderr") or R.get("kernel"))}</td></tr>
    </table>
  </div>
  <div class="why"><h3>Boundary</h3><p>{esc(R["boundary"])}</p></div>
</section>

<section>
  <div class="eye">CUDA to HIP map</div>
  <h2>The first translation table</h2>
  <div class="card" style="overflow-x:auto">
    <table>
      <tr><th>CUDA</th><th>HIP</th></tr>
      <tr><td>cudaMalloc</td><td>hipMalloc</td></tr>
      <tr><td>cudaFree</td><td>hipFree</td></tr>
      <tr><td>cudaDeviceSynchronize</td><td>hipDeviceSynchronize</td></tr>
      <tr><td>kernel&lt;&lt;&lt;grid, block&gt;&gt;&gt;</td><td>hipLaunchKernelGGL(kernel, grid, block, ...)</td></tr>
    </table>
  </div>
</section>
"""

(HERE / "out").mkdir(exist_ok=True)
(HERE / "out" / "index.html").write_text(page("GPU Serving Lab - 11 ROCm HIP", body), encoding="utf-8")
print("wrote out/index.html")

