module tb;
  logic clk = 0, rst = 1, wr_en = 0, rd_en = 0;
  logic [2:0] count;
  fifo #(.DEPTH(2)) dut(.clk, .rst, .wr_en, .rd_en, .count);
  always #5 clk = ~clk;
  initial begin
    $dumpfile("waveform.vcd"); $dumpvars(0, tb);
    #12 rst = 0;
    wr_en = 1; #10; // first accepted write
    #10;            // second accepted write; FIFO is now full
    #10;            // third write while full must be rejected
    if (count !== 3'd2) begin
      $display("FAIL cycle=3 signal=count expected=2 actual=%0d", count);
      $finish(1);
    end
    $display("PASS"); $finish(0);
  end
endmodule
