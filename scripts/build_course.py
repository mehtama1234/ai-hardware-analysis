#!/usr/bin/env python3
import html
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from course_spine import COURSE_SUBTITLE, COURSE_TITLE, INTRO, READING_PATH, SECTIONS


def esc(value):
    return html.escape(str(value or ""), quote=True)


def render_intro():
    return "".join(f"<p>{esc(p)}</p>" for p in INTRO)


def render_path():
    return "".join(f'<a href="{esc(href)}">{esc(label)}</a>' for href, label in READING_PATH)


def render_nav():
    return "".join(
        f'<a href="#s{idx}">{idx}. {esc(section["kicker"])}</a>'
        for idx, section in enumerate(SECTIONS, 1)
    )


def render_sections():
    parts = []
    for idx, section in enumerate(SECTIONS, 1):
        body = "".join(f"<p>{esc(p)}</p>" for p in section["body"])
        apps = "".join(f"<li>{esc(app)}</li>" for app in section["applications"])
        parts.append(
            f"""
<section class="part" id="s{idx}">
  <div class="kicker">{esc(section["kicker"])}</div>
  <h2>{idx}. {esc(section["title"])}</h2>
  <p class="summary">{esc(section["summary"])}</p>
  <div class="essay">{body}</div>
  <div class="uses"><h3>Where this shows up</h3><ul>{apps}</ul></div>
</section>"""
        )
    return "\n".join(parts)


PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<style>
:root{--g0:#0d1117;--g1:#11161e;--g2:#161c26;--line:#272f3d;--line2:#1e2635;--ink:#e8e3d8;--ink2:#b8c0cc;--ink3:#7a8494;--teal:#3ec9b6;--orange:#e09858;--serif:Palatino,"Palatino Linotype","Book Antiqua",Charter,Georgia,serif;--mono:ui-monospace,"SF Mono","Cascadia Code",Menlo,Consolas,monospace;--sans:system-ui,-apple-system,"Segoe UI",sans-serif}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--g0);color:var(--ink);font-family:var(--serif);font-size:18px;line-height:1.76;-webkit-font-smoothing:antialiased}.wrap{max-width:860px;margin:0 auto;padding:0 clamp(22px,5vw,48px)}
header{background:var(--g1);border-bottom:1px solid var(--line);padding:48px 0 42px}.bug{font-family:var(--mono);font-size:.68rem;letter-spacing:.22em;text-transform:uppercase;color:var(--teal);margin-bottom:16px}h1{font-size:clamp(2.4rem,6vw,4rem);line-height:1.04;letter-spacing:-.025em;margin:0 0 .3em}header p{max-width:66ch;color:var(--ink2);font-style:italic;font-size:1.16rem}
nav{position:sticky;top:0;z-index:2;background:rgba(13,17,23,.96);border-bottom:1px solid var(--line)}.navwrap{display:flex;gap:8px;overflow:auto;padding-top:10px;padding-bottom:10px}nav a{white-space:nowrap;font-family:var(--mono);font-size:.68rem;color:var(--ink3);text-decoration:none;background:var(--g1);border:1px solid var(--line2);border-radius:999px;padding:5px 9px}nav a:hover{color:var(--teal)}
.intro{background:var(--g1);border-left:3px solid var(--orange);border-radius:0 10px 10px 0;padding:20px 24px;margin:28px 0 18px}.intro p{color:var(--ink2);margin:0 0 12px}.intro p:last-child{margin-bottom:0}.path{border:1px solid var(--line);background:var(--g1);border-radius:10px;padding:16px 20px;margin:18px 0 24px}.path b{display:block;font-family:var(--mono);font-size:.66rem;letter-spacing:.16em;text-transform:uppercase;color:var(--ink3);margin-bottom:8px}.path a{display:inline-block;margin:4px 12px 4px 0;color:var(--teal);font-family:var(--sans);font-size:.92rem;text-decoration:none;border-bottom:1px solid rgba(62,201,182,.45)}
.part{border-bottom:1px solid var(--line);padding:34px 0}.kicker{font-family:var(--mono);font-size:.68rem;letter-spacing:.2em;text-transform:uppercase;color:var(--orange)}h2{font-size:clamp(1.75rem,4vw,2.35rem);line-height:1.12;letter-spacing:-.02em;margin:8px 0 8px}.summary{color:var(--ink3);font-family:var(--sans);font-size:1rem;margin:0 0 17px}.essay p{color:var(--ink2);margin:0 0 14px}.uses{background:var(--g1);border:1px solid var(--line2);border-left:3px solid var(--teal);border-radius:0 10px 10px 0;padding:15px 20px;margin-top:18px}.uses h3{font-family:var(--mono);font-size:.66rem;letter-spacing:.16em;text-transform:uppercase;color:var(--ink3);margin:0 0 8px}.uses ul{margin:0;padding-left:20px}.uses li{color:var(--ink2);margin:5px 0}
footer{padding:34px 0 70px;color:var(--ink3);font-family:var(--mono);font-size:.72rem}footer a{color:var(--teal);text-decoration:none}@media(max-width:720px){body{font-size:17px}.wrap{padding:0 20px}}
</style></head><body>
<header><div class="wrap"><div class="bug">AI hardware course spine</div><h1>__TITLE__</h1><p>__SUBTITLE__</p></div></header>
<nav><div class="wrap navwrap">__NAV__</div></nav>
<main class="wrap">
  <div class="intro">__INTRO__</div>
  <div class="path"><b>Read next</b>__PATH__</div>
  __SECTIONS__
  <footer>Part of the AI Hardware 2025 conference analysis. Continue to <a href="index.html">master narrative</a>, <a href="deepdives.html">deep dives</a>, or <a href="explorer.html">paper explorer</a>.</footer>
</main></body></html>
"""


def main():
    page = (
        PAGE.replace("__TITLE__", esc(COURSE_TITLE))
        .replace("__SUBTITLE__", esc(COURSE_SUBTITLE))
        .replace("__NAV__", render_nav())
        .replace("__INTRO__", render_intro())
        .replace("__PATH__", render_path())
        .replace("__SECTIONS__", render_sections())
    )
    (ROOT / "course.html").write_text(page)
    print(f"wrote course.html ({len(page) // 1024} KB, {len(SECTIONS)} sections)")


if __name__ == "__main__":
    main()
