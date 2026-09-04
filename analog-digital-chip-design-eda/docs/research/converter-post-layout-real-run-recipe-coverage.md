# Converter Post-Layout Real Run Recipe Coverage

This page checks whether the real-run recipe covers the current candidate checklist.

It does not produce post-layout evidence. It only checks that the recipe does not skip the fields and files that still block strict submission.

## First Principle

A checklist names the missing facts. A recipe gives an order for producing them. Those are different objects.

The recipe is useful only if every checklist item appears in the run order. If the checklist asks for ADC area, the recipe must say where ADC area comes from. If the checklist asks for a source rerun artifact, the recipe must include the break-even rerun step. If the checklist asks for a shared run id, the recipe must name every run-id field that has to match.

## Review Rule

The generated audit compares the current checklist fields to the current recipe fields.

If uncovered checklist fields is zero, the recipe covers the current fill work. If it is not zero, the recipe is incomplete and should not be treated as the handoff path.

## Refused Claim

This coverage audit does not prove the converter, does not fill the candidate payload, and does not create accepted evidence.
