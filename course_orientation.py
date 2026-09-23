"""Learning outcomes and an ungraded starting-point check for the course."""

ORIENTATION_ID = "course-orientation"

LEARNING_PATH = [
    {
        "title": "First, follow the work and the data",
        "body": "Begin with one request. Count its working and waiting time, then ask which steps can run together. Follow the numbers it uses, the storage it reads, and the connections its data travels through. Finally, compare doing the work again, reusing an earlier result, and changing the execution plan.",
        "links": [("s1", "Trace a request"), ("dependencies-and-pipelines", "Find required order"), ("s2", "Track number meaning"), ("s3", "Follow data movement"), ("s4", "Find shared connections"), ("s5", "Decide when to skip repeated work"), ("s6", "Compare execution plans")],
    },
    {
        "title": "Next, see what changes when work is shared",
        "body": "A design that works for one task may behave differently when requests compete, machines exchange data, or a chip runs into power and timing limits. Follow the shared resource and the work needed to coordinate it.",
        "links": [("queues-and-batching", "Understand waiting and queues"), ("s7", "Follow communication and recovery"), ("physical-design", "Connect the plan to physical limits")],
    },
    {
        "title": "Finally, check a complete result",
        "body": "Every lesson asks what the task must deliver. Now examine that requirement more closely: is an approximate answer acceptable, what may another user observe, and what must survive a crash? Follow a service request, stored update, training run, or scientific calculation through its final check. Then use the same questions to examine a paper.",
        "links": [("s8", "State and test a promise"), ("s9", "Examine privacy and observation"), ("s10", "Trace an accepted answer"), ("durable-update", "Follow a crash and retry"), ("training-workflow", "Check an accepted model"), ("scientific-workflow", "Check a scientific result")],
    },
]

OUTCOMES = [
    "Trace one request from arrival to accepted answer, separating work from waiting and one-request time from completion rate.",
    "Follow data through computation, memory, and communication; identify which resource can limit the complete task.",
    "Compare designs at the same accepted result, counting setup, movement, checking, accuracy, and failure costs.",
    "Read a reported result with its workload, comparison, units, device, and measurement conditions attached.",
    "Explain what a paper's evidence supports, what it leaves open, and one condition where its method may stop helping.",
]

CHECKS = [
    {
        "id": "orientation-time",
        "question": "A request spends 4 ms waiting, 3 ms reading, 2 ms computing, and 1 ms sending its answer. Assume the stages happen one after another. How long until this answer arrives?",
        "answer": "10 ms. Add all four stages: 4 + 3 + 2 + 1. This is the elapsed time for one request under the stated assumptions; it does not tell you how many requests the server can finish per second.",
        "lesson": "s1",
        "lesson_title": "Review elapsed time and completion rate",
    },
    {
        "id": "orientation-local-speedup",
        "question": "In the same example, computing drops from 2 ms to 1 ms. The other stages stay fixed. What is the new total, and why is it not half as long?",
        "answer": "9 ms: 4 + 3 + 1 + 1. Only one part got faster; the other 8 ms remain. A faster component does not make the whole task faster by the same factor.",
        "lesson": "s1",
        "lesson_title": "Review the complete request path",
    },
    {
        "id": "orientation-data-movement",
        "question": "A processor often has no work to do while it waits for data. Before buying a faster processor, what would you measure?",
        "answer": "Measure how long data takes to arrive, how often the requested data must be fetched, how many requests compete for the same path, and whether valid data can be reused. If transfer or contention is the delay, more compute capacity may sit idle.",
        "lesson": "s3",
        "lesson_title": "Review data access and movement",
    },
    {
        "id": "orientation-tail-delay",
        "question": "A service's average response time improves, but one request in every hundred still arrives after its deadline. Has the delay problem been solved for every user?",
        "answer": "No. The average improved for the measured requests, but one in every hundred still missed its deadline. Record how late those requests were and what made them wait. Also check whether the service's stated target allows that many misses. An average alone cannot answer either question.",
        "lesson": "queues-and-batching",
        "lesson_title": "Review queues and unusually slow requests",
    },
    {
        "id": "orientation-paper-evidence",
        "question": "A paper reports that one operation is faster on one tested device. Does that establish that the full application is faster on other devices?",
        "answer": "No. It supports the operation result under the reported workload, device, comparison, and measurement conditions. The full application may include other costs, and a different device may behave differently. Read the paper's evaluation boundary before extending the claim.",
        "lesson": "paper-walkthroughs",
        "lesson_title": "Compare a claim with the measured result",
    },
]


def render_orientation(escape):
    outcomes = "".join(f"<li>{escape(outcome)}</li>" for outcome in OUTCOMES)
    path = []
    for stage in LEARNING_PATH:
        links = " · ".join(f'<a href="#{escape(target)}">{escape(label)}</a>' for target, label in stage["links"])
        path.append(
            f'<li><h4>{escape(stage["title"])}</h4><p>{escape(stage["body"])}</p><p>{links}</p></li>'
        )
    checks = []
    for check in CHECKS:
        checks.append(
            f'<details class="orientation-check" id="{escape(check["id"])}">'
            f'<summary>{escape(check["question"])}</summary>'
            f'<p>{escape(check["answer"])}</p>'
            f'<p><a href="#{escape(check["lesson"])}">{escape(check["lesson_title"])}</a></p>'
            "</details>"
        )
    return (
        f'<section class="part orientation" id="{ORIENTATION_ID}" aria-labelledby="orientation-title">'
        '<div class="kicker">Start here · no specialist background required</div>'
        '<h2 id="orientation-title">What you will learn, and where to begin</h2>'
        '<p class="summary">You need basic arithmetic and percentages, not prior knowledge of chip design or distributed systems. The worked examples show their calculations and explain technical terms when they first become useful. Their invented numbers teach a relationship; they are not measurements from a paper.</p>'
        '<p>New to the subject? Begin with <a href="#s1">one request from arrival to answer</a> and use the next-lesson links. Reading a particular conference? Use its <a href="#conference-routes">reading route</a>, then follow the lesson links wherever you need an explanation. Looking up a word? Use the <a href="#concept-lookup">concept lookup</a>.</p>'
        '<h3>By the end, you should be able to</h3>'
        f'<ul class="orientation-outcomes">{outcomes}</ul>'
        '<h3>How the lessons fit together</h3>'
        '<p>For each example, first say what counts as a finished answer. Predict what makes it wait, then work through the calculation with its units. Change one assumption: make two steps share a processor, add a data transfer, or require an update to survive a power loss. Explain which part of the answer changes and why. The links below follow the order of the core lessons.</p>'
        f'<ol class="learning-path">{"".join(path)}</ol>'
        '<aside class="uses"><h3>What connects the conferences?</h3>'
        '<p>The conference names tell you where work was published. They do not divide the underlying problems into separate worlds. Consider storing numbers in fewer bits. That can reduce the bytes a program reads, but the machine may have to convert them before calculating. Rounding can also change the answer. To judge the choice, follow all three consequences: data moved, conversion work, and the result the user receives.</p>'
        '<p>In this course, a <strong>concept</strong> is an idea you can use in that explanation, such as rounding error or time spent waiting for data. A <strong>theme</strong> brings papers together around a question, such as when smaller stored numbers make a complete task faster. A <strong>subtheme</strong> narrows that question: how much conversion work can the saving afford, or when does rounding change a decision? These are the course’s reading groups, not official conference categories.</p>'
        '<p>Carry the question between conferences, not the reported speedup. Two papers may both reduce data movement while studying different programs, machines, and acceptable errors. Compare what causes the saving and what extra work it requires. Only compare their numerical results directly when the tasks and measurement conditions justify it.</p></aside>'
        '<aside class="uses"><h3>How to use a conference route</h3>'
        '<p>Start with the route’s evidence notice. It says whether the route is a broad source-backed synthesis or a limited guide built around a small number of papers. Next, read one theme and do its practice question before opening the linked walkthrough. In the walkthrough, separate the paper’s reported observation from the course’s invented calculation. Finally, open the source link and write down the workload, comparison, measured quantity, and condition that limits the claim. If any of those are absent, record the gap rather than filling it with an assumption.</p></aside>'
        '<aside class="uses"><h3>Keep three kinds of statements apart</h3>'
        '<p>In your notes, label a statement <strong>reported</strong> when the paper measured or proved it, <strong>calculated</strong> when you derived it from the paper’s numbers, and <strong>proposed</strong> when it is a test you think should happen next. A reported number needs its paper location. A calculation needs its arithmetic and assumptions. A proposed test needs a reason; it is not evidence that the paper already supplied.</p></aside>'
        '<aside class="uses"><h3>Check your starting point</h3>'
        '<p>Try each question before opening its answer. Write down the calculation or the observation you would need. If your reasoning differs, use the linked lesson to find the assumption responsible. These examples help you choose what to revisit. After the lessons, work through a guided paper and use the final challenge to assess a paper you have not studied here.</p></aside>'
        + "".join(checks)
        + '<p class="concept-links"><a href="#s1">Begin the ordered course</a> · '
        '<a href="#paper-walkthroughs">See guided paper examples</a> · '
        '<a href="#final-paper-challenge">Go to the final paper challenge</a></p></section>'
    )
