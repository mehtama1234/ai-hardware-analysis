module toy_cts_probe (
    input wire clk,
    input wire rst_n,
    input wire [7:0] data_in,
    input wire enable,
    output reg [7:0] state,
    output wire any_high,
    output wire parity
);
    wire [7:0] feedback;

    assign feedback = {state[6:0], state[7] ^ data_in[0]} ^ data_in;
    assign any_high = |state;
    assign parity = ^state;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= 8'h00;
        end else if (enable) begin
            state <= feedback;
        end
    end
endmodule
