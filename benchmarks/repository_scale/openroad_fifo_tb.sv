`timescale 1ns/1ps

module openroad_fifo_tb;
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
    #11;
    wrst_n = 1; rrst_n = 1;
    @(negedge wclk);
    wdata = 32'hcafe_beef;
    winc = 1;
    @(negedge wclk);
    winc = 0;
    wait (!rempty);
    @(negedge rclk);
    rinc = 1;
    // Sample the asynchronous read data at the consuming edge, before the
    // nonblocking read-pointer update advances raddr to the next word.
    @(posedge rclk);
    if (rdata !== 32'hcafe_beef) begin
      $display("FAIL fifo read data=%h", rdata);
      $finish(1);
    end
    rinc = 0;
    if (wfull === 1'bx || rempty === 1'bx) begin
      $display("FAIL fifo status unknown");
      $finish(1);
    end
    $display("PASS fifo functional read/write");
    $finish(0);
  end
endmodule
