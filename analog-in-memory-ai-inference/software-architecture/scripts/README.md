# AIMC Toolkit Install Scripts

Start from the [Connected System Map](../connected-system-map.html). These scripts use the same contract: object, constraint, design move, evidence, allowed claim, refused claim, and next handoff.

Run this from `ai-hardware-analysis/analog-in-memory-ai-inference/software-architecture`:

```bash
bash scripts/install-aimc-toolkits.sh
```

The script installs and checks the runnable Python simulators first:

- IBM AIHWKIT
- Sandia CrossSim

It also clones and probes the heavier source toolchains:

- analog-mlir
- SST core
- ALPINE/gem5-X

If system packages are missing, the script records the exact blocker and prints the apt command to run. The full report is written to:

```text
backend/.data/toolkit-install/install-report.txt
```
## Transformer execution contract

Build the first machine-readable workload, operator, movement, and hybrid
schedule package from the real deep transformer fixture:

```bash
python3 scripts/build_transformer_execution_contract.py \
  --model samples/deep-transformer-mlp-stack.onnx \
  --output /tmp/deep-transformer-execution-contract \
  --target-profile robotics \
  --phase prefill
```

Run the no-download contract check from the backend virtual environment:

```bash
cd backend
.venv/bin/python ../scripts/check_transformer_execution_contract.py
```

The output is planning and estimated evidence only. It deliberately refuses to
claim measured latency, energy, silicon behavior, or full LLM decode until those
separate gates are implemented.

Run the deterministic output gate for the MLP fixture. It compares the original
ONNX graph with a replay in which analog candidates receive a declared synthetic
relative weight-error model:

```bash
python3 scripts/run_transformer_output_comparison.py \
  --model samples/deep-transformer-mlp-stack.onnx \
  --output /tmp/deep-transformer-output-comparison \
  --target-profile robotics \
  --error-scale 0.001
```

Use the current physical gate to force exact digital fallback when extracted
converter artifacts are not accepted:

```bash
python3 scripts/run_transformer_output_comparison.py \
  --physical-gate ../../analog-digital-chip-design-eda/evidence/aimc-simulator-adapters/analog-converter-physical-cell-gate.json \
  --enforce-physical-gate \
  --output /tmp/deep-transformer-output-physical-gated
```

The JSON is a software experiment artifact, not a silicon claim. The next
replacement is measured per-tile calibration data and held-out token-level
decode agreement.

Run the attention-shaped decode slice with explicit digital K/V cache traffic:

```bash
python3 scripts/run_transformer_decode_comparison.py \
  --model samples/attention-block.onnx \
  --sequence-length 6 \
  --output /tmp/attention-decode-comparison \
  --error-scale 0.001
```

This reports per-token cache reads/writes, output-channel agreement, attention
entropy, and a conservative acceptance result. It is the bridge to a real
causal language-model decode, but it is not itself a tokenizer-level claim.

Run the token-ID causal-LM fixture, including an oracle check that manual
cached decode matches the full ONNX causal-prefill graph:

```bash
python3 samples/make-tiny-causal-lm-onnx.py
python3 scripts/run_tiny_causal_lm_decode.py \
  --model samples/tiny-causal-lm.onnx \
  --prompt 1,2 \
  --generated-steps 4 \
  --output /tmp/tiny-causal-lm-decode \
  --error-scale 0.001
```

This is a checked-in toy vocabulary and model, so the result is a token-level
software gate—not evidence about a production tokenizer or full LLM.

Run the seeded synthetic reliability sweep:

```bash
python3 scripts/run_tiny_causal_lm_reliability_sweep.py \
  --model samples/tiny-causal-lm.onnx \
  --error-scales 0,0.001,0.003,0.005,0.01 \
  --seeds 7,11,19,23 \
  --output /tmp/tiny-causal-lm-reliability
```

The sweep preserves every case and reports acceptance rate, worst relative
error, token agreement, exact free-running sequence agreement, and prefill
oracle status. Its error scales are synthetic until physical calibration data
is connected.

The checked-in five-scale/four-seed run produced 17/20 accepted cases. All
token sequences still agreed, but three 1% error cases exceeded the 1% relative
output-residual limit. That is an intentional useful failure boundary, not a
reason to silently loosen the gate.

Import the guarded calibrated attention profile from the sibling EDA repo:

```bash
python3 scripts/import_attention_calibration_profile.py \
  --model samples/attention-block.onnx \
  --profile ../../analog-digital-chip-design-eda/evidence/aimc-simulator-adapters/crosssim-calibrated-attention-block-analog-error-simulation.json \
  --output /tmp/attention-calibration-import
```

The importer checks source-model identity, candidate IDs, weight names and
shapes, residual limits, calibration scope, and claim level. It does not apply
the profile to another model and does not promote simulator evidence to silicon
evidence.

Use the matching profile in the attention decode replay:

```bash
python3 scripts/run_transformer_decode_comparison.py \
  --model samples/attention-block.onnx \
  --calibration-profile-json ../../analog-digital-chip-design-eda/evidence/aimc-simulator-adapters/crosssim-calibrated-attention-block-analog-error-simulation.json \
  --error-scale 0 \
  --output /tmp/attention-decode-calibrated
```

The runner applies only the imported profile's declared held-out residual
vectors to matching Q/K/V/O projections. It records that transformation and
keeps the simulator-only claim boundary.

Run the complete vertical slice and emit one hash-linked evidence package:

```bash
python3 scripts/run_transformer_vertical_slice.py \
  --output /tmp/transformer-vertical-slice
```

When a GPU host produces the real-model handoff, include it in the same
hash-linked package:

```bash
python3 scripts/run_transformer_vertical_slice.py \
  --output /tmp/transformer-vertical-slice-real-model \
  --real-model-evidence /path/to/gpu-run/serving-bridge.json
```

The CPU/GPU baseline intake can also be attached:

```bash
python3 scripts/run_transformer_vertical_slice.py \
  --output /tmp/transformer-vertical-slice-real-model \
  --real-model-intake /tmp/real-model-intake/real_model_intake.json
```

The package contains prefilling and decode contracts, output comparisons,
token-level decode, reliability results, calibrated-profile import, cost
benchmark, claim report, and a manifest hashing every artifact and source.

The package also imports the physical converter gate. At present all four
named cells are present, but two extracted follow-on artifacts are missing;
the import preserves those exact paths and does not treat starter payloads as
physical signoff. This is a downstream pre-silicon feasibility lane, not a
physical-device measurement and not the blocker for the model-level decision.

Start the real-model baseline intake on a CPU or GPU host with:

```bash
python3 scripts/run_real_model_intake.py \
  --model HuggingFaceTB/SmolLM2-135M \
  --device cuda \
  --output /tmp/real-model-intake
```

The resulting `real_model_intake.json` is model/tokenizer baseline evidence;
it must still be paired with a candidate serving run before the decision gate
can pass.

Run the first paired real-model serving comparison with:

```bash
python3 scripts/run_real_model_serving_comparison.py \
  --model openai-community/gpt2 \
  --device cuda \
  --output /tmp/real-model-serving
```

The comparison measures cached versus uncached generation and checks output
parity. It records end-to-end timing only; prefill/decode attribution and
energy remain open requirements.

The Colab characterization handoff closes the phase-attribution requirement
for the recorded scope. It measures synchronized manual prefill/decode timing,
KV allocator peaks, output parity, and batch sizes 1/2/4:

```bash
COLAB_SESSION_NAME=real-model-characterization-gpt2 \
COLAB_RUN_ID=colab-real-model-characterization-gpt2 \
COLAB_HANDOFF_MODE=real-model-characterization \
bash ../../gpu-mode-curriculum/scripts/run_colab_gpu_handoff_local.sh
```

Attach its `real_model_serving_characterization.json` report with
`--real-model-serving-characterization`; the report remains scoped to the
measured GPT-2/T4 protocol and does not claim energy, silicon benefit, or
production capacity.

When characterization is attached, the package also emits
`real_model_hybrid_cost_bridge.json`. It uses measured GPU timing, parity, and
KV-memory values as serving denominators while keeping the existing pJ model
explicitly modeled-only and forcing digital execution until physical and power
evidence gates pass.

The current end-to-end Colab gate is to extend this same real GPT-2/Tesla-T4
protocol to longer contexts, concurrency and tail latency, an operator/data-
movement breakdown, and synchronized power. The resulting decision may be
positive, negative, or insufficient; it must not be converted into a silicon
claim without separate physical evidence.

The CUDA paged-attention kernel now participates in full GPT-2 decode across
all 12 layers with token parity on Colab T4. Device-resident and persistent
cache variants were measured: the persistent candidate remains about 26% slower
on the short repeated trace and 43% slower on the long trace than native
scheduled serving. Native serving remains the baseline. The next connected
hardware investigation is the [real GPT-2 projection evaluation](../experiments/gpt2-hybrid-v1/README.md),
which propagates explicit provisional array errors through the actual model
and records converter/movement counts while keeping physical placement blocked.

When the extended report is attached, the package also emits
`real_model_workload_hardware_contract.json`. This derived contract currently
prioritizes decode-first digital runtime work, keeps KV-cache/control/
conversion-and-fallback paths digital-required, and records analog placement
as deferred. Its slopes and hotspots are derived from the measured GPT-2/T4
run; they are not generalized silicon specifications.

The package derives `real_model_decision.json` from that comparison. A CPU
result can establish parity and a bounded timing observation, but remains
`hardware_measurement_pending` until the same workload runs on the accelerator.

Verify the package invariants with:

```bash
python3 scripts/check_real_model_decision_package.py \
  --package /tmp/transformer-vertical-slice-real-model
```

Attach that result to the full package with:

```bash
python3 scripts/run_transformer_vertical_slice.py \
  --output /tmp/transformer-vertical-slice-real-model \
  --real-model-intake /tmp/real-model-intake/real_model_intake.json \
  --real-model-serving-comparison /tmp/real-model-serving/real_model_serving_comparison.json
```

On a GPU host, the complete three-stage handoff is one command:

```bash
bash scripts/run_real_model_gpu_handoff.sh \
  openai-community/gpt2 \
  /tmp/transformer-real-model-gpu
```

It runs real-model intake, cached/uncached serving comparison, and package
integration with `--device cuda`. The local workspace has no NVIDIA device, so
this command is intentionally host-side and must not be replaced by replayed
T4 fixtures. It fails before model loading when CUDA is unavailable.

The import also carries the EDA candidate-readiness result when available. This
currently reports a scaffold with 29 placeholders, 22 preflight issues, and 32
open checklist items, so the physical claim remains blocked even though the
starter cells exist.

When available, it also records the separate Magic starter-layout measurement
(currently 4/4 cells measured and a 237.6 um² macro bounding box). That number
is explicitly marked non-signoff and cannot enable analog placement.

Run the same token trace through the explicit cost denominator:

```bash
python3 scripts/benchmark_tiny_causal_lm.py \
  --model samples/tiny-causal-lm.onnx \
  --output /tmp/tiny-causal-lm-benchmark
```

This reports Python reference timing separately from modeled digital/hybrid
MAC, converter, and K/V-cache energy. The default coefficients are assumptions
that must be replaced with board, RTL, or accelerator measurements.

To enforce the current EDA physical gate and force analog candidates to
fallback while extracted artifacts are incomplete:

```bash
python3 scripts/build_transformer_execution_contract.py \
  --physical-gate ../../analog-digital-chip-design-eda/evidence/aimc-simulator-adapters/analog-converter-physical-cell-gate.json \
  --enforce-physical-gate \
  --output /tmp/deep-transformer-physical-gated
```

Validate the next GPU-host handoff with:

```bash
python3 scripts/import_real_model_inference_evidence.py \
  --source /path/to/gpu-run/serving-bridge.json \
  --output /tmp/real-model-inference
```

The importer requires model and tokenizer identity, accepted measured-GPU
execution, serving rows, and a non-synthetic workload. Existing synthetic T4
reports therefore produce an explicit blocked import rather than being
promoted into the real-model decision package.
