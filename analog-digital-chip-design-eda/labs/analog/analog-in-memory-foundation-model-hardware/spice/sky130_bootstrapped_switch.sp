* Sky130 idealized bootstrapped-switch fixture.
* The nfet gate is driven near input + vdd during sample, then pulled to zero during hold.

.lib "/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice" tt
.param vin=1.5
.param vdd=1.8
.param lmin=0.15
.param wn=2.0
.param csample=0.2p
.param cload=0.05p

VDD vdd 0 {vdd}
VSS vss 0 0
VIN in 0 PULSE(0 {vin} 0.1n 20p 20p 20n 40n)
VBOOT boot 0 PULSE(0 {vin+vdd} 0.2n 20p 20p 7n 20n)

XSW in boot sample vss sky130_fd_pr__nfet_01v8 W={wn} L={lmin}
CSAMPLE sample 0 {csample}
CLOAD sample 0 {cload}
RLEAK sample 0 100G

.tran 5p 10n
.measure tran acquired_v FIND v(sample) AT=6.8n
.measure tran held_v FIND v(sample) AT=8.5n
.measure tran input_v FIND v(in) AT=6.8n
.measure tran boot_v FIND v(boot) AT=6.8n
.measure tran acquisition_abs_error_v PARAM='abs(input_v-acquired_v)'
.measure tran hold_abs_delta_v PARAM='abs(held_v-acquired_v)'
.measure tran total_abs_error_v PARAM='abs(input_v-held_v)'
.control
run
.endc

.end
