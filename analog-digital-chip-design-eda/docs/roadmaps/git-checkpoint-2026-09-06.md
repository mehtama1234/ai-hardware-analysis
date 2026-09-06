# Local Git checkpoint — 2026-09-06

This checkpoint preserves recovered pre-crash work and subsequent hybrid
inference research across the two user-designated projects. It is not a
hardware-completion release. The current project checkpoint and restart ledger
describe the remaining system and hardware-access gates.

## Scope and evidence policy

- Commit source, tests, documentation and generated site state separately from
  experiment data and raw evidence, then retain both commits together.
- At inspection, 136 tracked files were modified and 3,757 untracked files
  existed in the two project folders. New files totalled about 231 MB; the
  largest was a 23 MB waveform. No individual file exceeded 25 MB.
- Preserve raw waveforms because evidence audits depend on their exact bytes.
  Do not silently exclude them while committing references that require them.
  Keep failed candidates, simulator logs and source snapshots as research
  evidence, not accepted hardware results. The root-level historical extracted
  SPICE artifact is retained as recovered material, not a promoted candidate.
- Existing ignore rules continue to exclude environments, Python caches and
  other already-ignored local material. A clean worktree does not mean those
  ignored files are backed up.
- No deletion, remote push, hardware programming, purchase or fabrication is
  part of this checkpoint. Local commits are not an off-machine backup.

## Validation actually performed

- `git diff --check`: pass.
- Latch unit-test discovery: 33 tests pass.
- `scripts/validate_project.py`: pass.
- AST syntax checks across 238 changed/untracked Python files: pass.
- Limited private-key/AWS-key/GitHub-token pattern scan: no alerts. This is
  not an exhaustive security audit.

Not performed: rerunning every historical experiment, complete end-to-end
hardware validation, or independent review of every generated artifact. These
commits preserve the research state; passing structural checks do not repair
known circuit failures or supply missing hardware access.
