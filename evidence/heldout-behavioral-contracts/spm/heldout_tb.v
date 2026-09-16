`timescale 1ns/1ps
module heldout_tb;
    reg clk = 0, rst = 0, y = 0;
    reg [31:0] x = 0;
    wire p;

    spm #(32) dut (.clk(clk), .rst(rst), .x(x), .y(y), .p(p));
    always #5 clk = ~clk;

    initial begin
        $dumpfile("trace.vcd");
        $dumpvars(0, dut);
        #1;
        rst = 1;
        #1;
        if (p !== 1'b0) begin
            $display("FAIL reset product p=%0d", p);
        end else begin
            $display("PASS heldout spm reset contract");
        end
        $finish;
    end
endmodule
