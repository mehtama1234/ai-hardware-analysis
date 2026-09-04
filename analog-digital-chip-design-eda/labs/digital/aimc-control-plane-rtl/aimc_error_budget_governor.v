module aimc_error_budget_governor (
    input wire sample_valid,
    input wire analog_candidate,
    input wire [7:0] residual_q8,
    input wire [3:0] drift_age,
    input wire [7:0] sensitivity_q8,
    input wire [7:0] cumulative_error_q8,
    output reg [1:0] service_decision,
    output reg [1:0] tile_action,
    output reg [3:0] reason,
    output reg [7:0] next_cumulative_error_q8
);
    localparam DECISION_DIGITAL = 2'd0;
    localparam DECISION_ANALOG = 2'd1;

    localparam ACTION_SERVE = 2'd0;
    localparam ACTION_RECALIBRATE = 2'd1;
    localparam ACTION_DISABLE = 2'd2;

    localparam REASON_NO_SAMPLE = 4'd0;
    localparam REASON_NOT_ANALOG_CANDIDATE = 4'd1;
    localparam REASON_RESIDUAL_TOO_HIGH = 4'd2;
    localparam REASON_CALIBRATION_TOO_OLD = 4'd3;
    localparam REASON_SENSITIVE_PATH_NEEDS_DIGITAL = 4'd4;
    localparam REASON_STATE_ERROR_BUDGET_SPENT = 4'd5;
    localparam REASON_ANALOG_WITHIN_BUDGET = 4'd6;
    localparam REASON_ANALOG_BUT_RECALIBRATE_SOON = 4'd7;

    wire [8:0] drift_risk_q8 = {5'd0, drift_age} * 9'd3;
/* verilator lint_off UNUSEDSIGNAL */
    wire [8:0] risk_q8 = {1'b0, residual_q8} + drift_risk_q8 + {5'd0, sensitivity_q8[7:4]};
/* verilator lint_on UNUSEDSIGNAL */
    wire [6:0] risk_increment_q8 = risk_q8[8:2];
    wire [9:0] accumulated_error = {2'b00, cumulative_error_q8} + {3'b000, risk_increment_q8};
    wire [7:0] bounded_next_error = accumulated_error[9:8] != 2'b00 ? 8'd255 : accumulated_error[7:0];

    always @(*) begin
        service_decision = DECISION_DIGITAL;
        tile_action = ACTION_SERVE;
        reason = REASON_NO_SAMPLE;
        next_cumulative_error_q8 = cumulative_error_q8;

        if (!sample_valid) begin
            reason = REASON_NO_SAMPLE;
        end else if (!analog_candidate) begin
            reason = REASON_NOT_ANALOG_CANDIDATE;
        end else if (residual_q8 > 8'd46) begin
            tile_action = ACTION_DISABLE;
            reason = REASON_RESIDUAL_TOO_HIGH;
        end else if (drift_age > 4'd11) begin
            tile_action = ACTION_RECALIBRATE;
            reason = REASON_CALIBRATION_TOO_OLD;
        end else if ((sensitivity_q8 >= 8'd192) && (residual_q8 > 8'd24)) begin
            reason = REASON_SENSITIVE_PATH_NEEDS_DIGITAL;
        end else if (bounded_next_error > 8'd96) begin
            tile_action = ACTION_RECALIBRATE;
            reason = REASON_STATE_ERROR_BUDGET_SPENT;
        end else if ((drift_age >= 4'd9) || (bounded_next_error >= 8'd80)) begin
            service_decision = DECISION_ANALOG;
            tile_action = ACTION_RECALIBRATE;
            reason = REASON_ANALOG_BUT_RECALIBRATE_SOON;
            next_cumulative_error_q8 = bounded_next_error;
        end else begin
            service_decision = DECISION_ANALOG;
            tile_action = ACTION_SERVE;
            reason = REASON_ANALOG_WITHIN_BUDGET;
            next_cumulative_error_q8 = bounded_next_error;
        end
    end
endmodule
