set ::env(DESIGN_NAME) aimc_control_plane
set ::env(VERILOG_FILES) "$::env(DESIGN_DIR)/src/aimc_control_plane.v"
set ::env(CLOCK_PORT) clk
set ::env(CLOCK_NET) $::env(CLOCK_PORT)
set ::env(CLOCK_PERIOD) 10.000
set ::env(SIGNOFF_SDC_FILE) "$::env(DESIGN_DIR)/src/constraint.sdc"
set ::env(FP_PIN_ORDER_CFG) "$::env(DESIGN_DIR)/pin_order.cfg"
set ::env(FP_CORE_UTIL) 35
set ::env(FP_ASPECT_RATIO) 1
set ::env(PL_TARGET_DENSITY) 0.45
set ::env(DIE_AREA) "0 0 120 120"
set ::env(DESIGN_IS_CORE) 0
set ::env(RUN_HEURISTIC_DIODE_INSERTION) 1
set ::env(CTS_MULTICORNER_LIB) 0
set ::env(CTS_SINK_CLUSTERING_SIZE) 8
set ::env(CTS_SINK_CLUSTERING_MAX_DIAMETER) 12
set ::env(CTS_DISABLE_POST_PROCESSING) 1
set ::env(CTS_REPORT_TIMING) 0
