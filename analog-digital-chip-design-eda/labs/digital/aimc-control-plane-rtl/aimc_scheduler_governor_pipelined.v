module aimc_scheduler_governor_pipelined (
    input wire clk,
    input wire rst_n,
    input wire sample_valid,
    input wire analog_candidate,
    input wire [7:0] requested_tile_id,
    input wire [1:0] tile0_health_action,
    input wire [1:0] tile1_health_action,
    input wire [1:0] tile2_health_action,
    input wire [1:0] tile3_health_action,
    input wire [3:0] tile_busy,
    input wire [1:0] maintenance_budget,
    input wire [7:0] residual_q8,
    input wire [3:0] drift_age,
    input wire [7:0] sensitivity_q8,
    input wire [7:0] cumulative_error_q8,
    output reg [1:0] final_decision,
    output reg [1:0] selected_tile,
    output reg [3:0] final_reason,
    output reg [7:0] next_cumulative_error_q8
);
    reg stage_valid;
    reg stage_analog_candidate;
    reg [7:0] stage_requested_tile_id;
    reg [1:0] stage_tile0_health_action;
    reg [1:0] stage_tile1_health_action;
    reg [1:0] stage_tile2_health_action;
    reg [1:0] stage_tile3_health_action;
    reg [3:0] stage_tile_busy;
    reg [1:0] stage_maintenance_budget;
    reg [7:0] stage_residual_q8;
    reg [3:0] stage_drift_age;
    reg [7:0] stage_sensitivity_q8;
    reg [7:0] stage_cumulative_error_q8;

    localparam DECISION_DIGITAL = 2'd0;
    localparam DECISION_ANALOG = 2'd1;
    localparam DECISION_RECALIBRATE = 2'd2;
    localparam DECISION_PROBE = 2'd3;

    localparam GOVERNOR_ACTION_RECALIBRATE = 2'd1;

    localparam SCHEDULER_REASON_NO_SAMPLE = 4'd0;
    localparam SCHEDULER_REASON_ANALOG_NOT_ALLOWED = 4'd1;
    localparam SCHEDULER_REASON_SERVE_REQUESTED_TILE = 4'd2;
    localparam SCHEDULER_REASON_SERVE_SPARE_TILE = 4'd3;
    localparam GOVERNOR_REASON_NO_SAMPLE = 4'd0;
    localparam GOVERNOR_REASON_NOT_ANALOG_CANDIDATE = 4'd1;
    localparam GOVERNOR_REASON_RESIDUAL_TOO_HIGH = 4'd2;
    localparam GOVERNOR_REASON_CALIBRATION_TOO_OLD = 4'd3;
    localparam GOVERNOR_REASON_SENSITIVE_PATH_NEEDS_DIGITAL = 4'd4;
    localparam GOVERNOR_REASON_STATE_ERROR_BUDGET_SPENT = 4'd5;

    localparam FINAL_REASON_NO_SAMPLE = 4'd0;
    localparam FINAL_REASON_NOT_ANALOG_CANDIDATE = 4'd1;
    localparam FINAL_REASON_SCHEDULER_DIGITAL = 4'd2;
    localparam FINAL_REASON_SCHEDULER_RECALIBRATE = 4'd3;
    localparam FINAL_REASON_SCHEDULER_PROBE = 4'd4;
    localparam FINAL_REASON_GOVERNOR_RESIDUAL_TOO_HIGH = 4'd5;
    localparam FINAL_REASON_GOVERNOR_CALIBRATION_TOO_OLD = 4'd6;
    localparam FINAL_REASON_GOVERNOR_SENSITIVE_PATH = 4'd7;
    localparam FINAL_REASON_GOVERNOR_STATE_BUDGET = 4'd8;
    localparam FINAL_REASON_ANALOG_REQUESTED_TILE = 4'd9;
    localparam FINAL_REASON_ANALOG_SPARE_TILE = 4'd10;
    localparam FINAL_REASON_ANALOG_RECALIBRATE_SOON = 4'd11;

    wire [1:0] scheduler_decision_d;
    wire [1:0] scheduler_selected_tile_d;
    wire [3:0] scheduler_reason_d;
    wire [1:0] governor_decision_d;
    wire [1:0] governor_action_d;
    wire [3:0] governor_reason_d;
    wire [7:0] governor_next_cumulative_error_q8_d;

    reg [1:0] scheduler_decision_q;
    reg [1:0] scheduler_selected_tile_q;
    reg [3:0] scheduler_reason_q;
    reg [1:0] governor_decision_q;
    reg [1:0] governor_action_q;
    reg [3:0] governor_reason_q;
    reg [7:0] governor_next_cumulative_error_q8_q;

    reg [1:0] final_decision_d;
    reg [3:0] final_reason_d;

    aimc_tile_service_scheduler scheduler (
        .sample_valid(stage_valid),
        .analog_candidate(stage_analog_candidate),
        .requested_tile_id(stage_requested_tile_id),
        .tile0_health_action(stage_tile0_health_action),
        .tile1_health_action(stage_tile1_health_action),
        .tile2_health_action(stage_tile2_health_action),
        .tile3_health_action(stage_tile3_health_action),
        .tile_busy(stage_tile_busy),
        .maintenance_budget(stage_maintenance_budget),
        .service_decision(scheduler_decision_d),
        .selected_tile(scheduler_selected_tile_d),
        .reason(scheduler_reason_d)
    );

    aimc_error_budget_governor governor (
        .sample_valid(stage_valid),
        .analog_candidate(stage_analog_candidate),
        .residual_q8(stage_residual_q8),
        .drift_age(stage_drift_age),
        .sensitivity_q8(stage_sensitivity_q8),
        .cumulative_error_q8(stage_cumulative_error_q8),
        .service_decision(governor_decision_d),
        .tile_action(governor_action_d),
        .reason(governor_reason_d),
        .next_cumulative_error_q8(governor_next_cumulative_error_q8_d)
    );

    always @(*) begin
        final_decision_d = DECISION_DIGITAL;
        final_reason_d = FINAL_REASON_SCHEDULER_DIGITAL;

        if ((scheduler_reason_q == SCHEDULER_REASON_NO_SAMPLE) || (governor_reason_q == GOVERNOR_REASON_NO_SAMPLE)) begin
            final_decision_d = DECISION_DIGITAL;
            final_reason_d = FINAL_REASON_NO_SAMPLE;
        end else if ((scheduler_reason_q == SCHEDULER_REASON_ANALOG_NOT_ALLOWED) || (governor_reason_q == GOVERNOR_REASON_NOT_ANALOG_CANDIDATE)) begin
            final_decision_d = DECISION_DIGITAL;
            final_reason_d = FINAL_REASON_NOT_ANALOG_CANDIDATE;
        end else if (scheduler_decision_q == DECISION_RECALIBRATE) begin
            final_decision_d = DECISION_RECALIBRATE;
            final_reason_d = FINAL_REASON_SCHEDULER_RECALIBRATE;
        end else if (scheduler_decision_q == DECISION_PROBE) begin
            final_decision_d = DECISION_PROBE;
            final_reason_d = FINAL_REASON_SCHEDULER_PROBE;
        end else if (scheduler_decision_q == DECISION_DIGITAL) begin
            final_decision_d = DECISION_DIGITAL;
            final_reason_d = FINAL_REASON_SCHEDULER_DIGITAL;
        end else if (governor_decision_q == DECISION_DIGITAL) begin
            if (governor_reason_q == GOVERNOR_REASON_RESIDUAL_TOO_HIGH) begin
                final_reason_d = FINAL_REASON_GOVERNOR_RESIDUAL_TOO_HIGH;
            end else if (governor_reason_q == GOVERNOR_REASON_CALIBRATION_TOO_OLD) begin
                final_decision_d = DECISION_RECALIBRATE;
                final_reason_d = FINAL_REASON_GOVERNOR_CALIBRATION_TOO_OLD;
            end else if (governor_reason_q == GOVERNOR_REASON_SENSITIVE_PATH_NEEDS_DIGITAL) begin
                final_reason_d = FINAL_REASON_GOVERNOR_SENSITIVE_PATH;
            end else if (governor_reason_q == GOVERNOR_REASON_STATE_ERROR_BUDGET_SPENT) begin
                final_decision_d = DECISION_RECALIBRATE;
                final_reason_d = FINAL_REASON_GOVERNOR_STATE_BUDGET;
            end else begin
                final_reason_d = FINAL_REASON_SCHEDULER_DIGITAL;
            end
        end else if (governor_action_q == GOVERNOR_ACTION_RECALIBRATE) begin
            final_decision_d = DECISION_ANALOG;
            final_reason_d = FINAL_REASON_ANALOG_RECALIBRATE_SOON;
        end else if (scheduler_reason_q == SCHEDULER_REASON_SERVE_SPARE_TILE) begin
            final_decision_d = DECISION_ANALOG;
            final_reason_d = FINAL_REASON_ANALOG_SPARE_TILE;
        end else if (scheduler_reason_q == SCHEDULER_REASON_SERVE_REQUESTED_TILE) begin
            final_decision_d = DECISION_ANALOG;
            final_reason_d = FINAL_REASON_ANALOG_REQUESTED_TILE;
        end else begin
            final_decision_d = DECISION_ANALOG;
            final_reason_d = FINAL_REASON_ANALOG_REQUESTED_TILE;
        end
    end

    always @(posedge clk) begin
        stage_valid <= sample_valid;
        stage_analog_candidate <= analog_candidate;
        stage_requested_tile_id <= requested_tile_id;
        stage_tile0_health_action <= tile0_health_action;
        stage_tile1_health_action <= tile1_health_action;
        stage_tile2_health_action <= tile2_health_action;
        stage_tile3_health_action <= tile3_health_action;
        stage_tile_busy <= tile_busy;
        stage_maintenance_budget <= maintenance_budget;
        stage_residual_q8 <= residual_q8;
        stage_drift_age <= drift_age;
        stage_sensitivity_q8 <= sensitivity_q8;
        stage_cumulative_error_q8 <= cumulative_error_q8;
        scheduler_decision_q <= scheduler_decision_d;
        scheduler_selected_tile_q <= scheduler_selected_tile_d;
        scheduler_reason_q <= scheduler_reason_d;
        governor_decision_q <= governor_decision_d;
        governor_action_q <= governor_action_d;
        governor_reason_q <= governor_reason_d;
        governor_next_cumulative_error_q8_q <= governor_next_cumulative_error_q8_d;
        selected_tile <= scheduler_selected_tile_q;
        next_cumulative_error_q8 <= governor_next_cumulative_error_q8_q;
    end

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            final_decision <= 2'd0;
            final_reason <= 4'd0;
        end else begin
            final_decision <= final_decision_d;
            final_reason <= final_reason_d;
        end
    end
endmodule
