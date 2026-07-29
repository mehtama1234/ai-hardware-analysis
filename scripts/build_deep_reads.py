#!/usr/bin/env python3
"""Build deep-read HTML pages (t4-deep.html through t9-deep.html) from per-paper .md files.

Usage:
    python scripts/build_deep_reads.py

Reads:  analysis/themes/deep/T{N}/*.md
Writes: analysis/themes/deep/t{N}-deep.html  (for N in 4..9)
"""
import re
import html
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # ~/ui-projects/ai-hardware-analysis
DEEP = ROOT / "analysis" / "themes" / "deep"

THEMES = {
    4: {
        "slug": "interconnect",
        "name": "Interconnect &amp; Communication",
        "tagline": "network-on-chip, cross-chip messaging, bandwidth walls, and the physics of moving data",
        "color": "--cyan",
    },
    5: {
        "slug": "sparsity",
        "name": "Sparsity &amp; MoE",
        "tagline": "sparse expert routing, pruning, conditional compute, and skipping the math you don't need",
        "color": "--violet",
    },
    6: {
        "slug": "compiler",
        "name": "Compiler &amp; Scheduling",
        "tagline": "auto-tuning, kernel fusion, tiling, dataflow scheduling, and making hardware actually run fast",
        "color": "--amber",
    },
    7: {
        "slug": "security",
        "name": "Security &amp; Isolation",
        "tagline": "rowhammer, side-channels, trusted execution, and keeping secrets safe on shared silicon",
        "color": "--coral",
    },
    8: {
        "slug": "reliability",
        "name": "Reliability &amp; Verification",
        "tagline": "fault tolerance, formal verification, coherence protocols, and making hardware trustworthy",
        "color": "--violet",
    },
    9: {
        "slug": "specialized",
        "name": "Specialized Accelerators",
        "tagline": "quantum error correction, domain-specific ASICs, neuromorphic chips, and hardware built for one job",
        "color": "--cyan",
    },
}

CSS = """
:root {
  --bg:#0A0E13; --bg2:#0F1520; --bg3:#141c28;
  --ink:#E8E3D6; --ink2:#9AABB8; --ink3:#5B6B78;
  --cyan:#38E1CF; --amber:#F5A65B; --violet:#9C8CFF; --coral:#FF6B5C;
  --line:#1E2A38; --mono:ui-monospace,'SF Mono','Cascadia Code',Menlo,Consolas,monospace;
  --sans:system-ui,-apple-system,'Segoe UI',sans-serif;
  --serif:Palatino,'Palatino Linotype','Book Antiqua',Charter,Georgia,serif;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{background:var(--bg);color:var(--ink);font-family:var(--sans);
  font-size:15px;line-height:1.65;-webkit-font-smoothing:antialiased;
  background-image:repeating-linear-gradient(0deg,transparent,transparent 43px,var(--line) 43px,var(--line) 44px),
    repeating-linear-gradient(90deg,transparent,transparent 43px,var(--line) 43px,var(--line) 44px);}
.wrap{max-width:920px;margin:0 auto;padding:0 clamp(16px,4vw,48px) 80px}
a{color:var(--cyan);text-underline-offset:3px;text-decoration:none}
a:hover{text-decoration:underline}
.topnav{padding:20px 0 10px;display:flex;gap:14px;flex-wrap:wrap;align-items:center}
.topnav a{font-family:var(--mono);font-size:.68rem;color:var(--ink3);border:1px solid var(--line);
  padding:3px 9px;border-radius:12px}
.topnav a:hover{color:var(--cyan);border-color:var(--cyan)}
.hero{padding:32px 0 24px;border-bottom:1px solid var(--line);margin-bottom:28px}
.hero .eyebrow{font-family:var(--mono);font-size:.65rem;letter-spacing:.2em;
  text-transform:uppercase;color:var(--amber);margin-bottom:10px}
.hero h1{font-size:clamp(1.8rem,4vw,2.6rem);font-weight:700;color:var(--ink);
  line-height:1.1;letter-spacing:-.02em;font-family:var(--serif)}
.hero .sub{font-size:.95rem;color:var(--ink2);margin-top:8px;font-family:var(--serif);font-style:italic}
.paper-card{background:var(--bg2);border:1px solid var(--line);border-radius:8px;
  padding:18px 20px;margin-bottom:14px;cursor:pointer;transition:border-color .15s}
.paper-card:hover{border-color:var(--cyan)}
.paper-card .pc-head{display:flex;gap:12px;align-items:flex-start}
.paper-card .pc-venue{font-family:var(--mono);font-size:.62rem;letter-spacing:.1em;
  text-transform:uppercase;color:var(--amber);white-space:nowrap;padding-top:3px}
.paper-card .pc-title{font-size:.97rem;font-weight:600;color:var(--ink);line-height:1.3}
.paper-card .pc-sub{font-family:var(--mono);font-size:.62rem;color:var(--cyan);margin-top:4px}
.paper-card .pc-summary{font-size:.88rem;color:var(--ink2);margin-top:10px;line-height:1.5;display:none}
.paper-card.open .pc-summary{display:block}
.paper-card .pc-toggle{font-family:var(--mono);font-size:.65rem;color:var(--ink3);margin-top:10px}
.section-h{font-family:var(--mono);font-size:.7rem;letter-spacing:.18em;text-transform:uppercase;
  color:var(--ink3);margin:28px 0 12px;padding-bottom:6px;border-bottom:1px solid var(--line)}
footer{padding:32px 0 48px;font-family:var(--mono);font-size:.65rem;color:var(--ink3);
  border-top:1px solid var(--line);margin-top:32px}
""".strip()

JS = """
document.querySelectorAll('.paper-card').forEach(card => {
  card.addEventListener('click', () => {
    card.classList.toggle('open');
    const t = card.querySelector('.pc-toggle');
    t.textContent = card.classList.contains('open') ? '\\u25b2 collapse' : '\\u25bc read analysis';
  });
});
""".strip()


def parse_md(path: Path) -> dict:
    """Parse a deep-read .md file into structured fields."""
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")

    # Title = first # heading
    title = ""
    for ln in lines:
        if ln.startswith("# "):
            title = ln[2:].strip()
            break

    # Venue and subtheme from bold line
    venue = ""
    subtheme = ""
    m = re.search(r"\*\*Venue:\*\*\s*([^\s·]+)", text)
    if m:
        venue = m.group(1).strip().rstrip("·").strip()
    m = re.search(r"\*\*Subtheme:\*\*\s*(.+)", text)
    if m:
        subtheme = m.group(1).strip()

    # Split into sections by ## headings
    sections: dict[str, str] = {}
    current = None
    buf: list[str] = []
    for ln in lines:
        if ln.startswith("## "):
            if current is not None:
                sections[current] = "\n".join(buf).strip()
            current = ln[3:].strip()
            buf = []
        else:
            if current is not None:
                buf.append(ln)
    if current is not None:
        sections[current] = "\n".join(buf).strip()

    return {
        "title": title,
        "venue": venue,
        "subtheme": subtheme,
        "sections": sections,
    }


def md_to_html(text: str) -> str:
    """Convert simple markdown paragraphs / bullet lists to HTML spans."""
    out: list[str] = []
    paras = re.split(r"\n{2,}", text.strip())
    for para in paras:
        para = para.strip()
        if not para:
            continue
        # Detect bullet list block
        bullet_lines = [ln for ln in para.split("\n") if re.match(r"^[-*]\s", ln)]
        if len(bullet_lines) == len([ln for ln in para.split("\n") if ln.strip()]):
            for ln in para.split("\n"):
                ln = ln.strip()
                if re.match(r"^[-*]\s", ln):
                    content = ln[2:].strip()
                    content = apply_inline(content)
                    out.append(
                        f'<p style="font-size:.84rem;color:var(--ink2);padding-left:12px">{content}</p>'
                    )
        else:
            content = apply_inline(para.replace("\n", " "))
            out.append(
                f'<p style="font-size:.84rem;color:var(--ink2);margin-top:6px">{content}</p>'
            )
    return "\n".join(out)


def apply_inline(s: str) -> str:
    """Apply bold (**text**) and escape HTML entities."""
    # Escape HTML first (but preserve any already-escaped)
    s = html.escape(s, quote=False)
    # Bold
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    # Italic *text*
    s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
    return s


def render_section(label: str, content: str, color: str = "var(--ink)") -> str:
    html_content = md_to_html(content)
    label_escaped = html.escape(label)
    return (
        f'<p style="margin-top:12px;font-weight:700;color:{color};font-size:.88rem">'
        f"{label_escaped}</p>\n{html_content}"
    )


def paper_card_html(paper: dict) -> str:
    title = html.escape(paper["title"])
    venue = html.escape(paper["venue"].upper())
    subtheme = html.escape(paper["subtheme"])
    sections = paper["sections"]

    summary_parts: list[str] = []

    if "What It Does" in sections:
        summary_parts.append(render_section("What It Does", sections["What It Does"]))

    if "The Key Result" in sections:
        summary_parts.append(render_section("The Key Result", sections["The Key Result"]))

    if "Why This Approach" in sections:
        summary_parts.append(render_section("Why This Approach", sections["Why This Approach"]))

    if "What It Leaves Open" in sections:
        summary_parts.append(render_section("What It Leaves Open", sections["What It Leaves Open"]))

    summary_html = "\n".join(summary_parts)

    return f"""<div class="paper-card">
  <div class="pc-head">
    <div class="pc-venue">{venue}</div>
    <div>
      <div class="pc-title">{title}</div>
      <div class="pc-sub">{subtheme}</div>
    </div>
  </div>
  <div class="pc-summary">{summary_html}</div>
  <div class="pc-toggle">&#x25BC; read analysis</div>
</div>"""


def build_page(n: int) -> int:
    meta = THEMES[n]
    theme_dir = DEEP / f"T{n}"
    md_files = sorted(theme_dir.glob("*-deep.md"))

    if not md_files:
        print(f"  [skip] T{n}: no .md files found")
        return 0

    papers = [parse_md(f) for f in md_files]
    count = len(papers)

    # Group papers by subtheme, preserving first-seen order
    by_subtheme: dict[str, list[dict]] = {}
    for p in papers:
        key = p["subtheme"] or "General"
        by_subtheme.setdefault(key, []).append(p)

    # Build card HTML
    cards_html_parts: list[str] = []
    for subtheme, group in by_subtheme.items():
        subtheme_escaped = html.escape(subtheme)
        cards_html_parts.append(
            f'<div class="section-h">{subtheme_escaped}</div>'
        )
        for p in group:
            cards_html_parts.append(paper_card_html(p))
    cards_html = "\n".join(cards_html_parts)

    slug = meta["slug"]
    name = meta["name"]  # already HTML-safe (contains &amp; etc.)
    tagline = html.escape(meta["tagline"])
    name_plain = name.replace("&amp;", "&")

    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Deep Reads: {name_plain} &middot; AI Hardware 2025</title>
<style>
{CSS}
</style>
</head>
<body>
<div class="wrap">
  <div class="topnav">
    <a href="../../../index.html">&#x2190; master narrative</a>
    <a href="../../../t{n}-deepdive.html">T{n} theme essay &#x2197;</a>
    <a href="index.html">&#x2190; deep reads hub</a>
    <a href="../../../explorer.html">explorer</a>
  </div>
  <div class="hero">
    <div class="eyebrow">AI Hardware 2025 &middot; {name_plain} &middot; Deep Reads</div>
    <h1>{name}: Top Papers</h1>
    <div class="sub">{count} high-impact papers &middot; {tagline}</div>
  </div>
  {cards_html}
  <footer>
    AI Hardware 2025 &middot; {name_plain} deep reads &middot; {count} papers &middot; click any card to expand &middot;
    <a href="../../../index.html">master narrative</a> &middot; <a href="../../../explorer.html">explorer</a>
  </footer>
</div>
<script>
{JS}
</script>
</body>
</html>"""

    out_path = DEEP / f"t{n}-deep.html"
    out_path.write_text(page, encoding="utf-8")
    print(f"  wrote {out_path.name}  ({count} papers, {len(by_subtheme)} subthemes)")
    return count


def update_index(counts: dict[int, int]) -> None:
    """Append T4-T9 cards to deep/index.html."""
    index_path = DEEP / "index.html"
    text = index_path.read_text(encoding="utf-8")

    # Build new cards
    extra_cards: list[str] = []
    descriptions = {
        4: (
            "9 papers on network-on-chip design, cross-chip communication, bandwidth walls, "
            "in-network compute, and the physics of moving data between accelerators. "
            "The fundamental bottleneck that scales worse than compute."
        ),
        5: (
            "14 papers spanning mixture-of-experts routing, weight pruning, activation sparsity, "
            "conditional computation, and hardware support for skipping unnecessary arithmetic."
        ),
        6: (
            "15 papers covering auto-tuning, kernel fusion, polyhedral tiling, dataflow scheduling, "
            "CGRA mapping, and the compilers that make modern accelerators actually run fast."
        ),
        7: (
            "8 papers on rowhammer mitigations, side-channel attacks, trusted execution environments, "
            "memory safety, and keeping secrets safe on shared silicon."
        ),
        8: (
            "10 papers on formal verification of cache coherence protocols, fault tolerance, "
            "CXL reliability, error correction, and making hardware trustworthy by construction."
        ),
        9: (
            "15 papers on quantum error correction accelerators, neuromorphic chips, "
            "domain-specific ASICs, genomics processors, and hardware built for exactly one job."
        ),
    }
    slugs = {
        4: "Interconnect &amp; Communication",
        5: "Sparsity &amp; MoE",
        6: "Compiler &amp; Scheduling",
        7: "Security &amp; Isolation",
        8: "Reliability &amp; Verification",
        9: "Specialized Accelerators",
    }
    for n in range(4, 10):
        c = counts.get(n, 0)
        name = slugs[n]
        desc = descriptions[n]
        card = (
            f'  <div class="theme-card">\n'
            f'    <h2>T{n} &middot; {name}</h2>\n'
            f'    <div class="desc">{desc}</div>\n'
            f'    <div class="meta">{c} papers</div>\n'
            f'    <a class="btn" href="t{n}-deep.html">read T{n} papers &rarr;</a>\n'
            f'  </div>'
        )
        extra_cards.append(card)

    # Remove any existing T4–T9 cards that we previously injected
    for n in range(4, 10):
        text = re.sub(
            rf'  <div class="theme-card">\s*<h2>T{n}[^<]*</h2>.*?</div>\s*',
            "",
            text,
            flags=re.DOTALL,
        )

    # Insert before the footer
    insert = "\n".join(extra_cards) + "\n"
    text = text.replace("  <footer>", insert + "  <footer>")

    # Update footer count
    total = sum(counts.values())
    text = re.sub(
        r"(\d+) papers across T1/T2/T3",
        f"{45 + total} papers across T1–T9",
        text,
    )
    text = re.sub(
        r"Top high-impact papers from T1, T2, T3",
        "Top high-impact papers from T1–T9",
        text,
    )

    index_path.write_text(text, encoding="utf-8")
    print(f"  updated index.html  (added T4-T9 entries, total papers ~{45+total})")


def add_deepdive_link(n: int) -> None:
    """Add a 'deep reads' nav pill to t{N}-deepdive.html if not already present."""
    page = ROOT / f"t{n}-deepdive.html"
    if not page.exists():
        print(f"  [skip] t{n}-deepdive.html not found")
        return
    text = page.read_text(encoding="utf-8")
    marker = f"analysis/themes/deep/t{n}-deep.html"
    if marker in text:
        print(f"  t{n}-deepdive.html already has deep reads link")
        return

    # Insert after the back link
    link_html = (
        f'<a href="analysis/themes/deep/t{n}-deep.html" '
        f'style="font-family:var(--mono);font-size:.75rem;color:var(--supply);'
        f'text-decoration:none;border:1px solid #4fc1b155;padding:3px 10px;'
        f'border-radius:10px">deep reads &rarr;</a>'
    )
    # Try to insert after .top div's closing tag or after the <a class="back" ...> line
    text_new = re.sub(
        r'(<div class="top">.*?</div>)',
        lambda m: m.group(0) + f'\n  <div style="padding:6px 0 10px">{link_html}</div>',
        text,
        count=1,
        flags=re.DOTALL,
    )
    if text_new == text:
        print(f"  [warn] could not inject link into t{n}-deepdive.html")
        return
    page.write_text(text_new, encoding="utf-8")
    print(f"  updated t{n}-deepdive.html with deep reads link")


def main() -> None:
    print("Building deep-read pages T4–T9...")
    counts: dict[int, int] = {}
    for n in range(4, 10):
        counts[n] = build_page(n)

    print("\nUpdating deep/index.html...")
    update_index(counts)

    print("\nPatching t{N}-deepdive.html pages...")
    for n in range(4, 10):
        add_deepdive_link(n)

    print("\nDone.")
    for n, c in counts.items():
        print(f"  T{n}: {c} papers")


if __name__ == "__main__":
    main()
