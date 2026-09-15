source $::env(DESIGN_DIR)/config.tcl

# The restored OpenLane/Sky130 diode model has zero ANTENNADIFFAREA. Disable
# both insertion paths for a diagnostic route/STA run; antenna signoff remains
# an explicit unresolved gate in the resulting report.
set ::env(RUN_HEURISTIC_DIODE_INSERTION) 0
set ::env(GRT_REPAIR_ANTENNAS) 0
