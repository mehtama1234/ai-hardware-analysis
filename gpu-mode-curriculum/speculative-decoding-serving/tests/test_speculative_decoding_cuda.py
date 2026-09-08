import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "gpu-kernels-serving-lab" / "13-capstone-mini-serving-engine"))

from run_speculative_decoding_cuda import speculative_generate  # noqa: E402
from neural_generator import NeuralGenerator  # noqa: E402


class SpeculativeDecodeTests(unittest.TestCase):
    def test_draft_target_path_matches_greedy_target(self):
        target = NeuralGenerator("cpu", hidden=32, heads=4, seed=151)
        draft = NeuralGenerator("cpu", hidden=32, heads=4, seed=152)
        expected, _ = target.generate("attention cache", 8, cached=True, cache_storage="preallocated")
        actual, stats = speculative_generate(target, draft, "attention cache", 8, 3)
        self.assertEqual(actual, expected)
        self.assertGreater(stats["draft_tokens"], 0)
        self.assertEqual(stats["kv_tokens_committed"], len(actual))
        self.assertGreaterEqual(stats["rollback_tokens"], 0)

    def test_exact_draft_records_no_rollback(self):
        target = NeuralGenerator("cpu", hidden=32, heads=4, seed=151)
        draft = NeuralGenerator("cpu", hidden=32, heads=4, seed=151)
        expected, _ = target.generate("gpu serving", 8, cached=True, cache_storage="preallocated")
        actual, stats = speculative_generate(target, draft, "gpu serving", 8, 4)
        self.assertEqual(actual, expected)
        self.assertEqual(stats["rollback_tokens"], 0)
        self.assertEqual(stats["accepted_tokens"], stats["draft_tokens"])

    def test_adaptive_policy_falls_back_and_preserves_target(self):
        target = NeuralGenerator("cpu", hidden=32, heads=4, seed=151)
        draft = NeuralGenerator("cpu", hidden=32, heads=4, seed=152)
        expected, _ = target.generate("attention cache", 8, cached=True, cache_storage="preallocated")
        actual, stats = speculative_generate(
            target, draft, "attention cache", 8, 3, fallback_threshold=0.5
        )
        self.assertEqual(actual, expected)
        self.assertTrue(stats["policy_fallback"])
        self.assertGreater(stats["fallback_tokens"], 0)


if __name__ == "__main__":
    unittest.main()
