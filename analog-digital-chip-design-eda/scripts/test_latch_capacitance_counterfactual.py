#!/usr/bin/env python3
"""Tests for a deliberately non-physical capacitance diagnostic."""
import unittest

from run_isolated_latch_v2_transient import symmetrize_capacitances


class CounterfactualTests(unittest.TestCase):
    def test_average_and_missing_mirror_preserve_total(self):
        source = (".subckt c out_p out_n vss\n"
                  "X0 out_p out_n vss vss nfet w=1 l=1\n"
                  "C0 out_p vss 2f\nC1 out_n vss 4f\n"
                  "C2 out_p tail 6f\nC3 out_p out_n 8f\n.ends c\n")
        result = symmetrize_capacitances(source)
        caps = {tuple(sorted(row.split()[1:3])): float(row.split()[3][:-1])
                for row in result.splitlines() if row.startswith("CSYM")}
        self.assertEqual(caps, {("out_p", "vss"): 3, ("out_n", "vss"): 3,
                                ("out_p", "tail"): 3, ("out_n", "tail"): 3,
                                ("out_n", "out_p"): 8})
        self.assertIn("X0 out_p out_n vss vss nfet w=1 l=1\n", result)
        self.assertEqual(result, symmetrize_capacitances(result))
        self.assertTrue(result.endswith(".ends c\n"))

    def test_unknown_units_fail_closed(self):
        with self.assertRaises(ValueError):
            symmetrize_capacitances(".subckt c\nC0 out_p vss 1p\n.ends c\n")


if __name__ == "__main__":
    unittest.main()
