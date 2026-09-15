module counter_svm(input logic clk, input logic rst, input logic enable, input logic [3:0] actual, output logic mismatch);
  logic [3:0] reference;
  always_ff @(posedge clk) begin
    if (rst) begin
      reference <= 4'd0;
      mismatch <= 1'b0;
    end else begin
      if (enable) reference <= reference + 4'd1;
      if (actual !== reference) mismatch <= 1'b1;
    end
  end
endmodule
