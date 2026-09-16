`timescale 1ns/1ps
module heldout_tb;
    reg clk = 0, rst = 0, s_axis_tvalid = 0, m_axis_tready = 1, rxd = 1;
    reg [7:0] s_axis_tdata = 0;
    reg [15:0] prescale = 1;
    wire [7:0] m_axis_tdata;
    wire m_axis_tvalid, s_axis_tready, txd, tx_busy, rx_busy, rx_overrun_error, rx_frame_error;
    uart dut(.clk(clk), .rst(rst), .s_axis_tdata(s_axis_tdata), .s_axis_tvalid(s_axis_tvalid),
             .s_axis_tready(s_axis_tready), .m_axis_tdata(m_axis_tdata),
             .m_axis_tvalid(m_axis_tvalid), .m_axis_tready(m_axis_tready), .rxd(rxd),
             .txd(txd), .tx_busy(tx_busy), .rx_busy(rx_busy),
             .rx_overrun_error(rx_overrun_error), .rx_frame_error(rx_frame_error),
             .prescale(prescale));
    always #5 clk = ~clk;
    initial begin
        $dumpfile("trace.vcd"); $dumpvars(0, dut);
        #1 rst = 1;
        @(posedge clk); #1;
        if (txd !== 1'b1) $display("FAIL reset idle txd=%b", txd);
        else $display("PASS heldout UART reset and idle-line contract");
        $finish;
    end
endmodule
