"""Exploratory differential-array projection; no physical device calibration implied."""

from dataclasses import asdict, dataclass
import hashlib
import math

import torch


@dataclass(frozen=True)
class Profile:
    tile_rows: int = 128
    tile_columns: int = 128
    weight_bits: int = 8
    dac_bits: int = 10
    adc_bits: int = 12
    read_noise_fraction: float = 0.0

    def __post_init__(self):
        if self.tile_rows < 1 or self.tile_columns < 1:
            raise ValueError("tile dimensions must be positive")
        if any(bits < 2 or bits > 16 for bits in (self.weight_bits, self.dac_bits, self.adc_bits)):
            raise ValueError("precision must be between 2 and 16 bits")
        if not math.isfinite(self.read_noise_fraction) or self.read_noise_fraction < 0:
            raise ValueError("noise must be finite and nonnegative")


def quantize(value, bound, bits):
    """Symmetric signed quantization; bound is fixed by calibration/weights."""
    maximum = 2 ** (bits - 1) - 1
    step = torch.as_tensor(bound, device=value.device, dtype=value.dtype).clamp_min(1e-12) / maximum
    return torch.round(value / step).clamp(-maximum, maximum) * step


class TiledProjection:
    def __init__(self, weight, bias, activation_bound, profile, seed=8181, settling_fraction=0.0,
                 charge_fraction=1.0):
        if not math.isfinite(activation_bound) or activation_bound <= 0:
            raise ValueError("a positive calibration activation bound is required")
        if not math.isfinite(settling_fraction) or settling_fraction < 0 or settling_fraction >= 1:
            raise ValueError("settling_fraction must be in [0, 1)")
        if not math.isfinite(charge_fraction) or charge_fraction <= 0 or charge_fraction > 1:
            raise ValueError("charge_fraction must be in (0, 1]")
        self.profile = profile
        self.weight = weight.detach().clone()
        self.bias = bias.detach().clone()
        self.activation_bound = activation_bound
        self.settling_fraction = settling_fraction
        self.charge_fraction = charge_fraction
        self.generator = torch.Generator(device=weight.device).manual_seed(seed)
        self.tiles = []
        for r in range(0, weight.shape[0], profile.tile_rows):
            for c in range(0, weight.shape[1], profile.tile_columns):
                w = self.weight[r:r + profile.tile_rows, c:c + profile.tile_columns]
                qw = quantize(w, w.abs().max(), profile.weight_bits)
                # Worst-case partial dot-product bound, shared by a tile's ADCs.
                # It is deliberately conservative and never fitted on evaluation data.
                adc_bound = float(qw.abs().sum(dim=0).max()) * activation_bound
                self.tiles.append((r, c, qw, max(adc_bound, 1e-12)))
        self.trace = []
        self.output_vectors = []
        self.output_scale = None
        self.output_correction = None
        self.output_quadratic = None
        self.context_threshold = None
        self.context_scale = None
        self.context_correction = None
        self.stateful_previous_scale = None
        self.stateful_previous2_scale = None
        self.input_energy_residual_scale = None
        self.input_energy_residual_center = None
        self.phase = "unspecified"

    def __call__(self, value, ideal=False):
        flat = value.reshape(-1, value.shape[-1])
        clipping = int((flat.abs() > self.activation_bound).sum())
        x = flat if ideal else quantize(flat, self.activation_bound, self.profile.dac_bits)
        output = x.new_zeros((x.shape[0], self.weight.shape[1]))
        adc_clips = 0
        for r, c, qw, bound in self.tiles:
            w = self.weight[r:r + qw.shape[0], c:c + qw.shape[1]] if ideal else qw
            partial = x[:, r:r + w.shape[0]] @ w
            if not ideal:
                if self.profile.read_noise_fraction:
                    partial = partial + torch.randn(partial.shape, generator=self.generator,
                                                    device=partial.device, dtype=partial.dtype) * (bound * self.profile.read_noise_fraction)
                adc_clips += int((partial.abs() > bound).sum())
                partial = quantize(partial, bound, self.profile.adc_bits)
                # Explicit reset -> charge -> settle trajectory. State is
                # deliberately scoped to this projection call/sequence.
                if self.charge_fraction != 1.0:
                    partial = partial * self.charge_fraction
                if self.settling_fraction:
                    previous = torch.zeros_like(partial)
                    if partial.shape[0] > 1:
                        previous[1:] = partial[:-1]
                    partial = ((1.0 - self.settling_fraction) * partial
                               + self.settling_fraction * previous)
            output[:, c:c + w.shape[1]] += partial
        output_flat = (output + self.bias).reshape(flat.shape[0], self.weight.shape[1])
        if self.stateful_previous_scale is not None:
            previous = torch.zeros_like(output_flat)
            if output_flat.shape[0] > 1:
                previous[1:] = output_flat[:-1]
            history = previous * self.stateful_previous_scale.to(output_flat.device, output_flat.dtype)
            if self.stateful_previous2_scale is not None:
                previous2 = torch.zeros_like(output_flat)
                if output_flat.shape[0] > 2:
                    previous2[2:] = output_flat[:-2]
                history = history + previous2 * self.stateful_previous2_scale.to(output_flat.device, output_flat.dtype)
            output_flat = (output_flat * self.output_scale.to(output_flat.device, output_flat.dtype)
                           + self.output_correction.to(output_flat.device, output_flat.dtype) + history)
        if self.context_threshold is not None:
            high = output_flat.norm(dim=1) >= self.context_threshold
            context_output = output_flat.clone()
            for mask, index in ((~high, 0), (high, 1)):
                if bool(mask.any()):
                    context_output[mask] = (output_flat[mask] * self.context_scale[index].to(output_flat.device, output_flat.dtype)
                                            + self.context_correction[index].to(output_flat.device, output_flat.dtype))
            output_flat = context_output
        if self.output_scale is not None:
            output_flat = output_flat * self.output_scale.to(output_flat.device, output_flat.dtype)
        if self.output_correction is not None:
            output_flat = output_flat + self.output_correction.to(output_flat.device, output_flat.dtype)
        if self.output_quadratic is not None:
            output_flat = output_flat + self.output_quadratic.to(output_flat.device, output_flat.dtype) * output_flat.square()
        if self.input_energy_residual_scale is not None:
            energy = flat.norm(dim=1, keepdim=True)
            output_flat = output_flat + (energy - self.input_energy_residual_center) * self.input_energy_residual_scale.to(output_flat.device, output_flat.dtype)
        self.output_vectors.append(output_flat.detach().cpu().numpy().copy())
        vector_fingerprints = []
        for row in output_flat.detach().cpu().contiguous().numpy():
            vector_fingerprints.append({
                "sha256": hashlib.sha256(row.tobytes()).hexdigest(),
                "l2_norm": float(torch.linalg.vector_norm(torch.from_numpy(row))),
                "max_abs": float(torch.from_numpy(row).abs().max()),
            })
        self.trace.append({"phase": self.phase, "vectors": flat.shape[0],
                           "input_values": flat.numel(), "dac_clipped_values": clipping if not ideal else 0,
                           "adc_clipped_values": adc_clips, "mode": "ideal_tiled" if ideal else "assumed_array",
                           "output_vector_fingerprints": vector_fingerprints,
                           "output_fingerprint_scope": "projection output tensor row; software replay only"})
        return output_flat.reshape(*value.shape[:-1], self.weight.shape[1])

    def contract(self):
        inputs, outputs = self.weight.shape
        row_tiles = math.ceil(inputs / self.profile.tile_rows)
        column_tiles = math.ceil(outputs / self.profile.tile_columns)
        return {
            "profile": asdict(self.profile), "weight_shape_input_output": [inputs, outputs],
            "calibrated_activation_abs_max": self.activation_bound,
            "readout_settling_fraction": self.settling_fraction,
            "readout_charge_fraction": self.charge_fraction,
            "logical_tiles": len(self.tiles), "physical_arrays_if_differential_pair": 2 * len(self.tiles),
            "signed_weight_representation": "differential pair; effective multilevel weight precision is assumed, not demonstrated",
            "input_representation": "signed DAC voltage assumed; no input bit serialization",
            "readout": "analog differential subtraction before one signed ADC per logical column",
            "adc_range": "activation bound times maximum column L1 weight norm within each tile",
            "accumulation": "digital float32 sum across row tiles and digital bias addition",
            "per_vector": {
                "macs": inputs * outputs,
                "dac_conversions_without_column_tile_broadcast": inputs * column_tiles,
                "adc_conversions_after_differential_subtraction": outputs * row_tiles,
                "array_evaluations": 2 * len(self.tiles),
                "digital_partial_sum_additions": outputs * (row_tiles - 1),
                "boundary_input_bytes_fp32": inputs * 4,
                "boundary_output_bytes_fp32": outputs * 4,
            },
            "excluded_physics": ["wire resistance", "conductance programming error", "drift", "nonlinear I/V",
                                 "PVT", "mismatch", "settling", "sample/hold", "SRAM contention"],
            "calibration_status": "activation-calibrated numerical model; not circuit-calibrated",
            "energy_latency": {"status": "not_identifiable_without_matched_cost_coefficients",
                               "required": ["DAC pJ/conversion", "ADC pJ/conversion", "array pJ/evaluation",
                                            "digital accumulation pJ/add", "boundary transfer pJ/byte",
                                            "converter sharing schedule and settling", "same-target digital projection cost"],
                               "energy_equation": "E_projection = N_DAC*e_DAC + N_ADC*e_ADC + N_array*e_array + N_add*e_add + bytes*e_move; add programming/calibration amortization",
                               "break_even": "E_projection plus integration overhead must be below same-target digital projection energy"},
        }
