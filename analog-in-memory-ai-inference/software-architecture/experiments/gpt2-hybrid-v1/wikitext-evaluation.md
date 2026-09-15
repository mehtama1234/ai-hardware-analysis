# GPT-2 projection sensitivity on sampled WikiText

This evaluation broadens the authored four-sentence smoke test to 4,096
next-token prediction positions spread across the WikiText-2 raw test split.
It measures the whole model's response when `transformer.h.0.mlp.c_fc` uses
the existing provisional tiled projection. It does not execute analog hardware.

## Frozen protocol

- Dataset: [Salesforce/WikiText](https://huggingface.co/datasets/Salesforce/wikitext/tree/b08601e04326c79dfdd32d625aee71d232d685c3),
  `wikitext-2-raw-v1`, revision `b08601e04326c79dfdd32d625aee71d232d685c3`.
  The publisher's card declares CC BY-SA 4.0; the package preserves that card.
- GPT-2 revision: `607a30d783dfa663caf39e06633721c8d4cfcd7e`.
- Calibration: 16 evenly spaced, disjoint 129-token windows from **train**.
  Only these activations determine the projection's range.
- Evaluation: 32 evenly spaced, disjoint 129-token windows from **test**.
  Each window starts with fresh context and scores 128 next-token targets.
- Rows are joined with a newline before tokenization, without added special
  tokens. The package records complete token selections, split hashes and
  selection offsets. Selection does not depend on model outputs.
- Original controls: ideal tiled projection must have maximum logit error below
  0.001. The v2 control is described below; restoring native execution must
  reproduce baseline logits exactly in every window in both versions.
- Candidates: weight8/DAC10 with ADC8, ADC12, and ADC12 plus normalized read
  noise of 0.001. Noise uses one fixed seed, 8181.
- Screening thresholds inherited from the earlier experiment: NLL increase
  at most 0.05 nats/token and teacher-forced argmax agreement at least 99%.
  These are provisional engineering thresholds, not a user task SLA.

## Reproduce and verify

From `software-architecture`, with GPT-2 already cached:

```bash
python3 scripts/run_gpt2_wikitext_projection.py --output experiments/gpt2-hybrid-v1/runs/new-wikitext-run
python3 scripts/check_gpt2_wikitext_projection.py experiments/gpt2-hybrid-v1/runs/new-wikitext-run
```

The runner downloads the pinned train/test Parquet files and card. It snapshots
source before numerical execution and refuses an existing output directory.
Per-window rows are flushed as they finish; a partial row file is not a completed
evaluation. `result.json` and `manifest.json` are written only after controls pass.
The checker verifies hashes, split separation, window accounting, aggregate
metric arithmetic, trace counts and physical-claim restrictions.

## Interpretation limits

This is sampled, short-context encyclopedia language modeling, not a full
WikiText perplexity score, production workload, generation benchmark or proof
that the data was absent from GPT-2 pretraining. Argmax agreement compares the
candidate to baseline; it does not measure agreement with the ground-truth token.
Perplexity is computed from token-weighted cross entropy on the selected targets.
The fixed noise seed does not establish variation across devices or seeds.

The numerical array model still lacks circuit-calibrated converter noise,
transfer behavior, settling, programming error and drift. CPU emulation times
are diagnostic runtime only. A passing quality screen cannot authorize analog
placement or establish energy/latency benefit.

The saved run directory is `runs/20260909-wikitext-sampled/`.

## First run: rejected by its control

All 128 variant/window rows completed, covering 4,096 predictions per variant.
The runner then rejected the evaluation because ideal tiled execution exceeded
the predeclared maximum absolute logit-error threshold in windows 21 and 23
(zero based). Their errors were 0.003159 and 0.001877 against a limit of 0.001.
Ideal argmax agreement was 100% overall and aggregate NLL difference was about
−8.2e−8 nats/token, but those observations do not override the frozen control.

`rejection_diagnosis.json` preserves source hashes and the failed rows. There
is intentionally no accepted `result.json` or `manifest.json`; the success
checker cannot accept this directory. The raw candidate rows are diagnostic:

| Candidate | NLL increase, nats/token | Baseline argmax agreement |
| --- | ---: | ---: |
| ADC8 | 0.068642 | 82.7393% |
| ADC12 | 0.001207 | 98.9014% |
| ADC12 with noise 0.001 | 0.014274 | 93.4326% |

None of these raw summaries meets the inherited joint screen. They must not be
reported as a qualified benchmark conclusion while the control is rejected.
Next, inspect numerical accumulation and logit scaling on the two failing
windows, validate the ideal control, and rerun under a protocol frozen before
the new run. Do not retroactively relax this run's threshold.

## Numerical diagnosis and v2 protocol

`runs/20260909-wikitext-numerics/result.json` compares native FP32, tiled FP32,
dense FP64 cast to FP32, and tiled FP64 cast to FP32 on both failed contexts.
The FP32 tiled projection differs from native by at most 1.91e−6. Dense and
tiled FP64 produce identical reported metrics after casting, and both also
differ from native. These observations support an accumulation-rounding
explanation rather than missing tiles or incorrect weights.

For the original FP32 tiling, maximum log-probability error is 0.000277 and
0.000175 in the two contexts, respectively. Their mean target NLL changes are
−5.20e−7 and −1.20e−6 nats/token, with all token decisions unchanged. Much of
the raw-logit difference cancels under softmax normalization. Raw logit error
alone therefore confounds probability changes with a common logit offset.

The v2 protocol is frozen before a new full run. It keeps the native FP32 model,
array model, dataset windows, and candidate quality thresholds unchanged. It
requires all of these ideal controls in **every** window:

1. Projection output agrees with native at absolute and relative tolerances
   of 1e−5, independently of downstream output behavior.
2. Maximum absolute log-probability error across every vocabulary entry is
   below 0.001. This bounds each probability ratio by exp(0.001), approximately
   a 0.1% relative change, while ignoring common logit offsets.
3. Absolute mean target NLL change is below 1e−5 nats/token.
4. All teacher-forced argmax choices match, and all tensors are finite.
5. Restored native execution reproduces logits exactly.

Log probabilities for the numerical control are calculated in FP64 from the
FP32 model logits. The model itself is unchanged. Tests accept a per-position
common offset and reject changed probabilities, incorrect projection outputs,
changed decisions and nonfinite values. This is an explicit protocol revision
informed by the failed run; it does not retroactively accept that run, constitute
independent unseen-data validation, or change candidate quality acceptance.

The v2 run directory is `runs/20260909-wikitext-probability-control-v2/`.
The run completed successfully with exit code zero. Verification and evidence
joining use:

```bash
python3 scripts/check_projection_numerical_control.py
python3 scripts/check_gpt2_wikitext_projection.py experiments/gpt2-hybrid-v1/runs/20260909-wikitext-probability-control-v2
python3 scripts/build_gpt2_evidence_decision.py --quality experiments/gpt2-hybrid-v1/runs/20260909-wikitext-probability-control-v2 --output experiments/gpt2-hybrid-v1/decisions/new-decision
```

The decision builder checks benchmark artifacts, the earlier compiled-runtime
manifest, current physical source hashes and extracted-netlist identity. It
copies the inputs into a new decision directory, preserving the current
physical-pointer contents as a snapshot. It explicitly distinguishes the
WikiText numerical workload from the earlier compiler fixture and circuit
tests. It cannot authorize analog execution from a numerical screen.

### Completed v2 result

All 32 contexts passed the numerical controls and exact native fallback.
Across them, maximum projection error was 2.86e−6, maximum log-probability
error was 0.000277, and maximum absolute per-context mean target NLL change
was 1.32e−6. All 128 per-variant/window quality rows exactly reproduced the
first experiment's NLL, argmax agreement and raw-logit-error measurements.

| Candidate | NLL increase, nats/token | Baseline argmax agreement | Joint screen |
| --- | ---: | ---: | --- |
| ADC8 | 0.068642 | 82.7393% | Fail |
| ADC12 | 0.001207 | 98.9014% | Fail |
| ADC12 with noise 0.001 | 0.014274 | 93.4326% | Fail |

The native baseline sampled perplexity is 54.93498. Every variant processed
4,128 input vectors and scored 4,096 next-token targets. DAC and ADC clipping
counters were zero for every variant. The quality loss is therefore not
explained by clipping under this numerical profile; quantization and assumed
noise remain relevant causes to investigate.

The package checker verified 10 hashes and 128 rows. Four mutation checks
rejected changed metric arithmetic, a failing numerical measurement paired
with a true pass flag, unsupported analog authorization and modified source.

The [combined decision package](decisions/20260909-wikitext-v2/README.md)
retains native digital execution. Its 10 artifact hashes were verified.
No nonideal candidate passes the provisional joint screen; physical electrical
qualification, actual target execution and matched timing/energy evidence also
remain incomplete. This closes the sampled numerical evaluation and evidence
join, not the overall model-to-hardware goal.

## Next experiment implementation: observed ADC range

`scripts/calibrated_adc_projection.py` provides a separate numerical projection
whose ADC ranges use maximum observed quantized training partials with fixed
10% headroom, capped by the conservative bound. Ranges are frozen before
evaluation; unexcited tiles retain the conservative range. Evaluation does not
refit them, and out-of-range partials remain visible in clipping counters.
Five small-tensor tests cover those properties, ideal execution, invalid inputs
and calibration-record isolation.

The separate [GPT-2 validation comparison](adc-range-validation.md) now evaluates
this implementation with frozen training calibration. Calibrated ADC12 passes
its provisional validation screen and the subsequent disjoint-context test
screen. It is not part of the two earlier WikiText runs and remains a noiseless
numerical profile without general task or physical qualification.
Its hardware obligations include programmable gain or
reference ranges and their switching/settling cost. The noise fraction remains
relative to the selected range; shrinking the range does not establish a
smaller physical noise floor. These assumptions must be resolved before using
an improved numerical result to set converter requirements.
