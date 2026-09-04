#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"

STYLE = """
:root{--bg:#f7f4ee;--ink:#1d2525;--muted:#5d6662;--line:#d8d0c3;--card:#ffffff;--accent:#0f6b61}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 system-ui,-apple-system,Segoe UI,sans-serif}
a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}
.wrap{max-width:1100px;margin:0 auto;padding:32px 20px}
header{border-bottom:1px solid var(--line);background:#fffaf1}
.k{font-size:12px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);font-weight:700}
h1{font-size:42px;line-height:1.08;margin:10px 0 12px}h2{font-size:25px;margin:34px 0 10px}h3{font-size:18px;margin:0 0 8px}
p{margin:0 0 14px}.lead{font-size:19px;color:var(--muted);max-width:820px}
nav{display:flex;flex-wrap:wrap;gap:10px;margin-top:18px}nav a,.pill{border:1px solid var(--line);border-radius:999px;padding:6px 10px;background:#fff;color:var(--ink);font-size:14px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:14px;margin-top:18px}
.card{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:16px}
.section{padding:28px 0;border-bottom:1px solid var(--line)}
article{max-width:840px}.article-body pre{background:#1f2827;color:#f5f0e8;padding:14px;border-radius:8px;overflow:auto}
.article-body code{background:#eee7da;padding:1px 4px;border-radius:4px}.article-body pre code{background:transparent;padding:0}
ul,ol{padding-left:22px}li{margin:6px 0}
table{border-collapse:collapse;width:100%;margin:14px 0;background:#fff}th,td{border:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}th{background:#fffaf1}
"""


def title_from_markdown(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def slug(path: Path) -> str:
    return path.stem


def markdown_to_html(text: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    in_code = False
    in_ul = False
    in_ol = False
    in_table = False
    paragraph: list[str] = []

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            out.append(f"<p>{inline(' '.join(paragraph))}</p>")
            paragraph = []

    def close_lists() -> None:
        nonlocal in_ul, in_ol
        if in_ul:
            out.append("</ul>")
            in_ul = False
        if in_ol:
            out.append("</ol>")
            in_ol = False

    def close_table() -> None:
        nonlocal in_table
        if in_table:
            out.append("</tbody></table>")
            in_table = False

    for raw in lines:
        line = raw.rstrip()
        if line.startswith("```"):
            flush_paragraph()
            close_lists()
            close_table()
            if in_code:
                out.append("</code></pre>")
                in_code = False
            else:
                out.append("<pre><code>")
                in_code = True
            continue
        if in_code:
            out.append(html.escape(line))
            continue
        if not line:
            flush_paragraph()
            close_lists()
            close_table()
            continue
        if line.startswith("#"):
            flush_paragraph()
            close_lists()
            close_table()
            level = min(len(line) - len(line.lstrip("#")), 3)
            content = line[level:].strip()
            out.append(f"<h{level}>{inline(content)}</h{level}>")
            continue
        if line.startswith("|") and line.endswith("|"):
            flush_paragraph()
            close_lists()
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            is_separator = all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)
            if is_separator:
                continue
            if not in_table:
                out.append("<table><tbody>")
                in_table = True
                tag = "th"
            else:
                tag = "td"
            out.append("<tr>" + "".join(f"<{tag}>{inline(cell)}</{tag}>" for cell in cells) + "</tr>")
            continue
        if line.startswith("- "):
            flush_paragraph()
            close_table()
            if in_ol:
                out.append("</ol>")
                in_ol = False
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            out.append(f"<li>{inline(line[2:].strip())}</li>")
            continue
        if re.match(r"^\d+\. ", line):
            flush_paragraph()
            close_table()
            if in_ul:
                out.append("</ul>")
                in_ul = False
            if not in_ol:
                out.append("<ol>")
                in_ol = True
            item_text = re.sub(r"^\d+\. ", "", line).strip()
            out.append(f"<li>{inline(item_text)}</li>")
            continue
        paragraph.append(line)
    flush_paragraph()
    close_lists()
    close_table()
    if in_code:
        out.append("</code></pre>")
    return "\n".join(out)


def inline(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda m: f'<a href="{html.escape(m.group(2), quote=True)}">{m.group(1)}</a>',
        escaped,
    )
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    return escaped


def page(title: str, kicker: str, lead: str, body: str, nav_prefix: str = "") -> str:
    nav = f"""<nav><a href="{nav_prefix}index.html">Hub</a><a href="{nav_prefix}synthesis.html">Synthesis</a><a href="{nav_prefix}paper-synthesis.html">Paper synthesis</a><a href="{nav_prefix}coverage-audit.html">Coverage audit</a><a href="{nav_prefix}concepts.html">Concepts</a><a href="{nav_prefix}labs.html">Labs</a><a href="{nav_prefix}research.html">Research</a><a href="{nav_prefix}papers.html">Papers</a></nav>"""
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><style>{STYLE}</style></head>
<body><header><div class="wrap"><div class="k">{html.escape(kicker)}</div><h1>{html.escape(title)}</h1><p class="lead">{html.escape(lead)}</p>{nav}</div></header><main class="wrap">{body}</main></body></html>"""


def write_markdown_page(source: Path, dest: Path, kicker: str, nav_prefix: str = "") -> tuple[str, str]:
    text = source.read_text(encoding="utf-8")
    if source.relative_to(ROOT).as_posix() == "docs/research/current-aimc-system-state.md":
        generated = ROOT / "evidence" / "aimc-hardware-lab" / "current-aimc-system-state.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    generated_reports = {
        "docs/research/sky130-transistor-dac-pvt-calibration-policy.md": "sky130-transistor-dac-pvt-calibration-policy.md",
        "docs/research/sky130-transistor-dac-mismatch-sweep.md": "sky130-transistor-dac-mismatch-sweep.md",
        "docs/research/sky130-transistor-dac-settling-sweep.md": "sky130-transistor-dac-settling-sweep.md",
        "docs/research/sky130-bottom-plate-cell.md": "sky130-bottom-plate-cell.md",
        "docs/research/sky130-bottom-plate-incremental-diagnostic.md": "sky130-bottom-plate-incremental-diagnostic.md",
        "docs/research/sky130-long-acquisition-coupled-probe.md": "sky130-long-acquisition-coupled-probe.md",
        "docs/research/measured-transistor-dac-sar-replay.md": "measured-transistor-dac-sar-replay.md",
        "docs/research/sky130-coupled-dac-comparator-bit.md": "sky130-coupled-dac-comparator-bit.md",
        "docs/research/sky130-physical-dac-sar-sequence.md": "sky130-physical-dac-sar-sequence.md",
        "docs/research/sky130-calibrated-physical-sar.md": "sky130-calibrated-physical-sar.md",
        "docs/research/sky130-coupled-sample-cap-sweep.md": "sky130-coupled-sample-cap-sweep.md",
        "docs/research/sky130-bottom-switch-scale-sweep.md": "sky130-bottom-switch-scale-sweep.md",
        "docs/research/sky130-bottom-plate-topology-sweep.md": "sky130-bottom-plate-topology-sweep.md",
    }
    generated_name = generated_reports.get(source.relative_to(ROOT).as_posix())
    if generated_name:
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / generated_name
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/next-aimc-evidence-work-queue.md":
        generated = ROOT / "evidence" / "aimc-hardware-lab" / "next-evidence-work-queue.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/onnx-fixture-inventory.md":
        generated = ROOT / "evidence" / "aimc-hardware-lab" / "onnx-fixture-inventory.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/aihwkit-residual-diagnostic.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "aihwkit-residual-diagnostic.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/aihwkit-ideal-forward-mapping-proof.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "aihwkit-ideal-forward-mapping-proof.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/aihwkit-forward-setting-sweep.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "aihwkit-forward-setting-sweep.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/aihwkit-physical-setting-review.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "aihwkit-physical-setting-review.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/aihwkit-current-tile-boundary-replay.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "aihwkit-current-tile-boundary-replay.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/aihwkit-converter-upgrade-target.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "aihwkit-converter-upgrade-target.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/aihwkit-converter-cost-model.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "aihwkit-converter-cost-model.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/aihwkit-target-noise-sensitivity.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "aihwkit-target-noise-sensitivity.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/aihwkit-converter-break-even.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "aihwkit-converter-break-even.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/converter-circuit-evidence-contract.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-circuit-evidence-contract.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/local-converter-circuit-estimate.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "local-converter-circuit-estimate.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/converter-circuit-simulation-estimate.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-circuit-simulation-estimate.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/converter-spice-handoff-spec.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-spice-handoff-spec.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/row-dac-settling-spice-evidence.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "row-dac-settling-spice-evidence.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/sar-readout-spice-evidence.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sar-readout-spice-evidence.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/shared-converter-loading-spice-evidence.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "shared-converter-loading-spice-evidence.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/converter-supply-energy-spice-evidence.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-supply-energy-spice-evidence.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/digital-physical-artifact-boundary.md":
        generated = ROOT / "evidence" / "aimc-hardware-lab" / "digital-physical-artifact-boundary.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/simulator-to-post-layout-gap-audit.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "simulator-to-post-layout-gap-audit.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/analog-converter-layout-work-order.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "analog-converter-layout-work-order.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/analog-converter-layout-starter-package.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "analog-converter-layout-starter-package.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/analog-converter-layout-tool-readiness.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "analog-converter-layout-tool-readiness.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/analog-converter-pdk-readiness.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "analog-converter-pdk-readiness.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/magic-sky130-extraction-smoke.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "magic-sky130-extraction-smoke.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/magic-sky130-compatibility.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "magic-sky130-compatibility.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/row-dac-10b-layout-smoke.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "row-dac-10b-layout-smoke.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/converter-starter-layout-smoke.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-starter-layout-smoke.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/converter-starter-post-layout-candidate.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-starter-post-layout-candidate.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/converter-starter-physical-artifacts.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-starter-physical-artifacts.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/converter-starter-parasitic-load-estimate.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-starter-parasitic-load-estimate.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/converter-starter-parasitic-break-even-rerun.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-starter-parasitic-break-even-rerun.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/converter-starter-extracted-rc-ngspice.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-starter-extracted-rc-ngspice.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/first-real-converter-candidate-packet.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "first-real-converter-candidate-packet.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/first-real-converter-rehearsal-payload.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "first-real-converter-rehearsal-payload.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/first-real-converter-blocker-work-order.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "first-real-converter-blocker-work-order.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/first-real-converter-physical-object-audit.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "first-real-converter-physical-object-audit.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/first-real-converter-physical-object-assembly.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "first-real-converter-physical-object-assembly.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/first-real-converter-energy-candidate.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "first-real-converter-energy-candidate.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/first-real-converter-latency-candidate.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "first-real-converter-latency-candidate.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/first-real-converter-noise-candidate.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "first-real-converter-noise-candidate.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/first-real-converter-area-candidate.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "first-real-converter-area-candidate.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/first-real-converter-break-even-candidate.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "first-real-converter-break-even-candidate.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/first-real-converter-candidate-loop-strict-readiness.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "first-real-converter-candidate-loop-strict-readiness.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/sky130-transistor-sample-switch-ngspice.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-transistor-sample-switch-ngspice.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/sky130-sample-switch-hold-mode-ngspice.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-sample-switch-hold-mode-ngspice.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/sky130-sample-switch-hold-mitigation-sweep.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-sample-switch-hold-mitigation-sweep.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/sky130-sample-switch-dummy-cancellation-ngspice.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-sample-switch-dummy-cancellation-ngspice.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/sky130-bottom-plate-sampling-ngspice.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-bottom-plate-sampling-ngspice.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/sky130-sample-hold-topology-decision-gate.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-sample-hold-topology-decision-gate.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/sky130-buffered-sample-hold-ngspice.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-buffered-sample-hold-ngspice.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/sky130-bootstrapped-switch-ngspice.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-bootstrapped-switch-ngspice.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/sky130-fully-differential-sampling-ngspice.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-fully-differential-sampling-ngspice.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/sky130-differential-dummy-cancellation-ngspice.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-differential-dummy-cancellation-ngspice.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/sky130-differential-dummy-candidate-input-sweep.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-differential-dummy-candidate-input-sweep.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/sky130-differential-dummy-candidate-mismatch-sweep.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-differential-dummy-candidate-mismatch-sweep.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/sky130-differential-dummy-candidate-decision-margin.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-differential-dummy-candidate-decision-margin.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/sky130-differential-dummy-candidate-offset-noise-stress.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-differential-dummy-candidate-offset-noise-stress.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/sky130-comparator-acceptance-fixture-spec.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-comparator-acceptance-fixture-spec.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/sky130-comparator-input-stage-ngspice.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-comparator-input-stage-ngspice.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/sky130-clocked-comparator-latch-ngspice.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-clocked-comparator-latch-ngspice.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/sky130-sample-hold-latch-kickback-ngspice.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-sample-hold-latch-kickback-ngspice.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/sky130-latch-input-size-kickback-sweep.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-latch-input-size-kickback-sweep.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/sky130-comparator-isolation-target.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-comparator-isolation-target.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/sky130-capacitive-latch-input-isolation-sweep.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-capacitive-latch-input-isolation-sweep.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/sky130-capacitive-isolation-both-polarity-confirm.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-capacitive-isolation-both-polarity-confirm.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/sky130-capacitive-isolation-post-layout-handoff.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-capacitive-isolation-post-layout-handoff.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/sky130-capacitive-isolation-physical-cell-gap.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-capacitive-isolation-physical-cell-gap.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/sky130-capacitive-isolation-post-layout-both-polarity.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-capacitive-isolation-post-layout-both-polarity.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/sky130-capacitive-isolation-extracted-port-mapping-diagnostic.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-capacitive-isolation-extracted-port-mapping-diagnostic.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/sky130-capacitive-isolation-extracted-coupling-strength-sweep.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-capacitive-isolation-extracted-coupling-strength-sweep.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/sky130-extracted-frontend-redesign-target.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-extracted-frontend-redesign-target.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/sky130-balanced-frontend-work-order.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-balanced-frontend-work-order.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/sky130-balanced-frontend-starter-extraction.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-balanced-frontend-starter-extraction.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/sky130-balanced-frontend-sign-preservation.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-balanced-frontend-sign-preservation.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/sky130-balanced-frontend-latch-decision.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-balanced-frontend-latch-decision.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/sky130-balanced-frontend-sense-gain-target.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-balanced-frontend-sense-gain-target.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/sky130-strong-sense-frontend-candidate.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-strong-sense-frontend-candidate.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/sky130-ultra-sense-frontend-candidate.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-ultra-sense-frontend-candidate.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/sky130-frontend-sense-efficiency-audit.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-frontend-sense-efficiency-audit.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/differential-sampling-control-proof-ngspice.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "differential-sampling-control-proof-ngspice.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/sky130-single-device-charge-injection-ngspice.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-single-device-charge-injection-ngspice.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/sky130-sample-switch-clock-edge-sweep.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-sample-switch-clock-edge-sweep.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/sky130-sample-hold-design-target.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-sample-hold-design-target.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/sky130-differential-matching-requirement.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-differential-matching-requirement.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/sky130-next-transistor-fixture-work-order.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-next-transistor-fixture-work-order.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/analog-converter-sky130-workbench-env.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "analog-converter-sky130-workbench-env.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/analog-converter-physical-cell-gate.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "analog-converter-physical-cell-gate.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/analog-converter-physical-flow-run.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "analog-converter-physical-flow-run.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/converter-post-layout-readiness.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-readiness.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/converter-post-layout-evidence-contract.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-evidence-contract.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/converter-post-layout-payload-template.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-payload-template.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/converter-post-layout-payload-validator.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-payload-validator.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/converter-post-layout-break-even-rerun-path.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-break-even-rerun-path.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/converter-post-layout-strict-intake.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-strict-intake-report.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/converter-post-layout-positive-path.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-positive-path-report.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/converter-post-layout-submission-path.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-submission-path-report.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/converter-post-layout-real-payload-package.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-real-payload-package.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/converter-post-layout-payload-preflight.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-payload-preflight-report.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/converter-post-layout-candidate-workspace.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-workspace.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/converter-post-layout-candidate-workspace-audit.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-workspace-audit.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/converter-post-layout-candidate-fill-checklist.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-fill-checklist.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/converter-post-layout-candidate-progress-report.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-progress-report.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/converter-post-layout-candidate-progress-gate.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-progress-gate.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/converter-post-layout-candidate-preflight-gate.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-preflight-gate.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/converter-post-layout-candidate-submission-gate.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-submission-gate.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/converter-post-layout-candidate-readiness-run.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-readiness-run.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/converter-post-layout-handoff-manifest.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-handoff-manifest.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/converter-post-layout-blocker-ledger.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-blocker-ledger.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/converter-post-layout-candidate-edit-plan.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-edit-plan.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/converter-post-layout-same-run-gate.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-same-run-gate.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/converter-post-layout-candidate-identity-initializer.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-identity-initializer.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/converter-post-layout-real-candidate-builder.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-real-candidate-builder.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/converter-post-layout-submission-preview.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-submission-preview.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/converter-post-layout-evidence-leakage-audit.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-evidence-leakage-audit.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/converter-post-layout-temporary-submission-proof.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-temporary-submission-proof.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/converter-post-layout-real-artifact-discovery.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-real-artifact-discovery.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/converter-post-layout-real-run-recipe.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-real-run-recipe.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source.relative_to(ROOT).as_posix() == "docs/research/converter-post-layout-real-run-recipe-coverage.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-real-run-recipe-coverage.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source == ROOT / "docs" / "research" / "first-real-converter-same-candidate-extracted-rc.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "first-real-converter-same-candidate-extracted-rc.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source == ROOT / "docs" / "research" / "first-real-converter-frontend-to-input-stage-proxy.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "first-real-converter-frontend-to-input-stage-proxy.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source == ROOT / "docs" / "research" / "first-real-converter-frontend-active-handoff-estimate.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "first-real-converter-frontend-active-handoff-estimate.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source == ROOT / "docs" / "research" / "first-real-converter-combined-active-handoff-work-order.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "first-real-converter-combined-active-handoff-work-order.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source == ROOT / "docs" / "research" / "sky130-frontend-input-stage-handoff-candidate.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-frontend-input-stage-handoff-candidate.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source == ROOT / "docs" / "research" / "sky130-transistor-handoff-replacement-work-order.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-transistor-handoff-replacement-work-order.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source == ROOT / "docs" / "research" / "sky130-frontend-transistor-input-stage-handoff-candidate.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-frontend-transistor-input-stage-handoff-candidate.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source == ROOT / "docs" / "research" / "sky130-transistor-handoff-decomposition.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-transistor-handoff-decomposition.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source == ROOT / "docs" / "research" / "sky130-transistor-handoff-probe-ladder.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-transistor-handoff-probe-ladder.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source == ROOT / "docs" / "research" / "sky130-frontend-sense-to-transistor-op-handoff.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-frontend-sense-to-transistor-op-handoff.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source == ROOT / "docs" / "research" / "sky130-frontend-sense-to-transistor-short-transient.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-frontend-sense-to-transistor-short-transient.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source == ROOT / "docs" / "research" / "sky130-frontend-sense-to-transistor-ramp-startup.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-frontend-sense-to-transistor-ramp-startup.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source == ROOT / "docs" / "research" / "sky130-extracted-frontend-to-transistor-gate-startup.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-extracted-frontend-to-transistor-gate-startup.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source == ROOT / "docs" / "research" / "sky130-extracted-frontend-gate-coupling-sweep.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-extracted-frontend-gate-coupling-sweep.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source == ROOT / "docs" / "research" / "sky130-extracted-frontend-source-follower-handoff.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-extracted-frontend-source-follower-handoff.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source == ROOT / "docs" / "research" / "sky130-extracted-frontend-differential-preamp.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-extracted-frontend-differential-preamp.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source == ROOT / "docs" / "research" / "sky130-measured-sense-differential-preamp.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-measured-sense-differential-preamp.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source == ROOT / "docs" / "research" / "sky130-measured-sense-preamp-bias-sweep.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-measured-sense-preamp-bias-sweep.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source == ROOT / "docs" / "research" / "sky130-measured-sense-preamp-op-map.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-measured-sense-preamp-op-map.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source == ROOT / "docs" / "research" / "sky130-preamp-known-good-sanity-gap.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-preamp-known-good-sanity-gap.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source == ROOT / "docs" / "research" / "sky130-preamp-known-good-reproduction.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-preamp-known-good-reproduction.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source == ROOT / "docs" / "research" / "sky130-extracted-frontend-preamp-gain-sweep.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-extracted-frontend-preamp-gain-sweep.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source == ROOT / "docs" / "research" / "sky130-frontend-preamp-interface-redesign-target.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-frontend-preamp-interface-redesign-target.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source == ROOT / "docs" / "research" / "sky130-frontend-preamp-capacitance-budget.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-frontend-preamp-capacitance-budget.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source == ROOT / "docs" / "research" / "sky130-frontend-preamp-interface-work-order.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-frontend-preamp-interface-work-order.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source == ROOT / "docs" / "research" / "sky130-frontend-preamp-interface-candidate.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-frontend-preamp-interface-candidate.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source == ROOT / "docs" / "research" / "sky130-lower-waste-frontend-preamp-candidate.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-lower-waste-frontend-preamp-candidate.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source == ROOT / "docs" / "research" / "sky130-combined-coupling-waste-frontend-preamp-candidate.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-combined-coupling-waste-frontend-preamp-candidate.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source == ROOT / "docs" / "research" / "sky130-active-isolation-preamp-target.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-active-isolation-preamp-target.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source == ROOT / "docs" / "research" / "sky130-active-isolation-preamp-candidate.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-active-isolation-preamp-candidate.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source == ROOT / "docs" / "research" / "sky130-offset-calibrated-active-isolation-preamp.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-offset-calibrated-active-isolation-preamp.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source == ROOT / "docs" / "research" / "sky130-transistor-active-isolation-preamp.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-transistor-active-isolation-preamp.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source == ROOT / "docs" / "research" / "sky130-swapped-transistor-active-isolation-preamp.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-swapped-transistor-active-isolation-preamp.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source == ROOT / "docs" / "research" / "sky130-polarity-corrected-transistor-handoff.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-polarity-corrected-transistor-handoff.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source == ROOT / "docs" / "research" / "sky130-polarity-contract-latch-sar-risk.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-polarity-contract-latch-sar-risk.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source == ROOT / "docs" / "research" / "sky130-polarity-named-isolated-latch-work-order.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-polarity-named-isolated-latch-work-order.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source == ROOT / "docs" / "research" / "sky130-source-follower-isolated-latch-candidate.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-source-follower-isolated-latch-candidate.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source == ROOT / "docs" / "research" / "sky130-sampled-internal-decision-cap-latch-candidate.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-sampled-internal-decision-cap-latch-candidate.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source == ROOT / "docs" / "research" / "sky130-two-phase-preamp-latch-candidate.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-two-phase-preamp-latch-candidate.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source == ROOT / "docs" / "research" / "sky130-isolated-latch-debug-ladder.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-isolated-latch-debug-ladder.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source == ROOT / "docs" / "research" / "sky130-preamp-alone-latch-debug.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-preamp-alone-latch-debug.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source == ROOT / "docs" / "research" / "sky130-preamp-op-latch-debug.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-preamp-op-latch-debug.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source == ROOT / "docs" / "research" / "sky130-known-good-shape-preamp-op-latch-debug.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-known-good-shape-preamp-op-latch-debug.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source == ROOT / "docs" / "research" / "sky130-preamp-op-deck-diff-diagnosis.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-preamp-op-deck-diff-diagnosis.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source == ROOT / "docs" / "research" / "sky130-known-good-shape-preamp-transient-latch-debug.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-known-good-shape-preamp-transient-latch-debug.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source == ROOT / "docs" / "research" / "sky130-latch-alone-from-preamp-voltage-debug.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-latch-alone-from-preamp-voltage-debug.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source == ROOT / "docs" / "research" / "sky130-latch-alone-swapped-preamp-voltage-debug.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-latch-alone-swapped-preamp-voltage-debug.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source == ROOT / "docs" / "research" / "sky130-swapped-latch-clock-timing-debug.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-swapped-latch-clock-timing-debug.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source == ROOT / "docs" / "research" / "sky130-clocked-latch-output-convention-diagnostic.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-clocked-latch-output-convention-diagnostic.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source == ROOT / "docs" / "research" / "sky130-corrected-convention-sample-hold-latch-kickback.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-corrected-convention-sample-hold-latch-kickback.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source == ROOT / "docs" / "research" / "sky130-corrected-convention-capacitive-isolation-confirm.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-corrected-convention-capacitive-isolation-confirm.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    if source == ROOT / "docs" / "research" / "sky130-corrected-convention-isolation-range-stress.md":
        generated = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-corrected-convention-isolation-range-stress.md"
        if generated.exists():
            text = f"{text}\n\n---\n\n{generated.read_text(encoding='utf-8')}"
    title = title_from_markdown(text, source.stem)
    body = f'<article class="article-body">{markdown_to_html(text)}</article>'
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(page(title, kicker, f"Source: {source.relative_to(ROOT)}", body, nav_prefix), encoding="utf-8")
    return title, dest.name


def paper_card(paper: dict[str, object], has_note: bool) -> str:
    concept_links = " ".join(
        f'<a class="pill" href="concepts/{html.escape(str(concept))}.html">{html.escape(str(concept))}</a>'
        for concept in paper.get("related_concepts", [])
    )
    lab_links = " ".join(
        f'<span class="pill">{html.escape(str(lab))}</span>'
        for lab in paper.get("related_labs", [])
    )
    note_link = ""
    if has_note:
        note_link = f'<p><a href="papers/{html.escape(str(paper["slug"]))}.html">Read full paper note</a></p>'
    return f"""<article class="card">
<div class="k">{html.escape(str(paper["track"]))} · {html.escape(str(paper["year"]))}</div>
<h3>{html.escape(str(paper["title"]))}</h3>
<p><strong>Object:</strong> {html.escape(str(paper["object_controlled"]))}</p>
<p><strong>Constraint:</strong> {html.escape(str(paper["constraint"]))}</p>
<p><strong>Mathematical form:</strong> {html.escape(str(paper["mathematical_form"]))}</p>
<p><strong>Concrete method:</strong> {html.escape(str(paper["concrete_method"]))}</p>
<p><strong>Evidence:</strong> {html.escape(str(paper["evidence_artifact"]))}</p>
<p><strong>Failure boundary:</strong> {html.escape(str(paper["failure_boundary"]))}</p>
<p>{concept_links}</p>
<p>{lab_links}</p>
{note_link}
</article>"""


def main() -> None:
    SITE.mkdir(parents=True, exist_ok=True)
    concept_dir = SITE / "concepts"
    lab_dir = SITE / "labs"
    concept_dir.mkdir(parents=True, exist_ok=True)
    lab_dir.mkdir(parents=True, exist_ok=True)

    synthesis_title, _ = write_markdown_page(ROOT / "docs" / "synthesis.md", SITE / "synthesis.html", "chip design synthesis")
    paper_synthesis_title, _ = write_markdown_page(ROOT / "docs" / "paper-corpus-synthesis.md", SITE / "paper-synthesis.html", "20-paper synthesis")
    coverage_title, _ = write_markdown_page(ROOT / "docs" / "coverage-audit.md", SITE / "coverage-audit.html", "coverage audit")
    aimc_title, _ = write_markdown_page(ROOT / "docs" / "analog-in-memory-foundation-model-synthesis.md", SITE / "analog-in-memory-foundation-model-synthesis.html", "analog in-memory synthesis")

    concept_cards = []
    for source in sorted((ROOT / "docs" / "concepts").glob("*.md")):
        title, filename = write_markdown_page(source, concept_dir / f"{slug(source)}.html", "first-principles concept", "../")
        concept_cards.append(f'<article class="card"><h3><a href="concepts/{filename}">{html.escape(title)}</a></h3><p>{html.escape(str(source.relative_to(ROOT)))}</p></article>')

    lab_cards = []
    for source in sorted((ROOT / "labs").glob("*/*/README.md")):
        lab_slug = "-".join(source.parts[-3:-1])
        title, filename = write_markdown_page(source, lab_dir / f"{lab_slug}.html", "chip design lab", "../")
        lab_cards.append(f'<article class="card"><h3><a href="labs/{filename}">{html.escape(title)}</a></h3><p>{html.escape(str(source.parent.relative_to(ROOT)))}</p></article>')

    research_dir = SITE / "research"
    research_dir.mkdir(parents=True, exist_ok=True)
    research_cards = []
    for source in sorted((ROOT / "docs" / "research").glob("*.md")):
        title, filename = write_markdown_page(source, research_dir / f"{slug(source)}.html", "research map", "../")
        research_cards.append(f'<article class="card"><h3><a href="research/{filename}">{html.escape(title)}</a></h3><p>{html.escape(str(source.relative_to(ROOT)))}</p></article>')

    concepts_body = f'<section class="section"><h2>Concept Articles</h2><div class="grid">{"".join(concept_cards)}</div></section>'
    (SITE / "concepts.html").write_text(page("Concept Atlas", f"{len(concept_cards)} first-principles articles", "Analog, digital, and EDA concepts organized by the object being controlled.", concepts_body), encoding="utf-8")

    labs_body = f'<section class="section"><h2>Lab Guides</h2><div class="grid">{"".join(lab_cards)}</div></section>'
    (SITE / "labs.html").write_text(page("Lab Track", f"{len(lab_cards)} practical labs", "SPICE, Verilog, synthesis, timing, layout verification, and analog in-memory compute guides.", labs_body), encoding="utf-8")

    research_body = f'<section class="section"><h2>Research Maps</h2><div class="grid">{"".join(research_cards)}</div></section>'
    (SITE / "research.html").write_text(page("Research Maps", "paper and tool taxonomy", "How future chip-design papers, tools, and labs should be read into the corpus.", research_body), encoding="utf-8")

    paper_note_dir = SITE / "papers"
    paper_note_dir.mkdir(parents=True, exist_ok=True)
    paper_note_slugs = set()
    for source in sorted((ROOT / "docs" / "papers").glob("*.md")):
        if source.name == "paper-note-template.md":
            continue
        write_markdown_page(source, paper_note_dir / f"{slug(source)}.html", "paper note", "../")
        paper_note_slugs.add(slug(source))

    papers = json.loads((ROOT / "sources" / "papers" / "seed-paper-index.json").read_text(encoding="utf-8"))
    paper_cards = "".join(paper_card(paper, str(paper["slug"]) in paper_note_slugs) for paper in papers)
    papers_body = f'<section class="section"><h2>Seed Paper Index</h2><p class="lead">These are starter paper targets. They are not yet a complete corpus; they define how each paper will be read into the project.</p><div class="grid">{paper_cards}</div></section>'
    (SITE / "papers.html").write_text(page("Paper Index", "seed paper intake", "First-principles paper entries organized by object, constraint, method, evidence, and failure boundary.", papers_body), encoding="utf-8")

    aimc_review_body = """<section class="section"><h2>AIMC Review Path</h2><p class="lead">Read this path as one proof chain: model placement, simulator evidence, converter requirements, Sky130 frontend evidence, active handoff, failed transistor handoff, and the strict gate that still blocks accepted converter evidence.</p><div class="grid">
<article class="card"><h3><a href="research/cross-repo-aimc-loop-proof.html">1. Cross-Repo Loop Proof</a></h3><p>Start with the current executable proof: backend placement, simulator payloads, RTL, evidence import, residual-aware placement, archive, and claim readiness.</p></article>
<article class="card"><h3><a href="research/aimc-end-to-end-proof-explanation.html">2. End-To-End Proof Explanation</a></h3><p>Read the plain-language chain from model operation to analog signal, converter decision, digital trust boundary, and remaining proof gaps.</p></article>
<article class="card"><h3><a href="research/aimc-remaining-proof-spine.html">2b. AIMC Remaining Proof Spine</a></h3><p>Tie the latest Sky130 isolated-latch evidence back to the model, simulator, converter, layout, strict-payload, and placement goals.</p></article>
<article class="card"><h3><a href="research/current-aimc-system-state.html">3. Current System State</a></h3><p>Read the short source-backed answer for what is supported, needs review, and blocked right now.</p></article>
<article class="card"><h3><a href="research/onnx-fixture-inventory.html">4. ONNX Fixture Inventory</a></h3><p>Review the actual local model slices and the current best fixed-weight MatMul fixture before replacing it with a real uploaded model slice.</p></article>
<article class="card"><h3><a href="research/simulator-to-placement-decision-boundary.html">5. Simulator To Placement Decision</a></h3><p>See why AIHWKIT/CrossSim payloads do not automatically become analog placement permission.</p></article>
<article class="card"><h3><a href="research/aihwkit-residual-diagnostic.html">5. AIHWKIT Residual Diagnostic</a></h3><p>Review which AIHWKIT payload rows exceed the positive residual boundary before changing the mapping.</p></article>
<article class="card"><h3><a href="research/aihwkit-ideal-forward-mapping-proof.html">6. AIHWKIT Ideal Forward Mapping</a></h3><p>Confirm that AIHWKIT receives the right MatMul object before tuning non-perfect forward behavior.</p></article>
<article class="card"><h3><a href="research/aihwkit-forward-setting-sweep.html">7. AIHWKIT Forward Setting Sweep</a></h3><p>Compare bounded AIHWKIT forward settings before choosing a physically defensible mapping.</p></article>
<article class="card"><h3><a href="research/aihwkit-physical-setting-review.html">8. AIHWKIT Physical Setting Review</a></h3><p>Check whether the passing AIHWKIT setting matches the local converter and noise boundary.</p></article>
<article class="card"><h3><a href="research/aihwkit-current-tile-boundary-replay.html">9. AIHWKIT Current Tile Replay</a></h3><p>Check what the existing 4-bit DAC and 6-bit ADC tile boundary does to the same rows.</p></article>
<article class="card"><h3><a href="research/aihwkit-converter-upgrade-target.html">10. AIHWKIT Converter Upgrade Target</a></h3><p>Turn the current-tile failure and passing fine-resolution setting into a concrete 10-bit input and 12-bit output design target.</p></article>
<article class="card"><h3><a href="research/aihwkit-converter-cost-model.html">11. AIHWKIT Converter Cost Model</a></h3><p>Estimate what the 10-bit input and 12-bit output target costs before treating it as analog placement permission.</p></article>
<article class="card"><h3><a href="research/aihwkit-target-noise-sensitivity.html">12. AIHWKIT Target Noise Sensitivity</a></h3><p>Check whether the 10-bit input and 12-bit output target survives small nonzero output noise.</p></article>
<article class="card"><h3><a href="research/aihwkit-converter-break-even.html">13. AIHWKIT Converter Break-Even</a></h3><p>Ask how much useful analog array work must be served before the 10-bit input and 12-bit output converter target is worth paying for.</p></article>
<article class="card"><h3><a href="research/converter-circuit-evidence-contract.html">14. Converter Circuit Evidence Contract</a></h3><p>Define the ADC/DAC energy, latency, noise, area, and sharing fields needed before break-even assumptions can be replaced.</p></article>
<article class="card"><h3><a href="research/local-converter-circuit-estimate.html">15. Local Converter Circuit Estimate</a></h3><p>Fill the converter evidence fields with explicit local planning numbers while keeping the claim boundary closed.</p></article>
<article class="card"><h3><a href="research/converter-circuit-simulation-estimate.html">16. Converter Circuit-Simulation Estimate</a></h3><p>Check the 10-bit row-drive and 12-bit readout target with explicit settling, quantization, noise, latency, energy, and sharing terms.</p></article>
<article class="card"><h3><a href="research/converter-spice-handoff-spec.html">17. Converter SPICE Handoff Spec</a></h3><p>Define the transistor-level converter testbenches that must replace behavioral settling, noise, latency, energy, and sharing terms.</p></article>
<article class="card"><h3><a href="research/row-dac-settling-spice-evidence.html">18. Row-DAC Settling SPICE Evidence</a></h3><p>Execute the first converter SPICE handoff test and check whether the 10-bit row-drive load settles within half of one code step.</p></article>
<article class="card"><h3><a href="research/sar-readout-spice-evidence.html">19. SAR Readout SPICE Evidence</a></h3><p>Execute the second converter SPICE handoff test and check whether the 12-bit readout sample settles within half of one ADC step.</p></article>
<article class="card"><h3><a href="research/shared-converter-loading-spice-evidence.html">20. Shared Converter Loading SPICE Evidence</a></h3><p>Execute the third converter SPICE handoff test and check whether shared mux loading still settles within half of one ADC step.</p></article>
<article class="card"><h3><a href="research/converter-supply-energy-spice-evidence.html">21. Converter Supply Energy SPICE Evidence</a></h3><p>Execute the fourth converter SPICE handoff test and integrate row-drive, ADC-reference, and mux energy on a named rail.</p></article>
<article class="card"><h3><a href="research/digital-physical-artifact-boundary.html">22. Digital Physical Artifact Boundary</a></h3><p>Separate completed digital OpenLane artifacts from the still-missing analog converter post-layout package.</p></article>
<article class="card"><h3><a href="research/simulator-to-post-layout-gap-audit.html">23. Simulator To Post-Layout Gap</a></h3><p>Show why AIHWKIT and CrossSim residual evidence does not by itself supply extracted converter energy, latency, noise, or area.</p></article>
<article class="card"><h3><a href="research/analog-converter-layout-work-order.html">24. Analog Converter Layout Work Order</a></h3><p>Turn the existing converter SPICE decks into layout, extraction, measurement, and rerun deliverables.</p></article>
<article class="card"><h3><a href="research/analog-converter-layout-starter-package.html">25. Analog Converter Layout Starter Package</a></h3><p>Create the source-side workbench files for drawing, extracting, measuring, and rerunning the converter package.</p></article>
<article class="card"><h3><a href="research/analog-converter-layout-tool-readiness.html">26. Analog Converter Layout Tool Readiness</a></h3><p>Check the local layout tools, starter files, and remaining missing physical converter files.</p></article>
<article class="card"><h3><a href="research/analog-converter-pdk-readiness.html">27. Analog Converter PDK Readiness</a></h3><p>Check the named Sky130 files needed for Magic extraction and ngspice post-layout simulation.</p></article>
<article class="card"><h3><a href="research/magic-sky130-extraction-smoke.html">28. Magic Sky130 Extraction Smoke</a></h3><p>Check whether local Magic can load Sky130 and extract a tiny non-converter cell.</p></article>
<article class="card"><h3><a href="research/magic-sky130-compatibility.html">29. Magic Sky130 Compatibility</a></h3><p>Record whether the local Magic binary is compatible enough for Sky130 extraction.</p></article>
<article class="card"><h3><a href="research/row-dac-10b-layout-smoke.html">30. Row DAC 10b Layout Smoke</a></h3><p>Extract the first named row-DAC starter cell without treating it as accepted converter evidence.</p></article>
<article class="card"><h3><a href="research/converter-starter-layout-smoke.html">31. Converter Starter Layout Smoke</a></h3><p>Extract all four named converter starter cells while keeping candidate evidence empty.</p></article>
<article class="card"><h3><a href="research/converter-starter-post-layout-candidate.html">32. Converter Starter Post-Layout Candidate</a></h3><p>Build a strict preflight-ready packet from the extracted starter macro while refusing accepted evidence.</p></article>
<article class="card"><h3><a href="research/converter-starter-physical-artifacts.html">33. Converter Starter Physical Artifacts</a></h3><p>Inspect the starter Magic cells, extracted files, SPICE outputs, and layout-box area without upgrading the claim.</p></article>
<article class="card"><h3><a href="research/converter-starter-parasitic-load-estimate.html">34. Converter Starter Parasitic Load Estimate</a></h3><p>Use extracted starter capacitances to estimate pin charge energy and first-order RC settling without claiming converter proof.</p></article>
<article class="card"><h3><a href="research/converter-starter-parasitic-break-even-rerun.html">35. Converter Starter Parasitic Break-Even Rerun</a></h3><p>Add the extracted starter capacitance cost to break-even scenarios without replacing real converter evidence.</p></article>
<article class="card"><h3><a href="research/converter-starter-extracted-rc-ngspice.html">36. Converter Starter Extracted RC Ngspice</a></h3><p>Run ngspice on the Magic-extracted starter macro capacitance network without claiming transistor converter proof.</p></article>
<article class="card"><h3><a href="research/sky130-transistor-sample-switch-ngspice.html">37. Sky130 Transistor Sample Switch Ngspice</a></h3><p>Run a Sky130 MOS transmission-gate sample path and check on-state sample error without claiming a full converter.</p></article>
<article class="card"><h3><a href="research/sky130-sample-switch-hold-mode-ngspice.html">38. Sky130 Sample Switch Hold Mode Ngspice</a></h3><p>Measure held-node movement after the Sky130 sample switch turns off and expose the next circuit issue.</p></article>
<article class="card"><h3><a href="research/sky130-sample-switch-hold-mitigation-sweep.html">39. Sky130 Sample Switch Hold Mitigation Sweep</a></h3><p>Test whether larger sample capacitance or switch resizing reduces Sky130 hold-mode error enough.</p></article>
<article class="card"><h3><a href="research/sky130-sample-switch-dummy-cancellation-ngspice.html">40. Sky130 Sample Switch Dummy Cancellation Ngspice</a></h3><p>Test whether opposite-clock dummy devices can cancel Sky130 sample-switch hold error.</p></article>
<article class="card"><h3><a href="research/sky130-bottom-plate-sampling-ngspice.html">41. Sky130 Bottom Plate Sampling Ngspice</a></h3><p>Test whether bottom-plate clock ordering reduces stored-voltage movement in a Sky130 sample-and-hold fixture.</p></article>
<article class="card"><h3><a href="research/sky130-sample-hold-topology-decision-gate.html">42. Sky130 Sample-Hold Topology Decision Gate</a></h3><p>Read the measured sample-switch evidence as one decision about the next converter sample-and-hold topology.</p></article>
<article class="card"><h3><a href="research/sky130-buffered-sample-hold-ngspice.html">43. Sky130 Buffered Sample-Hold Ngspice</a></h3><p>Test a naive Sky130 source-follower readout buffer and record whether it gives stable sample-hold evidence.</p></article>
<article class="card"><h3><a href="research/sky130-bootstrapped-switch-ngspice.html">44. Sky130 Bootstrapped Switch Ngspice</a></h3><p>Test an idealized input-referenced bootstrapped switch and record whether it gives stable sample-hold evidence.</p></article>
<article class="card"><h3><a href="research/sky130-fully-differential-sampling-ngspice.html">45. Sky130 Fully Differential Sampling Ngspice</a></h3><p>Test matched Sky130 differential sampling and record whether the decision voltage is more stable than each held node.</p></article>
<article class="card"><h3><a href="research/differential-sampling-control-proof-ngspice.html">46. Differential Sampling Control Proof Ngspice</a></h3><p>Use an ideal-switch control proof to separate differential cancellation math from Sky130 transistor deck stability.</p></article>
<article class="card"><h3><a href="research/sky130-single-device-charge-injection-ngspice.html">47. Sky130 Single-Device Charge Injection Ngspice</a></h3><p>Reduce the Sky130 hold disturbance problem to one nfet gate edge and record whether it is measurable.</p></article>
<article class="card"><h3><a href="research/sky130-sample-switch-clock-edge-sweep.html">48. Sky130 Sample Switch Clock Edge Sweep</a></h3><p>Keep the known Sky130 transmission-gate topology and test whether clock edge timing gives stable hold evidence.</p></article>
<article class="card"><h3><a href="research/sky130-sample-hold-design-target.html">49. Sky130 Sample-Hold Design Target</a></h3><p>Convert measured hold error into the reduction, cancellation, and capacitance target for the next circuit.</p></article>
<article class="card"><h3><a href="research/sky130-differential-matching-requirement.html">50. Sky130 Differential Matching Requirement</a></h3><p>Convert the hold-error target into the allowed mismatch and common-rejection target for differential sampling.</p></article>
<article class="card"><h3><a href="research/sky130-next-transistor-fixture-work-order.html">51. Sky130 Next Transistor Fixture Work Order</a></h3><p>Define the next measurable Sky130 transistor fixture, acceptance tests, and claim boundary.</p></article>
<article class="card"><h3><a href="research/sky130-comparator-acceptance-fixture-spec.html">52. Sky130 Comparator Acceptance Fixture Spec</a></h3><p>Turn the measured sample-hold and offset/noise budget into a concrete Sky130 comparator test contract.</p></article>
<article class="card"><h3><a href="research/sky130-comparator-input-stage-ngspice.html">53. Sky130 Comparator Input-Stage Ngspice</a></h3><p>Run a Sky130 transistor differential input-stage polarity proxy against the tiny comparator budget.</p></article>
<article class="card"><h3><a href="research/sky130-clocked-comparator-latch-ngspice.html">54. Sky130 Clocked Comparator Latch Ngspice</a></h3><p>Run a first Sky130 clocked latch proxy at the measured comparator target edge.</p></article>
<article class="card"><h3><a href="research/sky130-sample-hold-latch-kickback-ngspice.html">55. Sky130 Sample-Hold Latch Kickback Ngspice</a></h3><p>Connect the passing sample-hold candidate to the clocked latch and measure sampled-node kickback.</p></article>
<article class="card"><h3><a href="research/sky130-latch-input-size-kickback-sweep.html">56. Sky130 Latch Input-Size Kickback Sweep</a></h3><p>Sweep latch input width to see whether smaller devices reduce sampled-node kickback enough.</p></article>
<article class="card"><h3><a href="research/sky130-comparator-isolation-target.html">57. Sky130 Comparator Isolation Target</a></h3><p>Convert measured latch kickback failures into the required sampled-node isolation target.</p></article>
<article class="card"><h3><a href="research/sky130-capacitive-latch-input-isolation-sweep.html">58. Sky130 Capacitive Latch Input Isolation Sweep</a></h3><p>Sweep capacitive isolation between held nodes and latch gates to reduce kickback.</p></article>
<article class="card"><h3><a href="research/sky130-capacitive-isolation-both-polarity-confirm.html">59. Sky130 Capacitive Isolation Both-Polarity Confirm</a></h3><p>Confirm the passing capacitive-isolation candidates in both target-edge input directions.</p></article>
<article class="card"><h3><a href="research/sky130-capacitive-isolation-post-layout-handoff.html">60. Sky130 Capacitive Isolation Post-Layout Handoff</a></h3><p>Turn the confirmed schematic isolation candidate into a strict extracted-layout handoff without accepting it as post-layout evidence.</p></article>
<article class="card"><h3><a href="research/sky130-capacitive-isolation-physical-cell-gap.html">61. Sky130 Capacitive Isolation Physical Cell Gap</a></h3><p>Audit the exact layout, extracted netlist, model, rerun, and DRC/LVS files still missing for the confirmed isolation candidate.</p></article>
<article class="card"><h3><a href="research/sky130-capacitive-isolation-post-layout-both-polarity.html">62. Sky130 Capacitive Isolation Post-Layout Both-Polarity</a></h3><p>Rerun both input signs through the Magic-extracted RC frontend and record why the starter cell is not yet confirmed.</p></article>
<article class="card"><h3><a href="research/sky130-capacitive-isolation-extracted-port-mapping-diagnostic.html">63. Sky130 Capacitive Isolation Extracted Port Mapping</a></h3><p>Remove the latch and test whether any extracted frontend port mapping preserves the sampled differential sign.</p></article>
<article class="card"><h3><a href="research/sky130-capacitive-isolation-extracted-coupling-strength-sweep.html">64. Sky130 Capacitive Isolation Extracted Coupling Strength</a></h3><p>Measure whether stronger intended sample-to-gate coupling can overcome the extracted frontend sign error.</p></article>
<article class="card"><h3><a href="research/sky130-extracted-frontend-redesign-target.html">65. Sky130 Extracted Frontend Redesign Target</a></h3><p>Convert the extracted sign failure into a measurable physical redesign target before accepted evidence.</p></article>
<article class="card"><h3><a href="research/sky130-balanced-frontend-work-order.html">66. Sky130 Balanced Frontend Work Order</a></h3><p>Define the next buildable Sky130 frontend candidate, ports, topology moves, and acceptance checks.</p></article>
<article class="card"><h3><a href="research/sky130-balanced-frontend-starter-extraction.html">67. Sky130 Balanced Frontend Starter Extraction</a></h3><p>Extract the new balanced starter cell and check first-order sense-node capacitance symmetry.</p></article>
<article class="card"><h3><a href="research/sky130-balanced-frontend-sign-preservation.html">68. Sky130 Balanced Frontend Sign Preservation</a></h3><p>Drive the extracted balanced starter cell and check whether the sense nodes preserve both input signs.</p></article>
<article class="card"><h3><a href="research/sky130-balanced-frontend-latch-decision.html">69. Sky130 Balanced Frontend Latch Decision</a></h3><p>Compare the extracted sense-node signal against the latch proxy input needed for a digital decision.</p></article>
<article class="card"><h3><a href="research/sky130-balanced-frontend-sense-gain-target.html">70. Sky130 Balanced Frontend Sense Gain Target</a></h3><p>Turn the measured sense-node shortfall into the next physical frontend gain target.</p></article>
<article class="card"><h3><a href="research/sky130-strong-sense-frontend-candidate.html">71. Sky130 Strong Sense Frontend Candidate</a></h3><p>Extract and measure a closer-spaced sample-to-sense frontend against the sense-gain target.</p></article>
<article class="card"><h3><a href="research/sky130-ultra-sense-frontend-candidate.html">72. Sky130 Ultra Sense Frontend Candidate</a></h3><p>Extract and measure a larger mirrored sample-to-sense frontend against the remaining latch-transfer gap.</p></article>
<article class="card"><h3><a href="research/sky130-frontend-sense-efficiency-audit.html">73. Sky130 Frontend Sense Efficiency Audit</a></h3><p>Compare balanced, strong, and ultra extracted frontends to show why transfer rises slower than direct coupling.</p></article>
<article class="card"><h3><a href="research/comparator-decision-margin-from-first-principles.html">74. Comparator Decision Margin From First Principles</a></h3><p>Explain why sign preservation is weaker than a real comparator decision against offset, noise, kickback, and timing.</p></article>
<article class="card"><h3><a href="research/passive-frontend-vs-active-preamp.html">75. Passive Frontend Vs Active Preamp</a></h3><p>Define the next circuit fork: preserve the small signal passively or spend active power to amplify it before the latch.</p></article>
<article class="card"><h3><a href="research/converter-evidence-ladder.html">76. Converter Evidence Ladder</a></h3><p>Separate schematic SPICE, extraction, DRC/LVS, post-layout simulation, measured silicon, and accepted evidence.</p></article>
<article class="card"><h3><a href="research/analog-to-digital-to-model-error-flow.html">77. Analog-To-Digital-To-Model Error Flow</a></h3><p>Show how converter error becomes ADC code error, corrected residual, model-state risk, and accept-or-fallback behavior.</p></article>
<article class="card"><h3><a href="research/final-accepted-converter-gate.html">78. Final Accepted Converter Gate</a></h3><p>Define the exact same-run payload, strict submission, break-even rerun, and claim update that closes converter acceptance.</p></article>
<article class="card"><h3><a href="research/from-active-macro-to-real-transistor-handoff.html">79. From Active Macro To Real Transistor Handoff</a></h3><p>Explain why the active-macro handoff passed, why it is not enough, and what real Sky130 transistor handoff must prove.</p></article>
<article class="card"><h3><a href="research/sky130-transistor-handoff-decomposition.html">80. Sky130 Transistor Handoff Decomposition</a></h3><p>Separate frontend, standalone input-stage, macro-handoff, and real-transistor combined-deck evidence before the next circuit debug.</p></article>
<article class="card"><h3><a href="research/sky130-transistor-handoff-probe-ladder.html">81. Sky130 Transistor Handoff Probe Ladder</a></h3><p>Run smaller one-case probes that isolate transient, loading, frontend, and real-gate handoff behavior.</p></article>
<article class="card"><h3><a href="research/sky130-frontend-sense-to-transistor-op-handoff.html">82. Sky130 Frontend Sense To Transistor OP Handoff</a></h3><p>Feed measured frontend sense voltages into the real Sky130 input pair as a solvable operating-point handoff.</p></article>
<article class="card"><h3><a href="research/sky130-frontend-sense-to-transistor-short-transient.html">83. Sky130 Frontend Sense To Transistor Short Transient</a></h3><p>Start from the measured OP state and check whether output sign and margin survive a short local transient.</p></article>
<article class="card"><h3><a href="research/sky130-frontend-sense-to-transistor-ramp-startup.html">84. Sky130 Frontend Sense To Transistor Ramp Startup</a></h3><p>Ramp the real Sky130 input-pair gates from common-mode to the measured frontend sense voltages.</p></article>
<article class="card"><h3><a href="research/sky130-extracted-frontend-to-transistor-gate-startup.html">85. Sky130 Extracted Frontend To Transistor Gate Startup</a></h3><p>Run the extracted frontend and real transistor gates in one measured assisted-startup deck.</p></article>
<article class="card"><h3><a href="research/sky130-extracted-frontend-gate-coupling-sweep.html">86. Sky130 Extracted Frontend Gate Coupling Sweep</a></h3><p>Sweep assisted gate coupling and prebias strength to see whether passive tuning fixes the handoff.</p></article>
<article class="card"><h3><a href="research/sky130-extracted-frontend-source-follower-handoff.html">87. Sky130 Extracted Frontend Source-Follower Handoff</a></h3><p>Test whether a simple Sky130 source-follower buffer protects the extracted frontend signal.</p></article>
<article class="card"><h3><a href="research/sky130-extracted-frontend-differential-preamp.html">88. Sky130 Extracted Frontend Differential Preamp</a></h3><p>Test whether a biased Sky130 differential preamp can read the extracted frontend directly.</p></article>
<article class="card"><h3><a href="research/sky130-measured-sense-differential-preamp.html">89. Sky130 Measured Sense Differential Preamp</a></h3><p>Remove the extracted frontend and test whether the preamp bias can resolve measured sense voltages.</p></article>
<article class="card"><h3><a href="research/sky130-measured-sense-preamp-bias-sweep.html">90. Sky130 Measured Sense Preamp Bias Sweep</a></h3><p>Sweep preamp bias with measured sense voltages before reconnecting the extracted frontend.</p></article>
<article class="card"><h3><a href="research/sky130-measured-sense-preamp-op-map.html">91. Sky130 Measured Sense Preamp OP Map</a></h3><p>Map DC preamp bias points before spending more time on transient startup.</p></article>
<article class="card"><h3><a href="research/sky130-preamp-known-good-sanity-gap.html">92. Sky130 Preamp Known-Good Sanity Gap</a></h3><p>Compare the passing input-stage primitive with the failing measured-sense preamp OP deck.</p></article>
<article class="card"><h3><a href="research/sky130-preamp-known-good-reproduction.html">93. Sky130 Preamp Known-Good Reproduction</a></h3><p>Rerun the exact known-good input-stage deck at the prior target input and the smaller measured frontend input.</p></article>
<article class="card"><h3><a href="research/sky130-extracted-frontend-preamp-gain-sweep.html">94. Sky130 Extracted Frontend Preamp Gain Sweep</a></h3><p>Sweep simple preamp gain while attached to the extracted frontend and test whether output margin can be recovered.</p></article>
<article class="card"><h3><a href="research/sky130-frontend-preamp-interface-redesign-target.html">95. Sky130 Frontend Preamp Interface Redesign Target</a></h3><p>Convert the attached-preamp margin failure into the voltage-transfer improvement required before latch work.</p></article>
<article class="card"><h3><a href="research/sky130-frontend-preamp-capacitance-budget.html">96. Sky130 Frontend Preamp Capacitance Budget</a></h3><p>Turn the interface transfer target into useful coupling, wasted capacitance, and physical redesign choices.</p></article>
<article class="card"><h3><a href="research/sky130-frontend-preamp-interface-work-order.html">97. Sky130 Frontend Preamp Interface Work Order</a></h3><p>Name the concrete frontend-to-preamp redesign candidates and their acceptance tests.</p></article>
<article class="card"><h3><a href="research/sky130-frontend-preamp-interface-candidate.html">98. Sky130 Frontend Preamp Interface Candidate</a></h3><p>Rank the frontend-to-preamp candidate moves by the measured physical change still needed.</p></article>
<article class="card"><h3><a href="research/sky130-lower-waste-frontend-preamp-candidate.html">99. Sky130 Lower-Waste Frontend Preamp Candidate</a></h3><p>Test whether reducing non-signal sense capacitance to the budget target is enough for the attached preamp.</p></article>
<article class="card"><h3><a href="research/sky130-combined-coupling-waste-frontend-preamp-candidate.html">100. Sky130 Combined Coupling/Waste Frontend Preamp Candidate</a></h3><p>Test whether useful-coupling increase plus wasted-capacitance reduction is enough for the attached preamp.</p></article>
<article class="card"><h3><a href="research/sky130-active-isolation-preamp-target.html">101. Sky130 Active Isolation Preamp Target</a></h3><p>Turn the passive and source-follower failures into numeric requirements for the next active isolation candidate.</p></article>
<article class="card"><h3><a href="research/sky130-active-isolation-preamp-candidate.html">102. Sky130 Active Isolation Preamp Candidate</a></h3><p>Sweep a low-input-capacitance active isolation macro before the Sky130 preamp and expose the remaining balance problem.</p></article>
<article class="card"><h3><a href="research/sky130-offset-calibrated-active-isolation-preamp.html">103. Sky130 Offset-Calibrated Active Isolation Preamp</a></h3><p>Subtract the zero-input output from the active-isolation macro handoff and test both signs against margin.</p></article>
<article class="card"><h3><a href="research/sky130-transistor-active-isolation-preamp.html">104. Sky130 Transistor Active Isolation Preamp</a></h3><p>Replace the ideal isolation macro with a Sky130 transistor isolation pair and expose the remaining polarity issue.</p></article>
<article class="card"><h3><a href="research/sky130-swapped-transistor-active-isolation-preamp.html">105. Sky130 Swapped Transistor Active Isolation Preamp</a></h3><p>Test whether the transistor polarity failure is fixed by swapping isolation outputs into the preamp.</p></article>
<article class="card"><h3><a href="research/sky130-polarity-corrected-transistor-handoff.html">106. Sky130 Polarity-Corrected Transistor Handoff</a></h3><p>Apply an explicit converter polarity contract to the measured transistor handoff and check sign plus margin.</p></article>
<article class="card"><h3><a href="research/sky130-polarity-contract-latch-sar-risk.html">107. Sky130 Polarity Contract Latch/SAR Risk</a></h3><p>Join the polarity-corrected transistor handoff to latch kickback evidence and name the isolated decision target.</p></article>
<article class="card"><h3><a href="research/sky130-polarity-named-isolated-latch-work-order.html">108. Sky130 Polarity-Named Isolated Latch Work Order</a></h3><p>Turn the polarity contract and latch kickback blocker into the next isolated-latch circuit target.</p></article>
<article class="card"><h3><a href="research/sky130-source-follower-isolated-latch-candidate.html">109. Sky130 Source-Follower Isolated Latch Candidate</a></h3><p>Test the first isolated-latch candidate by buffering sampled nodes with Sky130 source followers before the latch.</p></article>
<article class="card"><h3><a href="research/sky130-sampled-internal-decision-cap-latch-candidate.html">110. Sky130 Sampled Internal Decision-Cap Latch Candidate</a></h3><p>Test whether copying the value to small internal decision capacitors isolates sampled nodes from latch kickback.</p></article>
<article class="card"><h3><a href="research/sky130-two-phase-preamp-latch-candidate.html">111. Sky130 Two-Phase Preamp-Then-Latch Candidate</a></h3><p>Test whether a quiet preamp phase before latch regeneration can preserve resolution while reducing sampled-node kickback.</p></article>
<article class="card"><h3><a href="research/sky130-isolated-latch-debug-ladder.html">112. Sky130 Isolated Latch Debug Ladder</a></h3><p>Split the timeout-heavy isolated latch failures into preamp-alone, latch-alone, clock, coupled, and SAR-threshold checks.</p></article>
<article class="card"><h3><a href="research/sky130-preamp-alone-latch-debug.html">113. Sky130 Preamp-Alone Latch Debug</a></h3><p>Run the first debug-ladder step by removing the regenerative latch and testing preamp transient settling alone.</p></article>
<article class="card"><h3><a href="research/sky130-preamp-op-latch-debug.html">114. Sky130 Preamp OP Latch Debug</a></h3><p>Remove transient startup and test whether the preamp bias has a DC operating point at the target-edge inputs.</p></article>
<article class="card"><h3><a href="research/sky130-known-good-shape-preamp-op-latch-debug.html">115. Sky130 Known-Good-Shape Preamp OP Latch Debug</a></h3><p>Rerun the exact known-good preamp OP deck shape for both target-edge signs.</p></article>
<article class="card"><h3><a href="research/sky130-preamp-op-deck-diff-diagnosis.html">116. Sky130 Preamp OP Deck-Diff Diagnosis</a></h3><p>Compare prior known-good OP evidence with the current known-good-shape rerun and name the executable blocker.</p></article>
<article class="card"><h3><a href="research/sky130-known-good-shape-preamp-transient-latch-debug.html">117. Sky130 Known-Good-Shape Preamp Transient Latch Debug</a></h3><p>Start from the OP-measured initial point and prove the preamp transient settles before latch reconnection.</p></article>
<article class="card"><h3><a href="research/sky130-latch-alone-from-preamp-voltage-debug.html">118. Sky130 Latch-Alone From Preamp Voltage Debug</a></h3><p>Drive the latch from measured preamp voltages and test resolution before reintroducing sampled-node kickback.</p></article>
<article class="card"><h3><a href="research/sky130-latch-alone-swapped-preamp-voltage-debug.html">119. Sky130 Latch-Alone Swapped Preamp Voltage Debug</a></h3><p>Swap the measured preamp voltages into the latch input and verify latch-alone polarity resolution.</p></article>
<article class="card"><h3><a href="research/sky130-swapped-latch-clock-timing-debug.html">120. Sky130 Swapped Latch Clock Timing Debug</a></h3><p>Sweep latch enable timing with the swapped measured-preamp mapping and show the sign convention still blocks coupled-kickback work.</p></article>
<article class="card"><h3><a href="research/sky130-clocked-latch-output-convention-diagnostic.html">121. Sky130 Clocked Latch Output Convention Diagnostic</a></h3><p>Reinterpret the measured clocked-latch rails and name the digital output convention that matches the source polarity contract.</p></article>
<article class="card"><h3><a href="research/sky130-corrected-convention-sample-hold-latch-kickback.html">122. Sky130 Corrected-Convention Sample-Hold Latch Kickback</a></h3><p>Reconnect the latch to sampled nodes with the corrected output convention and measure the remaining coupled-kickback blocker.</p></article>
<article class="card"><h3><a href="research/sky130-corrected-convention-capacitive-isolation-confirm.html">123. Sky130 Corrected-Convention Capacitive Isolation Confirm</a></h3><p>Use tiny capacitive latch-input isolation to preserve both signs while keeping sampled-node kickback below the 12-bit half-LSB line.</p></article>
<article class="card"><h3><a href="research/sky130-corrected-convention-isolation-range-stress.html">124. Sky130 Corrected-Convention Isolation Range Stress</a></h3><p>Stress the tiny capacitive-isolation branch across both signs and three input magnitudes before noise, timing, or layout claims.</p></article>
<article class="card"><h3><a href="research/analog-converter-sky130-workbench-env.html">Support A. Analog Converter Sky130 Workbench Environment</a></h3><p>Write local Magic, xschem, and ngspice setup files for the converter layout workbench.</p></article>
<article class="card"><h3><a href="research/analog-converter-physical-cell-gate.html">Support B. Analog Converter Physical Cell Gate</a></h3><p>Check that the named converter layout cells exist before any post-layout payload can be trusted.</p></article>
<article class="card"><h3><a href="research/analog-converter-physical-flow-run.html">Support C. Analog Converter Physical Flow Run</a></h3><p>Name the extraction commands that stay blocked until the converter cells exist.</p></article>
<article class="card"><h3><a href="research/converter-post-layout-readiness.html">Support D. Converter Post-Layout Readiness</a></h3><p>Name the extracted parasitic, energy, latency, noise, area, and sharing evidence needed before converter break-even can be replaced.</p></article>
<article class="card"><h3><a href="research/converter-post-layout-evidence-contract.html">Support E. Converter Post-Layout Evidence Contract</a></h3><p>Define the payload fields an extracted converter run must satisfy before break-even assumptions can be replaced.</p></article>
<article class="card"><h3><a href="research/converter-post-layout-payload-template.html">Support F. Converter Post-Layout Payload Template</a></h3><p>Show the field-by-field shape a real extracted converter result must fill before validation.</p></article>
<article class="card"><h3><a href="research/converter-post-layout-payload-validator.html">Support G. Converter Post-Layout Payload Validator</a></h3><p>Run the executable gate that rejects incomplete post-layout converter payloads and waits for a real extracted result.</p></article>
<article class="card"><h3><a href="research/converter-post-layout-break-even-rerun-path.html">Support H. Converter Post-Layout Break-Even Rerun Path</a></h3><p>Show how a validator-passing extracted payload reruns the converter replace-or-fallback decision.</p></article>
<article class="card"><h3><a href="research/converter-post-layout-strict-intake.html">Support I. Converter Post-Layout Strict Intake</a></h3><p>Require real extracted payloads to point to inspectable netlist, model, and rerun files.</p></article>
<article class="card"><h3><a href="research/converter-post-layout-positive-path.html">Support J. Converter Post-Layout Positive Path</a></h3><p>Prove the strict validator and rerun command path can accept a complete temporary fixture.</p></article>
<article class="card"><h3><a href="research/converter-post-layout-submission-path.html">Support K. Converter Post-Layout Submission Path</a></h3><p>Provide one command that validates a real payload, reruns break-even, and writes the submission report.</p></article>
<article class="card"><h3><a href="research/converter-post-layout-real-payload-package.html">Support L. Converter Real Payload Package</a></h3><p>Name the exact file package and physical numbers a layout or silicon result must provide before the converter claim can change.</p></article>
<article class="card"><h3><a href="research/converter-post-layout-payload-preflight.html">Support M. Converter Payload Preflight</a></h3><p>Review a candidate payload without writing accepted evidence, separating shape mistakes from missing inspectable files.</p></article>
<article class="card"><h3><a href="research/converter-post-layout-candidate-workspace.html">Support N. Converter Candidate Workspace</a></h3><p>Provide a staging folder for the first real payload while proving the default scaffold is not accepted as evidence.</p></article>
<article class="card"><h3><a href="research/converter-post-layout-candidate-workspace-audit.html">Support O. Converter Workspace Audit</a></h3><p>Count placeholders and missing files in the candidate workspace before preflight or submission.</p></article>
<article class="card"><h3><a href="research/converter-post-layout-candidate-fill-checklist.html">Support P. Converter Fill Checklist</a></h3><p>Translate the scaffold audit into exact field and file edits needed before preflight can pass.</p></article>
<article class="card"><h3><a href="research/converter-post-layout-candidate-progress-report.html">Support Q. Converter Candidate Progress</a></h3><p>Show whether the candidate package is still an editable scaffold or ready for preflight.</p></article>
<article class="card"><h3><a href="research/converter-post-layout-candidate-progress-gate.html">Support R. Converter Candidate Progress Gate</a></h3><p>Prove the progress logic rejects the current scaffold and accepts a complete temporary package without submitting evidence.</p></article>
<article class="card"><h3><a href="research/converter-post-layout-candidate-preflight-gate.html">Support S. Converter Candidate Preflight Gate</a></h3><p>Run actual preflight on the current scaffold and a complete temporary package without submitting evidence.</p></article>
<article class="card"><h3><a href="research/converter-post-layout-candidate-submission-gate.html">Support T. Converter Candidate Submission Gate</a></h3><p>Run strict submission on the current scaffold and a complete temporary package while keeping canonical evidence untouched.</p></article>
<article class="card"><h3><a href="research/converter-post-layout-candidate-readiness-run.html">Support U. Converter Candidate Readiness Run</a></h3><p>Run the one-command candidate audit, checklist, progress, and preflight chain before strict submission.</p></article>
<article class="card"><h3><a href="research/converter-post-layout-handoff-manifest.html">Support V. Converter Post-Layout Handoff Manifest</a></h3><p>Name the exact files, values, target boundary, and commands needed for the real converter handoff.</p></article>
<article class="card"><h3><a href="research/converter-post-layout-blocker-ledger.html">Support W. Converter Post-Layout Blocker Ledger</a></h3><p>Show every current blocker that prevents the candidate package from becoming accepted post-layout evidence.</p></article>
<article class="card"><h3><a href="research/converter-post-layout-candidate-edit-plan.html">Support X. Converter Candidate Edit Plan</a></h3><p>Map every candidate payload edit to its evidence source, accepted value shape, and readiness check.</p></article>
<article class="card"><h3><a href="research/converter-post-layout-same-run-gate.html">Support Y. Converter Same-Run Gate</a></h3><p>Require energy, latency, noise, area, simulation conditions, and rerun evidence to share one run identity.</p></article>
<article class="card"><h3><a href="research/converter-post-layout-candidate-identity-initializer.html">Support Z. Converter Identity Initializer</a></h3><p>Initialize one shared run identity and real file names without filling fake measured values or accepted evidence.</p></article>
<article class="card"><h3><a href="research/converter-post-layout-real-candidate-builder.html">Support AA. Converter Real Candidate Builder</a></h3><p>Build the candidate payload from real extracted files and numeric converter values without writing accepted evidence.</p></article>
<article class="card"><h3><a href="research/converter-post-layout-submission-preview.html">Support AB. Converter Submission Preview</a></h3><p>Preview strict submission blockers and would-write accepted evidence paths without creating accepted evidence.</p></article>
<article class="card"><h3><a href="research/converter-post-layout-evidence-leakage-audit.html">Support AC. Converter Leakage Audit</a></h3><p>Prove temporary builder fixtures and accepted-evidence previews did not leak into canonical evidence locations.</p></article>
<article class="card"><h3><a href="research/converter-post-layout-temporary-submission-proof.html">Support AD. Converter Temporary Submission Proof</a></h3><p>Prove builder, preview, and strict submitter can write accepted evidence to a temporary directory while canonical evidence stays untouched.</p></article>
<article class="card"><h3><a href="research/converter-post-layout-real-artifact-discovery.html">Support AE. Converter Real Artifact Discovery</a></h3><p>Audit the repo for existing extraction, model, and rerun files before claiming a real post-layout package exists.</p></article>
<article class="card"><h3><a href="research/converter-post-layout-real-run-recipe.html">Support AF. Converter Real Run Recipe</a></h3><p>Follow the concrete run order for turning the candidate folder into a real post-layout package that strict submission can judge.</p></article>
<article class="card"><h3><a href="research/converter-post-layout-real-run-recipe-coverage.html">Support AG. Converter Recipe Coverage</a></h3><p>Check that every current candidate checklist field appears in the generated real-run recipe.</p></article>
<article class="card"><h3><a href="research/first-real-converter-candidate-execution-plan.html">63. First Real Converter Candidate Execution Plan</a></h3><p>Turn the current 22 strict blockers into one ordered measurement plan for the first honest converter candidate.</p></article>
<article class="card"><h3><a href="research/first-real-converter-candidate-packet.html">64. First Real Converter Candidate Packet</a></h3><p>Collect the strongest local measurements into one partial candidate packet while naming the missing strict evidence.</p></article>
<article class="card"><h3><a href="research/first-real-converter-rehearsal-payload.html">65. First Real Converter Rehearsal Payload</a></h3><p>Fill safe identity and file references from the packet, then show the reduced strict blocker set without accepted evidence.</p></article>
<article class="card"><h3><a href="research/first-real-converter-blocker-work-order.html">66. First Real Converter Blocker Work Order</a></h3><p>Turn the rehearsal failures into six exact build and measurement tasks for the first real converter candidate.</p></article>
<article class="card"><h3><a href="research/first-real-converter-physical-object-audit.html">67. First Real Converter Physical Object Audit</a></h3><p>Audit blocker B1: whether the workspace contains one extracted physical converter object.</p></article>
<article class="card"><h3><a href="research/first-real-converter-physical-object-assembly.html">68. First Real Converter Physical Object Assembly</a></h3><p>Assemble one named candidate netlist from the local extracted starter converter cells.</p></article>
<article class="card"><h3><a href="research/first-real-converter-energy-candidate.html">69. First Real Converter Energy Candidate</a></h3><p>Bind simple-load SPICE energy to the named converter candidate while keeping strict extracted-energy open.</p></article>
<article class="card"><h3><a href="research/first-real-converter-latency-candidate.html">70. First Real Converter Latency Candidate</a></h3><p>Bind row-settling and readout timing evidence to the named converter candidate while keeping strict extracted timing open.</p></article>
<article class="card"><h3><a href="research/first-real-converter-noise-candidate.html">71. First Real Converter Noise Candidate</a></h3><p>Bind behavioral readout-noise evidence to the named converter candidate while keeping strict extracted noise open.</p></article>
<article class="card"><h3><a href="research/first-real-converter-area-candidate.html">72. First Real Converter Area Candidate</a></h3><p>Bind starter layout area estimates to the named converter candidate while keeping strict extracted area open.</p></article>
<article class="card"><h3><a href="research/first-real-converter-break-even-candidate.html">73. First Real Converter Break-Even Candidate</a></h3><p>Rerun candidate break-even from the named B1-B5 values while keeping accepted replacement open.</p></article>
<article class="card"><h3><a href="research/first-real-converter-candidate-loop-strict-readiness.html">74. First Real Converter Candidate Loop Strict Readiness</a></h3><p>Show why the B1-B6 candidate loop is complete but still not accepted strict evidence.</p></article>
<article class="card"><h3><a href="research/first-real-converter-same-candidate-extracted-rc.html">75. First Real Converter Same-Candidate Extracted RC</a></h3><p>Drive the assembled candidate netlist as one extracted-RC object while keeping accepted evidence closed.</p></article>
<article class="card"><h3><a href="research/first-real-converter-frontend-to-input-stage-proxy.html">76. First Real Converter Frontend To Input-Stage Proxy</a></h3><p>Feed the measured extracted-frontend sense signal into a Sky130 transistor input-stage proxy.</p></article>
<article class="card"><h3><a href="research/first-real-converter-frontend-active-handoff-estimate.html">77. First Real Converter Frontend Active Handoff Estimate</a></h3><p>Estimate whether the measured frontend signal becomes latch-useful after measured Sky130 input-stage gain.</p></article>
<article class="card"><h3><a href="research/first-real-converter-combined-active-handoff-work-order.html">78. First Real Converter Combined Active Handoff Work Order</a></h3><p>Turn the active-handoff timeout and estimate into the exact next same-deck circuit task.</p></article>
<article class="card"><h3><a href="research/sky130-frontend-input-stage-handoff-candidate.html">85. Sky130 Frontend Input-Stage Handoff Candidate</a></h3><p>Run the extracted frontend and active gain macro in one deck while keeping transistor proof open.</p></article>
<article class="card"><h3><a href="research/sky130-transistor-handoff-replacement-work-order.html">94. Sky130 Transistor Handoff Replacement Work Order</a></h3><p>Define the exact replacement of the active gain macro with a real Sky130 transistor input stage.</p></article>
<article class="card"><h3><a href="research/sky130-frontend-transistor-input-stage-handoff-candidate.html">95. Sky130 Frontend Transistor Input-Stage Handoff Candidate</a></h3><p>Run the extracted frontend into a real Sky130 transistor input stage and record the current failed handoff.</p></article>
<article class="card"><h3><a href="research/residual-aware-placement-decisions.html">63. Residual-Aware Placement</a></h3><p>Review which backend operators stay analog-allowed after accepted calibrated simulator evidence is matched to the operator family.</p></article>
<article class="card"><h3><a href="research/crosssim-layout-risk-adapter.html">64. CrossSim Layout Risk</a></h3><p>Review array, converter, wire, bit-slicing, and column-current risk for the CrossSim-backed analog-allowed rows.</p></article>
<article class="card"><h3><a href="research/measured-runtime-power-claim-upgrade-path.html">65. Measured Runtime And Power</a></h3><p>See the exact evidence needed before latency and energy can move from needs-review to supported.</p></article>
<article class="card"><h3><a href="research/next-aimc-evidence-work-queue.html">66. Next Evidence Work Queue</a></h3><p>Review the five concrete evidence upgrades needed before the system can make stronger simulator, layout, latency, and energy claims.</p></article>
</div></section>"""

    hub_body = f"""<section class="section"><h2>Start Here</h2><div class="grid">
<article class="card"><h3><a href="synthesis.html">{html.escape(synthesis_title)}</a></h3><p>Read the whole chip-design chain from charge to verified manufactured chip.</p></article>
<article class="card"><h3><a href="paper-synthesis.html">{html.escape(paper_synthesis_title)}</a></h3><p>Read the 20-paper corpus as one argument about preservation under translation.</p></article>
<article class="card"><h3><a href="coverage-audit.html">{html.escape(coverage_title)}</a></h3><p>Review what is covered, what is thin, and the next 25-paper expansion target.</p></article>
<article class="card"><h3><a href="analog-in-memory-foundation-model-synthesis.html">{html.escape(aimc_title)}</a></h3><p>Read the hybrid analog/digital argument from conductance to transformer partitioning.</p></article>
<article class="card"><h3><a href="concepts.html">Concept Atlas</a></h3><p>{len(concept_cards)} first-principles concept articles.</p></article>
<article class="card"><h3><a href="labs.html">Lab Track</a></h3><p>{len(lab_cards)} lab guides tied to circuit and EDA evidence.</p></article>
<article class="card"><h3><a href="research.html">Research Maps</a></h3><p>{len(research_cards)} maps for paper taxonomy and toolchain evidence.</p></article>
<article class="card"><h3><a href="papers.html">Paper Index</a></h3><p>{len(papers)} seed paper entries with object, constraint, method, evidence, and failure boundary.</p></article>
</div></section>{aimc_review_body}"""
    (SITE / "index.html").write_text(page("Analog, Digital Chip Design, and EDA", "local research site", "A first-principles corpus for circuit design and EDA.", hub_body), encoding="utf-8")

    print("PASS")
    print(f"concept_pages {len(concept_cards)}")
    print(f"lab_pages {len(lab_cards)}")
    print(f"research_pages {len(research_cards)}")
    print(f"paper_entries {len(papers)}")
    print(f"site {SITE}")


if __name__ == "__main__":
    main()
