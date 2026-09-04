# Converter Post-Layout Submission Path

This page shows the one-command intake path for a future real converter post-layout or measured-silicon payload.

The command runs strict validation, checks referenced files, reruns break-even, and writes a submission report only when the payload passes.

The important point is simple: a converter result does not become proof because it has a good number in it. It becomes usable only when the number is tied to the physical object that produced it. The payload must name the extracted netlist or measured setup, the model files, the energy, the latency, the noise, the area, the sharing rule, and the earlier break-even decision it wants to replace.

That is why the command writes accepted evidence only after strict validation and rerun both pass.

```bash
python3 scripts/submit_converter_post_layout_payload.py REAL_PAYLOAD.json
```

If the payload is real, this command creates an accepted rerun and a submission report under `evidence/aimc-simulator-adapters/accepted-post-layout/`. If the payload is a placeholder, a template, or a shape-correct record with missing files, it is rejected.
