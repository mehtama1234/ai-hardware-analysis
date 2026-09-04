# Sky130 Active Isolation Preamp Candidate

- status: `active_isolation_macro_candidate_failed_margin_or_runability`
- setting count: `4`
- case count: `8`
- measured case count: `8`
- timed-out case count: `0`
- passing setting count: `0`
- first passing setting: `None`
- best setting: `gain12_inverting_low_cin`
- best minimum abs preamp output diff V: `1.686660000e-02`
- output margin target V: `5.000000000e-04`
- accepted post-layout written: `False`

## First Principle

The passive frontend cannot push enough voltage into the preamp. The active-isolation idea is to read the frontend with a very small capacitance, make a larger differential voltage, and then let the existing preamp do its normal job.

This candidate is deliberately a macro. It answers the next design question before transistor sizing: how much isolated differential gain is enough, and does low input capacitance keep the frontend signal alive?

## Setting Summary

| setting | isolation gain | polarity | input cap fF | bias current uA | measured | sign pass | margin pass | min sense ratio | min output mV |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `unity_noninverting_low_cin` | `1.000` | `1` | `0.050` | `2.000` | `2` | `1` | `2` | `0.431373` | `1.414300` |
| `unity_inverting_low_cin` | `1.000` | `-1` | `0.050` | `2.000` | `2` | `1` | `2` | `0.431373` | `1.414300` |
| `gain4_inverting_low_cin` | `4.000` | `-1` | `0.050` | `8.000` | `2` | `1` | `2` | `0.431373` | `5.653500` |
| `gain12_inverting_low_cin` | `12.000` | `-1` | `0.050` | `24.000` | `2` | `1` | `2` | `0.431373` | `16.866600` |

## Refused Claim

does not prove a transistor isolation circuit, drawn layout, DRC/LVS, latch decision, SAR conversion, post-layout converter energy, or accepted converter evidence
