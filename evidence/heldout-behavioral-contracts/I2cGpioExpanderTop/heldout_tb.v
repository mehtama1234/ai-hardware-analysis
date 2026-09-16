`timescale 1ns/1ps
module heldout_tb;
    reg clock = 0, reset = 0;
    reg [2:0] io_address = 0;
    reg io_i2c_scl_read = 1, io_i2c_sda_read = 1;
    reg [7:0] io_gpio_pins_read = 0;
    wire io_i2c_scl_write, io_i2c_sda_write;
    wire [0:0] io_i2c_interrupts;
    wire [7:0] io_gpio_pins_write, io_gpio_pins_writeEnable;

    I2cGpioExpander dut(.*);
    always #5 clock = ~clock;

    initial begin
        $dumpfile("trace.vcd"); $dumpvars(0, dut);
        #1;
        @(posedge clock); #1;
        if (io_gpio_pins_writeEnable !== 8'h00 || io_gpio_pins_write !== 8'h00 || io_i2c_interrupts !== 1'b0)
            $display("FAIL I2C expander reset outputs");
        else $display("PASS heldout I2C GPIO expander reset contract");
        reset = 1'b1;
        $finish;
    end
endmodule
