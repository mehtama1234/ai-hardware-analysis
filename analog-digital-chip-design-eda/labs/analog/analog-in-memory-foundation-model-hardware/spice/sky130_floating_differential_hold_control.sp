* Sky130-library floating differential hold control.
* The held nodes are initialized floating capacitors. Charge injection is explicit and measured.

.lib "/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice" tt
.options method=gear reltol=1e-3 abstol=1e-12 vntol=1e-6

CSTOREP hp 0 0.2p
CSTOREN hn 0 0.2p
RLEAKP hp 0 100G
RLEAKN hn 0 100G
IINJP hp 0 PWL(0 0 7.02n 0 7.021n -5.000000000000001e-05 7.04n -5.000000000000001e-05 7.041n 0 10n 0)
IINJN hn 0 PWL(0 0 7.02n 0 7.021n -5.000000000000001e-05 7.04n -5.000000000000001e-05 7.041n 0 10n 0)

.ic v(hp)=0.91 v(hn)=0.89
.tran 20p 10n uic
.measure tran acquired_p_v FIND v(hp) AT=6.8n
.measure tran acquired_n_v FIND v(hn) AT=6.8n
.measure tran held_p_v FIND v(hp) AT=8.5n
.measure tran held_n_v FIND v(hn) AT=8.5n
.control
run
.endc

.end
