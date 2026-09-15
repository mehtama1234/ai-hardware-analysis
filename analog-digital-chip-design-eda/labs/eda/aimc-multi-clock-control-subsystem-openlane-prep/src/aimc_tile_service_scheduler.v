module aimc_tile_service_scheduler (
    input wire sample_valid,
    input wire analog_candidate,
/* verilator lint_off UNUSEDSIGNAL */
    input wire [7:0] requested_tile_id,
/* verilator lint_on UNUSEDSIGNAL */
    input wire [1:0] tile0_health_action,
    input wire [1:0] tile1_health_action,
    input wire [1:0] tile2_health_action,
    input wire [1:0] tile3_health_action,
    input wire [3:0] tile_busy,
    input wire [1:0] maintenance_budget,
    output reg [1:0] service_decision,
    output reg [1:0] selected_tile,
    output reg [3:0] reason
);
    localparam TILE_SERVE = 2'd0;
    localparam TILE_RECALIBRATE = 2'd1;
    localparam TILE_PROBE = 2'd3;

    localparam DECISION_DIGITAL = 2'd0;
    localparam DECISION_ANALOG = 2'd1;
    localparam DECISION_RECALIBRATE = 2'd2;
    localparam DECISION_PROBE = 2'd3;

    localparam REASON_NO_SAMPLE = 4'd0;
    localparam REASON_ANALOG_NOT_ALLOWED = 4'd1;
    localparam REASON_SERVE_REQUESTED_TILE = 4'd2;
    localparam REASON_SERVE_SPARE_TILE = 4'd3;
    localparam REASON_RECALIBRATE_TILE = 4'd4;
    localparam REASON_PROBE_TILE = 4'd5;
    localparam REASON_NO_MAINTENANCE_BUDGET = 4'd6;
    localparam REASON_ALL_TILES_DISABLED_OR_BUSY = 4'd7;

    wire [1:0] requested_index = requested_tile_id[1:0];
    wire tile0_can_serve = (tile_busy[0] == 1'b0) && (tile0_health_action == TILE_SERVE);
    wire tile1_can_serve = (tile_busy[1] == 1'b0) && (tile1_health_action == TILE_SERVE);
    wire tile2_can_serve = (tile_busy[2] == 1'b0) && (tile2_health_action == TILE_SERVE);
    wire tile3_can_serve = (tile_busy[3] == 1'b0) && (tile3_health_action == TILE_SERVE);
    wire tile0_needs_recalibrate = (tile_busy[0] == 1'b0) && (tile0_health_action == TILE_RECALIBRATE);
    wire tile1_needs_recalibrate = (tile_busy[1] == 1'b0) && (tile1_health_action == TILE_RECALIBRATE);
    wire tile2_needs_recalibrate = (tile_busy[2] == 1'b0) && (tile2_health_action == TILE_RECALIBRATE);
    wire tile3_needs_recalibrate = (tile_busy[3] == 1'b0) && (tile3_health_action == TILE_RECALIBRATE);
    wire tile0_needs_probe = (tile_busy[0] == 1'b0) && (tile0_health_action == TILE_PROBE);
    wire tile1_needs_probe = (tile_busy[1] == 1'b0) && (tile1_health_action == TILE_PROBE);
    wire tile2_needs_probe = (tile_busy[2] == 1'b0) && (tile2_health_action == TILE_PROBE);
    wire tile3_needs_probe = (tile_busy[3] == 1'b0) && (tile3_health_action == TILE_PROBE);
    wire any_serving_tile = tile0_can_serve || tile1_can_serve || tile2_can_serve || tile3_can_serve;
    wire any_recalibrate_tile = tile0_needs_recalibrate || tile1_needs_recalibrate || tile2_needs_recalibrate || tile3_needs_recalibrate;
    wire any_probe_tile = tile0_needs_probe || tile1_needs_probe || tile2_needs_probe || tile3_needs_probe;
    wire [1:0] first_serving_tile =
        tile0_can_serve ? 2'd0 :
        tile1_can_serve ? 2'd1 :
        tile2_can_serve ? 2'd2 : 2'd3;
    wire [1:0] first_recalibrate_tile =
        tile0_needs_recalibrate ? 2'd0 :
        tile1_needs_recalibrate ? 2'd1 :
        tile2_needs_recalibrate ? 2'd2 : 2'd3;
    wire [1:0] first_probe_tile =
        tile0_needs_probe ? 2'd0 :
        tile1_needs_probe ? 2'd1 :
        tile2_needs_probe ? 2'd2 : 2'd3;

    function [1:0] tile_action;
        input [1:0] index;
        begin
            case (index)
                2'd0: tile_action = tile0_health_action;
                2'd1: tile_action = tile1_health_action;
                2'd2: tile_action = tile2_health_action;
                default: tile_action = tile3_health_action;
            endcase
        end
    endfunction

    function tile_is_busy;
        input [1:0] index;
        begin
            case (index)
                2'd0: tile_is_busy = tile_busy[0];
                2'd1: tile_is_busy = tile_busy[1];
                2'd2: tile_is_busy = tile_busy[2];
                default: tile_is_busy = tile_busy[3];
            endcase
        end
    endfunction

    always @(*) begin
        service_decision = DECISION_DIGITAL;
        selected_tile = requested_index;
        reason = REASON_NO_SAMPLE;

        if (!sample_valid) begin
            service_decision = DECISION_DIGITAL;
            reason = REASON_NO_SAMPLE;
        end else if (!analog_candidate) begin
            service_decision = DECISION_DIGITAL;
            reason = REASON_ANALOG_NOT_ALLOWED;
        end else if ((tile_is_busy(requested_index) == 1'b0) && (tile_action(requested_index) == TILE_SERVE)) begin
            service_decision = DECISION_ANALOG;
            selected_tile = requested_index;
            reason = REASON_SERVE_REQUESTED_TILE;
        end else if (any_serving_tile) begin
            service_decision = DECISION_ANALOG;
            selected_tile = first_serving_tile;
            reason = REASON_SERVE_SPARE_TILE;
        end else if (maintenance_budget == 2'd0) begin
            service_decision = DECISION_DIGITAL;
            reason = REASON_NO_MAINTENANCE_BUDGET;
        end else if (any_recalibrate_tile) begin
            service_decision = DECISION_RECALIBRATE;
            selected_tile = first_recalibrate_tile;
            reason = REASON_RECALIBRATE_TILE;
        end else if (any_probe_tile) begin
            service_decision = DECISION_PROBE;
            selected_tile = first_probe_tile;
            reason = REASON_PROBE_TILE;
        end else begin
            service_decision = DECISION_DIGITAL;
            reason = REASON_ALL_TILES_DISABLED_OR_BUSY;
        end
    end
endmodule
