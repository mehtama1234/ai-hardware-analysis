module tb;
  logic rst = 1; logic [7:0] data = 0; logic [3:0] low;
  width_adapter dut(.rst, .data, .low);
  task check(input logic [7:0] value, input logic [3:0] expected);
    begin data = value; #1 if (low !== expected) $display("FAIL data=%0h", value); end
  endtask
  initial begin
    #1 if (low !== 4'b0000) $display("FAIL reset");
    rst = 0; check(8'hA5, 4'h5); check(8'hF0, 4'h0); check(8'h0F, 4'hF); check(8'h3C, 4'hC);
    $display("PASS"); $finish;
  end
endmodule
