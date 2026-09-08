import importlib.util
from pathlib import Path
import unittest
import torch

spec = importlib.util.spec_from_file_location("digits_quality", Path(__file__).resolve().parents[1] /
                                              "08-quantized-inference/run_digits_quality.py")
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)


class DigitsProtocolTests(unittest.TestCase):
    def test_split_disjoint_complete_reproducible(self):
        labels = torch.arange(10).repeat_interleave(10)
        train, test = lab.split_indices(labels)
        self.assertEqual(len(train), 80)
        self.assertEqual(len(test), 20)
        self.assertFalse(set(train.tolist()) & set(test.tolist()))
        self.assertEqual(sorted(train.tolist() + test.tolist()), list(range(100)))
        torch.testing.assert_close(train, lab.split_indices(labels)[0])
        self.assertEqual(torch.bincount(labels[test]).tolist(), [2] * 10)

    def test_quality_gate_rejects_regressions(self):
        self.assertTrue(all(lab.quality_gate(.95, .94, 400, 100).values()))
        for args in ((.80, .80, 400, 100), (.95, .90, 400, 100), (.95, .95, 400, 500)):
            self.assertFalse(all(lab.quality_gate(*args).values()))
