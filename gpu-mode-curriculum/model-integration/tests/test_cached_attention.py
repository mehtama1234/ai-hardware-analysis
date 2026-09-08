import sys
from pathlib import Path
import unittest
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from model_integration.tiny_transformer import TinyTransformerBlock


class CachedAttentionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.threads = torch.get_num_threads()
        torch.set_num_threads(1)

    @classmethod
    def tearDownClass(cls):
        torch.set_num_threads(cls.threads)

    def test_chunked_and_token_decode(self):
        generator = torch.Generator().manual_seed(103)
        x = torch.randn((2, 35, 16), generator=generator)
        for backend in ("materialized", "sdpa", "recomputed"):
            model = TinyTransformerBlock(16, 2, False, backend).eval()
            with torch.no_grad():
                full = model(x)
            for chunks in ((17, 1, 1, 16), (1,) * 35, (35,)):
                cache, position, outputs = None, 0, []
                for chunk in chunks:
                    previous = tuple(t.clone() for t in cache) if cache is not None else None
                    output, updated = model.forward_cached(x[:, position:position + chunk], cache)
                    if previous is not None:
                        for before, after in zip(previous, cache):
                            torch.testing.assert_close(before, after, atol=0, rtol=0)
                    position += chunk
                    self.assertEqual(updated[0].shape[-2], position)
                    self.assertFalse(output.requires_grad)
                    outputs.append(output)
                    cache = updated
                torch.testing.assert_close(torch.cat(outputs, dim=1), full, atol=2e-6, rtol=2e-5)

    def test_contract_rejections(self):
        model = TinyTransformerBlock(16, 2, False)
        x = torch.ones((1, 1, 16))
        with self.assertRaisesRegex(ValueError, "eval"):
            model.forward_cached(x)
        model.eval()
        for cache in ((), (torch.zeros(1), torch.zeros(1)),
                      (torch.zeros((1, 2, 3, 8)), torch.zeros((1, 2, 2, 8)))):
            with self.assertRaises(ValueError):
                model.forward_cached(x, cache)
