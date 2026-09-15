#!/usr/bin/env python3
import unittest
import torch
from projection_numerical_control import assess


class ControlTests(unittest.TestCase):
    def setUp(self):
        self.projection = torch.tensor([[1., 2., 3.]], dtype=torch.float64)
        self.logits = torch.tensor([[[1., 3., -2.], [2., -1., 4.]]], dtype=torch.float64)
        self.targets = torch.tensor([1, 2])

    def check_candidate(self, logits, projection=None):
        return assess(self.projection, self.projection if projection is None else projection,
                      self.logits, logits, self.targets)

    def test_position_specific_common_offset(self):
        shifted = self.logits + torch.tensor([[[100.], [-200.]]])
        self.assertTrue(self.check_candidate(shifted)["pass"])

    def test_probability_change_without_argmax_change(self):
        changed = self.logits.clone()
        changed[0, 0, 0] += .1
        result = self.check_candidate(changed)
        self.assertTrue(result["identical_argmax"])
        self.assertFalse(result["pass"])

    def test_local_arithmetic_must_pass_even_if_logits_match(self):
        self.assertFalse(self.check_candidate(self.logits, self.projection.flip(-1))["pass"])

    def test_decision_change(self):
        self.assertFalse(self.check_candidate(self.logits.flip(-1))["pass"])

    def test_nonfinite(self):
        bad = self.logits.clone()
        bad[0, 0, 0] = float("nan")
        self.assertFalse(self.check_candidate(bad)["pass"])


if __name__ == "__main__":
    unittest.main()
