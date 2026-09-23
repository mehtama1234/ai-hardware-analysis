#!/usr/bin/env python3
"""Check comparison-table rendering and the two original DAC data examples."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from build_course import render_example_table
from course_routes import ROUTES
from course_route_dac import DAC_ROUTE
from course_route_sc import SC_ROUTE


def main():
    output = (ROOT / 'course.html').read_text()
    count = 0
    for route in ROUTES:
        for theme in route['themes']:
            for table in (theme.get('worked_table'), theme.get('practice', {}).get('table')):
                if table:
                    assert render_example_table(table) in output
                    count += 1
    fixture = {'caption': '<test>', 'headings': ['A&B'], 'rows': [[0]]}
    rendered = render_example_table(fixture)
    assert '<caption>&lt;test&gt;</caption>' in rendered
    assert '<th scope="col">A&amp;B</th>' in rendered
    assert '<td>0</td>' in rendered
    for invalid in ({}, {'caption': 'x', 'headings': ['a'], 'rows': [[1, 2]]}):
        try:
            render_example_table(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError('Invalid table accepted')
    energy = DAC_ROUTE['themes'][4]['worked_table']['rows']
    expected = [
        ['Movement time', '2 s', '2 s'],
        ['Calculation time', '3 s', '5 s'],
        ['Completion time', f'{2+3} s', f'{2+5} s'],
        ['Stage energy', f'{2*3+3*4} J', f'{2*3+5*2} J'],
        ['Background energy', f'{2*(2+3)} J', f'{2*(2+5)} J'],
        ['Full-request energy', f'{2*3+3*4+2*(2+3)} J', f'{2*3+5*2+2*(2+5)} J'],
    ]
    assert energy == expected
    timing = DAC_ROUTE['themes'][5]['practice']['table']['rows']
    assert timing == [[str(bit), f'{delay} ms', f'{1+2*bit+delay} ms']
                      for bit in (0, 1) for delay in (0, 2)]
    pipeline, previous_finish = [], 0
    for chunk in range(1, 4):
        transfer_start, transfer_end = (chunk-1)*4, chunk*4
        calculation_start = max(transfer_end, previous_finish)
        previous_finish = calculation_start+6
        pipeline.append([str(chunk), f'{transfer_start}–{transfer_end}', f'{calculation_start}–{previous_finish}'])
    assert SC_ROUTE['themes'][3]['worked_table']['rows'] == pipeline
    print(f'Passed {count} rendered theme tables, escaping, validation, and DAC/SC table arithmetic.')


if __name__ == '__main__':
    main()
