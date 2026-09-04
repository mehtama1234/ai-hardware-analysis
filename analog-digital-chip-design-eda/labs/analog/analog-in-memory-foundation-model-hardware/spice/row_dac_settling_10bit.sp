* 10-bit row-DAC settling fixture for AIMC converter handoff.
* This is an executable load-and-settling model, not a transistor DAC.
* The Python runner overrides vtarget for low, midscale, and high-code cases.

.param vtarget=0.5
.param rdrv=600
.param rrow=100
.param cload=0.67p
.param trise=20p
.param tfall=20p

VDAC src 0 PULSE(0 {vtarget} 0.1n {trise} {tfall} 10n 20n)
RDRV src row_in {rdrv}
RROW row_in row_far {rrow}
CLOAD row_far 0 {cload}

.tran 10p 5n
.measure tran vsettled FIND v(row_far) AT=4.1n
.control
run
.endc

.end
