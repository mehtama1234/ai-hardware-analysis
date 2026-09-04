* 12-bit SAR readout settling fixture for AIMC converter handoff.
* This is a sampled readout load model, not a transistor ADC.
* The Python runner overrides vin for low, midscale, and high readout cases.

.param vin=0.5
.param rsource=200
.param csample=0.2p
.param trise=20p
.param tfall=20p

VREAD src 0 PULSE(0 {vin} 0.1n {trise} {tfall} 20n 40n)
RSRC src sample {rsource}
CSAMPLE sample 0 {csample}

.tran 5p 13n
.measure tran vsampled FIND v(sample) AT=12.1n
.control
run
.endc

.end
