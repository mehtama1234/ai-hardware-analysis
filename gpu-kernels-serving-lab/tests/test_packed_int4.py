import sys
from pathlib import Path
import unittest
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common.packed_int4 import PackedInt4, pack_int4, unpack_int4


class PackedInt4Tests(unittest.TestCase):
    def test_known_nibbles(self):
        weights = torch.tensor([-7., 7., 0., 1.])
        packed = pack_int4(weights, block=4)
        self.assertEqual(packed.payload.tolist(), [241, 152])
        torch.testing.assert_close(unpack_int4(packed), weights, atol=0, rtol=0)

    def test_tails_and_storage(self):
        for count in (1, 7, 31, 32, 33, 65):
            for block in (1, 3, 32):
                weights = torch.linspace(-1, 1, count)
                packed = pack_int4(weights, block)
                result = unpack_int4(packed)
                self.assertEqual(result.shape, weights.shape)
                self.assertEqual(packed.tensor_storage_bytes, (count + 1) // 2 + 4 * ((count + block - 1) // block))
                bounds = packed.scales.repeat_interleave(block)[:count] / 2 + 1e-7
                self.assertTrue(((weights - result).abs() <= bounds).all())

    def test_zeros_noncontiguous(self):
        weights = torch.zeros((3, 7)).t()
        self.assertFalse(weights.is_contiguous())
        torch.testing.assert_close(unpack_int4(pack_int4(weights)), weights)

    def test_invalid(self):
        for value in (torch.empty(0), torch.tensor([float("inf")]), torch.ones(3, dtype=torch.float64)):
            with self.assertRaises(ValueError):
                pack_int4(value)
        for block in (0, True, 1.5):
            with self.assertRaises(ValueError):
                pack_int4(torch.ones(3), block)
        with self.assertRaises(ValueError):
            unpack_int4(PackedInt4(torch.tensor([0], dtype=torch.uint8), torch.ones(1), (1,), 32))
