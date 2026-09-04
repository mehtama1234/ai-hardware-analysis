# Magic extraction smoke for the stronger sample-to-sense frontend starter cell.
# This produces physical-start evidence only, not accepted comparator proof.

drc off
load sky130_strong_sense_capacitive_frontend
select top cell
extract all
ext2spice lvs
ext2spice cthresh 0
ext2spice rthresh 0
ext2spice -o ../extracted/sky130_strong_sense_capacitive_frontend_extracted.spice
quit
