* Measured-sense preamp bias sweep.
* No extracted frontend. The input is the measured frontend sense voltage.

.lib "/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice" tt
.param vdd=1.8
.param rd=180000
.param itail=5e-06
.param win=4
.param lmin=0.15
.options method=gear reltol=1e-3 abstol=1e-14 vntol=1e-7 gmin=1e-12

VDD vdd 0 {vdd}
VINP inp 0 PWL(0 0.9 100p 0.9 700p 0.900033500000 2n 0.900033500000)
VINN inn 0 PWL(0 0.9 100p 0.9 700p 0.899966500000 2n 0.899966500000)
RDP vdd pre_p {rd}
RDN vdd pre_n {rd}
XPREP pre_p inp tail 0 sky130_fd_pr__nfet_01v8 W={win} L={lmin}
XPREN pre_n inn tail 0 sky130_fd_pr__nfet_01v8 W={win} L={lmin}
ITAIL tail 0 {itail}
CPREP pre_p 0 2f
CPREN pre_n 0 2f

.ic v(pre_p)=0.8 v(pre_n)=0.8 v(tail)=0.231
.tran 100p 2n uic
.measure tran pre_p_end_v FIND v(pre_p) AT=2n
.measure tran pre_n_end_v FIND v(pre_n) AT=2n
.measure tran tail_end_v FIND v(tail) AT=2n
.control
set noaskquit
run
.endc
.end
