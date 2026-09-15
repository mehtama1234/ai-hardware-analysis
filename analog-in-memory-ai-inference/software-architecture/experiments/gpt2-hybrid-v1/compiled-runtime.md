# GPT-2 shared compiler and SRAM execution

The first GPT-2 MLP projection now uses the same review compiler, command
encoding and SRAM allocation format as the existing Optdigits/transformer
workloads. All other GPT-2 modules execute through native PyTorch. The generated
instruction is `RUN_DIGITAL_SUPPORT`; a software interpreter decodes it and
executes the projection from SRAM-resident inputs, writes the output to the
allocated partial-sum buffer, and returns that output to the real model.

The arena is 24,576 bytes, within the existing 64 KiB contract. A vector is
loaded and executed at a time so prefill does not silently expand SRAM
capacity. Weights remain in host memory. This is observed software execution
of the shared review encoding, not firmware or physical chip execution.

## Runtime and evidence gates

The runtime checks artifact hashes, command/image identity, opcode, operator
index, SRAM offsets, bounds and overlap, and CPU float32 input dimensions.
Malformed commands fail before execution. An optimistic physical-evidence flag
cannot enable analog instructions when there is no bound analog executor.
Current fallback reasons include the missing array target, unavailable analog
executor, blocked converter gate and unverified final-netlist preamp path.

The final package is under the sibling EDA project's
`evidence/aimc-hardware-lab/gpt2-compiled-runtime/20260909-shared-sram-frozen/`.
It includes source snapshots, plan, shared compiler outputs, physical gate,
observed execution trace, model-quality comparison, and manifest. The initial
`20260909-shared-sram` run is superseded for source attribution because the
physical importer was updated during that run; use the frozen package.

## Candidate hardware schedule

The same sensitivity profile has a separate, explicitly assumed resource
schedule: 144 logical tiles, eight active logical tiles per wave, 16 ADC lanes
per tile, 18 waves per input vector, and eight ADC rounds per wave. Each wave
loads/drives its inputs, waits for settling, performs sampled readout rounds,
and digitally accumulates the partial outputs. All 144 tiles appear exactly
once per vector. Analog differential subtraction and sample/hold remain
unqualified hardware assumptions.

The schedule leaves physical durations unresolved. It records the equation
and per-vector conversion/array/accumulation/transfer counts, then applies
those counts to the observed digital token trace by phase. These are
counterfactual hardware counts, not operations performed by the CPU fallback.
Changing generation, batching, or EOS behavior requires a new trace. The
compiler's three planning cycles per command are not hardware timing.

## Reproduce

From `software-architecture`, with the pinned GPT-2 model cached:

```bash
HF_HUB_OFFLINE=1 python3 scripts/run_gpt2_compiled_runtime.py --output ../../analog-digital-chip-design-eda/evidence/aimc-hardware-lab/gpt2-compiled-runtime/new-run
python3 scripts/check_gpt2_compiled_package.py --package ../../analog-digital-chip-design-eda/evidence/aimc-hardware-lab/gpt2-compiled-runtime/new-run
python3 scripts/check_gpt2_compiled_runtime.py
python3 scripts/check_physical_evidence_selection.py
```

## Circuit diagnosis

The controlled comparison is saved in EDA
`evidence/aimc-simulator-adapters/recovery-20260909/preamp-reconnection-comparison.json`.
At 100 kΩ load, 1.8 V supply, 0.9 V common mode and ±100 mV differential:

| View | Decision at −100 mV | Decision at +100 mV | Both pass 0.9 V swing? |
| --- | ---: | ---: | --- |
| Unchanged extracted circuit | +0.033127 V | −0.038543 V | No |
| Hypothetical four-node reconnection | +0.286807 V | −0.799945 V | No |

The reconnection improves swing but is not a layout repair or qualified
converter. These results use a different load from the earlier 1 MΩ failure;
they must not be compared as if only connectivity changed across all runs.
The physical importer excludes the hypothetical view from latest extracted
evidence. The next circuit step is to repair actual geometry, re-extract, then
address gain/loading and test both polarities and the full conversion path.
