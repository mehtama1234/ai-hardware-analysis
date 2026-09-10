import sys
import unittest
from pathlib import Path

import torch
import torch.nn.functional as F

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fused_training_kernels.linear_cross_entropy import linear_cross_entropy


class LinearCrossEntropyTests(unittest.TestCase):
    def test_large_common_logit_offset_preserves_loss(self):
        hidden = torch.ones(3, 1, requires_grad=True)
        weight = torch.full((7, 1), 10000., requires_grad=True)
        labels = torch.tensor([0, 3, 6])
        actual = linear_cross_entropy(hidden, weight, labels, chunk_size=2)
        expected = F.cross_entropy(hidden @ weight.t(), labels)
        torch.testing.assert_close(actual, expected, atol=2e-7, rtol=2e-7)

    def test_derivatives_and_noncontiguous_inputs(self):
        torch.manual_seed(9)
        h = torch.randn(3, 5, dtype=torch.double).t().requires_grad_()
        w = torch.randn(3, 7, dtype=torch.double).t().requires_grad_()
        b = torch.randn(7, dtype=torch.double, requires_grad=True)
        y = torch.tensor([0, 6, -100, 2, 1])
        for reduction in ('mean', 'sum'):
            for chunk in (1, 3, 8):
                with self.subTest(reduction=reduction, chunk=chunk):
                    fn = lambda x, weight, bias: linear_cross_entropy(x, weight, y, bias, chunk_size=chunk, reduction=reduction)
                    self.assertTrue(torch.autograd.gradcheck(fn, (h, w, b)))
                    actual, expected = fn(h, w, b), F.cross_entropy(h @ w.t() + b, y, reduction=reduction)
                    torch.testing.assert_close(actual, expected)
                    for a, e in zip(torch.autograd.grad(2.7 * actual, (h, w, b)), torch.autograd.grad(2.7 * expected, (h, w, b))):
                        torch.testing.assert_close(a, e)

    def test_all_ignored_and_frozen_weight(self):
        h = torch.randn(4, 3, requires_grad=True)
        w = torch.randn(7, 3)
        y = torch.full((4,), -100)
        loss = linear_cross_entropy(h, w, y, chunk_size=3)
        self.assertTrue(torch.isnan(loss))
        loss.backward()
        self.assertEqual(torch.count_nonzero(h.grad).item(), 0)
        self.assertEqual(linear_cross_entropy(h, w, y, reduction='sum').item(), 0)
        y = torch.tensor([0, 1, 6, 2])
        actual = linear_cross_entropy(h, w, y, chunk_size=3)
        expected = F.cross_entropy(h @ w.t(), y)
        torch.testing.assert_close(torch.autograd.grad(actual, h)[0], torch.autograd.grad(expected, h)[0])
        with torch.autocast('cpu', dtype=torch.bfloat16):
            with self.assertRaisesRegex(ValueError, 'autocast'):
                linear_cross_entropy(h, w, y)

    def test_large_logits_and_invalid_targets(self):
        h = torch.tensor([[1000., -1000.]], requires_grad=True)
        w = torch.tensor([[1., 1.], [-1., 1.], [1., -1.]], requires_grad=True)
        y = torch.tensor([1])
        actual = linear_cross_entropy(h, w, y)
        expected = F.cross_entropy(h @ w.t(), y)
        torch.testing.assert_close(actual, expected)
        for a, e in zip(torch.autograd.grad(actual, (h, w)), torch.autograd.grad(expected, (h, w))):
            torch.testing.assert_close(a, e)
        with self.assertRaises(ValueError):
            linear_cross_entropy(h, w, torch.tensor([3]))

    def test_saved_tensors_exclude_logits(self):
        h = torch.randn(13, 5, requires_grad=True)
        w = torch.randn(17, 5, requires_grad=True)
        y = torch.arange(13) % 17
        saved = []
        with torch.autograd.graph.saved_tensors_hooks(lambda t: (saved.append(t.shape) or t), lambda t: t):
            loss = linear_cross_entropy(h, w, y, chunk_size=3)
        self.assertNotIn(torch.Size([13, 17]), saved)
        self.assertEqual(saved, [h.shape, w.shape, y.shape, torch.Size([])])
        loss.backward()

    def test_tied_embedding_multiseed_updates(self):
        # Synthetic regression test, not real-data learning evidence.
        for seed in (7, 19, 41):
            torch.manual_seed(seed)
            a = torch.nn.Parameter(torch.randn(11, 6) * 0.1)
            b = torch.nn.Parameter(a.detach().clone())
            opts = [torch.optim.AdamW([p], lr=0.01) for p in (a, b)]
            x, y = torch.tensor([1, 4, 1, 8, 2]), torch.tensor([4, 1, -100, 2, 3])
            for _ in range(5):
                for p, opt, custom in zip((a, b), opts, (False, True)):
                    opt.zero_grad(set_to_none=True)
                    h = F.embedding(x, p)
                    loss = linear_cross_entropy(h, p, y, chunk_size=2) if custom else F.cross_entropy(h @ p.t(), y)
                    loss.backward()
                    opt.step()
                torch.testing.assert_close(a, b, atol=2e-6, rtol=2e-5)
                for key in ('exp_avg', 'exp_avg_sq'):
                    torch.testing.assert_close(opts[0].state[a][key], opts[1].state[b][key], atol=2e-7, rtol=2e-5)


if __name__ == '__main__':
    unittest.main()
