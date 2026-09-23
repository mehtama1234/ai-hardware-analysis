"""Transfer exercise that asks readers to audit a paper not taught in advance."""

CAPSTONE_ID = "final-paper-challenge"


def render_capstone(escape):
    """Render the final paper-reading challenge using the course HTML escaper."""
    prompts = [
        (
            "1. State the claim",
            "In one sentence, name the problem, the proposed change, and the claimed benefit. Do not write “better” or "
            "“faster” without saying what was measured. Record the exact paper version and the page, section, or figure "
            "where you found it.",
        ),
        (
            "2. Follow the mechanism",
            "What work, data, or decision changes? What must remain correct for the change to help? "
            "Name one assumption the mechanism needs. Connect it to a paper from another conference in this course: "
            "describe the shared idea and one difference that prevents carrying the earlier result over unchanged. "
            "For example, both may save work by retaining a value, but differ in when that value becomes outdated.",
        ),
        (
            "3. Count the whole cost",
            "Choose one complete unit of work whose result can be accepted, such as one request, one model update, or one "
            "simulation that reaches an accepted answer. List the time, movement, storage, energy, setup, "
            "conversion, checking, or recovery costs that matter. Say which costs the paper measures "
            "and which it leaves out. Keep units attached to every number.",
        ),
        (
            "4. Audit one result",
            "Pick one table entry or plotted result. Identify the workload, comparison system, device or "
            "system, quantity being measured, and measurement conditions. Recalculate one simple value or ratio from the "
            "paper. If it is a percentage or rate, state its numerator and denominator. Explain the conclusion supported by "
            "that measurement and identify the conditions it covers. Did both systems process the same inputs and meet "
            "the same answer-quality requirement, with the same costs included? Record any difference. Is the number "
            "one run, an average, or another summary of repeated runs? Record the reported variation; if it is missing, "
            "say that you cannot assess how consistently the difference appears.",
        ),
        (
            "5. Find the boundary",
            "Describe a plausible workload or condition where the method may stop helping or may fail. "
            "Point to evidence in the paper that bears on this boundary, or say clearly that the paper "
            "does not test it.",
        ),
        (
            "6. Write the verdict",
            "Finish with two sentences: the strongest claim the evidence supports, and the next test "
            "you would run before relying on the result in a different setting.",
        ),
    ]
    prompt_html = []
    for index, (title, instruction) in enumerate(prompts, 1):
        field_id = f"paper-challenge-note-{index}"
        prompt_html.append(
            f'<div class="paper-challenge-step"><h3>{escape(title)}</h3>'
            f'<p>{escape(instruction)}</p>'
            f'<label for="{field_id}">Your notes for step {index}</label>'
            f'<textarea id="{field_id}" rows="4" spellcheck="true"></textarea></div>'
        )

    return (
        f'<section class="part paper-challenge" id="{CAPSTONE_ID}" aria-labelledby="paper-challenge-title">'
        '<div class="kicker">Final practice · use a paper you have not studied here</div>'
        '<h2 id="paper-challenge-title">Read a paper on your own, then check your evidence</h2>'
        '<p class="summary">Explain a paper so another reader can follow the proposed change, check one result, '
        'and identify a condition the authors have not established. Label each conclusion as reported by the paper, '
        'calculated from its numbers, or inferred as a next question. Use the six steps below to build that explanation.</p>'
        '<aside class="uses"><h3>Choose your paper</h3>'
        '<p>Pick a paper from one of the conference routes that is <em>not</em> among the guided walkthroughs above. '
        'Use the official conference or author paper as your source. Write down its title, authors, conference, '
        'year, and version before you begin. Prefer a full paper for the six-step audit. If the route provides only '
        'an abstract, use the bounded exercise below instead: state only the problem and proposed change that the '
        'abstract names, record the missing mechanism or evaluation details, and do not claim a measured result. '
        'An abstract alone cannot support the full audit.</p>'
        '<details class="uses abstract-paper-check"><summary>When only an abstract is available</summary>'
        '<p>Write three short notes: (1) what problem the abstract says the paper addresses; (2) what change or '
        'system it says is proposed; and (3) one evaluation fact you cannot establish without the full paper, such '
        'as the workload, comparison, device, metric, or failure case. Label the first two as <strong>abstract-reported</strong>, '
        'not as a complete paper description. Label the third as <strong>unknown</strong>. Do not turn a phrase such '
        'as “improves performance” into a speedup, baseline, or general claim. Use the source boundary to decide '
        'whether to keep looking for the full paper or stop with this limited account.</p></details>'
        '<p>This tests whether you can use the course ideas on a paper you were not taught. It does not mean every '
        'listed conference or paper has been fully reviewed.</p></aside>'
        '<p>Work through the steps in order. Keep the paper open and attach a page, section, table, or figure '
        'reference to each statement about the paper. Label your own arithmetic and your proposed next test so they '
        'cannot be mistaken for an author-reported result. The note boxes stay in this page only; copy your work elsewhere '
        'before leaving if you want to keep it.</p>'
        + ''.join(prompt_html) +
        '<details class="uses paper-challenge-rubric"><summary>Check your work with the 10-point rubric</summary>'
        '<p>Give each of these five checks 0, 1, or 2 points. A 2 means the answer is specific and points to '
        'the paper; a 1 means it is partly right but vague or missing a source; a 0 means it is absent or '
        'unsupported. A high total is not a substitute for a sound paper or a complete review.</p>'
        '<ol>'
        '<li><strong>Claim:</strong> Does your sentence say what changed, for which task, and what benefit is claimed?</li>'
        '<li><strong>Mechanism:</strong> Can a reader follow how the change produces the benefit and name a condition it needs? '
        'Does your connection to another conference paper identify both the shared idea and a relevant difference?</li>'
        '<li><strong>Whole cost:</strong> Are the measured unit, relevant overheads, and omitted costs visible?</li>'
        '<li><strong>Evidence:</strong> Can someone find your result in the paper and reproduce your arithmetic, units, and any percentage denominator? '
        'Have you checked that the compared systems did the same job, and recorded variation across runs or its absence?</li>'
        '<li><strong>Boundary:</strong> Did you name a plausible limit and distinguish a tested limit from an open question?</li>'
        '</ol>'
        '<p>If you scored below 2 on evidence, go back to the paper before strengthening your conclusion. '
        'If your verdict says “always,” “proves,” or “twice as fast” without naming the tested conditions and '
        'measured quantity, narrow it. Your final explanation should separate what the authors report, what '
        'you calculate from their data, and what you infer. If it uses a percentage, name the included cases and '
        'the cases left out.</p>'
        '<h3>Make the connection specific</h3>'
        '<p>Consider the <a href="#paper-lut-tensor-core-2025">LUT Tensor Core lookup-table example (ISCA 2025)</a> '
        'and the <a href="#paper-trrip-2025">TRRIP cache example (MICRO 2025)</a>. Both retain something '
        'so later work can reuse it. A lookup table saves arithmetic when several weight patterns use the same '
        'input values; changed inputs require a new table. A cache saves a fetch when a requested block is still '
        'present and valid. A poor reuse prediction can waste cache space even when the bytes remain correct. '
        'For your chosen paper, name what is retained, what later operation uses it, and what event makes it '
        'unusable or no longer worth keeping. These questions connect the mechanisms; each paper’s measured '
        'benefit still depends on its own workload and costs.</p>'
        '<h3>What a supported explanation looks like</h3>'
        '<p>Use this invented result to check your writing standard. Suppose a paper reports that a request '
        'takes 12 milliseconds before a change and 8 afterward on one device. Both runs meet the same output '
        'quality requirement. Its timing excludes a one-time preparation step that takes 20 milliseconds.</p>'
        '<p><strong>Reported:</strong> “For the tested request and device, execution fell from 12 to 8 milliseconds '
        'at the stated output quality; preparation was timed separately.” A real review would attach the '
        'paper location and identify the request, device, and quality measure. Writing only “the system is '
        'faster” would leave those facts unspecified.</p>'
        '<p><strong>Calculated:</strong> “The measured execution speedup is 12 ÷ 8 = 1.5×, equivalent to one-third '
        'less execution time. Including the 20-millisecond preparation once, one request takes 28 milliseconds. '
        'Five sequential requests take 20 + 5 × 8 = 60 milliseconds, equal to the original 5 × 12 = 60. '
        'Six take 68 milliseconds instead of 72.” This comparison assumes the original path needs no extra '
        'preparation, the new preparation is reusable, and the per-request times remain unchanged.</p>'
        '<p>The invented 12- and 8-millisecond values specify no variation across repeated runs. The arithmetic is '
        'checkable, but it does not tell us whether a real measurement would show the same difference consistently. '
        'Nor would a result from an easier input or a weaker answer-quality rule establish the same improvement. '
        'Record those limits separately: unequal work is a comparison problem; varying run times are a measurement '
        'question. Repeating an unequal comparison does not make the jobs equivalent.</p>'
        '<p><strong>Open question:</strong> “If each new input requires fresh preparation, the saving may disappear; '
        'I would measure how often preparation can be reused.” That is a proposed test under a different '
        'condition, not a failure demonstrated by the invented measurements. Keep the same distinction in '
        'your paper review: identify the measured result, show your arithmetic, and label the next question.</p></details>'
        '<p class="lesson-links"><a href="#paper-walkthroughs">Review the guided paper examples</a> · '
        '<a href="#conference-routes">Choose another conference route</a> · '
        '<a href="#course-checkpoints">Revisit the course checkpoints</a></p></section>'
    )
