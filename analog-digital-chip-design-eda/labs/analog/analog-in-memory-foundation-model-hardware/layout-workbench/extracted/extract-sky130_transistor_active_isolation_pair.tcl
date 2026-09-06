path search +../cells
load sky130_transistor_active_isolation_pair -force
select top cell
extract all
ext2spice lvs
ext2spice format ngspice
ext2spice -o sky130_transistor_active_isolation_pair_extracted.spice
quit -noprompt
