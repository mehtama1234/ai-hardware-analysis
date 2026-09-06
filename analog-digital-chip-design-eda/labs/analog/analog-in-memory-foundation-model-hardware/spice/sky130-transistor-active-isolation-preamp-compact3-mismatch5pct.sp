* Sky130 transistor active isolation before preamp.
* This replaces the ideal active-isolation macro with a small differential pair.
* It is schematic transistor evidence, not layout or accepted converter evidence.

.global VSUBS
.lib "/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice" tt
.include "/home/mehtama1/git-repo/ai-hardware-analysis/analog-digital-chip-design-eda/labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/extracted/sky130_ultra_sense_capacitive_frontend_extracted.spice"
.include "/home/mehtama1/git-repo/ai-hardware-analysis/analog-digital-chip-design-eda/labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/extracted/sky130_transistor_active_isolation_pair_extracted.spice"
.param vdd=1.800000
.param lmin=0.15
.options method=gear reltol=1e-3 abstol=1e-14 vntol=1e-7 chgtol=1e-16 gmin=1e-12
.temp 27.000000

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

RISO_P vdd iso_p 588000
RISO_N vdd iso_n 532000
XISO iso_tail iso_p iso_n sense_p sense_n sky130_transistor_active_isolation_pair
IISO_TAIL iso_tail 0 4e-06
CISO_P iso_p 0 2f
CISO_N iso_n 0 2f

RDP vdd pre_p 100000
RDN vdd pre_n 100000
XPREP pre_p iso_n pre_tail 0 sky130_fd_pr__nfet_01v8 W=4 L={lmin}
XPREN pre_n iso_p pre_tail 0 sky130_fd_pr__nfet_01v8 W=4 L={lmin}
IPRE_TAIL pre_tail 0 2e-05
CPREP pre_p 0 2f
CPREN pre_n 0 2f

.ic v(sense_p)=0.9 v(sense_n)=0.9 v(iso_p)=1.2 v(iso_n)=1.2 v(iso_tail)=0.25 v(pre_p)=1.0 v(pre_n)=1.0 v(pre_tail)=0.25
.tran 20p 3n
.measure tran sample_p_after_v FIND v(sp) AT=2.60n
.measure tran sample_n_after_v FIND v(sn) AT=2.60n
.measure tran sense_p_after_v FIND v(sense_p) AT=2.60n
.measure tran sense_n_after_v FIND v(sense_n) AT=2.60n
.measure tran iso_p_after_v FIND v(iso_p) AT=2.60n
.measure tran iso_n_after_v FIND v(iso_n) AT=2.60n
.measure tran pre_p_after_v FIND v(pre_p) AT=2.60n
.measure tran pre_n_after_v FIND v(pre_n) AT=2.60n
.control
set noaskquit
run
.endc
.end
