* Differential signed-weight crossbar.
* Positive and negative conductance columns are sensed separately.
* The signed dot product is I(pos) - I(neg).

.param gscale=100u

V1 row1 0 DC 0.25
V2 row2 0 DC 0.75
V3 row3 0 DC 0.50
V4 row4 0 DC 0.10

* Column 1 represents weights: +0.8, -0.1, +0.2, +0.5
R11P row1 col1p {1/(0.8*gscale)}
R11N row1 col1n 1e12
R21P row2 col1p 1e12
R21N row2 col1n {1/(0.1*gscale)}
R31P row3 col1p {1/(0.2*gscale)}
R31N row3 col1n 1e12
R41P row4 col1p {1/(0.5*gscale)}
R41N row4 col1n 1e12

* Column 2 represents weights: -0.4, +0.7, +0.1, -0.2
R12P row1 col2p 1e12
R12N row1 col2n {1/(0.4*gscale)}
R22P row2 col2p {1/(0.7*gscale)}
R22N row2 col2n 1e12
R32P row3 col2p {1/(0.1*gscale)}
R32N row3 col2n 1e12
R42P row4 col2p 1e12
R42N row4 col2n {1/(0.2*gscale)}

VS1P col1p 0 DC 0
VS1N col1n 0 DC 0
VS2P col2p 0 DC 0
VS2N col2n 0 DC 0

.control
op
let col1_signed = i(VS1P) - i(VS1N)
let col2_signed = i(VS2P) - i(VS2N)
print i(VS1P) i(VS1N) col1_signed
print i(VS2P) i(VS2N) col2_signed
quit
.endc

.end
