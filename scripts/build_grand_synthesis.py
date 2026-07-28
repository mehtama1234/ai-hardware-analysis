#!/usr/bin/env python3
"""Build grand-synthesis.html from grand-synthesis.md."""
import re, html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MD   = ROOT / "analysis/syntheses/grand-synthesis.md"
OUT  = ROOT / "grand-synthesis.html"

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
    in_ul = False
    title = ""
    skip_h1 = True

    def close_lists():
        nonlocal in_ul
        if in_ul:
            out.append('</ul>')
            in_ul = False

    for line in lines:
        s = line.strip()
        if s.startswith('# '):
            title = s[2:].strip()
            skip_h1 = False
            continue
        if skip_h1:
            continue
        if not s:
            close_lists()
            continue
        if s.startswith('## '):
            close_lists()
            heading = inline(s[3:])
            out.append(f'<hr class="divider"><h2 class="sec">{heading}</h2>')
            continue
        if s.startswith('### '):
            close_lists()
            heading = inline(s[4:])
            out.append(f'<h3 class="sub">{heading}</h3>')
            continue
        if s.startswith('- ') or s.startswith('* '):
            if not in_ul:
                out.append('<ul class="prose-list">')
                in_ul = True
            out.append(f'<li>{inline(s[2:])}</li>')
            continue
        close_lists()
        if s.startswith('> '):
            out.append(f'<blockquote class="pull">{inline(s[2:])}</blockquote>')
            continue
        out.append(f'<p>{inline(s)}</p>')

    close_lists()
    return title, '\n'.join(out)

THEME_NAV = [
    ("t1-deepdive.html", "T1 · Attention"),
    ("t2-deepdive.html", "T2 · Quantization"),
    ("t3-deepdive.html", "T3 · Memory Wall"),
    ("t4-deepdive.html", "T4 · Interconnects"),
    ("t5-deepdive.html", "T5 · Sparsity"),
    ("t6-deepdive.html", "T6 · Compilers"),
    ("t7-deepdive.html", "T7 · Security"),
    ("t8-deepdive.html", "T8 · Correctness"),
    ("t9-deepdive.html", "T9 · Beyond GPU"),
]

def build():
    md = MD.read_text()
    title, body = convert(md)

    pills = '\n  '.join(
        f'<a href="{href}">{esc(label)}</a>'
        for href, label in THEME_NAV
    )

    CSS = """
:root{
  --ground:#0d1117;--ground-2:#12161d;--ground-3:#161c24;--panel:#1a2030;
  --line:#252d3c;--line-soft:#1e2535;
  --ink:#ede9e1;--ink-dim:#b8c0cb;--ink-mute:#7a8698;
  --demand:#e89a5c;--supply:#42c4b2;--violet:#9c8cff;--warn:#e05858;
  --serif:"Iowan Old Style","Palatino Linotype",Palatino,Charter,Georgia,serif;
  --mono:ui-monospace,"SF Mono","Cascadia Code",Menlo,Consolas,monospace;
  --sans:system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{
  background:var(--ground);color:var(--ink);font-family:var(--serif);
  font-size:18px;line-height:1.75;-webkit-font-smoothing:antialiased;
  background-image:
    radial-gradient(ellipse 1200px 600px at 90% -5%, #1a2535 0%, transparent 65%),
    radial-gradient(ellipse 800px 500px at 10% 80%, #151f2e 0%, transparent 60%);
  background-attachment:fixed;
}
.wrap{max-width:820px;margin:0 auto;padding:0 clamp(22px,5vw,48px) 120px}
a{color:var(--supply);text-underline-offset:3px}
code{font-family:var(--mono);font-size:.82em;color:var(--supply);background:rgba(66,196,178,.1);padding:1px 5px;border-radius:3px}
strong,b{color:var(--ink);font-weight:600}
em,i{font-style:italic}

/* top */
.top{padding:32px 0 8px;display:flex;gap:16px;align-items:center;flex-wrap:wrap}
.back{font-family:var(--mono);font-size:.74rem;color:var(--ink-mute);text-decoration:none;letter-spacing:.02em}
.back:hover{color:var(--supply)}

/* hero — capstone treatment */
.hero{padding:40px 0 38px;border-bottom:2px solid var(--line)}
.hero .eyebrow{font-family:var(--mono);font-size:.7rem;letter-spacing:.28em;text-transform:uppercase;color:var(--supply);margin-bottom:18px}
.hero h1{
  font-family:var(--serif);font-size:clamp(2.5rem,6vw,4rem);
  font-weight:700;line-height:1.04;letter-spacing:-.025em;
  color:var(--ink);text-wrap:balance;margin-bottom:.25em
}
.hero .thesis{
  font-family:var(--serif);font-size:1.22rem;color:var(--demand);
  font-style:italic;line-height:1.42;max-width:640px;margin:.35em 0 1.1em
}
.hero .stats{
  display:flex;gap:28px;flex-wrap:wrap;font-family:var(--mono);
  font-size:.72rem;letter-spacing:.06em;color:var(--ink-mute);
  border-top:1px solid var(--line-soft);padding-top:16px;margin-top:8px
}
.hero .stats span b{color:var(--supply);font-weight:400}

/* theme nav */
.theme-nav{display:flex;flex-wrap:wrap;gap:7px;padding:20px 0 12px;border-bottom:1px solid var(--line-soft)}
.theme-nav .label{font-family:var(--mono);font-size:.68rem;letter-spacing:.12em;text-transform:uppercase;
  color:var(--ink-mute);align-self:center;padding-right:4px}
.theme-nav a{
  font-family:var(--mono);font-size:.7rem;letter-spacing:.05em;padding:5px 12px;
  border-radius:20px;text-decoration:none;border:1px solid var(--line);color:var(--ink-mute)
}
.theme-nav a:hover{border-color:var(--supply);color:var(--supply)}

/* essay body */
.essay{padding:56px 0 8px}
.divider{border:none;border-top:1px solid var(--line-soft);margin:50px 0 36px}
.sec{
  font-family:var(--serif);font-size:1.72rem;font-weight:600;color:var(--ink);
  padding-left:18px;border-left:3px solid var(--supply);line-height:1.15;
  text-wrap:balance;margin-bottom:.75em
}
.sub{
  font-family:var(--serif);font-size:1.22rem;color:var(--demand);
  margin:1.8em 0 .45em;line-height:1.2
}
p{color:var(--ink-dim);margin-bottom:1.05em;max-width:76ch}
p:last-child{margin-bottom:0}
p strong,p b{color:var(--ink)}
.prose-list{list-style:none;padding-left:1em;margin-bottom:1.1em;max-width:76ch}
.prose-list li{color:var(--ink-dim);margin-bottom:.45em;padding-left:.6em;position:relative}
.prose-list li::before{content:"·";color:var(--supply);position:absolute;left:-1em;font-size:1.1em}
.prose-list li strong,.prose-list li b{color:var(--ink)}
blockquote.pull{
  border-left:3px solid var(--demand);background:var(--ground-3);
  padding:14px 20px;margin:1.4em 0;border-radius:0 8px 8px 0;
  font-style:italic;color:var(--ink-dim)
}

/* footer */
footer{padding:48px 0 60px;color:var(--ink-mute);font-family:var(--mono);font-size:.72rem;
  border-top:1px solid var(--line-soft);margin-top:2em;line-height:1.8}
footer a{color:var(--supply);text-decoration:none}
:focus-visible{outline:2px solid var(--supply);outline-offset:3px}
"""

    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} · AI Hardware 2025</title>
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
  <div class="top">
    <a class="back" href="index.html">← master narrative</a>
    <a class="back" href="deepdives.html">deep dives</a>
    <a class="back" href="explorer.html">explorer</a>
    <a class="back" href="heatmap.html">heatmap</a>
  </div>

  <header class="hero">
    <div class="eyebrow">Grand Synthesis · AI Hardware 2025 · All Themes</div>
    <h1>{esc(title)}</h1>
    <div class="thesis">Arithmetic intensity is the single number every paper in this corpus is fighting. Here is how nine research communities are attacking it from different angles — and where they conflict.</div>
    <div class="stats">
      <span><b>2,090</b> papers analyzed</span>
      <span><b>9</b> first-principles themes</span>
      <span><b>13</b> venues · 2025</span>
      <span><b>Opus 4</b> synthesis</span>
    </div>
  </header>

  <nav class="theme-nav">
    <span class="label">Jump to theme →</span>
    {pills}
  </nav>

  <div class="essay">
{body}
  </div>

  <footer>
    AI Hardware 2025 · Grand Synthesis · written by Claude Opus from all 9 first-principles essays and 2,090 paper analyses ·
    <a href="index.html">master narrative</a> ·
    <a href="deepdives.html">all deep dives</a> ·
    <a href="explorer.html">explorer</a> ·
    <a href="heatmap.html">theme × venue heatmap</a>
  </footer>
</div>
</body>
</html>"""

    OUT.write_text(page)
    words = len(MD.read_text().split())
    print(f"Built {OUT.name} ({OUT.stat().st_size // 1024}KB) — essay: {words} words")

if __name__ == "__main__":
    build()
