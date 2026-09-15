#!/usr/bin/env python3
import unittest
import torch
from calibrated_adc_projection import CalibratedADCProjection
from tiled_projection_model import Profile


class RangeTests(unittest.TestCase):
    def make(self, inputs, **kwargs):
        return CalibratedADCProjection(torch.eye(2), torch.zeros(2), 1.0,
                                       Profile(tile_rows=1,tile_columns=1,adc_bits=8), inputs, **kwargs)

    def test_ranges_frozen_and_unseen_input_clips(self):
        projection = self.make(torch.tensor([[.2,.3]]))
        before = projection.contract()["adc_range"]
        self.assertEqual(len(projection.trace), 0)
        projection(torch.tensor([[1.,1.]]))
        self.assertGreater(projection.trace[-1]["adc_clipped_values"], 0)
        self.assertEqual(before, projection.contract()["adc_range"])
        for row in before["ranges"]:
            self.assertLessEqual(row["selected_bound"], row["conservative_bound"])

    def test_zero_signal_does_not_invent_narrow_range(self):
        projection = self.make(torch.zeros(2,2))
        for row in projection.contract()["adc_range"]["ranges"]:
            self.assertEqual(row["selected_bound"],row["conservative_bound"])

    def test_ideal_bypasses_calibrated_quantization(self):
        projection = self.make(torch.tensor([[.1,.1]]))
        value=torch.tensor([[.9,-.8]])
        torch.testing.assert_close(projection(value, ideal=True),value)

    def test_invalid_calibration(self):
        for value in [torch.empty(0,2),torch.ones(2,3),torch.full((1,2),float("nan"))]:
            with self.assertRaises(ValueError): self.make(value)
        with self.assertRaises(ValueError): self.make(torch.ones(1,2), headroom=.9)

    def test_contract_cannot_mutate_calibration_record(self):
        projection=self.make(torch.ones(1,2))
        contract=projection.contract()
        contract["adc_range"]["headroom"]=0
        self.assertEqual(projection.contract()["adc_range"]["headroom"],1.1)


if __name__ == "__main__":
    unittest.main()
