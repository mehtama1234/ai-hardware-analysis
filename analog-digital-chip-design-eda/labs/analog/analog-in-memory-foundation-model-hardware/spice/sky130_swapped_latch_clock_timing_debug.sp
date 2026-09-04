* Sky130 swapped latch clock timing debug.
* Ideal sources drive the latch using the polarity-corrected swapped preamp mapping.

.lib "/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice" tt
.param vdd=1.8
.param lmin=0.15
.param wn_latch=3.0
.param wp_latch=6.0
.param wn_in=0.5
.param wn_tail=20.0
.param vinp=0.820163600000
.param vinn=0.821595200000
.options method=gear reltol=1e-3 abstol=1e-14 vntol=1e-7 gmin=1e-12

VDD vdd 0 {vdd}
VINP inp 0 {vinp}
VINN inn 0 {vinn}
VCLK clk 0 PULSE(0 {vdd} 1.000n 20p 20p 5n 10n)
VCLKB clkb 0 PULSE({vdd} 0 1.000n 20p 20p 5n 10n)

XPREP vdd clkb outp vdd sky130_fd_pr__pfet_01v8 W={wp_latch} L={lmin}
XPREN vdd clkb outn vdd sky130_fd_pr__pfet_01v8 W={wp_latch} L={lmin}
XLP outp outn vdd vdd sky130_fd_pr__pfet_01v8 W={wp_latch} L={lmin}
XLN outp outn eval 0 sky130_fd_pr__nfet_01v8 W={wn_latch} L={lmin}
XRP outn outp vdd vdd sky130_fd_pr__pfet_01v8 W={wp_latch} L={lmin}
XRN outn outp eval 0 sky130_fd_pr__nfet_01v8 W={wn_latch} L={lmin}
XINP outp inp tail 0 sky130_fd_pr__nfet_01v8 W={wn_in} L={lmin}
XINN outn inn tail 0 sky130_fd_pr__nfet_01v8 W={wn_in} L={lmin}
XTAIL tail clk 0 0 sky130_fd_pr__nfet_01v8 W={wn_tail} L={lmin}
XEVAL eval clk 0 0 sky130_fd_pr__nfet_01v8 W={wn_tail} L={lmin}
COUTP outp 0 5f
COUTN outn 0 5f

.ic v(outp)=1.8 v(outn)=1.8
.tran 2p 2.800n uic
.measure tran outp_final_v FIND v(outp) AT=2.600n
.measure tran outn_final_v FIND v(outn) AT=2.600n
.control
set noaskquit
run
.endc

.end
