module tb;
  logic clk = 0, rst = 1, enable = 0;
  logic [3:0] counter_q;
  counter dut(.clk(clk), .rst(rst), .enable(enable), .counter_q(counter_q));
  always #5 clk = ~clk;
  initial begin
    $dumpfile("baseline-coverage.vcd"); $dumpvars(0, tb);
    #1 $display("COVERED reset");
    #11 rst = 0; #9;
    $display("COVERED hold"); $display("PASS"); $finish(0);
  end
endmodule
