"""Train-observed ADC ranges for a future, separately qualified experiment.

This requires programmable analog gain/reference ranges not established by the
physical design. It does not modify the existing worst-case-range benchmark.
"""
import hashlib
import math
from copy import deepcopy

import torch

from tiled_projection_model import TiledProjection, quantize


class CalibratedADCProjection(TiledProjection):
    def __init__(self, weight, bias, activation_bound, profile, calibration_inputs,
                 seed=8181, headroom=1.1):
        if not math.isfinite(headroom) or headroom < 1:
            raise ValueError("Headroom must be finite and at least one")
        if calibration_inputs.ndim < 2 or calibration_inputs.shape[-1] != weight.shape[0]:
            raise ValueError("Calibration inputs must match the input dimension")
        if calibration_inputs.numel() == 0 or not bool(torch.isfinite(calibration_inputs).all()):
            raise ValueError("Calibration inputs must be nonempty and finite")
        if calibration_inputs.dtype != weight.dtype or calibration_inputs.device != weight.device:
            raise ValueError("Calibration inputs must match weight dtype and device")
        super().__init__(weight, bias, activation_bound, profile, seed)
        flat = calibration_inputs.detach().reshape(-1, weight.shape[0])
        observed_input_hash = hashlib.sha256(flat.cpu().contiguous().view(torch.uint8).numpy().tobytes()).hexdigest()
        x = quantize(flat, activation_bound, profile.dac_bits)
        ranges = []
        calibrated_tiles = []
        with torch.inference_mode():
            for r, c, qw, conservative_bound in self.tiles:
                observed = float((x[:, r:r + qw.shape[0]] @ qw).abs().max())
                # No observed signal means no evidence to narrow this tile's range.
                bound = min(conservative_bound, observed * headroom) if observed > 0 else conservative_bound
                bound = max(bound, 1e-12)
                calibrated_tiles.append((r, c, qw, bound))
                ranges.append({"row": r, "column": c, "observed_partial_abs_max": observed,
                               "conservative_bound": conservative_bound, "selected_bound": bound,
                               "range_reduction_factor": conservative_bound / bound,
                               "unexcited_tile_uses_conservative_range": observed == 0})
        self.tiles = calibrated_tiles
        self.range_calibration = {"method": "maximum absolute quantized training partial times fixed headroom, capped at conservative bound",
                                  "headroom": headroom, "vectors": flat.shape[0],
                                  "input_tensor_sha256": observed_input_hash,
                                  "input_tensor_dtype": str(flat.dtype), "input_tensor_shape": list(flat.shape),
                                  "ranges": ranges, "frozen_before_evaluation": True}

    def contract(self):
        result = super().contract()
        result["adc_range"] = deepcopy(self.range_calibration)
        result["required_unqualified_hardware"] = ["per-tile programmable gain or ADC reference", "range switching and settling cost"]
        result["calibration_status"] = "training-activation numerical calibration; no physical converter calibration"
        result["noise_interpretation"] = "read_noise_fraction remains relative to each selected range; this does not preserve a fixed absolute physical noise floor"
        return result
