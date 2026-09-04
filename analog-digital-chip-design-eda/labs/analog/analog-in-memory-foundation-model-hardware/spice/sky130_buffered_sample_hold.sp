* Sky130 buffered sample-and-hold fixture.
* The sample capacitor drives a MOS gate; the readout load is moved to the source follower output.

.lib "/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice" tt
.param vin=1.5
.param vdd=1.8
.param lmin=0.15
.param sw_wn=2.0
.param sw_wp=4.0
.param buf_wn=8.0
.param bias_wn=1.0
.param csample=0.2p
.param cout=0.05p

VDD vdd 0 {vdd}
VSS vss 0 0
VIN in 0 PULSE(0 {vin} 0.1n 20p 20p 20n 40n)
VCTRL ctrl 0 PULSE(0 {vdd} 0.2n 20p 20p 7n 20n)
VCTRLB ctrlb 0 PULSE({vdd} 0 0.2n 20p 20p 7n 20n)
VBIAS bias 0 0.55

XSWN in ctrl sample vss sky130_fd_pr__nfet_01v8 W={sw_wn} L={lmin}
XSWP in ctrlb sample vdd sky130_fd_pr__pfet_01v8 W={sw_wp} L={lmin}
CSAMPLE sample 0 {csample}
RLEAK sample 0 100G

XBUF vdd sample out vss sky130_fd_pr__nfet_01v8 W={buf_wn} L={lmin}
XBIAS out bias vss vss sky130_fd_pr__nfet_01v8 W={bias_wn} L={lmin}
COUT out 0 {cout}

.tran 10p 12n
.measure tran acquired_sample_v FIND v(sample) AT=6.8n
.measure tran held_sample_v FIND v(sample) AT=8.5n
.measure tran acquired_out_v FIND v(out) AT=6.8n
.measure tran held_out_v FIND v(out) AT=8.5n
.measure tran input_v FIND v(in) AT=6.8n
.measure tran sample_hold_abs_delta_v PARAM='abs(held_sample_v-acquired_sample_v)'
.measure tran output_hold_abs_delta_v PARAM='abs(held_out_v-acquired_out_v)'
.measure tran output_gain_v_per_v PARAM='held_out_v/held_sample_v'
.control
run
.endc

.end
