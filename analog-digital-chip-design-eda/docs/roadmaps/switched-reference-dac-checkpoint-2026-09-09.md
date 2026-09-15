# Nominal switched-reference DAC and GPT-2 range binding

The reference-setting mechanism now has transistor-model simulation evidence
and a frozen mapping to all 144 GPT-2 projection tiles. This is a component
experiment and a proposed numerical profile, not analog inference execution.
The physical converter gate and digital fallback decision are unchanged.

## Circuit comparison

All three packages use a 32-transistor, 8-bit R-2R reference DAC with SKY130 TT
switch models at 27°C, 1.8 V supply and an ideal 1.2 V reference source.
Resistors, voltage sources and complementary gate drivers are ideal; loads
are experimental assumptions. These values do not assign the still
unresolved array conductance, row drive or transimpedance.

Packages are under `evidence/aimc-simulator-adapters/switched-reference-dac/`.

| Package | R | NFET/PFET widths | Both DC curves monotonic | Maximum reference-source static power, 1 TΩ load | Transients settled within observation |
| --- | --- | --- | --- | --- | --- |
| `20260909-full-v1` | 10 kΩ | 4/8 µm | No | 140.44 µW | 9/9 |
| `20260909-r100k` | 100 kΩ | 4/8 µm | Yes | 14.36 µW | 6/9 |
| `20260909-wide-switch` | 10 kΩ | 32/64 µm | Yes | 143.52 µW | 9/9 |

Lengths are 0.15 µm. DC characterization covers all 256 codes at 1 TΩ and
1 MΩ loads. The baseline's 127→128 step decreases output by 7.228 mV at 1 TΩ.
Its settling results do not repair its nonmonotonic transfer curve.

Transient probes are 26→255, 255→26 and 127→128 at 10 fF, 100 fF and 1 pF,
with a 1 TΩ resistive load. The transition begins at 20 ns, edges last 100 ps,
and observation ends at 220 ns. The sampled settling tolerance is target
reference voltage / 4094. The wider-switch candidate's slowest observed case
settles 104.99 ns after the edge. All three 100 kΩ cases at 1 pF remain outside
tolerance at the observation endpoint; longer-time settling was not tested.

Reference-source static power is only `-VREF * I(VREF)` at DC. It excludes
driver energy, transient reference current, ADC/array power and other supplies.
It cannot establish inference energy or compare whole-system efficiency.

## Frozen numerical profile

Use `evidence/aimc-hardware-lab/switched-reference-ranges/20260909-v1/`.
The wider-switch candidate is selected for further study because its sampled
DC curves are monotonic and all nine probe cases settle. This is not a proven
optimum or physical qualification.

The binding uses the 1 TΩ nominal DC curve normalized to its own code-255
output. Each tile receives the nearest nonzero reference code, with the lower
code breaking a tie. Codes span 26–255. The largest absolute relative range
change is **1.51591%**. At fixed physical gain:

```text
effective_ADC_bound = frozen_ADC_bound * simulated_reference_fraction / target_reference_fraction
```

Both ADC clipping/quantization and digital dequantization must use the effective
bound. Keeping the old digital scale would introduce an additional gain error.
Validation evaluation has now passed for these changed bounds (see below).
The earlier noiseless held-out pass belongs to the original frozen profile;
the finite-reference profile still needs its own held-out evaluation.

The mapping imports the checked controller's actual eight-bank, eighteen-wave
order. Including last-wave to next-vector first-wave reuse gives 144 distinct
code transitions. None matches the three existing transient probes. Startup
state, sequence timing, actual ADC reference loading and readiness delays are
unqualified. A transition table is not an executed controller or settling proof.

## Verification and next execution

All three complete DAC packages passed the raw-log/waveform checker: each has
47 artifact hashes, 512 DC samples and nine transient waveforms; local PDK
source hashes are also checked. Binding generation reverified all 2,359,296
weight codes, 144 normalized scales and controller source manifest. The binding
checker verifies all 144 code choices, effective scales and cyclic transitions.
Four mutation checks rejected stale dequantization, a missing vector-wrap
transition, a false quality pass and false transient coverage.

```bash
python3 scripts/check_switched_reference_ranges.py evidence/aimc-hardware-lab/switched-reference-ranges/20260909-v1
```

Next, evaluate the frozen effective bounds on validation contexts and simulate
the actual bank reference sequences under declared load/timing assumptions.
Any revised profile needs separate held-out evaluation. Array/device behavior,
full converter electrical qualification, extracted layout/PVT/mismatch,
physical target execution and matched end-to-end latency/energy remain open.

## Sequence experiment started

`scripts/run_reference_bank_sequences.py` now drives each bank through two
consecutive vectors, including vector-wrap transitions. The immutable run is
`evidence/aimc-simulator-adapters/reference-bank-sequences/20260909-v1/`.
It requests 24 bank/load simulations: eight banks at 10 fF, 100 fF and 1 pF,
with 36 transitions per simulation (864 observations). Command spacing is an
assumed 150 ns, gate edges 100 ps, and maximum transient step 50 ps. Initial
state is a DC operating point at the previous vector's last reference code;
power-up and actual ADC loads remain excluded.

At the initial checkpoint the process was still running. The first bank at 10 fF
finished with 36/36 sampled transitions settling before the next command;
the largest recorded delay was 0.811 ns. This partial result is not a complete
sequence pass. Each completed case saves raw waveforms and measurements; only
normal completion writes the top-level result and manifest. Four measurement
regressions pass, covering late glitches, persistent error, next-edge exclusion
and complementary gate stimulus across repeated vectors.

That first invocation subsequently exited with code 1: bank 5 at 100 fF hit
the 180-second subprocess timeout after 13 cases completed. Its process was
confirmed terminal before recovery. It remains an incomplete historical
package, not a full sequence pass.

The active recovery package is
`evidence/aimc-simulator-adapters/reference-bank-sequences/20260909-v2/`, created
by `scripts/resume_reference_bank_sequences.py`. It rechecked and copied the
13 completed waveforms and measurements, records hashes of the original run,
preserves the timed-out deck/logs under `failed-attempts/`, and runs only the
11 unfinished cases with a 600-second per-case allowance. Circuit settings,
stimulus, timestep and settling tolerance are unchanged. Execution session
24233 is the current recovery handle; revalidate it before waiting or resuming.
After completion run:

```bash
python3 scripts/check_reference_bank_sequences.py evidence/aimc-simulator-adapters/reference-bank-sequences/20260909-v2
```

The sibling software project has completed
`experiments/gpt2-hybrid-v1/runs/20260909-finite-reference-validation/`, comparing
the original and finite-reference ADC bounds on the existing sixteen validation
contexts. The finite-reference profile passed with 99.3652% baseline argmax
agreement and +0.000793248 nats/token loss across 2,048 predictions; there were
27 ADC clips and no DAC clips. All controls, 48-row verification and six
mutation rejection checks passed. The original-profile control exactly
reproduced the prior validation per-context losses and agreement counts.
See its `finite-reference-validation.md`. This does not reuse test contexts
or promote the original profile's held-out pass to the changed profile.

The separate finite-reference holdout has now also completed and verified:
99.4385% baseline argmax agreement and +0.000603370 nats/token across 4,096
predictions in 32 contexts disjoint from all 64 previously scored contexts.
There were 61 ADC clips and no DAC clips. Numerical controls, exact fallback,
96-row/144-bound verification and six result rejection checks passed. This
closes the sampled static-reference quality screen, not physical execution.
