# Converter Post-Layout Real Run Recipe

This page is the practical run order for turning the candidate converter folder into a real post-layout evidence package.

It does not supply evidence. It says what a real run must produce, where each object goes, and which command is allowed to judge the package.

## First Principle

A converter result is not a single number. It is a chain.

The layout creates one physical converter. Extraction turns that layout into a circuit file with the extra resistance and capacitance added by geometry. The simulator or silicon setup applies one voltage, one temperature, one corner or measured condition, and one command or lab procedure to that extracted object. The measurement step records energy, latency, noise, and area from that same object. The break-even step asks whether those values are good enough to replace the digital fallback assumption.

If any link comes from a different run, the package is not one claim. It is a mix of unrelated facts. That is why the payload uses one shared `run_id` across provenance, simulation, energy, latency, noise, area, and break-even rerun.

## Run Order

1. Create or choose one converter layout for the 10-bit DAC input and 12-bit ADC readout target.

2. Extract the post-layout circuit.

   The output must be an inspectable file, such as extracted SPICE, DSPF, or SPEF plus the files needed to read it. Put the primary file under `evidence/aimc-simulator-adapters/candidate-post-layout/netlist/`.

3. Collect the model or measurement setup files.

   For post-layout simulation, this means the model decks, corner files, include files, and any setup file used by the run command. For measured silicon, this means the measurement setup record. Put those files under `evidence/aimc-simulator-adapters/candidate-post-layout/models/`.

4. Run one named post-layout or measured-silicon experiment.

   Use one run name. Record it as `provenance.run_id`, then copy the same value into `simulation.run_id`, `energy.run_id`, `latency.run_id`, `noise.run_id`, `area.run_id`, and `break_even_rerun.run_id`.

5. Measure or compute the physical values from that same run.

   The required values are:

   - ADC energy per conversion
   - DAC energy per row drive
   - conversion time
   - row or sample settling time
   - output RMS noise
   - input-referred noise
   - ADC area
   - DAC area
   - supply voltage
   - temperature
   - process corner or measured condition

6. Check the fixed boundary.

   The DAC target stays 10 bits. The ADC target stays 12 bits. Output noise RMS must be at or below `0.004`. The sharing rule stays 64 rows, 4 columns, 4 converter instances, and 16 outputs per conversion cost unless the break-even model is changed at the same time.

7. Rerun the break-even calculation with the extracted or measured values.

   Put the source rerun JSON under `evidence/aimc-simulator-adapters/candidate-post-layout/rerun/`. This source rerun is the reason for `break_even_rerun.replacement_decision`. The later strict submission command will write its own accepted rerun only after the candidate passes.

8. Fill `evidence/aimc-simulator-adapters/candidate-post-layout/payload.json`.

   Remove `template_only: true` only after every placeholder has been replaced by a real value or real file path.

9. Run the readiness command.

   `python3 scripts/run_converter_post_layout_candidate_readiness.py`

10. If the readiness command reports ready, submit the payload.

    `python3 scripts/submit_converter_post_layout_payload.py evidence/aimc-simulator-adapters/candidate-post-layout/payload.json`

## What Each File Proves

- `payload.json` proves the claim has one machine-readable shape.
- `netlist/` proves the converter object can be inspected.
- `models/` proves the run condition is not only a label.
- `rerun/` proves the replace-or-fallback decision was recomputed from the candidate values.
- the shared `run_id` proves the values belong to one run.

## What Must Not Happen

Do not copy local schematic estimates into the post-layout payload. They are useful planning evidence, but they are not extracted layout or measured silicon.

Do not mix energy from one run with noise from another run. That would hide the actual converter being judged.

Do not create `accepted-post-layout` by hand. Only the strict submission command should write accepted evidence.

## Review Path

- Check the current gaps: `python3 scripts/run_converter_post_layout_candidate_readiness.py`
- Read the exact edit list: `site/research/converter-post-layout-candidate-edit-plan.html`
- Read the blockers: `site/research/converter-post-layout-blocker-ledger.html`
- Submit only after preflight is clean: `python3 scripts/submit_converter_post_layout_payload.py evidence/aimc-simulator-adapters/candidate-post-layout/payload.json`

## Refused Claim

This recipe does not prove post-layout behavior, does not provide measured silicon, and does not replace the digital fallback. It only defines the run order needed to produce a package that the strict gate can judge.
