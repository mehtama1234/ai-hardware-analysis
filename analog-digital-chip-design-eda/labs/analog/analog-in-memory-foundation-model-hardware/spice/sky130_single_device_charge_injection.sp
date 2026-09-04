* Sky130 single-device charge injection fixture.
* One nfet samples a DC input onto a capacitor; the gate edge then disturbs the held node.

.lib "/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice" tt
.param vdd=1.8
.param lmin=0.15
.param wn=2.0
.param csample=1.0p
.param vin=0.9

VDD vdd 0 {vdd}
VSS vss 0 0
VIN in 0 PULSE(0 {vin} 0.1n 20p 20p 20n 40n)
VG ctrl 0 PULSE(0 {vdd} 0.2n 20p 20p 7n 20n)
XEDGE in ctrl hold vss sky130_fd_pr__nfet_01v8 W={wn} L={lmin}
CSAMPLE hold 0 {csample}
RLEAK hold 0 100G

.tran 2p 10n
.measure tran before_edge_v FIND v(hold) AT=6.8n
.measure tran after_edge_v FIND v(hold) AT=8.5n
.measure tran input_v FIND v(in) AT=6.8n
.control
run
.endc

.end
