* Shared converter loading fixture for AIMC converter handoff.
* This is a muxed source-load model, not a full shared ADC layout.
* The Python runner overrides active_loads and vin for the tested cases.

.param vin=0.5
.param active_loads=16
.param rsource=200
.param rshare=35
.param csample=0.2p
.param cmux_unit=0.015p
.param trise=20p
.param tfall=20p

VREAD src 0 PULSE(0 {vin} 0.1n {trise} {tfall} 20n 40n)
RSRC src muxin {rsource}
RSHARE muxin sample {rshare}
CSAMPLE sample 0 {csample}
CMUX sample 0 {active_loads * cmux_unit}

.tran 5p 13n
.measure tran vshared FIND v(sample) AT=12.1n
.control
run
.endc

.end
