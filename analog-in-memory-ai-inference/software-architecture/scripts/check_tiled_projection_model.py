#!/usr/bin/env python3
"""Check ragged tiling, fixed quantization range, and deterministic noise."""

import unittest

import torch

from tiled_projection_model import Profile, TiledProjection, quantize


class ProjectionChecks(unittest.TestCase):
    def test_ragged_tiles_preserve_linear_map_and_counts(self):
        torch.manual_seed(4)
        x, w, bias = torch.randn(2, 3, 5), torch.randn(5, 7), torch.randn(7)
        projection = TiledProjection(w, bias, 4, Profile(tile_rows=3, tile_columns=4))
        torch.testing.assert_close(projection(x, ideal=True), x @ w + bias)
        contract = projection.contract()
        self.assertEqual(contract["logical_tiles"], 4)
        self.assertEqual(contract["physical_arrays_if_differential_pair"], 8)
        self.assertEqual(contract["per_vector"]["dac_conversions_without_column_tile_broadcast"], 10)
        self.assertEqual(contract["per_vector"]["adc_conversions_after_differential_subtraction"], 14)
        self.assertEqual(contract["per_vector"]["digital_partial_sum_additions"], 7)

    def test_fixed_range_clipping_does_not_recalibrate_on_evaluation(self):
        p = TiledProjection(torch.eye(2), torch.zeros(2), 1, Profile(tile_rows=1, tile_columns=1))
        result = p(torch.tensor([[3., -3.]]))
        torch.testing.assert_close(result, torch.tensor([[1., -1.]]))
        self.assertEqual(p.trace[0]["dac_clipped_values"], 2)
        self.assertEqual(p.activation_bound, 1)

    def test_exact_quantization_grid(self):
        x = torch.tensor([-2., -1., 0., 1., 2.])
        torch.testing.assert_close(quantize(x, 1, 2), torch.tensor([-1., -1., 0., 1., 1.]))

    def test_noise_reproducibility_and_repeated_read_variation(self):
        w, bias, x = torch.ones(4, 4), torch.zeros(4), torch.ones(1, 4) * 0.1
        profile = Profile(read_noise_fraction=0.01)
        a, b = TiledProjection(w, bias, 1, profile, 3), TiledProjection(w, bias, 1, profile, 3)
        first = a(x)
        torch.testing.assert_close(first, b(x), rtol=0, atol=0)
        self.assertFalse(torch.equal(first, a(x)))

    def test_invalid_physical_assumptions_fail(self):
        for kwargs in ({"tile_rows": 0}, {"adc_bits": 1}, {"read_noise_fraction": float("nan")}, {"read_noise_fraction": -1}):
            with self.assertRaises(ValueError):
                Profile(**kwargs)
        with self.assertRaises(ValueError):
            TiledProjection(torch.eye(2), torch.zeros(2), 0, Profile())


if __name__ == "__main__":
    torch.set_num_threads(2)
    unittest.main()
