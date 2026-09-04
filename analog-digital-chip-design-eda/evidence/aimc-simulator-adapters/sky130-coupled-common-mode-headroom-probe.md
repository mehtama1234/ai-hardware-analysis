# Sky130 Coupled Common-Mode Headroom Probe

- status: `lower_common_mode_did_not_restore_endpoint_convergence`
- topology: `PMOS-only bottom-plate switch feeding the physical comparator`
- source: `0.6 V`
- reference: `0.9 V`
- code: `15`
- result: `timed out after 20 s`

Lowering the source/reference common-mode pair did not make the selected
high-code endpoint converge. This rejects scalar voltage remapping as the
repair. The next candidate must change endpoint initialization or the
charge-transfer ratio.

This is a negative diagnostic only. It does not prove SAR accuracy, PVT,
mismatch/noise yield, extracted layout, board behavior, or silicon behavior.
