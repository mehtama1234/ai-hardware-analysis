# AIMC Toolkit Install Scripts

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
