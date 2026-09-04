# Analog Tile Error Evidence

This measurement turns an analog tile into the evidence packet consumed by the digital governor. The object is a dot product. The useful question is whether the measured dot product is still safe enough to become transformer state.

The model includes conductance programming error, drift, DAC quantization, ADC quantization, SPICE-measured row-voltage drop, calibration age, and path sensitivity. Those are not separate stories. They meet at the governor inputs:

```text
residual_q8: how much analog output error remains
drift_age: how long the tile has run since calibration
sensitivity_q8: how much this model path amplifies numeric error
analog_candidate: whether the tile should even be offered to the scheduler/governor
```

## Summary

- scenarios: 8
- offered as analog candidates: 8
- not offered as analog candidates: 0

## Evidence Table

| scenario | ADC | DAC | program sigma % | drift % | row case ohm | SPICE current loss % | far-row scale | age | residual q8 | sensitivity q8 | candidate | meaning |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| fresh_tile_low_sensitivity | 7 | 7 | 1.00 | 0.00 | 25 | 1.84 | 0.982 | 1 | 6 | 89 | 1 | governor should admit this tile evidence |
| fresh_tile_high_sensitivity | 7 | 7 | 1.00 | 0.00 | 25 | 1.84 | 0.982 | 1 | 6 | 209 | 1 | governor should admit this tile evidence |
| six_bit_normal_tile | 6 | 6 | 2.00 | 1.00 | 100 | 6.93 | 0.931 | 4 | 12 | 140 | 1 | governor should admit this tile evidence |
| wire_drop_stressed_tile | 6 | 6 | 2.00 | 1.00 | 500 | 26.63 | 0.734 | 5 | 12 | 140 | 1 | governor should admit this tile evidence |
| drifted_tile | 6 | 6 | 2.00 | 6.00 | 100 | 6.93 | 0.931 | 10 | 12 | 140 | 1 | governor should admit this tile evidence |
| stale_calibration_tile | 6 | 6 | 2.00 | 2.50 | 100 | 6.93 | 0.931 | 13 | 12 | 140 | 1 | governor should recalibrate because calibration age is above the hard stop |
| programming_error_tile | 6 | 6 | 7.00 | 2.00 | 100 | 6.93 | 0.931 | 6 | 12 | 140 | 1 | governor should admit this tile evidence |
| low_precision_tile | 4 | 4 | 2.00 | 1.00 | 100 | 6.93 | 0.931 | 4 | 49 | 140 | 1 | governor should refuse because residual is above the hard stop |

## First-Principles Reading

An analog array does not produce a model value. It produces a physical measurement. The measurement becomes useful only after the digital side asks how far it may be from the ideal dot product, how old the calibration is, and how dangerous that error is for the current model path.

Residual is the local miss: the difference between the ideal dot product and the measured tile output after converter and array effects. Row-drop now enters from the SPICE row-wire experiment: the script takes the measured current loss for a stated segment resistance and uses it to reduce the effective activation seen by farther cells. Drift age is the time dimension of the miss: even if the last measurement was good, the stored conductance may have moved. Sensitivity is the model dimension: the same numeric error can be harmless in one projection and dangerous near a selection boundary.

The governor exists because these three facts must be joined. A fresh low-sensitivity tile can be admitted. A stale tile should recalibrate even if its current residual is moderate. A high-sensitivity path can require digital fallback at residual levels that would be acceptable elsewhere. This is the concrete analog-to-digital bridge: physics becomes residual, residual becomes a budget entry, and the budget decides whether analog compute is allowed for this token.
