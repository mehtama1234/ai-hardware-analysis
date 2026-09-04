# Magic extraction skeleton for the AIMC converter macro.
# Replace the placeholder cell names after real layout cells exist.

drc off
load aimc_converter_macro
select top cell
extract all
ext2spice lvs
ext2spice cthresh 0
ext2spice rthresh 0
ext2spice -o aimc_converter_macro_extracted.sp
quit
