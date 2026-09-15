module tb;
  logic clk = 0, rst = 1, enable = 0;
  logic [3:0] counter_q;
  counter dut(.clk(clk), .rst(rst), .enable(enable), .counter_q(counter_q));
  always #5 clk = ~clk;
  initial begin
    $dumpfile("targeted-coverage.vcd"); $dumpvars(0, tb);
    #1 $display("COVERED reset");
    #11 rst = 0; #9;
    if (counter_q !== 4'd0) begin $display("FAIL hold"); $finish(1); end
    $display("COVERED hold");
    enable = 1; #10;
    if (counter_q !== 4'd1) begin $display("FAIL enable"); $finish(1); end
    $display("COVERED enable");
    enable = 0; #10;
    if (counter_q !== 4'd1) begin $display("FAIL post-enable-hold"); $finish(1); end
    $display("COVERED post-enable-hold"); $display("PASS"); $finish(0);
  end
endmodule
