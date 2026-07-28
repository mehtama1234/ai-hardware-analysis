#!/usr/bin/env python3
"""Build a styled HTML page from cross-venue-2025-themes.md."""
import re, html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC  = ROOT / "analysis/syntheses/cross-venue-2025-themes.md"
OUT  = ROOT / "synthesis.html"

CSS = """
:root{--g0:#0f1218;--g1:#14171d;--g2:#1a1f28;--g3:#222834;
--line:#2b323d;--line2:#20262f;
--ink:#e8e4dc;--ink2:#b0b8c4;--ink3:#737d8a;
--teal:#3fbfb0;--orange:#e09050;--red:#d95a4a;
--serif:Palatino,"Palatino Linotype",Charter,Georgia,serif;
--mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace;
--sans:system-ui,-apple-system,"Segoe UI",sans-serif;}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--g0);color:var(--ink);font-family:var(--sans);font-size:16px;
line-height:1.72;-webkit-font-smoothing:antialiased}
.wrap{max-width:780px;margin:0 auto;padding:0 clamp(20px,5vw,40px) 80px}
.top{padding:28px 0 6px;display:flex;gap:16px;align-items:center;flex-wrap:wrap}
.back{font-family:var(--mono);font-size:.73rem;color:var(--ink3);text-decoration:none}
.back:hover{color:var(--teal)}
.nav-pills{display:flex;gap:8px;flex-wrap:wrap;padding:14px 0 28px;border-bottom:1px solid var(--line)}
.nav-pills a{font-family:var(--mono);font-size:.68rem;letter-spacing:.08em;text-transform:uppercase;
color:var(--ink3);text-decoration:none;padding:4px 10px;border:1px solid var(--line2);border-radius:20px}
.nav-pills a:hover{color:var(--teal);border-color:var(--teal)}
header.hero{padding:36px 0 28px;border-bottom:1px solid var(--line)}
header.hero .ey{font-family:var(--mono);font-size:.7rem;letter-spacing:.2em;text-transform:uppercase;
color:var(--orange);margin-bottom:.6em}
header.hero h1{font-family:var(--serif);font-size:clamp(2rem,5vw,3rem);font-weight:600;
color:var(--ink);line-height:1.1;margin-bottom:.4em;text-wrap:balance}
header.hero .sub{font-family:var(--serif);font-size:1.15rem;color:var(--ink2)}
header.hero .meta{font-family:var(--mono);font-size:.72rem;color:var(--ink3);margin-top:14px}
h2{font-family:var(--serif);font-size:1.65rem;font-weight:600;color:var(--ink);
margin:3em 0 .7em;padding-top:1.5em;border-top:1px solid var(--line2);line-height:1.15;text-wrap:balance}
h2:first-of-type{border-top:none;margin-top:2em}
h3{font-family:var(--serif);font-size:1.22rem;font-weight:600;color:var(--ink);margin:1.8em 0 .5em}
p{color:var(--ink2);margin-bottom:1em}
strong{color:var(--ink);font-weight:600}
em{color:var(--ink);font-style:italic}
code{font-family:var(--mono);font-size:.82em;color:var(--teal);background:var(--g3);
padding:1px 5px;border-radius:3px;white-space:nowrap}
ul,ol{padding-left:1.4em;margin-bottom:1em}
li{color:var(--ink2);margin-bottom:.35em}
li strong{color:var(--ink)}
li code{font-size:.8em}
blockquote{border-left:3px solid var(--teal);padding:12px 18px;margin:1.5em 0;
background:var(--g2);border-radius:0 8px 8px 0}
blockquote p{color:var(--ink2);margin:0}
hr{border:none;border-top:1px solid var(--line);margin:2.5em 0}
.caveat{background:var(--g2);border:1px solid var(--line);border-left:3px solid var(--orange);
border-radius:8px;padding:14px 18px;margin:1.5em 0}
.caveat p{margin:0;color:var(--ink2);font-size:.9rem}
footer{padding:40px 0 60px;color:var(--ink3);font-family:var(--mono);font-size:.73rem}
a{color:var(--teal);text-underline-offset:3px}
"""

def md_inline(s):
    """Convert inline markdown (bold, italic, code, links) to HTML."""
    s = html.escape(s)
    # code first (protect backtick content)
    s = re.sub(r'`([^`]+)`', lambda m: f'<code>{m.group(1)}</code>', s)
    # bold+italic
    s = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'\*(.+?)\*', r'<em>\1</em>', s)
    # links
    s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', s)
    return s

def convert(md):
    lines = md.splitlines()
    out = []
    in_ul = False
    in_ol = False
    skip_frontmatter = True

    def close_list():
        nonlocal in_ul, in_ol
        if in_ul: out.append('</ul>'); in_ul = False
        if in_ol: out.append('</ol>'); in_ol = False

    for line in lines:
        # skip the file-path comment at the very top
        stripped = line.strip()

        if stripped.startswith('# '):
            close_list()
            skip_frontmatter = False
            continue  # skip the top-level H1 (we render it in the hero)

        if skip_frontmatter:
            continue

        if stripped == '---':
            close_list()
            out.append('<hr>')
            continue

        if stripped.startswith('## '):
            close_list()
            text = md_inline(stripped[3:])
            # extract anchor from number prefix
            m = re.match(r'^(\d+)\.\s+\*\*(.+?)\*\*', stripped[3:])
            anchor = ''
            if m:
                anchor = f' id="s{m.group(1)}"'
            out.append(f'<h2{anchor}>{text}</h2>')
            continue

        if stripped.startswith('### '):
            close_list()
            out.append(f'<h3>{md_inline(stripped[4:])}</h3>')
            continue

        if stripped.startswith('- ') or stripped.startswith('* '):
            if not in_ul:
                close_list(); out.append('<ul>'); in_ul = True
            out.append(f'<li>{md_inline(stripped[2:])}</li>')
            continue

        m = re.match(r'^(\d+)\.\s+(.*)', stripped)
        if m:
            if not in_ol:
                close_list(); out.append('<ol>'); in_ol = True
            out.append(f'<li>{md_inline(m.group(2))}</li>')
            continue

        close_list()

        if stripped == '':
            continue

        if stripped.startswith('> '):
            out.append(f'<blockquote><p>{md_inline(stripped[2:])}</p></blockquote>')
            continue

        # detect coverage/caveat paragraph
        text = md_inline(stripped)
        if 'under-sampled' in stripped or 'Coverage' in stripped and 'confidence' in stripped.lower():
            out.append(f'<div class="caveat"><p>{text}</p></div>')
        else:
            out.append(f'<p>{text}</p>')

    close_list()
    return '\n'.join(out)

def main():
    md = SRC.read_text()

    # Extract title and subtitle from first heading + corpus line
    title = "Cross-Venue Synthesis — AI Hardware 2025"
    subtitle = "Six venues, one year: what the whole field is doing, where it agrees, where it diverges"
    meta_line = "MLSys · ISCA · MICRO · HPCA · ASPLOS · DAC &nbsp;·&nbsp; 719 papers · 603 analyzed · 120 read in full"

    # Section nav
    sections = [
        ("s1", "The big picture"),
        ("s2", "Per-venue character"),
        ("s3", "Shared themes"),
        ("s4", "What differs"),
        ("s5", "Cross-cutting"),
        ("s6", "Coverage"),
    ]
    nav = "".join(f'<a href="#{s}">{label}</a>' for s, label in sections)

    body = convert(md)

    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Cross-Venue Synthesis · AI Hardware 2025</title>
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
  <div class="top">
    <a class="back" href="deepdives.html">← deep dives</a>
    <a class="back" href="explorer.html">explorer</a>
    <a class="back" href="mlsys-2025-bigpicture.html">big picture</a>
  </div>
  <header class="hero">
    <div class="ey">AI Hardware 2025 · Cross-venue analysis</div>
    <h1>{title}</h1>
    <div class="sub">{subtitle}</div>
    <div class="meta">{meta_line}</div>
  </header>
  <nav class="nav-pills">{nav}</nav>
  {body}
  <footer>Six venues · 719 papers · Opus synthesis from per-venue digests and sampled paper JSONs ·
  <a href="deepdives.html">deep dives</a> · <a href="explorer.html">explorer</a></footer>
</div>
</body>
</html>"""

    OUT.write_text(page)
    print(f"wrote {OUT} ({OUT.stat().st_size // 1024}KB)")

if __name__ == "__main__":
    main()
