import random
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from parallel_primitives.reference import exclusive_scan, stable_compact, histogram, radix_sort_indices


class PrimitiveReferenceTests(unittest.TestCase):
    def test_scan_against_sequential_oracle(self):
        rng = random.Random(181)
        for count in (0, 1, 2, 3, 7, 31, 32, 33, 255, 256, 257):
            for values in ([0] * count, [1] * count,
                           [rng.randrange(-100, 101) for _ in range(count)]):
                original = values.copy()
                total, expected = 0, []
                for value in values:
                    expected.append(total)
                    total += value
                self.assertEqual(exclusive_scan(values), expected)
                self.assertEqual(values, original)

    def test_large_integers_are_exact_not_fixed_width(self):
        self.assertEqual(exclusive_scan([2**63, 2**63, -2**64]), [0, 2**63, 2**64])

    def test_compaction_stable_and_matches_filter(self):
        rng = random.Random(182)
        for count in (0, 1, 3, 31, 32, 33, 257):
            # Repeated keys with unique positions expose reordering.
            values = [(i % 3, i) for i in range(count)]
            for flags in ([False] * count, [True] * count,
                          [bool(i % 2) for i in range(count)],
                          [bool(rng.randrange(2)) for _ in range(count)]):
                before = flags.copy()
                self.assertEqual(stable_compact(values, flags), [v for v, k in zip(values, flags) if k])
                self.assertEqual(flags, before)

    def test_invalid_contracts(self):
        for values in ([True], [1.0], [None]):
            with self.assertRaises(ValueError):
                exclusive_scan(values)
        for flags in ([1], [], [False, True]):
            with self.assertRaises(ValueError):
                stable_compact(["x"], flags)

    def test_histogram_exact_counts(self):
        rng = random.Random(183)
        for bins in (1, 3, 256):
            for count in (0, 1, 33, 257):
                values = [rng.randrange(bins) for _ in range(count)]
                result = histogram(values, bins)
                self.assertEqual(result, [values.count(i) for i in range(bins)])
                self.assertEqual(sum(result), count)

    def test_radix_permutation_and_duplicate_stability(self):
        rng = random.Random(184)
        cases = [[], [0], [2**32 - 1, 0, 256, 255, 65536, 65535, 2**24],
                 [7] * 33, list(range(257)), list(range(256, -1, -1)),
                 [rng.randrange(2**32) for _ in range(257)],
                 [rng.randrange(8) * 2**24 for _ in range(257)]]
        for keys in cases:
            before = keys.copy()
            order = radix_sort_indices(keys)
            self.assertEqual(order, sorted(range(len(keys)), key=lambda i: keys[i]))
            self.assertEqual(sorted(order), list(range(len(keys))))
            self.assertEqual(keys, before)

    def test_histogram_and_radix_reject_invalid(self):
        for keys in ([-1], [2**32], [True], [1.0]):
            with self.assertRaises(ValueError):
                radix_sort_indices(keys)
        for bins in (0, -1, True, 1.5):
            with self.assertRaises(ValueError):
                histogram([], bins)
        for values in ([-1], [3], [True], [1.0]):
            with self.assertRaises(ValueError):
                histogram(values, 3)


if __name__ == "__main__":
    unittest.main()
