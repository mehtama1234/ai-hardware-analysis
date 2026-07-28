#!/usr/bin/env python3
"""
build_theme_deepdives.py

Rebuilds t1-t9-deepdive.html pages by prepending a rich first-principles essay
section to each existing deepdive file.  The existing paper list (from the old
HTML) is preserved verbatim after the essay.

Also rewrites deepdives.html with one-line teasers drawn from the essays.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent

SYNTHESES = ROOT / "analysis" / "syntheses"

# ──────────────────────────────────────────────────────────────────────────────
# Theme metadata: (title, subtitle, paper_count_line) — all sourced from the
# existing hero sections in the t*-deepdive.html files.
# ──────────────────────────────────────────────────────────────────────────────
THEMES = {
    1: {
        "title": "Serving language models fast",
        "sub": "attention and the model&#x27;s running notes",
        "count": "207 papers · 43 read in full · 164 from the abstract",
        "papers": 207,
        "full": 43,
    },
    2: {
        "title": "Using smaller numbers",
        "sub": "rounding to save memory and time",
        "count": "134 papers · 16 read in full · 118 from the abstract",
        "papers": 134,
        "full": 16,
    },
    3: {
        "title": "The memory wall",
        "sub": "moving the math to where the data already is",
        "count": "325 papers · 27 read in full · 298 from the abstract",
        "papers": 325,
        "full": 27,
    },
    4: {
        "title": "When chips must talk to chips",
        "sub": "the wiring and messages between them",
        "count": "161 papers · 10 read in full · 151 from the abstract",
        "papers": 161,
        "full": 10,
    },
    5: {
        "title": "Skipping the work that doesn&#x27;t matter",
        "sub": "most of the numbers barely count",
        "count": "107 papers · 13 read in full · 94 from the abstract",
        "papers": 107,
        "full": 13,
    },
    6: {
        "title": "Describing hardware so a machine can build it",
        "sub": "compilers and chip generators",
        "count": "204 papers · 12 read in full · 192 from the abstract",
        "papers": 204,
        "full": 12,
    },
    7: {
        "title": "Trusting the machine",
        "sub": "attacks on chips, and the defenses",
        "count": "141 papers · 6 read in full · 135 from the abstract",
        "papers": 141,
        "full": 6,
    },
    8: {
        "title": "Being sure it&#x27;s actually correct",
        "sub": "silent errors, faults, and proofs",
        "count": "150 papers · 8 read in full · 142 from the abstract",
        "papers": 150,
        "full": 8,
    },
    9: {
        "title": "Beyond the GPU",
        "sub": "new kinds of chips, and new jobs for them",
        "count": "324 papers · 17 read in full · 307 from the abstract",
        "papers": 324,
        "full": 17,
    },
}

# ──────────────────────────────────────────────────────────────────────────────
# CSS for the new first-principles essay layer (injected once per file)
# ──────────────────────────────────────────────────────────────────────────────
ESSAY_CSS = """
/* ── first-principles essay ── */
.essay{padding:48px 0 8px}
.essay h2.sec{font-size:1.62rem;color:var(--ink);margin:0 0 .55em;padding-left:16px;
  border-left:3px solid var(--supply);line-height:1.2}
.essay h3.sub{font-size:1.18rem;color:var(--demand);margin:1.6em 0 .45em;font-family:var(--serif)}
.essay .prose p{color:var(--ink-dim);max-width:780px}
.essay .prose p b,.essay .prose b{color:var(--ink)}
.essay .prose ul{color:var(--ink-dim);padding-left:1.4em;margin:0 0 1em;max-width:780px}
.essay .prose ul li{margin-bottom:.35em;list-style:none;padding-left:.5em}
.essay .prose ul li::before{content:"·";color:var(--supply);margin-right:.55em;font-size:1.1em}
.essay blockquote.venue{background:var(--ground-2);border:1px solid var(--line);
  border-left:3px solid var(--demand);border-radius:8px;
  padding:14px 18px;margin:1em 0 1.2em;color:var(--ink-dim);font-size:.97rem}
.essay blockquote.venue p{margin:0;color:var(--ink-dim)}
.essay .essay-divider{border:none;border-top:1px solid var(--line-soft);margin:44px 0}
/* theme nav pills */
.theme-nav{display:flex;flex-wrap:wrap;gap:7px;padding:18px 0 10px;border-bottom:1px solid var(--line-soft)}
.theme-nav a{font-family:var(--mono);font-size:.7rem;letter-spacing:.06em;padding:5px 12px;
  border-radius:20px;text-decoration:none;border:1px solid var(--line);color:var(--ink-mute)}
.theme-nav a:hover{border-color:var(--supply);color:var(--supply)}
.theme-nav a.cur{border-color:var(--supply);background:rgba(79,193,177,.10);color:var(--supply)}
"""

# ──────────────────────────────────────────────────────────────────────────────
# Theme nav label abbreviations
# ──────────────────────────────────────────────────────────────────────────────
THEME_NAV_LABELS = {
    1: "T1 · Attention",
    2: "T2 · Quantization",
    3: "T3 · Memory Wall",
    4: "T4 · Interconnects",
    5: "T5 · Sparsity",
    6: "T6 · Compilers",
    7: "T7 · Security",
    8: "T8 · Correctness",
    9: "T9 · Beyond GPU",
}

# ──────────────────────────────────────────────────────────────────────────────
# Markdown → HTML conversion
# ──────────────────────────────────────────────────────────────────────────────

def md_inline(text: str) -> str:
    """Convert inline markdown: **bold**, `code`, backtick citations."""
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    # Inline code / backtick-wrapped paper IDs  → styled span
    text = re.sub(r'`([^`]+)`', r'<code style="font-family:var(--mono);font-size:.88em;color:var(--supply)">\1</code>', text)
    return text


def is_venue_line(line: str) -> bool:
    """Detect lines that start with an at-venue callout."""
    return bool(re.match(r'^(At |"At |\(At )', line.strip()))


def md_to_html_essay(md_text: str) -> str:
    """
    Convert the first-principles markdown essay to a rich HTML block.
    Returns a <div class="essay"> block without the h1 title line.
    """
    lines = md_text.split('\n')
    html_parts = []

    # Skip the h1 line (we use it for the hero instead)
    i = 0
    while i < len(lines) and not lines[i].startswith('# '):
        i += 1
    if i < len(lines):
        i += 1  # skip the h1

    in_list = False
    in_para = False
    para_buf = []

    def flush_para():
        nonlocal in_para, para_buf
        if para_buf:
            text = ' '.join(para_buf).strip()
            if text:
                # Detect venue callouts: lines that look like citation sentences
                if is_venue_line(text):
                    html_parts.append(f'<blockquote class="venue"><p>{md_inline(text)}</p></blockquote>')
                else:
                    html_parts.append(f'<p>{md_inline(text)}</p>')
        para_buf = []
        in_para = False

    def flush_list():
        nonlocal in_list
        if in_list:
            html_parts.append('</ul>')
            in_list = False

    while i < len(lines):
        line = lines[i]
        raw = line.rstrip()

        # H2: section divider
        if raw.startswith('## '):
            flush_para()
            flush_list()
            heading_text = raw[3:].strip()
            html_parts.append(f'<hr class="essay-divider"><h2 class="sec">{md_inline(heading_text)}</h2>')
            html_parts.append('<div class="prose">')
            i += 1
            continue

        # H3: subtheme header
        if raw.startswith('### '):
            flush_para()
            flush_list()
            heading_text = raw[4:].strip()
            html_parts.append(f'</div><h3 class="sub">{md_inline(heading_text)}</h3><div class="prose">')
            i += 1
            continue

        # H4: minor header — treat like h3 but smaller
        if raw.startswith('#### '):
            flush_para()
            flush_list()
            heading_text = raw[5:].strip()
            html_parts.append(f'</div><h3 class="sub" style="font-size:1rem;color:var(--ink-mute)">{md_inline(heading_text)}</h3><div class="prose">')
            i += 1
            continue

        # Bullet list item
        if raw.startswith('- ') or raw.startswith('* '):
            flush_para()
            if not in_list:
                html_parts.append('<ul>')
                in_list = True
            item_text = raw[2:].strip()
            html_parts.append(f'<li>{md_inline(item_text)}</li>')
            i += 1
            continue

        # Blank line
        if not raw.strip():
            flush_para()
            flush_list()
            i += 1
            continue

        # Regular paragraph text — accumulate
        flush_list()
        para_buf.append(raw.strip())
        in_para = True
        i += 1

    flush_para()
    flush_list()
    # Close any open prose div
    html_parts.append('</div>')

    return '<div class="essay">\n' + '\n'.join(html_parts) + '\n</div>'


# ──────────────────────────────────────────────────────────────────────────────
# Theme nav HTML
# ──────────────────────────────────────────────────────────────────────────────

def build_theme_nav(current_n: int) -> str:
    parts = ['<nav class="theme-nav">']
    for n in range(1, 10):
        label = THEME_NAV_LABELS[n]
        cls = ' class="cur"' if n == current_n else ''
        parts.append(f'  <a href="t{n}-deepdive.html"{cls}>{label}</a>')
    parts.append('</nav>')
    return '\n'.join(parts)


# ──────────────────────────────────────────────────────────────────────────────
# Existing HTML stripping helpers
# ──────────────────────────────────────────────────────────────────────────────

def extract_existing_css(html: str) -> str:
    """Pull the <style> block from the old HTML."""
    m = re.search(r'<style>(.*?)</style>', html, re.DOTALL)
    return m.group(1) if m else ''


def extract_papers_section(html: str) -> str:
    """
    Extract the <section> that contains the papers list (last big section).
    The papers section starts with class="sh" containing 'the papers'.
    """
    # Find the section with "the papers" heading
    m = re.search(r'(<section>.*?<span class="k">the papers</span>.*?</section>)', html, re.DOTALL)
    if m:
        return m.group(1)
    # Fallback: return everything after the last </section> that precedes footer
    parts = html.split('<section>')
    if len(parts) > 1:
        # The last section is the papers section
        return '<section>' + parts[-1].split('</section>')[0] + '</section>'
    return ''


def extract_footer(html: str) -> str:
    m = re.search(r'(<footer>.*?</footer>)', html, re.DOTALL)
    return m.group(1) if m else '<footer>AI Hardware 2025 · <a href="deepdives.html">back to hub</a></footer>'


# ──────────────────────────────────────────────────────────────────────────────
# Build one deepdive page
# ──────────────────────────────────────────────────────────────────────────────

def build_deepdive(n: int, md_text: str, old_html: str) -> str:
    theme = THEMES[n]
    title = theme["title"]
    sub = theme["sub"]
    count = theme["count"]
    papers = theme["papers"]

    # Extract pieces from old HTML
    old_css = extract_existing_css(old_html)
    papers_section = extract_papers_section(old_html)
    footer_html = extract_footer(old_html)

    # Convert essay markdown → HTML
    essay_html = md_to_html_essay(md_text)

    # Build theme nav
    theme_nav = build_theme_nav(n)

    # Compose the full page
    page = f"""<style>
{old_css}
{ESSAY_CSS}
</style>
<div class="wrap">
  <div class="top">
    <a class="back" href="deepdives.html">← all deep dives</a>
  </div>
  {theme_nav}
  <header class="hero">
    <div class="eyebrow">first-principles deep dive · T{n} of 9</div>
    <h1>{title}</h1>
    <div class="sub">{sub}</div>
    <div class="count">{count}</div>
  </header>

  {essay_html}

  {papers_section}
  <footer>{papers} papers in this theme · AI Hardware 2025 · <a href="deepdives.html">back to hub</a></footer>
</div>
"""
    return page


# ──────────────────────────────────────────────────────────────────────────────
# One-liner teasers for deepdives.html hub
# ──────────────────────────────────────────────────────────────────────────────

def extract_teaser(md_text: str, max_chars: int = 260) -> str:
    """
    Pull the first real paragraph of the essay (after the h1 and ## Problem heading)
    and trim it to max_chars.
    """
    lines = md_text.split('\n')
    # Skip until after "## The Problem" (or first h2)
    i = 0
    # skip h1
    while i < len(lines) and not lines[i].startswith('# '):
        i += 1
    i += 1
    # skip to first h2
    while i < len(lines) and not lines[i].startswith('## '):
        i += 1
    i += 1  # skip the h2 line itself
    # skip blank lines
    while i < len(lines) and not lines[i].strip():
        i += 1
    # collect the first paragraph
    para = []
    while i < len(lines) and lines[i].strip():
        para.append(lines[i].strip())
        i += 1
    text = ' '.join(para)
    # strip markdown bold/italics
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    if len(text) > max_chars:
        text = text[:max_chars].rsplit(' ', 1)[0] + '…'
    return text


# ──────────────────────────────────────────────────────────────────────────────
# Build deepdives.html hub
# ──────────────────────────────────────────────────────────────────────────────

def build_hub(teasers: dict) -> str:
    """Rebuild deepdives.html with updated teasers."""
    # Read the existing hub to preserve CSS and t0 card
    hub_path = ROOT / "deepdives.html"
    old_hub = hub_path.read_text()

    # Extract CSS from old hub
    old_css = extract_existing_css(old_hub)

    # Extract t0 card (theme 0 = "Everything else")
    t0_m = re.search(r'(<a class="card" href="t0-deepdive\.html">.*?</a>)', old_hub, re.DOTALL)
    t0_card = t0_m.group(1) if t0_m else ''

    # Build cards for t1-t9
    cards = []
    for n in range(1, 10):
        t = THEMES[n]
        teaser = teasers.get(n, '')
        # Escape HTML in teaser
        teaser_safe = teaser.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        card = f'''<a class="card" href="t{n}-deepdive.html"><h3>{t["title"]}</h3>
          <div class="sub">{t["sub"]}</div>
          <p style="color:var(--ink-dim);font-size:.95rem;margin:.2em 0 .6em">{teaser_safe}</p>
          <div class="m"><b>{t["papers"]}</b> papers · <b>{t["full"]}</b> read in full</div></a>'''
        cards.append(card)

    # Append t0 card
    if t0_card:
        cards.append(t0_card)

    cards_html = ''.join(cards)

    hub = f"""<style>
{old_css}
</style>
<div class="wrap">
  <header class="hero" style="border-bottom:1px solid var(--line);padding-top:44px">
    <div class="eyebrow" style="color:var(--demand)">AI hardware 2025 · deep dives</div>
    <h1 style="font-size:clamp(2.3rem,6vw,3.6rem);margin:.3em 0 .3em">Every theme, all the way down</h1>
    <div class="sub">Nine chapters. Each one builds the problem from first principles, walks the approaches, then explains every paper — the full method where the paper was openly available.</div>
    <div class="count">1,809 papers · 11 venues · 120 read in full text</div>
  </header>
  <section><div class="cards">{cards_html}</div></section>
  <footer>Start anywhere. Each chapter stands alone. · <a href="mlsys-2025-bigpicture.html">the one-page overview</a></footer>
</div>
"""
    return hub


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def main():
    rebuilt = []
    teasers = {}
    missing = []

    for n in range(1, 10):
        md_path = SYNTHESES / f"t{n}-firstprinciples.md"
        html_path = ROOT / f"t{n}-deepdive.html"

        if not md_path.exists():
            print(f"  [skip] t{n}: essay not found at {md_path}", file=sys.stderr)
            missing.append(n)
            continue

        if not html_path.exists():
            print(f"  [skip] t{n}: deepdive HTML not found at {html_path}", file=sys.stderr)
            missing.append(n)
            continue

        md_text = md_path.read_text()
        old_html = html_path.read_text()

        print(f"  building t{n}: {THEMES[n]['title']} …")
        new_html = build_deepdive(n, md_text, old_html)
        html_path.write_text(new_html)
        rebuilt.append(n)

        teaser = extract_teaser(md_text)
        teasers[n] = teaser
        print(f"    teaser: {teaser[:80]}…")

    print(f"\n  rebuilding deepdives.html hub …")
    hub_html = build_hub(teasers)
    (ROOT / "deepdives.html").write_text(hub_html)
    print(f"  deepdives.html updated.")

    print(f"\n  Done. Rebuilt: {len(rebuilt)} pages (T{',T'.join(str(x) for x in rebuilt)})")
    if missing:
        print(f"  Skipped: T{',T'.join(str(x) for x in missing)}")


if __name__ == "__main__":
    main()
