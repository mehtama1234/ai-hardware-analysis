module tb;
  logic clk = 1'b0;
  logic rst = 1'b1;
  logic valid;
  logic write;
  logic [7:0] address;
  logic [31:0] write_data;
  logic ready;
  logic [31:0] read_data;
  logic error;

  always #5 clk = ~clk;
  csr_dut dut(.*);
  csr_sequence seq_inst(.*);

  initial begin
    #12 rst = 1'b0;
    #500 $display("TESTBENCH_TIMEOUT");
    $finish(1);
  end
endmodule
