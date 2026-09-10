module formal_bad(input clk, output reg q);
  always @(posedge clk)
    q <= 1'b1;
endmodule
