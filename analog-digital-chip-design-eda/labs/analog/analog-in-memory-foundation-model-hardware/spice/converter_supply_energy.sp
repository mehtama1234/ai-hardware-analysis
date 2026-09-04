* Converter supply-energy fixture for AIMC converter handoff.
* This is a switched-capacitance load model, not extracted converter power.
* The Python runner overrides vin for representative conversion cases.

.param vin=0.5
.param vdd=1.0
.param cdac=0.28p
.param cadc=4.096p
.param cmux=0.24p
.param rdac=80
.param radc=60
.param rmux=35
.param trise=20p
.param tfall=20p

VDAC dac_src 0 PULSE(0 {vin} 0.1n {trise} {tfall} 20n 40n)
RDAC dac_src dac_out {rdac}
CDAC dac_out 0 {cdac}

VADC adc_src 0 PULSE(0 {vdd} 4.0n {trise} {tfall} 12n 40n)
RADC adc_src adc_ref {radc}
CADC adc_ref 0 {cadc}

VMUX mux_src 0 PULSE(0 {vin} 4.0n {trise} {tfall} 12n 40n)
RMUX mux_src sample {rmux}
CMUX sample 0 {cmux}

.tran 5p 17n
.measure tran edac INTEG par('-v(dac_src)*i(vdac)') FROM=0.1n TO=4.1n
.measure tran eadc INTEG par('-v(adc_src)*i(vadc)') FROM=4.0n TO=16.1n
.measure tran emux INTEG par('-v(mux_src)*i(vmux)') FROM=4.0n TO=16.1n
.measure tran vdacsettled FIND v(dac_out) AT=4.1n
.measure tran vadcsettled FIND v(adc_ref) AT=16.1n
.measure tran vsamplesettled FIND v(sample) AT=16.1n
.control
run
.endc

.end
