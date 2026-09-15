load preamp_n_nfet -force
select top cell
drc check
drc count
extract all
ext2spice lvs
ext2spice cthresh 0
ext2spice rthresh 0
ext2spice -o extracted.spice
quit -noprompt
