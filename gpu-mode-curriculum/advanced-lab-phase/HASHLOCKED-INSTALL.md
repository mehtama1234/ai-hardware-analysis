# Observed offline hash-checked CPU installation

The second fresh virtual environment installed successfully with pip exit code
0. Observed command, from the repository root:

```bash
/tmp/gpu-checkpoint-cpu-tNuEhP/venv-hashlocked/bin/python -m pip install --disable-pip-version-check --no-compile --no-index --find-links /tmp/gpu-checkpoint-cpu-tNuEhP/wheels --require-hashes -r gpu-mode-curriculum/advanced-lab-phase/cpu-wheel-lock.txt --log /tmp/gpu-checkpoint-cpu-tNuEhP/hashlocked-install.log
```

The environment was newly created with `python3 -m venv`, without inherited
system packages. All 15 dependencies were installed from the local wheel set;
`--no-index` disabled package-index lookup and `--require-hashes` checked the
recorded wheel hashes. `--no-compile` only omitted installation-time bytecode
generation. The system environment and first isolated environment were unchanged.

Observed installation identities:

- Lock SHA-256: `5d872688a867394a87071c346e64cdcb7844746dba9c86b50fb0701351f70507`.
- Installation log SHA-256: `dccaa68924a3921fed51d01c96b69ebd8bf5a83000e6471008d1a12bca66b575`.
- Log completion: `2026-09-06T19:14:19` local time.

The paths above are temporary and are not portable deliverables. Reproduction
requires acquiring the same wheels and preserving the recorded lock, not simply
regenerating hashes for different files.

The full checkpoint subsequently passed under the second environment: 55 tests
and all eight CPU experiments succeeded; the CUDA training request was explicitly
unavailable. All isolation/dependency/execution checks passed and the recorded
checkpoint hash matched the actual file. The interpreter recorded in
`isolated-cpu-reproduction.json` is the `venv-hashlocked` interpreter above.

This establishes observed offline hash-checked installation and runtime
reproduction against the current worktree. It does not establish fresh-checkout
validity, GPU execution, or completion of the broader curriculum goal. The wheel
manifest's installation flag remains false by design because its builder only
validates archives; installation/runtime evidence is recorded separately here
and in the reproduction report.

## Current expanded reproduction

The exact 15-wheel set was reacquired and installed offline into a new Python
3.10 virtual environment at `/tmp/gpu-checkpoint-repro-CIEqu4/venv` using the
same lock and `--require-hashes`. The expanded checkpoint then passed with 116
tests and 23 CPU experiments. All 25 isolation/dependency/execution checks
passed; CUDA and HIP remained explicit unavailable results. The authoritative
current report is [isolated-cpu-reproduction.json](isolated-cpu-reproduction.json).

This establishes package-level reproducibility for the current source snapshot,
not reproduction on an independent host or GPU hardware.
