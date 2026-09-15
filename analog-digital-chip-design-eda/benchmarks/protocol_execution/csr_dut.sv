module csr_dut(
    input logic clk,
    input logic rst,
    input logic valid,
    input logic write,
    input logic [7:0] address,
    input logic [31:0] write_data,
    output logic ready,
    output logic [31:0] read_data
);
  logic [31:0] value;
  assign ready = !rst;
  assign read_data = value;
  always_ff @(posedge clk) begin
    if (rst) value <= 32'h0;
    else if (valid && write && address == 8'h4) value <= write_data;
  end
endmodule
