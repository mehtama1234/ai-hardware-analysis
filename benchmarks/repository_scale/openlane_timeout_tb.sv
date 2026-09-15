`timescale 1ns/1ps

module openlane_timeout_tb;
  logic clk, rst, start;
  wire timed_out;
  timeout dut(.clk(clk), .rst(rst), .start(start), .timed_out(timed_out));
  always #5 clk = ~clk;

  initial begin
    clk = 0; rst = 1; start = 0;
    repeat (2) @(posedge clk);
    rst = 0;
    @(negedge clk);
    start = 1;
    @(negedge clk);
    start = 0;
    // The specified timeout is two active cycles after start.
    @(posedge clk);
    #1;
    if (!timed_out) begin
      $display("FAIL timeout boundary is late");
      $finish(1);
    end
    $display("PASS timeout boundary");
    $finish(0);
  end
endmodule
