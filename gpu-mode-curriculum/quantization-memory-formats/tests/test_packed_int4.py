import sys
import unittest
from pathlib import Path
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from quantization_memory_formats.packed_int4 import pack_int4, linear


class PackedInt4Tests(unittest.TestCase):
    def test_round_trip_and_storage(self):
        torch.manual_seed(4)
        weight = torch.randn(5, 8)
        packed = pack_int4(weight)
        self.assertEqual(tuple(packed.data.shape), (5, 4))
        self.assertEqual(packed.storage_bytes, 5 * 4 + 5 * 4)
        self.assertLessEqual((packed.dequantize() - weight).abs().max().item(), float(packed.scales.max()))

    def test_zero_rows_and_signed_nibbles(self):
        weight = torch.tensor([[0., 0., 0., 0.], [-7., -1., 1., 7.]])
        packed = pack_int4(weight)
        torch.testing.assert_close(packed.dequantize(), weight)
        self.assertEqual(packed.data[1].tolist(), [0xF9, 0x71])

    def test_linear_matches_dequantized_reference(self):
        torch.manual_seed(6)
        x, w, b = torch.randn(3, 8), torch.randn(4, 8), torch.randn(4)
        packed = pack_int4(w)
        torch.testing.assert_close(linear(x, packed, b), x @ packed.dequantize().t() + b)
        for bad in (torch.ones(3, 7), torch.ones(3, 8, dtype=torch.int8), torch.full((4, 8), float('nan'))):
            with self.assertRaises(ValueError):
                pack_int4(bad)


if __name__ == '__main__':
    unittest.main()
