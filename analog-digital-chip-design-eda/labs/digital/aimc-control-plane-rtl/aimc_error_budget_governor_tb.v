`timescale 1ns/1ps

module aimc_error_budget_governor_tb;
    reg sample_valid = 0;
    reg analog_candidate = 0;
    reg [7:0] residual_q8 = 8'd0;
    reg [3:0] drift_age = 4'd0;
    reg [7:0] sensitivity_q8 = 8'd0;
    reg [7:0] cumulative_error_q8 = 8'd0;
    wire [1:0] service_decision;
    wire [1:0] tile_action;
    wire [3:0] reason;
    wire [7:0] next_cumulative_error_q8;

    aimc_error_budget_governor dut (
        .sample_valid(sample_valid),
        .analog_candidate(analog_candidate),
        .residual_q8(residual_q8),
        .drift_age(drift_age),
        .sensitivity_q8(sensitivity_q8),
        .cumulative_error_q8(cumulative_error_q8),
        .service_decision(service_decision),
        .tile_action(tile_action),
        .reason(reason),
        .next_cumulative_error_q8(next_cumulative_error_q8)
    );

    task run_case;
        input [160*8:1] name;
        input in_sample_valid;
        input in_analog_candidate;
        input [7:0] in_residual_q8;
        input [3:0] in_drift_age;
        input [7:0] in_sensitivity_q8;
        input [7:0] in_cumulative_error_q8;
        input [1:0] expected_service_decision;
        input [1:0] expected_tile_action;
        input [3:0] expected_reason;
        input [7:0] expected_next_cumulative_error_q8;
        begin
            sample_valid = in_sample_valid;
            analog_candidate = in_analog_candidate;
            residual_q8 = in_residual_q8;
            drift_age = in_drift_age;
            sensitivity_q8 = in_sensitivity_q8;
            cumulative_error_q8 = in_cumulative_error_q8;
            #1;
            $display("%0s,residual=%0d,drift=%0d,sensitivity=%0d,cumulative=%0d,decision=%0d,action=%0d,reason=%0d,next=%0d", name, residual_q8, drift_age, sensitivity_q8, cumulative_error_q8, service_decision, tile_action, reason, next_cumulative_error_q8);
            if (
                service_decision !== expected_service_decision ||
                tile_action !== expected_tile_action ||
                reason !== expected_reason ||
                next_cumulative_error_q8 !== expected_next_cumulative_error_q8
            ) begin
                $display("FAIL %0s expected_decision=%0d expected_action=%0d expected_reason=%0d expected_next=%0d", name, expected_service_decision, expected_tile_action, expected_reason, expected_next_cumulative_error_q8);
                $finish;
            end
        end
    endtask

    initial begin
`include "generated_error_budget_governor_cases.vh"
        $display("PASS aimc_error_budget_governor_tb");
        $finish;
    end
endmodule
