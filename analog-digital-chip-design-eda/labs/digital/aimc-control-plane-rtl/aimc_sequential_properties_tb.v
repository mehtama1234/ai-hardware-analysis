`timescale 1ns/1ps
module aimc_sequential_properties_tb;
  reg core_clk=0, maintenance_clk=0, rst_n=0;
  reg maintenance_budget_async=0, sample_valid=0, resident_weights=1, tile_enabled=1;
  reg [3:0] op_class=4'd1;
  reg [7:0] tile_id=0, requested_tile_id=0, weak_tiles=0;
  reg [11:0] adc_code=12'd160;
  reg signed [8:0] zero_code=9'sd128, gain_q6=9'sd64;
  reg signed [15:0] bias=0;
  reg [7:0] estimated_state_error=8'd10, state_error_budget=8'd100;
  reg [7:0] attention_flip_rate=0, attention_flip_budget=8'd15;
  reg [7:0] token_flip_rate=0, token_flip_budget=8'd15;
  reg [9:0] residual_abs=10'd3, residual_budget=10'd20;
  reg [15:0] calibration_age=16'd32;
  reg calibration_done=0, probe_request=0, probe_passed=0, probe_failed=0;
  reg analog_candidate=1;
  reg [1:0] tile1_health_action=0, tile2_health_action=0, tile3_health_action=0;
  reg [3:0] tile_busy=0, drift_age=0;
  reg [7:0] sensitivity_q8=0, cumulative_error_q8=0;
  wire signed [15:0] corrected_value;
  wire [1:0] execution_path, final_decision, selected_tile;
  wire [3:0] controller_reason, governor_reason;
  wire [7:0] last_fallback_tile_id, next_cumulative_error_q8;
  wire [15:0] fallback_count, accepted_count, residual_fallback_count, stale_fallback_count;
  wire [1:0] tile0_health_action;
  wire maintenance_budget_core;
  integer failures=0;

  aimc_multi_clock_control_subsystem dut(.*);
  always #5 core_clk=~core_clk;
  always #7 maintenance_clk=~maintenance_clk;

  task check;
    input condition;
    input [8*80-1:0] property_name;
    begin
      if (!condition) begin
        $display("FAIL property=%0s", property_name);
        failures = failures + 1;
      end else $display("PASS property=%0s", property_name);
    end
  endtask

  initial begin
    repeat (2) @(negedge core_clk);
    #1;
    check(!rst_n && maintenance_budget_core === 1'b0 && execution_path === 2'd0 && fallback_count === 16'd0 && accepted_count === 16'd0, "reset_determinism");
    rst_n=1;

    // The maintenance value must cross through maintenance sampling and two
    // core-domain synchronizer stages, never appearing after only one core edge.
    @(negedge maintenance_clk) maintenance_budget_async=1'b1;
    @(posedge maintenance_clk);
    @(posedge core_clk); #1;
    check(maintenance_budget_core === 1'b0, "cdc_not_visible_after_one_core_edge");
    @(posedge core_clk); #1;
    check(maintenance_budget_core === 1'b1, "cdc_visible_after_two_core_edges");

    // Registered inputs and the readout pipeline must produce a nominal accept.
    @(negedge core_clk) sample_valid=1'b1;
    @(negedge core_clk) sample_valid=1'b0;
    repeat (5) @(posedge core_clk);
    #1;
    check(execution_path === 2'd1 && accepted_count != 16'd0, "registered_nominal_acceptance");

    // A disabled tile must take the digital fallback and increment accounting.
    @(negedge core_clk) begin tile_enabled=1'b0; sample_valid=1'b1; end
    @(negedge core_clk) sample_valid=1'b0;
    repeat (5) @(posedge core_clk);
    #1;
    check(execution_path === 2'd0 && fallback_count != 16'd0, "disabled_tile_fallback_accounting");

    // Exercise both directions of the CDC path. Each transition is changed
    // before the maintenance-domain edge, then must remain hidden for one
    // core edge and become visible on the second.
    @(negedge maintenance_clk) maintenance_budget_async=1'b0;
    @(posedge maintenance_clk);
    @(posedge core_clk); #1;
    check(maintenance_budget_core === 1'b1, "cdc_second_transition_hidden_one_edge");
    @(posedge core_clk); #1;
    check(maintenance_budget_core === 1'b0, "cdc_second_transition_visible_two_edges");
    @(negedge maintenance_clk) maintenance_budget_async=1'b1;
    @(posedge maintenance_clk);
    @(posedge core_clk); #1;
    check(maintenance_budget_core === 1'b0, "cdc_third_transition_hidden_one_edge");
    @(posedge core_clk); #1;
    check(maintenance_budget_core === 1'b1, "cdc_third_transition_visible_two_edges");

    // Repeated nominal and disabled transactions must preserve accounting:
    // every accepted request increments the corresponding counter, and a
    // disabled tile cannot be counted as an analog acceptance.
    tile_enabled=1'b1;
    repeat (3) begin
      @(negedge core_clk) sample_valid=1'b1;
      @(negedge core_clk) sample_valid=1'b0;
      repeat (5) @(posedge core_clk);
    end
    tile_enabled=1'b0;
    repeat (3) begin
      @(negedge core_clk) sample_valid=1'b1;
      @(negedge core_clk) sample_valid=1'b0;
      repeat (5) @(posedge core_clk);
    end
    #1;
    check(accepted_count >= 16'd4, "repeated_acceptance_accounting");
    check(fallback_count >= 16'd4, "repeated_fallback_accounting");
    check(accepted_count + fallback_count == 16'd8, "acceptance_fallback_partition");

    // Asynchronous reset must erase accumulated state and release the
    // controller in its deterministic reset condition.
    @(negedge core_clk) rst_n=1'b0;
    #1;
    check(fallback_count === 16'd0 && accepted_count === 16'd0 && execution_path === 2'd0, "reset_recovery_clears_accounting");
    @(negedge core_clk) rst_n=1'b1;
    repeat (2) @(posedge core_clk);
    #1;
    check(fallback_count === 16'd0 && accepted_count === 16'd0, "reset_recovery_starts_clean");

    if (failures == 0) $display("PASS aimc_sequential_properties_tb");
    else $display("FAIL aimc_sequential_properties_tb failures=%0d", failures);
    $finish;
  end
endmodule
