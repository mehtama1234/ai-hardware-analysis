source $::env(DESIGN_DIR)/config.tcl

# The Sky130 diode model in the restored local PDK reports zero
# ANTENNADIFFAREA. Leave antenna repair enabled, but do not pre-insert the
# heuristic diode that causes OpenROAD global routing to abort.
set ::env(RUN_HEURISTIC_DIODE_INSERTION) 0
