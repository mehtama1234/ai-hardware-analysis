# Sky130 Transistor-Switched Capacitor DAC

- status: `transistor_switched_capacitor_dac_incomplete_or_half_lsb_failed`
- codes measured: `0` of `2`
- half-LSB target V: `5.625000000e-02`
- maximum settling error V: not measured
- all measured codes within half-LSB: `False`
- measured code order monotonic: `False`

## First-Principles Reading

The capacitor array stores charge, but the MOS switches determine how quickly charge arrives and how much error the sampling edge leaves behind. This fixture replaces the ideal switch boundary with Sky130 NMOS/PMOS devices and keeps the code-dependent top-plate measurement unchanged.

A pass here would establish a transistor-switched DAC boundary, not a complete SAR. A failure means the switch sizing, timing, common-mode range, or capacitor ratio must be repaired before coupling the DAC to the comparator.

## Refused Claim

does not prove capacitor mismatch statistics, reference loading across a full SAR, comparator coupling, extracted layout, board behavior, or silicon
