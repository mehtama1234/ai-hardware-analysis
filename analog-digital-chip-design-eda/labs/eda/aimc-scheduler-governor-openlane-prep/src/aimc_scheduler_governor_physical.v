module aimc_scheduler_governor_physical (
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
    reg sample_valid_q;
    reg analog_candidate_q;
    reg [7:0] requested_tile_id_q;
    reg [1:0] tile0_health_action_q;
    reg [1:0] tile1_health_action_q;
    reg [1:0] tile2_health_action_q;
    reg [1:0] tile3_health_action_q;
    reg [3:0] tile_busy_q;
    reg [1:0] maintenance_budget_q;
    reg [7:0] residual_q8_q;
    reg [3:0] drift_age_q;
    reg [7:0] sensitivity_q8_q;
    reg [7:0] cumulative_error_q8_q;
    wire [1:0] final_decision_d;
    wire [1:0] selected_tile_d;
    wire [3:0] final_reason_d;
    wire [7:0] next_cumulative_error_q8_d;

    aimc_scheduler_governor policy (
        .sample_valid(sample_valid_q),
        .analog_candidate(analog_candidate_q),
        .requested_tile_id(requested_tile_id_q),
        .tile0_health_action(tile0_health_action_q),
        .tile1_health_action(tile1_health_action_q),
        .tile2_health_action(tile2_health_action_q),
        .tile3_health_action(tile3_health_action_q),
        .tile_busy(tile_busy_q),
        .maintenance_budget(maintenance_budget_q),
        .residual_q8(residual_q8_q),
        .drift_age(drift_age_q),
        .sensitivity_q8(sensitivity_q8_q),
        .cumulative_error_q8(cumulative_error_q8_q),
        .final_decision(final_decision_d),
        .selected_tile(selected_tile_d),
        .final_reason(final_reason_d),
        .next_cumulative_error_q8(next_cumulative_error_q8_d)
    );

    always @(posedge clk) begin
        sample_valid_q <= sample_valid;
        analog_candidate_q <= analog_candidate;
        requested_tile_id_q <= requested_tile_id;
        tile0_health_action_q <= tile0_health_action;
        tile1_health_action_q <= tile1_health_action;
        tile2_health_action_q <= tile2_health_action;
        tile3_health_action_q <= tile3_health_action;
        tile_busy_q <= tile_busy;
        maintenance_budget_q <= maintenance_budget;
        residual_q8_q <= residual_q8;
        drift_age_q <= drift_age;
        sensitivity_q8_q <= sensitivity_q8;
        cumulative_error_q8_q <= cumulative_error_q8;
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

    always @(posedge clk) begin
        selected_tile <= selected_tile_d;
        next_cumulative_error_q8 <= next_cumulative_error_q8_d;
    end
endmodule
