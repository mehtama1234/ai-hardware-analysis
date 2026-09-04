* CMOS inverter starter deck.
* This is a conceptual placeholder until a real PDK model is selected.

.param vdd=1.8
VDD vdd 0 {vdd}
VIN in 0 PULSE(0 {vdd} 1n 100p 100p 5n 10n)

* Level-1 toy devices for first measurements only.
M1 out in 0 0 nmos W=1u L=180n
M2 out in vdd vdd pmos W=2u L=180n

.model nmos nmos level=1 VTO=0.5 KP=120u
.model pmos pmos level=1 VTO=-0.5 KP=40u

.tran 10p 20n
.control
run
print v(in) v(out)
.endc

.end

