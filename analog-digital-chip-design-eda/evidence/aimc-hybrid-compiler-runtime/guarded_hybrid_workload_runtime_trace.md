# Guarded Hybrid Workload Runtime

This trace consumes the shared target command schedule in two modes: simulator-candidate mode and physically guarded mode.

- workloads/models: `12`
- commands: `321`
- simulator analog candidate commands: `46`
- physical guarded digital fallbacks: `46`
- physical converter gate: `blocked_sar_source_common_mode`

## Runtime Decision

Analog commands remain visible for simulator analysis, but every such command is converted to an explicit digital fallback in the physical-guarded trace because the Sky130 converter has not passed its threshold-spacing gate. The wake-word package already selects digital execution from its cost policy.

## Claim Boundary

does not prove measured fallback latency, measured energy, board runtime, physical analog execution, silicon, or production readiness
