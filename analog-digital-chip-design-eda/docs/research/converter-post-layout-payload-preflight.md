# Converter Post-Layout Payload Preflight

This page shows the review step before strict submission.

Submission is allowed to write accepted evidence. Preflight is not. Preflight only reads a candidate payload and reports whether the packet is complete enough to submit.

That distinction matters because a real post-layout result can still be incomplete as evidence. It may have energy but no extracted netlist. It may have a netlist but no model files. It may have good noise but a different sharing rule. Preflight turns those gaps into explicit issues before the evidence ledger is touched.
