module formal_constant(input clk, output reg q);
  always @(posedge clk)
    q <= 1'b0;
endmodule
