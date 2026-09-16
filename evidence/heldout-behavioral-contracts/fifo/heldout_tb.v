`timescale 1ns/1ns
module heldout_tb;
    reg wclk = 0, rclk = 0;
    reg wrst_n = 1, rrst_n = 1;
    reg winc = 0, rinc = 0;
    reg [31:0] wdata = 0;
    wire [31:0] rdata;
    wire wfull, rempty;

    fifo dut(.rdata(rdata), .wfull(wfull), .rempty(rempty), .wdata(wdata),
             .winc(winc), .wclk(wclk), .wrst_n(wrst_n), .rinc(rinc),
             .rclk(rclk), .rrst_n(rrst_n));
    always #2 wclk = ~wclk;
    always #3 rclk = ~rclk;

    initial begin
        $dumpfile("trace.vcd");
        $dumpvars(0, dut);
        #1;
        wrst_n = 1'b0; rrst_n = 1'b0;
        #1;
        if (rempty !== 1'b1 || wfull !== 1'b0) $display("FAIL reset flags");
        wrst_n = 1'b1; rrst_n = 1'b1;
        @(negedge wclk); wdata = 32'hc0de1234; winc = 1'b1;
        @(negedge wclk); winc = 1'b0;
        repeat (8) @(posedge rclk);
        if (rempty !== 1'b0) $display("FAIL write did not become visible");
        else $display("PASS heldout fifo reset and asynchronous transfer contract");
        $finish;
    end
endmodule
