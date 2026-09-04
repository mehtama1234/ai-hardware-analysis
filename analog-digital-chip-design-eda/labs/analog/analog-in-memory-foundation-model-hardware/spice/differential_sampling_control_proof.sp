* Differential sampling control proof.
* Ideal switches isolate topology behavior from Sky130 model convergence.

.param vinp=1.0
.param vinn=0.8
.param common=0.005
.param mismatch=0.0003

VINP inp 0 {vinp}
VINN inn 0 {vinn}
VCTRL ctrl 0 PULSE(1 0 7n 20p 20p 20n 40n)

.model SWMOD SW(Ron=10 Roff=1e12 Vt=0.5 Vh=0.05)
SP inp hp ctrl 0 SWMOD
SN inn hn ctrl 0 SWMOD
CP hp 0 0.2p
CN hn 0 0.2p

IINJP hp 0 PWL(0 0 7.02n 0 7.021n -5.000000000000001e-05 7.04n -5.000000000000001e-05 7.041n 0 10n 0)
IINJN hn 0 PWL(0 0 7.02n 0 7.021n -5.300000000000001e-05 7.04n -5.300000000000001e-05 7.041n 0 10n 0)
.tran 20p 10n
.measure tran acquired_p_v FIND v(hp) AT=6.8n
.measure tran acquired_n_v FIND v(hn) AT=6.8n
.measure tran held_p_v FIND v(hp) AT=8.5n
.measure tran held_n_v FIND v(hn) AT=8.5n
.measure tran acquired_diff_v PARAM='acquired_p_v-acquired_n_v'
.measure tran held_diff_v PARAM='held_p_v-held_n_v'
.measure tran p_hold_abs_delta_v PARAM='abs(held_p_v-acquired_p_v)'
.measure tran n_hold_abs_delta_v PARAM='abs(held_n_v-acquired_n_v)'
.measure tran diff_hold_abs_delta_v PARAM='abs(held_diff_v-acquired_diff_v)'
.control
run
.endc

.end
