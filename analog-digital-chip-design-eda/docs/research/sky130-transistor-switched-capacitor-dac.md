# Sky130 Transistor-Switched Capacitor DAC

This page is the next physical boundary after the ideal-switch capacitor DAC. It uses Sky130 NMOS/PMOS devices for the sample path and bottom-plate redistribution switches, then measures the same binary code thresholds and settling error.

## Reproduce

```bash
python3 scripts/run_sky130_transistor_switched_capacitor_dac.py
```

For a long current-state campaign, use the explicit timing contract and a
checkpoint directory. Completed code receipts are written immediately and
matching checkpoints are reused on a resume:

```bash
AIMC_TRANSISTOR_DAC_CODES=0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15 \
AIMC_TRANSISTOR_DAC_DECISION_NS=7.9 AIMC_TRANSISTOR_DAC_TRAN_NS=8 \
AIMC_TRANSISTOR_DAC_STEP_PS=20 \
AIMC_TRANSISTOR_DAC_CHECKPOINT_DIR=/tmp/sky130-fourbit-checkpoints \
python3 scripts/run_sky130_transistor_switched_capacitor_dac.py
```

The checkpoint artifacts are per-code diagnostics. They do not turn a
coarse-step or resumed campaign into same-resolution acceptance evidence.

The physical handoff screen is opt-in and fail-closed by design. The
reproducible baseline is:

```bash
AIMC_TRANSISTOR_DAC_TRANSISTOR_HANDOFF=1 \
AIMC_TRANSISTOR_DAC_TRANSISTOR_HANDOFF_NS=3 \
AIMC_TRANSISTOR_DAC_TRANSISTOR_HANDOFF_DEAD_NS=0.25 \
AIMC_TRANSISTOR_DAC_DECISION_NS=7.9 AIMC_TRANSISTOR_DAC_TRAN_NS=8 \
AIMC_TRANSISTOR_DAC_STEP_PS=50 \
python3 scripts/run_sky130_transistor_switched_capacitor_dac.py
```

Additional active-hold, PMOS/NMOS bank, gate-slew, re-clamp, keeper, and
isolated-rail modes are diagnostic controls only. Every receipt reports its
control parameters, measured-code coverage, top-plate error, and bottom-plate
legality; a converged subset is not a converter qualification.

The machine-readable result is `evidence/aimc-simulator-adapters/sky130-transistor-switched-capacitor-dac.json`.

The first switch-sizing and timing diagnostic improves the worst measured error to about `143 mV` with wider devices and a `70 ns` redistribution read point. After fixing a repeating-pulse control bug, all sixteen codes complete and their measured order is monotonic. Codes `8` through `11`, `14`, and `15` exceed the `56.25 mV` half-LSB target; the worst error is about `206.9 mV`, so the DAC is not accepted for the SAR loop.

## Boundary

This is transistor-switched DAC evidence. It does not prove capacitor mismatch statistics, reference loading across a full SAR, comparator coupling, extracted layout, board behavior, or silicon.
