# Sky130 Two-Phase Offset And Noise Sweep

- status: `wrong_code_proxy_swept_not_circuit_noise_proof`
- measured pre-latch signal V: `7.469000000e-04`
- measured kickback V: `1.990000000e-05`
- half-LSB V: `2.197265625e-04`
- cases: `80`
- wrong-code proxy passing cases: `80`
- pass fraction: `1.000`
- worst remaining margin V: `1.474000000e-04`

## First-Principles Reading

The latch does not know whether an error came from offset, random noise, or clock kickback. It only sees the remaining distance between the intended differential signal and the decision boundary. This sweep subtracts the absolute offset, three standard deviations of a supplied noise assumption, and the measured kickback multiplier from the measured pre-latch signal.

This is a wrong-code proxy. It is useful for sizing the next experiment, but it is not a measurement of offset or noise.

## Worst Case

- offset: `2.000000000e-04` V
- noise RMS: `1.000000000e-04` V
- kickback multiplier: `5.000`
- remaining margin: `1.474000000e-04` V

## Refused Claim

does not measure transistor noise, offset distributions, mismatch, SAR bit cycling, extracted parasitics, or accepted converter evidence
