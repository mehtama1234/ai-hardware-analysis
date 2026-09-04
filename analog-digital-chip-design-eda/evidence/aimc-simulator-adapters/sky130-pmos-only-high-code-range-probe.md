# Sky130 PMOS-Only High-Code Range Probe

- status: `pmos_only_high_code_converges_but_violates_range_and_spacing`
- source acquisition: `long`
- timeout budget: `180 s`

At the nominal `1.2 V` source and `1.5 V` reference, code `14` measured
`2.466102 V` and code `15` measured `2.473010 V`. Both comparator signs were
correct, but the spacing was only `6.908 mV` versus the required `56.25 mV`,
and both values exceeded the `1.8 V` supply.

With a lower `0.6 V` source and `0.9 V` reference, code `15` still measured
`2.315697 V`. Scalar common-mode remapping therefore does not close the
headroom problem.

This is nominal high-code evidence only. It does not prove a complete SAR,
PVT/mismatch/noise yield, extracted layout, board behavior, or silicon.
