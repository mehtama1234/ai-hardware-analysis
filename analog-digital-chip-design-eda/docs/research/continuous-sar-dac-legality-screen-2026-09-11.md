# Continuous SAR DAC legality screen — 2026-09-11

This screen isolates the remaining physical failure after the retained-state
control fix. Each case ran one conversion against the pinned local Sky130
models at a 100 ps diagnostic step. The coarse step is suitable for topology
triage only; it is not the qualification configuration.

| Case | DAC threshold samples (V) | Result |
| --- | --- | --- |
| Retention fix | `[0.043, 1.495, 0.848, -0.450]` | plate leaves legal range |
| Rail switches + clamp | `[0.151, 0.050, -0.308, 1.133]` | still out of range |
| Rail switches + clamp + ground precharge | `[0.141, -0.056, -0.414, 1.027]` | still out of range |
| Isolated plate switch, 8 µm | `[0.342, 0.178, -0.148, 1.294]` | improved, still out of range |
| Isolated plate switch, 64 µm + 5 pF hold | `[0.358, 0.130, -0.204, 1.237]` | improved, still out of range |
| Sequential rail handoff, 100 Ω | `[0.048, 0.060, 0.060, 0.060]` | legal, but clamps every plate high and decodes `15` |
| Phase ends at trial end, no rail handoff | `[0.707, -0.251, -0.223, -0.223]` | timing correction changes charge state, still out of range |
| Fixed retained pattern + 100 Ω handoff | post-trial rows: `[0.007, -0.000, 1.756, 1.794] → [-0.004, 0.003, 1.801, 0.000]` | per-bit handoff follows the known pattern |
| Raw capture at decision edge | state `[0.004, 0.004, 0.004, 0.004]`, raw `[0, 0, 0, 0]` | converges with corrected polarity, DAC still rejected |
| Five-conversion raw late capture | state alternates near rails across history; codes `[15, 15, 15, 15, 15]` | repeated-history capture is unstable and DAC remains illegal |
| One conversion, restore latch disabled | state `[0.004, 0.004, 0.004, 0.004]` | stable low hold, but multi-conversion run became stiff |
| One conversion, damped clocked restore | state `[0.004, 0.004, 0.004, 0.004]` | stable low hold with finite 100 Ω rail paths |
| Five conversions, damped clocked restore | states alternate low/high by history; raw rails alternate `[0,0,0,0]` / `[1.8,1.8,1.8,1.8]` | restore is stable per conversion but comparator capture is not bit-specific |
| Five conversions, 3 ns latch precharge | same alternating state history; codes remain `15` | longer latch reset does not make capture bit-specific |
| One conversion, PMOS bank 16 | `[0.352, 0.359, 0.359, 0.359]` | plate legality improves, but all four inputs remain nearly identical |
| Isolated plates + timed handoff, fixed pattern | post-trial rows preserve mixed rails (`~0/0/1.8/1.8`, then `~0/0/1.8/0`) | weighting is preserved after handoff; sampled DAC still out of range |
| Isolated handoff moved early (3 ns trial) | `[0.062, -0.293, -0.464, -0.460]` | earlier handoff still leaves sampled DAC out of range |
| Isolated handoff + 100 fF capacitive copy | preamp signs `[+,-,-,-]` | input isolation restores some bit specificity; plate legality still open |
| Five-conversion live capacitive copy | preamp magnitudes vary by bit, but sign remains uniform per conversion; codes `[15,15,15,15,15]` | loading is reduced, DAC feedback still lacks bit decisions |
| Fixed pattern + source-follower copy | preamp `[+0.068,-0.007,-0.006,-0.004] V` | weaker bit separation than capacitive copy |
| Capacitive copy + top-plate rail clamp | `[0.385,-0.138,-0.438,-0.330]` | clamp does not repair sampled trajectory |
| Capacitive copy + 100 Ω PMOS source resistance | `[0.377,-0.140,-0.464,-0.368]` | source damping has no material effect |
| Capacitive copy + PMOS bank 2 | `[0.303,-0.173,-0.463,-0.387]` | lower bank preserves MSB level but worsens lower-bit excursions |
| Capacitive copy + PMOS bank 4 | `[0.354,-0.150,-0.463,-0.373]` | middle bank does not close legality |
| Bootstrapped high-side NMOS | `[0.565,-0.032,-0.347,-0.242]` | MSB improves, lower-bit charge transfer remains illegal |
| Bootstrapped path + 128 µm low-side device | no transient | Sky130 model rejects the oversized device; sizing screen is invalid |
| Capacitive copy + 100 fF sense isolation | `[0.384,-0.144,-0.477,-0.382]` | comparator isolation does not restore plate legality or weighting |
| Capacitive copy + 10 pF top dummy | `[0.237,-0.050,-0.247,-0.191]` | attenuation reduces excursions but still violates range and weakens MSB |
| Capacitive copy + top reset | `[0.358,-0.048,-0.413,-0.136]` | reset improves some nodes but does not close range |
| Capacitive copy + top reset + bottom precharge | `[0.372,-0.045,-0.409,-0.133]` | combined charge controls improve excursion slightly, still rejected |
| Capacitive copy + 10 pF top hold | `[0.234,-0.046,-0.239,-0.185]` | common-mode hold attenuates swing but still violates range |
| Acquisition at trial end +0.5 ns | `[-0.294,-0.467,-0.458,-0.456]` | later measurement does not recover top-plate charge |
| Acquisition at trial end +2 ns | `[-0.297,-0.467,-0.457,-0.456]` | no meaningful settling improvement |
| Capacitive copy 1 pF | `[0.385,-0.138,-0.465,-0.366]` | larger copy capacitance removes preamp signal without fixing legality |
| Switched preamp handoff + 100 fF copy | `[0.380,-0.143,-0.468,-0.369]` | promoted handoff does not recover top-plate legality |
| Post-trial acquisition schedule | `[-0.300,-0.465,-0.459,-0.456]` | plate rails settle, but top node collapses and preamp loses signal |

Receipts:

- `evidence/aimc-simulator-adapters/local-retention-ideal1-100ps.json`
- `evidence/aimc-simulator-adapters/local-retention-rail1-100ps.json`
- `evidence/aimc-simulator-adapters/local-retention-precharge1-100ps.json`
- `evidence/aimc-simulator-adapters/local-retention-isolated1-100ps.json`
- `evidence/aimc-simulator-adapters/local-retention-isolated64-100ps.json`
- `evidence/aimc-simulator-adapters/local-retention-handoff1-100ps-v2.json`
- `evidence/aimc-simulator-adapters/local-retention-phasefix1-100ps.json`
- `evidence/aimc-simulator-adapters/local-posttrial-probe1-100ps.json`
- `evidence/aimc-simulator-adapters/local-posttrial-fixed-handoff-probe1-100ps.json`
- `evidence/aimc-simulator-adapters/local-raw-latecapture1-100ps.json`
- `evidence/aimc-simulator-adapters/local-raw-latecapture5-100ps.json`
- `evidence/aimc-simulator-adapters/local-raw-norestore1-100ps.json`
- `evidence/aimc-simulator-adapters/local-damped-restore1-100ps.json`
- `evidence/aimc-simulator-adapters/local-damped-restore5-100ps.json`
- `evidence/aimc-simulator-adapters/local-damped-precharge3-100ps.json`
- `evidence/aimc-simulator-adapters/local-pmosbank16-100ps.json`
- `evidence/aimc-simulator-adapters/local-isolated-handoff-fixed1-100ps.json`
- `evidence/aimc-simulator-adapters/local-isolated-handoff-early-fixed1-100ps.json`
- `evidence/aimc-simulator-adapters/local-capcopy-fixed1-100ps.json`
- `evidence/aimc-simulator-adapters/local-capcopy-live5-100ps.json`
- `evidence/aimc-simulator-adapters/local-sourcecopy-fixed1-100ps.json`
- `evidence/aimc-simulator-adapters/local-capcopy-topclamp-fixed1-100ps.json`
- `evidence/aimc-simulator-adapters/local-pmos-series100-fixed1-100ps.json`
- `evidence/aimc-simulator-adapters/local-pmosbank2-fixed1-100ps.json`
- `evidence/aimc-simulator-adapters/local-pmosbank4-fixed1-100ps.json`
- `evidence/aimc-simulator-adapters/local-bootstrapped-high-fixed1-100ps.json`
- `evidence/aimc-simulator-adapters/local-bootstrapped-nmos128-fixed1-100ps.json`
- `evidence/aimc-simulator-adapters/local-senseisolation-fixed1-100ps.json`
- `evidence/aimc-simulator-adapters/local-capcopy-dummy10p-fixed1-100ps.json`
- `evidence/aimc-simulator-adapters/local-capcopy-topreset-fixed1-100ps.json`
- `evidence/aimc-simulator-adapters/local-capcopy-reset-precharge-fixed1-100ps.json`
- `evidence/aimc-simulator-adapters/local-top-hold10p-fixed1-100ps.json`
- `evidence/aimc-simulator-adapters/local-acq-plus0p5-fixed1-100ps.json`
- `evidence/aimc-simulator-adapters/local-acq-plus2-fixed1-100ps.json`
- `evidence/aimc-simulator-adapters/local-capcopy1p-fixed1-100ps.json`
- `evidence/aimc-simulator-adapters/local-switched-handoff-capcopy-fixed1-100ps.json`
- `evidence/aimc-simulator-adapters/local-postsample-fixed1-100ps.json`

The retained-state probes in the first case are near rails (`0.004, 1.801,
1.802, 0.004 V`), so the state-storage repair is behaving as intended. The
remaining defect is charge transfer and plate biasing during the physical DAC
trial. A 100 Ω sequential rail handoff brings every plate into the legal range,
but its first control mapping clamps all four plates high and returns code 15.
The next topology experiment must gate the handoff per physical trial decision
and preserve charge redistribution before comparator enable. No analog
accuracy, energy, PVT, or silicon claim is authorized by this screen.
The capacitive copy stage changes the preamp differential from a uniform sign
to `[+,-,-,-]` under the fixed pattern, showing that preamp loading was masking
some bit information. It does not yet repair the out-of-range DAC plates.
The new post-trial probe shows why the mapping is hard to diagnose from the
existing cycle samples: immediately after each trial, the measured plate rows
are already near the high rail (`[1.800, 1.800, 1.800, 1.800]` for the first
bit, followed by rows with only the first bit low). These probes are now part
of the receipt schema and should be copied into the next Colab run.

With fixed retained states, the same probe shows the 100 Ω handoff follows the
known per-bit pattern as each bit commits. The live closed-loop run still
captures an all-low state, so the next repair target is the comparator
decision-to-state capture path rather than rail-switch polarity.
Disabling the cross-coupled restore latch gives a stable one-conversion hold,
but the five-conversion variant becomes numerically stiff. The next repair
should replace the latch with an explicitly clocked, damped restore element
and retain the decision-edge probe.

The raw capture source was corrected to the accepted comparator polarity
(`V(outn)-V(outp)`). Static deck inspection verifies the generated expression;
capturing at the decision edge now converges and produces rail-valued state
storage. The one-conversion result remains rejected because the DAC trajectory
is not yet legal or correctly decoded.

The full five-conversion damped-restore receipt completes, but raw decisions
alternate between all-low and all-high rails by conversion and every decoded
code remains `15`. This rules out the cross-coupled latch as the only cause;
the comparator is receiving a non-bit-specific DAC trajectory.
Increasing latch precharge from 1 ns to 3 ns does not change that result, so
the missing behavior is per-bit evaluation timing or comparator-input handoff,
not reset duration alone.

The combined isolated-plate and timed-handoff fixture preserves a mixed
per-bit rail pattern under fixed states. This is the first topology screen that
keeps binary weighting visible after handoff; the remaining failure is the
settling/sample interval used to feed the comparator.
Moving the handoff earlier with a deliberately shortened diagnostic trial does
not recover the sampled DAC values, so the next change must inspect the top
plate redistribution and comparator input isolation as well as timing.

The measured preamp differential is uniform in sign within each conversion
(`+,+,+,+`, then `-,-,-,-`, alternating by history), while the comparator
differential follows that sign. The latch is therefore responding consistently
to a non-bit-specific DAC input. The next repair target is the DAC charge
trajectory and plate handoff; further latch-reset tuning is not justified until
the four preamp inputs acquire the intended per-bit sequence.
