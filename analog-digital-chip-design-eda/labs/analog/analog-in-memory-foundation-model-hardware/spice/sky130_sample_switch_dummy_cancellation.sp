* Sky130 sample-switch dummy cancellation fixture.
* Dummy devices are shorted at the sample node and clocked on the opposite edge.

.lib "/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice" tt
.param vin=1.5
.param vdd=1.8
.param lmin=0.15
.param switch_wn=2.0
.param switch_wp=4.0
.param dummy_wn=1.0
.param dummy_wp=2.0
.param csample=1.0p
.param cload=0.05p

VDD vdd 0 {vdd}
VSS vss 0 0
VIN in 0 PULSE(0 {vin} 0.1n 20p 20p 20n 40n)
VCTRL ctrl 0 PULSE(0 {vdd} 0.2n 20p 20p 7n 20n)
VCTRLB ctrlb 0 PULSE({vdd} 0 0.2n 20p 20p 7n 20n)

XSWN in ctrl sample vss sky130_fd_pr__nfet_01v8 W={switch_wn} L={lmin}
XSWP in ctrlb sample vdd sky130_fd_pr__pfet_01v8 W={switch_wp} L={lmin}
XDUMN sample ctrlb sample vss sky130_fd_pr__nfet_01v8 W={dummy_wn} L={lmin}
XDUMP sample ctrl sample vdd sky130_fd_pr__pfet_01v8 W={dummy_wp} L={lmin}
CSAMPLE sample 0 {csample}
CLOAD sample 0 {cload}
RLEAK sample 0 100G

.tran 2p 10n
.measure tran acquired_v FIND v(sample) AT=6.8n
.measure tran held_v FIND v(sample) AT=8.5n
.measure tran input_v FIND v(in) AT=6.8n
.measure tran hold_abs_delta_v PARAM='abs(held_v-acquired_v)'
.measure tran total_abs_error_v PARAM='abs(input_v-held_v)'
.control
run
.endc

.end
