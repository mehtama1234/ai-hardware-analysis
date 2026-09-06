#!/usr/bin/env python3
"""Structural negative controls for the repeated-cycle testbench."""
import unittest

from run_latch_repeated_readout import replace_line, stimulus, output_reset_source


class RepeatedReadoutTests(unittest.TestCase):
    def test_release_slew_preserves_start_of_precharge(self):
        self.assertEqual(output_reset_source(1.75,20,1000,.5,50),
                         "VRESET reset 0 PULSE(0 1.75 8n 20p 1000p 29.5n 50n)")
        self.assertEqual(output_reset_source(1.75,500,1000,.5,50),
                         "VRESET reset 0 PULSE(0 1.75 8n 500p 1000p 29.02n 50n)")
        self.assertEqual(output_reset_source(1.75,500,2000,.5,50),
                         "VRESET reset 0 PULSE(0 1.75 8n 500p 2000p 29.02n 50n)")

    def test_replacement_requires_exactly_one_line(self):
        for text in ("VN x 0 1\n", "VP x 0 1\nVP x 0 2\n"):
            with self.assertRaises(ValueError):
                replace_line(text, "VP ", "VP x 0 3")
        self.assertEqual(replace_line("VP x 0 1\nVN x 0 2\n", "VP ", "VP x 0 3"),
                         "VP x 0 3\nVN x 0 2\n")

    def test_input_changes_between_evaluations_not_at_sampling(self):
        p = stimulus([-0.5, 0.5, -0.5], 1)
        n = stimulus([-0.5, 0.5, -0.5], -1)
        self.assertEqual(p, "PWL(0n 0.89975 45n 0.89975 45.02n 0.90025 95n 0.90025 95.02n 0.89975)")
        self.assertEqual(n, "PWL(0n 0.90025 45n 0.90025 45.02n 0.89975 95n 0.89975 95.02n 0.90025)")

    def test_longer_setup_preserves_values_and_advances_only_transition(self):
        self.assertEqual(stimulus([-0.5,0.5],1,10),
                         "PWL(0n 0.89975 40n 0.89975 40.02n 0.90025)")

    def test_longer_period_keeps_input_setup_relative_to_next_cycle(self):
        self.assertEqual(stimulus([-0.5,0.5],1,5,100),
                         "PWL(0n 0.89975 95n 0.89975 95.02n 0.90025)")


if __name__ == "__main__":
    unittest.main()
