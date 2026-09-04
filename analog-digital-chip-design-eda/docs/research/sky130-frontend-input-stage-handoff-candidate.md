# Sky130 Frontend Input-Stage Handoff Candidate

This page records the first same-deck handoff candidate between the extracted ultra frontend and an active gain stage.

The frontend is the extracted Sky130 capacitance network. The active stage is a bounded gain macro using the measured local Sky130 input-stage gain. This is a useful circuit handoff because both blocks are in one transient deck, but it is not a transistor input-stage proof.

The purpose is to separate two questions. First, can the extracted frontend produce a signed sense voltage and pass that state to an active stage in one run? Second, can the real Sky130 transistor input pair do that same job without stalling, loading the frontend, adding too much offset/noise, or hurting latch timing? This page answers only the first question.
