`timescale 1ns/1ps
module aimc_multi_clock_control_subsystem_tb;
    reg core_clk = 0, maintenance_clk = 0, rst_n = 0;
    reg maintenance_budget_async = 0, sample_valid = 0, resident_weights = 1, tile_enabled = 1;
    reg [3:0] op_class = 4'd1;
    reg [7:0] tile_id = 0, requested_tile_id = 0, weak_tiles = 0;
    reg [11:0] adc_code = 12'd160;
    reg signed [8:0] zero_code = 9'sd128, gain_q6 = 9'sd64;
    reg signed [15:0] bias = 0;
    reg [7:0] estimated_state_error = 8'd10, state_error_budget = 8'd100;
    reg [7:0] attention_flip_rate = 0, attention_flip_budget = 8'd15;
    reg [7:0] token_flip_rate = 0, token_flip_budget = 8'd15;
    reg [9:0] residual_abs = 10'd3, residual_budget = 10'd20;
    reg [15:0] calibration_age = 16'd32;
    reg calibration_done = 0, probe_request = 0, probe_passed = 0, probe_failed = 0;
    reg analog_candidate = 1;
    reg [1:0] tile1_health_action = 0, tile2_health_action = 0, tile3_health_action = 0;
    reg [3:0] tile_busy = 0, drift_age = 0;
    reg [7:0] sensitivity_q8 = 0, cumulative_error_q8 = 0;
    wire signed [15:0] corrected_value;
    wire [3:0] controller_reason, governor_reason;
    wire [7:0] last_fallback_tile_id, next_cumulative_error_q8;
    wire [15:0] fallback_count, accepted_count, residual_fallback_count, stale_fallback_count;
    wire [1:0] tile0_health_action, selected_tile;
    wire maintenance_budget_core;
    wire [1:0] final_decision;
    wire [1:0] execution_path;

    aimc_multi_clock_control_subsystem dut (.*);
    always #5 core_clk = ~core_clk;
    always #7 maintenance_clk = ~maintenance_clk;

    initial begin
        repeat (2) @(negedge core_clk);
        rst_n = 1;
        @(negedge maintenance_clk) maintenance_budget_async = 1;
        repeat (5) @(posedge core_clk);
        if (maintenance_budget_core !== 1'b1) begin $display("FAIL CDC budget did not synchronize"); $finish; end
        @(negedge core_clk) sample_valid = 1;
        #1;
        if (final_decision !== 2'd1) begin $display("FAIL governor did not select analog during request"); $finish; end
        @(negedge core_clk) sample_valid = 0;
        repeat (4) @(posedge core_clk);
        if (execution_path !== 2'd1) begin $display("FAIL analog path was not accepted"); $finish; end
        $display("PASS aimc_multi_clock_control_subsystem_tb");
        $finish;
    end
endmodule
