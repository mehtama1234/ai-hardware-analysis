* Sky130 two-phase preamp then latch candidate.
* Phase 1 samples the input. Phase 2 lets a resistor-load preamp form an internal difference.
* Phase 3 enables the latch after the preamp has settled.

.lib "/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice" tt
.param vdd=1.8
.param lmin=0.15
.param wn=2.0
.param wp=4.0
.param dummy_wn=1.0
.param dummy_wp=2.0
.param cstore=0.2p
.param pre_w=8.0
.param pre_tail=20u
.param pre_rd=100k
.param wn_latch=3.0
.param wp_latch=6.0
.param wn_in=0.5
.param wn_tail=20.0
.param vinp=0.900076485293
.param vinn=0.899923514707
.options method=gear reltol=1e-3 abstol=1e-14 vntol=1e-7 chgtol=1e-16 gmin=1e-12

VDD vdd 0 {vdd}
VSS vss 0 0
VINP inp 0 PULSE(0 {vinp} 0.05n 20p 20p 20n 40n)
VINN inn 0 PULSE(0 {vinn} 0.05n 20p 20p 20n 40n)
VCTRL ctrl 0 PULSE(0 {vdd} 0.10n 20p 20p 0.75n 20n)
VCTRLB ctrlb 0 PULSE({vdd} 0 0.10n 20p 20p 0.75n 20n)
VCLK clk 0 PULSE(0 {vdd} 1.60n 20p 20p 5n 10n)
VCLKB clkb 0 PULSE({vdd} 0 1.60n 20p 20p 5n 10n)

XSWNP inp ctrl sp vss sky130_fd_pr__nfet_01v8 W={wn} L={lmin}
XSWPP inp ctrlb sp vdd sky130_fd_pr__pfet_01v8 W={wp} L={lmin}
XSWNN inn ctrl sn vss sky130_fd_pr__nfet_01v8 W={wn} L={lmin}
XSWPN inn ctrlb sn vdd sky130_fd_pr__pfet_01v8 W={wp} L={lmin}
XDUMNP sp ctrlb sp vss sky130_fd_pr__nfet_01v8 W={dummy_wn} L={lmin}
XDUMPP sp ctrl sp vdd sky130_fd_pr__pfet_01v8 W={dummy_wp} L={lmin}
XDUMNN sn ctrlb sn vss sky130_fd_pr__nfet_01v8 W={dummy_wn} L={lmin}
XDUMPN sn ctrl sn vdd sky130_fd_pr__pfet_01v8 W={dummy_wp} L={lmin}
CSP sp 0 {cstore}
CSN sn 0 {cstore}
RLEAKP sp 0 100G
RLEAKN sn 0 100G

RPREP vdd pre_p {pre_rd}
RPREN vdd pre_n {pre_rd}
XPREP pre_p sp pre_tail_node 0 sky130_fd_pr__nfet_01v8 W={pre_w} L={lmin}
XPREN pre_n sn pre_tail_node 0 sky130_fd_pr__nfet_01v8 W={pre_w} L={lmin}
IPRE pre_tail_node 0 {pre_tail}
CPREP pre_p 0 2f
CPREN pre_n 0 2f

XLPRE1 vdd clkb outp vdd sky130_fd_pr__pfet_01v8 W={wp_latch} L={lmin}
XLPRE2 vdd clkb outn vdd sky130_fd_pr__pfet_01v8 W={wp_latch} L={lmin}
XLP outp outn vdd vdd sky130_fd_pr__pfet_01v8 W={wp_latch} L={lmin}
XLN outp outn eval 0 sky130_fd_pr__nfet_01v8 W={wn_latch} L={lmin}
XRP outn outp vdd vdd sky130_fd_pr__pfet_01v8 W={wp_latch} L={lmin}
XRN outn outp eval 0 sky130_fd_pr__nfet_01v8 W={wn_latch} L={lmin}
XINP outp pre_p tail 0 sky130_fd_pr__nfet_01v8 W={wn_in} L={lmin}
XINN outn pre_n tail 0 sky130_fd_pr__nfet_01v8 W={wn_in} L={lmin}
XTAIL tail clk 0 0 sky130_fd_pr__nfet_01v8 W={wn_tail} L={lmin}
XEVAL eval clk 0 0 sky130_fd_pr__nfet_01v8 W={wn_tail} L={lmin}
COUTP outp 0 5f
COUTN outn 0 5f

.ic v(sp)=0.9 v(sn)=0.9 v(pre_p)=1.0 v(pre_n)=1.0 v(pre_tail_node)=0.25 v(outp)=1.8 v(outn)=1.8
.tran 5p 3n
.measure tran sampled_p_before_v FIND v(sp) AT=0.90n
.measure tran sampled_n_before_v FIND v(sn) AT=0.90n
.measure tran sampled_p_after_v FIND v(sp) AT=2.70n
.measure tran sampled_n_after_v FIND v(sn) AT=2.70n
.measure tran preamp_p_before_latch_v FIND v(pre_p) AT=1.45n
.measure tran preamp_n_before_latch_v FIND v(pre_n) AT=1.45n
.measure tran preamp_p_after_latch_v FIND v(pre_p) AT=2.70n
.measure tran preamp_n_after_latch_v FIND v(pre_n) AT=2.70n
.measure tran output_p_final_v FIND v(outp) AT=2.70n
.measure tran output_n_final_v FIND v(outn) AT=2.70n
.control
run
.endc
.end
