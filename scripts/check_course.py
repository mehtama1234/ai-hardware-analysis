#!/usr/bin/env python3
"""Structural checks only: these do not establish teaching quality or layout."""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from course_glossary import GLOSSARY
from course_spine import SECTIONS
from course_routes import CONFERENCE_SCOPE, ROUTES, ROUTE_EVIDENCE_STATUS
from course_papers import PAPERS
from course_coverage import coverage_for
from course_learning import CHECKPOINTS, PREREQUISITES
from course_comparisons import COMPARISONS
from course_capstone import CAPSTONE_ID
from course_orientation import CHECKS, LEARNING_PATH, ORIENTATION_ID, OUTCOMES
from course_entry import COURSE_ENTRY, COURSE_ENTRY_CSS
from course_interactives import REQUEST_LATENCY_MODEL


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.ids = []
        self.links = []
        self.textareas = []
        self.range_controls = []
        self.label_targets = []
        self.feed(text)

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if tag == 'a' and 'href' in attrs:
            self.links.append(attrs['href'])
        if tag == 'textarea' and 'id' in attrs:
            self.textareas.append(attrs['id'])
        if tag == 'input' and attrs.get('type') == 'range' and 'id' in attrs:
            self.range_controls.append(attrs['id'])
        if tag == 'label' and 'for' in attrs:
            self.label_targets.append(attrs['for'])


def main():
    course_html = (ROOT / 'course.html').read_text()
    document = Document(course_html)
    documents = {(ROOT / 'course.html').resolve(): document}

    def load_document(path):
        # Many source pages return to the same large course document. Parse each
        # file once per run while retaining every link and anchor assertion.
        path = path.resolve()
        if path not in documents:
            documents[path] = Document(path.read_text())
        return documents[path]

    assert 'Read next' not in course_html, 'Supplemental research links should not interrupt the start of the tutorial'
    assert 'Optional research pages' in course_html
    optional_start = course_html.index('id="optional-research-pages"')
    assert optional_start > course_html.index(f'id="{CAPSTONE_ID}"')
    assert optional_start > course_html.index('id="concept-lookup"')
    assert '#optional-research-pages' in document.links, 'Contents menu should expose supplemental research pages'
    assert 'one focused paper walkthrough in each route' not in course_html
    assert 'The coverage table shows the distribution of guided paper walkthroughs.' in course_html
    model = REQUEST_LATENCY_MODEL
    assert model['id'] in document.ids, 'Missing request latency model'
    assert document.range_controls == [f'{model["id"]}-control'], 'Expected one labeled course range control'
    assert f'{model["id"]}-control' in document.label_targets, 'Latency control needs a visible label'
    assert f'{model["id"]}-explanation' in course_html and 'aria-live="polite"' in course_html
    assert 'does not predict the completion rate' in course_html, 'Latency model must not imply throughput evidence'
    homepage = (ROOT / 'index.html').read_text()
    assert COURSE_ENTRY in homepage, 'Homepage course entry differs from shared source'
    assert COURSE_ENTRY_CSS.strip() in homepage, 'Homepage course entry styling differs from shared source'
    for href in Document(COURSE_ENTRY).links:
        url = urlsplit(href)
        assert url.path == 'course.html' and url.fragment in document.ids, f'Broken homepage entry: {href}'
    duplicates = [key for key, count in Counter(document.ids).items() if count > 1]
    assert not duplicates, f'Duplicate IDs: {duplicates}'
    for href in document.links:
        url = urlsplit(href)
        if url.scheme or url.netloc:
            continue
        target = ROOT / unquote(url.path) if url.path else ROOT / 'course.html'
        assert target.is_file(), f'Missing file: {href}'
        if url.fragment and target.suffix == '.html':
            linked = load_document(target)
            assert unquote(url.fragment) in linked.ids, f'Missing anchor: {href}'
    for section in SECTIONS:
        assert section['id'] in document.ids, section['id']
        assert section.get('exercise', {}).get('question') and section['exercise'].get('answer'), f'Missing exercise: {section["id"]}'
    for index, section in enumerate(SECTIONS):
        start = course_html.index(f'<section class="part" id="{section["id"]}">')
        end = (course_html.index('<section class="part"', start + 1)
               if index + 1 < len(SECTIONS) else course_html.index('<section class="part" id="course-checkpoints"'))
        lesson_html = course_html[start:end]
        assert 'role="navigation" aria-label="Lesson navigation"' in lesson_html
        if index:
            previous = SECTIONS[index - 1]
            assert f'href="#{previous["id"]}">Previous: {previous["kicker"]}</a>' in lesson_html
        if index + 1 < len(SECTIONS):
            following = SECTIONS[index + 1]
            assert f'href="#{following["id"]}">Next: {following["kicker"]}</a>' in lesson_html
    order = {section['id']: index for index, section in enumerate(SECTIONS)}
    assert set(PREREQUISITES) == set(order), 'Prerequisite map does not cover exactly the lessons'
    for lesson, dependencies in PREREQUISITES.items():
        assert len(dependencies) == len(set(dependencies)), f'Duplicate prerequisite: {lesson}'
        for dependency in dependencies:
            assert dependency in order and order[dependency] < order[lesson], f'Unknown, circular, or later prerequisite: {lesson}: {dependency}'
    assert 'course-checkpoints' in document.ids
    assert 'cross-conference-questions' in document.ids
    assert 'class="coverage-table"' in course_html
    assert 'Teaching coverage' in course_html and 'Evidence status' in course_html
    assert 'Every listed route has theme and subtheme teaching blocks' in course_html
    assert CAPSTONE_ID in document.ids, 'Missing final transfer challenge'
    assert f'#{CAPSTONE_ID}' in document.links, 'Final challenge is not linked from course navigation'
    assert len(document.textareas) == 6, 'Final challenge should have six note fields'
    assert set(document.textareas) <= set(document.label_targets), 'Every note field needs a visible label'
    assert 'reported by the paper, calculated from its numbers, or inferred as a next question' in course_html
    assert 'state its numerator and denominator' in course_html
    assert 'Did both systems process the same inputs' in course_html
    assert 'Record the reported variation' in course_html
    assert 'Repeating an unequal comparison does not make the jobs equivalent' in course_html
    assert ORIENTATION_ID in document.ids, 'Missing learner orientation and starting check'
    assert f'#{ORIENTATION_ID}' in document.links, 'Starting check is not reachable from course navigation'
    assert len(OUTCOMES) == 5 and len(CHECKS) == 5
    assert len(LEARNING_PATH) == 3
    for stage in LEARNING_PATH:
        assert stage['title'] and stage['body']
        for target, label in stage['links']:
            assert label and f'#{target}' in document.links, f'Missing learning-path link: {target}'
    for check in CHECKS:
        assert check['id'] in document.ids and check['question'] and check['answer']
        assert f'#{check["lesson"]}' in document.links, f'Missing starting-point route: {check["id"]}'
    for item in COMPARISONS:
        assert item['id'] in document.ids and f'#{item["id"]}' in document.links
        assert item['paragraphs'] and item['links'] and item['question'] and item['answer']
    for item in CHECKPOINTS:
        assert item['id'] in document.ids
        assert item['setup'] and item['question'] and item['answer'] and item['review']
    assert len({route['id'] for route in ROUTES}) == len(ROUTES), 'Duplicate route IDs'
    assert {route['id'] for route in ROUTES} <= {key for key, label in CONFERENCE_SCOPE}, 'Route outside declared scope'
    assert set(ROUTE_EVIDENCE_STATUS) == {route['id'] for route in ROUTES}
    assert all(status and 'Route-level evidence boundary appears below' not in status
               for status in ROUTE_EVIDENCE_STATUS.values())
    for route in ROUTES:
        assert f'route-{route["id"]}' in document.ids
        row_start = course_html.index(f'id="coverage-{route["id"]}"')
        row_end = course_html.index('</tr>', row_start)
        count_text = f'Focused paper walkthroughs: {coverage_for(route, PAPERS)["papers"]}.'
        assert count_text in course_html[row_start:row_end], f'Inaccurate visible paper count for {route["id"]}'
        for index, theme in enumerate(route['themes'], 1):
            assert f'route-{route["id"]}-theme-{index}' in document.ids
            assert theme['subthemes'] and theme['reading'] and theme['body']
            if theme.get('worked_example'):
                assert theme.get('practice', {}).get('question') and theme['practice'].get('answer'), 'Worked theme lacks explained practice'
    assert len({term[0] for term in GLOSSARY}) == len(GLOSSARY), 'Duplicate glossary keys'
    assert len({paper['id'] for paper in PAPERS}) == len(PAPERS), 'Duplicate paper IDs'
    for paper in PAPERS:
        assert paper['route'] in {route['id'] for route in ROUTES}
        assert f'paper-{paper["id"]}' in document.ids
        assert f'#paper-{paper["id"]}' in document.links
        assert paper['identity'] and paper['scope'] and paper['exercise']['answer']
        assert any(block.get('sources') for block in paper['blocks']), 'Missing primary source links'
    for key, label, definition, lesson in GLOSSARY:
        assert f'term-{key}' in document.ids, key
        assert f'#term-{key}' in document.links, f'No lesson link to {key}'
        assert f'#{lesson}' in document.links, f'No explanation link for {key}'
        assert label and definition
    source_pages = sorted((ROOT / 'course-sources').rglob('*.html'))
    for path in source_pages:
        source = load_document(path)
        assert len(source.ids) == len(set(source.ids)), f'Duplicate source anchors: {path}'
        assert 'source-text' in source.ids
        for href in source.links:
            url = urlsplit(href)
            if url.scheme or url.netloc:
                continue
            target = (path.parent / unquote(url.path)).resolve() if url.path else path
            # Check generated navigation; historical notes may reference unavailable artifacts.
            if not url.path or target == ROOT / 'course.html' or target.is_relative_to(ROOT / 'course-sources'):
                assert target.is_file(), f'Missing source-page target: {path}: {href}'
                linked = load_document(target)
                if url.fragment:
                    assert unquote(url.fragment) in linked.ids, f'Missing source-page anchor: {path}: {href}'
    print(f'Passed structural checks: {len(SECTIONS)} lessons, {len(GLOSSARY)} concepts, '
          f'{len(document.links)} course links, {len(source_pages)} source pages, {len(PAPERS)} paper walkthroughs. '
          'External URLs, historical artifact links, and visual layout not tested.')


if __name__ == '__main__':
    main()
