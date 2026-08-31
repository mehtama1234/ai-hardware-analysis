# GPUMODE GPU Evidence Provenance

This layer separates synthetic GPU-shaped fixtures, local host-collected smoke
runs, and true measured accelerator-host imports.

Run:

```bash
python3 scripts/build_gpu_runs.py
python3 scripts/build_gpu_provenance.py
python3 scripts/verify_gpu_provenance.py
```

Artifacts:

- `gpu-provenance/gpu-provenance-report.json`
- `gpu-provenance/reports/gpu-provenance-report.md`
- `site/gpu-provenance.html`
