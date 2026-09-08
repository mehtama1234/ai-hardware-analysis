# Fixed-protocol MoE learning experiment

Observed result: all three seeds passed without changing the protocol. Held-out
MSE was 0.00753646, 0.00631578 and 0.00390279 respectively; affine baseline MSE was
0.22743643. Values were independently recomputed from saved predictions/targets,
and source hashes matched. See `reports/trained-task-cpu.json`.

Run from the repository root in the documented CPU environment:

```bash
python3 gpu-mode-curriculum/moe-routing-all-to-all/run_trained_task.py
python3 gpu-mode-curriculum/moe-routing-all-to-all/verify_trained_task.py
```

The target is a declared piecewise-affine function of two uniformly sampled
inputs in `[-1,1]`: `x0+x1` when `x0>=0`, otherwise `-2*x0+0.5*x1`. Data seed 270
produces 512 training and 256 held-out examples. No held-out labels enter updates.
Three predeclared model seeds (271, 281, 291) each train for exactly 200 full-batch
Adam steps at learning rate 0.03. No early stopping or seed selection is used.

The model has four linear experts and a learned linear router using the tested
selected-logit top-2 policy. Capacity equals token count, so no assignment is
dropped. No load-balancing loss is used. The comparator is an affine least-squares
fit using training data only. It has three parameters versus the MoE's sixteen;
this is not a compute- or parameter-matched architecture comparison.

Acceptance was fixed before execution: every seed must obtain held-out MSE at
most 0.1 and at most half the dense-affine baseline MSE. Every seed's result is
retained. Failure is an experiment result; it must not trigger retuning against
this holdout. Training loss traces, held-out predictions/targets, final weights,
expert loads, data identity and source hashes are stored in the JSON report.

The standalone verifier recomputes prediction MSE and the ratio to the recorded
baseline, enforces the fixed protocol/seed coverage, and rejects truncated or
non-finite arrays, incomplete training traces and inconsistent assignment counts.
Three report-contract tests pass. The verifier also reconstructs and hashes the
declared dataset, independently refits the training-only affine baseline, and
replays the saved router/expert tensors against every stored holdout prediction
and expert-load count. This verification passed on the recorded report. It does
not replay optimizer history or independently retrain the model; source hashes
and the original training experiment remain necessary complementary evidence.

This is supervised synthetic learning evidence, not language modeling, expert
specialization, generalization beyond the sampled task, throughput or distributed
training. The three runs share a holdout and are not independent dataset trials.
The experiment is not yet in the aggregate checkpoint. A subsequent model or
protocol choice needs separate development data and a fresh final evaluation.

## Frozen-weight distributed replay

Verified result: all three trained models replayed successfully on two ranks.
Maximum prediction difference was zero across the 256 holdout examples per
model; recombined MSE matched the single-process results. Training-artifact and
source freshness checks passed. See `reports/trained-distributed-cpu.json`.

```bash
python3 gpu-mode-curriculum/moe-routing-all-to-all/run_trained_distributed.py
```

This follow-up consumes the existing trained report; it never retrains. It checks
training-source freshness, reconstructs the declared data and verifies its hash,
then divides the same 256 held-out examples between two CPU/Gloo processes.
Each rank constructs only its owned expert tensors, while router weights are
replicated. The candidate executes the existing dispatch/compute/return path.

Every prediction is compared with the frozen single-process prediction, not
merely its aggregate MSE. The parent combines rank-local squared-error sums and
checks that the trained artifact did not change during execution. The report
records that artifact's SHA alongside source hashes, preventing a silent change
of trained weights. This tests deployment fidelity on the same holdout, not a
new independent quality evaluation. It remains outside the aggregate checkpoint.
