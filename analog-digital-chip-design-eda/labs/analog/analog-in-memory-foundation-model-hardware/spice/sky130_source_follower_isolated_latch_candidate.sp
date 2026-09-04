* Sky130 source-follower isolated latch candidate.
* The sampled nodes drive source-follower gates. The latch reads follower sources.

.lib "/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice" tt
.param vdd=1.8
.param lmin=0.15
.param wn=2.0
.param wp=4.0
.param dummy_wn=1.0
.param dummy_wp=2.0
.param csample=0.2p
.param cload=0.05p
.param wn_latch=3.0
.param wp_latch=6.0
.param wn_in=0.5
.param wn_tail=20.0
.param wf=1.000000
.param ifollow=2.000000000000e-06
.param vinp=0.900076485293
.param vinn=0.899923514707

VDD vdd 0 {vdd}
VSS vss 0 0
VINP inp 0 PULSE(0 {vinp} 0.05n 20p 20p 20n 40n)
VINN inn 0 PULSE(0 {vinn} 0.05n 20p 20p 20n 40n)
VCTRL ctrl 0 PULSE(0 {vdd} 0.10n 20p 20p 0.75n 20n)
VCTRLB ctrlb 0 PULSE({vdd} 0 0.10n 20p 20p 0.75n 20n)
VCLK clk 0 PULSE(0 {vdd} 1.00n 20p 20p 5n 10n)
VCLKB clkb 0 PULSE({vdd} 0 1.00n 20p 20p 5n 10n)

XSWNP inp ctrl sp vss sky130_fd_pr__nfet_01v8 W={wn} L={lmin}
XSWPP inp ctrlb sp vdd sky130_fd_pr__pfet_01v8 W={wp} L={lmin}
XSWNN inn ctrl sn vss sky130_fd_pr__nfet_01v8 W={wn} L={lmin}
XSWPN inn ctrlb sn vdd sky130_fd_pr__pfet_01v8 W={wp} L={lmin}
XDUMNP sp ctrlb sp vss sky130_fd_pr__nfet_01v8 W={dummy_wn} L={lmin}
XDUMPP sp ctrl sp vdd sky130_fd_pr__pfet_01v8 W={dummy_wp} L={lmin}
XDUMNN sn ctrlb sn vss sky130_fd_pr__nfet_01v8 W={dummy_wn} L={lmin}
XDUMPN sn ctrl sn vdd sky130_fd_pr__pfet_01v8 W={dummy_wp} L={lmin}
CSP sp 0 {csample}
CSN sn 0 {csample}
CLP sp 0 {cload}
CLN sn 0 {cload}
RLEAKP sp 0 100G
RLEAKN sn 0 100G

XFOLP bufp sp vdd vdd sky130_fd_pr__nfet_01v8 W={wf} L={lmin}
XFOLN bufn sn vdd vdd sky130_fd_pr__nfet_01v8 W={wf} L={lmin}
IFOLP bufp 0 {ifollow}
IFOLN bufn 0 {ifollow}
CBUFP bufp 0 2f
CBUFN bufn 0 2f

XPREP vdd clkb outp vdd sky130_fd_pr__pfet_01v8 W={wp_latch} L={lmin}
XPREN vdd clkb outn vdd sky130_fd_pr__pfet_01v8 W={wp_latch} L={lmin}
XLP outp outn vdd vdd sky130_fd_pr__pfet_01v8 W={wp_latch} L={lmin}
XLN outp outn eval 0 sky130_fd_pr__nfet_01v8 W={wn_latch} L={lmin}
XRP outn outp vdd vdd sky130_fd_pr__pfet_01v8 W={wp_latch} L={lmin}
XRN outn outp eval 0 sky130_fd_pr__nfet_01v8 W={wn_latch} L={lmin}
XINP outp bufp tail 0 sky130_fd_pr__nfet_01v8 W={wn_in} L={lmin}
XINN outn bufn tail 0 sky130_fd_pr__nfet_01v8 W={wn_in} L={lmin}
XTAIL tail clk 0 0 sky130_fd_pr__nfet_01v8 W={wn_tail} L={lmin}
XEVAL eval clk 0 0 sky130_fd_pr__nfet_01v8 W={wn_tail} L={lmin}
COUTP outp 0 5f
COUTN outn 0 5f

.tran 2p 3n
.measure tran sampled_diff_before_v PARAM='v(sp)-v(sn)' AT=0.90n
.measure tran sampled_diff_after_v PARAM='v(sp)-v(sn)' AT=2.60n
.measure tran sampled_diff_kickback_v PARAM='abs(sampled_diff_after_v-sampled_diff_before_v)'
.measure tran buffer_diff_before_v PARAM='v(bufp)-v(bufn)' AT=0.90n
.measure tran buffer_diff_after_v PARAM='v(bufp)-v(bufn)' AT=2.60n
.measure tran output_diff_final_v PARAM='v(outn)-v(outp)' AT=2.60n
.control
run
.endc
.end
