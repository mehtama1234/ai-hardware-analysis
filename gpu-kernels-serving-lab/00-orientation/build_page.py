"""Build the Session 00 orientation page from the inventory JSON."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.report import esc, load_json, page


HERE = Path(__file__).resolve().parent
DATA = load_json(HERE / "out_orientation.json")


def status_cell(value: object) -> str:
    if value in (True, "available"):
        return '<td class="ok">available</td>'
    if value:
        return f'<td class="ok">{esc(value)}</td>'
    return '<td class="warn">missing</td>'


def package_rows() -> str:
    rows = []
    for name, version in DATA["software"]["packages"].items():
        rows.append(f"<tr><td>{esc(name)}</td>{status_cell(version)}</tr>")
    return "\n".join(rows)


def device_rows() -> str:
    torch = DATA["torch"]
    devices = torch.get("devices") or []
    if not devices:
        return '<tr><td>No CUDA/HIP devices reported by torch</td><td class="warn">skip</td><td>Later GPU sessions should emit skip artifacts until hardware is available.</td></tr>'
    rows = []
    for dev in devices:
        rows.append(
            "<tr>"
            f"<td>{esc(dev.get('name'))}</td>"
            f"<td class=\"ok\">{esc(dev.get('total_memory_mb'))} MB</td>"
            f"<td>SM {esc(dev.get('major'))}.{esc(dev.get('minor'))}, {esc(dev.get('multi_processor_count'))} multiprocessors</td>"
            "</tr>"
        )
    return "\n".join(rows)


def command_rows() -> str:
    rows = []
    for name, entry in DATA["commands"].items():
        path = entry.get("path")
        state = "available" if path else None
        detail = path or "not on PATH"
        if entry.get("stdout_head"):
            detail += " | " + " / ".join(entry["stdout_head"][:2])
        rows.append(f"<tr><td>{esc(name)}</td>{status_cell(state)}<td>{esc(detail)}</td></tr>")
    return "\n".join(rows)


body = f"""
<header>
  <div class="kick">GPU kernels and LLM serving lab - Session 00</div>
  <h1>Map the machine before optimizing it.</h1>
  <p class="dek">This first page records what the local environment can actually run: PyTorch,
  CUDA or ROCm tools, Triton, Hugging Face packages, vLLM, and JAX. Later sessions reuse
  the same measurement habit: run the code, write JSON, then render the explanation from
  the evidence.</p>
</header>

<section>
  <div class="eye">Stack path</div>
  <h2>From API call to accelerator work</h2>
  <div class="card">
    <pre>prompt
  -> tokenizer
  -> model weights
  -> attention and KV cache
  -> framework runtime
  -> fused kernels / custom kernels
  -> scheduler and memory manager
  -> response tokens</pre>
  </div>
  <div class="why"><h3>Boundary</h3><p>{esc(DATA["boundary"])}</p></div>
</section>

<section>
  <div class="eye">Hardware inventory</div>
  <h2>What this machine exposes</h2>
  <div class="card" style="overflow-x:auto">
    <table>
      <tr><th>device</th><th>memory/status</th><th>details</th></tr>
      {device_rows()}
    </table>
  </div>
</section>

<section>
  <div class="eye">Runtime inventory</div>
  <h2>Python packages</h2>
  <div class="card" style="overflow-x:auto">
    <table>
      <tr><th>package</th><th>version/status</th></tr>
      {package_rows()}
    </table>
  </div>
</section>

<section>
  <div class="eye">Compiler and driver tools</div>
  <h2>Command-line interfaces</h2>
  <div class="card" style="overflow-x:auto">
    <table>
      <tr><th>tool</th><th>status</th><th>detail</th></tr>
      {command_rows()}
    </table>
  </div>
</section>

<section>
  <div class="eye">Next slice</div>
  <p class="next">Next: Session 01 will run a Hugging Face generation baseline and record
  tokens/sec, TTFT, peak memory, prompt length, output length, and the KV-cache estimate.</p>
</section>
"""

(HERE / "out").mkdir(exist_ok=True)
(HERE / "out" / "index.html").write_text(page("GPU Serving Lab - 00 Orientation", body), encoding="utf-8")
print("wrote out/index.html")

