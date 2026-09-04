* Sky130 comparator input-stage polarity proxy.
* This is a transistor differential-pair input stage with ideal bias and resistive loads.
* It is not a clocked latch and not a noise simulation.

.lib "/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice" tt
.param vdd=1.8
.param lmin=0.15
.param wn=8.0
.param vinp=0.899923514707
.param vinn=0.900076485293
.param rd=100k
.param itail=20u

VDD vdd 0 {vdd}
VINP inp 0 {vinp}
VINN inn 0 {vinn}
RDP vdd outp {rd}
RDN vdd outn {rd}
XINP outp inp tail 0 sky130_fd_pr__nfet_01v8 W={wn} L={lmin}
XINN outn inn tail 0 sky130_fd_pr__nfet_01v8 W={wn} L={lmin}
ITAIL tail 0 {itail}
COUTP outp 0 2f
COUTN outn 0 2f

.op
.control
op
.endc

.end
