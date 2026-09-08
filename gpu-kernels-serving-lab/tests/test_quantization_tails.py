import importlib.util
from pathlib import Path
import unittest
import torch

spec = importlib.util.spec_from_file_location("quantization_lab", Path(__file__).resolve().parents[1] /
                                              "08-quantized-inference/run.py")
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)


class QuantizationTailTests(unittest.TestCase):
    def test_every_value_retained(self):
        for size in (1, 7, 31, 32, 33, 65):
            x = torch.linspace(-1, 1, size)
            for quantize in (lab.int4_block_quant, lab.mxfp4_like_quant):
                with self.subTest(size=size, quantize=quantize.__name__):
                    result = quantize(torch, x)
                    self.assertEqual(result.shape, x.shape)
                    self.assertTrue(torch.isfinite(result).all())

    def test_zero_and_tail_isolation(self):
        for quantize in (lab.int4_block_quant, lab.mxfp4_like_quant):
            torch.testing.assert_close(quantize(torch, torch.zeros(33)), torch.zeros(33))
            prefix = torch.linspace(-1, 1, 32)
            extended = torch.cat((prefix, torch.tensor([1000.])))
            torch.testing.assert_close(quantize(torch, extended)[:32], quantize(torch, prefix), atol=0, rtol=0)
            self.assertGreater(quantize(torch, extended)[-1].item(), 0)

    def test_invalid_inputs(self):
        for quantize in (lab.int4_block_quant, lab.mxfp4_like_quant):
            for x in (torch.empty(0), torch.tensor([float("nan")]), torch.tensor([1])):
                with self.assertRaises(ValueError):
                    quantize(torch, x)
            for block in (0, -1, True, 1.5):
                with self.assertRaises(ValueError):
                    quantize(torch, torch.ones(3), block)
