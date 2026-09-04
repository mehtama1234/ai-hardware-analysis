module aimc_operation_partition_physical (
    input wire clk,
    input wire rst_n,
    input wire [3:0] op_class,
    input wire resident_weights,
    input wire [7:0] estimated_state_error,
    input wire [7:0] state_error_budget,
    input wire [7:0] attention_flip_rate,
    input wire [7:0] attention_flip_budget,
    input wire [7:0] token_flip_rate,
    input wire [7:0] token_flip_budget,
    input wire [15:0] calibration_age,
    input wire [7:0] weak_tiles,
    output reg [1:0] placement,
    output reg [3:0] reason
);
    reg [3:0] op_class_q;
    reg resident_weights_q;
    reg [7:0] estimated_state_error_q;
    reg [7:0] state_error_budget_q;
    reg [7:0] attention_flip_rate_q;
    reg [7:0] attention_flip_budget_q;
    reg [7:0] token_flip_rate_q;
    reg [7:0] token_flip_budget_q;
    reg [15:0] calibration_age_q;
    reg [7:0] weak_tiles_q;
    wire [1:0] placement_d;
    wire [3:0] reason_d;

    aimc_operation_partition partition (
        .op_class(op_class_q),
        .resident_weights(resident_weights_q),
        .estimated_state_error(estimated_state_error_q),
        .state_error_budget(state_error_budget_q),
        .attention_flip_rate(attention_flip_rate_q),
        .attention_flip_budget(attention_flip_budget_q),
        .token_flip_rate(token_flip_rate_q),
        .token_flip_budget(token_flip_budget_q),
        .calibration_age(calibration_age_q),
        .weak_tiles(weak_tiles_q),
        .placement(placement_d),
        .reason(reason_d)
    );

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            op_class_q <= 4'd0;
            resident_weights_q <= 1'b0;
            estimated_state_error_q <= 8'd0;
            state_error_budget_q <= 8'd0;
            attention_flip_rate_q <= 8'd0;
            attention_flip_budget_q <= 8'd0;
            token_flip_rate_q <= 8'd0;
            token_flip_budget_q <= 8'd0;
            calibration_age_q <= 16'd0;
            weak_tiles_q <= 8'd0;
            placement <= 2'd0;
            reason <= 4'd0;
        end else begin
            op_class_q <= op_class;
            resident_weights_q <= resident_weights;
            estimated_state_error_q <= estimated_state_error;
            state_error_budget_q <= state_error_budget;
            attention_flip_rate_q <= attention_flip_rate;
            attention_flip_budget_q <= attention_flip_budget;
            token_flip_rate_q <= token_flip_rate;
            token_flip_budget_q <= token_flip_budget;
            calibration_age_q <= calibration_age;
            weak_tiles_q <= weak_tiles;
            placement <= placement_d;
            reason <= reason_d;
        end
    end
endmodule
