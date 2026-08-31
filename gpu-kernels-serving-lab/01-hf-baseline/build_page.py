"""Build Session 01 from the Hugging Face baseline JSON."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.report import esc, load_json, page


HERE = Path(__file__).resolve().parent
DATA = load_json(HERE / "out_hf_baseline.json")
R = DATA["result"]


def metric_rows() -> str:
    metrics = [
        ("path", R.get("path")),
        ("model", R.get("model")),
        ("device", R.get("device")),
        ("dtype", R.get("dtype")),
        ("batch size", R.get("batch_size")),
        ("prompt tokens", R.get("prompt_tokens")),
        ("generated tokens/request", R.get("generated_tokens_per_request")),
        ("TTFT", f"{R['ttft_ms']} ms" if R.get("ttft_ms") is not None else "not measured"),
        ("decode time", f"{R.get('total_decode_ms')} ms"),
        ("throughput", f"{R.get('tokens_per_sec')} tokens/sec"),
        ("peak memory", f"{R.get('peak_memory_mb')} MB" if R.get("peak_memory_mb") is not None else "not available"),
        ("parameters", f"{R.get('parameter_count'):,}" if R.get("parameter_count") else None),
        ("weight memory estimate", f"{R.get('weight_memory_mb_estimate')} MB"),
        ("KV-cache estimate", f"{R.get('kv_cache_mb_estimate')} MB"),
    ]
    return "\n".join(f"<tr><td>{esc(k)}</td><td>{esc(v)}</td></tr>" for k, v in metrics)


def outputs_block() -> str:
    outputs = R.get("sample_outputs") or []
    if not outputs:
        return "<p>No real text outputs were decoded because the local fallback path ran.</p>"
    empty = '<span class="mono">empty continuation</span>'
    items = "".join(f"<li>{esc(text) if text else empty}</li>" for text in outputs)
    return f"<ul>{items}</ul>"


fallback = ""
if R.get("fallback_reason"):
    fallback = f"""
    <div class="why"><h3>Fallback reason</h3><p>{esc(R["fallback_reason"])}</p></div>
    """

body = f"""
<header>
  <div class="kick">GPU kernels and LLM serving lab - Session 01</div>
  <h1>Start with the model API everyone actually uses.</h1>
  <p class="dek">Before custom kernels or serving engines, we need the high-level baseline:
  load a model, tokenize prompts, generate continuations, and record the time and memory
  the API hides. This page is generated from `out_hf_baseline.json`.</p>
</header>

<section>
  <div class="eye">Measured baseline</div>
  <h2>Generation result</h2>
  <div class="card" style="overflow-x:auto">
    <table>
      <tr><th>field</th><th>value</th></tr>
      {metric_rows()}
    </table>
  </div>
  {fallback}
  <div class="why"><h3>Boundary</h3><p>{esc(R["boundary"])}</p></div>
</section>

<section>
  <div class="eye">Why this matters</div>
  <h2>The API collapses several hardware costs into one call</h2>
  <p>`model.generate()` looks like one operation, but it includes tokenization, weight reads,
  attention/KV-cache reads and writes, kernel launches, sampling or greedy decode, and Python
  scheduling overhead. Later sessions pull those pieces apart until the bottleneck is visible.</p>
</section>

<section>
  <div class="eye">Decoded outputs</div>
  <h2>What came back</h2>
  <div class="card">{outputs_block()}</div>
</section>

<section>
  <div class="eye">Next slice</div>
  <p class="next">Next: Session 02 builds the roofline view with vector add, reduction,
  matrix multiply, and KV-cache scan microbenchmarks.</p>
</section>
"""

(HERE / "out").mkdir(exist_ok=True)
(HERE / "out" / "index.html").write_text(page("GPU Serving Lab - 01 HF Baseline", body), encoding="utf-8")
print("wrote out/index.html")
