path search +../cells
load sky130_transistor_active_isolation_pair -force
select top cell
drc on
drc catchup
drc statistics
drc count
quit -noprompt
