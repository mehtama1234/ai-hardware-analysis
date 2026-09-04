* Sky130 hold-only differential injection fixture.
* The Sky130 model library is loaded, but no MOS switch changes state during transient.

.lib "/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice" tt
.param vinp=0.91
.param vinn=0.89

.options method=gear reltol=1e-3 abstol=1e-12 vntol=1e-6
VINP hp 0 {vinp}
VINN hn 0 {vinn}
CSTOREP hp 0 0.2p
CSTOREN hn 0 0.2p

IINJP hp 0 PWL(0 0 7.02n 0 7.021n -5.000000000000001e-05 7.04n -5.000000000000001e-05 7.041n 0 10n 0)
IINJN hn 0 PWL(0 0 7.02n 0 7.021n -5.000000000000001e-05 7.04n -5.000000000000001e-05 7.041n 0 10n 0)

.tran 20p 10n
.measure tran acquired_p_v FIND v(hp) AT=6.8n
.measure tran acquired_n_v FIND v(hn) AT=6.8n
.measure tran held_p_v FIND v(hp) AT=8.5n
.measure tran held_n_v FIND v(hn) AT=8.5n
.control
run
.endc

.end
