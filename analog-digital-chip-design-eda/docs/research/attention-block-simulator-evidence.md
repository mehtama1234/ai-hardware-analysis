# Attention-Block Simulator Evidence

This page explains the attention-shaped simulator replay.

The projection-stack proof has repeated static-weight projections. This page adds the part that makes foundation models harder: the graph forms Q and K, builds scores from them, applies softmax, mixes V by those scores, and then applies an output projection.

## Object

The object is `attention-block.onnx`.

It is a small attention-shaped fixture, not a pretrained model. It has three token rows and width eight:

- `attn.q.matmul`: static Q projection
- `attn.k.matmul`: static K projection
- `attn.v.matmul`: static V projection
- `attn.scores.matmul`: dynamic QK score formation
- `attn.scale`: digital score scaling
- `attn.softmax`: digital selection
- `attn.value.matmul`: dynamic value mixing
- `attn.out.matmul`: static output projection

The analog simulator replay covers only the static projection weights: Q, K, V, and output projection.

## Constraint

The dynamic attention operations stay digital in this proof.

That is the key boundary. A crossbar is natural for a fixed weight matrix. The attention score matrix is made from current activations, not stored model weights. Softmax is a selection rule over those scores. Value mixing uses input-dependent weights. Those operations need separate evidence before they can be claimed as analog work.

## Design Move

Generate the fixture with:

```bash
/home/mehtama1/git-repo/ai-hardware-analysis/analog-in-memory-ai-inference/software-architecture/backend/.venv/bin/python /home/mehtama1/git-repo/ai-hardware-analysis/analog-in-memory-ai-inference/software-architecture/samples/make-attention-block-onnx.py
```

Run the replay with:

```bash
python3 scripts/run_attention_block_aimc_simulator_payloads.py
```

The script extracts real ONNX initializer weights, computes a digital reference, sends only the static projection MatMuls through AIHWKIT and CrossSim, then computes score formation, scaling, softmax, value mixing, and final comparison in ordinary digital arithmetic.

The output files are:

- `evidence/aimc-simulator-adapters/aihwkit-attention-block-analog-error-simulation.json`
- `evidence/aimc-simulator-adapters/crosssim-attention-block-analog-error-simulation.json`
- `evidence/aimc-simulator-adapters/attention-block-simulator-payload-run-summary.json`

## Evidence

The current result is not a positive simulator claim.

Both AIHWKIT and CrossSim execute the attention-shaped replay. CrossSim passes the guarded positive-evidence check. AIHWKIT is rejected for a positive claim because its residual is above the local threshold.

That is a good result for the evidence system. It proves the path can run a harder graph and that the guard stops weak numerical agreement from being described as a working analog attention result.

## Allowed Claim

The system can say:

AIHWKIT and CrossSim now execute an attention-shaped ONNX replay where static projection weights pass through simulator APIs and dynamic attention operations remain digital. CrossSim passes the guarded evidence check. AIHWKIT runs but is rejected for a positive simulator claim because its residual exceeds the local threshold.

## Refused Claim

The system cannot say:

- analog attention has been proven
- softmax has been moved to analog
- value mixing has been moved to analog
- token accuracy has been measured
- a pretrained foundation model has been simulated
- silicon behavior has been calibrated
- board latency or board power has been measured
- the design is ready for tapeout

## Next Handoff

The calibrated attention replay now exists as a separate proof page.

The next proof is to use those calibrated residuals in the placement and governor path. A layer should not be marked analog-friendly just because a simulator can run it. The system should ask a stricter question: after calibration on separate inputs, does the held-out residual stay low enough for the model path that will consume it? CrossSim currently passes that check on this fixture. AIHWKIT currently does not.
