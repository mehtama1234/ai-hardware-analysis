# Calibrated range controller contract

The quality-tested GPT-2 profile now has an exact descriptor table and checked
controller ordering model. The compiler rejects calibrated analog lowering
because its review ISA cannot configure ranges or await readiness. The generated
package uses digital fallback.

Use `evidence/aimc-hardware-lab/calibrated-range-controller/20260909-v2/`.
Version v1 predates binding-epoch checks and is superseded. Neither version
performs hardware I/O or implements a physical converter.

## Binding and ordering

All 144 descriptors reproduce the held-out profile's bounds exactly. Each
16-byte little-endian record contains uint16 tile/row/column identifiers,
uint8 ADC width/reserved fields and a float64 bound in model partial-sum units.
The table occupies 2,304 bytes. It is review data, not hardware register codes.

The resource hypothesis retains all 144 logical tiles' weights and shares
eight ADC banks with 16 lanes each. Per input vector, it schedules 18 waves,
eight ADC rounds per wave, 144 range configurations and 18,432 conversions.
The 2,016-event software replay assumes readiness acknowledgements; it does not
measure device signals or time.

```text
select tile + new binding epoch
  -> configure range
  -> matching range-ready acknowledgement
  -> load DAC
  -> matching array-ready acknowledgement
  -> eight ADC read rounds
  -> accumulate
```

Epochs increase across waves and vectors. Old acknowledgements are rejected
even when bank/tile identifiers match. Hardware epoch width, rollover, reset,
flush behavior and timeouts remain undefined requirements.

The compiled digital arena remains 24,576 bytes. A proposed descriptor
reservation after it would bring the total to 26,880 bytes, within the 64 KiB
planning budget. Digital fallback does not load or use that reservation.

## Physical mapping remains open

Under an explicitly assumed linear differential-array model:

```text
I_diff = alpha_tile * beta_DAC * model_partial
R_tile = V_ADC_full_scale / (alpha_tile * beta_DAC * selected_bound)
```

Conductance per weight unit (`alpha_tile`), voltage per input unit (`beta_DAC`),
ADC full-scale voltage and transimpedance gain remain null. Fixed gain with
adjustable ADC reference is another unqualified option. Noise across settings,
switching/settling, sample/hold, mux timing, area and energy also remain unknown.
Values from the failed comparator experiment are not assigned to this mapping.

## Verification

Seven unit tests passed: descriptor round-trip/coverage, readiness ordering,
stale acknowledgements, duplicate/incomplete reads, invalid tables and compiler
rejection. A full-compiler negative check rejected calibrated analog lowering
before command emission. Legacy review lowering remained functional. The actual
digital fallback package passed the existing bytecode reference interpreter.

All 20 artifact hashes, 144 exact range bindings and the 2,016-event replay
verified. The compiler emits one `RUN_DIGITAL_SUPPORT` command and zero range
register writes. Its planning cycles are not measured timing.

From the EDA project, use a new directory:

```bash
python3 scripts/check_calibrated_adc_controller_contract.py
python3 scripts/build_calibrated_adc_controller_contract.py --quality ../analog-in-memory-ai-inference/software-architecture/experiments/gpt2-hybrid-v1/runs/20260909-calibrated-adc12-holdout --output evidence/aimc-hardware-lab/calibrated-range-controller/new-run
```

Next work must supply the physical mapping and implement a target-bound
configuration/readiness interface. This contract does not authorize analog
execution or complete the full inference goal.

The [model-derived scaling follow-up](normalized-array-scaling-2026-09-09.md)
now binds actual weight/DAC codes to all 144 descriptors. Under its explicit
linear-array assumptions, it derives a 9.6758:1 relative gain span or reference
fractions from 0.103351 to 1. Absolute physical values and setting precision
remain unqualified; the compiler's rejection still applies.
