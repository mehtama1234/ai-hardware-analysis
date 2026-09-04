* Sky130 clocked comparator latch proxy.
* Cross-coupled inverter latch with an nfet input pair and ideal input voltages.
* This is a schematic-level latch fixture, not extracted layout and not noise proof.

.lib "/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice" tt
.param vdd=1.8
.param lmin=0.15
.param wn_latch=3.0
.param wp_latch=6.0
.param wn_in=10.0
.param wn_tail=20.0
.param vinp=0.900076485293
.param vinn=0.899923514707

VDD vdd 0 {vdd}
VINP inp 0 {vinp}
VINN inn 0 {vinn}
VCLK clk 0 PULSE(0 {vdd} 1n 20p 20p 5n 10n)
VCLKB clkb 0 PULSE({vdd} 0 1n 20p 20p 5n 10n)

* Precharge both latch nodes high before evaluation.
XPREP vdd clkb outp vdd sky130_fd_pr__pfet_01v8 W={wp_latch} L={lmin}
XPREN vdd clkb outn vdd sky130_fd_pr__pfet_01v8 W={wp_latch} L={lmin}

* Cross-coupled inverter latch.
XLP outp outn vdd vdd sky130_fd_pr__pfet_01v8 W={wp_latch} L={lmin}
XLN outp outn eval 0 sky130_fd_pr__nfet_01v8 W={wn_latch} L={lmin}
XRP outn outp vdd vdd sky130_fd_pr__pfet_01v8 W={wp_latch} L={lmin}
XRN outn outp eval 0 sky130_fd_pr__nfet_01v8 W={wn_latch} L={lmin}

* Differential input pair steers the falling side during evaluation.
XINP outp inp tail 0 sky130_fd_pr__nfet_01v8 W={wn_in} L={lmin}
XINN outn inn tail 0 sky130_fd_pr__nfet_01v8 W={wn_in} L={lmin}
XTAIL tail clk 0 0 sky130_fd_pr__nfet_01v8 W={wn_tail} L={lmin}
XEVAL eval clk 0 0 sky130_fd_pr__nfet_01v8 W={wn_tail} L={lmin}

COUTP outp 0 5f
COUTN outn 0 5f
.ic v(outp)=1.8 v(outn)=1.8 v(tail)=0 v(eval)=0

.tran 2p 3n uic
.measure tran outp_pre_v FIND v(outp) AT=0.8n
.measure tran outn_pre_v FIND v(outn) AT=0.8n
.measure tran outp_final_v FIND v(outp) AT=2.6n
.measure tran outn_final_v FIND v(outn) AT=2.6n
.measure tran output_diff_final_v PARAM='outn_final_v-outp_final_v'
.measure tran input_kick_proxy_v PARAM='abs(vinp-vinn)'
.control
run
.endc

.end
