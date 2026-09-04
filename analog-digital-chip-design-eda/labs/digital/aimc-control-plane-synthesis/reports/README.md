# AIMC Control Plane Synthesis Reports

This folder holds generated Yosys artifacts for the AIMC control-plane RTL.

Run from the parent lab directory:

```bash
yosys synth_aimc_control_plane.ys
```

Expected generated files:

- `aimc_control_plane_synth.log`
- `aimc_control_plane_synth.v`

These files are evidence for RTL lowering. They are not timing, layout, or signoff evidence.
