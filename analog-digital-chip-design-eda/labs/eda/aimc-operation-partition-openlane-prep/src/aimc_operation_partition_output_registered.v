module aimc_operation_partition_output_registered (
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
    wire [1:0] placement_d;
    wire [3:0] reason_d;

    aimc_operation_partition partition (
        .op_class(op_class),
        .resident_weights(resident_weights),
        .estimated_state_error(estimated_state_error),
        .state_error_budget(state_error_budget),
        .attention_flip_rate(attention_flip_rate),
        .attention_flip_budget(attention_flip_budget),
        .token_flip_rate(token_flip_rate),
        .token_flip_budget(token_flip_budget),
        .calibration_age(calibration_age),
        .weak_tiles(weak_tiles),
        .placement(placement_d),
        .reason(reason_d)
    );

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            placement <= 2'd0;
            reason <= 4'd0;
        end else begin
            placement <= placement_d;
            reason <= reason_d;
        end
    end
endmodule
