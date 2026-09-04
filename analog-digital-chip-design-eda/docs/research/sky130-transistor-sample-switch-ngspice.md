# Sky130 Transistor Sample Switch Ngspice

This page records the first converter-adjacent ngspice run that uses Sky130 MOS transistor models.

The generated evidence below tests a small transmission-gate sample path. The question is narrow: when the sample switch is turned on, can a MOS switch charge the sample node close to the input before the readout window ends?

This is stronger than an ideal resistor fixture because the switch is now a transistor device from the process model. It is still not a full converter. It does not prove a DAC ladder, SAR capacitor array, comparator decision, mismatch, noise, extracted transistor layout, DRC/LVS, or accepted post-layout replacement evidence.

