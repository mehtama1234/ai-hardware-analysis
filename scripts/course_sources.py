"""Readable copies of the Markdown notes directly cited by the course.

Requires markdown-it-py. Source notes remain unchanged; no recursive export.
"""
import html
import os
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit, urlunsplit

from markdown_it import MarkdownIt


def source_href(href):
    url = urlsplit(href)
    if not url.scheme and not url.netloc and url.path.endswith('.md'):
        return urlunsplit(('', '', 'course-sources/' + url.path[:-3] + '.html', url.query, url.fragment))
    return href


def build_sources(root, sections, routes):
    references = {}
    for item, anchor in [(s, s['id']) for s in sections] + [(r, 'route-' + r['id']) for r in routes]:
        for href, label in item.get('sources', []):
            url = urlsplit(href)
            if not url.scheme and not url.netloc and url.path.endswith('.md'):
                references.setdefault(url.path, {})[anchor] = item['title']
    outputs = {path: root / urlsplit(source_href(path)).path for path in references}
    parser = MarkdownIt('commonmark', {'html': False}).enable('table')
    for path, returns in references.items():
        original = root / path
        destination = outputs[path]
        tokens = parser.parse(original.read_text())
        headings, used = [], set()
        for index, token in enumerate(tokens):
            if token.type == 'heading_open':
                title = tokens[index + 1].content
                slug = re.sub(r'[^\w\- ]', '', title.lower()).replace(' ', '-') or 'section'
                base, count = slug, 0
                while slug in used:
                    count += 1
                    slug = f'{base}-{count}'
                used.add(slug)
                token.attrSet('id', slug)
                if token.tag in ('h1', 'h2'):
                    headings.append((slug, title))
            for child in token.children or []:
                attribute = 'href' if child.type == 'link_open' else 'src' if child.type == 'image' else None
                if not attribute:
                    continue
                value = child.attrGet(attribute)
                url = urlsplit(value)
                if url.scheme or url.netloc or not url.path:
                    continue
                target = (original.parent / unquote(url.path)).resolve()
                try:
                    relative = target.relative_to(root).as_posix()
                except ValueError:
                    relative = None
                target = outputs.get(relative, target)
                child.attrSet(attribute, urlunsplit(('', '', os.path.relpath(target, destination.parent), url.query, url.fragment)))
        esc = html.escape
        course = os.path.relpath(root / 'course.html', destination.parent)
        backlinks = ''.join(f'<li><a href="{esc(course)}#{esc(anchor)}">{esc(title)}</a></li>' for anchor, title in returns.items())
        contents = ''.join(f'<li><a href="#{esc(slug)}">{esc(title)}</a></li>' for slug, title in headings)
        title = headings[0][1] if headings else original.stem
        raw = os.path.relpath(original, destination.parent)
        body = parser.renderer.render(tokens, parser.options, {})
        page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(title)} · Course source notes</title>
<style>
main p,main li{{overflow-wrap:anywhere}}
:root{{color-scheme:dark}}*{{box-sizing:border-box}}body{{margin:0;background:#10151d;color:#e8edf4;font:19px/1.75 Georgia,serif}}main,header,footer{{max-width:860px;margin:auto;padding:24px}}a{{color:#9dcfff;overflow-wrap:anywhere}}a:focus-visible,summary:focus-visible{{outline:3px solid #ffd78a;outline-offset:4px}}h1,h2,h3{{line-height:1.25;overflow-wrap:anywhere}}h1{{font-size:2rem}}h2{{margin-top:2.5rem}}header,footer,summary{{font-family:system-ui,sans-serif}}header{{border-bottom:1px solid #536074}}header p{{color:#c3cddb}}pre{{overflow:auto;padding:16px;background:#1b2636}}code{{overflow-wrap:anywhere;font-size:.88em}}img{{max-width:100%;height:auto}}table{{display:block;overflow:auto;border-collapse:collapse;font-size:.9rem}}th,td{{border:1px solid #536074;padding:8px;min-width:120px;text-align:left}}blockquote{{margin-left:0;padding-left:20px;border-left:3px solid #536074}}summary{{cursor:pointer;min-height:44px}}.skip{{position:absolute;left:12px;top:-100px}}.skip:focus{{top:12px;background:#10151d;padding:12px}}
</style></head><body><a class="skip" href="#source-text">Skip to source text</a>
<header><a href="{esc(course)}">Course home</a><p>Research notes, not a finished lesson. Evidence limits and historical status in these notes still apply. Formatting this page does not mean its claims have been independently checked.</p>
<details><summary>Return to a lesson or conference route</summary><ul>{backlinks}</ul></details>
<details><summary>On this page</summary><ul>{contents}</ul></details>
<p><a href="{esc(raw)}">Original Markdown</a></p></header>
<main id="source-text">{body}</main><footer><a href="{esc(course)}">Return to the course</a></footer></body></html>'''
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(page)
    return len(outputs)
