module fifo #(parameter DEPTH = 2) (
  input logic clk, input logic rst, input logic wr_en, input logic rd_en,
  output logic [2:0] count
);
  always_ff @(posedge clk) begin
    if (rst) count <= 3'd0;
    else begin
      // SEEDED_BUG: write is not gated by full
      case ({wr_en, rd_en})
        2'b10: count <= count + 3'd1;
        2'b01: count <= (count != 0) ? count - 3'd1 : count;
        default: count <= count;
      endcase
    end
  end
endmodule
