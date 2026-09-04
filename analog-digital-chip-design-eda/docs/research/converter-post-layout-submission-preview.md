# Converter Post-Layout Submission Preview

This page is generated from the submission preview artifact.

The preview is the last review step before strict submission. It reads the candidate payload, runs the same strict blockers used by the submitter, and shows whether accepted evidence would be written.

It does not write accepted evidence.

## First Principle

Accepted evidence should appear only after the object is already real. For this converter flow, real means one converter id, one run id, real extraction files, real model files, a real rerun source artifact, and numeric energy, latency, noise, and area values.

The preview keeps those two actions separate. It can say what would happen. It cannot make the result happen.

## Safe Command

`python3 scripts/preview_converter_post_layout_submission.py --expect-blocked`

On the current scaffold, this command should report blocked before submission.

## Refused Claim

This preview does not submit evidence, does not create `accepted-post-layout`, does not run break-even, and does not prove post-layout converter replacement.
