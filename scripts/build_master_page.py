#!/usr/bin/env python3
"""Build the master first-principles narrative page from analysis/master-narrative.md."""
import re, html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC  = ROOT / "analysis/master-narrative.md"
OUT  = ROOT / "index.html"

THEME_LINKS = {
    "T1": "t1-deepdive.html",
    "T2": "t2-deepdive.html",
    "T3": "t3-deepdive.html",
    "T4": "t4-deepdive.html",
    "T5": "t5-deepdive.html",
    "T6": "t6-deepdive.html",
    "T7": "t7-deepdive.html",
    "T8": "t8-deepdive.html",
    "T9": "t9-deepdive.html",
    "T0": "t0-deepdive.html",
}

CSS = """
:root {
  --g0: #0d1117; --g1: #11161e; --g2: #161c26; --g3: #1c2330;
  --line: #272f3d; --line2: #1e2635;
  --ink: #e8e3d8; --ink2: #b8c0cc; --ink3: #7a8494;
  --teal: #3ec9b6; --orange: #e09858; --red: #d95a4a; --gold: #c9a84c;
  --serif: Palatino, "Palatino Linotype", "Book Antiqua", Charter, Georgia, serif;
  --mono: ui-monospace, "SF Mono", "Cascadia Code", Menlo, Consolas, monospace;
  --sans: system-ui, -apple-system, "Segoe UI", sans-serif;
}
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body {
  background: var(--g0); color: var(--ink); font-family: var(--serif);
  font-size: 18px; line-height: 1.78; -webkit-font-smoothing: antialiased;
}

/* layout */
.shell { display: grid; grid-template-columns: 240px 1fr; min-height: 100vh; }
.sidebar {
  position: sticky; top: 0; height: 100vh; overflow-y: auto;
  padding: 32px 20px 40px; border-right: 1px solid var(--line);
  background: var(--g1); display: flex; flex-direction: column; gap: 0;
}
.main { padding: 0 clamp(28px, 6vw, 80px) 120px; max-width: 820px; }

/* sidebar */
.site-label {
  font-family: var(--mono); font-size: .62rem; letter-spacing: .22em;
  text-transform: uppercase; color: var(--ink3); margin-bottom: 24px;
  padding-bottom: 16px; border-bottom: 1px solid var(--line2);
}
.nav-heading {
  font-family: var(--mono); font-size: .6rem; letter-spacing: .18em;
  text-transform: uppercase; color: var(--ink3); margin: 20px 0 8px;
}
.nav-link {
  display: block; font-family: var(--sans); font-size: .82rem;
  color: var(--ink3); text-decoration: none; padding: 5px 8px;
  border-radius: 6px; line-height: 1.35; margin-bottom: 2px;
  transition: color .15s, background .15s;
}
.nav-link:hover { color: var(--teal); background: var(--g2); }
.nav-link.theme { padding-left: 14px; }
.nav-divider { border: none; border-top: 1px solid var(--line2); margin: 16px 0; }
.sidebar-links { margin-top: auto; padding-top: 20px; border-top: 1px solid var(--line2); }
.sidebar-links a {
  display: block; font-family: var(--mono); font-size: .65rem;
  color: var(--ink3); text-decoration: none; padding: 4px 0;
}
.sidebar-links a:hover { color: var(--teal); }

/* hero */
.hero { padding: 60px 0 44px; border-bottom: 1px solid var(--line); }
.hero .eyebrow {
  font-family: var(--mono); font-size: .7rem; letter-spacing: .22em;
  text-transform: uppercase; color: var(--orange); margin-bottom: 20px;
}
.hero h1 {
  font-family: var(--serif); font-size: clamp(2.4rem, 5vw, 3.8rem);
  font-weight: 700; line-height: 1.06; color: var(--ink);
  text-wrap: balance; margin-bottom: .4em; letter-spacing: -.02em;
}
.hero .sub {
  font-family: var(--serif); font-size: 1.2rem; color: var(--ink2);
  font-style: italic; max-width: 560px; margin-bottom: 20px;
}
.hero .meta {
  font-family: var(--mono); font-size: .7rem; color: var(--ink3);
}

/* opening constraint section */
.constraint-block {
  padding: 48px 0 40px; border-bottom: 1px solid var(--line);
}
.constraint-block .sh {
  font-size: 1.85rem; color: var(--ink); margin-bottom: .7em;
}

/* bridge */
.bridge {
  padding: 36px 0; border-bottom: 1px solid var(--line);
  background: none;
}
.bridge .sh { font-size: 1.65rem; color: var(--ink); margin-bottom: .7em; }

/* theme sections */
.theme-section {
  padding: 48px 0 36px; border-bottom: 1px solid var(--line);
}
.theme-section .theme-slug {
  font-family: var(--mono); font-size: .65rem; letter-spacing: .2em;
  text-transform: uppercase; color: var(--teal); display: block; margin-bottom: 10px;
}
.theme-section h2 {
  font-size: 1.75rem; color: var(--ink); margin-bottom: .25em; line-height: 1.15;
  text-wrap: balance;
}
.theme-section .deepdive-link {
  font-family: var(--mono); font-size: .68rem; color: var(--ink3);
  text-decoration: none; letter-spacing: .05em;
}
.theme-section .deepdive-link:hover { color: var(--teal); }
.face {
  background: var(--g2); border-left: 3px solid var(--orange);
  border-radius: 0 8px 8px 0; padding: 14px 20px; margin: 20px 0 24px;
}
.face p { color: var(--ink2); margin: 0; font-size: .97rem; font-style: italic; }
.connects {
  background: var(--g2); border: 1px solid var(--line2);
  border-radius: 10px; padding: 16px 22px; margin-top: 24px;
}
.connects .cl {
  font-family: var(--mono); font-size: .62rem; letter-spacing: .16em;
  text-transform: uppercase; color: var(--teal); margin-bottom: 8px;
}
.connects p { color: var(--ink3); margin: 0; font-size: .95rem; }

/* closing section */
.closing { padding: 48px 0 80px; }
.closing h2 { font-size: 1.75rem; color: var(--ink); margin-bottom: .7em; }

/* prose */
.prose p { color: var(--ink2); margin-bottom: 1.1em; }
.prose p:last-child { margin-bottom: 0; }
.prose strong { color: var(--ink); font-weight: 600; }
.prose em { color: var(--ink); font-style: italic; }

/* big callout quote */
.callout {
  border-left: 3px solid var(--teal); padding: 16px 24px;
  margin: 28px 0; background: var(--g2); border-radius: 0 10px 10px 0;
}
.callout p { color: var(--ink); font-size: 1.05rem; margin: 0; font-style: italic; }

/* footer */
footer {
  padding: 40px 0 60px; color: var(--ink3);
  font-family: var(--mono); font-size: .7rem;
  border-top: 1px solid var(--line2); margin-top: 0;
}
footer a { color: var(--teal); text-decoration: none; }

/* links */
a { color: var(--teal); text-underline-offset: 3px; }

/* responsive */
@media (max-width: 800px) {
  .shell { grid-template-columns: 1fr; }
  .sidebar { position: static; height: auto; border-right: none;
    border-bottom: 1px solid var(--line); flex-direction: row;
    flex-wrap: wrap; gap: 4px; padding: 16px; }
  .nav-heading, .site-label, .nav-divider, .sidebar-links { display: none; }
  .nav-link { font-size: .75rem; padding: 4px 10px; border: 1px solid var(--line);
    border-radius: 20px; }
  .main { padding: 0 20px 80px; }
}
"""

SECTIONS = [
    ("constraint", "The one constraint"),
    ("bridge",     "Nine answers to one question"),
    ("t1", "T1 — Running notes"),
    ("t2", "T2 — Smaller numbers"),
    ("t3", "T3 — Math to the data"),
    ("t4", "T4 — Chips talking"),
    ("t5", "T5 — Skip the waste"),
    ("t6", "T6 — Describe hardware"),
    ("t7", "T7 — When shortcuts leak"),
    ("t8", "T8 — Knowing it's right"),
    ("t9", "T9 — Build for the job"),
    ("t0", "T0 — The other drawer"),
    ("closing", "Where it all points"),
]

def esc(s): return html.escape(str(s or ""))

def inline(s):
    s = esc(s)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    s = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'\*(.+?)\*', r'<em>\1</em>', s)
    return s

def render_paras(text):
    """Render a block of text as prose paragraphs, detecting Connects to: blocks."""
    if not text.strip(): return ""
    paragraphs = re.split(r'\n\s*\n', text.strip())
    out = []
    in_connects = False
    connects_buf = []

    for para in paragraphs:
        para = para.strip()
        if not para: continue
        if para.startswith("**Connects to:**") or para.startswith("**Connects to**"):
            in_connects = True
            connects_buf.append(para)
        elif in_connects:
            connects_buf.append(para)
        else:
            out.append(f'<p>{inline(para)}</p>')

    if connects_buf:
        body = " ".join(connects_buf)
        # strip the bold header
        body = re.sub(r'^\*\*Connects to[:\*]+\*\*\s*', '', body)
        out.append(
            f'<div class="connects"><div class="cl">Connects to</div>'
            f'<p>{inline(body)}</p></div>'
        )
    return "\n".join(out)

def parse_markdown(md):
    """Parse the markdown into structured sections."""
    lines = md.splitlines()
    title = subtitle = ""
    sections = []  # list of (anchor, h2_text, body_lines)
    cur_anchor = cur_title = None
    cur_body = []

    for line in lines:
        stripped = line.strip()
        # extract title
        if stripped.startswith("# "):
            title = stripped[2:]
            continue
        # extract italic subtitle
        if stripped.startswith("*") and stripped.endswith("*") and not title == "":
            subtitle = stripped.strip("*")
            continue
        if stripped == "---":
            continue
        if stripped.startswith("## "):
            # flush previous
            if cur_anchor is not None:
                sections.append((cur_anchor, cur_title, "\n".join(cur_body)))
            h2 = stripped[3:]
            # determine anchor
            m = re.match(r'^(T\d+)\s*[—–-]', h2)
            if m:
                cur_anchor = m.group(1).lower()
            elif "one constraint" in h2.lower():
                cur_anchor = "constraint"
            elif "nine answers" in h2.lower():
                cur_anchor = "bridge"
            elif "where it all" in h2.lower():
                cur_anchor = "closing"
            else:
                cur_anchor = re.sub(r'\W+', '-', h2.lower())[:20]
            cur_title = h2
            cur_body = []
        else:
            if cur_anchor is not None:
                cur_body.append(line)
    # flush last
    if cur_anchor is not None:
        sections.append((cur_anchor, cur_title, "\n".join(cur_body)))

    return title, subtitle, sections

def render_section(anchor, h2_text, body):
    # split face-of-constraint line from main body
    face = ""
    rest = body
    face_m = re.match(
        r'^\s*The specific face of the constraint[^:\n]*:(.+?)(?=\n\n|\Z)',
        body.strip(), re.S | re.I
    )
    if face_m:
        face_text = face_m.group(1).strip()
        rest = body[face_m.end():].strip()
        face = f'<div class="face"><p>{inline(face_text)}</p></div>'

    prose = render_paras(rest)

    # Theme section
    if re.match(r'^T\d', anchor.upper()):
        slug = anchor.upper()
        # strip "T1 — " from display
        display_title = re.sub(r'^T\d+\s*[—–-]\s*', '', h2_text)
        link_href = THEME_LINKS.get(slug, "#")
        return f'''<section class="theme-section" id="{anchor}">
  <span class="theme-slug">{slug}</span>
  <h2>{esc(display_title)}</h2>
  <a class="deepdive-link" href="{link_href}">read the full deep dive →</a>
  {face}
  <div class="prose">{prose}</div>
</section>'''

    if anchor == "constraint":
        return f'''<section class="constraint-block" id="{anchor}">
  <h2 class="sh">{esc(h2_text)}</h2>
  <div class="prose">{render_paras(body)}</div>
</section>'''

    if anchor == "bridge":
        return f'''<section class="bridge" id="{anchor}">
  <h2 class="sh">{esc(h2_text)}</h2>
  <div class="prose">{render_paras(body)}</div>
</section>'''

    if anchor == "closing":
        return f'''<section class="closing" id="{anchor}">
  <h2>{esc(h2_text)}</h2>
  <div class="prose">{render_paras(body)}</div>
</section>'''

    return f'''<section id="{anchor}">
  <h2>{esc(h2_text)}</h2>
  <div class="prose">{render_paras(body)}</div>
</section>'''


def build_sidebar():
    links = []
    links.append('<div class="site-label">AI Hardware 2025</div>')
    links.append('<div class="nav-heading">On this page</div>')
    links.append('<a class="nav-link" href="#constraint">The one constraint</a>')
    links.append('<a class="nav-link" href="#bridge">Nine answers</a>')
    links.append('<hr class="nav-divider">')
    links.append('<div class="nav-heading">The themes</div>')

    THEME_NAV = [
        ("t1", "T1 — Running notes"),
        ("t2", "T2 — Smaller numbers"),
        ("t3", "T3 — Math to the data"),
        ("t4", "T4 — Chips talking"),
        ("t5", "T5 — Skip the waste"),
        ("t6", "T6 — Describe hardware"),
        ("t7", "T7 — When shortcuts leak"),
        ("t8", "T8 — Knowing it's right"),
        ("t9", "T9 — Build for the job"),
        ("t0", "T0 — The other drawer"),
    ]
    for anchor, label in THEME_NAV:
        links.append(f'<a class="nav-link theme" href="#{anchor}">{esc(label)}</a>')

    links.append('<hr class="nav-divider">')
    links.append('<a class="nav-link" href="#closing">Where it points</a>')

    links.append('<hr class="nav-divider">')
    links.append('<div class="nav-heading">By venue</div>')
    for conf, label in [("mlsys","MLSys"),("isca","ISCA"),("micro","MICRO"),
                        ("hpca","HPCA"),("asplos","ASPLOS"),("dac","DAC"),
                        ("isscc","ISSCC"),("hotchips","Hot Chips"),
                        ("sc","SC"),("vlsid","VLSID"),("cgo","CGO"),("iccad","ICCAD")]:
        links.append(f'<a class="nav-link theme" href="{conf}-2025-bigpicture.html">{label}</a>')

    links.append('''<div class="sidebar-links">
  <a href="deepdives.html">deep dives hub</a>
  <a href="explorer.html">paper explorer</a>
  <a href="synthesis.html">cross-venue synthesis</a>
</div>''')

    return "\n".join(links)


def main():
    md = SRC.read_text()
    title, subtitle, sections = parse_markdown(md)

    sidebar = build_sidebar()
    body_sections = "\n".join(render_section(a, t, b) for a, t, b in sections)

    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>The Deep Read · AI Hardware 2025</title>
<style>{CSS}</style>
</head>
<body>
<div class="shell">
  <nav class="sidebar">{sidebar}</nav>
  <div class="main">
    <header class="hero">
      <div class="eyebrow">AI Hardware 2025 · The master narrative</div>
      <h1>One constraint.<br>Nine answers.</h1>
      <div class="sub">What 2,344 papers from fifteen venues are all really about — and how they connect.</div>
      <div class="meta">MLSys · ISCA · MICRO · HPCA · ASPLOS · DAC · ISSCC · Hot Chips · SC · VLSID · CGO · ICCAD · DATE · OSDI · USENIX ATC &nbsp;·&nbsp; 2,344 papers</div>
    </header>
    {body_sections}
    <footer>
      2,344 papers · 15 venues · First-principles narrative by Opus 4 from all theme intros and the cross-venue synthesis ·
      <a href="deepdives.html">deep dives</a> · <a href="explorer.html">explorer</a> · <a href="synthesis.html">cross-venue synthesis</a>
    </footer>
  </div>
</div>
</body>
</html>"""

    OUT.write_text(page)
    print(f"wrote {OUT} ({OUT.stat().st_size // 1024}KB)")


if __name__ == "__main__":
    main()
