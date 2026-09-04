# Converter Post-Layout Real Run Recipe Coverage

- status: `real_run_recipe_covers_current_checklist`
- recipe field count: `37`
- checklist field count: `32`
- covered checklist field count: `32`
- blocker field count: `34`
- payload blocker field count: `32`
- non-field boundary blocker count: `2`
- covered blocker field count: `32`
- uncovered blocker field count: `0`

This audit checks the recipe against the current checklist. The recipe is useful only if every checklist edit appears in at least one ordered step.

## First Principle

A run recipe can sound complete while still skipping a needed field. This audit removes that ambiguity. It compares the fields the candidate package still needs with the fields named by the ordered recipe.

## Uncovered Checklist Fields

- none

## Non-Field Boundary Blockers

- `template payloads cannot be submitted`
- `template payloads cannot pass same-run consistency`

## Uncovered Payload Blocker Fields

- none

## Refused Claim

does not supply real post-layout files, measured values, accepted evidence, or analog replacement proof
