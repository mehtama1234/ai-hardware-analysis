module tb;
  logic clk = 0, rst = 1, wr_en = 0, rd_en = 0; logic [2:0] count;
  fifo #(.DEPTH(2)) dut(.clk, .rst, .wr_en, .rd_en, .count);
  always #5 clk = ~clk;
  task tick; begin #10; end endtask
  initial begin
    tick; rst = 0; wr_en = 1; tick;
    if (count !== 3'd1) $display("FAIL first-write");
    tick;
    if (count !== 3'd2) $display("FAIL second-write");
    tick;
    if (count !== 3'd2) $display("FAIL full-boundary");
    wr_en = 0; rd_en = 1; tick; if (count !== 3'd1) $display("FAIL read");
    rd_en = 0; tick; if (count !== 3'd1) $display("FAIL idle");
    $display("PASS"); $finish;
  end
endmodule
