module signed_add(input logic rst, input logic signed [3:0] a, input logic signed [3:0] b, output logic signed [5:0] sum);
  // SEEDED_BUG: operands are zero-extended instead of sign-extended
  assign sum = rst ? 6'sd0 : $signed(a) + $signed(b);
endmodule
