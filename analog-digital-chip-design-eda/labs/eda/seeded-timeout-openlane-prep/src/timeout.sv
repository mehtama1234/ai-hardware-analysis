module timeout(input logic clk, input logic rst, input logic start, output logic timed_out);
  logic [2:0] count;
  always_ff @(posedge clk) begin
    if (rst) count <= 3'd0;
    else if (start) count <= 3'd1;
    else if (count != 3'd0) count <= count + 3'd1;
  end
  assign timed_out = count >= 3'd3;
endmodule
