set ::env(DESIGN_NAME) aimc_multi_clock_control_subsystem
set ::env(VERILOG_FILES) "$::env(DESIGN_DIR)/src/aimc_multi_clock_control_subsystem.v $::env(DESIGN_DIR)/src/aimc_micro_tile_controller.v $::env(DESIGN_DIR)/src/aimc_operation_partition.v $::env(DESIGN_DIR)/src/aimc_tile_readout.v $::env(DESIGN_DIR)/src/aimc_scheduler_governor.v $::env(DESIGN_DIR)/src/aimc_tile_service_scheduler.v $::env(DESIGN_DIR)/src/aimc_error_budget_governor.v"
set ::env(CLOCK_PORT) core_clk
set ::env(CLOCK_NET) $::env(CLOCK_PORT)
set ::env(CLOCK_PERIOD) 10.000
set ::env(BASE_SDC_FILE) "$::env(DESIGN_DIR)/src/base_multi_clock.sdc"
set ::env(SIGNOFF_SDC_FILE) "$::env(DESIGN_DIR)/src/constraint.sdc"
set ::env(FP_PIN_ORDER_CFG) "$::env(DESIGN_DIR)/pin_order.cfg"
set ::env(FP_CORE_UTIL) 30
set ::env(FP_ASPECT_RATIO) 1
set ::env(PL_TARGET_DENSITY) 0.40
set ::env(DIE_AREA) "0 0 220 220"
set ::env(DESIGN_IS_CORE) 0
set ::env(RUN_HEURISTIC_DIODE_INSERTION) 1
set ::env(DIODE_ON_PORTS) in
set ::env(VSRC_LOC_FILES) "VPWR $::env(DESIGN_DIR)/src/vsrc_vpwr.loc VGND $::env(DESIGN_DIR)/src/vsrc_vgnd.loc"
set ::env(CTS_MULTICORNER_LIB) 0
set ::env(CTS_SINK_CLUSTERING_SIZE) 8
set ::env(CTS_SINK_CLUSTERING_MAX_DIAMETER) 12
set ::env(CTS_DISABLE_POST_PROCESSING) 1
set ::env(CTS_REPORT_TIMING) 0
