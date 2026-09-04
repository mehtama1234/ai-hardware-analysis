* Four-by-four resistive crossbar for analog matrix-vector multiply.
* Row voltages are inputs. Conductances are weights. Column currents are sums.

.param r11=10k r12=20k r13=40k r14=80k
.param r21=16k r22=12k r23=33k r24=60k
.param r31=30k r32=18k r33=15k r34=90k
.param r41=70k r42=25k r43=22k r44=14k

V1 row1 0 DC 0.20
V2 row2 0 DC 0.45
V3 row3 0 DC 0.10
V4 row4 0 DC 0.70

R11 row1 col1 {r11}
R21 row2 col1 {r21}
R31 row3 col1 {r31}
R41 row4 col1 {r41}

R12 row1 col2 {r12}
R22 row2 col2 {r22}
R32 row3 col2 {r32}
R42 row4 col2 {r42}

R13 row1 col3 {r13}
R23 row2 col3 {r23}
R33 row3 col3 {r33}
R43 row4 col3 {r43}

R14 row1 col4 {r14}
R24 row2 col4 {r24}
R34 row3 col4 {r34}
R44 row4 col4 {r44}

* Ideal current-sense boundary. Each zero-volt source holds the column at virtual ground.
VSENSE1 col1 0 DC 0
VSENSE2 col2 0 DC 0
VSENSE3 col3 0 DC 0
VSENSE4 col4 0 DC 0

.control
op
print i(VSENSE1) i(VSENSE2) i(VSENSE3) i(VSENSE4)
quit
.endc

.end
