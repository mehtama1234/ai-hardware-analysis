module tb;
  logic rst = 1; logic [1:0] sel = 0; logic [3:0] decode;
  decoder dut(.rst, .sel, .decode);
  task check(input logic [1:0] s, input logic [3:0] expected);
    begin sel = s; #1 if (decode !== expected) $display("FAIL sel=%0d", s); end
  endtask
  initial begin
    #1 if (decode !== 4'b0000) $display("FAIL reset");
    rst = 0; check(2'd0, 4'b0001); check(2'd1, 4'b0010); check(2'd2, 4'b0100); check(2'd3, 4'b1000);
    $display("PASS"); $finish;
  end
endmodule
