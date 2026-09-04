# Sky130 Two-Phase Offset And Noise Sweep

This page summarizes the bounded wrong-code proxy around the passing two-phase preamp-then-latch schematic. The machine-readable source is `evidence/aimc-simulator-adapters/sky130-two-phase-offset-noise-sweep.json`.

## Result

- 80 offset, noise, and kickback combinations were evaluated.
- All 80 passed the wrong-code proxy.
- The measured pre-latch signal was `0.7469 mV`.
- The measured kickback was `19.9 uV`.
- The worst tested case used `200 uV` offset, `100 uV RMS` noise at three sigma, and `5x` measured kickback.
- The worst remaining margin was `147.4 uV`.

## First-Principles Reading

The latch only sees the remaining distance to its decision boundary. The proxy therefore subtracts absolute offset, three standard deviations of the supplied noise assumption, and the tested kickback from the measured pre-latch signal. This is the right shape of the budget, because each error can move the decision toward the wrong code.

The result says the measured schematic has useful margin under this bounded assumption. It does not say that the transistor circuit has `100 uV RMS` noise, `200 uV` offset, or stable mismatch. Those values must be measured or simulated from a defined transistor population and process/temperature/voltage corners.

## Next Gate

Run a real offset and noise experiment on the same two-phase circuit, then add SAR threshold cycling. The accepted record must retain the same polarity contract, both input signs, conversion timing, and the extracted physical boundary.

## Refused Claim

This proxy does not prove transistor noise, offset distributions, mismatch, SAR bit cycling, extracted parasitics, or accepted converter evidence.
