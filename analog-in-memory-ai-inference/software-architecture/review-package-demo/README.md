# Demo Review Package

This folder is a demo evidence package for the analog chip roadmap page.

It is not measured silicon proof. It shows the file shape the product should export after reviewing one workload against one analog chip target.

Each artifact answers five plain questions:

1. What did this step check?
2. What proof level does the result have?
3. What claim can this support?
4. What claim must stay blocked?
5. What should the team build or measure next?

The package should remain useful after a meeting. A reader should be able to open the files and understand what was tested, what was estimated, what was only assumed, and what is still missing.

The generated archive is `demo-analog-roadmap-001-package.zip`. It contains this README, the readable package index, the executive brief, the engineering work queue, the schema, the manifest, all fourteen step artifacts, and the journey JSON used by the roadmap page.

`end-to-end-meaty-goal.md` states the finished product goal in plain language for executives and developers. It defines the desired page, package, diagrams, writing rules, proof rules, and acceptance bar.

`meeting-walkthrough.md` gives a timed guide for presenting the package in an executive, customer, investor, or engineering review.

`research-backlog.md` lists the research passes to run next, the source standards for each claim type, and the roadmap decisions each research pass is allowed to change.

`plain-language-glossary.md` explains chip, compiler, model, board, calibration, and proof terms for readers who do not already know the background.

`audience-export-map.md` explains how executives, customer technical teams, investors, engineering leads, and product owners should read the same evidence without changing the facts or hiding missing proof.

`reuse-modification-map.md` explains what outside toolkits can help with, what must be changed for our chip, and what the company must own itself.

`action-evidence-map.md` explains what every future run or import action should produce, which proof level it can support, and which claims must stay blocked.

`silicon-board-proof-map.md` explains how a chip feature becomes a board-measured product claim only after runtime, calibration, power, temperature, task, and fallback evidence are tied to the same setup.

`execution-roadmap.md` turns the strategy into staged milestones with owners, deliverables, exit criteria, safer claims, and claims that must still stay blocked.

`physical-ai-opportunity-map.md` explains which Physical AI markets are realistic first proof targets, which are risky first claims, and what evidence would be needed.

`static-diagrams.md` provides plain text diagrams for the full product flow, analog/digital split, proof ladder, silicon-to-board path, claim gate, and company-owned product layer.

`rendered-screenshots.md` lists desktop and mobile screenshots of the main roadmap and package index. These screenshots help offline reviewers see the rendered pages without running the server.

Regenerate screenshots with `backend/.venv/bin/python backend/scripts/capture_review_screenshots.py` while the static server is running at `http://127.0.0.1:8080`.

The `import-templates/` folder contains example JSON shapes for the evidence files the product must eventually import from compilers, simulators, boards, lab instruments, calibration runs, weight-update tests, sensor-path tests, and task-accuracy runs.

`completion-audit.md` maps the end-to-end goal to the current package evidence. It says what is present in the demo, what is not proven yet, and what build gates remain.

`source-review-register.md` lists checked outside examples, allowed use, and do-not-claim boundaries. It keeps market context separate from proof that this chip works.

Build it with:

```bash
backend/.venv/bin/python backend/scripts/build_demo_review_package_archive.py
```
