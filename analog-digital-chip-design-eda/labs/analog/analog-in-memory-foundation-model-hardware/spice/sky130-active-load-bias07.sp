* Two-stage transistor preamp attached to extracted Sky130 frontend.
.global VSUBS
.lib "/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice" tt
.include "/home/mehtama1/git-repo/ai-hardware-analysis/analog-digital-chip-design-eda/labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/extracted/sky130_ultra_sense_capacitive_frontend_extracted.spice"
.param vdd=1.8
.param lmin=0.15
.param rd1=500k
.param rd2=500k
.param itail1=4u
.param itail2=4u
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
RDP1 vdd pre_p {rd1}
RDN1 vdd pre_n {rd1}
XINP1 pre_p sense_p tail1 0 sky130_fd_pr__nfet_01v8 W={w1} L={lmin}
XINN1 pre_n sense_n tail1 0 sky130_fd_pr__nfet_01v8 W={w1} L={lmin}
ITAIL1 tail1 0 {itail1}
VBIAS_LOAD bias_load 0 0.700000
XLOADP out_p bias_load vdd vdd sky130_fd_pr__pfet_01v8 W=4 L=0.15
XLOADN out_n bias_load vdd vdd sky130_fd_pr__pfet_01v8 W=4 L=0.15
XINP2 out_p pre_p tail2 0 sky130_fd_pr__nfet_01v8 W={w2} L={lmin}
XINN2 out_n pre_n tail2 0 sky130_fd_pr__nfet_01v8 W={w2} L={lmin}
ITAIL2 tail2 0 {itail2}
COUTP out_p 0 2f
COUTN out_n 0 2f
.ic v(sense_p)=0.9 v(sense_n)=0.9 v(pre_p)=1.0 v(pre_n)=1.0 v(out_p)=1.0 v(out_n)=1.0
.tran 20p 3n
.measure tran sense_p_after_v FIND v(sense_p) AT=2.60n
.measure tran sense_n_after_v FIND v(sense_n) AT=2.60n
.measure tran pre_p_after_v FIND v(pre_p) AT=2.60n
.measure tran pre_n_after_v FIND v(pre_n) AT=2.60n
.measure tran out_p_after_v FIND v(out_p) AT=2.60n
.measure tran out_n_after_v FIND v(out_n) AT=2.60n
.control
set noaskquit
run
.endc
.end
