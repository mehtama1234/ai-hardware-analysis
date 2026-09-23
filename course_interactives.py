"""Small, original teaching models used by the course frontend."""


REQUEST_LATENCY_MODEL = {
    "id": "request-latency-model",
    "fixed_before_ms": 7,
    "calculation_ms": 2,
    "fixed_after_ms": 1,
    "calculation_min_ms": 0,
    "calculation_max_ms": 8,
    "stages": [
        ("Wait in the queue", "queue", 4),
        ("Read the input", "read", 3),
        ("Calculate", "calculation", None),
        ("Send the answer", "delivery", 1),
    ],
}


def render_interactive(key, esc):
    if key is None:
        return ""
    if key != "request-latency-model":
        raise ValueError(f"Unknown course interactive: {key}")

    model = REQUEST_LATENCY_MODEL
    rows = []
    for label, stage_id, value in model["stages"]:
        shown = model["calculation_ms"] if value is None else value
        value_id = f'{model["id"]}-{stage_id}-ms'
        rows.append(
            f'<tr><th scope="row">{esc(label)}</th>'
            f'<td><output id="{esc(value_id)}">{shown}</output> ms</td></tr>'
        )

    fixed_floor = model["fixed_before_ms"] + model["fixed_after_ms"]
    initial_total = fixed_floor + model["calculation_ms"]
    return (
        f'<aside class="interactive-model" id="{esc(model["id"])}" '
        f'data-fixed-before-ms="{fixed_floor}" data-fixed-after-ms="0">'
        '<h3>Change one stage; keep the rest fixed</h3>'
        '<p>This is the same invented, sequential request as above. The queue wait, '
        'input read, and answer delivery stay fixed; only calculation time changes. '
        'That isolates one cause of latency. It does not predict the completion rate '
        'of a server handling many requests.</p>'
        f'<label for="{esc(model["id"])}-control">Calculation time: '
        f'<output id="{esc(model["id"])}-control-value">{model["calculation_ms"]}</output> ms</label>'
        f'<input id="{esc(model["id"])}-control" type="range" min="{model["calculation_min_ms"]}" '
        f'max="{model["calculation_max_ms"]}" step="1" value="{model["calculation_ms"]}" '
        f'aria-describedby="{esc(model["id"])}-hint">'
        f'<p id="{esc(model["id"])}-hint" class="model-hint">Use the arrow keys or drag the control. '
        f'Total = 4 ms waiting + 3 ms reading + calculation + 1 ms delivery.</p>'
        f'<div class="table-wrap"><table><caption>Sequential elapsed-time model; each stage is counted once.</caption>'
        f'<thead><tr><th scope="col">Stage</th><th scope="col">Time</th></tr></thead>'
        f'<tbody>{"".join(rows)}<tr class="model-total"><th scope="row">Request elapsed time</th>'
        f'<td><output id="{esc(model["id"])}-total-ms">{initial_total}</output> ms</td></tr></tbody></table></div>'
        f'<p id="{esc(model["id"])}-explanation" aria-live="polite">'
        f'At the starting value, this request takes {initial_total} ms. Even if calculation took zero, '
        f'the other stages would still take {fixed_floor} ms.</p>'
        '</aside>'
    )


INTERACTIVE_SCRIPT = """<script>
(() => {
  document.querySelectorAll('.interactive-model').forEach((model) => {
    const control = model.querySelector('input[type="range"]');
    if (!control) return;
    const value = model.querySelector('#' + CSS.escape(control.id) + '-value');
    const total = model.querySelector('#' + CSS.escape(model.id) + '-total-ms');
    const explanation = model.querySelector('#' + CSS.escape(model.id) + '-explanation');
    const calculation = model.querySelector('#' + CSS.escape(model.id) + '-calculation-ms');
    const fixed = Number(model.dataset.fixedBeforeMs) + Number(model.dataset.fixedAfterMs);
    const update = () => {
      const calculationMs = Number(control.value);
      const elapsedMs = fixed + calculationMs;
      value.value = String(calculationMs);
      calculation.value = String(calculationMs);
      total.value = String(elapsedMs);
      explanation.textContent = `With ${calculationMs} ms of calculation, this request takes ${elapsedMs} ms. ` +
        `If calculation became free, the unchanged stages would still take ${fixed} ms.`;
    };
    control.addEventListener('input', update);
    update();
  });
})();
</script>"""
