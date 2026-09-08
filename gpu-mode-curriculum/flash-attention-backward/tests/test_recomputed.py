import sys
from pathlib import Path
import unittest
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from flash_attention_backward.reference import attention
from flash_attention_backward.recomputed import recomputed_attention


class RecomputedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.threads = torch.get_num_threads()
        torch.set_num_threads(1)

    @classmethod
    def tearDownClass(cls):
        torch.set_num_threads(cls.threads)

    def test_outputs_and_gradients(self):
        generator = torch.Generator().manual_seed(13)
        # Initial key tiles entirely masked: exercises -inf online state.
        mask = torch.tensor([[False, False, False, True, True]] * 3)
        for dtype in (torch.float32, torch.float64):
            inputs = tuple(torch.randn(shape, generator=generator, dtype=dtype).requires_grad_()
                           for shape in ((2, 3, 4), (2, 5, 4), (2, 5, 2)))
            for kwargs in ({}, {"causal": True}, {"allowed": mask}):
                for block in (1, 2, 8):
                    with self.subTest(dtype=dtype, kwargs=kwargs, block=block):
                        actual = recomputed_attention(*inputs, block=block, **kwargs)
                        expected = attention(*inputs, **kwargs)
                        g = torch.randn(actual.shape, generator=generator, dtype=dtype)
                        ag = torch.autograd.grad(actual, inputs, g)
                        eg = torch.autograd.grad(expected, inputs, g)
                        for a, e in zip((actual, *ag), (expected, *eg)):
                            torch.testing.assert_close(a, e, atol=2e-6, rtol=2e-5)

    def test_gradcheck(self):
        generator = torch.Generator().manual_seed(15)
        inputs = tuple(torch.randn((2, 2), generator=generator, dtype=torch.float64).requires_grad_()
                       for _ in range(3))
        for causal in (False, True):
            self.assertTrue(torch.autograd.gradcheck(
                lambda *xs: recomputed_attention(*xs, block=1, causal=causal), inputs))

    def test_saved_tensors_are_not_quadratic(self):
        q, k, v = (torch.randn((1, 64, 8), requires_grad=True) for _ in range(3))
        def capture(fn):
            saved = []
            def pack(tensor):
                saved.append((tuple(tensor.shape), tensor.numel() * tensor.element_size()))
                return tensor
            with torch.autograd.graph.saved_tensors_hooks(pack, lambda tensor: tensor):
                fn(q, k, v, causal=True)
            return saved
        dense = capture(attention)
        tiled = capture(recomputed_attention)
        self.assertIn((1, 64, 64), [shape for shape, _ in dense])
        self.assertNotIn((1, 64, 64), [shape for shape, _ in tiled])
        self.assertLess(sum(size for _, size in tiled), sum(size for _, size in dense))

    def test_invalid_block(self):
        for block in (0, -1, True, 1.5):
            with self.assertRaises(ValueError):
                recomputed_attention(*(torch.ones((2, 2)) for _ in range(3)), block=block)


if __name__ == "__main__":
    unittest.main()
