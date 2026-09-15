module tb;
  logic rst = 1; logic [3:0] data = 0; logic even;
  parity dut(.rst, .data, .even);
  task check(input logic [3:0] value, input logic expected);
    begin data = value; #1 if (even !== expected) $display("FAIL data=%0h", value); end
  endtask
  initial begin
    #1 if (even !== 1'b0) $display("FAIL reset");
    rst = 0; check(4'b0000, 1'b1); check(4'b0011, 1'b1); check(4'b0001, 1'b0); check(4'b0111, 1'b0);
    $display("PASS"); $finish;
  end
endmodule
