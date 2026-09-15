# Colab four-workstream demo

From a Colab cell after cloning this repository:

```python
import sys
sys.path.insert(0, "/content/ai-hardware-analysis/analog-digital-chip-design-eda")
from colab.run_four_workstream_colab import run_demo

result = run_demo()
print(result["status"])
print(result["checkpoint"])
```

The same entry point can also be run directly from the repository root:

```bash
python3 colab/run_four_workstream_colab.py
```

The provider-free default runs the seeded design with the local JSONL fixture.
To use a real local worker, set `VERIFICATION_LLM_COMMAND` before calling
`run_demo()`. The result includes the four-workstream artifacts and a
hash-verified checkpoint. Colab also emits a hash-verified
`four-workstream-evidence-manifest.json` and checks it during checkpoint
resume. This is a software/toolchain demonstration; Colab
does not provide FPGA/SVM acceleration or commercial EDA tools. The seeded
formal model is included by default; its intentional defect produces a
classified counterexample that is preserved as evidence, not a release claim.
The demo also exercises the seeded coverage report, one bounded
assertion-generator team handoff, and an explicitly approved repair retest on
a run-local copy; the canonical seeded RTL remains unchanged. It also runs the
same agent-generated repair contract across four seeded designs.
The matrix report contains per-design evidence paths and a self-digest.
Each matrix case first generates a fresh failing baseline waveform from the
current RTL and testbench.
The seeded-counter debug input also exercises CDFG-based golden/RTL signal
alignment and records its ambiguity and unresolved-match counts.
The demo also runs a four-design specification-grounded assertion matrix for
the counter, arbiter, decoder, and FIFO. Every case must produce an admitted
review-only agent proposal and pass explicit SVA lowering/compiler validation;
the self-digested matrix is not formal proof or signoff.
Protocol execution additionally requires the command to reference the exact
generated sequence artifact, so coverage markers from an unrelated command
cannot satisfy the runtime evidence gate.

## Four-task real causal-agent run

The four-class real causal-agent experiment can be packaged from the verified
161-stage artifact:

```bash
python3 scripts/package_real_four_causal_agent_colab_task.py \
  --peripheral-causal-report /tmp/next-stage-milestone-161-four-causal-agent-20260915/real-peripheral-causal-localization/real-peripheral-causal-localization-report.json \
  --operation-causal-report /tmp/next-stage-milestone-161-four-causal-agent-20260915/real-causal-localization/real-causal-localization-report.json \
  --error-budget-causal-report /tmp/next-stage-milestone-161-four-causal-agent-20260915/real-error-budget-causal-localization/real-error-budget-causal-localization-report.json \
  --multiclock-causal-report /tmp/next-stage-milestone-161-four-causal-agent-20260915/real-multiclock-causal-localization/real-multiclock-causal-localization-report.json \
  --output /tmp/real-four-causal-agent-colab.tgz
```

Upload the archive to Colab as `/content/real-four-causal-agent.tgz` and run
`run_real_four_causal_agent_remote.py`. The runner downloads the configured HF
model, executes all four repair trajectories on the GPU, and checks each
digest-bound result. The offline archive smoke test is passing; a live Qwen
result is not claimed until Colab executes the runner.

Before upload, validate the archive itself with:

```bash
python3 scripts/check_real_four_causal_agent_colab_package.py \
  /tmp/real-four-causal-agent-colab.tgz
```

After downloading the Colab summary, validate it independently with:

```bash
python3 scripts/check_real_four_causal_agent_remote_summary.py \
  /path/to/real-four-causal-agent-colab-summary.json
```

The same flow is available as `real_four_causal_agent_run.ipynb`; upload the
notebook to Colab, upload the generated `.tgz` when prompted, and run the cells
in order.

## Real multi-module structural/CDFG slice gate

The repository-scale structural context gate can be rerun from the monorepo
root after the real-design catalog has been produced:

```bash
python3 scripts/run_real_multimodule_structural_ir.py \
  /path/to/real-multimodule-rtl-catalog.json \
  --output /tmp/real-multimodule-structural-ir
python3 scripts/check_real_multimodule_structural_ir.py \
  /tmp/real-multimodule-structural-ir/real-multimodule-structural-ir-report.json
```

The report covers Yosys structural IR, parser-backed CDFG extraction, and one
bounded backward dependency slice per target. It is context-reduction evidence
only; it does not claim functional localization or equivalence.

## Next-stage Colab run

Run the next-stage seeded evaluation in one fresh artifact directory:

```bash
python3 colab/run_next_stage_colab.py --agent-backend local --require-real-agent
```

Set `VERIFICATION_LLM_COMMAND` or `VERIFICATION_LLM_BATCH_COMMAND` to the
Colab JSONL model worker first. The
bundle runs held-out mutation evaluation, coverage closure, repaired
induction, security red/blue checks, an eight-design repository-agent matrix,
and a focused repository-agent handoff. Use `--agent-backend mock` for a
provider-free transport replay. The report keeps
the claim boundary separate from generalization, physical signoff, and
automatic release.
