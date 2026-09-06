load sky130_isolated_frontend_active_load_latch_v2 -force
select top cell
extract all
ext2spice lvs
ext2spice hierarchy off
ext2spice cthresh 0
ext2spice rthresh 0
ext2spice -o extracted.spice
quit -noprompt
