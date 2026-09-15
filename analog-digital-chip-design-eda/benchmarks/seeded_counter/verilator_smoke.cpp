#include "Vcounter.h"
#include "verilated.h"

static void tick(Vcounter* dut) {
    dut->clk = 0;
    dut->eval();
    dut->clk = 1;
    dut->eval();
}

int main(int argc, char** argv) {
    Verilated::commandArgs(argc, argv);
    Vcounter dut;
    dut.rst = 1;
    dut.enable = 0;
    tick(&dut);
    if (dut.counter_q != 0) return 1;
    dut.rst = 0;
    tick(&dut);
    if (dut.counter_q != 0) return 2;
    dut.enable = 1;
    tick(&dut);
    if (dut.counter_q != 1) return 3;
    VL_PRINTF("VERILATOR_SMOKE_PASS\n");
    return 0;
}
