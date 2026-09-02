# AIMC Toolkit Install Scripts

Start from the [Connected System Map](../connected-system-map.html). These scripts use the same contract: object, constraint, design move, evidence, allowed claim, refused claim, and next handoff.

Run this from `ai-hardware-analysis/analog-in-memory-ai-inference/software-architecture`:

```bash
bash scripts/install-aimc-toolkits.sh
```

The script installs and checks the runnable Python simulators first:

- IBM AIHWKIT
- Sandia CrossSim

It also clones and probes the heavier source toolchains:

- analog-mlir
- SST core
- ALPINE/gem5-X

If system packages are missing, the script records the exact blocker and prints the apt command to run. The full report is written to:

```text
backend/.data/toolkit-install/install-report.txt
```
