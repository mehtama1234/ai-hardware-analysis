import importlib.util
import unittest
from pathlib import Path

import torch

MODULE_PATH = Path(__file__).resolve().parents[1] / "run_vectorized_simulation.py"
spec = importlib.util.spec_from_file_location("vectorized_simulation", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class VectorizedSimulationTests(unittest.TestCase):
    def test_vectorized_matches_scalar_oracle(self):
        starts = torch.tensor([[0, 0], [2, 2], [30, 30]], dtype=torch.int64)
        goals = torch.tensor([[0, 1], [1, 2], [29, 30]], dtype=torch.int64)
        actions = torch.tensor([[2, 0, 0], [3, 0, 2], [1, 1, 3]], dtype=torch.int64)
        expected_positions, expected_rewards = module.scalar_rollout(starts.tolist(), goals.tolist(), actions.tolist())
        positions, rewards = module.vectorized_rollout(starts, goals, actions)
        self.assertEqual(positions.tolist(), expected_positions)
        self.assertEqual(rewards.tolist(), expected_rewards)

    def test_boundaries_are_clamped(self):
        starts = torch.tensor([[0, 0]], dtype=torch.int64)
        goals = torch.tensor([[0, 0]], dtype=torch.int64)
        actions = torch.tensor([[0], [2]], dtype=torch.int64)
        positions, rewards = module.vectorized_rollout(starts, goals, actions)
        self.assertEqual(positions.tolist(), [[[0, 0]][0]])
        self.assertEqual(rewards.tolist(), [[10.0], [10.0]])

    def test_policy_termination_and_reset_match_oracle(self):
        starts = torch.tensor([[0, 0], [2, 2]], dtype=torch.int64)
        goals = torch.tensor([[0, 2], [1, 2]], dtype=torch.int64)
        expected = module.scalar_policy_episode(starts.tolist(), goals.tolist(), 4)
        actual = module.vectorized_policy_episode(starts, goals, 4)
        self.assertEqual(actual[0].tolist(), expected[0])
        self.assertEqual(actual[1].tolist(), expected[1].tolist())
        self.assertEqual(actual[2].tolist(), expected[2].tolist())
        self.assertEqual(actual[3], expected[3])


if __name__ == "__main__":
    unittest.main()
