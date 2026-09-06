# Sky130 Continuous SAR Sequenced Bottom Precharge

The earlier continuous candidate left all bottom plates floating during the
source-acquisition interval. A parallel ground-precharge device was rejected
because it injected charge into the retained state. This experiment instead
uses the existing low-side switch itself: it is turned on to ground during
the first 4 ns of each acquisition, opened for a 1 ns non-overlap interval,
and only then driven by the decision-dependent redistribution waveform.

This is the first test of a real phase-separated bottom-plate architecture.
The one-conversion diagnostic decodes `2→2` with legal DAC thresholds, but its
strict bottom-plate range is narrowly missed (`−140 µV` to `1.80051 V`). In a
five-conversion run with the historical reference profile, the state is
better controlled but the old calibration is no longer valid:
`0→3, 2→6, 4→6, 6→8, 7→8`.

With an experimentally tuned profile (`0.6, 0.3, 0.3, 0.7, 0.7`), the same
physical sequence reaches `2→2, 4→4, 6→6`, but the endpoints remain wrong
(`0→4, 7→6`). A second endpoint probe gives `0→1` and `7→6`; therefore
reference tuning alone has not established endpoint windows.

The change is retained as the leading architecture candidate, but it is not
accepted. It still needs endpoint-separable transfer, strict 0–1.8 V range,
all five correct conversions, and then PVT, mismatch/noise, extraction, and
layout evidence.

The 2 pF top-dummy follow-up is also rejected: it still reaches about `1.99 V`
and returns `0→4, 2→4, 4→5, 6→8, 7→8` under the tuned profile.

Evidence:

- `evidence/aimc-simulator-adapters/sky130-continuous-sequenced-precharge-single.json`
- `evidence/aimc-simulator-adapters/sky130-continuous-sequenced-precharge-full.json`
- `evidence/aimc-simulator-adapters/sky130-continuous-sequenced-precharge-ref06303707-full.json`
- `evidence/aimc-simulator-adapters/sky130-continuous-sequenced-precharge-ref015030307072-full.json`
- `evidence/aimc-simulator-adapters/sky130-continuous-sequenced-precharge-topdummy2-full.json`
