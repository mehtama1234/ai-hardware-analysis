# Converter Circuit Evidence Contract

This page defines what must replace the local converter break-even assumptions.

- schema: `sources/evidence/converter-circuit-evidence-schema.json`
- current status: `contract_defined_placeholder_not_claim_ready`
- target ADC bits: `12`
- target DAC bits: `10`
- output noise budget: `0.004`
- claim-ready to replace break-even: `False`

## First-Principles Reading

The break-even page says the converter target can become useful only if real converter cost is low enough and shared across enough useful outputs. This contract says what real means.

A converter proof has to measure five separate things. Energy says how much electrical work is spent per conversion. Latency says how long the signal must settle and how long the ADC decision takes. Noise says whether the converter output stays inside the 0.004 budget. Area says how much silicon is spent and whether converters are copied or shared. Sharing says how many rows, columns, and outputs pay for one converter cost.

Without those fields, a converter number is only a planning estimate. With those fields, the system can rerun the break-even table using circuit or measured evidence instead of assumptions.

## Required Fields

- `result_type`
- `converter_id`
- `measurement_level`
- `target_boundary`
- `energy`
- `latency`
- `noise`
- `area`
- `sharing`
- `provenance`
- `claim_boundary`

## Measurement Levels

- `local_estimate`
- `circuit_simulation`
- `post_layout_simulation`
- `measured_silicon`

## Current Placeholder

The current placeholder is intentionally not claim-ready. It carries the target bit and noise boundary forward, but leaves energy, latency, area, and sharing as missing measured facts.

## Required Next Evidence

- transistor-level or post-layout ADC energy for 12-bit output conversion
- DAC row-driver energy for 10-bit input drive
- settling and conversion time for the same converter setting
- output noise RMS below 0.004 in the same scale used by the replay
- area and converter-sharing rule for the tile
- rerun of the break-even table with measured or post-layout numbers

## Refused Claim

does not prove converter energy, converter latency, converter area, silicon noise, or board power
