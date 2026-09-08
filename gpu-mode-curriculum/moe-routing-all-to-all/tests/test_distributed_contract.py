from pathlib import Path
import sys
import unittest
from unittest.mock import patch
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from moe_routing_all_to_all.distributed import agree_contract, local_contract


class DistributedContractTests(unittest.TestCase):
    def inputs(self, count=2):
        return torch.ones(count, 3), torch.ones(count, 4), torch.ones(2, 2, 3)

    def test_empty_and_uneven_counts_share_contract(self):
        expected = local_contract(*self.inputs(2), 2, 3, 2)
        for count in (0, 1, 5):
            self.assertEqual(local_contract(*self.inputs(count), 2, 3, 2), expected)

    def test_bad_shapes_and_values(self):
        for weights in (None, torch.ones(2, 3), torch.ones(0, 2, 3), torch.ones(2, 2, 4)):
            x, l, _ = self.inputs()
            with self.assertRaises(ValueError):
                local_contract(x, l, weights, 2, 3, 2)
        for k, capacity in ((True, 3), (0, 3), (5, 3), (2, -1)):
            with self.assertRaises(ValueError):
                local_contract(*self.inputs(), k, capacity, 2)

    def test_peer_rejection_and_mismatch_propagate(self):
        # Mock metadata transport only; actual two-process failures are checked
        # by run_distributed_reference.py, not claimed from this test.
        signature = local_contract(*self.inputs(), 2, 3, 2)
        for peer in ({"error": "bad peer"}, {"contract": (*signature[:-1], 4)}):
            def gather(output, local):
                output[:] = [local, peer]
            with patch("moe_routing_all_to_all.distributed.dist.get_world_size", return_value=2), \
                 patch("moe_routing_all_to_all.distributed.dist.all_gather_object", side_effect=gather):
                with self.assertRaises(ValueError):
                    agree_contract(*self.inputs(), 2, 3)


if __name__ == "__main__":
    unittest.main()
