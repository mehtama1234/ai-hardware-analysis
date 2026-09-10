import math
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fused_training_kernels.evaluation import evaluate_tokens


class UniformModel(torch.nn.Module):
    def forward(self, input_ids, use_cache):
        return SimpleNamespace(logits=torch.zeros(*input_ids.shape, 7))


class EvaluationTests(unittest.TestCase):
    def test_unequal_blocks_use_token_weighting(self):
        class BiasedModel(torch.nn.Module):
            def forward(self, input_ids, use_cache):
                logits = torch.tensor([0., 2.]).expand(*input_ids.shape, 2)
                return SimpleNamespace(logits=logits)
        tokens = [0, 1, 1, 1, 1, 0]
        report = evaluate_tokens(BiasedModel(), tokens, sequence=4)
        expected = torch.nn.functional.cross_entropy(torch.tensor([[0., 2.]]).expand(5, 2), torch.tensor(tokens[1:]))
        self.assertAlmostEqual(report['mean_nll'], float(expected), places=6)
        unweighted = sum(r['nll_sum'] / r['targets'] for r in report['blocks']) / 2
        self.assertGreater(abs(report['mean_nll'] - unweighted), 0.5)

    def test_tail_tokens_count_once_and_mode_restored(self):
        model = UniformModel().train()
        report = evaluate_tokens(model, list(range(7)) + [0, 1, 2], sequence=4)
        self.assertEqual(report['targets'], 9)
        self.assertEqual([r['targets'] for r in report['blocks']], [4, 4, 1])
        scored = [i for r in report['blocks'] for i in range(r['target_start'], r['target_end'])]
        self.assertEqual(scored, list(range(1, 10)))
        self.assertAlmostEqual(report['mean_nll'], math.log(7), places=6)
        self.assertTrue(model.training)


if __name__ == '__main__':
    unittest.main()
