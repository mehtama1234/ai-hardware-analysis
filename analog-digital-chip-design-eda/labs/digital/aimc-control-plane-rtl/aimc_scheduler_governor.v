module aimc_scheduler_governor (
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
    input wire [7:0] residual_q8,
    input wire [3:0] drift_age,
    input wire [7:0] sensitivity_q8,
    input wire [7:0] cumulative_error_q8,
    output reg [1:0] final_decision,
    output reg [1:0] selected_tile,
    output reg [3:0] final_reason,
    output wire [7:0] next_cumulative_error_q8
);
    localparam DECISION_DIGITAL = 2'd0;
    localparam DECISION_ANALOG = 2'd1;
    localparam DECISION_RECALIBRATE = 2'd2;
    localparam DECISION_PROBE = 2'd3;

    localparam GOVERNOR_ACTION_RECALIBRATE = 2'd1;

    localparam SCHEDULER_REASON_NO_SAMPLE = 4'd0;
    localparam SCHEDULER_REASON_ANALOG_NOT_ALLOWED = 4'd1;
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

    wire [1:0] scheduler_decision;
    wire [1:0] scheduler_selected_tile;
    wire [3:0] scheduler_reason;
    wire [1:0] governor_decision;
    wire [1:0] governor_action;
    wire [3:0] governor_reason;

    aimc_tile_service_scheduler scheduler (
        .sample_valid(sample_valid),
        .analog_candidate(analog_candidate),
        .requested_tile_id(requested_tile_id),
        .tile0_health_action(tile0_health_action),
        .tile1_health_action(tile1_health_action),
        .tile2_health_action(tile2_health_action),
        .tile3_health_action(tile3_health_action),
        .tile_busy(tile_busy),
        .maintenance_budget(maintenance_budget),
        .service_decision(scheduler_decision),
        .selected_tile(scheduler_selected_tile),
        .reason(scheduler_reason)
    );

    aimc_error_budget_governor governor (
        .sample_valid(sample_valid),
        .analog_candidate(analog_candidate),
        .residual_q8(residual_q8),
        .drift_age(drift_age),
        .sensitivity_q8(sensitivity_q8),
        .cumulative_error_q8(cumulative_error_q8),
        .service_decision(governor_decision),
        .tile_action(governor_action),
        .reason(governor_reason),
        .next_cumulative_error_q8(next_cumulative_error_q8)
    );

    always @(*) begin
        final_decision = DECISION_DIGITAL;
        selected_tile = scheduler_selected_tile;
        final_reason = FINAL_REASON_SCHEDULER_DIGITAL;

        if ((scheduler_reason == SCHEDULER_REASON_NO_SAMPLE) || (governor_reason == GOVERNOR_REASON_NO_SAMPLE)) begin
            final_decision = DECISION_DIGITAL;
            final_reason = FINAL_REASON_NO_SAMPLE;
        end else if ((scheduler_reason == SCHEDULER_REASON_ANALOG_NOT_ALLOWED) || (governor_reason == GOVERNOR_REASON_NOT_ANALOG_CANDIDATE)) begin
            final_decision = DECISION_DIGITAL;
            final_reason = FINAL_REASON_NOT_ANALOG_CANDIDATE;
        end else if (scheduler_decision == DECISION_RECALIBRATE) begin
            final_decision = DECISION_RECALIBRATE;
            final_reason = FINAL_REASON_SCHEDULER_RECALIBRATE;
        end else if (scheduler_decision == DECISION_PROBE) begin
            final_decision = DECISION_PROBE;
            final_reason = FINAL_REASON_SCHEDULER_PROBE;
        end else if (scheduler_decision == DECISION_DIGITAL) begin
            final_decision = DECISION_DIGITAL;
            final_reason = FINAL_REASON_SCHEDULER_DIGITAL;
        end else if (governor_decision == DECISION_DIGITAL) begin
            if (governor_reason == GOVERNOR_REASON_RESIDUAL_TOO_HIGH) begin
                final_reason = FINAL_REASON_GOVERNOR_RESIDUAL_TOO_HIGH;
            end else if (governor_reason == GOVERNOR_REASON_CALIBRATION_TOO_OLD) begin
                final_decision = DECISION_RECALIBRATE;
                final_reason = FINAL_REASON_GOVERNOR_CALIBRATION_TOO_OLD;
            end else if (governor_reason == GOVERNOR_REASON_SENSITIVE_PATH_NEEDS_DIGITAL) begin
                final_reason = FINAL_REASON_GOVERNOR_SENSITIVE_PATH;
            end else if (governor_reason == GOVERNOR_REASON_STATE_ERROR_BUDGET_SPENT) begin
                final_decision = DECISION_RECALIBRATE;
                final_reason = FINAL_REASON_GOVERNOR_STATE_BUDGET;
            end else begin
                final_reason = FINAL_REASON_SCHEDULER_DIGITAL;
            end
        end else if (governor_action == GOVERNOR_ACTION_RECALIBRATE) begin
            final_decision = DECISION_ANALOG;
            final_reason = FINAL_REASON_ANALOG_RECALIBRATE_SOON;
        end else if (scheduler_reason == SCHEDULER_REASON_SERVE_SPARE_TILE) begin
            final_decision = DECISION_ANALOG;
            final_reason = FINAL_REASON_ANALOG_SPARE_TILE;
        end else begin
            final_decision = DECISION_ANALOG;
            final_reason = FINAL_REASON_ANALOG_REQUESTED_TILE;
        end
    end
endmodule
