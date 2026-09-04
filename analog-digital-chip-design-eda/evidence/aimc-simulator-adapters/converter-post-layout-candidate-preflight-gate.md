# Converter Post-Layout Candidate Preflight Gate

- status: `preflight_gate_passed`
- current scaffold rejected: `True`
- temporary complete payload ready: `True`
- synthetic accepted evidence persisted: `False`
- current scaffold issue count: `22`
- current scaffold same-run validation passed: `False`
- temporary complete issue count: `0`
- temporary complete same-run validation passed: `True`

This gate runs the actual preflight command against two packages. The current candidate scaffold must be rejected. A temporary complete package must be ready. Neither path is allowed to write accepted evidence.

## First Principle

Preflight is the door before submission. It should answer one narrow question: can the package be inspected enough for strict submission to start? If fields are placeholders or files are missing, the answer is no. If the fields are concrete and the files exist, the answer is yes.

This still does not say the converter is good. It says the packet is complete enough to be judged.

## Refused Claim

does not submit the temporary package, does not write accepted evidence, and does not prove real post-layout physics
