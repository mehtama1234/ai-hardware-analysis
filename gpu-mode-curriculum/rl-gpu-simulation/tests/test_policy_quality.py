import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "run_policy_quality.py"
spec = importlib.util.spec_from_file_location("policy_quality", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PolicyQualityTests(unittest.TestCase):
    def test_shortest_action_prioritizes_vertical_then_horizontal(self):
        import torch
        positions = torch.tensor([[0, 0], [3, 2], [2, 1], [2, 2]])
        goals = torch.tensor([[2, 1], [1, 2], [2, 3], [2, 2]])
        self.assertEqual(module.shortest_action(positions, goals).tolist(), [1, 0, 3, 0])


if __name__ == "__main__":
    unittest.main()
