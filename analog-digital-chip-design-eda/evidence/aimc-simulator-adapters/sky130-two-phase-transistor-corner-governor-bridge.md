# Sky130 Two-Phase Transistor Corner Governor Bridge

This report feeds measured transistor corner amplitude into the existing digital governor.

- measured cases: `54`
- analog-service decisions: `39`
- digital-fallback decisions: `15`
- preamp margin target: `0.0005 V`

## First-Principles Reading

A comparator sign can remain correct while its differential signal becomes too small for noise, offset, kickback, and latch uncertainty. The governor therefore treats the measured preamp amplitude as an eligibility condition.

The nominal and fast/high-supply rows remain eligible in this fixture. The slow/cold/low-supply rows fall back to digital because their measured amplitude is below the handoff target. This is a control decision backed by a circuit measurement, not a claim that the circuit works across PVT.

## Refused Claim

does not prove a transistor SAR, random mismatch/noise yield, extracted layout, board behavior, or silicon
