module aimc_error_budget_governor_physical (
    input wire clk,
    input wire rst_n,
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
    reg sample_valid_q;
    reg analog_candidate_q;
    reg [7:0] residual_q8_q;
    reg [3:0] drift_age_q;
    reg [7:0] sensitivity_q8_q;
    reg [7:0] cumulative_error_q8_q;
    wire [1:0] service_decision_d;
    wire [1:0] tile_action_d;
    wire [3:0] reason_d;
    wire [7:0] next_cumulative_error_q8_d;

    aimc_error_budget_governor governor (
        .sample_valid(sample_valid_q),
        .analog_candidate(analog_candidate_q),
        .residual_q8(residual_q8_q),
        .drift_age(drift_age_q),
        .sensitivity_q8(sensitivity_q8_q),
        .cumulative_error_q8(cumulative_error_q8_q),
        .service_decision(service_decision_d),
        .tile_action(tile_action_d),
        .reason(reason_d),
        .next_cumulative_error_q8(next_cumulative_error_q8_d)
    );

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            sample_valid_q <= 1'b0;
            analog_candidate_q <= 1'b0;
            residual_q8_q <= 8'd0;
            drift_age_q <= 4'd0;
            sensitivity_q8_q <= 8'd0;
            cumulative_error_q8_q <= 8'd0;
            service_decision <= 2'd0;
            tile_action <= 2'd0;
            reason <= 4'd0;
            next_cumulative_error_q8 <= 8'd0;
        end else begin
            sample_valid_q <= sample_valid;
            analog_candidate_q <= analog_candidate;
            residual_q8_q <= residual_q8;
            drift_age_q <= drift_age;
            sensitivity_q8_q <= sensitivity_q8;
            cumulative_error_q8_q <= cumulative_error_q8;
            service_decision <= service_decision_d;
            tile_action <= tile_action_d;
            reason <= reason_d;
            next_cumulative_error_q8 <= next_cumulative_error_q8_d;
        end
    end
endmodule
