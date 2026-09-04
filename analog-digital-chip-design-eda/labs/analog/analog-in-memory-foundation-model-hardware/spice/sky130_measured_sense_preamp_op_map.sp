* Measured-sense preamp DC operating-point map.

.lib "/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice" tt
.param vdd=1.8
.param rd=100000
.param itail=2e-05
.param win=8
.param lmin=0.15

VDD vdd 0 {vdd}
VINP inp 0 0.900033500000
VINN inn 0 0.899966500000
RDP vdd pre_p {rd}
RDN vdd pre_n {rd}
XPREP pre_p inp tail 0 sky130_fd_pr__nfet_01v8 W={win} L={lmin}
XPREN pre_n inn tail 0 sky130_fd_pr__nfet_01v8 W={win} L={lmin}
ITAIL tail 0 {itail}
CPREP pre_p 0 2f
CPREN pre_n 0 2f

.op
.control
set noaskquit
op
.endc

.end
