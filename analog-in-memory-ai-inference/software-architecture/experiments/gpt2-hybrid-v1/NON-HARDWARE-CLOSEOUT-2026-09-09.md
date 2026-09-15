# Non-hardware closeout

The software and numerical part of the hybrid-inference investigation is
closed at a reproducible checkpoint. The final decision remains **retain native
digital execution** until an analog target is qualified.

## Closed evidence

- Real, pinned `openai-community/gpt2` (124M) and pinned WikiText-2 data.
- First MLP projection mapped to 144 logical tiles with signed weight/DAC/ADC
  contracts and exact digital fallback.
- Training-calibrated finite-reference profile evaluated on 32 test contexts
  disjoint from 64 previously scored contexts (4,096 predictions).
- Finite-reference result: 99.4385% baseline next-token argmax agreement,
  +0.000603370 nats/token, 61 ADC clips and no DAC clips.
- Ideal arithmetic controls, exact restored digital fallback, source hashes,
  context exclusion and all 144 effective ADC bounds verified.
- Six result mutation checks reject false qualification, altered aggregates,
  stale ranges, relabeled splits and missing fallback evidence.
- Joined decision package is
  `decisions/20260909-finite-reference-holdout/`; its hashes and linked source
  paths were verified. It explicitly has no analog executor, physical array
  qualification, or matched latency/energy.

The nominal switched-reference DAC study is also documented in the sibling EDA
project. It establishes a monotonic candidate curve and maps finite reference
codes to the 144 tiles, but uses ideal resistors/drivers and assumed loads.
The repeated bank-sequence run covered 23/24 cases before the final 1 pF case
hit the 600-second simulator timeout. Its output and failed deck/logs remain
preserved; no complete settling claim is made.

## What is deliberately not closed

The numerical profile is noiseless and only covers one GPT-2 projection. It is
not a general task-quality claim. The extracted converter currently fails its
electrical margin requirement and lacks complete converter LVS. A promising
synthetic capacitance/drain-isolation topology passed single-cycle small-input
tests but failed one of eight repeated decisions, showing history-dependent
polarity. No physical analog array, silicon, board, or matched power/timing
measurement is available.

The remaining hardware work is therefore well-defined: resolve reset/history
behavior, implement the selected topology in layout, close extraction/DRC/LVS
and converter electrical qualification, bind array and converter errors to the
finite-reference model, then run the same workload on a real analog target and
measure total latency and energy against the digital baseline.

No additional software claim should be promoted until those boundaries change.
