#!/usr/bin/env python3
"""Check original RSizing teaching examples, not the paper's circuit results."""
from fractions import Fraction
from math import ceil, isclose, log, sqrt


def main():
    delays = {'A': (7, 11), 'B': (Fraction(19, 2),) * 2}
    means = {name: sum(values) / 2 for name, values in delays.items()}
    yields = {name: Fraction(sum(v <= 10 for v in values), 2)
              for name, values in delays.items()}
    assert means['A'] == 9 and means['B'] == Fraction(19, 2)
    assert yields == {'A': Fraction(1, 2), 'B': 1}
    assert round(sqrt(3**2 + 1**2), 3) == 3.162
    assert round(sqrt(.2**2 + 1**2), 3) == 1.020
    full = 1000 * 1000
    screened = 1000 * 5 + 20 * 1000
    assert screened == 25_000 and full / screened == 40

    population = set(range(1000))
    delay_fail = set(range(10))
    current_fail = set(range(10, 20))
    assert len(population - delay_fail) == 990
    assert len(population - current_fail) == 990
    assert len(population - (delay_fail | current_fail)) == 980
    assert len(population - (delay_fail | delay_fail)) == 990
    assert Fraction(99, 100)**2 == Fraction(9801, 10_000)
    # Exhaust all placements of two failure sets in a small population.
    from itertools import combinations
    tiny = set(range(6))
    for left in combinations(tiny, 2):
        for right in combinations(tiny, 2):
            assert len(tiny - (set(left) | set(right))) >= 6 - 2 - 2
    assert 1 - 3 * Fraction(1, 100) == Fraction(97, 100)
    assert 1 - 3 * Fraction(1, 300) == Fraction(99, 100)

    assert round(.999**1000 * 100, 1) == 36.8
    lower = .05**(1 / 1000)
    assert round(lower * 100, 3) == 99.701
    assert lower < .999
    threshold = log(.05) / log(.999)
    assert ceil(threshold) == 2995
    assert .05**(1 / 2994) < .999 <= .05**(1 / 2995)
    assert isclose(lower**1000, .05)
    print('RSizing teaching checks passed: acceptance, spread, simulation counts, joint failures, and all-pass confidence bounds. No circuit results reproduced.')


if __name__ == '__main__':
    main()
