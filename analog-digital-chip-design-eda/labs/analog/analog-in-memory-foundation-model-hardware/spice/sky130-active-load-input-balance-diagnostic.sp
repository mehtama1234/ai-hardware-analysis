* Extracted input-branch balance diagnostic; structural models only.
.global VSUBS
.model LATCH_NMOS nmos level=1 kp=200u vto=0.55 lambda=0.02
.model SENSE_P_NMOS nmos level=1 kp=200u vto=0.55 lambda=0.02
.model SENSE_N_NMOS nmos level=1 kp=1600u vto=0.55 lambda=0.02
.model LOAD_PMOS pmos level=1 kp=25u vto=-0.55 lambda=0.02
.options method=gear maxord=1 reltol=1e-4 abstol=1e-12 gmin=1e-9
* NGSPICE file created from sky130_latch_precharge_tail_active_load_flat.ext - technology: sky130A

.subckt sky130_latch_precharge_tail_active_load_flat out_p out_n sense_p sense_n tail
+ reset vdd vss eval
M0 out_p out_n tail VSUBS LATCH_NMOS ad=3.36 pd=8 as=3.12 ps=7.6 w=1.2 l=0.6
M1 out_n sense_n tail VSUBS SENSE_N_NMOS ad=3.36 pd=8 as=3.12 ps=7.6 w=1.2 l=0.6
M2 out_n out_p vdd_active w_400_8300# LOAD_PMOS ad=3.36 pd=8 as=3.12 ps=7.6 w=1.2 l=0.6
M3 out_n out_p tail VSUBS LATCH_NMOS ad=3.36 pd=8 as=3.12 ps=7.6 w=1.2 l=0.6
M4 out_n reset vdd w_12400_300# LOAD_PMOS ad=3.36 pd=8 as=3.12 ps=7.6 w=1.2 l=0.6
M5 out_p sense_p tail VSUBS SENSE_P_NMOS ad=3.36 pd=8 as=3.12 ps=7.6 w=1.2 l=0.6
M6 tail eval vss VSUBS LATCH_NMOS ad=16.8 pd=17.6 as=15.6 ps=17.2 w=6 l=0.6
M7 out_p out_n vdd_active w_400_8300# LOAD_PMOS ad=3.36 pd=8 as=3.12 ps=7.6 w=1.2 l=0.6
M8 out_p reset vdd w_12400_300# LOAD_PMOS ad=3.36 pd=8 as=3.12 ps=7.6 w=1.2 l=0.6
C0 out_p sense_n 0.00703f
C1 vdd out_p 0.28588f
C2 tail sense_p 0.18959f
C3 out_n w_12400_300# 0.70572f
C4 out_n tail 2.28538f
C5 vdd reset 0.20878f
C6 out_p reset 0.07615f
C7 eval tail 0.09415f
C8 vss out_n 0.06009f
C9 vdd w_12400_300# 1.53672f
C10 vdd_active w_400_8300# 1.45314f
C11 tail sense_n 0.1962f
C12 out_n vdd_active 0.41731f
C13 vss eval 0.04634f
C14 out_p w_12400_300# 0.76428f
C15 out_p tail 3.33055f
C16 out_n w_400_8300# 3.73158f
C17 reset w_12400_300# 4.03573f
C18 vss out_p 0.1661f
C19 eval out_n 0.02298f
C20 out_p vdd_active 1.78838f
C21 out_n sense_n 0.04664f
C22 vdd out_n 0.07263f
C23 out_p sense_p 0.04035f
C24 out_p w_400_8300# 3.33197f
C25 out_p out_n 1.90148f
C26 eval out_p 0.04062f
C27 out_n reset 0.05967f
C28 vss tail 0.19272f
C29 vdd VSUBS 0.90789f
C30 tail VSUBS 20.48017f
C31 vss VSUBS 0.75002f
C32 out_p VSUBS 7.58735f
C33 vdd_active VSUBS 18.81513f
C34 w_12400_300# VSUBS 30f
C35 w_400_8300# VSUBS 45f
.ends


VDD vdd 0 1.8
VDD_ACTIVE vdd_active 0 1.8
VSS vss 0 0
VSUB VSUBS 0 0
VSP sense_p 0 PULSE(0.9 1.15 0.50n 20p 20p 20n 40n)
VSN sense_n 0 PULSE(0.9 0.65 0.50n 20p 20p 20n 40n)
VRESET reset 0 PULSE(0 1.8 2.00n 20p 20p 18n 20n)
VEVAL eval 0 PULSE(0 1.8 2.10n 20p 20p 7n 20n)
XU out_p out_n sense_p sense_n tail reset vdd vss eval sky130_latch_precharge_tail_active_load_flat
.ic v(out_p)=1.8 v(out_n)=1.8
.tran 20p 10n uic
.measure tran out_p_eval FIND v(out_p) AT=4.00n
.measure tran out_n_eval FIND v(out_n) AT=4.00n
.measure tran output_diff_eval PARAM='out_p_eval-out_n_eval'
.control
run
.endc
.end
