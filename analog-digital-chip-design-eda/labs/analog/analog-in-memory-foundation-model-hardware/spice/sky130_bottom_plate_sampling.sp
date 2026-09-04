* Sky130 bottom-plate sampling fixture.
* The stored value is the voltage across CSAMPLE: v(top)-v(bottom).

.lib "/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice" tt
.param vin=1.5
.param vdd=1.8
.param lmin=0.15
.param wn=2.0
.param wp=4.0
.param csample=1.0p
.param cload=0.05p

VDD vdd 0 {vdd}
VSS vss 0 0
VIN in 0 PULSE(0 {vin} 0.1n 20p 20p 20n 40n)
VTOP top_ctrl 0 PULSE(0 {vdd} 0.2n 20p 20p 7.0n 20n)
VTOPB top_ctrlb 0 PULSE({vdd} 0 0.2n 20p 20p 7.0n 20n)
VBOT bot_ctrl 0 PULSE(0 {vdd} 0.2n 20p 20p 6.8n 20n)
VBOTB bot_ctrlb 0 PULSE({vdd} 0 0.2n 20p 20p 6.8n 20n)

XTOPN in top_ctrl top vss sky130_fd_pr__nfet_01v8 W={wn} L={lmin}
XTOPP in top_ctrlb top vdd sky130_fd_pr__pfet_01v8 W={wp} L={lmin}
XBOTN bottom bot_ctrl vss vss sky130_fd_pr__nfet_01v8 W={wn} L={lmin}
XBOTP bottom bot_ctrlb vss vdd sky130_fd_pr__pfet_01v8 W={wp} L={lmin}

CSAMPLE top bottom {csample}
CLOAD top 0 {cload}
RLEAKTOP top 0 100G
RLEAKBOT bottom 0 100G

.tran 2p 10n
.measure tran acquired_top_v FIND v(top) AT=6.6n
.measure tran acquired_bottom_v FIND v(bottom) AT=6.6n
.measure tran held_top_v FIND v(top) AT=8.5n
.measure tran held_bottom_v FIND v(bottom) AT=8.5n
.measure tran input_v FIND v(in) AT=6.6n
.measure tran acquired_stored_v PARAM='acquired_top_v-acquired_bottom_v'
.measure tran held_stored_v PARAM='held_top_v-held_bottom_v'
.measure tran hold_abs_delta_v PARAM='abs(held_stored_v-acquired_stored_v)'
.measure tran total_abs_error_v PARAM='abs(input_v-held_stored_v)'
.control
run
.endc

.end
