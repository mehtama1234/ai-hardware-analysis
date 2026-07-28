#!/usr/bin/env python3
"""Assemble robotics-style per-theme deep-dive pages + a hub, from the generated deep content.

Reads analysis/themes/deep/<key>_intro.json  (problem_in_depth, approaches[], where_it_stands)
      analysis/themes/deep/papers/<id>.json   (what_it_does, method_in_detail, confidence)
      analysis/themes/buckets/<key>.jsonl      (paper order/titles/venues)
Writes <key>-deepdive.html for each theme + deepdives.html hub.
Usage: python3 scripts/build_deepdives.py
"""
import json, glob, html, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEEP = ROOT / "analysis/themes/deep"
BUCK = ROOT / "analysis/themes/buckets"

THEMES = [
    ("T1_attention", "Serving language models fast", "attention and the model's running notes"),
    ("T2_quantization", "Using smaller numbers", "rounding to save memory and time"),
    ("T3_memory", "The memory wall", "moving the math to where the data already is"),
    ("T4_interconnect", "When chips must talk to chips", "the wiring and messages between them"),
    ("T5_sparsity", "Skipping the work that doesn't matter", "most of the numbers barely count"),
    ("T6_compiler", "Describing hardware so a machine can build it", "compilers and chip generators"),
    ("T7_security", "Trusting the machine", "attacks on chips, and the defenses"),
    ("T8_reliability", "Being sure it's actually correct", "silent errors, faults, and proofs"),
    ("T9_specialized", "Beyond the GPU", "new kinds of chips, and new jobs for them"),
    ("T0_other", "Everything else that keeps it running", "scheduling, data, and infrastructure"),
]

def esc(s): return html.escape(str(s or "")).strip()

def paras(text):
    text = str(text or "").strip()
    if not text: return ""
    # split on blank lines OR labeled points; keep it simple: split on double newline, else single
    blocks = re.split(r"\n\s*\n", text) if "\n\n" in text else re.split(r"(?<=[.])\s*\n", text)
    out = []
    for b in blocks:
        b = b.strip()
        if not b: continue
        # bold a leading "Label." up to ~28 chars
        m = re.match(r"^([A-Z][A-Za-z /-]{1,30}?[.:])\s+(.*)$", b, re.S)
        if m:
            out.append(f"<p><b>{esc(m.group(1))}</b> {esc(m.group(2))}</p>")
        else:
            out.append(f"<p>{esc(b)}</p>")
    return "\n".join(out)

CSS = """
:root{--ground:#14171d;--ground-2:#181c23;--panel:#1c212a;--line:#2b323d;--line-soft:#242a34;
--ink:#eae7e0;--ink-dim:#b7bcc4;--ink-mute:#8b93a0;--demand:#e8975a;--supply:#4fc1b1;--warn:#e0584b;
--serif:"Iowan Old Style","Palatino Linotype",Palatino,Charter,Georgia,serif;
--mono:ui-monospace,"SF Mono","Cascadia Code",Menlo,Consolas,monospace;
--sans:system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;}
*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);font-family:var(--sans);font-size:17px;line-height:1.68;
-webkit-font-smoothing:antialiased;background-image:radial-gradient(1100px 560px at 82% -10%,#1d2530,transparent 60%);background-attachment:fixed}
.wrap{max-width:820px;margin:0 auto;padding:0 clamp(20px,5vw,40px)}
a{color:var(--supply);text-underline-offset:3px}
h1,h2,h3,h4{font-family:var(--serif);font-weight:600;letter-spacing:-.01em;line-height:1.12;text-wrap:balance;margin:0}
p{margin:0 0 1em}
.eyebrow{font-family:var(--mono);font-size:.72rem;letter-spacing:.22em;text-transform:uppercase;color:var(--ink-mute)}
.top{padding:36px 0 8px}
.back{font-family:var(--mono);font-size:.75rem;color:var(--ink-mute);text-decoration:none}
.back:hover{color:var(--supply)}
header.hero{padding:26px 0 34px;border-bottom:1px solid var(--line)}
header.hero h1{font-size:clamp(2.1rem,5vw,3.2rem);margin:.3em 0 .2em}
header.hero .sub{font-family:var(--serif);font-size:1.3rem;color:var(--ink-dim)}
header.hero .count{font-family:var(--mono);font-size:.75rem;color:var(--ink-mute);margin-top:14px}
section{padding:40px 0;border-bottom:1px solid var(--line-soft)}
.sh{font-size:1.7rem;margin-bottom:.7em;color:var(--ink)}
.sh .k{font-family:var(--mono);font-size:.7rem;letter-spacing:.16em;text-transform:uppercase;color:var(--demand);display:block;margin-bottom:.5em}
.prose p{color:var(--ink-dim)} .prose p b{color:var(--ink)}
.appr{border-left:2px solid var(--line);padding:2px 0 2px 20px;margin:0 0 26px}
.appr h3{font-size:1.28rem;color:var(--ink);margin-bottom:.5em}
.appr h3 .n{font-family:var(--mono);color:var(--supply);font-size:.9rem;margin-right:8px}
.appr .prose p{font-size:.98rem}
.where{background:var(--ground-2);border:1px solid var(--line);border-left:3px solid var(--supply);border-radius:10px;padding:18px 22px}
.where p{margin:0 0 .7em;color:var(--ink-dim)} .where p:last-child{margin:0}
.paper{padding:30px 0;border-top:1px solid var(--line)}
.paper .ph{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap;margin-bottom:4px}
.paper .pid{font-family:var(--mono);font-size:.72rem;color:var(--supply)}
.paper .badge{font-family:var(--mono);font-size:.62rem;letter-spacing:.04em;padding:2px 7px;border-radius:4px;text-transform:uppercase}
.paper .badge.hi{color:var(--supply);border:1px solid #4fc1b155}
.paper .badge.lo{color:var(--ink-mute);border:1px solid var(--line)}
.paper h4{font-size:1.32rem;color:var(--ink);margin:.15em 0 .7em}
.paper .lab{font-family:var(--mono);font-size:.66rem;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-mute);margin:16px 0 6px}
.paper .wid p,.paper .mid p{color:var(--ink-dim)} .paper .mid p b{color:var(--ink)}
.paper .mid{background:var(--ground-2);border:1px solid var(--line-soft);border-radius:10px;padding:16px 20px}
.paper .note{font-size:.9rem;color:var(--ink-mute);font-style:italic}
footer{padding:44px 0 80px;color:var(--ink-mute);font-family:var(--mono);font-size:.76rem}
:focus-visible{outline:2px solid var(--supply);outline-offset:3px}
/* hub */
.cards{display:flex;flex-direction:column;gap:14px}
.card{display:block;text-decoration:none;background:linear-gradient(180deg,var(--panel),var(--ground-2));
border:1px solid var(--line);border-radius:13px;padding:22px 24px}
.card:hover{border-color:var(--supply)}
.card h3{font-size:1.4rem;color:var(--ink);margin-bottom:.2em}
.card .sub{font-family:var(--serif);color:var(--ink-dim);font-size:1.02rem;margin-bottom:.5em}
.card .m{font-family:var(--mono);font-size:.72rem;color:var(--ink-mute)}
.card .m b{color:var(--supply);font-weight:400}
"""

def paper_ids(key):
    ids = []
    p = BUCK / f"{key}.jsonl"
    if p.exists():
        for l in p.open():
            r = json.loads(l); ids.append((r["id"], r.get("t"), r.get("v"), r.get("c")))
    # full-text (high) first
    ids.sort(key=lambda x: (x[3] != "high", x[0]))
    return ids

def render_paper(pid, title, venue, conf):
    f = DEEP / "papers" / f"{pid}.json"
    d = json.loads(f.read_text()) if f.exists() else {}
    hi = (d.get("confidence") == "high") and d.get("method_in_detail")
    badge = '<span class="badge hi">full text</span>' if hi else '<span class="badge lo">from abstract</span>'
    wid = paras(d.get("what_it_does")) or "<p class='note'>(summary pending)</p>"
    mid = ""
    if hi:
        mid = f'<div class="lab">The method, in detail</div><div class="mid prose">{paras(d.get("method_in_detail"))}</div>'
    else:
        mid = '<p class="note">Read from the abstract only — the full method wasn\'t available (this venue is paywalled).</p>'
    return f'''<div class="paper" id="{esc(pid)}">
      <div class="ph"><span class="pid">{esc(pid)}</span><span class="badge-wrap">{badge}</span><span style="color:var(--ink-mute);font-family:var(--mono);font-size:.7rem">{esc(venue)}</span></div>
      <h4>{esc(title)}</h4>
      <div class="lab">What it does</div><div class="wid prose">{wid}</div>
      {mid}
    </div>'''

def render_theme(key, title, subtitle):
    intro_f = DEEP / f"{key}_intro.json"
    intro = json.loads(intro_f.read_text()) if intro_f.exists() else {}
    ids = paper_ids(key)
    nhi = sum(1 for _,_,_,c in ids if c == "high")
    appr = "\n".join(
        f'<div class="appr"><h3><span class="n">{i}.</span>{esc(a.get("title"))}</h3><div class="prose">{paras(a.get("prose"))}</div></div>'
        for i, a in enumerate(intro.get("approaches", []), 1))
    papers = "\n".join(render_paper(pid, t, v, c) for pid, t, v, c in ids)
    body = f'''<div class="wrap">
  <div class="top"><a class="back" href="deepdives.html">← all deep dives</a></div>
  <header class="hero">
    <div class="eyebrow">deep dive</div>
    <h1>{esc(title)}</h1>
    <div class="sub">{esc(subtitle)}</div>
    <div class="count">{len(ids)} papers · {nhi} read in full · {len(ids)-nhi} from the abstract</div>
  </header>
  <section class="prose"><h2 class="sh"><span class="k">the problem</span>The problem, in depth</h2>{paras(intro.get("problem_in_depth")) or "<p>(pending)</p>"}</section>
  <section><h2 class="sh"><span class="k">the approaches</span>How the field actually tackles it</h2>{appr or "<p>(pending)</p>"}</section>
  <section><h2 class="sh"><span class="k">where it stands</span>What's solved, what's open</h2><div class="where prose">{paras(intro.get("where_it_stands")) or "<p>(pending)</p>"}</div></section>
  <section><h2 class="sh"><span class="k">the papers</span>Every paper in this theme</h2>{papers}</section>
  <footer>AI Hardware 2025 · full text where openly available, else the abstract · <a href="deepdives.html">back to hub</a></footer>
</div>'''
    (ROOT / f"{key.split('_')[0].lower()}-deepdive.html").write_text(f"<style>{CSS}</style>\n{body}")
    return len(ids), nhi

def render_hub(stats):
    cards = []
    for (key, title, subtitle), (n, nhi) in zip(THEMES, stats):
        slug = key.split('_')[0].lower()
        intro_f = DEEP / f"{key}_intro.json"
        teaser = ""
        if intro_f.exists():
            t = json.loads(intro_f.read_text()).get("problem_in_depth", "")
            teaser = esc(t[:220].rsplit(" ", 1)[0]) + "…"
        cards.append(f'''<a class="card" href="{slug}-deepdive.html"><h3>{esc(title)}</h3>
          <div class="sub">{esc(subtitle)}</div>
          <p style="color:var(--ink-dim);font-size:.95rem;margin:.2em 0 .6em">{teaser}</p>
          <div class="m"><b>{n}</b> papers · <b>{nhi}</b> read in full</div></a>''')
    body = f'''<div class="wrap">
  <header class="hero" style="border-bottom:1px solid var(--line);padding-top:44px">
    <div class="eyebrow" style="color:var(--demand)">AI hardware 2025 · deep dives</div>
    <h1 style="font-size:clamp(2.3rem,6vw,3.6rem);margin:.3em 0 .3em">Every theme, all the way down</h1>
    <div class="sub">Nine chapters. Each one builds the problem from first principles, walks the approaches, then explains every paper — the full method where the paper was openly available.</div>
    <div class="count">1,809 papers · 11 venues · 120 read in full text</div>
  </header>
  <section><div class="cards">{"".join(cards)}</div></section>
  <footer>Start anywhere. Each chapter stands alone. · <a href="mlsys-2025-bigpicture.html">the one-page overview</a></footer>
</div>'''
    (ROOT / "deepdives.html").write_text(f"<style>{CSS}</style>\n{body}")

def main():
    stats = [render_theme(k, t, s) for k, t, s in THEMES]
    render_hub(stats)
    done = sum(1 for k,_,_ in THEMES if (DEEP/f'{k}_intro.json').exists())
    npapers = len(list((DEEP/'papers').glob('*.json')))
    print(f"built {len(THEMES)} theme pages + hub. intros ready: {done}/10. paper writeups: {npapers}/503")

if __name__ == "__main__":
    main()
