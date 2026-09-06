load combined_latch_capture -force
select top cell
drc on
drc catchup
drc count
drc listall why
extract all
ext2spice lvs
ext2spice hierarchy off
ext2spice subcircuit on
ext2spice subcircuit top on
ext2spice cthresh 0
ext2spice rthresh 0
ext2spice -o extracted.spice
quit -noprompt
