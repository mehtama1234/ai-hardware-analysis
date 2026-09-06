load receiver_nfet -force
box position 0um 0um
box size 0um 0um
sky130::sky130_fd_pr__nfet_01v8_draw [sky130::sky130_fd_pr__nfet_01v8_defaults]
save receiver_nfet
load receiver_pfet -force
box position 0um 0um
box size 0um 0um
sky130::sky130_fd_pr__pfet_01v8_draw [sky130::sky130_fd_pr__pfet_01v8_defaults]
save receiver_pfet
quit -noprompt
