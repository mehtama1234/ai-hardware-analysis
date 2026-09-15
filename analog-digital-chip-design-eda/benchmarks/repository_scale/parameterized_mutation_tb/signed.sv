module tb;
  logic rst = 1; logic signed [3:0] a = 0, b = 0; logic signed [5:0] sum;
  signed_add dut(.rst, .a, .b, .sum);
  task check(input integer av, input integer bv, input integer expected);
    begin a = av; b = bv; #1 if (sum !== expected) $display("FAIL a=%0d b=%0d", av, bv); end
  endtask
  initial begin
    #1 if (sum !== 0) $display("FAIL reset");
    rst = 0; check(-1, -1, -2); check(-1, 1, 0); check(2, 3, 5); check(-8, -1, -9);
    $display("PASS"); $finish;
  end
endmodule
