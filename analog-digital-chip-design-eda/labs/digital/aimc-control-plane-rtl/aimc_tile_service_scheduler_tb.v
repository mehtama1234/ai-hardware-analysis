`timescale 1ns/1ps

module aimc_tile_service_scheduler_tb;
    reg sample_valid = 0;
    reg analog_candidate = 0;
    reg [7:0] requested_tile_id = 8'd0;
    reg [1:0] tile0_health_action = 2'd0;
    reg [1:0] tile1_health_action = 2'd0;
    reg [1:0] tile2_health_action = 2'd0;
    reg [1:0] tile3_health_action = 2'd0;
    reg [3:0] tile_busy = 4'b0000;
    reg [1:0] maintenance_budget = 2'd0;
    wire [1:0] service_decision;
    wire [1:0] selected_tile;
    wire [3:0] reason;

    aimc_tile_service_scheduler dut (
        .sample_valid(sample_valid),
        .analog_candidate(analog_candidate),
        .requested_tile_id(requested_tile_id),
        .tile0_health_action(tile0_health_action),
        .tile1_health_action(tile1_health_action),
        .tile2_health_action(tile2_health_action),
        .tile3_health_action(tile3_health_action),
        .tile_busy(tile_busy),
        .maintenance_budget(maintenance_budget),
        .service_decision(service_decision),
        .selected_tile(selected_tile),
        .reason(reason)
    );

    task run_case;
        input [160*8:1] name;
        input in_sample_valid;
        input in_analog_candidate;
        input [7:0] in_requested_tile_id;
        input [1:0] in_tile0_health_action;
        input [1:0] in_tile1_health_action;
        input [1:0] in_tile2_health_action;
        input [1:0] in_tile3_health_action;
        input [3:0] in_tile_busy;
        input [1:0] in_maintenance_budget;
        input [1:0] expected_service_decision;
        input [1:0] expected_selected_tile;
        input [3:0] expected_reason;
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
            #1;
            $display("%0s,tile_actions=%0d%0d%0d%0d,busy=%0d%0d%0d%0d,budget=%0d,decision=%0d,selected_tile=%0d,reason=%0d", name, tile0_health_action, tile1_health_action, tile2_health_action, tile3_health_action, tile_busy[0], tile_busy[1], tile_busy[2], tile_busy[3], maintenance_budget, service_decision, selected_tile, reason);
            if (
                service_decision !== expected_service_decision ||
                selected_tile !== expected_selected_tile ||
                reason !== expected_reason
            ) begin
                $display("FAIL %0s expected_decision=%0d expected_selected_tile=%0d expected_reason=%0d", name, expected_service_decision, expected_selected_tile, expected_reason);
                $finish;
            end
        end
    endtask

    initial begin
`include "generated_tile_scheduler_cases.vh"
        $display("PASS aimc_tile_service_scheduler_tb");
        $finish;
    end
endmodule
