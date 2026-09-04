# Sky130 Transistor DAC PVT Calibration Policy

This is the controller-facing answer to a practical question: can measured DAC codes be corrected well enough to let the analog SAR use them at a given operating point?

## Rule

A corner may request analog SAR service only when codes 0, 8, and 15 are measured, every measured code is within half an LSB, and an endpoint gain/offset correction leaves code 8 within half an LSB. Otherwise the controller must use digital fallback or keep the analog path in bring-up mode.

## Results

| corner | measured | endpoint-corrected code 8 error | decision | reason |
| --- | ---: | ---: | --- | --- |
| ff_85c_1p98v | 2 | missing | digital_fallback | required_calibration_code_missing, measured_code_outside_half_lsb, corner_timeout_or_incomplete |
| ss_minus20c_1p62v | 3 | 3.682 LSB | digital_fallback | endpoint_calibration_does_not_fix_midscale, measured_code_outside_half_lsb |
| tt_25c_1p80v | 3 | 3.438 LSB | digital_fallback | endpoint_calibration_does_not_fix_midscale, measured_code_outside_half_lsb |

## Interpretation

The nominal and slow corners have enough measurements to test endpoint correction, but the midscale residual remains several half-LSBs. This means the DAC is not behaving like a simple shifted and scaled ideal DAC; the switch resistance, charge injection, capacitor ratios, settling, and operating point interact. A two-point calibration would hide the internal shape error rather than remove it.

The fast/hot/high-supply corner also has a timeout at code 0. A timeout is a functional failure for a converter policy, even if other codes complete. The current safe policy is therefore digital fallback for all representative corners.

## Next Measurement

Measure all 16 codes repeatedly at every corner, then add capacitor mismatch, switch mismatch, comparator noise, reference loading, and SAR closed-loop conversions. Only a calibration model that passes those distributions should be allowed to replace this fallback decision.

This policy is evidence about the boundary and its control response. It is not silicon, board, or tapeout evidence.
