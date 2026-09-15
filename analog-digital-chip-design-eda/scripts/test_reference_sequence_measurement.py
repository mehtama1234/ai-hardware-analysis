#!/usr/bin/env python3
"""Regression cases for settling windows and repeated bank-code stimuli."""
import unittest

import numpy as np
from run_reference_bank_sequences import analyze, bank_events, deck_for


class SequenceMeasurementTest(unittest.TestCase):
    def setUp(self):
        self.protocol = dict(first_edge_s=20e-9, edge_s=100e-12, dwell_s=150e-9,
                             maximum_step_s=50e-12, stop_s=320e-9, tolerance_fraction=1/4094)
        self.events = [dict(from_code=26, to_code=255, sequence_index=0),
                       dict(from_code=255, to_code=26, sequence_index=1)]
        self.curve = {26: .12, 255: 1.2}
        t = np.arange(0, 320e-9 + 25e-12, 50e-12)
        v = np.where(t < 20.1e-9, .12, np.where(t < 170.1e-9, 1.2, .12))
        self.data = np.column_stack((t, v))

    def test_next_edge_does_not_invalidate_previous_settling(self):
        rows = analyze(self.data, self.events, self.curve, self.protocol)
        self.assertTrue(all(r['settled_before_next_edge'] for r in rows))
        self.assertLess(rows[0]['sampled_settling_after_edge_s'], 51e-12)

    def test_late_glitch_requires_resettling(self):
        self.data[2000, 1] += .01
        row = analyze(self.data, self.events, self.curve, self.protocol)[0]
        self.assertTrue(row['settled_before_next_edge'])
        self.assertGreater(row['sampled_settling_after_edge_s'], 79e-9)

    def test_persistent_error_is_not_settled(self):
        mask = (self.data[:, 0] >= 20.1e-9) & (self.data[:, 0] < 170e-9)
        self.data[mask, 1] += .01
        row = analyze(self.data, self.events, self.curve, self.protocol)[0]
        self.assertFalse(row['settled_before_next_edge'])
        self.assertIsNone(row['sampled_settling_after_edge_s'])

    def test_vector_wrap_and_complementary_pwl_are_preserved(self):
        transitions = [dict(bank=0, from_code=26 if i % 2 == 0 else 255,
                            to_code=255 if i % 2 == 0 else 26) for i in range(18)]
        events = bank_events({'steady_state_bank_transitions': transitions}, 0)
        self.assertEqual(len(events), 36)
        self.assertEqual(events[18]['from_code'], events[17]['to_code'])
        p = dict(self.protocol, stop_s=20e-9 + 36 * 150e-9)
        deck = deck_for(events, 1e-13, p)
        gates = [line for line in deck.splitlines() if line.startswith('VB')]
        self.assertEqual(len(gates), 16)
        for a, b in zip(gates[::2], gates[1::2]):
            points_a = np.fromstring(a.split('PWL(')[1][:-1], sep=' ').reshape(-1, 2)
            points_b = np.fromstring(b.split('PWL(')[1][:-1], sep=' ').reshape(-1, 2)
            np.testing.assert_array_equal(points_a[:, 0], points_b[:, 0])
            np.testing.assert_allclose(points_a[:, 1] + points_b[:, 1], 1.8)
            self.assertTrue(np.all(np.diff(points_a[:, 0]) > 0))


if __name__ == '__main__':
    unittest.main()
