* Extracted balanced frontend to Sky130 latch handoff.
.lib "/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice" tt
.include "/home/mehtama1/git-repo/ai-hardware-analysis/analog-digital-chip-design-eda/labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/extracted/sky130_balanced_capacitive_isolation_frontend_extracted.spice"
.param vdd=1.8
.param lmin=0.15
.param wp_latch=6
.param wn_latch=3
.param wn_in=10
.param wn_tail=20
.param vinp=0.900076485293
.param vinn=0.899923514707
VDD vdd 0 {vdd}
VSS vss 0 0
VSP sp 0 PULSE(0 {vinp} 0.05n 20p 20p 20n 40n)
VSN sn 0 PULSE(0 {vinn} 0.05n 20p 20p 20n 40n)
VCS clk_sample 0 PULSE(0 {vdd} 1.00n 20p 20p 5n 10n)
VCL clk_latch 0 PULSE(0 {vdd} 2.00n 20p 20p 5n 10n)
VCLB clkb 0 PULSE({vdd} 0 2.00n 20p 20p 5n 10n)
VCM vcm_reset 0 0.9
XFRONT vss vdd sp sense_p clk_sample vcm_reset clk_latch sense_n sn sky130_balanced_capacitive_isolation_frontend
RBIASP sense_p vcm_reset 100G
RBIASN sense_n vcm_reset 100G
XPREP vdd clkb outp vdd sky130_fd_pr__pfet_01v8 W={wp_latch} L={lmin}
XPREN vdd clkb outn vdd sky130_fd_pr__pfet_01v8 W={wp_latch} L={lmin}
XLP outp outn vdd vdd sky130_fd_pr__pfet_01v8 W={wp_latch} L={lmin}
XLN outp outn eval 0 sky130_fd_pr__nfet_01v8 W={wn_latch} L={lmin}
XRP outn outp vdd vdd sky130_fd_pr__pfet_01v8 W={wp_latch} L={lmin}
XRN outn outp eval 0 sky130_fd_pr__nfet_01v8 W={wn_latch} L={lmin}
XINP outp sense_p tail 0 sky130_fd_pr__nfet_01v8 W={wn_in} L={lmin}
XINN outn sense_n tail 0 sky130_fd_pr__nfet_01v8 W={wn_in} L={lmin}
XTAIL tail clk_latch 0 0 sky130_fd_pr__nfet_01v8 W={wn_tail} L={lmin}
XEVAL eval clk_latch 0 0 sky130_fd_pr__nfet_01v8 W={wn_tail} L={lmin}
CSP sp 0 0.2p
CSN sn 0 0.2p
COUTP outp 0 5f
COUTN outn 0 5f
.tran 2p 6n
.measure tran sense_p_before_v FIND v(sense_p) AT=1.90n
.measure tran sense_n_before_v FIND v(sense_n) AT=1.90n
.measure tran sense_p_after_v FIND v(sense_p) AT=4.60n
.measure tran sense_n_after_v FIND v(sense_n) AT=4.60n
.measure tran sample_p_before_v FIND v(sp) AT=1.90n
.measure tran sample_n_before_v FIND v(sn) AT=1.90n
.measure tran sample_p_after_v FIND v(sp) AT=4.60n
.measure tran sample_n_after_v FIND v(sn) AT=4.60n
.measure tran outp_final_v FIND v(outp) AT=4.60n
.measure tran outn_final_v FIND v(outn) AT=4.60n
.measure tran output_diff_final_v PARAM='outn_final_v-outp_final_v'
.control
run
.endc
.end
