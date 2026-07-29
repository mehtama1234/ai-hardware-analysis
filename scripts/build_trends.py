#!/usr/bin/env python3
"""Rebuild trends.html from analysis/yoy-comparison.json.
Usage: python3 scripts/build_trends.py
"""
import json, html as htmllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "analysis/yoy-comparison.json"
OUT  = ROOT / "trends.html"

d = json.load(DATA.open())
meta = d.get("meta", {})
tc   = d.get("theme_comparison", [])
tm   = d.get("top_movers", {})
vb   = d.get("venue_breakdown", {})
tot24 = sum(d.get("all_theme_totals_2024", {}).values())
tot25 = sum(d.get("all_theme_totals_2025", {}).values())
matched_venues = meta.get("matched_venues", [])

THEME_COLORS = {
    "T1_attention":    "#38E1CF",
    "T2_quantization": "#F5A65B",
    "T3_memory":       "#9C8CFF",
    "T4_interconnect": "#FF6B5C",
    "T5_sparsity":     "#4ECDC4",
    "T6_compiler":     "#FFE66D",
    "T7_security":     "#FF4E50",
    "T8_reliability":  "#6BCB77",
    "T9_specialized":  "#C9A84C",
    "T0_other":        "#5B6B78",
}

def esc(s): return htmllib.escape(str(s))

def make_bar_chart():
    # Filter out T0_other, sort by 2024 count desc
    rows = [t for t in tc if t["theme"] != "T0_other"]
    rows.sort(key=lambda x: x["count_2024"], reverse=True)
    max24 = max(r["count_2024"] for r in rows) if rows else 1
    max25 = max(r["count_2025"] for r in rows) if rows else 1

    bars = []
    for r in rows:
        w24 = max(1, int(r["count_2024"] / max24 * 240))
        w25 = max(1, int(r["count_2025"] / max25 * 240))
        pct = r["pct_change"]
        sign = "+" if pct >= 0 else ""
        col = THEME_COLORS.get(r["theme"], "#5B6B78")
        bars.append(f"""
      <div class="bar-row">
        <div class="bar-label">{esc(r['short'])}</div>
        <div class="bar-tracks">
          <div class="bar-track">
            <div class="bar bar-24" style="width:{w24}px"></div>
            <span class="bar-count">{r['count_2024']}</span>
          </div>
          <div class="bar-track">
            <div class="bar bar-25" style="width:{w25}px;background:{col}"></div>
            <span class="bar-count">{r['count_2025']}</span>
          </div>
        </div>
        <div class="bar-delta {'pos' if pct >= 0 else 'neg'}">{sign}{pct:.0f}%</div>
      </div>""")
    return "\n".join(bars)

def make_mover_cards():
    cards = []
    for role in ["biggest_grower", "biggest_shrinker", "new_entrant"]:
        m = tm.get(role)
        if not m:
            continue
        label_map = {"biggest_grower": "↑ Biggest grower", "biggest_shrinker": "↓ Slowest grower", "new_entrant": "★ Emerging"}
        css_class = "grower" if role == "biggest_grower" else ("shrinker" if role == "biggest_shrinker" else "new")
        sign = "+" if m.get("pct_change", 0) >= 0 else ""
        cards.append(f"""
    <div class="mover-card {css_class}">
      <div class="mover-role">{label_map[role]}</div>
      <div class="mover-label">{esc(m.get('short', m.get('theme','')))}</div>
      <div class="mover-stat">{sign}{m.get('pct_change',0):.0f}% ({m.get('count_2024',0)} → {m.get('count_2025',0)} papers)</div>
    </div>""")
    return "\n".join(cards)

def make_venue_breakdown():
    rows = []
    for v in sorted(vb, key=lambda x: x.get("venue", "")):
        venue = v.get("venue", "")
        t24 = v.get("total_2024", 0)
        t25 = v.get("total_2025", 0)
        if t24 == 0 and t25 == 0:
            continue
        max_val = max(t24, t25, 1)
        w24 = max(1, int(t24 / max_val * 120))
        w25 = max(1, int(t25 / max_val * 120))
        pct = ((t25 - t24) / t24 * 100) if t24 > 0 else 0
        rows.append(f"""
      <div class="venue-row">
        <div class="venue-name">{esc(venue)}</div>
        <div class="venue-bars">
          <div class="vbar-row"><span class="vbar-key">24</span><div class="vbar-tracks"><div class="vbar vbar-24" style="width:{w24}px"></div></div><span style="font-size:.65rem;color:var(--ink3);margin-left:4px">{t24}</span></div>
          <div class="vbar-row"><span class="vbar-key">25</span><div class="vbar-tracks"><div class="vbar vbar-25" style="width:{w25}px"></div></div><span style="font-size:.65rem;color:var(--ink3);margin-left:4px">{t25}</span></div>
        </div>
        <div class="venue-pct">+{pct:.0f}%</div>
      </div>""")
    return "\n".join(rows)

# Read the essay from the syntheses file
essay_f = ROOT / "analysis/syntheses/yoy-2024-2025.md"
essay_html = ""
if essay_f.exists():
    import re
    md = essay_f.read_text()
    # Simple markdown to HTML
    lines = md.splitlines()
    paras = []
    for line in lines:
        s = line.strip()
        if not s:
            continue
        if s.startswith("## "):
            paras.append(f'<h2>{esc(s[3:])}</h2>')
        elif s.startswith("# "):
            continue  # skip title
        elif s.startswith("- "):
            paras.append(f'<li>{esc(s[2:])}</li>')
        else:
            paras.append(f'<p>{esc(s)}</p>')
    essay_html = "\n".join(paras)

coverage_note = f"""<strong>Coverage note:</strong> 2024 figures come from {tot24:,} Haiku-analyzed papers across {len(matched_venues)} matched venues
(ASPLOS, HPCA, ISCA, MICRO, MLSys, DAC, SC). Analysis ongoing — DAC and SC counts will grow as more papers complete.
Percentage deltas reflect real field growth for ASPLOS/HPCA/ISCA/MICRO/MLSys (near-complete coverage);
DAC and SC figures are partial. Theme <em>shares</em> within each venue are reliable even at partial coverage."""

page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>2024 → 2025: What Moved · AI Hardware YoY Trends</title>
<style>
:root {{
  --g0:#0d1117; --g1:#11161e; --g2:#161c26; --g3:#1c2330;
  --line:#272f3d; --line2:#1e2635;
  --ink:#e8e3d8; --ink2:#b8c0cc; --ink3:#7a8494;
  --teal:#3ec9b6; --orange:#e09858; --red:#d95a4a; --gold:#c9a84c;
  --violet:#9c8cff;
  --serif:Palatino,"Palatino Linotype","Book Antiqua",Charter,Georgia,serif;
  --mono:ui-monospace,"SF Mono","Cascadia Code",Menlo,Consolas,monospace;
  --sans:system-ui,-apple-system,"Segoe UI",sans-serif;
}}
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
html{{scroll-behavior:smooth}}
body{{background:var(--g0);color:var(--ink);font-family:var(--serif);font-size:18px;line-height:1.78;-webkit-font-smoothing:antialiased}}
.shell{{display:grid;grid-template-columns:240px 1fr;min-height:100vh}}
.sidebar{{position:sticky;top:0;height:100vh;overflow-y:auto;padding:32px 20px 40px;border-right:1px solid var(--line);background:var(--g1);display:flex;flex-direction:column;gap:0}}
.main{{padding:0 clamp(28px,6vw,80px) 120px;max-width:880px}}
.site-label{{font-family:var(--mono);font-size:.62rem;letter-spacing:.22em;text-transform:uppercase;color:var(--ink3);margin-bottom:24px;padding-bottom:16px;border-bottom:1px solid var(--line2)}}
.nav-link{{display:block;font-family:var(--sans);font-size:.82rem;color:var(--ink3);text-decoration:none;padding:5px 8px;border-radius:6px;line-height:1.35;margin-bottom:2px}}
.nav-link:hover,.nav-link.active{{color:var(--teal);background:var(--g2)}}
.hero{{padding:56px 0 44px;border-bottom:1px solid var(--line)}}
.hero .eyebrow{{font-family:var(--mono);font-size:.7rem;letter-spacing:.22em;text-transform:uppercase;color:var(--orange);margin-bottom:20px}}
.hero h1{{font-family:var(--serif);font-size:clamp(2.2rem,5vw,3.4rem);font-weight:700;line-height:1.06;color:var(--ink);text-wrap:balance;margin-bottom:.4em;letter-spacing:-.02em}}
.hero .sub{{font-family:var(--serif);font-size:1.15rem;color:var(--ink2);font-style:italic;max-width:560px;margin-bottom:24px}}
.hero .meta-row{{display:flex;gap:32px;flex-wrap:wrap;font-family:var(--mono);font-size:.7rem;color:var(--ink3);font-variant-numeric:tabular-nums}}
.hero .meta-row .stat b{{color:var(--teal);font-weight:400}}
.caveat{{background:var(--g2);border:1px solid var(--line);border-left:3px solid var(--gold);border-radius:0 8px 8px 0;padding:16px 20px;margin:28px 0;font-size:.88rem}}
.caveat p{{color:var(--ink2);margin:0}}
.caveat strong{{color:var(--gold);font-weight:600}}
.section{{padding:48px 0;border-bottom:1px solid var(--line2)}}
.section h2{{font-family:var(--serif);font-size:1.8rem;font-weight:600;color:var(--ink);margin-bottom:28px;letter-spacing:-.01em}}
.bar-chart{{display:flex;flex-direction:column;gap:14px;margin:24px 0}}
.bar-row{{display:grid;grid-template-columns:130px 1fr 80px;align-items:center;gap:12px}}
.bar-label{{font-family:var(--mono);font-size:.7rem;color:var(--ink2);text-align:right}}
.bar-tracks{{display:flex;flex-direction:column;gap:4px}}
.bar-track{{display:flex;align-items:center;gap:6px}}
.bar{{height:12px;border-radius:2px;transition:width .3s}}
.bar-24{{background:var(--violet);opacity:.8}}
.bar-count{{font-family:var(--mono);font-size:.65rem;color:var(--ink3);min-width:28px}}
.bar-delta{{font-family:var(--mono);font-size:.75rem;font-weight:600;text-align:right}}
.bar-delta.pos{{color:var(--teal)}}
.bar-delta.neg{{color:var(--red)}}
.bar-legend{{display:flex;gap:24px;font-family:var(--mono);font-size:.68rem;color:var(--ink3);margin-bottom:16px}}
.leg-swatch{{display:inline-block;width:12px;height:8px;border-radius:1px;margin-right:6px;vertical-align:middle}}
.movers{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px;margin:24px 0}}
.mover-card{{padding:20px;border:1px solid var(--line);border-radius:8px;background:var(--g1);position:relative;overflow:hidden}}
.mover-card::before{{content:'';position:absolute;left:0;top:0;bottom:0;width:3px;background:var(--teal)}}
.mover-card.shrinker::before{{background:var(--orange)}}
.mover-card.new::before{{background:var(--violet)}}
.mover-role{{font-family:var(--mono);font-size:.62rem;letter-spacing:.12em;text-transform:uppercase;color:var(--ink3);margin-bottom:8px}}
.mover-label{{font-family:var(--sans);font-size:.95rem;font-weight:600;color:var(--ink);margin-bottom:6px}}
.mover-stat{{font-family:var(--mono);font-size:.78rem;color:var(--teal);font-weight:600}}
.mover-card.shrinker .mover-stat{{color:var(--orange)}}
.mover-card.new .mover-stat{{color:var(--violet)}}
.venue-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:20px;margin:24px 0}}
.venue-row{{padding:16px;background:var(--g1);border:1px solid var(--line);border-radius:8px}}
.venue-name{{font-family:var(--mono);font-size:.72rem;letter-spacing:.1em;text-transform:uppercase;color:var(--ink2);margin-bottom:10px}}
.venue-bars{{display:flex;flex-direction:column;gap:4px}}
.vbar-row{{display:flex;align-items:center;gap:5px;min-height:14px}}
.vbar-key{{font-family:var(--mono);font-size:.6rem;color:var(--ink3);min-width:16px}}
.vbar-tracks{{display:flex;gap:2px;flex:1;align-items:center}}
.vbar{{height:8px;border-radius:1px;min-width:1px}}
.vbar-24{{background:var(--violet);opacity:.8}}
.vbar-25{{background:var(--teal);opacity:.8}}
.venue-pct{{font-family:var(--mono);font-size:.68rem;color:var(--teal);margin-top:8px;font-weight:600}}
.prose h2{{font-family:var(--serif);font-size:1.5rem;font-weight:600;color:var(--ink);margin:2.5em 0 .6em;padding-top:1.2em;border-top:1px solid var(--line2)}}
.prose p{{color:var(--ink2);margin-bottom:1.1em}}
.prose li{{color:var(--ink2);margin-bottom:.4em;margin-left:1.4em}}
@media(max-width:680px){{.shell{{grid-template-columns:1fr}}.sidebar{{display:none}}}}
</style>
</head>
<body>
<div class="shell">
  <aside class="sidebar">
    <div class="site-label">AI Hardware 2025</div>
    <a class="nav-link" href="index.html">← master narrative</a>
    <a class="nav-link" href="grand-synthesis.html">grand synthesis</a>
    <a class="nav-link active" href="trends.html">year-over-year</a>
    <a class="nav-link" href="heatmap.html">heatmap</a>
    <a class="nav-link" href="explorer.html">explorer</a>
    <a class="nav-link" href="deepdives.html">theme deep dives</a>
  </aside>
  <main class="main">
    <div class="hero">
      <div class="eyebrow">AI Hardware · 2024 → 2025</div>
      <h1>2024 → 2025:<br>What Moved</h1>
      <div class="sub">{len(matched_venues)} matched venues. {tot24:,} analyzed 2024 papers against {tot25:,} 2025 papers. Where the field's weight shifted.</div>
      <div class="meta-row">
        <div class="stat">2024 analyzed: <b>{tot24:,}</b></div>
        <div class="stat">2025 corpus: <b>{tot25:,}</b></div>
        <div class="stat">venues matched: <b>{len(matched_venues)}</b></div>
      </div>
    </div>

    <div class="caveat">
      <p>{coverage_note}</p>
    </div>

    <div class="section">
      <h2>Theme shift, 2024 → 2025</h2>
      <div class="bar-legend">
        <span><span class="leg-swatch" style="background:var(--violet)"></span>2024</span>
        <span><span class="leg-swatch" style="background:var(--teal)"></span>2025</span>
      </div>
      <div class="bar-chart">
        {make_bar_chart()}
      </div>
    </div>

    <div class="section">
      <h2>Top movers</h2>
      <div class="movers">
        {make_mover_cards()}
      </div>
    </div>

    <div class="section">
      <h2>Venue by venue</h2>
      <div class="venue-grid">
        {make_venue_breakdown()}
      </div>
    </div>

    <div class="section prose">
      <h2>What the numbers mean</h2>
      {essay_html}
    </div>

    <footer style="padding:48px 0 60px;color:var(--ink3);font-family:var(--mono);font-size:.7rem;border-top:1px solid var(--line2);margin-top:2em">
      AI Hardware YoY · 2024 vs 2025 · {tot24:,} 2024 papers (Haiku) · {tot25:,} 2025 papers (Haiku) · <a href="index.html" style="color:var(--teal);text-decoration:none">master narrative</a>
    </footer>
  </main>
</div>
</body>
</html>"""

OUT.write_text(page)
print(f"Built trends.html ({len(page)//1024}KB)")
print(f"  2024: {tot24} papers | 2025: {tot25} papers | {len(matched_venues)} venues")
