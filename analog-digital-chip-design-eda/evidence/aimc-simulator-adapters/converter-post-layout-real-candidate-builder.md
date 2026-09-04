# Converter Post-Layout Real Candidate Builder

- status: `candidate_payload_built`
- self-test: `True`
- temporary fixture persisted: `False`
- wrote payload: `True`
- candidate payload: `temporary self-test payload removed`
- strict validation passed: `True`
- strict issue count: `0`
- preview status before removal: `ready_to_submit_without_writing`
- preview would write accepted evidence before removal: `True`
- preview strict issue count before removal: `0`

This builder turns a real run into the candidate payload shape used by preflight and strict submission.

## First Principle

A real run should be copied into the candidate workspace as a small packet: one payload, one extracted netlist, one model or measurement file, and one source rerun artifact. The payload should name one converter and one run id. The values should be numeric before the submitter is allowed to write accepted evidence.

The builder can assemble that packet. It cannot make the files true. The files and numbers must already come from the post-layout simulation or measured-silicon run.

## Copied Files


## Strict Issues

- none

## Next Command

`python3 scripts/build_converter_post_layout_candidate_from_real_run.py --netlist REAL.sp --model-file MODEL.sp --rerun-artifact RERUN.json ...`

## Refused Claim

does not write accepted evidence, does not bypass strict submission, and does not prove the input files came from silicon or layout
