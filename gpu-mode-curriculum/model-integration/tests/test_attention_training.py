import sys
import math
from pathlib import Path
import unittest
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from model_integration.attention_training import checked_error, run_training_case
from model_integration.tiny_transformer import TinyTransformerBlock


class IntegrationTests(unittest.TestCase):
    def test_training_pair(self):
        threads = torch.get_num_threads()
        torch.set_num_threads(1)
        try:
            for length in (1, 17, 33):
                result = run_training_case(length)
                self.assertEqual(len(result["steps"]), 3)
                self.assertTrue(all(row["parameter_gradient_errors"] for row in result["steps"]))
        finally:
            torch.set_num_threads(threads)

    def test_corruption_rejected(self):
        for actual in (None, torch.tensor(float("nan")), torch.tensor(1.0)):
            with self.assertRaises(AssertionError):
                checked_error(actual, torch.tensor(0.0))

    def test_training_timing_samples(self):
        threads = torch.get_num_threads()
        torch.set_num_threads(1)
        try:
            result = run_training_case(1, 1, benchmark=True)
            timing = result["timing"]
            self.assertEqual(timing["warmup_pairs"], 3)
            for key in ("reference_seconds", "candidate_seconds"):
                self.assertEqual(len(timing[key]), 10)
                self.assertTrue(all(math.isfinite(t) and t > 0 for t in timing[key]))
        finally:
            torch.set_num_threads(threads)

    def test_backend_validation(self):
        with self.assertRaises(ValueError):
            TinyTransformerBlock(16, 2, False, attention_backend="unknown")


if __name__ == "__main__":
    unittest.main()
