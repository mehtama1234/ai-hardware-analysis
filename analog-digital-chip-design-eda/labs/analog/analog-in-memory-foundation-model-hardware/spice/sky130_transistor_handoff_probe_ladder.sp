* Probe D: extracted frontend drives transistor gates through large isolation.
.global VSUBS
.lib "/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice" tt
.include "/home/mehtama1/git-repo/analog-digital-chip-design-eda/labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/extracted/sky130_ultra_sense_capacitive_frontend_extracted.spice"
VSUB VSUBS 0 0
VDD_SRC vdd 0 1.8
VSS vss 0 0
VSP sp 0 PULSE(0 0.900076485293 0.05n 20p 20p 20n 40n)
VSN sn 0 PULSE(0 0.899923514707 0.05n 20p 20p 20n 40n)
VCS clk_sample 0 PULSE(0 1.8 1.00n 20p 20p 5n 10n)
VCL clk_latch 0 PULSE(0 1.8 2.00n 20p 20p 5n 10n)
VCM vcm_reset 0 0.9
XFRONT vss vdd sp sense_p clk_sample vcm_reset clk_latch sense_n sn sky130_ultra_sense_capacitive_frontend
RBIASP sense_p vcm_reset 100G
RBIASN sense_n vcm_reset 100G
RGP sense_p gate_p 1Meg
RGN sense_n gate_n 1Meg
RGBP gate_p vcm_reset 100Meg
RGBN gate_n vcm_reset 100Meg

.param vdd=1.8
.param rd=100k
.param itail=20u
.param wn=8.0
.param lmin=0.15
.options method=trap reltol=1e-3 abstol=1e-14 vntol=1e-7

VDD vdd 0 {vdd}
RDP vdd outp {rd}
RDN vdd outn {rd}
XINP outp gate_p tail 0 sky130_fd_pr__nfet_01v8 W={wn} L={lmin}
XINN outn gate_n tail 0 sky130_fd_pr__nfet_01v8 W={wn} L={lmin}
ITAIL tail 0 {itail}
COUTP outp 0 2f
COUTN outn 0 2f

.tran 20p 3n
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
