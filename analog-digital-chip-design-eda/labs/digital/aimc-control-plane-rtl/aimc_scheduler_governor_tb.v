`timescale 1ns/1ps

module aimc_scheduler_governor_tb;
    reg sample_valid = 0;
    reg analog_candidate = 0;
    reg [7:0] requested_tile_id = 8'd0;
    reg [1:0] tile0_health_action = 2'd0;
    reg [1:0] tile1_health_action = 2'd0;
    reg [1:0] tile2_health_action = 2'd0;
    reg [1:0] tile3_health_action = 2'd0;
    reg [3:0] tile_busy = 4'b0000;
    reg [1:0] maintenance_budget = 2'd0;
    reg [7:0] residual_q8 = 8'd0;
    reg [3:0] drift_age = 4'd0;
    reg [7:0] sensitivity_q8 = 8'd0;
    reg [7:0] cumulative_error_q8 = 8'd0;
    wire [1:0] final_decision;
    wire [1:0] selected_tile;
    wire [3:0] final_reason;
    wire [7:0] next_cumulative_error_q8;

    aimc_scheduler_governor dut (
        .sample_valid(sample_valid),
        .analog_candidate(analog_candidate),
        .requested_tile_id(requested_tile_id),
        .tile0_health_action(tile0_health_action),
        .tile1_health_action(tile1_health_action),
        .tile2_health_action(tile2_health_action),
        .tile3_health_action(tile3_health_action),
        .tile_busy(tile_busy),
        .maintenance_budget(maintenance_budget),
        .residual_q8(residual_q8),
        .drift_age(drift_age),
        .sensitivity_q8(sensitivity_q8),
        .cumulative_error_q8(cumulative_error_q8),
        .final_decision(final_decision),
        .selected_tile(selected_tile),
        .final_reason(final_reason),
        .next_cumulative_error_q8(next_cumulative_error_q8)
    );

    task run_case;
        input [180*8:1] name;
        input in_sample_valid;
        input in_analog_candidate;
        input [7:0] in_requested_tile_id;
        input [1:0] in_tile0_health_action;
        input [1:0] in_tile1_health_action;
        input [1:0] in_tile2_health_action;
        input [1:0] in_tile3_health_action;
        input [3:0] in_tile_busy;
        input [1:0] in_maintenance_budget;
        input [7:0] in_residual_q8;
        input [3:0] in_drift_age;
        input [7:0] in_sensitivity_q8;
        input [7:0] in_cumulative_error_q8;
        input [1:0] expected_final_decision;
        input [1:0] expected_selected_tile;
        input [3:0] expected_final_reason;
        input [7:0] expected_next_cumulative_error_q8;
        begin
            sample_valid = in_sample_valid;
            analog_candidate = in_analog_candidate;
            requested_tile_id = in_requested_tile_id;
            tile0_health_action = in_tile0_health_action;
            tile1_health_action = in_tile1_health_action;
            tile2_health_action = in_tile2_health_action;
            tile3_health_action = in_tile3_health_action;
            tile_busy = in_tile_busy;
            maintenance_budget = in_maintenance_budget;
            residual_q8 = in_residual_q8;
            drift_age = in_drift_age;
            sensitivity_q8 = in_sensitivity_q8;
            cumulative_error_q8 = in_cumulative_error_q8;
            #1;
            $display("%0s,tile_actions=%0d%0d%0d%0d,busy=%0d%0d%0d%0d,residual=%0d,drift=%0d,sensitivity=%0d,cumulative=%0d,decision=%0d,selected_tile=%0d,reason=%0d,next=%0d", name, tile0_health_action, tile1_health_action, tile2_health_action, tile3_health_action, tile_busy[0], tile_busy[1], tile_busy[2], tile_busy[3], residual_q8, drift_age, sensitivity_q8, cumulative_error_q8, final_decision, selected_tile, final_reason, next_cumulative_error_q8);
            if (
                final_decision !== expected_final_decision ||
                selected_tile !== expected_selected_tile ||
                final_reason !== expected_final_reason ||
                next_cumulative_error_q8 !== expected_next_cumulative_error_q8
            ) begin
                $display("FAIL %0s expected_decision=%0d expected_selected_tile=%0d expected_reason=%0d expected_next=%0d", name, expected_final_decision, expected_selected_tile, expected_final_reason, expected_next_cumulative_error_q8);
                $finish;
            end
        end
    endtask

    initial begin
`include "generated_integrated_scheduler_governor_cases.vh"
        $display("PASS aimc_scheduler_governor_tb");
        $finish;
    end
endmodule
