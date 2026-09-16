`timescale 1ns/1ns
module heldout_tb;
    reg HCLK = 0, HRESETn = 1, HSEL = 0, HREADY = 1, HWRITE = 0;
    reg [1:0] HTRANS = 0;
    reg [2:0] HSIZE = 0;
    reg [31:0] HADDR = 0, HWDATA = 0;
    wire HREADYOUT;
    wire [1:0] HRESP;
    wire [31:0] HRDATA;

    AHB_SPM dut(.HCLK(HCLK), .HRESETn(HRESETn), .HSEL(HSEL), .HREADY(HREADY),
                .HTRANS(HTRANS), .HSIZE(HSIZE), .HWRITE(HWRITE),
                .HADDR(HADDR), .HWDATA(HWDATA), .HREADYOUT(HREADYOUT),
                .HRESP(HRESP), .HRDATA(HRDATA));
    always #5 HCLK = ~HCLK;

    initial begin
        $dumpfile("trace.vcd");
        $dumpvars(0, dut);
        #1;
        HRESETn = 1'b0;
        #1;
        if (HREADYOUT !== 1'b1) $display("FAIL reset ready=%b", HREADYOUT);
        HRESETn = 1'b1;
        @(posedge HCLK); #1;
        if (HREADYOUT !== 1'b1) $display("FAIL idle ready=%b", HREADYOUT);
        else $display("PASS heldout AHB scratchpad reset and idle contract");
        $finish;
    end
endmodule
