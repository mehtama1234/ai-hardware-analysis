#!/usr/bin/env python3
import html
import sys
from pathlib import Path
from course_sources import build_sources, source_href

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from course_spine import COURSE_SUBTITLE, COURSE_TITLE, INTRO, READING_PATH, SECTIONS
from course_glossary import GLOSSARY
from course_routes import CONFERENCE_SCOPE, ROUTES, ROUTE_EVIDENCE_STATUS
from course_papers import PAPERS
from course_learning import CHECKPOINTS, PREREQUISITES
from course_comparisons import COMPARISONS
from course_coverage import coverage_for
from course_subtheme_notes import get_subtheme_note
from course_capstone import CAPSTONE_ID, render_capstone
from course_orientation import ORIENTATION_ID, render_orientation
from course_interactives import INTERACTIVE_SCRIPT, render_interactive


def esc(value):
    return html.escape('' if value is None else str(value), quote=True)


def render_example_table(table):
    """Render a small comparison with its units and scope in the supplied labels."""
    if not table.get('caption') or not table.get('headings') or not table.get('rows'):
        raise ValueError('Example tables need a caption, headings, and rows')
    if any(len(row) != len(table['headings']) for row in table['rows']):
        raise ValueError('Example table row does not match its headings')
    headers = ''.join(f'<th scope="col">{esc(label)}</th>' for label in table['headings'])
    rows = ''.join('<tr>' + ''.join(f'<td>{esc(value)}</td>' for value in row) + '</tr>' for row in table['rows'])
    return (f'<div class="table-wrap"><table><caption>{esc(table["caption"])}</caption>'
            f'<thead><tr>{headers}</tr></thead><tbody>{rows}</tbody></table></div>')


def render_intro():
    return "".join(f"<p>{esc(p)}</p>" for p in INTRO)


def render_path():
    links = "".join(f'<li><a href="{esc(href)}">{esc(label)}</a></li>' for href, label in READING_PATH)
    return ('<section class="part optional-research" id="optional-research-pages">'
            '<h2>Optional research pages</h2>'
            '<p>These broader syntheses and tools supplement the lessons and conference routes. '
            'Use them after the course or alongside a topic you want to explore further; they are not prerequisites.</p>'
            f'<ul>{links}</ul></section>')


def render_nav():
    return "".join(
        f'<a href="#{esc(section["id"])}">{idx}. {esc(section["kicker"])}</a>'
        for idx, section in enumerate(SECTIONS, 1)
    )


def render_contents():
    lessons = ''.join(f'<li><a href="#{esc(section["id"])}">{esc(section["title"])}</a></li>' for section in SECTIONS)
    routes = ''.join(f'<li><a href="#route-{esc(route["id"])}">{esc(route["title"])}</a></li>' for route in ROUTES)
    papers = ''.join(f'<li><a href="#paper-{esc(paper["id"])}">{esc(paper["title"])}</a></li>' for paper in PAPERS)
    return ('<details class="contents"><summary>Choose a lesson or conference route</summary>'
            '<p><a href="#' + ORIENTATION_ID + '">Learning outcomes and starting-point check</a></p>'
            '<h2>Lessons in order</h2><ol>' + lessons + '</ol><h2>Conference routes</h2><ul>' + routes +
            '</ul><p><a href="#cross-conference-questions">Compare ideas across conferences</a></p><p><a href="#course-checkpoints">Practice across lessons</a></p><h2>Paper walkthroughs</h2><ul>' + papers + '</ul><p><a href="#' + CAPSTONE_ID + '">Final paper challenge</a></p><p><a href="#concept-lookup">Look up a concept</a></p><p><a href="#optional-research-pages">Optional research pages</a></p></details>')


def render_sections():
    parts = []
    for idx, section in enumerate(SECTIONS, 1):
        labels = {s['id']: s['kicker'] for s in SECTIONS}
        prerequisite_links = ' · '.join(f'<a href="#{esc(key)}">{esc(labels[key])}</a>' for key in PREREQUISITES[section['id']])
        prerequisite_links = f'<p class="concept-links">Review first: {prerequisite_links}</p>' if prerequisite_links else '<p class="concept-links">Start here. No earlier lesson is required.</p>'
        body = "".join(f"<p>{esc(p)}</p>" for p in section["body"])
        interactive = render_interactive(section.get("interactive"), esc)
        apps = "".join(f"<li>{esc(app)}</li>" for app in section["applications"])
        exercise = section.get("exercise")
        practice = (f'<aside class="uses"><h3>Work it through</h3><p>{esc(exercise["question"])}</p>'
                    f'<details><summary>Read the reasoning</summary><p>{esc(exercise["answer"])}</p></details></aside>') if exercise else ""
        sources = "".join(f'<li><a href="{esc(source_href(href))}">{esc(label)}</a></li>' for href, label in section.get("sources", []))
        references = f'<aside class="uses"><h3>Sources and further reading</h3><ul>{sources}</ul></aside>' if sources else ""
        steps = []
        if idx > 1:
            previous = SECTIONS[idx - 2]
            steps.append(f'<a href="#{esc(previous["id"])}">Previous: {esc(previous["kicker"])}</a>')
        if idx < len(SECTIONS):
            following = SECTIONS[idx]
            steps.append(f'<a href="#{esc(following["id"])}">Next: {esc(following["kicker"])}</a>')
        steps.append('<a href="#concept-lookup">Concept lookup</a>')
        navigation = '<div class="lesson-links" role="navigation" aria-label="Lesson navigation">' + " ".join(steps) + '</div>'
        terms = " · ".join(
            f'<a href="#term-{esc(key)}">{esc(label)}</a>'
            for key, label, definition, lesson in GLOSSARY if lesson == section['id']
        )
        concept_links = f'<p class="concept-links">Key concepts: {terms}</p>' if terms else ""
        table = section.get('table')
        worked_table = ''
        if table:
            headers = ''.join(f'<th scope="col">{esc(label)}</th>' for label in table['headings'])
            rows = ''.join('<tr>' + ''.join(f'<td>{esc(value)}</td>' for value in row) + '</tr>' for row in table['rows'])
            worked_table = f'<div class="table-wrap"><table><caption>{esc(table["caption"])}</caption><thead><tr>{headers}</tr></thead><tbody>{rows}</tbody></table></div>'
            after = section.get('table_after_paragraph')
            if after is not None:
                if not isinstance(after, int) or not 1 <= after <= len(section['body']):
                    raise ValueError(f'Invalid table position: {section["id"]}')
                paragraphs = [f'<p>{esc(p)}</p>' for p in section['body']]
                paragraphs.insert(after, worked_table)
                body = ''.join(paragraphs)
                worked_table = ''
        parts.append(
            f"""
<section class="part" id="{esc(section['id'])}">
  <div class="kicker">{esc(section["kicker"])}</div>
  <h2>{idx}. {esc(section["title"])}</h2>
  <p class="summary">{esc(section["summary"])}</p>
  {prerequisite_links}{concept_links}
  {worked_table}<div class="essay">{body}</div>{interactive}
  <div class="uses"><h3>Where this shows up</h3><ul>{apps}</ul></div>
  {practice}{references}{navigation}
</section>"""
        )
    return "\n".join(parts)


def render_glossary():
    lessons = {section['id']: section['kicker'] for section in SECTIONS}
    entries = []
    for key, label, definition, lesson in sorted(GLOSSARY, key=lambda term: term[1].casefold()):
        if lesson not in lessons:
            raise ValueError(f'Unknown lesson for glossary term {key}: {lesson}')
        entries.append(
            f'<div class="term" id="term-{esc(key)}"><dt>{esc(label)}</dt>'
            f'<dd>{esc(definition)} <a href="#{esc(lesson)}">Read the {esc(lessons[lesson])} lesson</a>.</dd></div>'
        )
    return ('<section class="part" id="concept-lookup"><h2>Concept lookup</h2>'
            '<p>Short definitions help you find your place. Follow a lesson link for the assumptions, examples, and failure cases.</p>'
            '<dl>' + ''.join(entries) + '</dl><a href="#course-content">Back to the start</a></section>')


def render_checkpoints():
    parts = ['<section class="part" id="course-checkpoints"><h2>Practice across lessons</h2>'
             '<p>Try these before opening the reasoning. Write down your timing boundary, assumptions, '
             'and acceptance condition as well as your answer. All scenarios are invented teaching examples.</p>']
    for item in CHECKPOINTS:
        review = ' · '.join(f'<a href="#{esc(key)}">{esc(label)}</a>' for key, label in item['review'])
        parts.append(f'<article id="{esc(item["id"])}"><h3>{esc(item["title"])}</h3>'
                     f'<p>{esc(item["setup"])}</p><p>{esc(item["question"])}</p>'
                     f'<details><summary>Read the reasoning</summary><p>{esc(item["answer"])}</p></details>'
                     f'<p>Review if needed: {review}</p></article>')
    return ''.join(parts) + '<p><a href="#conference-routes">Continue to a conference route</a></p></section>'


def render_comparisons():
    parts = ['<section class="part" id="cross-conference-questions"><h2>Follow one question across conferences</h2>'
             '<p>These connections are teaching interpretations of the course material, not a shared experiment or an official conference taxonomy. '
             'Choose a question, follow the worked explanation, then use the links to compare mechanisms and evidence.</p><ul>']
    parts.extend(f'<li><a href="#{esc(item["id"])}">{esc(item["title"])}</a></li>' for item in COMPARISONS)
    parts.append('</ul>')
    for item in COMPARISONS:
        parts.append(f'<article id="{esc(item["id"])}"><h3>{esc(item["title"])}</h3>')
        parts.extend(f'<p>{esc(p)}</p>' for p in item['paragraphs'])
        links = ''.join(f'<li><a href="#{esc(key)}">{esc(label)}</a></li>' for key, label in item['links'])
        parts.append(f'<h4>Reading path</h4><ul>{links}</ul><aside class="uses"><h4>Check the distinction</h4>'
                     f'<p>{esc(item["question"])}</p><details><summary>Read the reasoning</summary>'
                     f'<p>{esc(item["answer"])}</p></details></aside></article>')
    return ''.join(parts) + '</section>'


def render_routes():
    parts = ['<section class="part" id="conference-routes"><h2>Conference reading routes</h2>'
             '<p>Start with the common lessons, then follow the questions through a conference. '
             'Every listed route has theme and subtheme teaching blocks, worked examples, and explained theme exercises. '
             'Those counts describe course material, not how much of a conference was read or how strong its paper evidence is. '
             'Read each route’s evidence notice before extending a claim.</p>']
    parts.append('<ul>' + ''.join(f'<li><a href="#route-{esc(route["id"])}">{esc(route["title"])}</a></li>' for route in ROUTES) + '</ul>')
    drafted = {route['id']: route for route in ROUTES}
    route_status = {route['id']: route.get('coverage_status', ROUTE_EVIDENCE_STATUS[route['id']]) for route in ROUTES}
    coverage = []
    for key, label in CONFERENCE_SCOPE:
        name = f'<a href="#route-{esc(key)}">{esc(label)}</a>' if key in drafted else esc(label)
        status = route_status.get(key, 'Teaching route not yet drafted')
        components = ''
        if key in drafted:
            counts = coverage_for(drafted[key], PAPERS)
            components = (f'<p>{counts["themes"]} theme explanations · {counts["subthemes"]} subtheme entries.</p>'
                          f'<p>Dedicated worked-example blocks: {counts["worked_themes"]}/{counts["themes"]} themes. '
                          f'Explained theme exercises: {counts["practice_themes"]}/{counts["themes"]}. '
                          f'Focused paper walkthroughs: {counts["papers"]}.</p>')
        coverage.append(f'<tr id="coverage-{esc(key)}"><th scope="row">{name}</th><td>{components}</td>'
                        f'<td>{esc(status)}</td></tr>')
    parts.append('<div class="table-wrap"><table class="coverage-table"><caption>Course-writing coverage, not a rating of the underlying paper evidence. '
                 'Teaching counts describe explicit course components, not proceedings completeness or source quality. Inline examples and shared lessons are not counted as dedicated theme blocks. '
                 'Each route’s evidence notice below gives the fuller source limit.</caption><thead><tr><th scope="col">Conference</th>'
                 '<th scope="col">Teaching coverage</th><th scope="col">Evidence status</th></tr></thead><tbody>' + ''.join(coverage) + '</tbody></table></div>')
    for route in ROUTES:
        parts.append(f'<article id="route-{esc(route["id"])}"><h3>{esc(route["title"])}</h3>'
                     f'<p class="summary">{esc(route["status"])}</p><p>{esc(route["intro"])}</p>'
                     f'<aside class="uses"><h4>Evidence boundary</h4><p>{esc(route["evidence"])}</p></aside>')
        for paper in PAPERS:
            if paper['route'] == route['id']:
                parts.append(f'<p><a href="#paper-{esc(paper["id"])}">Paper walkthrough: {esc(paper["title"])}</a></p>')
        for index, theme in enumerate(route['themes'], 1):
            subtheme_parts = []
            for sub_number, (title, body) in enumerate(theme['subthemes'], 1):
                detail = get_subtheme_note(route['id'], index, sub_number)
                if detail:
                    teaching = (f'<div class="subtheme-detail"><b>Apply it</b><p>{esc(detail["example"])}</p>'
                                f'<p><b>Where it fails:</b> {esc(detail["failure"])}</p>'
                                f'<p><b>Evidence boundary:</b> {esc(detail["evidence"])}</p>'
                                f'<p><a href="{esc(detail["source"])}">Inspect the named source</a></p></div>')
                else:
                    teaching = ('<span class="subtheme-test">Apply it below: name the quantity that changes, '
                                'the cost it adds or removes, and the condition under which the argument stops holding.</span>')
                subtheme_parts.append(f'<dt>{esc(title)}</dt><dd>{esc(body)}{teaching}</dd>')
            subthemes = ''.join(subtheme_parts)
            lessons = ' · '.join(f'<a href="#{esc(key)}">{esc(title)}</a>' for key, title in theme['lessons'])
            worked = ''
            if theme.get('worked_example'):
                paragraphs = [f'<p>{esc(p)}</p>' for p in theme['worked_example']]
                if theme.get('worked_table'):
                    after = theme.get('table_after_paragraph', len(paragraphs))
                    if not isinstance(after, int) or not 1 <= after <= len(paragraphs):
                        raise ValueError(f'Invalid theme table position: {theme["title"]}')
                    paragraphs.insert(after, render_example_table(theme['worked_table']))
                worked = '<div class="uses"><h5>Worked teaching example</h5>' + ''.join(paragraphs) + '</div>'
            practice = ''
            if theme.get('practice'):
                answer_table = render_example_table(theme['practice']['table']) if theme['practice'].get('table') else ''
                practice = (f'<aside class="uses"><h5>Check your reasoning</h5><p>{esc(theme["practice"]["question"])}</p>'
                            f'<details><summary>Read the reasoning</summary><p>{esc(theme["practice"]["answer"])}</p>{answer_table}</details></aside>')
            parts.append(f'<section class="route-theme" id="route-{esc(route["id"])}-theme-{index}">'
                         f'<h4>{esc(theme["title"])}</h4><p>{esc(theme["body"])}</p><dl>{subthemes}</dl>'
                         f'{worked}{practice}<p class="evidence-boundary"><b>Evidence boundary.</b> {esc(theme["reading"])}</p><p class="concept-links">Review: {lessons}</p></section>')
        sources = ''.join(f'<li><a href="{esc(source_href(href))}">{esc(label)}</a></li>' for href, label in route['sources'])
        parts.append(f'<aside class="uses"><h4>Practice reading a paper</h4><p>{esc(route["exercise"])}</p>'
                     f'<ul>{sources}</ul></aside><p><a href="#course-content">Back to the lessons</a></p></article>')
    return ''.join(parts) + '</section>'


def render_papers():
    parts = ['<section class="part" id="paper-walkthroughs"><h2>Work through a paper</h2>'
             '<p>Read the common lessons first. Each walkthrough isolates a mechanism, uses labeled teaching examples, '
             'and states the limits of the source evidence. These are selected discussions, not complete conference reviews.</p>']
    for paper in PAPERS:
        prerequisites = ' · '.join(f'<a href="#{esc(key)}">{esc(label)}</a>' for key, label in paper['lessons'])
        parts.append(f'<article id="paper-{esc(paper["id"])}"><h3>{esc(paper["title"])}</h3>'
                     f'<p>{esc(paper["identity"])}</p><aside class="uses"><h4>Scope and evidence</h4><p>{esc(paper["scope"])}</p></aside>'
                     f'<p>Review first: {prerequisites}</p>')
        for block in paper['blocks']:
            parts.append(f'<h4>{esc(block["title"])}</h4>')
            parts.extend(f'<p>{esc(paragraph)}</p>' for paragraph in block['paragraphs'])
            for href, label in block.get('sources', []):
                parts.append(f'<p><a href="{esc(href)}">{esc(label)}</a></p>')
        exercise = paper['exercise']
        parts.append(f'<aside class="uses"><h4>Work it through</h4><p>{esc(exercise["question"])}</p>'
                     f'<details><summary>Read the reasoning</summary><p>{esc(exercise["answer"])}</p></details></aside>'
                     f'<p><a href="#route-{esc(paper["route"])}">Return to the conference route</a> · '
                     '<a href="#course-content">Return to the lessons</a></p></article>')
    return ''.join(parts) + '</section>'


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
main a{color:var(--teal)}.lesson-links{display:flex;justify-content:space-between;gap:18px;flex-wrap:wrap;margin-top:24px;font-family:var(--sans);font-size:1rem}.part{scroll-margin-top:90px}a:focus-visible,summary:focus-visible{outline:3px solid var(--orange);outline-offset:4px}summary{cursor:pointer}details p{margin-bottom:0}.skip{position:absolute;top:-100px;left:20px;z-index:5;background:var(--g0);color:var(--ink);padding:12px}.skip:focus{top:10px}@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
.concept-links{font-family:var(--sans);font-size:.9rem;color:var(--ink2)}.term{scroll-margin-top:90px;margin:24px 0}.term dt{font-family:var(--sans);font-weight:650;color:var(--ink)}.term dd{margin:6px 0 0;color:var(--ink2)}
.route-theme{margin:30px 0;scroll-margin-top:90px}.route-theme h4{font-size:1.25rem;margin-bottom:10px}.route-theme dt{font-family:var(--sans);font-weight:600}.route-theme dd{margin:6px 0 18px;color:var(--ink2)}.subtheme-test{display:block;margin-top:5px;color:var(--ink3);font-family:var(--sans);font-size:.86em}.subtheme-detail{margin:12px 0 4px;padding:12px 15px;background:var(--g1);border-left:3px solid var(--teal);font-family:var(--sans);font-size:.9em}.subtheme-detail p{margin:5px 0;color:var(--ink2)}.subtheme-detail b{color:var(--ink)}.evidence-boundary{border-left:3px solid var(--orange);padding-left:17px;color:var(--ink2)}.evidence-boundary b{font-family:var(--sans);font-size:.86em;color:var(--ink)}article{scroll-margin-top:90px}
:root{--ink3:#a0aaba}nav a{min-height:44px;display:flex;align-items:center;font-size:.75rem}.contents{margin:24px 0;padding:16px 20px;border:1px solid var(--line);border-radius:10px;background:var(--g1)}.contents summary{font-family:var(--sans);min-height:44px;padding:8px 0}.contents h2{font-size:1.35rem;margin-top:24px}.contents li{padding:6px 0}.contents a{display:inline-block;padding:4px 0}.contents ol,.contents ul{padding-left:24px}.orientation-outcomes{padding-left:24px;margin:10px 0 20px}.orientation-outcomes li{margin:7px 0;color:var(--ink2)}.orientation-check{margin:12px 0;padding:12px 16px;background:var(--g1);border:1px solid var(--line2);border-radius:8px;scroll-margin-top:90px}.orientation-check summary{font-family:var(--sans);font-size:.96rem;line-height:1.5;padding:4px 0;color:var(--ink)}.orientation-check p{color:var(--ink2)}.orientation-check a{color:var(--teal)}
.table-wrap{margin:24px 0}table{width:100%;border-collapse:collapse;font-family:var(--sans);font-size:.9rem}caption{text-align:left;color:var(--ink2);margin-bottom:12px}th,td{text-align:left;vertical-align:top;border-bottom:1px solid var(--line);padding:10px 6px;overflow-wrap:anywhere}th{color:var(--ink)}td{color:var(--ink2)}
@media(max-width:560px){.coverage-table caption{display:block;width:100%}.coverage-table thead{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}.coverage-table,.coverage-table tbody,.coverage-table tr,.coverage-table th,.coverage-table td{display:block;width:100%}.coverage-table tr{padding:16px 0;border-bottom:1px solid var(--line)}.coverage-table th,.coverage-table td{border:0;padding:0}.coverage-table th{font-size:1.05rem;margin-bottom:12px}.coverage-table td+td{margin-top:14px}.coverage-table td:nth-child(2)::before,.coverage-table td:nth-child(3)::before{display:block;font-family:var(--mono);font-size:.68rem;letter-spacing:.13em;text-transform:uppercase;color:var(--ink3);margin-bottom:3px}.coverage-table td:nth-child(2)::before{content:"Teaching coverage"}.coverage-table td:nth-child(3)::before{content:"Evidence status"}.coverage-table p{margin:0 0 8px}.coverage-table p:last-child{margin-bottom:0}}
#route-vlsid-2025-theme-4 th:first-child,#route-vlsid-2025-theme-4 td:first-child{width:25%;overflow-wrap:normal}
.paper-challenge-step{margin:22px 0;padding:0 0 20px;border-bottom:1px solid var(--line2)}.paper-challenge-step h3{font-size:1.2rem;margin:0 0 6px}.paper-challenge-step label{display:block;margin:14px 0 6px;font:600 .9rem var(--sans);color:var(--ink)}.paper-challenge-step textarea{display:block;width:100%;min-height:7rem;padding:12px;border:1px solid var(--line);border-radius:6px;background:var(--g1);color:var(--ink);font:1rem/1.55 var(--sans);resize:vertical}.paper-challenge-step textarea:focus-visible{outline:3px solid var(--orange);outline-offset:3px}.paper-challenge-rubric ol{padding-left:22px}.paper-challenge-rubric li{margin:8px 0;color:var(--ink2)}
.interactive-model{margin:22px 0;padding:18px 20px;background:var(--g1);border:1px solid var(--line);border-left:3px solid var(--teal);border-radius:0 9px 9px 0;scroll-margin-top:90px}.interactive-model h3{margin:0 0 8px;font-size:1.15rem}.interactive-model p{color:var(--ink2)}.interactive-model label{display:block;margin:16px 0 6px;font:600 .95rem var(--sans);color:var(--ink)}.interactive-model input[type=range]{display:block;width:100%;min-height:36px;accent-color:var(--teal)}.interactive-model input:focus-visible{outline:3px solid var(--orange);outline-offset:3px}.model-hint{font: .86rem/1.5 var(--sans);color:var(--ink3)!important}.model-total th,.model-total td{font-weight:700;color:var(--ink)}
</style></head><body>
<a class="skip" href="#course-content">Skip to lessons</a>
<header><div class="wrap"><div class="bug">Computer systems · a concept-first course</div><h1>__TITLE__</h1><p>__SUBTITLE__</p></div></header>
<nav aria-label="Course lessons and reference"><div class="wrap navwrap"><a href="#__ORIENTATION_ID__">Start and outcomes</a><a href="#concept-lookup">Concept lookup</a><a href="#conference-routes">Conference routes</a>__NAV__</div></nav>
<main class="wrap" id="course-content">
  <div class="intro">__INTRO__</div>
  __ORIENTATION__
  __CONTENTS__
  __SECTIONS__
  __CHECKPOINTS__
  __COMPARISONS__
  __ROUTES__
  __PAPERS__
  __CAPSTONE__
  __GLOSSARY__
  __PATH__
  <footer>Based on the conference research collection, including 2025 conferences and NSDI 2026. This course is under development. Continue to <a href="index.html">research overview</a>, <a href="deepdives.html">deep dives</a>, or <a href="explorer.html">paper explorer</a>.</footer>
</main>__INTERACTIVE_SCRIPT__</body></html>
"""


def main():
    source_count = 0 if '--course-only' in sys.argv else build_sources(ROOT, SECTIONS, ROUTES)
    page = (
        PAGE.replace("__TITLE__", esc(COURSE_TITLE))
        .replace("__SUBTITLE__", esc(COURSE_SUBTITLE))
        .replace("__NAV__", render_nav())
        .replace("__INTRO__", render_intro())
        .replace("__ORIENTATION_ID__", ORIENTATION_ID)
        .replace("__ORIENTATION__", render_orientation(esc))
        .replace("__CONTENTS__", render_contents())
        .replace("__SECTIONS__", render_sections())
        .replace("__CHECKPOINTS__", render_checkpoints())
        .replace("__COMPARISONS__", render_comparisons())
        .replace("__GLOSSARY__", render_glossary())
        .replace("__ROUTES__", render_routes())
        .replace("__PAPERS__", render_papers())
        .replace("__CAPSTONE__", render_capstone(esc))
        .replace("__INTERACTIVE_SCRIPT__", INTERACTIVE_SCRIPT)
        .replace("__PATH__", render_path())
    )
    (ROOT / "course.html").write_text(page)
    print(f"wrote course.html ({len(page) // 1024} KB, {len(SECTIONS)} sections) and {source_count} source pages")


if __name__ == "__main__":
    main()
