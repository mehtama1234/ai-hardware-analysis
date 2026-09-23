#!/usr/bin/env python3
"""Check the scientific lesson's teaching arithmetic, not a physical simulation."""
from fractions import Fraction as F
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from course_science import SCIENCE_LESSON


def main():
    u = v = F(0)
    for iteration in range(1, 11):
        u, v = v / 2, (u + 90) / 2
        residual = max(abs(2 * u - v), abs(90 - 2 * v + u))
        assert residual == F(90, 2**iteration)
        assert (residual <= F(1, 10)) == (iteration == 10)
    assert (u, v) == (F('29.970703125'), F('59.94140625'))
    text = ' '.join(SCIENCE_LESSON['body'])
    for value in ('29.970703125', '59.94140625', '0.088', '0.176'):
        assert value in text, f'Update the derivation check when prose changes: {value}'
    relative_limit = F('0.01') * 100
    absolute_limit = F('0.1')
    threshold = max(relative_limit, absolute_limit)
    example_residual = F('0.5')
    assert threshold == 1 and example_residual < threshold
    assert example_residual > absolute_limit
    for phrase in ('residual norm of 0.5 passes', 'not PETSc\'s default settings',
                   'may be preconditioned', 'reported as failure, not convergence'):
        assert phrase in text, f'Update the PETSc explanation check when prose changes: {phrase}'
    assert 2 + 1000 * F(10, 1000) + 1 + 1 == 14
    assert 2 + 1000 * F('0.0075') + 1 + 1 == F('11.5')
    assert 3 + 600 * F('0.010') + 1 + 1 == 11
    assert 2 + 1400 * F('0.008') + 1 + 1 == F('15.2')
    first_pass, interval = 996, 10
    detected = ((first_pass + interval - 1) // interval) * interval
    assert detected == 1000
    assert 4 + detected * F('0.008') + (detected // interval) * F('0.002') == F('12.2')
    print('Scientific lesson: exact recurrence, PETSc threshold example, and five timing comparisons passed.')


if __name__ == '__main__':
    main()
