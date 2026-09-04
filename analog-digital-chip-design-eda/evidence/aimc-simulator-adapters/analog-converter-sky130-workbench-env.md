# Analog Converter Sky130 Workbench Environment

- status: `sky130_workbench_environment_ready_not_layout`
- workbench: `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench`
- environment file count: `4`
- all PDK files present: `True`
- physical converter cell count: `4`
- ready for manual layout start: `True`
- candidate evidence written: `False`

## First Principle

The PDK tells the tools how to read process-specific shapes. The environment files put that knowledge next to the converter workbench, so a layout session starts from the same process, same model files, and same corner every time.

This still does not create the converter. It only removes setup ambiguity before the manual or imported physical-cell step.

## Environment Files

- `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/.magicrc` (194 bytes)
- `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/sky130-ngspice.includes` (163 bytes)
- `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/xschemrc.local` (209 bytes)
- `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/run-layout-env-check.sh` (596 bytes)

## PDK Files

- magic_rc: `/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/magic/sky130A.magicrc` exists `True` bytes `3713`
- magic_tech: `/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/magic/sky130A.tech` exists `True` bytes `164660`
- xschem_rc: `/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/xschem/xschemrc` exists `True` bytes `21397`
- ngspice_lib: `/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice` exists `True` bytes `6349`
- ngspice_tt: `/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/ngspice/corners/tt.spice` exists `True` bytes `2676`

## Start Commands

- `cd labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench`
- `magic -dnull -noconsole`
- `xschem --rcfile xschemrc.local`
- `./run-layout-env-check.sh`

## Refused Claim

does not draw converter cells, does not run DRC/LVS/extraction, does not write candidate evidence, and does not create accepted post-layout evidence
