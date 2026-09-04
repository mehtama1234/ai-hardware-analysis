* Sky130 preamp OP latch debug.
* DC operating point only: no transient startup and no regenerative latch.

.lib "/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice" tt
.param vdd=1.8
.param lmin=0.15
.param rd=100k
.param itail=20u
.param win=8.0
.param vinp=0.900076485293
.param vinn=0.899923514707

VDD vdd 0 {vdd}
VINP inp 0 {vinp}
VINN inn 0 {vinn}
RDP vdd pre_p {rd}
RDN vdd pre_n {rd}
XPREP pre_p inp tail 0 sky130_fd_pr__nfet_01v8 W={win} L={lmin}
XPREN pre_n inn tail 0 sky130_fd_pr__nfet_01v8 W={win} L={lmin}
ITAIL tail 0 {itail}
CPREP pre_p 0 2f
CPREN pre_n 0 2f

.op
.control
op
.endc
.end
