`timescale 1ns/1ps

module counter_tb;
    reg clk = 0;
    reg rst_n = 0;
    wire [3:0] count;

    counter dut (
        .clk(clk),
        .rst_n(rst_n),
        .count(count)
    );

    always #5 clk = ~clk;

    initial begin
        $dumpfile("counter.vcd");
        $dumpvars(0, counter_tb);
        #12 rst_n = 1;
        #100 $finish;
    end
endmodule

