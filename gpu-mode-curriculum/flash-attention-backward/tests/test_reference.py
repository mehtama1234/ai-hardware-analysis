import sys
from pathlib import Path
import unittest

import torch
from torch.nn.functional import scaled_dot_product_attention

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from flash_attention_backward.reference import attention


class AttentionReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.previous_threads = torch.get_num_threads()
        torch.set_num_threads(1)

    @classmethod
    def tearDownClass(cls):
        torch.set_num_threads(cls.previous_threads)

    def inputs(self, dtype=torch.float64):
        g = torch.Generator().manual_seed(41)
        return tuple(torch.randn(shape, generator=g, dtype=dtype).requires_grad_()
                     for shape in ((1, 2, 3, 4), (1, 2, 5, 4), (1, 2, 5, 2)))

    def test_forward_and_derivatives_against_sdpa(self):
        mask = torch.tensor([[True, False, True, False, True]] * 3)
        for dtype in (torch.float32, torch.float64):
            for kwargs in ({}, {"causal": True}, {"allowed": mask}):
                with self.subTest(dtype=dtype, kwargs=kwargs):
                    q, k, v = self.inputs(dtype)
                    got = attention(q, k, v, **kwargs)
                    expected = scaled_dot_product_attention(q, k, v,
                        attn_mask=kwargs.get("allowed"), is_causal=kwargs.get("causal", False))
                    gradient = torch.linspace(-1, 1, got.numel(), dtype=dtype).reshape_as(got)
                    actual_grads = torch.autograd.grad(got, (q, k, v), gradient)
                    expected_grads = torch.autograd.grad(expected, (q, k, v), gradient)
                    for actual, ref in zip((got, *actual_grads), (expected, *expected_grads)):
                        torch.testing.assert_close(actual, ref, atol=2e-6, rtol=2e-5)

    def test_finite_difference_gradient_check(self):
        inputs = tuple(t[:, :1, :2, :2].detach().requires_grad_() for t in self.inputs())
        for causal in (False, True):
            self.assertTrue(torch.autograd.gradcheck(lambda *xs: attention(*xs, causal=causal),
                                                     inputs, eps=1e-6, atol=1e-5, rtol=1e-3))

    def test_noncontiguous(self):
        q, k, v = (t.transpose(-2, -1).contiguous().transpose(-2, -1) for t in self.inputs())
        self.assertTrue(all(not t.is_contiguous() for t in (q, k, v)))
        torch.testing.assert_close(attention(q, k, v), scaled_dot_product_attention(q, k, v))

    def test_masked_keys_have_zero_gradient(self):
        q, k, v = self.inputs()
        mask = torch.tensor([[True, False, True, False, True]] * 3)
        output = attention(q, k, v, allowed=mask)
        dk, dv = torch.autograd.grad(output.sum(), (k, v))
        self.assertEqual(torch.count_nonzero(dk[..., 1::2, :]).item(), 0)
        self.assertEqual(torch.count_nonzero(dv[..., 1::2, :]).item(), 0)

    def test_large_finite_logits(self):
        q, k, v = self.inputs()
        output = attention(q * 100, k * 100, v)
        self.assertTrue(torch.isfinite(output).all())
        torch.testing.assert_close(output, scaled_dot_product_attention(q * 100, k * 100, v))

    def test_fully_masked_rows_rejected(self):
        with self.assertRaisesRegex(ValueError, "fully masked"):
            attention(*self.inputs(), allowed=torch.zeros((3, 5), dtype=torch.bool))

    def test_invalid_contracts(self):
        q, k, v = self.inputs()
        for kwargs in ({"allowed": torch.ones((3, 5))},
                       {"allowed": torch.ones((2, 2), dtype=torch.bool)},
                       {"causal": True, "allowed": torch.ones((3, 5), dtype=torch.bool)}):
            with self.assertRaises(ValueError):
                attention(q, k, v, **kwargs)
        with self.assertRaises(ValueError):
            attention(q.float(), k, v)


if __name__ == "__main__":
    unittest.main()
