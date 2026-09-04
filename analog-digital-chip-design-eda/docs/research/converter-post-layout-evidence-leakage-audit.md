# Converter Post-Layout Evidence Leakage Audit

This page is generated from the evidence leakage audit.

The audit checks that test fixtures did not become evidence. It looks at the candidate workspace, the accepted post-layout directory, and the builder self-test report.

## First Principle

A test fixture proves that the workflow can work. It does not prove that the converter worked.

That line matters. If a temporary file is left in the candidate workspace, a later reviewer may treat it as a real extracted file. If an accepted-evidence directory appears before strict submission, the site may look more complete than the hardware evidence allows.

This audit keeps the states separate:

- scaffold waiting for real files
- temporary self-test package removed
- accepted evidence only after strict submission

## Refused Claim

This audit does not prove real post-layout evidence exists and does not submit accepted evidence.
