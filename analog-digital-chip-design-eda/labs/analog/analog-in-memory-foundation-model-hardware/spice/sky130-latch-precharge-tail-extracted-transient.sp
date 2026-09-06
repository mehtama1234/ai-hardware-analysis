* Flat extracted latch/precharge/tail structural transient.
.global VSUBS
.model LATCH_NMOS nmos level=1 kp=200u vto=0.55 lambda=0.02
.model PRECHARGE_PMOS pmos level=1 kp=100u vto=-0.55 lambda=0.02
* NGSPICE file created from sky130_latch_precharge_tail_flat.ext - technology: sky130A

.subckt sky130_latch_precharge_tail_flat out_p out_n sense_p sense_n tail reset vdd
+ vss eval
M0 out_p out_n tail VSUBS LATCH_NMOS ad=3.36 pd=8 as=3.12 ps=7.6 w=1.2 l=0.6
M1 out_n sense_n tail VSUBS LATCH_NMOS ad=3.36 pd=8 as=3.12 ps=7.6 w=1.2 l=0.6
M2 out_n out_p tail VSUBS LATCH_NMOS ad=3.36 pd=8 as=3.12 ps=7.6 w=1.2 l=0.6
M3 out_n reset vdd vdd PRECHARGE_PMOS ad=3.36 pd=8 as=3.12 ps=7.6 w=1.2 l=0.6
M4 out_p sense_p tail VSUBS LATCH_NMOS ad=3.36 pd=8 as=3.12 ps=7.6 w=1.2 l=0.6
M5 tail eval vss VSUBS LATCH_NMOS ad=16.8 pd=17.6 as=15.6 ps=17.2 w=6 l=0.6
M6 out_p reset vdd vdd PRECHARGE_PMOS ad=3.36 pd=8 as=3.12 ps=7.6 w=1.2 l=0.6
C0 out_p vdd 0.76428f
C1 out_p sense_p 0.04035f
C2 reset out_n 0.05967f
C3 eval vss 0.04634f
C4 out_p eval 0.04062f
C5 sense_n tail 0.1962f
C6 out_n vdd 0.70572f
C7 out_p vss 0.1661f
C8 out_n eval 0.02298f
C9 out_n vss 0.06009f
C10 out_n out_p 1.2488f
C11 sense_n out_p 0.00703f
C12 out_n sense_n 0.04664f
C13 reset vdd 0.20878f
C14 vdd vdd 1.53672f
C15 sense_p tail 0.18959f
C16 eval tail 0.09415f
C17 reset vdd 4.03573f
C18 tail vss 0.19272f
C19 out_p tail 3.33055f
C20 out_p vdd 0.28588f
C21 out_n tail 2.28538f
C22 out_n vdd 0.07263f
C23 reset out_p 0.07615f
C24 vdd VSUBS 0.90789f
C25 out_n VSUBS 11.59099f
C26 out_p VSUBS 0.98136f
C27 tail VSUBS 29.38712f
C28 vss VSUBS 0.75002f
C29 vdd VSUBS 30f
.ends


.options method=gear maxord=1 reltol=1e-4 abstol=1e-12 gmin=1e-9
VDD vdd 0 1.8
VSUB VSUBS 0 0
VSP sense_p 0 PULSE(0.9 0.905 0.50n 20p 20p 20n 40n)
VSN sense_n 0 PULSE(0.9 0.895 0.50n 20p 20p 20n 40n)
VRESET reset 0 PULSE(0 1.8 1.00n 20p 20p 19n 20n)
VEVAL eval 0 PULSE(0 1.8 1.10n 20p 20p 8n 20n)
XU out_p out_n sense_p sense_n tail reset vdd vss eval sky130_latch_precharge_tail_flat
.ic v(out_p)=1.8 v(out_n)=1.8
.tran 20p 10n uic
.measure tran out_p_released FIND v(out_p) AT=1.20n
.measure tran out_n_released FIND v(out_n) AT=1.20n
.measure tran out_p_final FIND v(out_p) AT=8.00n
.measure tran out_n_final FIND v(out_n) AT=8.00n
.measure tran output_diff_released PARAM='out_p_released-out_n_released'
.measure tran output_diff_final PARAM='out_p_final-out_n_final'
.control
run
.endc
.end
