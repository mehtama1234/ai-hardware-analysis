# Analog Converter Physical Flow Run

This page is the command handoff after the physical-cell gate.

The gate asks whether the named converter cells exist. This runner asks what the extraction flow would do next. If the cells are missing, it stops and records the blocked commands. If the cells are present, the same command list becomes the manual extraction path into the candidate post-layout folder.

This is intentionally strict. It does not create fake `.mag`, `.gds`, extracted SPICE, area records, or accepted evidence. It only turns the next physical action into an executable boundary.
