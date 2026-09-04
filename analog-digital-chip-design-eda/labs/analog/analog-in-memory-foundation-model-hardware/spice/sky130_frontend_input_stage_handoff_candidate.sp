* Combined extracted frontend plus bounded active-gain handoff candidate.
* The frontend is the Magic-extracted ultra-sense capacitance network.
* The active input stage is represented by a bounded voltage-controlled gain macro using measured local gain.
* This is a same-deck handoff run, not a Sky130 transistor input-stage proof.

.global VSUBS
.include "/home/mehtama1/git-repo/analog-digital-chip-design-eda/labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/extracted/sky130_ultra_sense_capacitive_frontend_extracted.spice"
.param gain=9.201769060683
.param vcm=0.9
.param vdd=1.8

VDD vdd 0 {vdd}
VSS vss 0 0
VSUB VSUBS 0 0
VSP sp 0 PULSE(0 0.900076485293 0.05n 20p 20p 20n 40n)
VSN sn 0 PULSE(0 0.899923514707 0.05n 20p 20p 20n 40n)
VCS clk_sample 0 PULSE(0 {vdd} 1.00n 20p 20p 5n 10n)
VCL clk_latch 0 PULSE(0 {vdd} 2.00n 20p 20p 5n 10n)
VCM vcm_reset 0 PULSE(0.9 1.8 0.50n 20p 20p 0.50n 2n)

XFRONT vss vdd sp sense_p clk_sample vcm_reset clk_latch sense_n sn sky130_ultra_sense_capacitive_frontend
RBIASP sense_p vcm_reset 100G
RBIASN sense_n vcm_reset 100G

VOUTPCM outp_cm 0 {vcm}
VOUTNCM outn_cm 0 {vcm}
EOUTP outp outp_cm sense_n sense_p 4.600884530341
EOUTN outn outn_cm sense_p sense_n 4.600884530341
COUTP outp 0 2.000e-15
COUTN outn 0 2.000e-15
ROUTP outp 0 100G
ROUTN outn 0 100G

.tran 2p 3n
.measure tran sample_p_after_v FIND v(sp) AT=2.60n
.measure tran sample_n_after_v FIND v(sn) AT=2.60n
.measure tran sense_p_after_v FIND v(sense_p) AT=2.60n
.measure tran sense_n_after_v FIND v(sense_n) AT=2.60n
.measure tran outp_after_v FIND v(outp) AT=2.60n
.measure tran outn_after_v FIND v(outn) AT=2.60n
.control
run
.endc
.end
