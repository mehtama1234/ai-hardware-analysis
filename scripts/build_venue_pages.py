#!/usr/bin/env python3
"""Build per-venue big-picture HTML pages from analysis/syntheses/<conf>-<year>-bigpicture.md.

Usage: python3 scripts/build_venue_pages.py
Writes <conf>-<year>-bigpicture.html for every bigpicture.md found.
"""
import re, html, glob
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SYNTH = ROOT / "analysis/syntheses"

VENUES = {
    "mlsys":    ("MLSys",     "Machine Learning Systems"),
    "isca":     ("ISCA",      "Computer Architecture"),
    "micro":    ("MICRO",     "Microarchitecture"),
    "hpca":     ("HPCA",      "High-Performance Architecture"),
    "asplos":   ("ASPLOS",    "Architecture + Systems + PL"),
    "dac":      ("DAC",       "Design Automation"),
    "isscc":    ("ISSCC",     "Solid-State Circuits"),
    "hotchips": ("Hot Chips", "Industry Silicon"),
    "sc":       ("SC",        "Supercomputing"),
    "vlsid":    ("VLSID",     "VLSI Design"),
    "cgo":      ("CGO",       "Compiler Optimization"),
    "iccad":    ("ICCAD",     "EDA & Design Automation"),
    "date":     ("DATE",      "Design, Automation & Test in Europe"),
    "osdi":     ("OSDI",     "Operating Systems & Systems Software"),
    "usenix":   ("USENIX ATC", "Annual Technical Conference"),
    "fccm":     ("FCCM",      "Reconfigurable Computing"),
}

CSS = """
:root {
  --g0:#0d1117; --g1:#11161e; --g2:#161c26; --g3:#1c2330;
  --line:#272f3d; --line2:#1e2635;
  --ink:#e8e3d8; --ink2:#b8c0cc; --ink3:#7a8494;
  --teal:#3ec9b6; --orange:#e09858; --gold:#c9a84c;
  --serif:Palatino,"Palatino Linotype","Book Antiqua",Charter,Georgia,serif;
  --mono:ui-monospace,"SF Mono","Cascadia Code",Menlo,Consolas,monospace;
  --sans:system-ui,-apple-system,"Segoe UI",sans-serif;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{background:var(--g0);color:var(--ink);font-family:var(--serif);
  font-size:18px;line-height:1.78;-webkit-font-smoothing:antialiased}
.wrap{max-width:780px;margin:0 auto;padding:0 clamp(24px,5vw,60px) 100px}
a{color:var(--teal);text-underline-offset:3px}
/* top nav */
.top{padding:28px 0 6px;display:flex;gap:16px;align-items:center;flex-wrap:wrap}
.back{font-family:var(--mono);font-size:.72rem;color:var(--ink3);text-decoration:none}
.back:hover{color:var(--teal)}
/* venue pills nav */
.venue-nav{display:flex;gap:6px;flex-wrap:wrap;padding:14px 0 28px;
  border-bottom:1px solid var(--line)}
.venue-nav a{font-family:var(--mono);font-size:.65rem;letter-spacing:.08em;
  text-transform:uppercase;color:var(--ink3);text-decoration:none;
  padding:4px 10px;border:1px solid var(--line2);border-radius:20px}
.venue-nav a:hover,.venue-nav a.cur{color:var(--teal);border-color:var(--teal)}
/* hero */
.hero{padding:44px 0 32px;border-bottom:1px solid var(--line)}
.hero .eyebrow{font-family:var(--mono);font-size:.7rem;letter-spacing:.22em;
  text-transform:uppercase;color:var(--orange);margin-bottom:16px}
.hero h1{font-family:var(--serif);font-size:clamp(2.2rem,5vw,3.4rem);
  font-weight:700;line-height:1.07;color:var(--ink);letter-spacing:-.02em;
  text-wrap:balance;margin-bottom:.3em}
.hero .sub{font-family:var(--serif);font-size:1.15rem;color:var(--ink2);font-style:italic}
/* section headings */
h2{font-family:var(--serif);font-size:1.7rem;font-weight:600;color:var(--ink);
  margin:3em 0 .7em;padding-top:1.6em;border-top:1px solid var(--line2);
  line-height:1.15;text-wrap:balance}
h2:first-of-type{border-top:none;margin-top:2em}
h3{font-family:var(--serif);font-size:1.28rem;font-weight:600;color:var(--ink);
  margin:2.2em 0 .5em;padding-left:14px;border-left:3px solid var(--teal)}
h4{font-family:var(--serif);font-size:1.08rem;font-weight:600;color:var(--ink2);
  margin:1.6em 0 .4em;padding-left:10px;border-left:2px solid var(--line)}
/* prose */
p{color:var(--ink2);margin-bottom:1.1em}
p:last-child{margin-bottom:0}
strong{color:var(--ink);font-weight:600}
em{color:var(--ink);font-style:italic}
code{font-family:var(--mono);font-size:.82em;color:var(--teal);
  background:var(--g3);padding:1px 5px;border-radius:3px}
ul,ol{padding-left:1.4em;margin-bottom:1em}
li{color:var(--ink2);margin-bottom:.4em}
li strong{color:var(--ink)}
blockquote{border-left:3px solid var(--teal);padding:12px 18px;margin:1.5em 0;
  background:var(--g2);border-radius:0 8px 8px 0}
blockquote p{color:var(--ink2);margin:0}
/* footer */
footer{padding:48px 0 60px;color:var(--ink3);font-family:var(--mono);font-size:.7rem;
  border-top:1px solid var(--line2);margin-top:2em}
footer a{color:var(--teal);text-decoration:none}
"""

ALL_VENUES_NAV = [
    ("mlsys",    "MLSys"),
    ("isca",     "ISCA"),
    ("micro",    "MICRO"),
    ("hpca",     "HPCA"),
    ("asplos",   "ASPLOS"),
    ("dac",      "DAC"),
    ("isscc",    "ISSCC"),
    ("hotchips", "Hot Chips"),
    ("sc",       "SC"),
    ("vlsid",    "VLSID"),
    ("cgo",      "CGO"),
    ("iccad",    "ICCAD"),
    ("date",     "DATE"),
    ("osdi",     "OSDI"),
    ("usenix",   "ATC"),
    ("fccm",     "FCCM"),
]

def esc(s): return html.escape(str(s or ""))

def inline(s):
    s = esc(s)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    s = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'\*(.+?)\*', r'<em>\1</em>', s)
    return s

def convert(md):
    lines = md.splitlines()
    out = []
    in_ul = in_ol = False
    skip_h1 = True

    def close_lists():
        nonlocal in_ul, in_ol
        if in_ul: out.append('</ul>'); in_ul = False
        if in_ol: out.append('</ol>'); in_ol = False

    for line in lines:
        s = line.strip()

        if s.startswith('# '):
            skip_h1 = False
            continue  # title rendered in hero
        if skip_h1:
            continue
        if s == '---':
            close_lists(); out.append('<hr style="border:none;border-top:1px solid var(--line);margin:2em 0">'); continue
        if s.startswith('## '):
            close_lists()
            out.append(f'<h2>{inline(s[3:])}</h2>')
            continue
        if s.startswith('#### '):
            close_lists()
            out.append(f'<h4>{inline(s[5:])}</h4>')
            continue
        if s.startswith('### '):
            close_lists()
            out.append(f'<h3>{inline(s[4:])}</h3>')
            continue
        if s.startswith('- ') or s.startswith('* '):
            if not in_ul: close_lists(); out.append('<ul>'); in_ul = True
            out.append(f'<li>{inline(s[2:])}</li>'); continue
        m = re.match(r'^(\d+)\.\s+(.*)', s)
        if m:
            if not in_ol: close_lists(); out.append('<ol>'); in_ol = True
            out.append(f'<li>{inline(m.group(2))}</li>'); continue
        close_lists()
        if not s: continue
        if s.startswith('> '):
            out.append(f'<blockquote><p>{inline(s[2:])}</p></blockquote>'); continue
        out.append(f'<p>{inline(s)}</p>')

    close_lists()
    return '\n'.join(out)

def build_venue_nav(cur_conf, year):
    pills = []
    for conf, label in ALL_VENUES_NAV:
        href = f"{conf}-{year}-bigpicture.html"
        cls = ' class="cur"' if conf == cur_conf else ''
        pills.append(f'<a href="{href}"{cls}>{esc(label)}</a>')
    return '<nav class="venue-nav">' + ''.join(pills) + '</nav>'

def build_page(md_path):
    stem = md_path.stem
    if '-deepdive' in stem:
        conf, year = stem.replace('-deepdive', '').rsplit('-', 1)
    else:
        conf, year = stem.replace('-bigpicture', '').rsplit('-', 1)
    short, domain = VENUES.get(conf, (conf.upper(), ""))
    md = md_path.read_text()

    # extract title from first # line
    title_m = re.search(r'^#\s+(.+)$', md, re.M)
    title = title_m.group(1) if title_m else f"{short} {year}"

    body_html = convert(md)
    venue_nav = build_venue_nav(conf, year)

    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} · Big Picture</title>
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
  <div class="top">
    <a class="back" href="index.html">← master narrative</a>
    <a class="back" href="deepdives.html">deep dives</a>
    <a class="back" href="explorer.html">explorer</a>
  </div>
  {venue_nav}
  <header class="hero">
    <div class="eyebrow">AI Hardware 2025 · {esc(domain)}</div>
    <h1>{esc(title)}</h1>
    <div class="sub">First-principles overview — the problem, the approaches, where it fits</div>
  </header>
  {body_html}
  <footer>
    AI Hardware 2025 · {esc(short)} big picture · written by Haiku from venue digest and sampled paper JSONs ·
    <a href="index.html">master narrative</a> · <a href="explorer.html">explorer</a> · <a href="deepdives.html">deep dives</a>
  </footer>
</div>
</body>
</html>"""

    out = ROOT / f"{conf}-{year}-bigpicture.html"
    out.write_text(page)
    return out, out.stat().st_size // 1024

def main():
    # prefer deepdive over bigpicture for each venue
    seen = {}
    for md in sorted(SYNTH.glob("*-2025-*.md")):
        if 'deepdive' not in md.stem and 'bigpicture' not in md.stem:
            continue
        stem = md.stem
        if '-deepdive' in stem:
            conf = stem.replace('-2025-deepdive', '')
        else:
            conf = stem.replace('-2025-bigpicture', '')
        # deepdive wins over bigpicture
        if conf not in seen or 'deepdive' in md.stem:
            seen[conf] = md
    for conf, md in sorted(seen.items()):
        out, kb = build_page(md)
        print(f"  {out.name} ({kb}KB)")
    print(f"built {len(seen)} venue pages")

if __name__ == "__main__":
    main()
