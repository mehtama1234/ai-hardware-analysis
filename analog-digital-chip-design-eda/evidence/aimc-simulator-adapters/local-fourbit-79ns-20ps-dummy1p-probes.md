# Sky130 Transistor-Switched Capacitor DAC

- status: `transistor_switched_capacitor_dac_passed_boundary`
- codes measured: `3` of `3`
- half-LSB target V: `5.625000000e-02`
- maximum settling error V: `5.192100000e-02`
- all measured codes within half-LSB: `True`
- measured code order monotonic: `True`

## First-Principles Reading

The capacitor array stores charge, but the MOS switches determine how quickly charge arrives and how much error the sampling edge leaves behind. This fixture replaces the ideal switch boundary with Sky130 NMOS/PMOS devices and keeps the code-dependent top-plate measurement unchanged.

A pass here would establish a transistor-switched DAC boundary, not a complete SAR. A failure means the switch sizing, timing, common-mode range, or capacitor ratio must be repaired before coupling the DAC to the comparator.

## Refused Claim

does not prove capacitor mismatch statistics, reference loading across a full SAR, comparator coupling, extracted layout, board behavior, or silicon
