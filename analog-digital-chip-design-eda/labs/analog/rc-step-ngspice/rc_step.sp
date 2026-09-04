* RC step response: voltage changes by moving charge through resistance.

.param vdd=1.0
VIN in 0 PULSE(0 {vdd} 1n 10p 10p 10n 20n)
R1 in out 10k
C1 out 0 1p

.tran 10p 30n
.control
run
print v(in) v(out)
.endc

.end

