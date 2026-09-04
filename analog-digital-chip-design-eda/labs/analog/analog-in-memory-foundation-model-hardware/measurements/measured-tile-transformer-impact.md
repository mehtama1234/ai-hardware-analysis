# Measured Tile Transformer Impact

This experiment takes the residual from `analog-nonideality-stack.csv` and uses it as the analog tile error source inside a small transformer block. The question is no longer whether one tile output is close to one dot product. The question is whether that measured tile error can enter attention, MLP, logits, and the residual stream without changing the model decision too much.

```text
measured_tile_residual: 0.09000
measured_tile_residual_q8: 12
hidden: 24
context: 12
trials: 40
```

## Results

| policy | qkv | scores | out proj | mlp | logits | scale | state error | attention error | mlp error | logit error | attention flip | token flip | decision | reason |
| --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| all_digital_reference | digital | digital | digital | digital | digital | 0.00 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | digital_reference | reference_path |
| measured_fixed_projection_tile | analog | digital | analog | analog | digital | 0.40 | 0.0450 | 0.0652 | 0.0637 | 0.0436 | 0.1250 | 0.1750 | analog_path | measured_tile_within_budget |
| measured_projection_stressed_tile | analog | digital | analog | analog | digital | 1.00 | 0.1125 | 0.1619 | 0.1594 | 0.1087 | 0.1750 | 0.2000 | digital_fallback | attention_selection_too_sensitive |
| measured_attention_scores_analog | analog | analog | analog | analog | digital | 0.65 | 0.0783 | 0.1166 | 0.1069 | 0.0762 | 0.1750 | 0.1250 | digital_fallback | attention_selection_too_sensitive |
| measured_logits_analog | analog | digital | analog | analog | analog | 0.65 | 0.0732 | 0.1057 | 0.1035 | 0.0948 | 0.1500 | 0.2000 | digital_fallback | token_choice_too_sensitive |

## First-Principles Reading

A tile residual is not automatically a model residual. The tile error first changes Q, K, V, output projection, or MLP vectors. Those changed vectors then pass through attention selection, value mixing, residual addition, nonlinear activation, and logits. Some errors shrink. Some errors line up with sensitive decisions and grow.

The fixed-projection case is the useful analog target. It sends Q/K/V, output projection, and MLP matvecs through the measured tile model while keeping attention scores and logits digital. That is the cleanest claim because trained weights are resident and the digital side still owns selection and token choice.

The stressed-tile case uses the same placement but spends the full measured residual. If state error crosses the budget, the right conclusion is not that analog compute failed everywhere. The right conclusion is narrower: this tile state should not serve this model path without calibration, correction, or digital fallback.

The analog-attention case changes the object. Attention scores choose changing memory. A small score movement can change which token is selected. That is why attention top-flip rate is a first-class metric, not an afterthought.

The analog-logits case changes the final ranking. Logit RMS error is incomplete because generation depends on rank and probability movement. A logits accelerator must prove that it preserves the choices the sampler will see.

The control-plane rule is simple: the scheduler may choose analog for a class of operations, but the governor must judge the measured state error, attention selection movement, and token-choice movement before the result is trusted.
