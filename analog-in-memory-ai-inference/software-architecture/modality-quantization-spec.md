# Modality-Aware Quantization Spec

Start from the [Connected System Map](connected-system-map.html). This specification uses the same contract: object, constraint, design move, evidence, allowed claim, refused claim, and next handoff.

## Purpose

Quantization sensitivity cannot be judged with one generic accuracy number.

The shared engine can test lower precision, analog noise, and protected layers. But each modality needs its own metric and failure definition. The product should ask what the model does before it decides what "safe quantization" means.

```text
model graph
  -> workload profile
  -> modality adapter
  -> task metric adapter
  -> precision trial
  -> analog-error trial
  -> per-layer sensitivity
  -> recommendation
```

## Required Workload Profile

Each quantization run must include:

- modality
- task type
- primary metric
- secondary metric
- primary failure cost
- calibration dataset description
- target device profile

Example:

```json
{
  "modality": "audio",
  "task_type": "wake_word",
  "primary_metric": "false_reject_rate",
  "secondary_metric": "false_accept_rate",
  "primary_failure_cost": "missed_keyword",
  "calibration_dataset": "noisy speech windows, 30 minutes",
  "target_profile": "wearable"
}
```

## Modality Adapters

### Audio

Use cases:

- wake-word detection
- event detection
- simple voice command classification

Metrics:

- false accept rate
- false reject rate
- accuracy under noise
- latency per audio window

Sensitive regions:

- first feature extraction layers
- small-signal layers near decision threshold
- final classifier

Risk:

Small numeric shifts can turn a quiet or noisy signal into the wrong decision.

Recommendation style:

```text
INT8 is safe across most layers. Keep the first feature layer and final classifier at INT8. Do not approve INT4 until false accepts and false rejects are checked under noisy input.
```

### Vision Classification

Use cases:

- image classification
- defect classification
- scene classification

Metrics:

- top-1 accuracy
- top-5 accuracy
- per-class accuracy drop
- confusion changes

Sensitive regions:

- first convolution
- final classifier head
- layers after aggressive downsampling

Risk:

Average accuracy can hide one class getting worse.

Recommendation style:

```text
INT4 is a candidate for middle convolution blocks. Keep the first convolution and classifier head at INT8 until per-class drops are reviewed.
```

### Object Detection

Use cases:

- person detection
- defect localization
- smart camera event detection

Metrics:

- mAP
- recall
- box quality
- confidence threshold movement

Sensitive regions:

- detection heads
- small-object paths
- confidence score layers

Risk:

The model may still classify well but miss boxes, shift boxes, or lower confidence scores.

Recommendation style:

```text
Do not judge this model with top-1 accuracy. Measure recall and box quality after quantization, especially for small objects and low-confidence detections.
```

### Robotics Perception

Use cases:

- obstacle detection
- sensor fusion
- navigation support
- local decision support

Metrics:

- latency
- output jitter
- worst-case error
- safety margin
- rare-case failure count

Sensitive regions:

- fusion gates
- attention blocks
- final planning or control-support heads

Risk:

Average accuracy can look acceptable while rare outputs become unstable.

Recommendation style:

```text
Keep safety-relevant output heads at higher precision. Quantization approval requires latency and jitter checks, not only average accuracy.
```

### Industrial Anomaly Detection

Use cases:

- fault detection
- vibration anomaly
- machine health monitoring
- rare defect detection

Metrics:

- anomaly recall
- false negative rate
- false positive rate
- threshold drift

Sensitive regions:

- bottleneck embeddings
- reconstruction heads
- anomaly scoring layers

Risk:

Rare fault examples may be underrepresented in calibration data. A small numeric shift can hide the event that matters most.

Recommendation style:

```text
Do not approve lower precision from average accuracy alone. Check rare-event recall and threshold movement after quantization.
```

### Health Wearable

Use cases:

- physiological signal classification
- event detection
- trend monitoring

Metrics:

- sensitivity
- specificity
- false alarm rate
- missed-event rate
- behavior across users and signal quality

Sensitive regions:

- first signal-processing layers
- temporal aggregation layers
- final event head

Risk:

Signals may be small, noisy, and user-dependent. A model can work on average while failing for weaker signals.

Recommendation style:

```text
Keep first signal layers and final event layers protected. Require checks across users, motion noise, and weak-signal cases.
```

### Edge LLM

Use cases:

- small language model inference
- local assistant
- retrieval support
- summarization

Metrics:

- perplexity
- task score
- token latency
- output-logit stability
- memory and KV-cache pressure

Sensitive regions:

- attention projections
- output logits
- normalization-adjacent layers
- KV-cache handling

Risk:

Token quality can degrade even when simple operator coverage looks good.

Recommendation style:

```text
Treat attention and output logits as sensitive. Measure quality and token latency, not only matrix coverage or TOPS/W.
```

## API Shape

```text
POST /analyses/{analysis_id}/quantize
```

Request:

```json
{
  "modality": "vision",
  "task_type": "object_detection",
  "primary_metric": "recall",
  "primary_failure_cost": "missed_object",
  "precision_trials": ["INT8", "INT4_selective", "INT4_all"],
  "analog_error_model": "estimated",
  "calibration_dataset_id": "calib-set-001"
}
```

Response:

```json
{
  "status": "estimated",
  "modality": "vision",
  "task_metric": "recall",
  "baseline": 0.921,
  "trials": [
    {
      "precision": "INT8",
      "metric": 0.918,
      "risk": "low"
    },
    {
      "precision": "INT4_selective",
      "metric": 0.904,
      "risk": "medium"
    },
    {
      "precision": "INT4_all",
      "metric": 0.861,
      "risk": "high"
    }
  ],
  "layer_recommendations": [
    {
      "layer_id": "detector.head",
      "recommendation": "keep INT8",
      "reason": "detection head affects recall and confidence thresholds"
    }
  ]
}
```

## Acceptance Criteria

- The user must choose or confirm modality before interpreting quantization.
- The report must show the task metric, not only generic accuracy.
- The report must show whether results are estimated, simulated, or measured.
- The report must identify sensitive layers.
- The report must recommend precision per layer or block.
- The report must explain the primary failure risk in plain language.
