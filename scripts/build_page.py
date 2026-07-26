#!/usr/bin/env python3
"""Render the 10 per-theme writeup JSONs into the big-picture page at the <!--THEMES--> marker.

Reads analysis/themes/page.template.html + analysis/themes/sections/<key>.json
Writes mlsys-2025-bigpicture.html
Usage: python3 scripts/build_page.py
"""
import json, glob, html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SECT = ROOT / "analysis/themes/sections"
BUCK = ROOT / "analysis/themes/buckets"

# display order + numbering + human titles
ORDER = [
    ("T1_attention", "LLM serving, attention & the model's growing notes"),
    ("T2_quantization", "Using smaller numbers"),
    ("T3_memory", "The memory wall — moving compute to the data"),
    ("T4_interconnect", "When chips must talk to chips"),
    ("T5_sparsity", "Skipping the work that doesn't matter"),
    ("T6_compiler", "Describing hardware so a machine can build it"),
    ("T7_security", "Trusting the machine"),
    ("T8_reliability", "Being sure it's actually correct"),
    ("T9_specialized", "Beyond the GPU"),
    ("T0_other", "Everything else that keeps it running"),
]


def esc(s):
    return html.escape(str(s or "")).strip()


def conf_of(key):
    """count high/low from the bucket for a small stat line."""
    hi = lo = 0
    p = BUCK / f"{key}.jsonl"
    if p.exists():
        for l in p.open():
            c = json.loads(l).get("c")
            if c == "high":
                hi += 1
            else:
                lo += 1
    return hi, lo


def render_paper(pp, lowset):
    pid = esc(pp.get("id"))
    name = esc(pp.get("name"))
    gloss = esc(pp.get("gloss"))
    nm = f"<b>{name}</b> — " if name else ""
    low = ' <span class="lowtag">abstract-only</span>' if pp.get("id") in lowset else ""
    return (f'<div class="prow"><span class="pid">{pid}</span>'
            f'<span class="pg">{nm}{gloss}{low}</span></div>')


def render_theme(i, key, title):
    f = SECT / f"{key}.json"
    if not f.exists():
        return f'<div class="theme"><div class="tnum">Theme {i}</div><h3>{esc(title)}</h3>'\
               f'<p style="color:var(--ink-mute)">(section pending)</p></div>'
    d = json.loads(f.read_text())
    hi, lo = conf_of(key)
    n = hi + lo
    # which ids are abstract-only
    lowset = set()
    p = BUCK / f"{key}.jsonl"
    if p.exists():
        for l in p.open():
            r = json.loads(l)
            if r.get("c") != "high":
                lowset.add(r.get("id"))

    groups_html = []
    for g in d.get("groups", []):
        papers = "".join(render_paper(pp, lowset) for pp in g.get("papers", []))
        groups_html.append(
            f'<div class="tgroup"><h4>{esc(g.get("heading"))}</h4>'
            f'<p class="gx">{esc(g.get("explain"))}</p>'
            f'<div class="plist">{papers}</div></div>')

    return f'''<div class="theme" id="{key}" data-reveal>
      <div class="tnum">Theme {i} · {n} papers</div>
      <h3>{esc(title)}</h3>
      <div class="frame">
        <div class="fb problem"><div class="lab">the problem</div><p>{esc(d.get("problem_plain"))}</p></div>
        <div class="fb approach"><div class="lab">the approach</div><p>{esc(d.get("approach_plain"))}</p></div>
      </div>
      <p class="tstat">Why it matters — {esc(d.get("why_plain"))}</p>
      {"".join(groups_html)}
      <p class="connect">{esc(d.get("connect"))}</p>
    </div>'''


def main():
    nav = " ".join(
        f'<a href="#{key}">{i}. {esc(title)}</a>'
        for i, (key, title) in enumerate(ORDER, 1))

    themes = "\n".join(render_theme(i, key, title) for i, (key, title) in enumerate(ORDER, 1))

    section = f'''<section>
    <div class="sec-head prose">
      <div class="eyebrow kicker">the details</div>
      <h2>Every theme, from first principles</h2>
      <p>The whole field, theme by theme: the plain-language problem, the approach, and every one of the 503 papers glossed and grouped. Abstract-only papers are marked — their read is shallower.</p>
      <div class="themenav">{nav}</div>
    </div>
    {themes}
  </section>'''

    tpl = (ROOT / "analysis/themes/page.template.html").read_text()
    out = tpl.replace("<!--THEMES-->", section)
    (ROOT / "mlsys-2025-bigpicture.html").write_text(out)
    print(f"rendered {sum(1 for k,_ in ORDER if (SECT/f'{k}.json').exists())}/10 theme sections -> mlsys-2025-bigpicture.html")


if __name__ == "__main__":
    main()
