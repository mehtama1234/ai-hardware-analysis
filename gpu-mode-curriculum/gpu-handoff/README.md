# GPU Host Handoff

This layer packages the generated GPU promotion manifest, dry-run command suite, GPU-run collector, and validation commands into a single handoff bundle for accelerator machines.

Run locally:

```bash
python3 scripts/build_gpu_handoff.py
python3 scripts/verify_gpu_handoff.py
```

On a GPU host:

```bash
bash gpu-handoff/bin/run-gpu-host-handoff.sh h100-node-001 --dry-run
bash gpu-handoff/bin/run-gpu-host-handoff.sh h100-node-001 --execute
```
