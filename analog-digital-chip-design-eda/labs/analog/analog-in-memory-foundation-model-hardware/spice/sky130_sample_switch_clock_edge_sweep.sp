* Sky130 transmission-gate clock-edge sweep.
* This keeps the known-running sample switch and changes only control edge time.

.lib "/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice" tt
.param vin=0.9
.param vdd=1.8
.param lmin=0.15
.param wn=2.0
.param wp=4.0
.param csample=0.2p
.param cload=0.05p

VDD vdd 0 {vdd}
VSS vss 0 0
VIN in 0 PULSE(0 {vin} 0.1n 20p 20p 20n 40n)
VCTRL ctrl 0 PULSE(0 {vdd} 0.2n 100.0p 100.0p 7n 20n)
VCTRLB ctrlb 0 PULSE({vdd} 0 0.2n 100.0p 100.0p 7n 20n)

XSWN in ctrl sample vss sky130_fd_pr__nfet_01v8 W={wn} L={lmin}
XSWP in ctrlb sample vdd sky130_fd_pr__pfet_01v8 W={wp} L={lmin}
CSAMPLE sample 0 {csample}
CLOAD sample 0 {cload}
RLEAK sample 0 100G

.tran 2p 10n
.measure tran acquired_v FIND v(sample) AT=6.8n
.measure tran held_v FIND v(sample) AT=8.5n
.measure tran input_v FIND v(in) AT=6.8n
.control
run
.endc

.end
