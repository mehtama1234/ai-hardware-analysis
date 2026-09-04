# Converter Post-Layout Payload Template

This is the field-by-field template for the real converter payload.

- status: `template_defined_not_evidence`
- template: `sources/evidence/converter-post-layout-payload.template.json`
- validator: `scripts/validate_converter_post_layout_payload.py`

## First-Principles Reading

The converter claim has to join four objects that are easy to confuse. The layout creates a physical circuit. Extraction turns that layout into a circuit with wire and device parasitics. Simulation or silicon measurement turns that extracted circuit into numbers. The break-even rerun decides whether those numbers are good enough to replace the old digital fallback.

A useful payload cannot skip any of those objects. If it has energy but no extracted netlist, the number is floating. If it has an extracted netlist but no model files or command, the run cannot be repeated. If it has noise but no shared converter rule, the cost is not the same system. If it has all circuit numbers but no break-even rerun, it has not answered the system question.

## How To Fill It

- replace every `REPLACE_WITH...` value with a value from the extracted post-layout run or measured silicon run
- keep `adc_bits` at `12`, `dac_bits` at `10`, and `output_noise_budget` at or below `0.004`
- keep the sharing rule at 64 rows, 4 columns, 4 converter instances, and 16 outputs per conversion cost unless the break-even model is changed too
- use one shared `run_id` across provenance, simulation, energy, latency, noise, area, and break-even rerun fields
- rerun the break-even calculation with extracted energy, latency, noise, area, and the same sharing rule
- run `python3 scripts/validate_converter_post_layout_payload.py FILLED_PAYLOAD.json` before using it as evidence

## Refused Claim

does not claim any extracted converter result exists and is intentionally not validator-ready
