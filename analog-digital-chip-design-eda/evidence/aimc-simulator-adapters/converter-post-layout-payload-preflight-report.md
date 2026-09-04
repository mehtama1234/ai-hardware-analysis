# Converter Post-Layout Payload Preflight

- status: `preflight_ready`
- missing-file payload reported not ready: `True`
- temporary complete payload reported ready: `True`
- synthetic accepted evidence persisted: `False`
- preflight command: `python3 scripts/preflight_converter_post_layout_payload.py REAL_PAYLOAD.json`

Preflight is the review step before submission. It reads a candidate payload, checks the same shape and file boundaries as strict submission, and writes a report. It does not write accepted evidence.

## First Principle

A payload can fail in two different ways. A shape mistake means it does not say enough, such as missing an energy term or using the wrong sharing rule. A file mistake means it says the right kind of thing but points to files that are not present. The second case is dangerous because the payload looks complete while the physical evidence is not inspectable.

Preflight separates those cases before the final submission command is allowed to touch the accepted evidence directory.

## Refused Claim

does not submit real post-layout evidence, does not write accepted evidence, and does not replace converter break-even assumptions
