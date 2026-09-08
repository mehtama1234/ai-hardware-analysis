# Native HIP validation path

From the repository root, on a suitable HIP development host:

```bash
python3 gpu-mode-curriculum/programming-projects/rocm-hip-port/run_native.py
```

The runner builds the native source in a temporary directory (120-second limit),
then runs it (60-second limit). Compilation failure, malformed output, numerical
failure or invalid timing is a failure, not a skip. Missing `hipcc` or an explicit
no-device response is unavailable. Exit codes are 0 passed, 1 failed, 2 unavailable.
The report retains compiler command/output, execution output and source hashes.
Temporary binaries are removed afterward.

The program checks lengths 1, 255, 256, 257 and 65539 with 256 threads per block.
Host inputs are deterministic binary fractions; FP64 host addition is the oracle.
NaN-initialized output must become finite and agree within absolute error 1e-6.
Three warmups precede seven device-event batches of 100 launches. Per-launch
batch averages exclude allocation and copies but may include gaps between launches.
This is not sustained memory-bandwidth or isolated single-kernel latency proof.

`measure.py` remains a readiness/metadata report and never invokes this program.
Its numerical correctness is therefore `not_executed`, even when `hipcc` exists.
The native runner is separate and must actually pass before hardware acceptance.

```bash
python3 -m unittest discover -s gpu-mode-curriculum/programming-projects/rocm-hip-port -p 'test_*.py' -v
```

Six Python tests passed locally; they cover readiness labeling, generator preservation, missing compiler,
compile timeout, valid synthetic payload and rejected corrupt payloads. They do
not compile or run HIP. The local native attempt reports unavailable because
`hipcc` is absent. Actual compilation, GPU execution, sanitizer checks, device
identity/topology capture and a matched second-platform comparison remain open.

The aggregate advanced checkpoint now runs these Python tests and requests native
execution. Only an unavailable result with empty rows and no GPU acceptance is
an allowed skip; actual build/run/validation failures fail the checkpoint.
