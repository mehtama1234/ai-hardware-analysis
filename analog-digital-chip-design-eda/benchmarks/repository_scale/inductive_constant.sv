module constant_invariant(input logic clk, input logic rst, input logic enable);
  logic [1:0] state = 2'd0;
  always_ff @(posedge clk) begin
    if (rst) state <= 2'd0;
    else if (enable) state <= 2'd0;
    else state <= 2'd0;
    assert(state == 2'd0);
  end
endmodule
