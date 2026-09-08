import copy
import sys
from pathlib import Path
import unittest
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common.packed_int4 import PackedInt4, unpack_int4
from common.packed_linear import PackedInt4Linear, converted_copy, tensor_storage_bytes


class PackedLinearTests(unittest.TestCase):
    def test_linear_and_state_roundtrip(self):
        source = torch.nn.Linear(7, 5).eval()
        packed = converted_copy(source)
        x = torch.randn((2, 7))
        weights = unpack_int4(PackedInt4(packed.payload, packed.scales, (5, 7), 32))
        torch.testing.assert_close(packed(x), torch.nn.functional.linear(x, weights, source.bias))
        loaded = converted_copy(torch.nn.Linear(7, 5))
        loaded.load_state_dict(packed.state_dict())
        torch.testing.assert_close(loaded(x), packed(x), atol=0, rtol=0)
        self.assertEqual(list(packed.parameters()), [])
        self.assertFalse(hasattr(packed, "weight"))

    def test_copy_and_storage(self):
        model = torch.nn.Sequential(torch.nn.Linear(32, 32), torch.nn.ReLU(), torch.nn.Linear(32, 16))
        before = copy.deepcopy(model.state_dict())
        packed = converted_copy(model)
        self.assertTrue(isinstance(packed[0], PackedInt4Linear))
        self.assertLess(tensor_storage_bytes(packed), tensor_storage_bytes(model))
        for name, value in model.state_dict().items():
            torch.testing.assert_close(value, before[name], atol=0, rtol=0)

    def test_contracts(self):
        packed = converted_copy(torch.nn.Linear(7, 5))
        state = packed.get_extra_state()
        state["block"] = 16
        with self.assertRaises(ValueError):
            packed.set_extra_state(state)
        with self.assertRaises(ValueError):
            packed(torch.ones(7, dtype=torch.float64))
        packed.train()
        with self.assertRaises(ValueError):
            packed(torch.ones(7))
