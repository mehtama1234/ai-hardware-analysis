# Checkpoint environment and reproduction boundary

The existing `gpu-kernels-serving-lab/requirements.txt` is an unpinned broad lab
list. It is not a reproducible environment for this advanced checkpoint.

Capture the active interpreter's core dependency closure:

```bash
python3 gpu-mode-curriculum/scripts/capture_checkpoint_environment.py
```

The script records installed versions and checks active default-extra dependency
constraints for PyTorch, NumPy, scikit-learn and packaging, recursively. It emits
`environment-snapshot.json` and `observed-environment-constraints.txt`. Direct
URLs are not copied from package metadata. Optional environment inventory probes
in older labs are outside this minimal closure.

These constraints are observations, not a tested install recipe or wheel-hashed
lockfile. Inspect missing packages/conflicts before attempting reproduction.
Distribution metadata and runtime build strings can differ: the current torch
distribution reports 2.4.1 while its imported runtime identifies 2.4.1+cu121.
Installed CUDA libraries do not prove a device or CUDA compiler is available.

## Remaining isolated reproduction gate

1. Select CPU-only versus CUDA wheel provenance explicitly; do not install both
   into one environment or silently change backends.
2. Resolve compatible versions in a new virtual environment without inherited
   site packages, record artifact hashes and interpreter/platform requirements.
3. Run the full checkpoint there, including the trained digits task, and compare
   correctness and protocol outcomes. Do not require timings to match another host.
4. Record the clean environment's source hashes, package closure and raw logs.
5. Only then mark isolated reproduction accepted. A metadata audit alone cannot
   establish it, and optional GPU work must remain unavailable when appropriate.

## CPU-only candidate recipe

`cpu-requirements.txt` pins the CPU checkpoint's dependencies separately from
the observed CUDA-enabled environment. Use Python 3.10 on Linux x86_64 for this
initial reproduction target. Create a new virtual environment without
`--system-site-packages`; then use its Python executable for both commands:

```bash
python -m pip install --index-url https://download.pytorch.org/whl/cpu torch==2.4.1+cpu
python -m pip install --index-url https://pypi.org/simple -r gpu-mode-curriculum/advanced-lab-phase/cpu-requirements.txt
python -m pip check
python gpu-mode-curriculum/scripts/run_isolated_cpu_reproduction.py
```

The first command follows the [official PyTorch 2.4.1 CPU wheel instructions](https://docs.pytorch.org/get-started/previous-versions/).
The second pins transitive dependencies too; any unpinned versions temporarily
selected by the first command must be replaced before running the checkpoint.
This installs approximately 195 MB of compressed PyTorch plus dependencies,
with larger unpacked disk usage. It does not install CUDA runtimes or a GPU
compiler. Successful installation alone does not complete reproduction.

The wrapper verifies virtual-environment configuration, disabled user/system
site packages, imported package locations, CPU-only PyTorch, exact version pins,
and `pip check` before running the checkpoint. It records raw subprocess logs
and the regenerated checkpoint hash in `isolated-cpu-reproduction.json`.
This is reproduction against the current worktree: a fresh checkout and a
wheel-hashed lock remain separate requirements even if this check passes.

## Verified CPU reproduction (2026-09-07 UTC)

The freshly recreated pinned Python 3.10 CPU environment completed the expanded
checkpoint: 116 tests passed, all 23 CPU experiment commands passed, and the
CUDA/HIP requests reported unavailable. All 25 wrapper checks passed, including
isolation, pins, pip consistency, artifact regeneration and use of the new
interpreter throughout. The recorded checkpoint SHA-256 matches its actual file.

Evidence: [isolated-cpu-reproduction.json](isolated-cpu-reproduction.json).
The temporary environment is `/tmp/gpu-checkpoint-repro-CIEqu4/venv`; it is not a
portable deliverable and may be removed by normal temporary-directory cleanup.
Use the pinned recipe to recreate it rather than relying on that path.

This closes the current-worktree/hash-locked package-environment check. A separate
fresh-source snapshot reproduction has also now passed; see
`fresh-checkout-reproduction.json`. That snapshot proves source-tree isolation,
not an independent host or GPU reproduction, and the original system environment
was not modified.

## Verified fresh source snapshot (2026-09-07)

`scripts/run_fresh_checkout_reproduction.py` copied the complete current source
snapshot (including uncommitted and untracked lab files) into a temporary Git
repository, created and verified a clean commit, and ran the full checkpoint from
that checkout. The snapshot passed all 116 tests, 23 CPU experiments, and
the explicit CUDA/HIP-unavailable checks. The recorded snapshot revision and
checkpoint hash are in [fresh-checkout-reproduction.json](fresh-checkout-reproduction.json).

This is stronger than current-worktree execution but is not a second machine or
accelerator result. The next foundation gate is independent-host reproduction
and broader profiler capture.

## Exact wheel lock

`cpu-wheel-lock.txt` and `cpu-wheel-manifest.json` identify 15 inspected wheels
for CPython 3.10/Linux x86_64, totaling 275,429,948 bytes. The builder verifies
archive metadata, names/versions, compatibility tags and active dependency
closure before hashing. Tests reject byte changes, metadata mismatches and
missing dependencies. This manifest is a byte-identity record, not a signature
or independent upstream security audit.

To build from a downloaded wheel directory and install offline into a NEW venv:

```bash
python gpu-mode-curriculum/scripts/build_cpu_wheel_lock.py /path/to/wheels
python -m pip install --no-compile --no-index --find-links /path/to/wheels --require-hashes -r gpu-mode-curriculum/advanced-lab-phase/cpu-wheel-lock.txt
python gpu-mode-curriculum/scripts/run_isolated_cpu_reproduction.py
```

Use the new virtual environment's Python for the install and reproduction
commands. `--no-compile` skips installation-time bytecode generation only.
The wheel files are temporary local artifacts, not checked into this repository.
Collect the CPU torch wheel from the official PyTorch CPU index and the other
pinned wheels from PyPI; keep this recorded lock unchanged when verifying a
reproduction. Regenerating hashes from arbitrary replacement wheels does not
verify those replacements against the original lock.

The latest offline hash-checked installation and runtime reproduction passed:
116 tests and all 23 CPU experiments succeeded, with CUDA/HIP explicitly
unavailable. See [the installation record](HASHLOCKED-INSTALL.md) and
`isolated-cpu-reproduction.json`. Independent-host and GPU validation remain
open.
