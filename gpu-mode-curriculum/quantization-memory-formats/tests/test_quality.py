import sys
import unittest
from pathlib import Path
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from quantization_memory_formats.quality import measure_linear_quality


class QualityTests(unittest.TestCase):
    def test_metrics_are_finite_and_storage_is_reported(self):
        torch.manual_seed(11)
        metrics = measure_linear_quality(torch.randn(9, 8), torch.randn(5, 8), torch.randn(5))
        self.assertEqual(metrics['rows'], 9)
        self.assertLess(metrics['storage_ratio'], 0.6)
        for key in ('max_abs_error', 'rmse', 'relative_l2_error', 'cosine_similarity', 'storage_ratio'):
            self.assertTrue(torch.isfinite(torch.tensor(metrics[key])))
        self.assertGreaterEqual(metrics['cosine_similarity'], -1)
        self.assertLessEqual(metrics['cosine_similarity'], 1)

    def test_zero_reference_is_stable(self):
        metrics = measure_linear_quality(torch.zeros(2, 4), torch.ones(3, 4))
        self.assertEqual(metrics['max_abs_error'], 0)
        self.assertEqual(metrics['relative_l2_error'], 0)
        self.assertEqual(metrics['cosine_similarity'], 0)


if __name__ == '__main__':
    unittest.main()
