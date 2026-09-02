# Rendered Screenshots

Start from the main workbench [Connected System Map](../connected-system-map.html). This screenshot index uses the same object, constraint, design move, evidence, allowed claim, refused claim, and next-handoff contract.

This file lists the rendered screenshots included with the review package.

The screenshots are not chip proof. They prove only that the HTML review experience was rendered and captured for offline review.

## Screenshot Set

| File | View | Page | What It Checks |
|---|---|---|---|
| `screenshots/company-roadmap-desktop.png` | desktop, 1440 pixels wide | main roadmap page | The full roadmap can render as one long executive and engineering page. |
| `screenshots/company-roadmap-mobile.png` | mobile, 390 pixels wide | main roadmap page | The full roadmap can render on a narrow screen without requiring the desktop layout. |
| `screenshots/review-package-index-desktop.png` | desktop, 1440 pixels wide | review package index | The package index can render the manifest, artifact cards, dependency cards, and linked docs. |
| `screenshots/review-package-index-mobile.png` | mobile, 390 pixels wide | review package index | The package index can render on a narrow screen for offline review. |

## Review Use

Use these screenshots when a reviewer needs to scan the rendered experience without running the server.

Use the live HTML when checking interaction, artifact loading, package links, or browser behavior.

Regenerate the screenshots with:

```bash
backend/.venv/bin/python backend/scripts/capture_review_screenshots.py
```

This command expects the static server to be running at `http://127.0.0.1:8080`.

## Visual QA Checklist

When reviewing the screenshots, check these items:

- The first screen states the decision clearly.
- The proof warning is visible near the start.
- The page explains terms before relying on them.
- The blocker board is easy to find.
- The evidence ladder is visible and separates proof levels.
- The modification playbook shows silicon, compiler/runtime, backend, frontend, and proof work.
- The review package index shows the executive answer, artifacts, dependencies, import templates, and linked standalone docs.
- The mobile screenshots do not require the desktop layout to understand the page.
- Text does not visibly overlap other text.
- Large diagrams or cards do not hide the safe claim and blocked claim boundary.

If any item fails, update the page before using the package externally.

## Claim Boundary

The screenshots can support this claim:

```text
The demo review pages were rendered and captured for offline review.
```

The screenshots cannot support these claims:

```text
The chip works.
The board ran.
Power was measured.
Calibration was proven.
The compiler target is complete.
The package proves full VLA readiness.
```
