# Hardware access requirements — checkpoint follow-up

## Observed local visibility, 2026-09-06

Read-only inventory found no accessible analog-compute board or measurement
instrument. `lsusb` returned exit 1 with no devices; this is limited visibility,
not proof of no physical USB hardware. `lspci` listed Virtio storage/filesystem
devices and a Microsoft 3D controller, not a positively identified analog array
or FPGA target. No FPGA class, IIO device directory, USB instrument class,
serial-by-id, usbtmc, ttyUSB or ttyACM paths were present.

No remote network scan, lab connection, device programming, purchase or external
message was attempted. Disconnected and remote hardware access remains unknown.

## Minimum workload capability, derived from the frozen contract

- Execute 64 input features against 32 output columns: 2,048 signed weights
  and 2,048 multiply-accumulate terms per first-layer evaluation.
- Return 32 analog-computed results to digital bias/ReLU processing. Tiling,
  bit slicing or multiplexing may expand the number of conversions and transfers;
  those counts cannot be fixed until the array and converter are specified.
- Retain the digital 32×10 output layer, argmax, calibration and fault fallback.
- Support reproducible weight realization/programming, input encoding, output
  scaling, saturation/error reporting and synchronized task traces.
- Expose a defensible power/energy measurement boundary, including conversion,
  controller/data movement and fallback. Instruments must resolve that boundary;
  requirements for bandwidth, sampling and uncertainty depend on actual hardware.

These are logical workload requirements, not a selected electrical design.
For example, two conductance cells per signed weight would imply 4,096 cells
before redundancy/bit slicing, but that encoding has NOT been selected.
We must not infer a physical 64×32 crossbar from the matrix shape.

## Information needed to choose the implementation

1. Analog computation: device/board identity, actual availability, array type and
   dimensions, programming/input/output interfaces, usable documentation.
2. Control: available FPGA/MCU/host boards and interface access. A controller
   alone is not the analog computation path.
3. Measurement: available power/current instruments, oscilloscope/DAQ and
   synchronization connections, including remote lab access if applicable.
4. Constraints: whether hardware already exists; if not, budget/access/fabrication
   constraints for a proposal. Any acquisition still needs explicit approval.

If the answer is “software only,” the honest next deliverable is a feasibility
and acquisition proposal plus circuit-linked simulation, not a claim of hardware
completion. The original hardware-backed goal remains open.
