"""Small-sample VLSID route; not a complete proceedings interpretation."""

VLSID_ROUTE = {
    "id": "vlsid-2025",
    "title": "VLSID 2025: connect a representation to the device that realizes it",
    "status": "Four-theme route with two full walkthroughs (TimeFloats and the pulse-bit study). One other locally reviewed paper informs the small sample; energy-accounting discrepancies remain unresolved and conference coverage is incomplete.",
    "intro": "A stored bit pattern, a pulse duration, and a circuit connection are different ways of making an intended operation physical. Their failure modes differ. Begin by asking what physical quantity represents the value, what can disturb it, and which later operation interprets it. The small local VLSID sample provides examples of this connection; it does not establish the dominant ideas across the whole conference.",
    "evidence": "The synthesis uses three papers with locally extracted text and detailed written reviews of their evaluations; two of those records now have full learner walkthroughs here. The other 95 records have only abstracts or titles. No independent reproduction was performed. The four themes below draw on that small sample. When a study evaluated only a model, the route does not present its result as a measurement of manufactured hardware.",
    "themes": [
        {
            "title": "1. Follow a physical error into the answer",
            "body": "A number can be stored as bits or represented by how long a signal lasts. The same-sized disturbance need not have the same effect in each representation. First translate the disturbance into a changed value; then check how the next calculation or decision uses that value.",
            "subthemes": [
                ("How much does the stored value change?", "Apply the decoding rule to the disturbed bits or signal duration. Count the numerical change, not just the number of disturbed bits."),
                ("Does that change affect the required result?", "Follow the changed value into the later calculation or decision. An error bound may preserve one decision while leaving another uncertain."),
            ],
            "reading": "The local pulse-bit-error review connects ordinary control-memory faults to simulated quantum outputs. TimeFloats supplies a different time-domain representation discussed in theme 2. The linear duration rule and four-bit values below are teaching models, not either paper's implementation.",
            "worked_example": [
                "Use an invented time encoding: a value x is represented by a duration t = 10 + 2x ns for x between 0 and 4. The decoder subtracts 10 and divides by 2. A duration error of at most 0.4 ns therefore gives a decoded-value error of at most 0.2, provided the same rule applies and no clipping occurs. If a later decision asks whether x is at least 2, a true value of 1.9 can be decoded as 2.1 and change the decision. A bounded local error does not imply an unchanged task output.",
                "Contrast that with an ordinary unsigned four-bit encoding. Starting from 0011, changing the last bit changes 3 to 2, while changing the first changes 3 to 11. Both are one-bit changes but their numerical consequences differ eightfold. Neither example is a model of all errors in a physical circuit. The encoding, disturbance, and downstream decision must all be specified before an error rate becomes informative.",
                "There is a cost to making a duration less sensitive to the same timing error. Change the invented rule to t = 10 + 4x ns, keeping x between 0 and 4. The same 0.4 ns disturbance now changes the decoded value by at most 0.1, but the largest duration grows from 18 ns to 26 ns. In this model, more time separates neighboring values. That improves tolerance to a fixed absolute timing error while increasing the longest signal duration; it does not establish a free improvement in speed or energy.",
                "The VLSID pulse-bit-error study examines bits stored in the ordinary electronics that control a quantum processor. Those bits describe pulse amplitudes and phases, meaning the pulse's size and position within its oscillation. A changed stored bit alters the pulse description, which can alter the simulated gate output. The local review records much larger effects for some high-significance fields than for other tested bits. These are faults in classical control data, not interchangeable with an abstract error applied directly to a qubit.",
                "The review limits the detailed evidence to Qiskit simulations using an IBM device model, rather than physical quantum-hardware measurements. That permits a bounded question: under this representation and simulated setup, which bit changes most disturb the output? It does not establish the frequency of those faults in manufactured control memory or the same sensitivity on every device. Counting possible errors, measuring their consequences, and estimating how often they occur remain separate tasks.",
                "Some plotted values need a further qualification. Section 3.2 of the pulse-bit preprint says two tested bit positions produced invalid pulses. The authors filled the missing graph values by drawing straight lines between neighboring results; those filled values are estimates, not simulated outcomes for the invalid pulses. They also assume that the system detects these pulses and stops transmission. Section 4.1 relies on that assumption when excluding those bits from correction. A proposed safeguard is therefore part of the reasoning, but its operation is not established by the neighboring simulation results.",
            ],
            "practice": {
                "question": "A decoded value is 2.3 and the time-encoding example's justified absolute error bound is 0.2. Can its true value be below 2? What if the decoded value is 2.1?",
                "answer": "For 2.3, the true value lies between 2.1 and 2.5, so it cannot be below 2 under the stated bound. For 2.1, the interval is 1.9 to 2.3 and crosses the decision threshold; the bound cannot settle the decision. This uses a worst-case bound, not a typical or mean error, and assumes the decoder and range conditions remain valid.",
            },
            "lessons": [("s2", "Representation error"), ("s8", "Fault models"), ("physical-design", "Physical conditions")],
        },
        {
            "title": "2. Count the work around near-memory arithmetic",
            "body": "Calculating where values are stored can avoid sending them to a separate processor. But inputs may need conversion, outputs must be readable by the next stage, and training changes stored parameters. Follow that whole path before comparing energy.",
            "subthemes": [
                ("What work remains besides multiplication?", "Count loading, scale alignment, conversion, updates, and output handling. Explain which work is done once and which repeats for each input."),
                ("Do the energy and error accounts cover the same operation?", "Check component totals, units, device assumptions, and output quality. Keep unresolved accounting differences visible."),
            ],
            "reading": "TimeFloats connects stored weights to time-domain arithmetic, alignment, conversion, and updates. Its focused walkthrough records an unresolved energy-accounting discrepancy. The nJ costs below are invented and do not repair or validate the paper's reported pJ totals.",
            "worked_example": [
                "Consider invented energy costs for repeatedly using one fixed set of stored parameters. A reference path uses 6 nJ per input vector, including movement and calculation. A proposed near-data path uses 0.5 nJ for input conversion, 1 nJ for calculation, and 0.5 nJ for output conversion: 2 nJ per vector. Loading its parameters costs 30 nJ once. After n vectors, the comparison is 6n versus 30 + 2n nJ. Seven vectors lose at 42 versus 44; eight win at 48 versus 46. The benefit depends on reuse, not only on the central operation.",
                "Now suppose the parameters change after every vector and each change costs the same 30 nJ. The proposed path needs 32 nJ per vector and loses to the 6-nJ reference. Real update costs need not equal initial loading, but omitting them would conceal the question. Reusing old parameters when the algorithm requires new ones is not a valid way to recover the saving. Keep parameter version and permitted update timing attached to the energy comparison.",
                "TimeFloats computes sums of input-weight products using signal durations and memory circuitry. Floating-point values have a magnitude part and an exponent that sets its scale. Products with different scales cannot simply be added as though their magnitude parts used the same units. The paper's five-step path includes combining exponents, finding a shared scale, adjusting inputs, computing products and their sum, and converting the result back to a digital floating-point value. A cheap multiplication leaves these supporting steps to be counted.",
                "Conversion also affects the answer. The source describes modeled device variation when converting bits to timing signals and converting results back to bits. It evaluates a specified statistical perturbation model; the result is not a guarantee over every manufactured circuit. Under the tested model, exponent computations are more sensitive than magnitude computations. That supports examining where to spend limited correction resources, not treating every physical error as having the same consequence.",
                "The energy account needs caution too. Section IV-B lists component costs of 1.28, 3.25, 0.023, 1.32, and 2.421 pJ, which sum to 8.294 pJ, while stating a total of 5.8 pJ. The focused walkthrough also records different entries in Table I. These differences remain unresolved. Do not silently choose a preferred total or use the headline efficiency to predict full training energy. The implementation evidence is synthesis and circuit simulation, not a measured fabricated chip.",
            ],
            "practice": {
                "question": "If output conversion instead costs 1.5 nJ per vector, with all other invented costs unchanged and one initial load, how many vectors are needed for a strict energy win?",
                "answer": "The recurring cost becomes 0.5 + 1 + 1.5 = 3 nJ. Require 30 + 3n < 6n, so n > 10: ten vectors tie and eleven are the first strict win. Additional idle energy, loading time, quality differences, or supporting components could change the full-system decision and are not included in this toy account.",
            },
            "lessons": [("s3", "Placement and movement"), ("s6", "Conversion costs"), ("physical-design", "Energy and evidence")],
        },
        {
            "title": "3. Choose the device that can finish the required job",
            "body": "Starting sooner is not the same as finishing sooner. A device may need extra operations to move values between its connected units, or may produce a less accurate answer. Count waiting, preparation, execution, and checking before choosing where to run.",
            "subthemes": [
                ("After translation and mapping", "Evaluate the program after it is adapted to the target's supported operations and connections. The source-level operation count may omit work introduced by that mapping."),
                ("Queue, noise, and acceptance", "Compare arrival-to-accepted-result time under the task's quality condition. A quicker start does not guarantee an earlier usable result."),
            ],
            "reading": "QuaLITi connects circuit structure and device noise to simulated model accuracy, and separately studies real-device queues. Its estimated full inference waiting times are not measured complete inference runs. The A/B timings and uncertainty intervals below are invented examples.",
            "worked_example": [
                "In a generic invented device-selection problem, A has a 2-ms queue, 3-ms transfer and translation preparation, 8-ms execution, and 1-ms acceptance check. B has a 5-ms queue, 1-ms preparation, 4-ms execution, and 1-ms check. With sequential stages and both results accepted, A takes 14 ms and B 11. Choosing the shortest queue selects the later answer. This is not a quantum-device benchmark; it isolates the difference between starting sooner and finishing sooner after target-specific work.",
                "Suppose instead that total-time predictions are A = 12 ms with a justified uncertainty range of ±3 ms, and B = 13 ms with ±0.5 ms. Their possible intervals, 9–15 and 12.5–13.5, overlap. The smaller central prediction does not guarantee an earlier result. B has the smaller worst-case bound in this example; A has the smaller prediction. Which criterion matters depends on the requested promise and on whether those bounds actually apply to the current job.",
                "QuaLITi considers quantum circuits running on devices with different available connections and error characteristics. If an operation needs two quantum states that are not suitably connected, adapting the circuit can introduce extra operations to move those states. A source-level count omits that work. The paper therefore examines the circuit after translation for each target, alongside operation errors and errors in reading out the result. Choosing a device changes the implementation being evaluated, not just its place in a queue.",
                "The evidence comes from different stages. The training and inference experiments use three noisy Qiskit simulators built from device-calibration data, with selected eight-qubit connection patterns. Separately, the paper observes queues on real IBM devices and submits a small dummy circuit to measure waiting. It then estimates inference waiting time by applying that measured wait to every data point. That calculation assumes future requests experience the same wait; it is not a measurement of the full model serving every input on those devices.",
                "An original example shows the estimate's sensitivity. Multiplying a 2-second observed wait by ten separately queued requests predicts 20 seconds of waiting. If the first five instead wait 2 seconds each and the next five wait 8 seconds each, total waiting is 50 seconds. If requests are batched, they may not even incur ten separate waits. Queue observations can inform a decision, but the arrival pattern, submission method, and changing queue must match the model used to turn them into a completion-time claim.",
            ],
            "practice": {
                "question": "A new measurement reduces A's justified interval to 10–11 ms, while B remains 12.5–13.5 ms. What ranking follows? What could invalidate that inference before execution?",
                "answer": "Every time in A's interval is less than every time in B's, so A is faster under those stated bounds. A queue that changes after measurement, a different mapped program, or changed operating conditions can make the bounds inapplicable. This inference concerns time only; the accepted-result requirement must still hold for both devices.",
            },
            "lessons": [("s4", "Connections"), ("queues-and-batching", "Waiting"), ("s10", "Worker selection")],
        },
        {
            "title": "4. Label how each result was obtained",
            "body": "A simulation answers a question about a model. A measurement records what happened in a particular test. They answer different evidence questions; combining them does not make the whole result measured. Name the evidence for each part, the conditions it covers, and any unresolved discrepancy.",
            "subthemes": [
                ("What is modeled", "Name the process, timing, variation, error, and surrounding-system assumptions. Identify which conclusion depends on each assumption."),
                ("What is measured", "State which components were physically present and tested. Keep mixed measured and estimated quantities labeled within the same result."),
            ],
            "reading": "The three-record evaluation review separates pulse-bit simulations, TimeFloats circuit modeling, and QuaLITi's mixed simulation/queue evidence. The table summarizes those limits, not a new experiment. The additive error bounds below are original teaching assumptions.",
            "worked_table": {
                "caption": "What the three reviewed records support—and what they do not establish.",
                "headings": ["Study", "What was checked", "What remains open"],
                "rows": [
                    ["Pulse-bit errors", "Control-bit changes in a quantum simulator", "How often real faults occur; effects on other devices"],
                    ["TimeFloats", "Circuit design and variation models", "No chip tested; energy totals disagree"],
                    ["QuaLITi", "Model simulations and separate device wait tests", "Full waiting time estimated, not timed"],
                ],
            },
            "table_after_paragraph": 2,
            "worked_example": [
                "Take a deliberately linear teaching model: the final numerical error equals the sum of encoding error, calculation error, and readout error. Suppose justified absolute bounds are 0.2, 0.15, and 0.1. The largest permitted absolute total is at most 0.45, because the errors can have the same sign. That bound does not meet a required limit of 0.3. It also does not prove every run fails: errors can be smaller or cancel. The model cannot certify the requirement from these bounds alone.",
                "Do not silently replace worst-case bounds with an average-case combination. Any statistical claim needs assumptions about distributions and dependence. Nor does measuring the encoding stage convert modeled calculation and readout terms into measurements. A mixed result should identify its measured and modeled parts, their operating conditions, and why their combination is justified. If the final computation is nonlinear, even this simple additive account may not apply.",
                "The three reviewed records need different next checks. For the pulse-bit study, the simulated sensitivity does not supply a physical rate of memory faults. For TimeFloats, the inconsistent energy entries need reconciliation before the reported total can support a reliable energy comparison. For QuaLITi, measuring a representative full inference workload would test the assumption that a dummy circuit's wait can be applied to every data point. These are missing pieces of evidence, not experiments this course has performed.",
                "Keep a paper-reported number separate from a number whose accounting you have checked. Adding the TimeFloats prose components verifies what those listed values sum to; it does not determine which conflicting entry is correct. Similarly, observing a queue verifies that observation, not a future wait. A careful writeup can explain a mechanism and its limits while leaving the unresolved claim unresolved.",
                "A missing result also needs a reason. A run that stops because its input is invalid differs from a run that finishes with a wrong answer. Connecting nearby points in a graph does not tell us which would happen on the real device. For the pulse-bit study, the next check would exercise the assumed stop mechanism: does it recognize the invalid pulse, prevent transmission, and report the interruption? Then record whether the requested computation is retried or left unfinished. This is a proposed test, not evidence supplied by the graph.",
            ],
            "practice": {
                "question": "The calculation bound improves from 0.15 to 0.05 and the readout bound from 0.1 to 0.04. Is the same 0.3 requirement certified by the linear model? Does this establish the behavior of a manufactured chip?",
                "answer": "The combined bound becomes 0.2 + 0.05 + 0.04 = 0.29, so the requirement follows within this model if each bound is valid jointly for the operating conditions. It does not independently establish real-chip behavior: the implementation must match the model, and omitted effects or invalid component bounds can defeat the conclusion. Keep the model-level result and physical evidence separate.",
            },
            "lessons": [("physical-design", "Evidence stages"), ("s8", "Scope of validation")],
        },
    ],
    "exercise": "In a deliberately simple unsigned four-bit encoding, 0011 represents 3. Flipping the last bit produces 0010, or 2: an error of 1. Flipping the first bit produces 1011, or 11: an error of 8. Both are one-bit faults. Explain why reporting only a bit-flip count misses value sensitivity, and why even value error is insufficient without knowing how the next operation uses the number. This example concerns ordinary binary encoding, not a numerical result from the VLSID papers.",
    "sources": [
        ("https://arxiv.org/html/2405.05511v1", "Pulse-bit study — preprint sections 3.2 and 4.1: invalid pulses, estimated plot values, and assumed stopping behavior"),
        ("https://arxiv.org/html/2409.00495v1", "Hashem and colleagues, TimeFloats — inspected preprint; sections III–IV support the focused walkthrough"),
        ("https://doi.org/10.1109/VLSID64188.2025.00101", "VLSID 2025 publication record — conference identity; final text not compared here"),
        ("analysis/vlsid-2025-first-principles-synthesis.md", "VLSID three-record bounded synthesis and unresolved coverage"),
        ("analysis/vlsid-2025-full-evaluation-adjudication-001-003.md", "VLSID evaluation review — pulse-bit sensitivity and device-evidence limits"),
    ],
}
