# Converter Post-Layout Strict Intake

This report checks the file boundary for future post-layout converter evidence.

- status: `strict_file_intake_ready_waiting_for_real_artifacts`
- shape-only payload: `evidence/aimc-simulator-adapters/dry-run/converter-post-layout-evidence.shape-only-missing-files.json`
- shape validation passed: `True`
- strict validation rejected missing files: `True`
- strict rerun rejected missing files: `True`

## First-Principles Reading

A payload can have the right numbers and still fail as evidence. If the extracted netlist path is missing, the converter is not inspectable. If model files are missing, the process corner is only a label. If the break-even rerun artifact is missing, the replacement decision cannot be audited.

Strict intake therefore adds a file test after the field test. The ordinary validator checks the payload shape, units, numeric bounds, and sharing rule. The strict mode also checks that the extracted netlist, model files, and break-even rerun artifact exist.

## Refused Claim

does not provide post-layout evidence and does not make a converter replacement decision
