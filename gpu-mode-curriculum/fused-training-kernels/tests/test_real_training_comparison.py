import sys
import unittest
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from check_real_training_parity import compare


class ComparisonTests(unittest.TestCase):
    def test_single_bad_element_cannot_hide_in_aggregate(self):
        reference = torch.ones(10000)
        actual = reference.clone()
        actual[-1] += 0.1
        result = compare(actual, reference, atol=2e-5, rtol=5e-4)
        self.assertFalse(result['passed'])
        self.assertEqual(result['outside_tolerance'], 1)

    def test_nonfinite_values_fail_even_if_shared(self):
        for value in (float('nan'), float('inf')):
            tensor = torch.tensor([value])
            result = compare(tensor, tensor, atol=2e-5, rtol=5e-4)
            self.assertFalse(result['passed'])
            self.assertFalse(result['finite'])


if __name__ == '__main__':
    unittest.main()
