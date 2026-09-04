* Extracted frontend to Sky130 transistor gate startup.
* The extracted frontend is present and transient-driven.
* The transistor gate nodes are weakly assisted toward the measured sense voltages.
* This is not a full free gate handoff, latch, SAR loop, or accepted converter result.

.global VSUBS
.lib "/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice" tt
.include "/home/mehtama1/git-repo/analog-digital-chip-design-eda/labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/extracted/sky130_ultra_sense_capacitive_frontend_extracted.spice"
.param vdd=1.8
.param rd=100k
.param rtail=45k
.param wn=8.0
.param lmin=0.15
.options method=gear reltol=1e-3 abstol=1e-14 vntol=1e-7 chgtol=1e-16 gmin=1e-12

VDD vdd 0 {vdd}
VSS vss 0 0
VSUB VSUBS 0 0
VSP sp 0 PULSE(0 0.900076485293 0.05n 20p 20p 20n 40n)
VSN sn 0 PULSE(0 0.899923514707 0.05n 20p 20p 20n 40n)
VCS clk_sample 0 PULSE(0 {vdd} 1.00n 20p 20p 5n 10n)
VCL clk_latch 0 PULSE(0 {vdd} 2.00n 20p 20p 5n 10n)
VCM vcm_reset 0 PULSE(0.9 1.8 0.50n 20p 20p 0.50n 2n)

XFRONT vss vdd sp sense_p clk_sample vcm_reset clk_latch sense_n sn sky130_ultra_sense_capacitive_frontend
RBIASP sense_p 0 100G
RBIASN sense_n 0 100G

RGP sense_p gate_p 1Meg
RGN sense_n gate_n 1Meg
VGPRE gate_p_pre 0 PWL(0 0.9 0.60n 0.9 1.50n 0.900033500000 3n 0.900033500000)
VGNRE gate_n_pre 0 PWL(0 0.9 0.60n 0.9 1.50n 0.899966500000 3n 0.899966500000)
RPREP gate_p_pre gate_p 100k
RPREN gate_n_pre gate_n 100k

RDP vdd outp {rd}
RDN vdd outn {rd}
XINP outp gate_p tail 0 sky130_fd_pr__nfet_01v8 W={wn} L={lmin}
XINN outn gate_n tail 0 sky130_fd_pr__nfet_01v8 W={wn} L={lmin}
RTAIL tail 0 {rtail}
COUTP outp 0 2f
COUTN outn 0 2f

.ic v(sense_p)=0.9 v(sense_n)=0.9 v(gate_p)=0.9 v(gate_n)=0.9 v(outp)=1.0 v(outn)=1.0 v(tail)=0.25
.tran 20p 3n
.measure tran sample_p_after_v FIND v(sp) AT=2.60n
.measure tran sample_n_after_v FIND v(sn) AT=2.60n
.measure tran sense_p_after_v FIND v(sense_p) AT=2.60n
.measure tran sense_n_after_v FIND v(sense_n) AT=2.60n
.measure tran gate_p_after_v FIND v(gate_p) AT=2.60n
.measure tran gate_n_after_v FIND v(gate_n) AT=2.60n
.measure tran outp_after_v FIND v(outp) AT=2.60n
.measure tran outn_after_v FIND v(outn) AT=2.60n
.control
set noaskquit
run
.endc
.end
