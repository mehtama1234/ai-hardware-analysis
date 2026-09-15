# WikiText numerical control checkpoint

The full model-to-hardware goal remains active. The CPU evaluation recorded
below has now completed and passed verification; hardware qualification remains
incomplete. The earlier running-process observations are preserved as history.

## Completion update

The existing process completed all 32 windows and exited with code zero.
All ideal numerical controls and exact digital fallback checks passed. The
package verifier checked 10 hashes and 128 rows, and four mutation checks
rejected corrupted arithmetic, failing numerical measurements, unsupported
analog claims and changed source. All quality rows exactly reproduce the
original experiment; only the documented numerical-control protocol changed.

No nonideal candidate passes the unchanged provisional quality screen:
ADC8 agreement is 82.7393%, ADC12 is 98.9014%, and ADC12 with noise 0.001 is
93.4326%. The NLL increases are 0.068642, 0.001207 and 0.014274 nats/token.
All clipping counters are zero.

The decision builder completed and its 10 output artifact hashes verified.
The decision is `retain_native_digital_execution`, saved in the sibling
software project under
`software-architecture/experiments/gpt2-hybrid-v1/decisions/20260909-wikitext-v2/`.
It preserves separate benchmark, compiled-software and physical-evidence scopes.

A separate train-observed ADC-range implementation and five unit tests are
prepared and pass. It has not yet been evaluated in GPT-2 and is not used in
either completed benchmark. Next development should evaluate range/precision
choices on validation data with frozen training calibration, then qualify on
independent task-representative data. Physical execution and matched costs
remain required for the full goal.

## Completed work

The first WikiText run completed all candidate rows but failed its absolute
raw-logit control. The two failing contexts were reproduced with native/tiled
FP32 and dense/tiled FP64 projection arithmetic. Local errors were about
1.91e−6; much of the larger downstream logit difference cancelled under
normalization. All six diagnostic cases retained the baseline token choices.

The original run remains rejected. A documented v2 protocol separately checks
local projection arithmetic, log probabilities, mean target loss, exact token
choices and exact digital fallback. Five control tests passed, including
negative tests for changed probabilities, incorrect arithmetic and nonfinite
inputs. Dataset selections, native baseline, candidate models and provisional
candidate acceptance thresholds are unchanged. The completed v2 rows checked
against the first run reproduced its quality metrics exactly.

See the sibling software project:
`software-architecture/experiments/gpt2-hybrid-v1/wikitext-evaluation.md`.

## Historical running work at the initial checkpoint

- Process: PID 223777, command `python3 scripts/run_gpt2_wikitext_projection.py
  --output experiments/gpt2-hybrid-v1/runs/20260909-wikitext-probability-control-v2`.
- Tool session: 92961. The last authoritative poll reported the process still
  running and 20 of 32 windows completed. About 1 GB of process memory was
  swapped out during the slowdown.
- Output directory is in the sibling software project's `software-architecture`.
- All 20 observed ideal-control rows passed. A final accepted package has not
  yet been observed.

This is a historical observation, not proof that a process remains live. Poll
the existing session or inspect the PID/command before taking action. Do not
restart or overwrite the run merely because output is delayed.

## Verification commands (now completed)

After the existing process terminates successfully, run from the sibling
software project's `software-architecture` directory:

```bash
python3 scripts/check_gpt2_wikitext_projection.py experiments/gpt2-hybrid-v1/runs/20260909-wikitext-probability-control-v2
python3 scripts/test_wikitext_package_rejection.py experiments/gpt2-hybrid-v1/runs/20260909-wikitext-probability-control-v2
python3 scripts/build_gpt2_evidence_decision.py --quality experiments/gpt2-hybrid-v1/runs/20260909-wikitext-probability-control-v2 --output experiments/gpt2-hybrid-v1/decisions/20260909-wikitext-v2
```

The package rejection tests and decision builder have now run successfully
against the completed v2 package. The final outcome is also recorded in the
software experiment documentation. For future runs, preserve failed rows and
diagnose the reported failure rather than treating partial rows as accepted.

The builder verifies and snapshots the current physical evidence and links the
earlier compiled-runtime fixture with explicit workload boundaries. Physical
sources, extracted netlist and 11 compiler artifact hashes were independently
checked during this turn. No analog executor, qualified converter/array profile
or matched hardware timing/energy evidence has been established.
