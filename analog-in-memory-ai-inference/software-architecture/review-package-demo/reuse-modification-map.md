# Reuse And Modification Map

Start from the main workbench [Connected System Map](../connected-system-map.html). This map uses the same object, constraint, design move, evidence, allowed claim, refused claim, and next-handoff contract.

This file answers one practical question:

```text
What can we reuse, what must we change, and what must we build ourselves?
```

The short answer is:

```text
We can reuse toolkits for narrow proof steps. We still need our own chip target, runtime package, board path, calibration path, evidence contract, and claim engine.
```

## Rule

No outside toolkit owns the full product.

A toolkit can help answer one question, such as whether analog noise may hurt accuracy or whether a memory grid may create layout risk. It does not prove that our chip runs a customer workload on a board with measured power, measured temperature, calibration, fallback, and task accuracy.

## Reuse Map

| Area | What We Reuse | What We Modify Or Build | What This Can Prove | What This Cannot Prove |
| --- | --- | --- | --- | --- |
| Analog accuracy | AIHWKIT, AIHWKIT-Lightning, XBTorch, RxNN, TxSim, or a local analog-error model. | Add our memory behavior, drift behavior, write behavior, temperature assumptions, voltage assumptions, and calibration assumptions. | It can support an analog accuracy risk discussion under stated assumptions. | It cannot prove board speed, board power, final silicon behavior, or production readiness. |
| Crossbar layout risk | CrossSim or a local crossbar layout estimator. | Add our tile size, wire assumptions, bit-slicing rule, converter range, array count, and physical placement assumptions. | It can support a layout risk estimate or simulation. | It cannot prove the packaged chip behaves the same way without measured silicon. |
| Compiler structure | analog-mlir ideas such as layer extraction, analog conversion, weight isolation, task graph assembly, and Golem/SST lowering. | Add transformer scanning, VLA action-head handling, sensor-front-end handling, chip-specific lowering, runtime command generation, register writes, firmware interface, board package output, calibration metadata, update metadata, and failure handling. | It can support compiler mapping evidence when tied to a target and artifact. | It cannot prove deployability until it can generate a package the board can load and run. |
| System simulation | SST/Golem, ALPINE/gem5-X, gem5-style simulation, or a local runtime estimator. | Add our host dispatch model, memory movement model, converter timing, tile parallelism, firmware behavior, fallback behavior, and failure paths. | It can support system timing risk before board hardware is ready. | It cannot prove measured board latency, measured energy, or measured heat. |
| Hardware estimates | NeuroSim, MNSIM, spreadsheets, or local area and energy estimators. | Add our cell choice, node assumptions, ADC/DAC cost, SRAM cost, board support cost, package assumptions, and measurement boundaries. | It can support early planning and tradeoff discussion. | It cannot prove real power, cost, yield, or thermal behavior. |
| Board runtime | Existing board links such as USB, Ethernet, PCIe, JTAG, UART, or vendor debug tools. | Add our board package format, firmware loader, command protocol, runtime status, failure trace, debug trace, and synchronized artifact id. | It can prove that the exact package ran or failed on the exact board setup. | It cannot prove power or task accuracy unless those traces are collected for the same run. |
| Power and thermal measurement | Lab power meters, rail monitors, thermal cameras, on-board sensors, and imported trace files. | Add rail naming, sampling rules, board id, firmware id, package id, workload id, temperature locations, and pass/fail rules. | It can prove measured energy and temperature for the tested setup. | It cannot prove model accuracy or long-term reliability by itself. |
| Calibration | Simulators can suggest risks. Board and lab tools must create the real calibration record. | Add temperature monitors, voltage monitors, reference cells, tile health checks, weak-tile lists, correction values, recalibration commands, and fallback rules. | It can support trust in a measured run when tied to the same board, chip, and condition. | It cannot be replaced by generic simulator assumptions. |
| Weight updates | TxSim, XBTorch, RxNN, AIHWKIT-style update models, or internal write models. | Add update scope, write command, write latency, write energy, endurance, retention, recalibration, rollback, and failed-update behavior. | It can classify the product as fixed-weight, periodic-update, adapter-update, or adaptive-blocked. | It cannot prove adaptive Physical AI unless update cost, endurance, rollback, and post-update accuracy are measured or validated. |
| Sensor path | Sensor datasheets, board traces, local preprocessing estimates, and task datasets. | Add capture timing, buffering, synchronization, preprocessing, input energy, ownership boundary, and task linkage. | It can show whether the full input path is counted. | It cannot prove chip benefit if sensor and preprocessing cost are excluded from the result. |
| Evidence package | Manifest, schema, step artifacts, import templates, package index, archive builder, and smoke tests. | Add live adapters, raw file preservation, source review records, claim rules, report generation, package comparison, and user upload/import flows. | It can prove that the review workflow separates assumptions from evidence. | It cannot prove chip performance until real evidence artifacts exist. |

## What We Should Not Build From Scratch First

Do not start by writing a full physics simulator, full compiler, full board service, and full dashboard from nothing.

Start by reusing known tools where they answer a narrow question:

- use AIHWKIT-style tools for analog behavior risk
- use CrossSim-style tools for crossbar layout risk
- use analog-mlir ideas for model-to-analog compiler structure
- use SST/Golem or ALPINE-style tools for system timing risk
- use lab import templates for board, power, thermal, calibration, update, sensor, and task evidence

## What We Must Own

We must own the parts that are specific to our product:

- the chip target
- the physical tile rules
- the bit-slicing rules
- the ADC and DAC scheduling rules
- the calibration profile format
- the weak-tile and correction-value format
- the weight update and rollback policy
- the board package format
- the runtime command protocol
- the source-to-claim rules
- the final claim engine

## Product Meaning

For a user, this map should remove confusion.

They should not leave thinking:

```text
AIHWKIT will build the product for us.
```

They should leave thinking:

```text
AIHWKIT and related tools help us test specific risks. The company still has to build the chip-specific compiler, runtime, board, calibration, evidence, and claim layers.
```
