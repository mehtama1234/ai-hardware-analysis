# DarwinGame: Playing Tournaments for Tuning Applications in Noisy Cloud Environments

**Venue:** ASPLOS · **Subtheme:** Performance Scheduling & Autotuning

## What It Does

DarwinGame is a tournament-based tuner that bypasses the inability to control cloud interference by co-locating multiple copies of the same application with different tuning configurations on the same VM, exposing all competing configurations to identical interference conditions simultaneously. Tournaments are structured across four phases: (1) Regional phase (Swiss-style): the search space is divided into 10,000 regions; configurations within each region compete in parallel with early termination when a clear winner emerges based on work-done execution score; (2) Global phase (double-elimination style): regional winners compete with losers given a second chance, with both execution score and consistency score (average 1/rank across games) used for judging; (3) Playoffs (barrage style): top survivors compete two-at-a-time without early termination; (4) Final: two finalists compete to produce the winning configuration. This multi-phase design identifies configurations with both low execution time and low performance variability under interference.

Co-locating multiple application copies with different tuning configurations in the same VM game to expose all candidates to identical interference, then using a multi-phase tournament structure (Swiss + double-elimination + barrage) to rank configurations robustly under noisy cloud conditions.

## The Key Result

- **Speedup:** >27% reduction in execution time vs. OpenTuner/BLISS/ActiveHarmony in cloud environments
- **Accuracy:** 4.2% above optimal on average (vs. 40%+ for next best tuner BLISS)
- **Other:** <0.5% performance variability; >15% improvement when integrated with existing tuners

## Why This Approach

Introduction of interference-aware cloud performance tuning as a new research area and first solution (DarwinGame).. Tournament-based design with Swiss, double-elimination, and barrage phases that systematically identify configurations with low execution time and low interference sensitivity.. Integration mechanism allowing DarwinGame to enhance existing tuners (OpenTuner, BLISS) as a subspace search oracle.. Evaluation on AWS (m5.8xlarge, 32 vCPUs) with Redis, GROMACS, FFmpeg, LAMMPS: >27% execution time reduction over existing tuners, <0.5% performance variability, >15% improvement when integrated with existing tuners.

This work addresses the fundamental problem: Existing application performance tuners (OpenTuner, ActiveHarmony, BLISS) implicitly assume a dedicated interference-free execution environment; when used as-is in shared cloud environments with unpre...

## What It Leaves Open

- DarwinGame targets static tunable parameters only and does not provide provable theoretical bounds on convergence due to the unpredictable nature of cloud interference; co-location within a VM introduces additional noise that can affect smaller configurations.
