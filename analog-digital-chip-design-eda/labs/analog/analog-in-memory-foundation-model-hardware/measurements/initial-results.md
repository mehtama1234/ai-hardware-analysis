# Initial Results

Run:

```bash
python3 ../python/analog_matmul.py
```

Expected reading:

- More ADC bits should usually reduce output error until conductance noise and DAC precision dominate.
- More drift should increase output error unless calibration is added.
- The tiny transformer MLP projection should have larger error than one matrix-vector multiply because error passes through two analog boundaries and a nonlinear activation.

The next measurement should add calibration. Measure the analog output for known inputs, estimate a per-output gain and bias, and apply that correction digitally before the value enters the next model layer.

## Calibration And Energy

Run:

```bash
python3 ../python/calibration_and_energy.py
```

Expected reading:

- Calibration should reduce stable gain and offset error.
- Calibration should not remove random conductance noise or quantization loss.
- ADC energy should grow quickly with bit count in the relative model.
- The useful design question is not the lowest matrix error by itself. It is the lowest error that still leaves a system-level energy advantage.

The energy model uses relative units. It is not claiming a process-node number. It teaches the scaling shape: array compute can be cheap while ADCs, DACs, digital accumulation, and movement become the real boundary.

## Prefill And Decode Estimator

Run:

```bash
python3 ../python/prefill_decode_estimator.py
```

Expected reading:

- Prefill and decode should be measured separately.
- Higher ADC and DAC precision makes analog projection less favorable because conversion cost rises.
- Decode must pay KV-cache movement as the generated sequence grows.
- A design can improve dense projection energy and still struggle if decode is dominated by cache traffic and small-batch scheduling.

The estimator uses relative units. It is not a process-node energy claim. It is a check on the first-principles argument: analog compute is useful when saved weight movement and multiply work are larger than converter, accumulation, correction, and memory costs.

## Attention And KV Cache

Run:

```bash
python3 ../python/attention_kv_cache_model.py
```

Expected reading:

- KV cache size grows with context length even when the active attention window is capped.
- Full-context decode increases read bytes per generated token as the context grows.
- Near-cache compute can reduce dot-product cost, but it does not remove softmax, masking, cache writes, or cache reads.
- Analog cache state is the hardest claim because it must also prove write quality, retention, refresh, and read disturbance.

The model uses relative units. It is meant to separate three claims that are often mixed together: analog projections, attention dot products near memory, and analog storage of changing token state.

## Attention Score Noise

Run:

```bash
python3 ../python/attention_score_noise.py
```

Expected reading:

- Small score noise is more dangerous when the top scores are close.
- The useful measurement is not only score error. It is top-token flip rate, probability movement, and output-vector error.
- A score error can be small in RMS terms while still changing which memory vector receives the most attention.
- Larger margins make the same noise less damaging.

This experiment is a model-behavior check. It asks whether analog score error changes the memory read, not only whether the dot product is numerically close.

## Tiny Transformer Block Noise

Run:

```bash
python3 ../python/tiny_transformer_block_noise.py
```

Expected reading:

- Projection noise and attention score noise should be measured together.
- The important number is final block-state error, because that is what enters the next block.
- Attention error and MLP error can interact through the residual state.
- A low top-token flip rate does not prove safety if probability movement and MLP error still move the hidden state.

This experiment is still a toy model. Its value is that it measures the same object a real hybrid accelerator must preserve: the hidden state after attention, MLP, and residual addition.

## Multi-Layer Error Drift

Run:

```bash
python3 ../python/multilayer_error_drift.py
```

Expected reading:

- One-layer error does not describe a deep model.
- Stable bias and random noise should be reported separately.
- Bias can create persistent state movement across depth.
- Calibration matters because it removes stable gain and offset before they become repeated state drift.

The experiment is a toy residual stack. Its value is conceptual: it makes repeated hardware error visible as a state-history problem.

## Calibration Schedule

Run:

```bash
python3 ../python/calibration_schedule.py
```

Expected reading:

- More calibration samples reduce fit noise but increase overhead.
- Shorter intervals reduce stale drift but require more calibration events.
- Longer intervals reduce overhead but raise worst-case residual error before the next calibration.
- The useful design object is the interval that keeps residual error below model tolerance without spending too much runtime on measurement.

The model uses relative units. It is a schedule check, not a process-node claim.

## Tile Health Monitor

Run:

```bash
python3 ../python/tile_health_monitor.py
```

Expected reading:

- Full fixed recalibration should minimize stale drift but spend the most measurement work.
- Selective recalibration should reduce worst-column error with much less calibration work.
- Occasional full sweeps should catch columns the noisy health probe misses.
- The right policy depends on tolerated worst-column error, not only mean error.

The model is a controller sketch. It treats calibration as a limited measurement budget that should be spent where error is growing.

## Serving Policy

Run:

```bash
python3 ../python/serving_policy.py
```

Expected reading:

- Prefill should often choose analog because projection reuse is high.
- Small-batch long-context decode can choose digital because cache movement and control dominate.
- Batched decode can choose analog when batch reuse pays for conversion.
- Calibration due and poor tile health can force a digital fallback even when projection work looks analog-friendly.

The model is a scheduler sketch. It turns analog acceleration into a runtime decision instead of a fixed property of the chip.

## Hybrid Control Plane

Run:

```bash
python3 ../python/hybrid_control_plane.py
```

Expected reading:

- The chip should produce a request trace, not only an average speedup.
- Each row should say whether the request used analog, batched analog decode, or digital fallback, and why.
- Long-context decode can stay digital even when analog projection math is cheap, because cache movement is part of the request.
- Stale calibration, weak tiles, or missing resident weights should cause fallback before the model state is damaged.

The model is a control-plane sketch. It treats the scheduler, tile-health monitor, converter boundary, calibration age, KV-cache pressure, and digital fallback as one execution decision.

## Tile Readout Boundary

Run:

```bash
python3 ../python/tile_readout_boundary.py
```

Expected reading:

- The ADC code is a measured number, not the model value.
- Zero-code removal handles fixed offset at the converter/tile boundary.
- Gain and bias correction move the measured value back toward the digital reference scale.
- Saturation, stale calibration, high residual, and disabled tiles should force fallback.

Current output:

```text
tile_readout_boundary
case,centered_adc,scaled,corrected,valid,fallback,reason
centered_adc_with_unit_gain,32,32,32,1,0,ok
gain_and_bias_correction,32,48,43,1,0,ok
disabled_tile_fallback,32,32,32,0,1,tile_disabled
residual_fallback,32,32,32,0,1,residual_high
stale_calibration_fallback,32,32,32,0,1,calibration_stale
high_saturation_fallback,4095,4095,2047,0,1,saturated_high
low_saturation_fallback,-255,-255,-2048,0,1,saturated_low
```

The model mirrors the RTL readout block. Its value is conceptual: it makes the boundary visible before synthesis. Analog current becomes an ADC code; the digital side decides whether that code is corrected enough to enter model state.

## Micro-Tile Execution Trace

Run:

```bash
python3 ../python/micro_tile_execution_trace.py
```

Expected reading:

- Placement and acceptance are separate decisions.
- A fixed projection can be allowed to try analog and still fall back after readout.
- Hybrid attention work is not sampled by the direct tile readout path.
- Digital-only work never reaches the analog readout boundary.

Current output:

```text
micro_tile_execution_trace
case,op,placement,placement_reason,readout_reason,corrected,final_path,final_reason
qkv_analog_accepted,qkv,analog,fixed_weight_analog,ok,32,analog_accepted,readout_valid
qkv_residual_fallback,qkv,analog,fixed_weight_analog,residual_high,32,digital,readout_residual_high
qkv_disabled_tile_fallback,qkv,analog,fixed_weight_analog,tile_disabled,32,digital,readout_tile_disabled
attention_hybrid_review,attention_score,hybrid,hybrid_needs_evidence,not_sampled,0,hybrid_review,hybrid_review
softmax_digital_rule,softmax,digital,digital_rule,not_sampled,0,digital,digital_rule
missing_weight_fallback,qkv,digital,missing_weights,not_sampled,0,digital,missing_weights
```

The model is the Python counterpart to the integrated RTL controller. It makes the end-to-end control rule readable before looking at Verilog: choosing analog is permission to try the tile; accepting analog is a later decision based on the corrected measurement.

## Generated RTL Micro-Tile Vectors

Run:

```bash
python3 ../python/generate_micro_tile_rtl_vectors.py
```

Current output:

```text
wrote ../../digital/aimc-control-plane-rtl/generated_micro_tile_cases.vh
wrote measurements/generated-micro-tile-rtl-vectors.csv
wrote measurements/generated-micro-tile-rtl-vectors.md
```

The generated include is consumed by `aimc_micro_tile_controller_tb.v`. This connects the analog-side trace to the RTL checker: when the analog model says a stale tile should fall back and request recalibration, the Verilog testbench checks the same counter and action. When repeated residual failures mean correction is no longer enough, the Verilog testbench checks that `tile_health_action` moves to disable.

The generated Markdown table is the review surface for the same sequence. The generated CSV is the machine-readable record of input conditions, expected path, reason code, counters, and health action.

Run the closed-loop checker from the RTL lab:

```bash
python3 check_generated_micro_tile_trace.py
```

Current output:

```text
PASS generated_micro_tile_trace
cases 8
csv ../../analog/analog-in-memory-foundation-model-hardware/measurements/generated-micro-tile-rtl-vectors.csv
```

This is stronger than a handwritten test log. The checker regenerates the analog-derived vectors, runs the Verilog testbench, parses the printed hardware trace, and compares every expected path, reason, counter, and health action against the CSV.

## Transformer-Layer Trust Trace

Run:

```bash
python3 ../python/transformer_layer_trust_trace.py
```

Expected reading:

- Q, K, V, output, and MLP projections are plausible analog candidates.
- Each candidate still needs a readout decision before the layer can use the result.
- A failed readout returns the digital projection rather than letting bad analog state flow forward.
- The final check is hidden-state error, not just projection error.

Current output:

```text
transformer_layer_trust_trace
dim,8
context,5

op,placement,readout,final_path,relative_error
q_projection,analog,ok,analog_accepted,0.0260
k_projection_0,analog,ok,analog_accepted,0.0127
v_projection_0,analog,ok,analog_accepted,0.0122
k_projection_1,analog,ok,analog_accepted,0.0219
v_projection_1,analog,ok,analog_accepted,0.0209
k_projection_2,analog,ok,analog_accepted,0.0112
v_projection_2,analog,residual_high,digital_fallback,0.0000
k_projection_3,analog,ok,analog_accepted,0.0117
v_projection_3,analog,ok,analog_accepted,0.0148
k_projection_4,analog,ok,analog_accepted,0.0204
v_projection_4,analog,ok,analog_accepted,0.0184
output_projection,analog,ok,analog_accepted,0.0182
mlp_up,analog,ok,analog_accepted,0.0246
mlp_down,analog,calibration_stale,digital_fallback,0.0000

layer_summary
attention_top_clean,2
attention_top_traced,2
attention_probability_movement,0.0035
final_hidden_state_relative_error,0.0071
```

The important result is not the specific number `0.0071`. The important result is the measurement shape. The trace records every analog candidate, the readout reason, the final path, and the layer-level hidden-state error after fallback. That is the trust-boundary idea applied to the value a transformer actually passes forward.

## Error Budget Ledger

Run:

```bash
python3 ../python/error_budget_ledger.py
```

Expected reading:

- Projection residual is a local measurement at the analog boundary.
- Attention probability movement and final hidden-state error are model-facing measurements.
- Stable bias can matter more than similar-sized random noise because it pushes values in a repeated direction.
- Fallback should be judged by the hidden-state error it prevents, not only by how many analog attempts it rejects.

Current output:

```text
error_budget_ledger
hidden,12
context,6
trials,20

case,mean_projection_residual,max_projection_residual,mean_fallbacks_per_layer,attention_top_flip_rate,attention_probability_movement,attention_output_error,final_hidden_state_error
clean_reference,0.0000,0.0000,0.00,0.0000,0.0000,0.0000,0.0000
dac_quantization_only,0.0336,0.1242,0.00,0.0000,0.0096,0.1047,0.0409
conductance_noise_only,0.0303,0.0490,0.00,0.1000,0.0134,0.0519,0.0226
adc_readout_only,0.0407,0.1594,0.00,0.0000,0.0100,0.1492,0.0551
stable_bias_only,0.0628,0.2388,0.00,0.0500,0.0121,0.2549,0.1175
attention_score_noise_only,0.0000,0.0000,0.00,0.1000,0.0599,0.0846,0.0203
combined_no_fallback,0.0897,0.3366,0.00,0.1000,0.0644,0.3347,0.1474
combined_with_fallback,0.0888,0.3187,1.55,0.1000,0.0644,0.1838,0.0696
```

The concrete lesson is that local projection error is not enough. `stable_bias_only` has a mean projection residual of `0.0628`, but it creates `0.1175` final hidden-state error. `attention_score_noise_only` has no projection residual, but still moves attention probabilities and flips the top attention target in some trials. The combined fallback case shows the value of the trust boundary: the analog attempts still happen, but the worst measured projections are refused before they damage the layer state.

## Tile Telemetry Policy

Run:

```bash
python3 ../python/tile_telemetry_policy.py
```

Expected reading:

- Accepted and fallback counters become runtime evidence.
- A tile should not be judged from one failure.
- Residual-heavy fallback means the tile is not correcting well enough.
- Stale fallback means the tile may be useful again after recalibration.
- Accepted rate is useful only when reason codes explain the failures.

Current output:

```text
tile_telemetry_policy
requests_per_tile,64

tile_id,attempts,accepted,fallback,accept_rate,residual_fallback,stale_fallback,action,reason
11,64,59,5,0.922,5,0,serve,accepted_readouts_dominate
12,64,46,18,0.719,18,0,disable,residual_fallbacks_are_repeated
13,64,36,28,0.562,28,0,disable,residual_fallbacks_are_repeated
14,64,50,14,0.781,4,10,recalibrate,calibration_evidence_is_stale
15,64,45,19,0.703,19,0,disable,residual_fallbacks_are_repeated
```

The lesson is that telemetry changes the design from a static accelerator into a managed physical system. The controller should not only say `analog` or `digital`. It should create evidence about which tiles deserve future analog work.
