`timescale 1ns/1ps

module aimc_micro_tile_controller_tb;
    reg clk = 0;
    reg rst_n = 0;
    reg sample_valid = 0;
    reg [3:0] op_class = 4'd1;
    reg resident_weights = 1;
    reg [7:0] tile_id = 8'd0;
    reg tile_enabled = 1;
    reg [11:0] adc_code = 12'd160;
    reg signed [8:0] zero_code = 9'sd128;
    reg signed [8:0] gain_q6 = 9'sd64;
    reg signed [15:0] bias = 16'sd0;
    reg [7:0] estimated_state_error = 8'd60;
    reg [7:0] state_error_budget = 8'd100;
    reg [7:0] attention_flip_rate = 8'd5;
    reg [7:0] attention_flip_budget = 8'd15;
    reg [7:0] token_flip_rate = 8'd5;
    reg [7:0] token_flip_budget = 8'd15;
    reg [9:0] residual_abs = 10'd3;
    reg [9:0] residual_budget = 10'd20;
    reg [15:0] calibration_age = 16'd32;
    reg [7:0] weak_tiles = 8'd1;
    reg calibration_done = 0;
    reg probe_request = 0;
    reg probe_passed = 0;
    reg probe_failed = 0;
    wire signed [15:0] corrected_value;
    wire [1:0] execution_path;
    wire [3:0] reason;
    wire [7:0] last_fallback_tile_id;
    wire [15:0] fallback_count;
    wire [15:0] accepted_count;
    wire [15:0] residual_fallback_count;
    wire [15:0] stale_fallback_count;
    wire [1:0] tile_health_action;

    aimc_micro_tile_controller dut (
        .clk(clk),
        .rst_n(rst_n),
        .sample_valid(sample_valid),
        .op_class(op_class),
        .resident_weights(resident_weights),
        .tile_id(tile_id),
        .tile_enabled(tile_enabled),
        .adc_code(adc_code),
        .zero_code(zero_code),
        .gain_q6(gain_q6),
        .bias(bias),
        .estimated_state_error(estimated_state_error),
        .state_error_budget(state_error_budget),
        .attention_flip_rate(attention_flip_rate),
        .attention_flip_budget(attention_flip_budget),
        .token_flip_rate(token_flip_rate),
        .token_flip_budget(token_flip_budget),
        .residual_abs(residual_abs),
        .residual_budget(residual_budget),
        .calibration_age(calibration_age),
        .weak_tiles(weak_tiles),
        .calibration_done(calibration_done),
        .probe_request(probe_request),
        .probe_passed(probe_passed),
        .probe_failed(probe_failed),
        .corrected_value(corrected_value),
        .execution_path(execution_path),
        .reason(reason),
        .last_fallback_tile_id(last_fallback_tile_id),
        .fallback_count(fallback_count),
        .accepted_count(accepted_count),
        .residual_fallback_count(residual_fallback_count),
        .stale_fallback_count(stale_fallback_count),
        .tile_health_action(tile_health_action)
    );

    always #5 clk = ~clk;

    task run_case;
        input [160*8:1] name;
        input [3:0] in_op_class;
        input in_resident_weights;
        input [7:0] in_tile_id;
        input in_tile_enabled;
        input [9:0] in_residual_abs;
        input [15:0] in_calibration_age;
        input [1:0] expected_path;
        input [3:0] expected_reason;
        input [7:0] expected_last_fallback_tile_id;
        input [15:0] expected_fallback_count;
        input [15:0] expected_accepted_count;
        input [15:0] expected_residual_fallback_count;
        input [15:0] expected_stale_fallback_count;
        input [1:0] expected_tile_health_action;
        begin
            @(negedge clk);
            op_class = in_op_class;
            resident_weights = in_resident_weights;
            tile_id = in_tile_id;
            tile_enabled = in_tile_enabled;
            residual_abs = in_residual_abs;
            calibration_age = in_calibration_age;
            sample_valid = 1'b1;
            @(negedge clk);
            sample_valid = 1'b0;
            @(negedge clk);
            #1;
            $display("%0s,path=%0d,reason=%0d,value=%0d,last_fallback_tile=%0d,fallback_count=%0d,accepted_count=%0d,residual_fallback_count=%0d,stale_fallback_count=%0d,tile_health_action=%0d", name, execution_path, reason, corrected_value, last_fallback_tile_id, fallback_count, accepted_count, residual_fallback_count, stale_fallback_count, tile_health_action);
            if (
                execution_path !== expected_path ||
                reason !== expected_reason ||
                last_fallback_tile_id !== expected_last_fallback_tile_id ||
                fallback_count !== expected_fallback_count ||
                accepted_count !== expected_accepted_count ||
                residual_fallback_count !== expected_residual_fallback_count ||
                stale_fallback_count !== expected_stale_fallback_count ||
                tile_health_action !== expected_tile_health_action
            ) begin
                $display("FAIL %0s expected_path=%0d expected_reason=%0d expected_last_fallback_tile=%0d expected_fallback_count=%0d expected_accepted_count=%0d expected_residual_fallback_count=%0d expected_stale_fallback_count=%0d expected_tile_health_action=%0d", name, expected_path, expected_reason, expected_last_fallback_tile_id, expected_fallback_count, expected_accepted_count, expected_residual_fallback_count, expected_stale_fallback_count, expected_tile_health_action);
                $finish;
            end
        end
    endtask

    task run_control_case;
        input [160*8:1] name;
        input in_calibration_done;
        input in_probe_request;
        input in_probe_passed;
        input in_probe_failed;
        input [1:0] expected_tile_health_action;
        begin
            @(negedge clk);
            sample_valid = 1'b0;
            calibration_done = in_calibration_done;
            probe_request = in_probe_request;
            probe_passed = in_probe_passed;
            probe_failed = in_probe_failed;
            @(negedge clk);
            calibration_done = 1'b0;
            probe_request = 1'b0;
            probe_passed = 1'b0;
            probe_failed = 1'b0;
            #1;
            $display("%0s,path=%0d,reason=%0d,value=%0d,last_fallback_tile=%0d,fallback_count=%0d,accepted_count=%0d,residual_fallback_count=%0d,stale_fallback_count=%0d,tile_health_action=%0d", name, execution_path, reason, corrected_value, last_fallback_tile_id, fallback_count, accepted_count, residual_fallback_count, stale_fallback_count, tile_health_action);
            if (tile_health_action !== expected_tile_health_action) begin
                $display("FAIL %0s expected_tile_health_action=%0d", name, expected_tile_health_action);
                $finish;
            end
        end
    endtask

    initial begin
        $dumpfile("aimc_micro_tile_controller.vcd");
        $dumpvars(0, aimc_micro_tile_controller_tb);

        repeat (2) @(negedge clk);
        rst_n = 1'b1;

`include "generated_micro_tile_cases.vh"

        run_control_case("maintenance_disabled_enters_probe", 1'b0, 1'b1, 1'b0, 1'b0, 2'd3);
        run_control_case("maintenance_probe_failed_disables", 1'b0, 1'b0, 1'b0, 1'b1, 2'd2);
        run_control_case("maintenance_disabled_enters_probe_again", 1'b0, 1'b1, 1'b0, 1'b0, 2'd3);
        run_control_case("maintenance_probe_passed_serves", 1'b0, 1'b0, 1'b1, 1'b0, 2'd0);
        run_case("post_probe_stale_recalibrates", 4'd1, 1'b1, 8'd19, 1'b1, 10'd3, 16'd2048, 2'd0, 4'd11, 8'd19, 16'd5, 16'd1, 16'd2, 16'd2, 2'd1);
        run_control_case("maintenance_calibration_done_serves", 1'b1, 1'b0, 1'b0, 1'b0, 2'd0);

        $display("PASS aimc_micro_tile_controller_tb");
        $finish;
    end
endmodule
