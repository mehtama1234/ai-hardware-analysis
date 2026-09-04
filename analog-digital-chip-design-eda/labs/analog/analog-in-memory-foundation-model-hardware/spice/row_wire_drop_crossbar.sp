* Row wire drop in a simple crossbar.
* The left side is driven by an input voltage. Each row segment has resistance.
* The cells farther from the driver see a smaller voltage.

.param rseg=25
.param rcell1=10k rcell2=10k rcell3=10k rcell4=10k

VIN in 0 DC 0.8

RROW1 in n1 {rseg}
RROW2 n1 n2 {rseg}
RROW3 n2 n3 {rseg}
RROW4 n3 n4 {rseg}

R1 n1 col {rcell1}
R2 n2 col {rcell2}
R3 n3 col {rcell3}
R4 n4 col {rcell4}

VSENSE col 0 DC 0

.control
op
print v(in) v(n1) v(n2) v(n3) v(n4) i(VSENSE)
alterparam rseg = 100
reset
op
print v(in) v(n1) v(n2) v(n3) v(n4) i(VSENSE)
alterparam rseg = 500
reset
op
print v(in) v(n1) v(n2) v(n3) v(n4) i(VSENSE)
quit
.endc

.end
