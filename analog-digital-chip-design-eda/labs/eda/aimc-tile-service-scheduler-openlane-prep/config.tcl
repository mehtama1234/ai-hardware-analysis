set ::env(DESIGN_NAME) aimc_tile_service_scheduler_physical
set ::env(VERILOG_FILES) "$::env(DESIGN_DIR)/src/aimc_tile_service_scheduler.v $::env(DESIGN_DIR)/src/aimc_tile_service_scheduler_physical.v"
set ::env(CLOCK_PORT) clk
set ::env(CLOCK_NET) $::env(CLOCK_PORT)
set ::env(CLOCK_PERIOD) 5.000
set ::env(SIGNOFF_SDC_FILE) "$::env(DESIGN_DIR)/src/constraint.sdc"
set ::env(FP_PIN_ORDER_CFG) "$::env(DESIGN_DIR)/pin_order.cfg"
set ::env(FP_CORE_UTIL) 30
set ::env(FP_ASPECT_RATIO) 1
set ::env(PL_TARGET_DENSITY) 0.42
set ::env(DIE_AREA) "0 0 80 80"
set ::env(DESIGN_IS_CORE) 0
set ::env(RUN_HEURISTIC_DIODE_INSERTION) 1
