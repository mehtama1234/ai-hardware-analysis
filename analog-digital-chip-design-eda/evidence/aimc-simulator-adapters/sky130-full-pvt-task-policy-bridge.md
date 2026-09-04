# Sky130 Full PVT And Task Policy Bridge

This page joins two gates that must both pass before an analog projection is allowed to serve the model: physical converter eligibility and model-quality evidence.

- PVT policy cases: `54`
- analog-allowed cases: `39`
- digital-fallback cases: `15`
- CrossSim model gate: `True`
- CrossSim surrogate error: `6.716349688914575e-08`

## First-Principles Reading

A model-level simulator pass cannot rescue a converter that loses amplitude or fails to converge at a physical corner. Conversely, a circuit that produces a large signal is not enough if the mapped model operation exceeds its error budget. The service decision is the intersection of both gates.

In this run the CrossSim calibrated deep MLP surrogate passes, so the remaining exclusions come from the physical matrix: low preamp amplitude or a non-convergent transient forces digital fallback. This is a policy bridge, not a claim that task accuracy was remeasured at each PVT point.

## Refused Claim

does not prove task quality at every physical corner, random noise or mismatch yield, SAR conversion, extracted layout, board behavior, or silicon
