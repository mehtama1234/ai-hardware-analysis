#!/usr/bin/env python3
"""Audit declared course components without claiming editorial completion."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from course_coverage import coverage_for
from course_papers import PAPERS
from course_routes import CONFERENCE_SCOPE, ROUTES
from check_course import Document


def main():
    routes = {r['id']: r for r in ROUTES}
    assert set(routes) == {key for key, label in CONFERENCE_SCOPE}
    document = Document((ROOT / 'course.html').read_text())
    print('Venue | themes | subthemes | dedicated examples | explained exercises | walkthroughs')
    for key, label in CONFERENCE_SCOPE:
        counts = coverage_for(routes[key], PAPERS)
        assert f'coverage-{key}' in document.ids
        assert 0 <= counts['worked_themes'] <= counts['themes']
        assert 0 <= counts['practice_themes'] <= counts['themes']
        print(f'{label} | {counts["themes"]} | {counts["subthemes"]} | '
              f'{counts["worked_themes"]} | {counts["practice_themes"]} | {counts["papers"]}')
    # Small independent fixture catches accidentally counting exercises as examples.
    fixture = {'id': 'fixture', 'themes': [
        {'subthemes': [('a', 'b')], 'worked_example': ['example']},
        {'subthemes': [('c', 'd'), ('e', 'f')], 'practice': {'question': 'q', 'answer': 'a'}},
        {'subthemes': [], 'practice': {'question': 'q'}},
    ]}
    assert coverage_for(fixture, [{'route': 'fixture'}, {'route': 'elsewhere'}]) == {
        'themes': 3, 'subthemes': 3, 'worked_themes': 1, 'practice_themes': 1, 'papers': 1,
    }
    print('These are structural counts. Source review, teaching quality, and subtheme completeness require separate review.')


if __name__ == '__main__':
    main()
