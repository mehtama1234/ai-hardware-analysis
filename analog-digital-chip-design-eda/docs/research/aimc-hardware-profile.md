# AIMC Hardware Profile

This is the versioned architecture contract used by the mixed analog-memory,
digital-memory, and SRAM workload packages. It gives compiler and comparison
artifacts one stable target to name while the physical converter remains under
investigation.

- profile: `educational-hybrid-tile-v1`
- tile: `16 x 16`, `2`-bit cells, `4` weight slices, `24`-bit accumulation
- converter assumption: `4`-bit DAC, `6`-bit ADC, `0..1.8 V` nominal range
- SRAM contract: `64 KiB`, `32 bytes/cycle` read and write bandwidth
- calibration: startup, every `1024` inferences, and after a PVT change
- nominal PVT envelope: `-20 C` to `85 C` at `1.8 V`
- physical converter gate: `blocked_sar_source_common_mode`

The profile is a planning and simulator contract, not a claim that the current
Sky130 converter satisfies these values. Every workload contract and the shared
compiler package must reference this exact profile ID. The portfolio validator
rejects missing profiles, mismatched IDs, or malformed hardware fields.

Source artifact: `evidence/aimc-hardware-lab/hardware-profile-educational-hybrid-tile-v1.json`.
