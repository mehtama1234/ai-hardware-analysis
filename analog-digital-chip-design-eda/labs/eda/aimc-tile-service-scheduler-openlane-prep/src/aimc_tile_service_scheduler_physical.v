module aimc_tile_service_scheduler_physical (
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
    output reg [1:0] service_decision,
    output reg [1:0] selected_tile,
    output reg [3:0] reason
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
    wire [1:0] service_decision_d;
    wire [1:0] selected_tile_d;
    wire [3:0] reason_d;

    aimc_tile_service_scheduler scheduler (
        .sample_valid(sample_valid_q),
        .analog_candidate(analog_candidate_q),
        .requested_tile_id(requested_tile_id_q),
        .tile0_health_action(tile0_health_action_q),
        .tile1_health_action(tile1_health_action_q),
        .tile2_health_action(tile2_health_action_q),
        .tile3_health_action(tile3_health_action_q),
        .tile_busy(tile_busy_q),
        .maintenance_budget(maintenance_budget_q),
        .service_decision(service_decision_d),
        .selected_tile(selected_tile_d),
        .reason(reason_d)
    );

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            sample_valid_q <= 1'b0;
            analog_candidate_q <= 1'b0;
            requested_tile_id_q <= 8'd0;
            tile0_health_action_q <= 2'd0;
            tile1_health_action_q <= 2'd0;
            tile2_health_action_q <= 2'd0;
            tile3_health_action_q <= 2'd0;
            tile_busy_q <= 4'd0;
            maintenance_budget_q <= 2'd0;
            service_decision <= 2'd0;
            selected_tile <= 2'd0;
            reason <= 4'd0;
        end else begin
            sample_valid_q <= sample_valid;
            analog_candidate_q <= analog_candidate;
            requested_tile_id_q <= requested_tile_id;
            tile0_health_action_q <= tile0_health_action;
            tile1_health_action_q <= tile1_health_action;
            tile2_health_action_q <= tile2_health_action;
            tile3_health_action_q <= tile3_health_action;
            tile_busy_q <= tile_busy;
            maintenance_budget_q <= maintenance_budget;
            service_decision <= service_decision_d;
            selected_tile <= selected_tile_d;
            reason <= reason_d;
        end
    end
endmodule
