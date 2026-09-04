# Transformer Partition Simulator Results

Run:

```bash
python3 python/transformer_partition_simulator.py
```

The simulator compares four hardware policies inside one small transformer block.

```text
policy,qkv,scores,value_mix,out_proj,mlp,logits,state_error,attention_error,mlp_error,logit_error,top_flip_rate,token_flip_rate,top3_overlap,attention_probability_movement,logit_probability_movement,decision,reason
all_digital_reference,digital,digital,digital,digital,digital,digital,0.0000,0.0000,0.0000,0.0000,0.0000,0.0000,1.0000,0.0000,0.0000,digital_reference,reference_path
fixed_projection_analog,analog,digital,digital,analog,analog,digital,0.0694,0.1008,0.0973,0.0674,0.1250,0.1250,0.9271,0.0000,0.0432,analog_path,allowed
analog_logits_experiment,analog,digital,digital,analog,analog,analog,0.0694,0.1008,0.0973,0.0743,0.1250,0.0625,0.9063,0.0000,0.0477,analog_path,allowed
analog_attention_experiment,analog,analog,analog,analog,analog,digital,0.0816,0.1333,0.1095,0.0842,0.2812,0.1250,0.8542,0.0634,0.0571,digital_fallback,fallback_attention_selection
stale_unhealthy_tiles,analog,digital,digital,analog,analog,digital,0.2174,0.3165,0.3034,0.2089,0.2500,0.1250,0.8229,0.0000,0.1337,digital_fallback,fallback_state_error
```

The first useful result is that fixed trained projections can survive the toy analog boundary. Q/K/V, attention output, and MLP projections use analog matvecs, while score computation, softmax, value mixing, and logits remain digital. The mean block-state error stays below the budget. Attention top-token selection and final token choice move sometimes, but they stay inside the stated tolerance for this toy run.

The second result is that analog logits are a separate claim from analog hidden projections. In this run, the analog vocabulary projection still stays inside the token-choice budget. That does not prove it is always safe. It says the right measurement is rank behavior: top token flips, top-3 overlap, and probability movement, not only logit RMS error.

The third result is that analog attention is a different and harder claim. The top-attended token flips in about 28 percent of trials. That triggers fallback because attention is selecting changing memory. The relevant error is not only dot-product error; it is whether the same memory receives attention.

The fourth result is that stale and unhealthy tiles should not be hidden behind average error. With old calibration and weak tiles, state error rises beyond the budget. The correct behavior is digital fallback, not a stronger analog claim.

The lab therefore supports the partition rule in the research map: analog arrays are best treated as resident-weight projection engines, while digital logic owns memory addresses, masks, softmax, residual control, normalization, calibration decisions, and fallback.
