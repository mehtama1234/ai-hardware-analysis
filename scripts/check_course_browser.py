#!/usr/bin/env python3
"""Browser checks for the static course; requires Python Playwright and a browser.

Example: python3 scripts/check_course_browser.py --chromium /path/to/chrome
WebKit: python3 scripts/check_course_browser.py --browser webkit
Set LD_LIBRARY_PATH outside this script if the browser needs local shared libraries.
Screenshots are diagnostic output, not an accessibility certification.
"""
import argparse
from pathlib import Path
import sys
from tempfile import mkdtemp

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from course_spine import SECTIONS
from course_routes import ROUTES
from course_papers import PAPERS
from course_learning import CHECKPOINTS
from course_comparisons import COMPARISONS
from course_capstone import CAPSTONE_ID
from course_orientation import CHECKS, ORIENTATION_ID
from course_interactives import REQUEST_LATENCY_MODEL


def follow_section(page, target):
    """Exercise same-page navigation without reparsing the entire course."""
    page.evaluate('(id) => { location.hash = id; }', target)
    page.wait_for_function(
        '(id) => Math.abs(document.getElementById(id).getBoundingClientRect().top - 90) < 3',
        arg=target,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--browser', choices=('chromium', 'webkit'), default='chromium')
    parser.add_argument('--chromium', help='Optional Chromium executable (legacy option).')
    parser.add_argument('--executable-path', help='Optional executable or launcher for the selected browser.')
    parser.add_argument('--widths', nargs='+', type=int, choices=(390, 1280), default=[390, 1280],
                        help='Viewport widths to check; defaults to both. Useful for resuming a terminated run.')
    parser.add_argument('--changed-sections-only', action='store_true',
                        help='Run the responsive keyboard/anchor checks for the new orientation and capstone only; does not replace the full regression.')
    args = parser.parse_args()
    if args.browser != 'chromium' and args.chromium:
        parser.error('--chromium cannot be combined with --browser webkit')
    if args.chromium and args.executable_path:
        parser.error('Choose --chromium or --executable-path, not both')
    output = Path(mkdtemp(prefix='conference-course-browser-'))
    with sync_playwright() as playwright:
        launch_options = {'headless': True}
        if args.chromium or args.executable_path:
            launch_options['executable_path'] = args.chromium or args.executable_path
        browser = getattr(playwright, args.browser).launch(**launch_options)
        print(f'Checking {args.browser} {browser.version}', flush=True)
        try:
            if args.changed_sections_only:
                for width in args.widths:
                    page = browser.new_page(viewport={'width': width, 'height': 844}, reduced_motion='reduce')
                    page.goto((ROOT / 'course.html').as_uri())
                    nav = page.locator('nav')
                    targets = [ORIENTATION_ID] + [check['id'] for check in CHECKS] + [CAPSTONE_ID]
                    for target in targets:
                        page.evaluate('(id) => { location.hash = id; }', target)
                        page.wait_for_function(
                            '(id) => Math.abs(document.getElementById(id).getBoundingClientRect().top - 90) < 3',
                            arg=target,
                        )
                        bounds = page.locator(f'#{target}').bounding_box()
                        nav_bounds = nav.bounding_box()
                        assert bounds['y'] >= nav_bounds['y'] + nav_bounds['height'], f'Navigation covers {target}'
                        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'Overflow at {target} ({width}px)'

                    orientation = page.locator(f'#{ORIENTATION_ID}')
                    for check in CHECKS:
                        prompt = page.locator(f'#{check["id"]}')
                        assert prompt.get_attribute('open') is None, 'Starting-point answer should begin closed'
                        prompt.locator('summary').focus()
                        page.keyboard.press('Enter')
                        assert prompt.get_attribute('open') is not None, 'Starting-point keyboard toggle failed'
                        assert prompt.locator(f'a[href="#{check["lesson"]}"]').count() == 1, 'Starting-point lesson link missing'
                    assert orientation.locator('details').count() == len(CHECKS)
                    page.evaluate('(id) => { location.hash = id; }', ORIENTATION_ID)
                    page.screenshot(path=str(output / f'orientation-focused-{width}.png'))

                    page.goto((ROOT / 'course.html').as_uri() + '#' + CAPSTONE_ID)
                    challenge = page.locator(f'#{CAPSTONE_ID}')
                    assert challenge.locator('textarea').count() == 6, 'Paper challenge note fields are missing'
                    first_note = challenge.locator('textarea').first
                    first_note.focus()
                    page.keyboard.insert_text('Claim, task, and paper page recorded.')
                    assert first_note.input_value() == 'Claim, task, and paper page recorded.'
                    rubric = challenge.locator('details.paper-challenge-rubric')
                    assert rubric.get_attribute('open') is None, 'Capstone rubric should start closed'
                    rubric.locator('summary').focus()
                    page.keyboard.press('Enter')
                    assert rubric.get_attribute('open') is not None, 'Capstone keyboard rubric toggle failed'
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'Capstone overflow ({width}px)'
                    page.screenshot(path=str(output / f'capstone-focused-{width}.png'))
                    page.close()
                    print(f'Focused additions check passed at {width}px: {len(targets)} anchors, keyboard answers, note entry, rubric, and overflow.')
                print(f'Focused screenshots: {output}; the full course regression has not been run by this option.')
                return

            for width in args.widths:
                page = browser.new_page(viewport={'width': width, 'height': 844}, reduced_motion='reduce')
                page.goto((ROOT / 'index.html').as_uri())
                entry = page.locator('#course-entry')
                entry.scroll_into_view_if_needed()
                assert entry.evaluate('(el) => el.scrollWidth <= el.clientWidth'), 'Homepage course entry overflows'
                page.screenshot(path=str(output / f'homepage-course-{width}.png'))
                first_lesson = entry.locator('a[href="course.html#s1"]')
                first_lesson.focus()
                page.keyboard.press('Enter')
                page.wait_for_url('**/course.html#s1')
                assert page.locator('#s1 h2').is_visible(), 'Homepage entry did not reach first lesson'
                page.goto((ROOT / 'course.html').as_uri())
                page.keyboard.press('Tab')
                assert page.locator('.skip').evaluate('(el) => el === document.activeElement'), 'Skip link is not first'
                page.keyboard.press('Enter')
                page.locator('.contents summary').focus()
                page.keyboard.press('Enter')
                assert page.locator('.contents').get_attribute('open') is not None, 'Keyboard contents toggle failed'
                page.locator('.contents').evaluate('(el) => window.scrollTo(0, el.getBoundingClientRect().top + scrollY - 90)')
                page.screenshot(path=str(output / f'contents-{width}.png'))
                latency = page.locator(f'#{REQUEST_LATENCY_MODEL["id"]}')
                control = latency.locator('input[type="range"]')
                assert control.get_attribute('aria-describedby') == f'{REQUEST_LATENCY_MODEL["id"]}-hint'
                assert control.input_value() == '2'
                assert latency.locator(f'#{REQUEST_LATENCY_MODEL["id"]}-total-ms').evaluate('(el) => el.value') == '10'
                control.focus()
                page.keyboard.press('Home')
                assert control.input_value() == '0', 'Range control minimum keyboard step failed'
                assert latency.locator(f'#{REQUEST_LATENCY_MODEL["id"]}-total-ms').evaluate('(el) => el.value') == '8'
                assert latency.locator(f'#{REQUEST_LATENCY_MODEL["id"]}-calculation-ms').evaluate('(el) => el.value') == '0'
                page.keyboard.press('End')
                assert control.input_value() == '8', 'Range control maximum keyboard step failed'
                assert latency.locator(f'#{REQUEST_LATENCY_MODEL["id"]}-total-ms').evaluate('(el) => el.value') == '16'
                assert latency.locator(f'#{REQUEST_LATENCY_MODEL["id"]}-explanation').get_attribute('aria-live') == 'polite'
                assert latency.evaluate('(el) => el.scrollWidth <= el.clientWidth'), 'Latency model overflows its card'
                control.evaluate('(el) => { el.value = "2"; el.dispatchEvent(new Event("input", {bubbles: true})); el.blur(); }')
                page.evaluate('(id) => { const el = document.getElementById(id); window.scrollTo(0, el.getBoundingClientRect().top + scrollY - 90); }', REQUEST_LATENCY_MODEL['id'])
                page.wait_for_function('(id) => Math.abs(document.getElementById(id).getBoundingClientRect().top - 90) < 3', arg=REQUEST_LATENCY_MODEL['id'])
                page.screenshot(path=str(output / f'latency-model-{width}.png'))
                ids = [section['id'] for section in SECTIONS]
                ids += [REQUEST_LATENCY_MODEL['id']]
                ids += [f'route-{route["id"]}' for route in ROUTES] + ['concept-lookup']
                ids += ['paper-walkthroughs'] + [f'paper-{paper["id"]}' for paper in PAPERS]
                ids += ['course-checkpoints'] + [item['id'] for item in CHECKPOINTS]
                ids += ['cross-conference-questions'] + [item['id'] for item in COMPARISONS]
                ids += [CAPSTONE_ID]
                ids += [ORIENTATION_ID] + [check['id'] for check in CHECKS]
                theme_practice = [f'route-{route["id"]}-theme-{i}' for route in ROUTES
                                  for i, theme in enumerate(route['themes'], 1) if theme.get('practice')]
                ids += theme_practice
                for target in ids:
                    page.evaluate('(id) => { location.hash = id; }', target)
                    page.wait_for_function('(id) => Math.abs(document.getElementById(id).getBoundingClientRect().top - 90) < 3', arg=target)
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'Page overflow at {width}: {target}'
                    bounds = page.locator(f'#{target}').bounding_box()
                    nav = page.locator('nav').bounding_box()
                    assert bounds['y'] >= nav['y'] + nav['height'], f'Navigation covers target: {target}'
                page.goto((ROOT / 'course.html').as_uri() + '#' + ORIENTATION_ID)
                orientation = page.locator(f'#{ORIENTATION_ID}')
                assert orientation.locator('details').count() == len(CHECKS), 'Starting-point check count differs'
                for check in CHECKS:
                    prompt = page.locator(f'#{check["id"]}')
                    assert prompt.get_attribute('open') is None, 'Starting-point answers should begin closed'
                    prompt.locator('summary').focus()
                    page.keyboard.press('Enter')
                    assert prompt.get_attribute('open') is not None, 'Starting-point keyboard answer toggle failed'
                    assert prompt.locator(f'a[href="#{check["lesson"]}"]').count() == 1, 'Starting-point answer lacks its lesson route'
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'Starting-point section overflows'
                page.screenshot(path=str(output / f'orientation-{width}.png'))
                page.goto((ROOT / 'course.html').as_uri() + '#s6')
                page.locator('#s6 h2').wait_for()
                page.screenshot(path=str(output / f'compiler-{width}.png'))
                exercise = page.locator('#s6 details')
                exercise.locator('summary').focus()
                page.keyboard.press('Enter')
                assert exercise.get_attribute('open') is not None, 'Keyboard exercise toggle failed'
                page.goto((ROOT / 'course.html').as_uri() + '#s7')
                page.locator('#s7 h2').wait_for()
                page.screenshot(path=str(output / f'distributed-work-{width}.png'))
                distributed_exercise = page.locator('#s7 details')
                distributed_exercise.locator('summary').focus()
                page.keyboard.press('Enter')
                assert distributed_exercise.get_attribute('open') is not None, 'Distributed-work exercise keyboard toggle failed'
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'Distributed-work section overflows'
                page.goto((ROOT / 'course.html').as_uri() + '#s8')
                page.locator('#s8 h2').wait_for()
                page.screenshot(path=str(output / f'correctness-{width}.png'))
                correctness_exercise = page.locator('#s8 details')
                correctness_exercise.locator('summary').focus()
                page.keyboard.press('Enter')
                assert correctness_exercise.get_attribute('open') is not None, 'Correctness exercise keyboard toggle failed'
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'Correctness section overflows'
                page.goto((ROOT / 'course.html').as_uri() + '#scientific-workflow')
                page.screenshot(path=str(output / f'science-{width}.png'))
                science_exercise = page.locator('#scientific-workflow details')
                science_exercise.locator('summary').focus()
                page.keyboard.press('Enter')
                assert science_exercise.get_attribute('open') is not None, 'Scientific exercise toggle failed'
                for item in CHECKPOINTS + COMPARISONS:
                    follow_section(page, item['id'])
                    practice = page.locator(f'#{item["id"]} details')
                    assert practice.get_attribute('open') is None, 'Checkpoint answer should start closed'
                    practice.locator('summary').focus()
                    page.keyboard.press('Enter')
                    assert practice.get_attribute('open') is not None, 'Checkpoint keyboard toggle failed'
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'Open checkpoint answer overflows'
                page.screenshot(path=str(output / f'checkpoint-{width}.png'))
                for target in theme_practice:
                    follow_section(page, target)
                    practice = page.locator(f'#{target} details')
                    assert practice.get_attribute('open') is None, 'Theme answer should start closed'
                    practice.locator('summary').focus()
                    page.keyboard.press('Enter')
                    assert practice.get_attribute('open') is not None, 'Theme practice keyboard toggle failed'
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'Theme answer overflows'
                    for table_index, table in enumerate(page.locator(f'#{target} table').all()):
                        assert table.locator('caption').count() == 1, 'Theme table lacks caption'
                        assert table.locator('th[scope="col"]').count() > 0, 'Theme table lacks column headers'
                        assert table.evaluate('(el) => el.getBoundingClientRect().width <= el.parentElement.clientWidth + 1'), 'Theme table overflows its container'
                        table.scroll_into_view_if_needed()
                        page.screenshot(path=str(output / f'{target}-table-{table_index}-{width}.png'))
                page.screenshot(path=str(output / f'theme-practice-{width}.png'))
                for paper in PAPERS:
                    follow_section(page, 'paper-' + paper['id'])
                    page.screenshot(path=str(output / f'paper-{paper["id"]}-{width}.png'))
                    practice = page.locator(f'#paper-{paper["id"]} details')
                    assert practice.get_attribute('open') is None, 'Paper answer should start closed'
                    practice.locator('summary').focus()
                    page.keyboard.press('Enter')
                    assert practice.get_attribute('open') is not None, 'Paper exercise toggle failed'
                page.goto((ROOT / 'course.html').as_uri() + '#' + CAPSTONE_ID)
                challenge = page.locator(f'#{CAPSTONE_ID}')
                assert challenge.locator('textarea').count() == 6, 'Paper challenge note fields are missing'
                first_note = challenge.locator('textarea').first
                first_note.fill('Claim, task, and paper page recorded.')
                assert first_note.input_value() == 'Claim, task, and paper page recorded.'
                rubric = challenge.locator('details.paper-challenge-rubric')
                assert rubric.get_attribute('open') is None, 'Capstone rubric should start closed'
                rubric.locator('summary').focus()
                page.keyboard.press('Enter')
                assert rubric.get_attribute('open') is not None, 'Capstone rubric keyboard toggle failed'
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'Capstone rubric overflows'
                sources = sorted((ROOT / 'course-sources').rglob('*.html'))
                for source in sources:
                    page.goto(source.as_uri())
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'Source overflow at {width}: {source.name}'
                    page.keyboard.press('Tab')
                    assert page.locator('.skip').evaluate('(el) => el === document.activeElement')
                    returns = page.locator('header details').first
                    returns.locator('summary').focus()
                    page.keyboard.press('Enter')
                    assert returns.get_attribute('open') is not None
                    assert returns.locator('a').count() > 0
                page.screenshot(path=str(output / f'source-{width}.png'))
                page.close()
                print(f'Passed {width}px: keyboard entry, contents, {len(ids)} anchor positions, overflow, exercise toggle; {len(sources)} source pages and return menus.')
        finally:
            browser.close()
    print(f'Screenshots for visual inspection: {output}')


if __name__ == '__main__':
    main()
