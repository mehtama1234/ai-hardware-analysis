* Two-stage transistor preamp attached to extracted Sky130 frontend.
.global VSUBS
.lib "/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice" tt
.include "/home/mehtama1/git-repo/ai-hardware-analysis/analog-digital-chip-design-eda/labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/extracted/sky130_ultra_sense_capacitive_frontend_extracted.spice"
.param vdd=1.8
.param lmin=0.15
.param rd1=500000
.param rd2=500000
.param itail1=4e-06
.param itail2=4e-06
.param w1=1
.param w2=1
.param vinp=0.900076485293
.param vinn=0.899923514707
.options method=gear reltol=1e-3 abstol=1e-14 vntol=1e-7 chgtol=1e-16 gmin=1e-12
VDD vdd 0 {vdd}
VSS vss 0 0
VSUB VSUBS 0 0
VSP sp 0 PULSE(0 {vinp} 0.05n 20p 20p 20n 40n)
VSN sn 0 PULSE(0 {vinn} 0.05n 20p 20p 20n 40n)
VCS clk_sample 0 PULSE(0 {vdd} 1.00n 20p 20p 5n 10n)
VCL clk_latch 0 PULSE(0 {vdd} 2.00n 20p 20p 5n 10n)
VCM vcm_reset 0 PULSE(0.9 1.8 0.50n 20p 20p 0.50n 2n)
XFRONT vss vdd sp sense_p clk_sample vcm_reset clk_latch sense_n sn sky130_ultra_sense_capacitive_frontend
RBIASP sense_p 0 100G
RBIASN sense_n 0 100G
XLOAD1REF pre_p pre_p vdd vdd sky130_fd_pr__pfet_01v8 W=8 L=0.15
XLOAD1MIR pre_n pre_p vdd vdd sky130_fd_pr__pfet_01v8 W=8 L=0.15
XINP1 pre_p sense_p tail1 0 sky130_fd_pr__nfet_01v8 W={w1} L={lmin}
XINN1 pre_n sense_n tail1 0 sky130_fd_pr__nfet_01v8 W={w1} L={lmin}
ITAIL1 tail1 0 {itail1}
XLOAD2REF out_p out_p vdd vdd sky130_fd_pr__pfet_01v8 W=8 L=0.15
XLOAD2MIR out_n out_p vdd vdd sky130_fd_pr__pfet_01v8 W=8 L=0.15
XINP2 out_p pre_p tail2 0 sky130_fd_pr__nfet_01v8 W={w2} L={lmin}
XINN2 out_n pre_n tail2 0 sky130_fd_pr__nfet_01v8 W={w2} L={lmin}
ITAIL2 tail2 0 {itail2}
COUTP out_p 0 2f
COUTN out_n 0 2f
* Offset trim is the measured zero-input differential from the two-stage preamp run.
VTRIMP corr_p out_p DC -0.0771165
VTRIMN corr_n out_n DC 0.0771165
XBUFP vdd corr_p buf_p 0 sky130_fd_pr__nfet_01v8 W=2 L=0.15
XBUFN vdd corr_n buf_n 0 sky130_fd_pr__nfet_01v8 W=2 L=0.15
RBUFP buf_p 0 100k
RBUFN buf_n 0 100k
CBUFP buf_p 0 2f
CBUFN buf_n 0 2f

VTRIMBP latch_corr_p buf_p DC -0.0135539
VTRIMBN latch_corr_n buf_n DC 0.0135539

VCLB clkb 0 PULSE(1.8 0 2.00n 20p 20p 5n 10n)
XPREPL vdd clk_latch lat_p vdd sky130_fd_pr__pfet_01v8 W=6 L=0.15
XPRENL vdd clk_latch lat_n vdd sky130_fd_pr__pfet_01v8 W=6 L=0.15
XLPL lat_p lat_n vdd vdd sky130_fd_pr__pfet_01v8 W=6 L=0.15
XLNL lat_p lat_n eval 0 sky130_fd_pr__nfet_01v8 W=3 L=0.15
XRPL lat_n lat_p vdd vdd sky130_fd_pr__pfet_01v8 W=6 L=0.15
XRNL lat_n lat_p eval 0 sky130_fd_pr__nfet_01v8 W=3 L=0.15
XINPL lat_p latch_corr_p tail_l 0 sky130_fd_pr__nfet_01v8 W=1 L=0.15
XINNL lat_n latch_corr_n tail_l 0 sky130_fd_pr__nfet_01v8 W=1 L=0.15
XTAILL tail_l clk_latch 0 0 sky130_fd_pr__nfet_01v8 W=4 L=0.15
XEVAL eval clk_latch 0 0 sky130_fd_pr__nfet_01v8 W=4 L=0.15
CLATP lat_p 0 5f
CLATN lat_n 0 5f
.ic v(sense_p)=0.9 v(sense_n)=0.9 v(pre_p)=1.0 v(pre_n)=1.0 v(out_p)=1.0 v(out_n)=1.0
.tran 20p 6n
.measure tran sense_p_after_v FIND v(sense_p) AT=2.60n
.measure tran sense_n_after_v FIND v(sense_n) AT=2.60n
.measure tran pre_p_after_v FIND v(pre_p) AT=2.60n
.measure tran pre_n_after_v FIND v(pre_n) AT=2.60n
.measure tran out_p_after_v FIND v(out_p) AT=2.60n
.measure tran out_n_after_v FIND v(out_n) AT=2.60n
.measure tran preamp_out_p_for_trim_v FIND v(out_p) AT=2.60n
.measure tran preamp_out_n_for_trim_v FIND v(out_n) AT=2.60n
.measure tran buffer_out_p_for_trim_v FIND v(buf_p) AT=2.60n
.measure tran buffer_out_n_for_trim_v FIND v(buf_n) AT=4.60n
.measure tran lat_p_final_v FIND v(lat_p) AT=4.60n
.measure tran lat_n_final_v FIND v(lat_n) AT=4.60n
.measure tran latch_output_diff_v PARAM='lat_n_final_v-lat_p_final_v'
.control
set noaskquit
run
.endc
.end
