# Multi-module local qualification decision

The joint ADC12 replay covers 3 GPT-2 modules and fails the provisional task-quality screen at 0.9524 teacher-forced argmax agreement, while preserving 3/4 exact generations.

This is a bounded negative local result. Per-module disjoint calibration, governed fallback tracing, and modeled multi-module cost accounting are now complete locally. The cost coefficients are assumptions, not measurements, and physical authorization remains closed.

The package contains `multimodule_runtime_trace.json` and `multimodule_cost_trace.jsonl`. Every vector is routed to digital fallback because the joint ADC12 quality gate fails; no analog execution is authorized.
