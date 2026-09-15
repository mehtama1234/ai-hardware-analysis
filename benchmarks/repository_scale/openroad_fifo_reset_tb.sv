`timescale 1ns/1ps

module openroad_fifo_reset_tb;
  logic [31:0] wdata;
  logic winc, wclk, wrst_n;
  logic rinc, rclk, rrst_n;
  wire [31:0] rdata;
  wire wfull, rempty;

  fifo dut (
    .rdata(rdata), .wfull(wfull), .rempty(rempty), .wdata(wdata),
    .winc(winc), .wclk(wclk), .wrst_n(wrst_n), .rinc(rinc),
    .rclk(rclk), .rrst_n(rrst_n)
  );

  always #2 wclk = ~wclk;
  always #3 rclk = ~rclk;

  initial begin
    wclk = 0; rclk = 0; wdata = 0; winc = 0; rinc = 0;
    wrst_n = 0; rrst_n = 0;
    #1;
    if (rempty !== 1'b1) begin
      $display("FAIL fifo reset empty=%b", rempty);
      $finish(1);
    end
    #10;
    wrst_n = 1; rrst_n = 1;
    #1;
    if (rempty !== 1'b1) begin
      $display("FAIL fifo post-reset empty=%b", rempty);
      $finish(1);
    end
    $display("PASS fifo reset state");
    $finish(0);
  end
endmodule
