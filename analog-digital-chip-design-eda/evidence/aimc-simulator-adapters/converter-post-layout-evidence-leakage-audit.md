# Converter Post-Layout Evidence Leakage Audit

- status: `no_evidence_leakage_detected`
- accepted post-layout exists: `False`
- candidate file count: `5`
- candidate non-scaffold file count: `0`
- candidate temp marker hit count: `0`
- builder temp paths are labeled: `True`
- builder preview ready before removal: `True`
- issue count: `0`

This audit protects the line between a test fixture and evidence. A temporary builder package may prove that the mechanics work. It must not leave files in the canonical candidate workspace, and it must not create accepted evidence.

## First Principle

A proof helper is allowed to make temporary objects. It is not allowed to make those objects look like real converter evidence. The evidence folder should show only two states: a scaffold waiting for real files, or accepted evidence written by the strict submitter after a real package passes.

## Issues

- none

## Refused Claim

does not prove real post-layout evidence exists and does not submit accepted evidence
