# Executive Brief

Package: `demo-analog-roadmap-001`

This brief explains the demo review package without requiring the reader to open raw JSON.

Start from the main workbench [Connected System Map](../connected-system-map.html) when you need the full path from package object to constraint, evidence, allowed claim, refused claim, and next handoff.

## Connected-System Contract

Read this package through the same contract as the live workbench:

```text
object -> constraint -> design move -> evidence -> allowed claim -> refused claim -> next handoff
```

For the current live AIMC work, the object is package `pkg-e931662a01293df2`. The proven loop is local model placement into hardware-lab evidence and backend claim readiness. The refused claims are measured board latency, measured energy, calibrated silicon, analog macro integration, package reliability, and production readiness.

## Current Answer

The current safe answer is **partial fit with missing proof**.

Analog compute may help parts of the workload that spend most of their time doing repeated matrix math. That does not mean the whole modern AI workload is ready for analog execution. Dynamic attention, normalization, action timing, safety behavior, calibration, board runtime, power, temperature, task accuracy, weight updates, and sensor input costs still need proof.

## What Is Safe To Say

It is safe to say:

- the roadmap has a clear proof path
- the demo package has fourteen review artifacts
- each artifact states its proof level, missing evidence, supported claims, and blocked claims
- analog may be useful for selected matrix-heavy sections if later evidence supports the same package and setup

## What Is Not Safe To Say

It is not safe to say:

- hardware proof exists for the chip
- measured power savings exist for the chip
- measured task accuracy exists for the chip
- the chip can run a full VLA model
- the chip supports adaptive weight updates
- the simulator proves production behavior

Those claims need matching artifacts before they are allowed.

## Why This Matters Now

More AI work is moving into machines, sensors, vehicles, robots, industrial systems, and other local devices. These systems often cannot wait for a cloud response. They also have limited power and must react to the physical world.

This trend creates an opening for low-power local inference chips. It also raises the bar. A chip company must prove the whole path, not only the analog math block.

## Main Decision

The right company roadmap is not "build an analog chip and then write software later."

The right roadmap is:

1. build the virtual chip model and proof workbench
2. build the compiler and runtime path
3. build the hybrid analog and digital chip target
4. connect board, power, temperature, calibration, task, update, and sensor evidence
5. export one review package that separates proof from assumption

## Top Blockers

The strongest blockers are:

- no real chip target compiler output yet
- no board runtime trace yet
- no measured power or temperature trace yet
- no task accuracy result from the same package and setup yet
- no calibration trace or failed-calibration fallback proof yet
- no weight update endurance, rollback, or post-update accuracy proof yet
- no sensor-to-answer timing and energy evidence yet

## Next Executive Milestone

The next meaningful milestone is not a broader claim. It is a stronger evidence package.

The company should aim to produce a package where one selected workload has:

- model parse
- analog fit report
- analog simulation result
- crossbar layout simulation
- compiler mapping
- runtime estimate
- board run
- power trace
- temperature trace
- task accuracy result
- calibration record
- final safe claim boundary

Until then, the safe claim remains partial fit with missing proof.
