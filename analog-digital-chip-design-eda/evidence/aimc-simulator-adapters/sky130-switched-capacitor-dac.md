# Sky130 Switched-Capacitor DAC

- status: `switched_capacitor_dac_measured_but_half_lsb_failed`
- bits: `4`
- codes measured: `6` of `6`
- half-LSB target V: `5.625000000e-02`
- maximum settling error V: `8.788500000e-02`
- all measured codes within half-LSB: `False`

## First-Principles Reading

A capacitor DAC does not create a voltage by instruction. During sampling, charge is placed on the top plate. During redistribution, the bottom plates move between reference and ground, and the top plate moves by charge conservation. The code is useful only if that movement settles close enough to the intended threshold before the comparator fires.

This first boundary uses ideal switch models so the capacitor charge law can be isolated. The next circuit must replace those switches with the selected Sky130 transmission-gate or MOS implementation and measure resistance, charge injection, reference loading, and mismatch.

## Refused Claim

does not prove transistor switch resistance, capacitor mismatch, DAC reference loading, comparator coupling, SAR conversion, extracted layout, or silicon
