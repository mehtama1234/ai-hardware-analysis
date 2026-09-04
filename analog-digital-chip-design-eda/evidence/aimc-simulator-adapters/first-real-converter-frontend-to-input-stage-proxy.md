# First Real Converter Frontend To Input-Stage Proxy

- status: `frontend_to_input_stage_proxy_timed_out_not_strict_evidence`
- candidate id: `aimc_readout_candidate_001`
- run id: `aimc_readout_candidate_001_frontend_to_input_stage_proxy_run001`
- source frontend evidence: `evidence/aimc-simulator-adapters/sky130-ultra-sense-frontend-candidate.json`
- source frontend candidate: `sky130_ultra_sense_capacitive_frontend`
- generated deck: `labs/analog/analog-in-memory-foundation-model-hardware/spice/first_real_converter_frontend_to_input_stage_proxy.sp`
- case count: `4`
- polarity pass count: `0`
- timed-out case count: `4`
- minimum frontend sense diff V: `0.000000000e+00`
- minimum active-stage input diff V: `0.000000000e+00`
- active-stage input floor V: `1.000000000e-04`
- floor case count: `4`
- minimum output diff V: `0.000000000e+00`
- minimum stage gain V/V: `0.000000`
- minimum overall sample-to-output gain V/V: `0.000000`
- same-run strict payload ready: `False`
- accepted post-layout written: `False`
- csv: `labs/analog/analog-in-memory-foundation-model-hardware/measurements/first-real-converter-frontend-to-input-stage-proxy.csv`

## First Principle

The passive frontend creates a very small voltage difference. That difference is not useful by itself unless the next circuit can turn it into a larger, correctly signed electrical state.

This run takes the measured sense-node sign from the extracted ultra frontend and feeds a bounded small input difference into a Sky130 transistor differential pair. The raw frontend difference is only about 67 microvolts, so the deck uses a 100 microvolt floor to keep the active-stage operating-point solve in a practical range. The input pair spends current to make a larger output difference. In simple terms: the passive block preserves the sign, and the active block pays power to make that sign easier for a latch to decide.

This is a bridge, not an accepted converter. The frontend and input pair are not yet one extracted layout netlist. The pair is not a clocked latch. There is no SAR loop, no code transition, no noise or mismatch simulation, and no signed physical area for the whole converter.

## Result

| reset mode | original sample diff mV | frontend sense diff uV | active input diff uV | input-stage output diff mV | stage gain V/V | overall gain V/V | polarity correct |
|---|---:|---:|---:|---:|---:|---:|---|
| `quiet_vcm` | `-0.153000` | `-67.000000` | `-100.000000` | `timeout` | `timeout` | `timeout` | `False` |
| `quiet_vcm` | `0.153000` | `67.000000` | `100.000000` | `timeout` | `timeout` | `timeout` | `False` |
| `reset_pulse` | `-0.153000` | `-67.000000` | `-100.000000` | `timeout` | `timeout` | `timeout` | `False` |
| `reset_pulse` | `0.153000` | `67.000000` | `100.000000` | `timeout` | `timeout` | `timeout` | `False` |

## Strict Blockers

- The frontend sense values and active input stage are connected by a scripted proxy, not one extracted post-layout netlist containing both blocks.
- The measured frontend sense difference is below the practical active-stage deck floor used here, so this run proves sign handoff at a bounded proxy input rather than direct acceptance of the raw frontend output.
- The active stage is a differential-pair polarity and gain proxy, not a clocked comparator with metastability, kickback, offset, or noise evidence.
- The run does not include DAC switching, SAR bit cycling, full supply-current integration, DRC/LVS area, or a same-run break-even payload.

## Refused Claim

does not prove a full comparator, full converter, same-run extracted post-layout package, or accepted replacement evidence
