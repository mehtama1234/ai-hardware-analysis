load aimc_converter_macro_active_candidate -force
select top cell
drc check
drc count
extract all
ext2spice lvs
ext2spice cthresh 0
ext2spice rthresh 0
ext2spice -o aimc_converter_macro_active_candidate_extracted.spice
quit -noprompt
