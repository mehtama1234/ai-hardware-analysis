#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass


MAX_CALIBRATION_AGE = 1024


@dataclass(frozen=True)
class ReadoutCase:
    name: str
    tile_enabled: bool
    adc_code: int
    zero_code: int
    gain_q6: int
    bias: int
    residual_abs: int
    residual_budget: int
    calibration_age: int


def clamp_signed_12(value: int) -> tuple[int, str | None]:
    if value > 2047:
        return 2047, "saturated_high"
    if value < -2048:
        return -2048, "saturated_low"
    return value, None


def readout(case: ReadoutCase) -> dict[str, int | str]:
    centered = case.adc_code - case.zero_code
    scaled = (centered * case.gain_q6) >> 6
    corrected, saturation = clamp_signed_12(scaled + case.bias)

    reason = "ok"
    valid = 1
    fallback = 0

    if saturation is not None:
        reason = saturation
    elif not case.tile_enabled:
        reason = "tile_disabled"
    elif case.residual_abs > case.residual_budget:
        reason = "residual_high"
    elif case.calibration_age >= MAX_CALIBRATION_AGE:
        reason = "calibration_stale"

    if reason != "ok":
        valid = 0
        fallback = 1

    return {
        "centered_adc": centered,
        "scaled": scaled,
        "corrected": corrected,
        "valid": valid,
        "fallback": fallback,
        "reason": reason,
    }


def main() -> None:
    cases = [
        ReadoutCase("centered_adc_with_unit_gain", True, 160, 128, 64, 0, 3, 20, 32),
        ReadoutCase("gain_and_bias_correction", True, 160, 128, 96, -5, 3, 20, 32),
        ReadoutCase("disabled_tile_fallback", False, 160, 128, 64, 0, 3, 20, 32),
        ReadoutCase("residual_fallback", True, 160, 128, 64, 0, 40, 20, 32),
        ReadoutCase("stale_calibration_fallback", True, 160, 128, 64, 0, 3, 20, 2048),
        ReadoutCase("high_saturation_fallback", True, 4095, 0, 64, 0, 3, 20, 32),
        ReadoutCase("low_saturation_fallback", True, 0, 255, 64, -2000, 3, 20, 32),
    ]

    print("tile_readout_boundary")
    print("case,centered_adc,scaled,corrected,valid,fallback,reason")
    for case in cases:
        result = readout(case)
        print(
            f"{case.name},{result['centered_adc']},{result['scaled']},"
            f"{result['corrected']},{result['valid']},{result['fallback']},{result['reason']}"
        )

    print()
    print("interpretation")
    print("An ADC code is not yet a model value.")
    print("The digital side must remove zero, apply gain and bias, clamp unsafe values, and reject stale or high-residual tile outputs.")


if __name__ == "__main__":
    main()
