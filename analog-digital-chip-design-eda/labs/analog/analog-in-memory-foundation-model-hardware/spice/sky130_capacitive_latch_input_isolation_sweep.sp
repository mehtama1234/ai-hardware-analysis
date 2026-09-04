* Sky130 capacitive latch-input isolation sweep.
* The sample nodes drive latch input gates through small capacitors and weak common-mode bias.

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
.param ciso=2.000000000000e-16
.param vinp=0.900076485293
.param vinn=0.899923514707

VDD vdd 0 {vdd}
VSS vss 0 0
VBIAS vcm 0 0.9
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

* Isolated comparator input nodes.
CISO_P sp gp {ciso}
CISO_N sn gn {ciso}
RBIASP gp vcm 100G
RBIASN gn vcm 100G

XPREP vdd clkb outp vdd sky130_fd_pr__pfet_01v8 W={wp_latch} L={lmin}
XPREN vdd clkb outn vdd sky130_fd_pr__pfet_01v8 W={wp_latch} L={lmin}
XLP outp outn vdd vdd sky130_fd_pr__pfet_01v8 W={wp_latch} L={lmin}
XLN outp outn eval 0 sky130_fd_pr__nfet_01v8 W={wn_latch} L={lmin}
XRP outn outp vdd vdd sky130_fd_pr__pfet_01v8 W={wp_latch} L={lmin}
XRN outn outp eval 0 sky130_fd_pr__nfet_01v8 W={wn_latch} L={lmin}
XINP outp gp tail 0 sky130_fd_pr__nfet_01v8 W={wn_in} L={lmin}
XINN outn gn tail 0 sky130_fd_pr__nfet_01v8 W={wn_in} L={lmin}
XTAIL tail clk 0 0 sky130_fd_pr__nfet_01v8 W={wn_tail} L={lmin}
XEVAL eval clk 0 0 sky130_fd_pr__nfet_01v8 W={wn_tail} L={lmin}
COUTP outp 0 5f
COUTN outn 0 5f

.tran 2p 3n
.measure tran sampled_p_before_v FIND v(sp) AT=0.90n
.measure tran sampled_n_before_v FIND v(sn) AT=0.90n
.measure tran sampled_p_after_v FIND v(sp) AT=2.60n
.measure tran sampled_n_after_v FIND v(sn) AT=2.60n
.measure tran gate_p_before_v FIND v(gp) AT=0.90n
.measure tran gate_n_before_v FIND v(gn) AT=0.90n
.measure tran gate_p_after_v FIND v(gp) AT=2.60n
.measure tran gate_n_after_v FIND v(gn) AT=2.60n
.measure tran outp_final_v FIND v(outp) AT=2.60n
.measure tran outn_final_v FIND v(outn) AT=2.60n
.measure tran output_diff_final_v PARAM='outn_final_v-outp_final_v'
.control
run
.endc

.end
