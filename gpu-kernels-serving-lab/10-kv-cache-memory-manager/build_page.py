"""Build Session 10 from KV-cache simulator JSON."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.report import esc, load_json, page


HERE = Path(__file__).resolve().parent
DATA = load_json(HERE / "out_kv_cache_memory_manager.json")


def rows() -> str:
    out = []
    for r in DATA["rows"]:
        fit0 = "yes" if r["fits_without_prefix_cache"] else "no"
        fit1 = "yes" if r["fits_with_prefix_cache"] else "no"
        fit1_cls = "ok" if r["fits_with_prefix_cache"] else "bad"
        out.append(
            "<tr>"
            f"<td>{esc(r['name'])}</td>"
            f"<td>{esc(r['requests'])}</td>"
            f"<td>{esc(r['blocks_without_prefix_cache'])}</td>"
            f"<td>{esc(r['blocks_with_prefix_cache'])}</td>"
            f"<td>{esc(r['saved_pct'])}%</td>"
            f"<td>{esc(fit0)}</td>"
            f"<td class=\"{fit1_cls}\">{esc(fit1)}</td>"
            "</tr>"
        )
    return "\n".join(out)


body = f"""
<header>
  <div class="kick">GPU kernels and LLM serving lab - Session 10</div>
  <h1>The KV cache behaves like a memory allocator.</h1>
  <p class="dek">PagedAttention-style serving is easier to understand once tokens become
  blocks. This session simulates block allocation, capacity pressure, and prefix reuse.</p>
</header>

<section>
  <div class="eye">Simulation assumptions</div>
  <h2>{esc(DATA["assumptions"]["block_size_tokens"])} tokens per block</h2>
  <p>Capacity is {esc(DATA["assumptions"]["capacity_blocks"])} blocks. {esc(DATA["assumptions"]["note"])}</p>
  <div class="why"><h3>Boundary</h3><p>{esc(DATA["boundary"])}</p></div>
</section>

<section>
  <div class="eye">Block accounting</div>
  <h2>Prefix reuse can change whether a batch fits</h2>
  <div class="card" style="overflow-x:auto">
    <table>
      <tr><th>scenario</th><th>requests</th><th>blocks no prefix</th><th>blocks with prefix</th><th>saved</th><th>fits no prefix</th><th>fits with prefix</th></tr>
      {rows()}
    </table>
  </div>
</section>

<section>
  <div class="eye">Serving implication</div>
  <p class="next">The scheduler is not just deciding which request runs next. It is packing
  blocks into scarce accelerator memory while trying to reuse shared prefixes and avoid
  preemption.</p>
</section>
"""

(HERE / "out").mkdir(exist_ok=True)
(HERE / "out" / "index.html").write_text(page("GPU Serving Lab - 10 KV Cache", body), encoding="utf-8")
print("wrote out/index.html")

