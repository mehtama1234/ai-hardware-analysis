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
VSP sp 0 PULSE(0.9 0.900076485293 3.000n 20p 20p 20n 40n)
VSN sn 0 PULSE(0.9 0.899923514707 3.000n 20p 20p 20n 40n)
VCS clk_sample 0 PULSE(0 1.8 3.800n 20p 20p 5n 10n)
VCL clk_latch 0 PULSE(0 1.8 5.000n 20p 20p 5n 10n)
VCM vcm_reset 0 PULSE(0.9 1.8 0.50n 20p 20p 0.50n 2n)
XFRONT vss vdd sp sense_p clk_sample vcm_reset clk_latch sense_n sn sky130_ultra_sense_capacitive_frontend
RBIASP sense_p 0 100G
RBIASN sense_n 0 100G
RDP1 vdd pre_p 500000
RDN1 vdd pre_n 500000
XINP1 pre_p sense_p tail1 0 sky130_fd_pr__nfet_01v8 W={w1} L={lmin}
XINN1 pre_n sense_n tail1 0 sky130_fd_pr__nfet_01v8 W={w1} L={lmin}
ITAIL1 tail1 0 {itail1}
RDP2 vdd out_p 500000
RDN2 vdd out_n 500000
XINP2 out_p pre_p tail2 0 sky130_fd_pr__nfet_01v8 W={w2} L={lmin}
XINN2 out_n pre_n tail2 0 sky130_fd_pr__nfet_01v8 W={w2} L={lmin}
ITAIL2 tail2 0 {itail2}
COUTP out_p 0 2f
COUTN out_n 0 2f
* Live extracted preamp with dynamic offset-transfer interface.
VBIAS gate_bias 0 0.9
VCAL cal_ctrl 0 PULSE(1.8 0 3.600n 20p 20p 20n 40n)
XCALP gate_p cal_ctrl gate_bias 0 sky130_fd_pr__nfet_01v8 W=2 L=0.15
XCALN gate_n cal_ctrl gate_bias 0 sky130_fd_pr__nfet_01v8 W=2 L=0.15
CRXINP out_p rx_input_p 100f
CRXINN out_n rx_input_n 100f
RRXBIASP rx_input_p gate_bias 1000000
RRXBIASN rx_input_n gate_bias 1000000
RRXP rx_p 0 500000
RRXN rx_n 0 500000
XRXP rx_p rx_input_p vdd vdd sky130_fd_pr__pfet_01v8 W=0.5 L=0.15
XRXN rx_n rx_input_n vdd vdd sky130_fd_pr__pfet_01v8 W=0.5 L=0.15
VTRIMBP trim_bias_p 0 0.7
VTRIMBN trim_bias_n 0 0.7
XTRIMP rx_p trim_bias_p 0 0 sky130_fd_pr__nfet_01v8 W=0.5 L=0.15
XTRIMN rx_n trim_bias_n 0 0 sky130_fd_pr__nfet_01v8 W=0.5 L=0.15
RGAININP rx_p gain_in_p 1000000
RGAININN rx_n gain_in_n 1000000
RGAINBIASP gain_in_p 0 1000000
RGAINBIASN gain_in_n 0 1000000

RGAINP vdd gain_p 300000
RGAINN vdd gain_n 300000
XGAINP gain_p gain_in_p gain_tail 0 sky130_fd_pr__nfet_01v8 W=2 L=0.15
XGAINN gain_n gain_in_n gain_tail 0 sky130_fd_pr__nfet_01v8 W=2 L=0.15
IGAIN gain_tail 0 2e-06
VGAINRESET gain_reset 0 PULSE(1.8 0 3.600n 20p 20p 20n 40n)
XGAINRP gain_p gain_reset gate_bias 0 sky130_fd_pr__nfet_01v8 W=4 L=0.15
XGAINRN gain_n gain_reset gate_bias 0 sky130_fd_pr__nfet_01v8 W=4 L=0.15
VGAINTRIMP gain_trim_p 0 0.7
VGAINTRIMN gain_trim_n 0 0.7
XGAINTRIMP gain_p gain_trim_p 0 0 sky130_fd_pr__nfet_01v8 W=0.5 L=0.15
XGAINTRIMN gain_n gain_trim_n 0 0 sky130_fd_pr__nfet_01v8 W=0.5 L=0.15
RREGENINP gain_p regen_in_p 1000000
RREGENINN gain_n regen_in_n 1000000
RREGENBIASP regen_in_p 0 1000000
RREGENBIASN regen_in_n 0 1000000

VREGENRESET regen_reset 0 PULSE(1.8 0 3.600n 20p 20p 20n 40n)

XREGENRP regen_p regen_reset gate_bias 0 sky130_fd_pr__nfet_01v8 W=4 L=0.15
XREGENRN regen_n regen_reset gate_bias 0 sky130_fd_pr__nfet_01v8 W=4 L=0.15

XREGENCP regen_p regen_n vdd vdd sky130_fd_pr__pfet_01v8 W=2 L=0.15
XREGENCN regen_p regen_n 0 0 sky130_fd_pr__nfet_01v8 W=2 L=0.15
XREGENDP regen_n regen_p vdd vdd sky130_fd_pr__pfet_01v8 W=2 L=0.15
XREGENDN regen_n regen_p 0 0 sky130_fd_pr__nfet_01v8 W=2 L=0.15
XREGENINP regen_p regen_in_p regen_tail 0 sky130_fd_pr__nfet_01v8 W=2 L=0.15
XREGENINN regen_n regen_in_n regen_tail 0 sky130_fd_pr__nfet_01v8 W=2 L=0.15
IREGEN regen_tail 0 2e-06
VREGENTRIMP regen_trim_p 0 0.7
VREGENTRIMN regen_trim_n 0 0.7
XREGENTRIMP regen_p regen_trim_p 0 0 sky130_fd_pr__nfet_01v8 W=0.5 L=0.15
XREGENTRIMN regen_n regen_trim_n 0 0 sky130_fd_pr__nfet_01v8 W=0.5 L=0.15
CCP regen_p gate_n 100f
CCN regen_n gate_p 100f
VRESETB resetb 0 PULSE(1.8 0 5.000n 20p 20p 5n 10n)
XEQ lat_p resetb lat_n 0 sky130_fd_pr__nfet_01v8 W=2 L=0.15


RGP gate_p gate_bias 100000000000
RGN gate_n gate_bias 100000000000
VCLB clkb 0 PULSE(1.8 0 5.000n 20p 20p 5n 10n)
XPREP vdd clk_latch lat_p vdd sky130_fd_pr__pfet_01v8 W=6 L=0.15
XPREN vdd clk_latch lat_n vdd sky130_fd_pr__pfet_01v8 W=6 L=0.15
XLP lat_p lat_n vdd vdd sky130_fd_pr__pfet_01v8 W=6 L=0.15
XLN lat_p lat_n eval 0 sky130_fd_pr__nfet_01v8 W=3 L=0.15
XRP lat_n lat_p vdd vdd sky130_fd_pr__pfet_01v8 W=6 L=0.15
XRN lat_n lat_p eval 0 sky130_fd_pr__nfet_01v8 W=3 L=0.15
XINP lat_p gate_p tail 0 sky130_fd_pr__nfet_01v8 W=10 L=0.15
XINN lat_n gate_n tail 0 sky130_fd_pr__nfet_01v8 W=10 L=0.15
XTAIL tail clk_latch 0 0 sky130_fd_pr__nfet_01v8 W=20 L=0.15
XEVAL eval clk_latch 0 0 sky130_fd_pr__nfet_01v8 W=20 L=0.15
CLATP lat_p 0 5f
CLATN lat_n 0 5f
.ic v(sense_p)=0.9 v(gate_p)=0.9 v(gate_n)=0.9 v(sense_n)=0.9 v(pre_p)=1.0 v(pre_n)=1.0 v(out_p)=1.0 v(out_n)=1.0
.tran 20p 12n
.measure tran sense_p_after_v FIND v(sense_p) AT=2.60n
.measure tran sense_n_after_v FIND v(sense_n) AT=2.60n
.measure tran pre_p_after_v FIND v(pre_p) AT=2.60n
.measure tran pre_n_after_v FIND v(pre_n) AT=2.60n
.measure tran out_p_after_v FIND v(out_p) AT=2.60n
.measure tran out_n_after_v FIND v(out_n) AT=2.60n
.measure tran live_out_p_v FIND v(out_p) AT=4.800n
.measure tran live_out_n_v FIND v(out_n) AT=4.800n
.measure tran gate_p_cal_v FIND v(gate_p) AT=4.800n
.measure tran gate_n_cal_v FIND v(gate_n) AT=4.800n
.measure tran gate_p_eval_v FIND v(gate_p) AT=5.350n
.measure tran gate_n_eval_v FIND v(gate_n) AT=5.350n
.measure tran lat_p_final_v FIND v(lat_p) AT=9.600n
.measure tran lat_n_final_v FIND v(lat_n) AT=9.600n
.measure tran latch_output_diff_v PARAM='lat_n_final_v-lat_p_final_v'
.measure tran gain_p_v FIND v(gain_p) AT=4.800n
.measure tran gain_n_v FIND v(gain_n) AT=4.800n
.measure tran gain_diff_v PARAM='gain_p_v-gain_n_v'
.measure tran active_rx_p_v FIND v(rx_p) AT=4.800n
.measure tran active_rx_n_v FIND v(rx_n) AT=4.800n
.measure tran active_rx_p_eval_v FIND v(rx_p) AT=5.350n
.measure tran active_rx_n_eval_v FIND v(rx_n) AT=5.350n
.control
set noaskquit
run
.endc
.end
