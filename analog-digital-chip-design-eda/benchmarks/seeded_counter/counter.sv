module counter(input logic clk, input logic rst, input logic enable, output logic [3:0] counter_q);
  always_ff @(posedge clk) begin
    if (rst)
      counter_q <= 4'd0;
    else
      counter_q <= counter_q + 4'd1; // SEEDED_BUG: missing enable guard
  end
endmodule
