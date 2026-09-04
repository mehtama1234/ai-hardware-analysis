* Sky130 preamp-alone latch debug.
* No regenerative latch is attached. This checks whether the preamp itself settles.

.lib "/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice" tt
.param vdd=1.8
.param lmin=0.15
.param rd=100k
.param itail=20u
.param win=8.0
.param vinp=0.900076485293
.param vinn=0.899923514707
.options method=gear reltol=1e-3 abstol=1e-14 vntol=1e-7 gmin=1e-12

VDD vdd 0 {vdd}
VINP inp 0 PWL(0 0.9 100p 0.9 500p {vinp} 2n {vinp})
VINN inn 0 PWL(0 0.9 100p 0.9 500p {vinn} 2n {vinn})
RDP vdd pre_p {rd}
RDN vdd pre_n {rd}
XPREP pre_p inp tail 0 sky130_fd_pr__nfet_01v8 W={win} L={lmin}
XPREN pre_n inn tail 0 sky130_fd_pr__nfet_01v8 W={win} L={lmin}
ITAIL tail 0 {itail}
CPREP pre_p 0 2f
CPREN pre_n 0 2f

.ic v(pre_p)=1.0 v(pre_n)=1.0 v(tail)=0.25
.tran 20p 2n uic
.measure tran pre_p_1p2n_v FIND v(pre_p) AT=1.20n
.measure tran pre_n_1p2n_v FIND v(pre_n) AT=1.20n
.measure tran pre_p_1p6n_v FIND v(pre_p) AT=1.60n
.measure tran pre_n_1p6n_v FIND v(pre_n) AT=1.60n
.measure tran pre_p_2n_v FIND v(pre_p) AT=2.00n
.measure tran pre_n_2n_v FIND v(pre_n) AT=2.00n
.measure tran tail_2n_v FIND v(tail) AT=2.00n
.control
set noaskquit
run
.endc
.end
