# Course frontend check — 2026-09-21

The previous command-line Chromium screenshots at deep links were blank. The same
compiler deep link renders under Python Playwright: at 390px width its section begins
at approximately 90px from the viewport top, beneath navigation, with no document-wide
horizontal overflow. The blank captures do not reproduce in this check. Their exact
cause is not established.

## Repeatable checks

### CorrectBench scenario definition — 2026-09-22

Added a plain-language definition of a test scenario before introducing the
validator’s thresholds. The source-backed disagreement and acceptance limits
remain explicit. Build, structural, learning, and editorial checks passed.
The mobile opening capture `/tmp/course-correctbench-review/correctbench-390.png`
was inspected and readable without overflow.

### GSIM correctness boundary — 2026-09-22

Added the paper’s selected-design correctness result beside its simulator
speed results, with an explicit boundary around tested designs and workloads.
The paragraph remains clear that simulator speed is not chip performance.
Build, structural, learning, and editorial checks passed. The mobile capture
`/tmp/course-gsim-review/gsim-390.png` was inspected and readable without
overflow; the focused desktop capture was not completed.

### ISSCC ConvFormer digest review — 2026-09-22

Checked the three-page ConvFormer digest and added an editorial check that
preserves its source type, fabricated-chip boundary, comparison assumptions,
and separate quality obligation. Existing route prose already explained the
terms and limits clearly, so no reader-facing wording change was required.
Editorial and whitespace checks passed.

### FCCM bank mapping source review — 2026-09-22

Checked the Banked Memories manuscript’s sections III–VI. The walkthrough
keeps the four-bank remainder arithmetic as an invented teaching model and
separates it from the paper’s 16-bank address mapping, arbitration, and
latency path. Existing editorial checks passed; no reader-facing change was
needed and no new conference-coverage claim was made.

### NSDI source-status notice — 2026-09-22

Updated the NSDI route notice to distinguish its two final-PDF walkthroughs
from the broader abstract-based synthesis. Build, structural, learning, and
editorial checks passed. Focused screenshots at 390px and 1280px were
inspected; the notice and route introduction were readable with no overflow.

### Di-PS evidence denominator review — 2026-09-22

Checked the final NSDI 2026 PDF and verified the walkthrough’s distinction
between controlled speedup baselines and the production overhead statements.
The editorial check now preserves the separate denominator warning, the
pseudo-gradient filtering boundary, and the fact that results are reported
by the authors. Editorial checks and whitespace checks passed. No layout
change was required in this pass.

### FastServe terminology and metric boundary — 2026-09-22

Reviewed the final NSDI 2026 PDF text around sections 2, 4.1–4.2, and 6.1–6.2.
Added plain-language definitions of prefill, decoding, and the key–value
cache, and made the P95 tail-latency measure explicit. The paper’s reported
hardware, models, workloads, and comparison boundary remain unchanged. Build,
structural, learning, and editorial checks passed. Focused walkthrough captures
at 390px/1280px had no horizontal overflow; this was not a full browser
regression.

### Full Chromium regression after capstone update — 2026-09-22

The complete browser runner passed at 390px and 1280px: 175 anchors, keyboard
entry, exercises, theme practices, 26 walkthroughs, 52 source pages and
return menus, and overflow checks. Screenshots: `/tmp/conference-course-browser-i6332vcs/`.
The browser checker now selects the capstone rubric by its class because the
capstone contains a separate abstract-only details panel.

### Abstract-only paper exercise — 2026-09-22

Added a bounded path for learners using an abstract-only record. The panel
requires problem, proposed change, and one unknown evaluation fact, and warns
against inventing a speedup or baseline. The browser checker now selects the
rubric by class because the capstone has two details panels. Build, structural,
learning, and editorial checks passed; focused Chromium checks passed at both
widths. The expanded mobile panel was inspected and readable. No full browser
regression was run for this change.

### OSDI evidence boundary notice — 2026-09-22

Updated the route notice to distinguish the four focused primary-source
walkthroughs from the rest of the 53-paper corpus. Build, structural,
learning, and editorial checks passed. Focused Chromium screenshots at 390px
and 1280px found no horizontal overflow; this was not a full browser
regression. The change clarifies review scope and adds no paper claims.

### Connecting concepts, themes, and conferences — 2026-09-22

Added an orientation panel explaining the course's reading groups through
data movement, conversion work, and rounding. Build, structural, learning,
and editorial checks passed. Focused Chromium orientation/capstone checks
passed at both widths; artifacts: `/tmp/conference-course-browser-a8avy9nl/`.
Panel captures: `/tmp/course-conference-connection-tgzzrizw/`. The tall mobile
element capture includes the fixed navigation over its content; three
additional viewport captures place each paragraph below navigation and show
the text readable through ordinary scrolling. Those three views and the
desktop panel were inspected. No full browser regression was run in this pass.

### QServe number roles and channel definition — 2026-09-22

Added definitions before the format name and explained the grouping that
shares a channel scale. Updated wording checks to retain the two-step
conversion, weight/activation definitions, safe range, and separate key
adjustment. Build, structural, editorial, and learning checks passed.
Focused Chromium checks at 390px/1280px found no document overflow. All four
paragraph images in `/tmp/course-qserve-terms-7hsm16s1/` were inspected and
readable. This is not a new full browser regression.

### Plain-language conference evidence notices — 2026-09-22

Reworded ISCA, HPCA, MICRO, and VLSID notices and coverage labels without
changing their counts or source limits. Build, learning, structural, and
editorial checks passed. Focused Chromium checks at 390px/1280px verified all
four revised notices and coverage labels, with no document overflow. All
four HPCA sample images in `/tmp/course-evidence-language-9zc40ws6/` were
inspected and readable, including the mobile coverage-card form. The other
three notices were checked programmatically, not visually sampled in this run.

### MapReduce storage and coordinator failure — 2026-09-22

Revised two paragraphs against sections 3.3 and 3.6 of the OSDI 2004 paper.
The course states which completed work is rerun, why storage location matters,
and the coordinator-failure limit of that implementation. Build and structural
checks passed; learning and editorial checks passed after replacing the old
generic commit-wording assertion with the revised text and failure boundaries.
Focused Chromium checks at 390px/1280px found no document overflow. All four
paragraph screenshots in `/tmp/course-mapreduce-boundary-_3q0lcc8/` were
inspected and readable. This does not replace a full browser regression.

### FCCM clock-rate conversion — 2026-09-22

Made the cycle-count comparison explicit: 200 MHz gives 5 ns per cycle;
eight cycles take 40 ns. The slower-clock design and 150 MHz tie use the
same conversion. Added exact-rational checks without changing the example's
results. Build, learning, structural, and editorial checks passed. Focused
Chromium checks at 390px and 1280px found no document overflow. All four
paragraph screenshots in `/tmp/course-fccm-clock-units-xvdzts20/` were
visually inspected and readable. This is not a full browser regression.

### QServe reconstruction range — 2026-09-22

Read the final conference paper's relevant quantization and execution
passages on PDF pages 4–7. Added its 120-to-128 overflow example and direct
page-5/page-7 citations. Recalculated `(15 − 7) × 16 = 128`; this does not
reproduce the system or prove model accuracy. Build, learning, structural
(1,357 links), and editorial checks passed. Focused Chromium checks at
390px and 1280px verified the paragraph, citation targets, and no horizontal
document overflow. Both screenshots in `/tmp/course-qserve-overflow-mtg3gn9t/`
were visually inspected and readable. This is not a new full browser run.

### Walkthrough paragraph structure — 2026-09-22

Split six dense passages across QServe, BlitzScale, Banked Memories, EMT,
Pimba, and FlashInfer at seven subject boundaries. Verified exact preservation
of their wording and order using parsed source strings. Build, learning,
structural, and editorial checks passed. Focused Chromium checks verified all
seven new paragraph starts at 390px and 1280px with no document overflow.
Four QServe/BlitzScale viewport screenshots in
`/tmp/course-paragraph-flow-f_93gx6i/` were inspected; the new paragraph gaps
are clear and the sampled text is readable. The probe intentionally scrolls
to the paragraph, so preceding headings may lie above the viewport. This
sample is not a full visual review of all six walkthroughs.

### SC measurement subtheme notes — 2026-09-22

Replaced generic application instructions with explicit timing examples in
both measurement subthemes. Updated their failure explanations and linked
their evidence blocks to the already reviewed MT4G and CGSim primary
sections. Build, learning, structural, and editorial checks passed. Focused
Chromium checks at 390px and 1280px verified both rendered notes, their exact
source targets, and no horizontal document overflow. All four note images in
`/tmp/course-sc-subthemes-ge8hkcxp/` were inspected and readable. This is a
two-subtheme check, not a complete review of all subthemes or browser behavior.

### Training redistribution and sample weights — 2026-09-22

Added an original numerical example connecting work assignment to the
combination rule. Exact-fraction tests compare the mean of four worker means
with the mean of twelve equally weighted examples. Build, learning,
structural, and editorial checks passed. Focused Chromium checks at 390px
and 1280px found the paragraph without document-width overflow. Both images
in `/tmp/course-training-weights-coyw2ild/` were inspected and readable;
after inspection, replaced the unnecessary phrase “scalar values” with
“numbers.” This is not a paper result or a full browser regression.

### Final exercise: equivalent work and run variation — 2026-09-22

Strengthened step four and its rubric to check both comparison equivalence
and reported variation. Added a worked explanation of why correct arithmetic
does not settle either issue. Structural assertions retain the new prompts.
Build, learning, structural, and editorial checks passed. Focused Chromium
checks at 390px and 1280px verified note entry, keyboard opening of the rubric,
and no horizontal document overflow. All four screenshots in
`/tmp/course-capstone-comparison-05rhhhdu/` were inspected and readable.
This is a focused check, not a new full browser regression.

### O(1) means a bound in a named size — 2026-09-22

Corrected the glossary definition and clarified the BlitzScale explanation.
An original 30/60 GB example varies model count separately from worker count;
the arithmetic check does not test the paper's implementation. Build,
learning, structural, and editorial checks passed. Focused Chromium checks
at 390px and 1280px found no document-width overflow. All four screenshots
in `/tmp/course-growth-bound-bym2m4zx/` were inspected and readable. The full
browser regressions predate these prose changes.

### Concrete concept-lookup definitions — 2026-09-22

Revised bottleneck, checkpoint, and quorum entries; these definitions also
appear beside their linked lessons. Checked the three-of-five overlap by
enumerating every pair of groups. Build, arithmetic, structural, and editorial
checks passed. The editorial check's old `failure assumptions` phrase was
replaced with checks for the new surviving-state wording and explicit
non-majority boundary. Focused Chromium checks at 390px and 1280px exercised
each glossary entry's keyboard link and checked document width. All six
entry screenshots in `/tmp/course-glossary-review-8p7iwqzs/` were visually
inspected and readable. The full two-engine regression predates this prose
change; this focused check does not replace it.

### Second browser engine — 2026-09-22

The regression runner now accepts `--browser webkit` as well as the default
Chromium. `--executable-path` permits a local launcher; the existing
`--chromium` invocation remains supported. Neither engine changes the test
set. Conflicting executable options are rejected.

The existing WebKit 2248 bundle did not match the installed Playwright
version. Downloaded its matching WebKit 2359 (26.6) and extracted missing
Ubuntu libraries into `/tmp/course-webkit-libs.yU8CBU/root`, without system
package installation. The bundled launcher overwrites `LD_LIBRARY_PATH`, so
`/tmp/course-webkit-libs.yU8CBU/run-webkit.sh` supplies the bundled paths and
temporary libraries directly to MiniBrowser. It does not alter browser code.
Run this environment-specific check with:

```sh
python3 -u scripts/check_course_browser.py --browser webkit --executable-path /tmp/course-webkit-libs.yU8CBU/run-webkit.sh
```

Chromium compatibility was rechecked with `--changed-sections-only` at 390px
and 1280px: all seven targeted anchors, keyboard answers, note entry, rubric,
and overflow checks passed. Artifacts: `/tmp/conference-course-browser-s6up43wy/`.
This focused run does not replace the earlier full Chromium regression.

WebKit's complete 390px checks passed: 175 anchor positions, keyboard entry,
contents, exercises, and 52 source pages with return menus. The process then
ended with exit 143 before completing 1280px; no test assertion failure was
reported. Preserve the partial evidence in
`/tmp/conference-course-browser-ah1j8m0j/`. The narrow latency control, VLSID
evidence table, and source return-menu images were inspected and readable.
Added `--widths 1280` to resume the same full checks at the unfinished width;
the default still tests both widths. A partial run is not a desktop pass.

The resumed full 1280px run completed successfully, covering the same 175
anchors, exercises, keyboard interactions, and 52 source pages/return menus.
Artifacts: `/tmp/conference-course-browser-ejuu9br6/`. The desktop latency
control and source return-menu screenshots were inspected and readable.
Together, the completed 390px pass and resumed 1280px pass establish the full
automated WebKit scope at both widths for this course snapshot. They are not
a test on Safari hardware, a complete visual inspection, or source validation.
CLI checks also confirmed rejection of conflicting executable options and
unsupported widths. Structural checks and `git diff --check` passed.

### Representation cost as connection speed changes — 2026-09-22

Expanded the cross-conference representation comparison with fixed 120/60 MB
stored forms and 7 ms decoding/copying cost. Exact-fraction checks validate
the three connection rates and the break-even rate. Build, learning,
structural, and editorial checks passed. Focused browser checks at 390px and
1280px verified the example, keyboard opening of its answer, and no horizontal
document overflow. All four example/answer images in
`/tmp/course-compression-rate-fe6pxzrj/` were visually inspected and readable.
This does not replace a full browser regression or establish paper results.

### MT4G unavailable versus incorrect results — 2026-09-22

Checked the paper's section V and revised the SC measurement discussion to
separate blocked hardware access, missing reference measurements, and a
reported incorrect cache-sharing indication. Verified the new primary-source
anchor. Build, arithmetic, structural (1,355 links), and editorial checks
passed. Focused Playwright checks at 390px and 1280px confirmed both new
paragraphs and their citation, with no document-wide horizontal overflow.
All four paragraph screenshots in `/tmp/course-mt4g-source-adoqogoe/` were
visually inspected and readable. This is not an independent MT4G run or a
new full-course browser regression.

### CGSim calibration source review — 2026-09-22

Revised the SC measurement lesson against section 4.2 of the CGSim author
manuscript: historical jobs and per-site speed tuning are reported; a separate
held-out job set is not described there. The course distinguishes that
reporting limit from proof that no such test occurred. Added the direct
section link and verified its HTML anchor exists. Build, arithmetic,
structural (1,354 links), and editorial checks passed. Focused browser checks
at 390px and 1280px found the new text and citation with no document-width
overflow. All four paragraph screenshots in
`/tmp/course-cgsim-source-tphwgaxs/` were inspected and readable. This does not
replace the full browser regression or broaden the paper's experimental claims.

### SC worker averages and whole-job completion — 2026-09-22

Added two paragraphs and an exercise extension explaining why individual
worker averages do not determine the time to finish a job that waits for both.
Exact-fraction tests check all three paired-delay models. Build, arithmetic,
structural, and editorial checks passed. The focused browser probe initially
used incorrect containers for the theme paragraphs and exercise; inspecting
the generated HTML resolved the selectors. The corrected probe passed at
390px and 1280px, including keyboard opening of the answer and document-width
checks. All four paragraph screenshots in
`/tmp/course-sc-paired-workers-lqyzzbsv/` were visually inspected and readable.
This is not a new full browser regression or a paper-result validation.

### SC source-count correction — 2026-09-22

Reconciled the 433-record inventory with `scripts/check_sc_course_coverage.py`:
119 local texts, 312 abstract-only records, and two title-only records. The
three failed PDF acquisitions belong to the abstract-only group. Updated the
route notice, coverage summary, and synthesis without claiming additional
paper reviews. The route explains what an abstract cannot establish.

Rebuilt the course; structural, learning-arithmetic, and editorial checks
passed. After the final wording edit, reran the inventory and structural
checks. Focused Playwright checks at 390px and 1280px confirmed the revised
paragraph, with no document-wide horizontal overflow. Both paragraph
screenshots in `/tmp/course-sc-inventory-66hpp5bl/` were visually inspected
and readable. This is a focused check, not a new full browser regression.

Completion scope is tracked separately in `COURSE_COMPLETION_AUDIT.md`. It
distinguishes verified structure and current link reachability from unproven
source accuracy and complete visual review. A passing check in this file is
not a completion claim.

External-link reachability, 2026-09-22: `scripts/check_course_external_links.py`
scanned 166 canonical HTTP(S) URLs from `course.html` and 52 generated source
pages. It received responses from 153; 12 DOI/ACM pages returned 403 to the
automated checker; no URL returned 404/410 or another HTTP error. The PETSc
documentation page failed the terminal checker because of a temporary local
DNS error, then opened successfully through the web reader. This records
reachability at one time, not citation accuracy or future availability.

Fresh full browser regression, 2026-09-22: the current generated course passed
at both 390px and 1280px after the navigation and table changes. It covered
homepage entry, contents, 175 anchors, the range control, core and route
exercises, paper walkthroughs, the final challenge, 52 source pages and return
menus, keyboard interactions, and horizontal overflow. Screenshots are in
`/tmp/conference-course-browser-mnn6yff4/`; sampled contents, long-practice,
QServe, and source-page images were readable. The complete screenshot set is
a diagnostic record, not an exhaustive human visual or accessibility audit.

Current full browser regression, 2026-09-22: after the recent source-backed
prose updates, the same complete local suite passed again at 390px and 1280px:
homepage entry, contents, 175 anchors, exercises, 26 walkthroughs, 52 source
pages and return menus, keyboard interactions, and horizontal-overflow checks.
Screenshots are in `/tmp/conference-course-browser-jexb9qf6/`; the narrow
Past-Future walkthrough was manually inspected and readable. This is current
local-browser evidence, not an exhaustive human visual or accessibility audit.

Latest route-evidence-label check: every coverage-table row now has a concrete
route-specific source boundary instead of the generic “see below” message. The
structural check requires a label for each of the 14 routes. Focused Chromium
checks at 390px and 1280px verified all labels, row count, responsive layout,
and no horizontal overflow. Build and learning arithmetic checks pass. This
clarifies the existing evidence audit; it does not add a conference-wide review.

Latest lesson-navigation check: all 16 core lessons now have an explicit
`role="navigation"` region labeled “Lesson navigation.” The structural check
validates each previous/next target. Focused Chromium checks at 390px and
1280px verified all regions and neighbor labels, keyboard activation from the
first lesson to the second and from the final lesson back to its predecessor,
and no horizontal overflow. This is a focused navigation check, not a full
browser regression.

Latest mobile coverage-table visual review: the three-column table technically
fit at 390px but split conference names and body text into unreadable narrow
columns. It now becomes labeled per-conference cards below 560px, while keeping
the normal semantic table at desktop width. The first card CSS accidentally
left the HTML caption at its intrinsic narrow width; a second inspection caught
and corrected it with a full-width block caption. Final responsive checks at
390px and 1280px verify the distinct mobile/desktop display modes, 14 rows,
caption width, and no document overflow. Visual screenshots inspected:
`/tmp/course-coverage-cards-final-333xkyr7/`. Build, learning arithmetic, and
structural checks pass. This targeted visual review does not replace a full
site screenshot review.

Latest coverage-table check: the conference table now presents separate
Teaching coverage and Evidence status columns. It has all 14 conference rows,
and each row preserves the explicit warning that teaching coverage is not a
proceedings-wide paper review. Build, learning arithmetic, and structural
checks pass. Focused Chromium checks at 390px and 1280px verified headers,
row count, table width, and document width. This focused test is not a new
full-browser regression.

Latest PIMBA/QServe terminology check: definitions for row buffer, prefill,
QoQ, eight-bit integer work, and Tensor Cores now occur at their first needed
use. Build, learning arithmetic, and structural checks pass. Focused Chromium
checks at 390px and 1280px confirmed the added definitions and no horizontal
overflow. This is an editorial pass, not a new source review or full browser
regression.

Latest Di-PS and EMT editorial check: Di-PS now makes its quality evidence
specific (four-cluster LLaMA3.2-1B emulation, training loss, and three named
task scores), then separates that from production's uncontrolled account.
EMT's simulator heading now describes the actual evidence boundary. Build,
learning calculations, and structural checks pass. Focused Chromium checks at
390px and 1280px verified the revised text and no horizontal overflow. This is
not a fresh full-browser regression or an independent reproduction of either
paper.

Latest final-challenge check: the paper-audit prompts now require a concrete
measured quantity, percentage numerator/denominator, and labels separating
reported, calculated, and inferred statements. Structural checks enforce the
two new prompt phrases. Focused Chromium checks at 390px and 1280px confirmed
the six note fields, keyboard-operated rubric, and no horizontal overflow.
This focused check does not replace a full browser regression.

Latest cross-conference comparison check: the success lesson now includes a
100-request example, a counted overlap exercise, and the distinction between
predicted probability and observed joint success. Arithmetic checks enumerate
all eleven possible failure overlaps. Build and structural checks pass with
unchanged link/source counts. Focused Chromium checks at 390px and 1280px
verified the new prose, keyboard-opened answer (84%), and absence of horizontal
overflow. The preceding full browser regression was not rerun for this prose
change; this focused test does not establish a new full-site visual review.

Latest opening and responsive-table review: the opening now links all 16 core
lessons in reading order, including shared connections and avoiding repeated
work. The learning check verifies that exact sequence. Structural checks pass
with 1,325 links and 52 source pages.

The full browser regression found the VLSID evidence table extending about
6px beyond its mobile container. Table cells now permit long words to wrap;
the VLSID study-name column has reserved space, and its cells use shorter
summaries while the surrounding paragraphs retain the detailed limits.
An initial process terminated without completion; a subsequent run exposed the
table failure. Neither is counted as a pass. The repaired regression completed
at 390px and 1280px: 175 anchor positions, keyboard exercises, 52 source pages,
and source-return menus passed. Checkpoint, theme, and paper navigation now
uses same-page anchors rather than repeatedly reloading the entire course.
The final column-width and cell-copy refinements also received a focused check
of every table at both widths, plus visual inspection of the revised table.

Inspected opening screenshots: `/tmp/course-opening-review-7ocxdot5/`.
Completed regression screenshots: `/tmp/conference-course-browser-q7myd4py/`.
Inspected final table screenshots: `/tmp/course-table-short-cdwize71/`.
These temporary images record this run, not permanent published assets. Build,
learning calculations, structural checks, and scoped whitespace checks pass.
The browser regression and selected screenshots do not establish that every
paragraph or source claim has completed editorial review.

Latest ICCAD editorial check: revised all four lessons and subtheme labels.
The three-design prediction example now has checked delays 10.1, 9.8, and
9.95 ns, with mean absolute error 0.25 ns; arithmetic checks also verify the
incorrect acceptance of A and rejection of C. Clarified the counter's stored
state versus the scope of its exhaustive next-value check. Build, structural,
learning, editorial-heuristic, and scoped whitespace checks passed. Focused
Chromium checks at 390px and 1280px verified the revised example, keyboard
answers in all four sections, and no document-wide horizontal overflow.
These checks do not prove source accuracy or visual polish.

Latest FCCM editorial check: all three sections now use descriptive titles and
introduce memory banks, word addresses, and padding before using those terms.
The first section separates starting a read from delivering its result. Its
paper-reading paragraph was checked against sections III.A–B of the author
manuscript; the exercise uses explicitly different timing assumptions.
Rebuild, learning calculations, structural checks, and scoped whitespace checks
passed. Focused Chromium checks at 390px and 1280px confirmed all three section
titles, keyboard-operated answers, and no document-wide horizontal overflow.
This was not a screenshot review or a full-site browser regression.

Install the source-rendering dependency with
`python3 -m pip install -r scripts/requirements-course.txt` when needed.
Run `python3 scripts/build_course.py` and `python3 scripts/check_course.py`.
The latest structural check covers 16 lessons, 52 concepts, 1,346 course links,
26 focused paper walkthroughs, and generated navigation in 52 source-note pages. It checks course-linked
local files and HTML anchors, not external URL availability, historical artifact
links inside research notes, or citation accuracy.

Run the browser check with the installed environment:

```bash
LD_LIBRARY_PATH=/home/mehta/.cache/sdl-browser-libs/usr/lib/x86_64-linux-gnu python3 scripts/check_course_browser.py --chromium /home/mehta/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome
```

Both 390×844 and 1280×844 passed: first keyboard target is the skip link;
the contents list opens with Enter; all 161 lesson, route, glossary, paper, comparison, and practice section
targets clear the sticky navigation; document width stays within the viewport at
those targets; and the compiler exercise opens with Enter. Reduced motion is
enabled for these position checks. Screenshots are saved to a new temporary directory
on each run. The mobile and desktop compiler screenshots were visually inspected;
their title, text, and concept links are readable and not clipped horizontally.

The same two viewport widths also passed document-overflow, first-tab skip-link,
and keyboard return-menu checks for all 21 source-note pages. The VLSID source
page's mobile screenshot was visually inspected: its return links, focus outline,
and heading remain readable. The source pages preserve the original notes,
including their evidence limitations; they do not count as newly completed paper
walkthroughs. Only notes directly cited by the course are exported, without
recursively publishing the repository. Relative links are resolved from the
original note's location; directly exported notes link to their HTML versions.

## Not established

This is not an accessibility certification or a full cross-browser review. It does
not cover screen readers, every focus transition, every exercise, zoom, all possible
viewport sizes, normal-motion scrolling, or every paragraph's layout. It also does
not establish that the course content, conference coverage, or source checking is
complete. Conference routes still need deeper paper walkthroughs and fuller
theme/subtheme coverage. Physical-design, serving, durable-update, and distributed
training lessons are now drafted, along with a scientific-computing lesson covering
equation checks, model assumptions, and total solve time. Broader editorial and
source review remain unfinished. `python3 scripts/check_course_science.py` checks
the latter lesson's exact two-point iteration and timing arithmetic; it does not
validate a real heat simulation or establish scientific adequacy.

The FlashInfer (MLSys 2025) walkthrough is linked from the contents and its conference
route, with prerequisites, source-page links, an exercise, and return navigation.
The paper's sections 3.3–3.4 and 4–4.1 were inspected for the bounded mechanism and
evaluation summary. `python3 scripts/check_course_papers.py` checks only the original
teaching examples: equal-piece assignments, planning/combination overheads, and
weighted combinations. It does not reproduce the paper's measurements. Browser
checks include the walkthrough anchor and keyboard exercise at both viewport widths.

The BlitzScale (OSDI 2025) walkthrough adds queue-growth and partial-worker pipeline
examples, failure conditions, and a comparison with FlashInfer. The paper's section 4
cooperative-execution explanation, section 5.1 objectives, and sections 6–6.1 setup
and results were inspected. Its complete scheduling algorithm and implementation
have not been reviewed here. The paper-example checker covers the invented pipeline
completion times and continuous-flow backlog calculations, not the authors' results.
The shared browser checker discovers both walkthroughs from the course data.

The CXL coherence (ASPLOS 2025) walkthrough covers the distinction between a
permission property, a model proof, testing, and progress. Source sections 5.2, 6,
and 8 were inspected; the authors' Isabelle proof was not rerun. The optional
`python3 scripts/check_course_permissions.py` explores an original one-upgrade,
three-device toy protocol: all 11 reachable states of the correct variant preserve
its permission rule. Both intentionally weakened grant rules yield counterexamples.
This establishes neither CXL correctness nor liveness, repeated-operation safety,
or correctness of data values. The browser checker now discovers all three
walkthroughs and checks their anchors and keyboard exercises.

Every lesson now has a structured exercise and an explicit prerequisite list
(empty for the opening lesson). The structural check requires all prerequisite
targets to occur earlier in the course, preventing unknown targets and cycles.
Three cross-topic checkpoints test mean delay versus deadline success, time to an
accepted numerical result, and limits of correctness/performance evidence. Their
answers are initially collapsed, with review links to relevant lessons and papers.
`python3 scripts/check_course_learning.py` verifies their timing and break-even
arithmetic. Browser checks cover each checkpoint anchor and keyboard answer toggle,
including document overflow with answers open. These checks do not establish
learning effectiveness with readers or completeness of the conference material.

The FCCM banked-memory walkthrough develops address-to-bank mapping, a legal
service schedule, stride-dependent conflicts, padding cost, and cycles versus
elapsed time. Section III of arXiv:2503.24132v1 was rechecked and paper identity
confirmed against the official FCCM 2025 program. Its original teaching arithmetic
is covered by `scripts/check_course_papers.py`; there is no hardware reproduction.
The existing route's wider source gaps and manuscript benchmark-count discrepancy
remain unresolved. Browser tests discover the fourth walkthrough automatically.

Four question-led comparison paths now connect the existing lessons, paper
walkthroughs, and themes across the 14 conference routes. They distinguish causes
of waiting, representation costs, permission conditions, and evidence stages.
These connections are labeled teaching interpretations, not joint experiments.
Their new arithmetic examples are included in the learning checker, and browser
checks cover each comparison anchor and keyboard-operated answer. This navigation
and teaching layer does not close the routes' missing paper or subtheme coverage.

The FastServe (NSDI 2026) walkthrough uses the final USENIX paper rather than
earlier preprint headline numbers. Inspected passages cover scheduling, saved-state
pressure, experimental setup, metric definition, and the internal FCFS baseline.
Its original two-job examples separate mean delay, final completion, individual
deadlines, and state-transfer cost. Arithmetic checks cover these timelines,
the switching-cost break-even, and transfer-unit conversion. The paper's results
have not been reproduced, and the complete implementation has not been reviewed.

The homepage now has a guided-course entry with direct links to the first lesson,
cross-conference questions, paper walkthroughs, and coverage status. It explicitly
distinguishes the developing tutorial from the older narrative. The shared entry
and CSS live in `scripts/course_entry.py`; the homepage generator uses them, and
the structural checker verifies that the current homepage contains the same entry
and that its four course anchors exist. The homepage was patched in place, not
regenerated, to preserve existing unrelated additions. At 390px and 1280px the
browser check verifies that the entry itself does not overflow and that activating
its first-lesson link with the keyboard reaches the course. This is not a full
audit of the older homepage's content or layout.

All four ICCAD foundational themes now have original worked examples and explained
exercises. They cover penalty scores versus mandatory constraints, threshold errors
versus average prediction error, independent functional references, and serial or
parallel search cost. Arithmetic and the 256-input toy-counter comparison are
checked in `scripts/check_course_learning.py`. Browser checks discover theme-level
practice, check its anchors, and open its answers by keyboard at both widths.
This deepens the teaching guide; it does not supply missing ICCAD primary-paper
reviews or change the discovery-level source-coverage status.

The four ISSCC reading-guide themes now include original worked examples and
explained exercises. The examples distinguish sequential and overlapped phase
timing, simultaneous storage from reused storage, device energy from system energy,
and sampled measurements from untested operating combinations. Their timing,
capacity, and energy arithmetic is included in the learning checker; theme-level
browser checks cover the four additional exercise sections. The source boundary
remains one locally reviewed accelerator paper, not a conference-wide synthesis.

The conference coverage table now derives theme, subtheme, dedicated example,
explained theme-exercise, and focused paper-walkthrough counts from the same data
used to render the course. `python3 scripts/check_course_coverage.py` audits all
14 declared routes and tests counting with an independent fixture. The table
explicitly excludes inline examples and shared lessons from dedicated-theme
counts. This makes missing components visible without interpreting component
presence as adequate explanation, primary-source review, or course completion.

All four VLSID themes now include original worked examples and explained exercises:
encoding sensitivity at a decision threshold, loading/conversion energy amortized
over reuse, device selection from complete timing and uncertainty, and a deliberately
linear worst-case error model. Exact arithmetic is included in the learning checker.
The theme exercises are discovered by the browser checker. These examples are not
new findings from the three source-backed records and do not establish fabricated
hardware performance, a quantum-device benchmark, or complete VLSID coverage.

The LUT Tensor Core (ISCA 2025) walkthrough uses arXiv:2408.06003v3's design
overview and evaluation methodology. Its source summary keeps circuit synthesis,
kernel simulation, and model-level simulation distinct. Original examples cover
binary tables, two-bit decomposition, signed reinterpretation, reuse cost, table
growth, and a bounded rounding sum. The paper checker exhausts all two-bit weight
pairs for both input examples and checks the remaining arithmetic. No paper
performance result or hardware implementation has been independently reproduced.

All eight SC themes now include original worked examples and explained exercises.
They cover accepted-job timing, a shared connection's capacity, compression cost
and numerical bounds, overlap with limited buffers, numerical behavior when moving
between devices, fixed versus growing workloads, retries and recovery, and
measurement conditions. The learning checker verifies the timing, rounding,
probability, and threshold calculations. The decimal rounding model is explicitly
invented, and the recovery example is one specified failure trace, not an expected
cost. These examples add teaching depth; they do not resolve the SC source-count
discrepancy, add a primary-paper walkthrough, or establish complete subtheme review.
The rebuilt course passed the 390px and 1280px browser checks, including all eight
new exercise toggles and the expanded 67-anchor set. SC theme eight's heading,
text wrapping, and example panel were also visually inspected at both widths;
this spot check is not a complete visual or accessibility audit.

DAC themes one, three, seven, and eight now have original worked examples and
explained exercises. These distinguish operation count from dependency paths,
pause boundaries from switching cost, an acceptable design from an unverified
prediction, and estimated logic timing from timing after wire routes are chosen.
The learning checker verifies the schedule, selection, and delay calculations.
The circuit examples explicitly state exact-integer and simplified-delay assumptions;
they do not assert transistor-level behavior or new results from DAC papers.
At that stage four DAC themes still lacked dedicated worked-example fields; the
subsequent expansion below fills those fields. The route still has no focused
primary-paper walkthrough.
The updated course passed browser checks at 390px and 1280px, covering 71 section
anchors and all discovered theme-exercise toggles. A separate visual spot check
of DAC theme eight found readable headings and wrapping at both widths. These
checks do not establish complete accessibility or validate paper-level claims.

The remaining DAC themes (two, four, five, and six) now have original worked
examples and explained exercises, bringing the route to eight of each. They cover
input reuse and another user's displaced data, propagated numerical error,
deadline-constrained full-request energy, and observable timing plus retained
copies. Exact arithmetic checks include both five-step error recurrences and all
four bit-delay cases in the timing example. These are explicitly simplified
teaching models, not measurements, security assessments, or claims that every
source subtheme has received complete treatment. Paper walkthroughs remain missing.
The numerical checks also enumerate all 32 extreme-sign sequences for each
five-step recurrence and confirm that its final bound is attained. The rebuilt
course passed the 390px and 1280px browser checks, now covering 75 anchor targets
and keyboard-opened exercises for all eight DAC themes.

Two DAC comparisons now have compact tables: complete-request time and energy,
and the four equally likely cases in the random-delay exercise. The latter stays
inside the closed answer, so the question does not reveal its own case analysis.
The renderer supports optional theme-example and answer tables with captions and
column headers, checks row widths, escapes content, and preserves numeric zero.
Run `python3 scripts/check_course_tables.py` to check the rendered tables against
the source data, reject malformed tables, and verify the two examples' values.
The browser checker additionally requires theme answers to start closed, opens
them by keyboard, and checks table width against the containing element. This
adds a targeted table check, not a screen-reader or complete accessibility audit.
The SC overlap example also includes a three-row transfer/calculation schedule,
placed after its schedule explanation and before the limited-buffer discussion.
Its table is checked by independently constructing start and finish times from
the stated dependencies. There are now three theme-level tables under this check.
The two DAC tables were visually inspected at 390px: captions and column headings
wrap without horizontal clipping, and the energy quantities remain aligned.
The final three-table build passed the full browser check at 390px and 1280px,
including table-container widths and closed-then-keyboard-opened answers. The SC
schedule table was visually inspected at both widths and remains readable within
its example panel. No external paper findings or conference-coverage counts changed.

DATE themes one, two, four, and six now have original worked examples and explained
exercises. They address reading updated versus old state, separate and joint
timing bounds, queue tests that discard required ordering, and search restrictions
that exclude valid component combinations. The learning checker verifies the
timing arithmetic, enumerates all distinct orderings of the queue trace, and
checks every combination in the two-component design example. These finite
models do not establish correctness of a compiler, a physical implementation,
or a generated test suite. Four DATE themes still need dedicated examples and
the route has no primary-paper walkthrough.
The rebuilt course passed the browser checks at 390px and 1280px, including the
four new DATE exercise toggles and 79 section anchors. These checks cover layout
and interaction, not the sufficiency of the route's paper evidence.

The DATE route now has a focused CorrectBench walkthrough. It uses author
manuscript arXiv:2411.08510v1, sections III and IV-A–B, with publication identity
checked against the publisher record. It distinguishes generated-design agreement,
the repair loop's stopping action, and reference-based Eval2 evaluation. Original
examples explain a shared reset mistake, a simplified disagreement rule (explicitly
not the paper's rule), exhausted repair cost, and different classification
denominators. Their arithmetic is included in the paper checker. This is not a
code audit, independent experiment, complete manuscript review, or verification
of generated tests. The four unfinished DATE theme examples remain unfinished.
The rebuilt page passed the 390px and 1280px browser checks, including the new
paper anchor and keyboard-operated answer (80 checked section targets in total).

DATE themes three, five, seven, and eight now also have original examples and
explained exercises, bringing the route to eight of each. They cover contention
as both delay and observation, fixed-slot capacity cost, weighted error and
precision-tag overhead, fallback deadlines, parity coverage and release order,
and completion of a batch under the same acceptance requirement. The learning
checker enumerates all five single-bit and ten double-bit patterns for the
specified five-bit parity code, as well as checking timing and error arithmetic.
These are bounded teaching models, not a measured privacy defense, device fault
distribution, or claim that all DATE source subthemes are fully reviewed.
The rebuilt course passed browser checks at 390px and 1280px, now including
84 anchor targets and keyboard-opened exercises for all eight DATE themes.

HPCA themes one, two, three, and five now contain original worked examples and
explained exercises. They cover storage-mode changes and spills, code-table size
versus access traffic, supply/calculation/output schedules, and specialization
with unsupported requests. The learning checker verifies capacity and traffic
counts, storage break-even, output-slot schedules, and supported-request thresholds.
The first pipeline count explicitly stops at calculation; later counts include
output storage. Four HPCA themes still lack dedicated examples, and no HPCA
primary-paper walkthrough has been added. These examples do not broaden the
seven-paper evidence sample.
The full browser check passed at 390px and 1280px with 88 anchor targets. After
the final wording clarification about calculation versus output storage, the page
was rebuilt, structural and arithmetic checks rerun, and that HPCA theme rechecked
at both widths for text presence, document overflow, and keyboard answer opening.

The remaining HPCA themes (four, six, seven, and eight) now have original worked
examples and explained exercises. They cover combined count/rate choices and
startup queues, instantaneous versus average power constraints, first-delivery
and later-gap requirements, and work imbalance with redistribution overhead.
The learning checker verifies the fluid backlog arithmetic, transition powers,
delivery traces, and discrete-cycle load assignments. These examples bring HPCA
to eight dedicated examples and eight explained exercises; they do not add a
paper walkthrough or establish complete source-subtheme coverage.
The rebuilt course passed browser checks at 390px and 1280px, including all eight
HPCA exercise toggles and 92 anchor targets across the course.

MICRO themes one through four now have original examples and explained exercises.
They cover starting cache state and access order, information retained by local
reductions, scale/offset meaning and metadata cost, and grouping overhead versus
buffer feasibility. The learning checker simulates the two-slot replacement rule
and verifies the traffic, encoded-sum, storage, and scheduling calculations.
The examples do not reproduce MICRO mechanisms or expand the 20-paper source
sample. Four MICRO themes and its primary-paper walkthroughs remain unfinished.
The rebuilt course passed browser checks at 390px and 1280px, including the four
new MICRO exercise toggles and 96 anchor targets across the course.

MICRO themes five and six now also have original examples and explained exercises.
They cover a vector-length guard, fallback and checking costs, and competing
numerical acceptance rules. Exact checks verify the supported-request threshold,
mean errors, threshold decisions, and maximum per-value errors. The security
paragraph keeps finite trial observations separate from general probabilities
and impossibility claims. These additions bring MICRO to six dedicated examples;
its last two themes and primary-paper walkthroughs remain unfinished.
The rebuilt course passed the 390px and 1280px browser checks, including 98
anchor targets and the two new keyboard-operated MICRO exercises.

MICRO themes seven and eight now include original examples and explained exercises,
bringing the route to eight of each. They cover cycle count versus elapsed time,
unchanged transfer costs, simultaneous buffer capacity, four-combination controlled
comparisons, and mixed measured/modeled timing. Exact arithmetic checks verify
frequency thresholds and an interaction that reverses a policy's effect. These
examples do not add MICRO primary-paper walkthroughs or validate any hardware
frequency, simulator, or causal claim about an actual conference result.
The rebuilt course passed browser checks at 390px and 1280px, including all eight
MICRO exercise toggles and 100 anchor targets across the course.

Two new cross-conference comparisons bring the question-led comparison set to
six. One derives joint costs instead of multiplying separately measured speedups,
including shared savings and added conversion. The other makes reuse lifetime
explicit and distinguishes advance preparation from eliminated work. They link
the existing MLSys, OSDI, FCCM, ISCA, HPCA, and DAC teaching material without
claiming that the paper mechanisms were integrated or their results reproduced.
The learning checker verifies the original joint-cost and repeated-preparation
calculations; structural checks verify the new internal reading links.
The rebuilt course passed browser checks at 390px and 1280px, covering 102
anchor targets and keyboard-operated answers for all six comparison lessons.

MLSys themes two and five now have dedicated original examples and explained
exercises. They cover peak training-state allocation, recalculation versus
out-and-back transfer, conditions for context reuse, preparation/training pipeline
timelines, and changed data coverage. The learning checker verifies capacity,
transfer break-even, and all four three-batch schedules. These examples do not
establish actual model accuracy, privacy, or device performance. Six MLSys themes
still lack dedicated example fields; the shared lessons and FlashInfer walkthrough
remain separate from that coverage count.
The rebuilt course passed browser checks at 390px and 1280px, including the two
new MLSys exercise toggles and 104 anchor targets across the course.

MLSys themes three and four now have dedicated examples and explained exercises.
They distinguish divided calculation from exchange and contention, and mean
response time from individual deadlines and device readiness. Exact arithmetic
checks cover the stated overlap totals, service orders, shared input-capacity
bound, and ready-versus-loading device cases. Overlap is explicitly conditional
on a legal schedule, not inferred from asynchronous submission. MLSys now has
four dedicated examples; four themes and fuller paper coverage remain unfinished.
The rebuilt course passed browser checks at 390px and 1280px, including the new
MLSys exercise toggles and 106 anchor targets across the course.

MLSys themes one and six now have original worked examples and explained exercises.
They cover operation fusion with temporary-storage costs, index and conversion
overhead for skipped entries, sustained versus initial service rate, and device
energy with preparation. Exact checks verify the retained-entry thresholds and
the two-phase workload timing and energy. The rate change is explicitly stipulated,
not presented as a thermal model or measured device result. MLSys now has six
dedicated examples; its trust and model/runtime-interface themes still need them.
The rebuilt course passed browser checks at 390px and 1280px, including the two
new MLSys exercise toggles and 108 anchor targets across the course.

MLSys themes seven and eight now have original examples and explained exercises,
bringing the route to eight of each. They cover deadline decisions versus average
prediction error, justified versus sampled error bounds, an explicitly invented
loader trust boundary, and exposed contribution rules with preparation cost.
The learning checker verifies misclassification counts, prefix sums, contribution
counts, and reuse arithmetic. The prefix-sum example is not an attention-kernel
implementation, and the loader example does not allege behavior of a real format.
Theme-level component presence still does not establish full subtheme coverage,
adequate primary-paper depth, or completion of the whole course.

An HPCA LEGO walkthrough was added using arXiv:2509.12053v1 and the MIT project
page for conference identity. It teaches relation-based reuse, path alignment
and register cost, graph transformations, fused-dataflow tradeoffs, and the
boundary between synthesis, RTL simulation, and measured hardware. Paper-reported
speedup and energy figures are labeled as such and were not reproduced. Original
teaching arithmetic is checked in `scripts/check_course_papers.py`. The walkthrough
does not make the other HPCA papers reviewed or establish that LEGO’s results
transfer to another chip, workload, or technology.
The rebuilt course passed browser checks at 390px and 1280px, including the new
paper page and answer control, for 111 anchor targets across the course.
The earlier MLSys build passed browser checks at 390px and 1280px, including all
eight MLSys exercise toggles and 110 anchor targets across the course.

OSDI now has original worked examples and explained exercises for all eight
themes. They develop observable call behavior, placement granularity, duplicate
requests and replica versions, migration costs, durable publication, authorization
through helpers, conditional timing, and idle costs attributed to requests.
A four-row crash-state table identifies the missing-payload state that the
specified publication ordering excludes. Arithmetic was checked with exact
fractions for placement sizes, decision thresholds, and timing/energy examples.
This develops the teaching route without expanding the reviewed paper corpus or
claiming that each source subtheme has received exhaustive treatment.

Editorial review corrected LEGO's addition-tree example: four inputs use three
binary additions, with depths three for a chain and two for a balanced tree.
The earlier claim that four serial additions become a two-level tree was wrong.
The delay-storage example now specifies one pair arriving per cycle; it explicitly
distinguishes three occupied delay stages from retaining one isolated value.
The paper summary was shortened, technical terms explained, and evaluation
settings retained. No synthesis, RTL simulation, or hardware measurement was run.

FCCM now has dedicated examples and explained exercises for its three themes.
The additions distinguish bank service from final delivery, derive the sustained
limit of a narrower return path, compare layout preparation against repeated
reads, recount conflicts for different row strides, and include setup time in
clock-rate comparisons. A temporary calculation checked the return schedule,
bank assignments, layout costs, and timing thresholds. These are original
teaching models; no additional conference-paper review or experiment is implied.
The rebuilt course passes structural, coverage-accounting, and table checks.
The OSDI crash-state table's 390px screenshot was visually inspected: its three
columns and caption fit the content area and the row labels remain readable.
The latest browser run passed at 390px and 1280px, covering 122 anchor targets,
the OSDI and FCCM theme exercises, all four theme tables, and keyboard return
navigation for all 21 source pages. Diagnostic screenshots are in
`/tmp/conference-course-browser-3d8z4yk1`. This confirms the tested interactions,
not full accessibility or editorial completeness.

ASPLOS now has dedicated worked examples and explained exercises for all eight
themes. The additions cover reservations versus observations, residual versus
answer error, layout choices across different consumers, exact filtering near
stored data, task placement and pipeline handling, energy per accepted result,
consistent checkpoints and the limits of protection claims, and queue recovery
after delayed adaptation. All quantities describe original teaching models;
they do not expand the set of reviewed paper results. Exact-fraction calculations
and small enumerations checked layout thresholds, task assignments, pipeline
completion times, filtering thresholds, energy ratios, and queue recovery.
The checkpoint example specifies its durable-publication assumption and does
not claim that a real storage implementation provides it.
The rebuilt page passed structural checks and browser checks at both 390px and
1280px, including 130 section targets, all eight ASPLOS exercise controls, and
the 21 source pages' keyboard return navigation. Screenshots from this run are
in `/tmp/conference-course-browser-4m899mrt`. No new source-paper claims or
complete-subtheme coverage are established by these checks.

NSDI now has dedicated worked examples and explained exercises for all ten
themes. They cover stale queue measurements, safe interruption and external
effects, state-copy catch-up, different causes behind equal mean delays,
device-to-host handoff, shared recovery reserves, diagnostic trace detail,
authorization and combined disclosures, task-specific summaries, and prediction
bounds versus averages. The numbers are original teaching scenarios, not new
claims about the listed papers. Temporary exact calculations checked queue
timing, interruption overhead, state-copy convergence, delay means, exception
fractions, reserve deficits, summary counterexamples, and search-cost payback.
Structural and table checks pass for the rebuilt page. These additions do not
independently verify the synthesis's 150-paper review record or complete every
subtheme's source treatment.
Browser checks passed at 390px and 1280px for 140 section targets, including
the ten NSDI exercise controls and return navigation on all 21 source pages.
Diagnostic screenshots are in `/tmp/conference-course-browser-zxh4cttg`.

ISCA now has worked examples and explained exercises for all eight themes.
The additions derive transfer/decode schedules, follow later consumers of
near-data results, account for overlap storage, identify shared network limits,
calculate shape-specific preparation payback, expose address-alias and ranking
counterexamples, distinguish mixed measured/modeled estimates, and compare
combined optimizations over a stated reuse lifetime. Exact calculations checked
the schedules, thresholds, and error margins. All quantities are original
teaching examples, not additional ISCA measurements. Structural, coverage, and
table checks pass. All fourteen routes now have theme-level teaching components;
subtheme completeness and adequate primary-paper depth remain separate open work.
Browser checks passed at 390px and 1280px, covering 148 section targets,
the eight ISCA exercise controls, and all 21 source pages' return navigation.
Diagnostic screenshots are in `/tmp/conference-course-browser-dm_b2995`.

The MICRO TRRIP walkthrough was added after inspecting the author manuscript
arXiv:2509.14041v1, sections 2.4, 3, and 4.1–4.4, with the conference DOI used
for publication identity. It explains the profile-to-cache information path and
distinguishes frequency-based “hot” labels from physical temperature. Its original
two-slot teaching policy deliberately reserves one slot and is explicitly not
TRRIP's aging-based policy. A temporary state simulation checked both access
traces, their hit/miss costs, and the exercise's whole-task savings. The source
evaluation remains author-reported simulation; no paper experiment was rerun.
Structural checks pass with nine walkthroughs and 712 course links.
Browser checks passed at 390px and 1280px for 149 section targets, including
the new TRRIP anchor and exercise, and all 21 source pages' keyboard return
navigation. The TRRIP mobile screenshot was visually inspected: the title,
evidence notice, and prerequisite links fit the content column. Screenshots
are in `/tmp/conference-course-browser-73e55rny`.

The SC cuSZ-Hi walkthrough was added after inspecting arXiv:2507.11165v1,
sections 3–5 and 6.1–6.2.4, and confirming SC identity through the conference DOI.
It separates bounded numerical loss from reversible integer encoding, derives
an original five-point reconstruction, gives a predictor-consistency counterexample,
and follows per-value error into a two-point slope. A separate invented transfer
model compares smaller output with faster compression. Exact-fraction calculations
checked reconstruction errors, code-run sizes, the slope bound, and the connection
rate at which the two modes tie. Those examples do not reproduce cuSZ-Hi or its
GPU measurements. Structural checks pass for ten papers and 723 course links.
Browser checks passed at 390px and 1280px for 150 section targets, the new
paper's keyboard exercise, and return navigation on all 21 source pages.
The mobile cuSZ-Hi screenshot was visually inspected: title, evidence notice,
and prerequisite links fit the content column. Diagnostic screenshots are in
`/tmp/conference-course-browser-1ro1et6_`.

The DAC GSIM walkthrough was added after inspecting arXiv:2508.02236v1,
sections II–IV, and locating the author-hosted DAC conference paper. It separates
host simulation runtime from simulated circuit behavior, counts activity-check
and grouping costs, demonstrates simultaneous register-update semantics, and
explains bit dependencies and expression-sharing costs. Small state and set
enumerations checked the original grouped-activity examples, swap trace, carry
case, and preparation/run totals. Paper speedups remain author-reported runtime
measurements, not chip-performance claims or reproduced experiments. Structural
checks pass with eleven walkthroughs and 734 course links.
Browser checks passed at 390px and 1280px for 151 section targets, including
the GSIM walkthrough and keyboard exercise, and all 21 source pages' return
navigation. The new mobile screenshot was visually inspected: the title,
scope notice, and prerequisite links fit the content column. Screenshots are
in `/tmp/conference-course-browser-bp0w3px_`.

The VLSID TimeFloats walkthrough uses the August 2024 author preprint,
arXiv:2409.00495v1, sections III–IV; it does not claim the preprint was compared
with the final 2025 conference text. Its energy-accounting discrepancy was
checked in both HTML and PDF extraction (Table I, page 5; prose, page 6) and
left unresolved. The course does not treat the claimed efficiency as independently
validated or the modeled design as measured silicon. Original examples cover
floating-point alignment, accumulation of discarded terms, timing-code margins,
and rounded-away updates. Exact arithmetic checked those examples and the two
different component sums. A missing prerequisite anchor was found and corrected;
the rebuilt page passes structural checks with twelve papers and 746 links.
Browser checks passed at 390px and 1280px for 152 section targets, including
the TimeFloats exercise and all 21 source pages' keyboard return navigation.
Its mobile screenshot was visually inspected: title, preprint-scope notice,
and prerequisite links remain readable. Screenshots are in
`/tmp/conference-course-browser-q62nhppo`.

The ISSCC ConvFormer walkthrough was added from the conference digest deposited
as arXiv:2512.17555v1. It distinguishes plain matrix-product reassociation from
the changed nonlinear attention formulation, follows live buffers through phased
reuse, and separates a pruning cost threshold from acceptable output quality.
Direct calculations checked both matrix orders, the softmax counterexample,
buffer footprints, transfer counts, factorized outputs, and retained-channel
thresholds. The chip results remain author-reported, and the prior-design
comparison's peak-efficiency assumptions are explicit. Structural checks pass
with thirteen papers and 756 course links; no chip experiment was reproduced.
The final ISSCC build, including the clarification that fully materialized matrix
sizes are not universal storage lower bounds, passed browser checks at 390px and
1280px for 153 section targets and all 21 source pages. Screenshots are in
`/tmp/conference-course-browser-tw2wp9c9`.

The ICCAD RSizing walkthrough was added after inspecting the author-hosted paper,
sections II–IV and Table II. Its teaching examples distinguish population variation
from uncertainty about a prediction, individual from joint acceptance, and an
observed all-pass sample from a population guarantee. The reported simulation
results and remaining approximation error stay explicit; no circuit experiment
was reproduced. `python3 scripts/check_course_rsizing.py` checks the original
population counts, spread calculation, screening cost, joint-failure bounds, and
all-pass confidence arithmetic. Structural checks pass with fourteen walkthroughs
and 796 links. All fourteen routes now have one walkthrough, but this does not
establish source-backed teaching coverage of every theme or subtheme.
Browser checks passed at 390px and 1280px for 154 section targets, the paper
exercises, and all 21 source pages' return navigation. The new mobile chapter
screenshot was visually inspected: heading and evidence notice fit the column.
Screenshots are in `/tmp/conference-course-browser-w8kqnysn`. A final plain-language
clarification defined nominal conditions and replaced unexplained distribution
terminology; after rebuilding, targeted browser checks verified that wording,
overflow, heading position, and the chapter's keyboard exercise at both widths.
The final build also passes the 994-link structural check.
After the subtheme prompt and evidence-boundary rendering change, the complete
browser regression again passed at 390px and 1280px for 154 section targets and
all 21 source pages. The rebuilt-page screenshots are in
`/tmp/conference-course-browser-81jxt14g`; the RSizing mobile paper view was
visually inspected for title, scope notice, and column fit.

The editorial triage script checks 97 route themes and 228 subtheme entries. It
found no obviously thin theme by its length and marker heuristics, but this is not
a quality certification: subthemes are currently definition entries, not separate
mini-lessons. The course goal therefore remains open until each subtheme is tied
explicitly to worked reasoning, a stopping condition, and an appropriate source.

The first subtheme-writing batch adds explicit application, failure, evidence, and
source blocks for all 30 subthemes in the VLSID, ISSCC, FCCM, and ICCAD routes.
The page was rebuilt and the full browser check passed again at both widths. A
targeted VLSID route view was also checked at 390px and 1280px; its two subtheme
blocks fit without horizontal overflow and the source links remain readable. The
targeted screenshots are in `/tmp/course-subtheme-view-xfz8kx03`.

A second subtheme-writing batch adds the same explicit application, failure,
evidence, and source treatment to all 32 DAC and DATE subthemes. The editorial
checker now verifies 62 explicit subtheme notes out of 228 total; the remaining
166 still need authored treatment.

The ISCA and HPCA batch adds 32 more explicit subtheme blocks. The editorial
checker now verifies 94 explicit subtheme notes out of 228 total; 134 remain.
The browser regression passed at both widths after rebuilding; the latest
screenshots are in `/tmp/conference-course-browser-s4ytq68`.

The MICRO and SC batch adds 32 more explicit subtheme blocks. The editorial
checker now verifies 126 explicit subtheme notes out of 228 total; 102 remain.
The complete browser regression passed again at both widths after rebuilding; the
latest screenshots are in `/tmp/conference-course-browser-dacd_qy8`.
After that batch, the complete browser regression passed again at 390px and
1280px for 154 section targets and all 21 source pages. The latest screenshots
are in `/tmp/conference-course-browser-2zvrhe7p`.

The final long-route batch adds explicit blocks to all remaining MLSys, OSDI,
ASPLOS, and NSDI subthemes. The editorial checker now verifies 228/228 subthemes
in source data and 228/228 complete blocks in generated HTML, each with
application, failure, evidence, and source fields. The full browser regression
passed at 390px and 1280px for 154 section targets and all 21 source pages; the
latest screenshots are in `/tmp/conference-course-browser-kbuxqg9f`. This proves
frontend structure and rendering, not citation correctness or independent paper
reproduction.

After correcting the route status text to distinguish explicit subtheme teaching
from broader conference-paper coverage, the final build passed structural and
editorial checks again. The browser regression passed at both widths for 154
section targets and all 21 source pages; the latest screenshots are in
`/tmp/conference-course-browser-0ensslal`.

The final source-link audit found 14 unique external URLs used by the authored
subtheme blocks and paper walkthroughs. Requests using a browser user agent
returned HTTP 200 for each URL, including the author-hosted PDFs and arXiv pages.
This checks reachability only; it does not replace reading the source or prove
that every nearby claim is supported by it.

## Follow-on learning-product work — 2026-09-22

Added a final paper-reading challenge after the guided walkthroughs. The learner
must choose a full paper from a conference route that is not one of those
walkthroughs, record the exact paper identity, and answer six staged questions:
state the claim, follow the mechanism, count the whole cost, audit one result,
find a boundary, and write a bounded verdict. Six labelled note fields are
available in the page; they do not save across reloads, so learners are told to
copy their notes elsewhere. A closed-by-default, keyboard-operable rubric checks
claim, mechanism, complete cost, traceable evidence, and limits. The homepage and
course contents both link to the challenge.

The structural checker now verifies the challenge anchor and all six visible
labels. The Chromium regression passed at 390px and 1280px for 155 section
targets, including keyboard entry, challenge field editing, rubric toggle, and
document overflow. Screenshots from the full pass are in
`/tmp/conference-course-browser-jpc1p0z0`; focused challenge views were inspected
at `/tmp/paper-challenge-390.png` and `/tmp/paper-challenge-1280.png`. The
structural audit reports 998 course links, 16 lessons, 40 concepts, 14 paper
walkthroughs, and 21 source pages. Arithmetic, paper-example, table, and editorial
checks also pass. These checks show that the exercise works as a page; they do
not show that a learner can complete it or that it improves independent reading.

The next required check is a real learner pilot. Ask Propel (or another intended
reader) to use the challenge on a paper they have not studied, without coaching
through the answers. Note where they hesitate, which terms need explanation, and
whether they can cite the paper for each part of their verdict. Revise from those
observations; do not claim learning transfer until that pilot has happened.

## Learning outcomes and starting-point check — 2026-09-22

Added five observable course outcomes and a five-question, ungraded self-check.
Each answer explains the reasoning and links to a relevant lesson; the final
question directs learners to the evidence boundary instead of inviting a
performance claim beyond the tested device and workload. The start page says
that no specialist hardware background is required, and the homepage and course
contents link directly to it.

`python3 scripts/check_course.py` passes with 1,008 course links, 16 lessons,
40 concepts, 14 paper walkthroughs, and 21 source pages. The editorial,
arithmetic, paper-example, and table checks pass. The expanded full browser suite
was terminated during its 1280px pass after completing the 390px pass. The
focused browser mode (`--changed-sections-only`) passed at 390px and 1280px: all
seven new section anchors, keyboard-opened explanations, lesson links, capstone
note entry, rubric toggle, and page overflow. Orientation and capstone screenshots
were visually inspected at both widths in `/tmp/conference-course-browser-w39nritb`.
This focused test does not replace the full regression; the earlier complete
course regression predates the orientation addition.

Added `PAPER-READING-PILOT.md` as a session protocol and observation record. It
specifies how to assess source-grounded reasoning without coaching, record
friction, and decide what to revise. No learner session has taken place yet, so
there is still no evidence that Propel can independently complete the challenge.

## Full browser regression rerun — 2026-09-22

The earlier browser process termination was not a course failure. Rerunning it
with the cached shared-library directory in `LD_LIBRARY_PATH` completed
successfully. At both 390×844 and 1280×844, Playwright checked all 161 course
section targets, document overflow, keyboard navigation and exercises, all 21
source-note pages, and their return menus. The focused additions run also passed
the seven orientation/challenge anchors, keyboard-opened answers, lesson links,
challenge note entry, rubric toggle, and overflow at both widths.

The full-run captures are in `/tmp/conference-course-browser-rq3xhpz7`; the
focused captures are in `/tmp/conference-course-browser-mp40l59z`. Mobile and
desktop capstone captures were visually inspected and their text, fields, and
rubric fit the viewport. This remains a browser regression, not a screen-reader
or accessibility certification, a complete editorial/source audit, or evidence
from an actual learner. The Propel pilot described above is still outstanding.

## Scientific-workflow source review — 2026-09-22

Reviewed the stopping-criteria explanation against the linked official PETSc
`KSPConvergedDefault` documentation and Netlib's *Templates for the Solution
of Linear Systems*. The lesson now distinguishes the equation residual from
error in the computed answer, explains in everyday terms that PETSc compares
against the larger relative or absolute limit, and gives a labeled invented
example (reference residual 100, relative limit 1, absolute limit 0.1). It also
warns that a preconditioned residual may not be the original equation mismatch
and that hitting the iteration limit is not default convergence. These are
bounded explanations of the documented solver rule, not claims about a paper's
measurements or proof that a physical model is adequate.

`python3 scripts/check_course_science.py` passes the exact recurrence and
timing arithmetic plus the new threshold example. `python3
scripts/check_course.py` passes with 1,008 course links. The complete browser
regression again passes at 390px and 1280px for 161 section targets and all 21
source pages. Captures are in `/tmp/conference-course-browser-ldzg3vyr`; the
mobile scientific-workflow section was visually inspected. This is one reviewed
lesson, not yet the course-wide claim-by-claim editorial and source audit.

## Dependency and bounded-buffer lesson review — 2026-09-22

The pipeline lesson previously said that a fast reader would eventually have to
pause, but did not show the cause numerically or distinguish a pausable producer
from an input source that cannot wait. It now calculates the illustrative rates:
one image every 2 ms is 0.5 images/ms, while one resize every 5 ms is 0.2
images/ms. Once flowing, the queue grows by about 0.3 image/ms if neither stage
is throttled. The explanation now states that a finite buffer only absorbs a
temporary mismatch: a pausable source waits when it fills; an unpausable source
requires dropping work or storing it elsewhere, or the buffer overflows.

Added the official OSTEP producer/consumer chapter as the source for the
bounded-buffer discussion, alongside the existing thread/concurrency chapter.
The rate difference and queue growth are explicitly labeled as an invented
teaching model, not a paper measurement. The learning arithmetic check now
verifies 0.5 − 0.2 = 0.3 images/ms and three excess images over 10 ms, as well
as the matching explanation in the source module. The structural audit passes
with 1,009 course links. The complete browser regression passes at 390px and
1280px for 161 section targets and 21 source pages; captures are in
`/tmp/conference-course-browser-o9iq_g_9`. This remains a bounded review of one
core lesson, not evidence that all course claims have been checked or that a
learner has completed the course.

## Precision lesson arithmetic review — 2026-09-22

Checked the precision lesson's worked bounds and its cited Jacob et al. paper.
The paper-specific description is deliberately limited to the arXiv abstract:
integer-only inference co-designed with training to preserve accuracy, evaluated
on image classification and detection on CPUs. Its result is not generalized to
other tasks, and all numeric examples in the lesson are labeled as teaching
examples.

This pass found and corrected a real decision example error: shifting scores
0.501 and 0.499 by −0.002 and +0.002 produces a tie, not a reversal. The lesson
now uses 0.502 and 0.498 shifted by −0.003 and +0.003, yielding 0.499 and 0.501.
It also states that the 0.2 summed-input-error bound assumes exact additions;
rounding during addition needs a separate error bound. The learning checker now
asserts both the quantization arithmetic and that the example actually reverses
the ordering.

`python3 scripts/check_course_learning.py` and `python3
scripts/check_course.py` pass; the structural count is 1,009 course links. The
full browser regression passes at 390px and 1280px for 161 anchors and 21 source
pages. The edited precision paragraphs were visually inspected at both widths;
captures are in `/tmp/conference-course-browser-g40ceyhv`. This verifies one
lesson's example and rendering, not every source claim or learner transfer.

## Memory, caching, and replacement lesson review — 2026-09-22

The linked OSTEP chapter citation had named only sections 22.1–22.3 even though
the lesson's recency rule and scan-failure boundary are treated in sections
22.5–22.6 and 22.12. The reference now identifies all the cited sections. The
lesson also adds a clearly invented two-item LRU trace: reading X and Y evicts
cached A and B, so the next A and B reads miss. OSTEP's own longer example
reports 0% hits when LRU cycles through 50 pages with room for 49; this is a
failure for that access pattern, not a claim that recency is generally useless.

The learning checker now exercises that trace, its no-scan baseline, and the
cache-cost arithmetic. The structural check passes with 1,009 course links; the
full browser regression passes at 390px and 1280px for 161 anchors and 21 source
pages. The replacement-policy paragraph was visually checked at mobile width;
captures are in `/tmp/conference-course-browser-pymwudi7`. This is a source
alignment and teaching-example check for one lesson, not a full audit of the
remaining course or a learner pilot.

## Interconnect routes and shared-capacity lesson review — 2026-09-22

Checked the CONGA mechanism description against the original SIGCOMM 2014 paper.
Its abstract says CONGA divides TCP flows into flowlets, estimates congestion on
fabric paths, and uses feedback from remote switches to place flowlets; the
course describes that mechanism without extending its results to unrelated
topologies or to the invented examples. The paper-specific description remains
explicitly abstract-scoped.

The routing lesson's four-transfer example now states the timing assumptions:
transfers start together, there is no competing traffic, and endpoints can keep
both paths busy. The arithmetic check covers the shared 10-GB/s bottleneck, the
18-GB versus 2-GB skew, the balanced one-second bound, and the post-failure
3-GB-buffer fill time of 0.5 seconds. It also checks each answer in the learner
exercise. The learning arithmetic check passes; the structural check passes at
1,009 links. The full browser regression passes at 390px and 1280px for 161
anchors and 21 source pages. The new assumptions paragraph was visually checked
on mobile; captures are in `/tmp/conference-course-browser-_d5g537_`. This
review does not establish that every networking or hardware-route claim across
the course has been checked.

## Skipping-work lesson review — 2026-09-22

Checked the sparse-storage, timing break-even, and worker-imbalance examples in
the lesson. Added a worked signed-error example: omitting products +0.10 and
−0.08 changes the sum by +0.02, while the no-cancellation bound is 0.18. A
second example shows why a small weight alone does not ensure a small effect:
weight 0.001 times input 1,000 contributes 1. The prose distinguishes this
local bound from whether later operations preserve task-level usefulness.

The EIE description remains limited to the paper's abstract: compressed-network
inference using sparse matrix-vector operations and shared weights. The lesson
does not transfer that paper's reported performance to other models or
hardware. Its storage, timing, and error values are teaching examples.

The learning checker passes the arithmetic and text assertions, and the
structural checker passes with 1,009 course links, 21 source pages, and 14 paper
walkthroughs. The full browser regression passes at 390px and 1280px, including
161 anchor positions, keyboard controls, overflow checks, and all source pages.
Screenshots are in `/tmp/conference-course-browser-fr2_j4fm`. Visual inspection
of the newly added omission-bound paragraph at both widths confirms readable
wrapping without clipping. This is a focused lesson check, not a review of every
course claim or evidence of learner transfer.

## Compiler lesson review — 2026-09-22

Reworked the compiler lesson to define an intermediate representation in plain
language and explain why an operation graph can preserve information that is
harder to see after lowering to individual reads and arithmetic instructions.
The TVM account now follows the primary paper's graph-to-tensor-schedule and
automated-search description (sections 2–5), rather than treating the abstract
as support for those implementation details. It remains a bounded account of
that paper, not a claim about what every compiler does.

Added learning checks for the separate-pass and fused logical transfer counts
(16 MB and 8 MB under the stated assumptions), the three-significant-digit
addition-order example (1 versus 0), and the 100-run specialization break-even
and 60-run exercise. The arithmetic/text checker passes; structural checks pass
with 16 lessons, 40 concepts, 1,009 links, 21 source pages, and 14 walkthroughs.
The full browser regression passes at 390px and 1280px for all 161 anchors and
21 source pages. The new definition paragraph was visually checked at both
widths; captures are in `/tmp/conference-course-browser-ugxdps8f`. This review
still does not establish course-wide source accuracy or learner transfer.

## Distributed-work lesson review — 2026-09-22

Checked the lesson's primary-source summary against the original OSDI 2004
MapReduce paper. Section 3.3 describes which completed outputs are lost with a
failed worker, atomic publication of outputs, and ignoring duplicate completion
messages; section 3.6 describes backup attempts for slow tasks. The course keeps
this as a historical example and does not claim the same retry rule fits every
operation.

Extended the learning checker to cover the lesson's fixed-work scaling and
exchange examples, shared-link lower bound, barrier wait, speculative-attempt
time gain, checkpoint overhead and conditional lost-work averages, and the
four-versus-eight-worker exercise. The teaching numbers match the stated
assumptions. Learning and structural checks pass; the structural count remains
16 lessons, 40 concepts, 1,009 links, 21 source pages, and 14 walkthroughs. The
full browser regression had already passed against this unchanged lesson text
at both target widths. This pass does not validate a distributed production
system or demonstrate learner transfer.

## Correctness and fault-boundary lesson review — 2026-09-22

Checked the OSTEP source boundary: chapter 42.1 illustrates crashes between
related writes; section 42.2 explains that a filesystem checker can restore
metadata consistency while still failing to recover the user's intended data.
The lesson keeps its separate counter/flag scenario as an invented example and
does not present it as an OSTEP experiment.

Extended the learning checker to verify the modulo-256 counter boundary, the
65,536 two-input test-space count, the stated independent-majority error
probability, parity encoding of three different valid counter values, and the
lesson's safety/progress and request-identity distinctions. The pre-existing
bit-flip enumeration still verifies that all single-bit changes in the
five-bit protected word are detected and all two-bit changes preserve even
parity. Learning and structural checks pass; the course remains at 16 lessons,
40 concepts, 1,009 links, 21 source pages, and 14 walkthroughs. No course text
or layout changed in this pass, so the immediately prior full browser run still
applies to the rendered page. This does not establish hardware fault coverage
or prove that an actual file system recovers a particular application state.

## Security and shared-state lesson review — 2026-09-22

Corrected a real arithmetic ambiguity in the timing example. An unspecified
"20 ms delay" did not ensure overlap between the lesson's 4–6 ms and 9–11 ms
cases. The example now says the same background delay can vary from 0 to 20 ms
for either case and calculates the possible ranges as 4–26 ms and 9–31 ms,
which overlap from 9 to 26 ms. It distinguishes ambiguity in one sample from
eliminating the signal across repeated samples.

Expanded the FLUSH+RELOAD description from abstract-level summary to the attack
conditions and steps reported in sections 2–4 of Yarom and Falkner's paper:
shared pages and last-level cache, flushing and timing a line, and the same-
physical-processor setup for their virtual-machine experiment. The lesson limits
the result to the tested setup and does not generalize vulnerability to current
machines. Also replaced the undefined "working set" phrase with a plain
description of actively used data and the capacity stranded by fixed
partitioning.

Added checks for the overlapping timing ranges, detector precision and missed
attacks, the fixed-partition example, and the attack's prerequisites and steps.
The learning and structural checks pass (16 lessons, 40 concepts, 1,009 links,
21 source pages, 14 paper walkthroughs). The full browser regression passes at
390px and 1280px for 161 anchors and 21 source pages. The three edited
paragraphs were visually checked at both widths. The timing and partition
captures are in `/tmp/conference-course-browser-xiisww45`; the final
source-bounded FLUSH+RELOAD paragraph captures are in
`/tmp/conference-course-browser-k_ybr0kf`. These checks do not prove resistance
to all side channels or validate performance on a current machine.

## End-to-end service lesson review — 2026-09-22

Added a linked arithmetic check for the capstone service trace. It verifies the
table's cumulative 8/12/32/44/47/50-ms stages; the original and faster cold
paths; the 80/20 warm/cold average and cold-request deadline misses; the
preparation/loading overlap assumption; per-request memory capacity; compressed
state plus conversion cost; and the busy-warm versus idle-cold exercise. It
also asserts the course's central accounting rules: use the same quality and
version promise, include all arrivals and failed/late outcomes, and do not
claim the proposed conference mechanisms have been tested together.

The learning arithmetic/text checks pass and the structural checker still
passes with 16 lessons, 40 concepts, 1,009 links, 21 source pages, and 14 paper
walkthroughs. The full browser regression passed after the most recent lesson
text changes; this pass changed only the checker, not rendered course content.
These checks validate the invented service model, not the proposed composition
protocol or a deployed service.

## Physical-limits lesson review — 2026-09-22

Checked the OpenROAD flow summary against the project's current official
documentation: floorplanning, placement, clock-tree synthesis, routing,
parasitic extraction, and final timing/physical checks. The lesson keeps this
as an example workflow and says no course design is thereby shown to have
completed it. Also checked the distinction between simulation, timing
analysis, design-rule checking, connectivity comparison, post-layout
simulation, and measurement of sampled chips; the text does not treat one as
proof of the others.

Added arithmetic/text checks for power versus energy, the measurement-boundary
example, the squared-voltage switching component, sustained work, timing
budget, and the exercise's preparation-energy crossover. Learning and
structural checks pass; the structural count remains 16 lessons, 40 concepts,
1,009 links, 21 source pages, and 14 paper walkthroughs. The full browser
regression passes on the current course at both target widths. The energy
boundary, timing-budget, and evidence-stage paragraphs were visually checked
at 390px and 1280px; captures are in
`/tmp/conference-course-browser-k_ybr0kf`. This review does not validate a
physical design or prove a manufactured chip meets a specified yield.

## Training-workflow lesson review — 2026-09-22

Corrected a real arithmetic error in the asynchronous-exchange example. The
optimistic fully overlapped step is 8 ms preparation + max(40, 12) ms for
calculation/exchange + 4 ms update = 52 ms, not 56. The concrete chunk-ready
schedule takes 58 ms: six milliseconds of the first transfer overlap
calculation, the final six-millisecond transfer begins only after all workers
finish at 48 ms, and the update then ends at 58 ms.

Added linked checks for the baseline stage table, worker-wait and mean-time
contrast, balanced-assignment costs, that chunk schedule, 52/58-ms comparison,
compression step duration and 1,049/1,050-step boundary, target-quality totals,
and the 1,300-step exercise. The learning arithmetic/text checks and structural
checks pass (16 lessons, 40 concepts, 1,009 links, 21 source pages, 14 paper
walkthroughs). The full browser regression passes at 390px and 1280px; the
corrected paragraph was visually checked at both widths. Captures are in
`/tmp/conference-course-browser-67m7jgst`. The examples remain teaching models,
not measurements of a named training system.

## MLSys first-theme route review — 2026-09-22

Reviewed the first MLSys teaching theme, “Change the work the device actually
performs.” Its fusion, storage, and indexed-sum examples are internally
consistent; the strict break-even thresholds are 33 retained entries without
conversion and 26 with the stated 20-unit conversion cost. The route frames
these as original teaching models and preserves the distinction between an
operation-count reduction, a complete-path saving, and an acceptable result.

Checked the route's evidence wording against
`metadata/mlsys-2025-first-principles-atlas-manifest.json`: 61 conference
records, 56 cataloged as full text, five cataloged as abstract-only, but 61
locally extracted source texts. The route correctly says those counts do not
mean independent reproduction and calls paper names reading leads. The learning
checker now guards the route's eight themes and 24 subthemes, requires a worked
example and exercise for each theme and example/failure/evidence/source detail
for each subtheme, and checks the first theme's calculations and evidence
boundary. Learning and structural checks pass. The last full browser regression
is still current because this pass changes no rendered content. This begins,
but does not complete, the route-by-route conference audit.

## MLSys memory-theme route review — 2026-09-22

Checked the second MLSys theme's three examples and subthemes. The peak
calculation is 22 GB versus 20 GB available; reducing saved intermediates by
3 GB leaves a 19-GB peak only under the stated no-extra-allocation assumption.
For the separate 2-GB out-and-back schedule, four GB takes 40 ms at 100 GB/s
and 10 ms at 400 GB/s; adding the stipulated 50-ms base gives 90 and 60 ms,
compared with 62 ms for recalculation. The exercise's break-even rate is
333⅓ GB/s, and the extra two-GB buffer makes the nominal 19-GB schedule
infeasible at 20 GB capacity.

The theme keeps serving-prefix reuse separate from training state and storage
placement; its subtheme notes do not attribute the original state-key or
training calculations to FlashInfer. Learning and structural checks pass, and
the checker covers all 24 MLSys subtheme details plus this theme's arithmetic
and source boundary. The previous full browser run remains current because
this pass changed no rendered content. The source review is still limited to
the first two MLSys themes, not the full route or other conferences.

## MLSys partitioning and overlap theme review — 2026-09-22

Checked the third MLSys theme's dependency and timing examples. The two-device
case takes 20 ms sequentially and 14 ms only under the stated six-millisecond
legal overlap; four devices take 26 ms and lose to the 24-ms single-device
baseline under the stipulated exchange cost. The longer-input case totals
44 ms. In the practice case, 15 + 10 − 4 = 21 ms beats 24 only when the
four-millisecond overlap and slower stage times are actually supported; without
overlap, 25 ms loses. This matches the lesson's warning not to subtract an
assumed overlap from isolated measurements.

The course labels these timelines as original teaching models and presents
context-parallelism and overlap papers as leads to compare, not proof that the
same schedule generalizes. The learning and structural checks pass; the checker
now validates the arithmetic and the three MLSys subtheme evidence notes. No
rendered course text changed, so the previous browser pass remains applicable.
Only themes 1–3 of the MLSys route have now had this focused review.

## MLSys scheduling theme review — 2026-09-22

Checked the fourth MLSys theme's scheduling and resource examples. For the
three simultaneous requests, the original completion times average 10 ms and
short-first averages 6 ms, but short-first misses the long request's absolute
time-9 deadline. Two devices that each calculate ten requests per second still
cannot exceed the shared input link's 12 requests per second. In the exercise,
ready-device completion times are 8/2/4 ms (mean 14/3); delaying the long
request four milliseconds for preparation moves its finish to 12 ms and the
mean to 6, while missing its deadline. The values and no-interference premise
remain labeled as toy assumptions.

The learning checker now verifies those averages, deadline outcomes, shared
input bound, and exercise cases; it also requires the three subtheme evidence
notes. Learning and structural checks pass. No rendered course content changed,
so the previous full browser regression remains current. This focused review
covers four of eight MLSys themes, not all papers behind the route's reading
leads or the other conference routes.

## MLSys data-supply theme review — 2026-09-22

Checked the fifth MLSys theme's training-input pipeline and data-selection
examples. Under the stated one-preparation-worker, one-trainer, ordered-batch
model, the three-batch completions are 44 ms for 12-ms preparation/8-ms
training, 40 ms when only training is halved, 30 ms when preparation is halved,
and 22 ms when both stages take 6 and 4 ms. The learning checker now calculates
these schedules directly and guards the key prose boundaries.

The data example correctly separates faster preparation from changed selection:
filtering 500 of 1,000 examples while dropping every example from a required
rare case does not establish unchanged performance on that case. The route also
does not claim local data storage proves privacy, nor attribute its data
selection example to the inference-serving paper used as one reading lead.
Learning and structural checks pass. No rendered text changed, so the previous
browser regression remains applicable. This focused pass covers five of eight
MLSys themes; paper-by-paper source verification and other conference routes
remain unfinished.

## MLSys sustained-device theme review — 2026-09-22

Checked the sixth MLSys theme's rates, completion times, energy, and scope. In
the stipulated 1,000-request model, the first device completes in 18 seconds
and uses 760 J; the second takes 50/3 seconds and uses 750 J. Adding its stated
two seconds and 100 J of exclusive preparation changes that to 56/3 seconds
and 850 J, reversing both comparisons. At 100 requests, the first device
finishes in 1 second using 60 J, while the second takes 5/3 seconds and uses
75 J. The learning check now calculates these cases exactly.

The course explicitly calls the rate drop stipulated, not a thermal model, and
excludes whole-system energy. Source-note attribution was stale: all three
subthemes previously linked FlashInfer even though the route points to other
papers. Replaced those with paper-specific sources and boundaries: MEADOW for
low-power FPGA dataflow, FlexInfer for CPU–GPU/PCIe execution choices, and
MAS-Attention for heterogeneous edge-accelerator attention dataflow. None is
used to claim the toy schedule is measured behavior. Learning and structural
checks pass. The full browser regression passed at 390px and 1280px across
161 anchors and 21 source pages. The remaining two MLSys themes, other
conference routes, and full paper-by-paper synthesis are still outstanding.

## MLSys result-trust theme review — 2026-09-22

Checked the seventh MLSys theme's decision counts and bound logic. The four
predictions (8, 9, 9, 12 ms) and outcomes (9, 11, 8, 10 ms) produce one
deadline miss among the three accepted requests and one deadline-meeting
request among the rejected requests. Mean absolute error is 1.5 ms, which
does not replace decision counts at the 10-ms threshold. A real upper-error
bound of 2 ms would justify accepting predictions at most 8 ms within that
bound's operating range; an 8.5-ms prediction plus the bound is 10.5 ms and
cannot be certified. The checker now calculates these counts and values.

The fictional model-file interface is explicitly separated from prediction
the three subtheme notes: AIOpsLab is the benchmark/evaluation lead, the
uncertainty paper concerns multimodal robotics rather than this toy time bound,
and the supply-chain paper studies Python ML-framework dependencies rather than
the invented file field. The local catalog marks the uncertainty record
abstract-only; its local text is not independent reproduction. Primary paper
pages confirm those bounded contexts. Learning and structural checks pass. The
course was rebuilt; the full browser regression passed at 390px and 1280px
across 161 anchors and 21 source pages. The selected screenshot set did not
include the MLSys theme itself, so it confirms shared layout behavior rather
than a theme-specific visual inspection. One of eight MLSys themes remained
without a focused review at that point; all other conference-route and
paper-by-paper work remains outstanding.

## MLSys structure-exposure theme review — 2026-09-22

Checked the eighth MLSys theme's outputs, contribution counts, preparation
cost, and reuse assumption. For four positions, the required prefix sums are
1/3/7/15, with 10 permitted contributions out of 16 possible. Under the toy
unit-cost model, one specialized use costs 18 rather than 16, so it loses; two
compatible uses with the same plan prepared only once cost 28 rather than 32.
For five positions, it costs 23 rather than 25. The lesson now says explicitly
that the prepared plan is shared across compatible uses, and the learning check
recomputes these comparisons. It also retains the counterexample: reusing a
prefix-only plan for an all-input sum produces wrong outputs.

Replaced the theme's stale FlashInfer links with scoped reading sources:
FlexAttention for programmable attention score/mask rules, XGrammar for
grammar-constrained generation, and The Hidden Bloat in Machine Learning
Systems for workload-dependent code removal. The toy operation and scheduling
tradeoffs are not attributed to those papers; unused in one workload is not
treated as proof that code is unnecessary for every supported input. Learning
checks pass. The course was rebuilt and the full browser regression passed at
390px and 1280px across 161 anchors and 21 source pages. I also captured and
visually inspected the MLSys theme-8 section at 390px: the heading, explanation,
subtheme labels, and exercise text wrap within the viewport without horizontal
clipping. This completes focused arithmetic/subtheme-note reviews of all eight
MLSys themes, but not the route's paper-by-paper source verification, other
conference routes, or course-wide synthesis.

## OSDI translation and specialization theme review — 2026-09-22

Started the OSDI route with “Translate a program without changing its promise.”
The aliasing example correctly separates equal returned values from the full
interface: an in-place update changes what a retained reference observes, so
it violates the stated new-array/non-mutation promise. The measurement example
also checks out: 8+1 and 5+4 both appear as 9 under unequal instrumentation,
which does not establish equal uninstrumented cost. Regression checks now
simulate the shared-reference mutation and verify the displayed totals.

Fixed mismatched source notes that pointed all three subthemes at BlitzScale.
They now point to QiMeng-Xpiler for cross-platform translation, Mirage for
multi-level tensor-program search, and KPerfIR for compiler-integrated profiling.
The evidence notes explicitly keep the examples original and retain the
papers' boundaries: QiMeng's candidate translation can fail and carries
substantial compile/search cost; Mirage's equivalence check is probabilistic;
KPerfIR's reported overhead/error are from its Triton evaluation, not the toy
instrumentation schedule. The route's Neutrino mention remains a separate
profiling lead, not support for the toy numbers. Learning, structural, and
editorial checks pass. The full browser regression passed at 390px and 1280px
for 161 anchors and 21 source pages. I also visually inspected the OSDI theme-1
section at 390px; headings, subtheme text, and exercise content remain readable
without horizontal clipping. The remaining OSDI themes and all other routes
remain unfinished.

## OSDI stored-state placement theme review — 2026-09-22

Checked the second OSDI theme's placement footprints and hit-rate threshold.
With four useful 4-KiB pages inside four 64-KiB regions, retaining whole
regions plus four 64-byte entries costs 256.25 KiB; retaining only the pages
costs 16.25 KiB, so only the latter fits the stated 32-KiB budget. When every
page is useful, fine placement needs 64 metadata entries and totals 260 KiB,
while coarse placement totals 256.25 KiB: the advantage reverses when coverage
changes. For local-hit cost 3 μs and local-miss cost 12 μs versus always-remote
10 μs, half hits average 7.5 μs, and the mean only strictly improves when the
hit fraction exceeds 2/9. The exercise correctly warns that the mean does not
certify the 12-μs miss against a deadline. The learning checker now computes
the byte counts, both coverage cases, and strict break-even.

Replaced stale BlitzScale source links: FineMem now anchors allocation
granularity and wasted space, Okapi anchors the distinction between I/O layout
and redundancy grouping, and Tiered Memory Management Beyond Hotness anchors
placement based on performance contribution. These papers do not supply the
toy dimensions or hit-rate model. Retained the route's explicit warning that
Tigon's CXL setup is emulated, not a physical-CXL demonstration. Learning,
structural, and editorial checks pass. The course was rebuilt and the full
browser regression passed at 390px and 1280px for 161 anchors and 21 source
pages. I also captured and visually inspected the OSDI theme-2 section at
390px: heading, explanatory paragraph, subtheme label, and evidence-card text
wrap within the viewport without horizontal clipping. OSDI themes 3–8 and the
other conference routes remain unfinished.

## OSDI communication and consistency theme review — 2026-09-22

Checked the third OSDI theme's retry, recovery, and replica examples. One
execution of request R moves the counter from zero to one; retrying R as a
fresh operation moves it to two, as would a genuinely new request S. The text
correctly distinguishes these identities. It also identifies the recovery
hazard when the counter update and remembered request outcome survive a crash
inconsistently. In the replica example, returning zero after promising that an
acknowledged increment will be visible violates that promise; an interface
that explicitly permits staleness makes a different promise. Learning checks
now guard these cases and the distinction between a timed-out request and
proof that it did not execute.

Corrected two stale subtheme links: Picsou now anchors cross-cluster message
acknowledgements, with an explicit caveat that its message-receipt protocol is
not the toy counter's durable exactly-once transaction; Skybridge anchors
bounded staleness for distributed caches, not the route's invented counter
measurements. The partial-loading pipeline example remains bounded to
BlitzScale. The primary OSDI descriptions support Picsou's quorum-acknowledgment
mechanism and Skybridge's bounded-staleness target. Learning, structural, and
editorial checks pass. Focused mobile inspection at 390px found the theme
heading, explanation, subtheme label, and evidence card readable without
horizontal clipping. OSDI themes 4–8 and other conference routes remain
unfinished.

## ASPLOS interfaces and visible facts theme review — 2026-09-22

Started theme 1 by checking all three subtheme reading links against the ideas
the blocks actually teach. Replaced the unrelated CXL source for program/data
meaning and interface guarantees with Coach, which documents guaranteed and
oversubscribed resources, prediction, and contention monitoring. Replaced the
generic systems-coordination citation for compiler representations with
BlockDepend, while explicitly labeling its local evidence as abstract-only.
Kept the existing 12 MB reservation race and loop-carried dependency examples;
they remain original teaching examples rather than paper results.

Added learning checks for the source-to-subtheme mappings and evidence limits.
Learning, structural, editorial, and diff checks pass. Full browser regression
passes at 390px and 1280px for 161 anchors and 21 source pages. Manual inspection
of the 390px theme 1 view found the heading, definition, subtheme, and exercise
card readable without horizontal clipping. ASPLOS themes 2–8 and the remaining
conference routes and final course-wide source audit remain unfinished.

## OSDI allocation theme source review — 2026-09-22

Began the fourth theme by checking its reading leads against the official OSDI
paper pages. Replaced generic BlitzScale attribution for queueing with Kamino,
whose paper concerns latency- and cache-aware VM-allocation scheduling; the
queue order and deadlines remain explicitly original. The migration/loading
subtheme stays linked to BlitzScale, whose paper studies model-parameter
loading and live autoscaling, while separating those results from the toy
twelve-millisecond cost. The contention subtheme now points to the OSDI
straggler study and distinguishes its cluster-trace/what-if investigation,
and WLB-LLM's training-workload balancing, from the invented shared-resource
example. Learning checks now guard these source boundaries and compute the
move threshold, shared-user impact, eleven-unit crossover, and repeated-move
cost directly. Structural and editorial checks pass. Full-course browser
regression passes at 390px and 1280px for 161 anchors and 21 source pages. The
theme-4 mobile screenshot is readable at 390px with no horizontal clipping.
OSDI themes 5–8 and other conference routes remain unfinished.

## OSDI durability and recovery theme review — 2026-09-22

Reviewed the crash-state table in theme 5: when publication metadata points to
the new version, the new payload must also be durable; the table marks the
opposite state as forbidden. The four-millisecond payload confirmation plus
two-millisecond publication means a durable-success reply costs at least six
milliseconds in the stipulated sequential model. Expanded the lesson with a
separate three-replica example to make the safety/progress tradeoff visible:
two durable copies preserve an acknowledged update through one crash in this
crash-only, no-concurrent-write model, while requiring every copy can stall
writes during one outage. The prose warns that acknowledgements alone do not
define a complete protocol.

Replaced generic BlitzScale evidence notes with the relevant OSDI sources:
F2FSJ for ordered data/metadata journaling, Basilisk for automated safety
invariant proofs (not repair or liveness), and KRR for kernel-scoped record and
replay (not arbitrary remote application inputs). Kept the toy payload/index,
replica, and timing examples clearly separate from paper results. Learning,
structural, and editorial checks pass. Full browser regression passes at
390px and 1280px for 161 anchors and 21 source pages; the 390px theme screenshot
is readable without horizontal clipping. OSDI themes 7–8 and other conference
routes remain unfinished.

## OSDI permissions and evidence theme review — 2026-09-22

Reworked theme 6's labels and opening in plain language, and expanded its
examples to separate three different promises: which data a component may
read, which resources and calls it may use, and what exact build is running.
The mutable-name example now states the race between authorization and later
resolution; the one-thousand-by-one-megabyte example checks the memory scale.
Added a fourth evidence step based on OSDI's artifact-review criteria: public
availability, working/documented functionality, and independently reproduced
paper results are distinct checks and none identifies the build used by a
live service.

Corrected the old generic BlitzScale notes. Paralegal now anchors static
privacy-policy analysis, the Extension Interface Model anchors bounded plugin
capabilities, and OSDI's artifact-evaluation rules anchor the separate claims
about available, functional, and results-reproduced artifacts. The route marks
its toy authorization race and memory budget as teaching examples, not paper
results. Learning, structural, and editorial checks pass. Full browser
regression passes at 390px and 1280px for 161 anchors and 21 source pages; the
390px theme screenshot is readable without horizontal clipping. OSDI theme 8
and other conference routes remain unfinished.

## OSDI performance variation theme review — 2026-09-22

Reviewed theme 7's made-up latency distributions and retitled/rephrased the
section and subthemes in everyday language. The nine-at-2-ms/one-at-20-ms trace
has a 3.8-ms mean but one five-millisecond deadline miss; the steady 4-ms trace
has a 4-ms mean and no such miss. Changing from one cold start in ten to five
cold starts in ten changes the mean to 11 ms. The practice's mean-only limit is
exactly a cold-start fraction of at most 1/6; cold requests still violate an
individual five-ms deadline. A separate timer example asks the learner to
connect handler timing to the same request's queueing, startup, and response.

Replaced generic BlitzScale evidence with Tintin for hardware-counter
measurement uncertainty and Fork in the Road for cold-start workflow and
concurrency. The source notes explicitly keep the request-delay values and
timer-boundary example original. Kept Serial Performance Optimization as a
reading lead for its removal/replacement/reordering framework while stating
that it does not supply the exercise's timing values. Learning, structural,
and editorial checks pass. Full browser regression passes at 390px and 1280px
for 161 anchors and 21 source pages; the mobile theme screenshot is readable
without horizontal clipping. OSDI theme 8 and the broader unfinished conference
routes remain.

## OSDI end-to-end cost theme review — 2026-09-22

Completed theme 8's request-to-usable-result example and integrated exercise.
In the stated sequential toy model, 6 + 4 + 3 + 2 = 15 ms; halving only the
three-millisecond compute step yields 13.5 ms, not half the total. Removing the
six-millisecond startup gives 9 ms. An eight-watt worker left ready for ten
seconds uses 80 joules; assigning that shared idle energy evenly across 20
requests gives four joules each, while four requests give 20 joules each.
These are explicit accounting examples, not paper measurements; the allocation
is not the physical energy caused by any one request.

Replaced generic paper attribution with PipeThreader for software scheduling
around specialized GPU units, MettEagle for container behavior in its stated
microkernel/Linux setups, and BlitzScale for model loading and live serving
scale-up. The prose separates each paper's actual scope from the invented
timeline and energy values. The route exercise now makes learners trace an
input or update through work, data movement, sharing, checks, and the user-
reliable result; distinguish sequential work from overlap; count setup/shared
idle energy with a stated allocation rule; compare the paper's measured
boundary; identify missing evidence; and propose a falsifiable improvement.

Learning checks verify the arithmetic and source boundaries; structural and
editorial checks pass. Full browser regression passes at 390px and 1280px for
161 anchors and 21 source pages. Manual inspection of the 390px theme 8 view
found the heading, explanation, subtheme, and exercise card readable without
horizontal clipping. Other conference routes and the final course-wide source
and teaching audit remain unfinished.

## ASPLOS answer and cost theme review — 2026-09-22

Completed theme 2's distinction between preserving the required answer and
reducing the resources needed to produce it. Its invented scalar equation
shows why residual size alone does not state answer accuracy: for 0.01x = 1,
an answer of 99 has residual 0.01 but answer error 1. The stated 0.1 answer
tolerance therefore requires residual at most 0.001. The practice problem's
0.004 residual for 0.02x = 1 implies answer error 0.2 and fails its 0.1 limit;
residual at most 0.002 would suffice in the exact-arithmetic model. A separate
cost example includes progress-check overhead, so four iterations plus four
half-millisecond checks take 6 ms, not 4 ms.

Replaced the inherited CXL source attribution with Voyager for input-adaptive
graph rewrites (explicitly abstract-only), MVQ for its inspected pruning and
quantization/accuracy tradeoff (not a general stopping proof), and Past-Future
for request-output-history-based memory admission (including its short-window
stability and warm-up limits). The route reading distinguishes these methods
from one another and from DarwinGame's noisy-cloud tuning. Learning, structural,
editorial, and diff checks pass. Full browser regression passes at 390px and
1280px for 161 anchors and 21 source pages; the 390px theme 2 view is readable
without horizontal clipping. ASPLOS themes 3–8 and the remaining course-wide
conference, source, and teaching audit are unfinished.

## ASPLOS placement, layout, and communication theme review — 2026-09-22

Completed theme 3 after checking its examples against the paper records and
primary sources. Corrected a substantive error in the Instruction-Aware
Cooperative TLB and Cache paper record: its mechanism is not synchronized
eviction of the same instruction from both structures. The author-hosted full
paper describes prioritizing instruction translations in the shared last-level
TLB, which increases data page walks, then using a second-level cache policy to
address resulting page-table cache pressure. Its reported geometric-mean
improvements are 18.9% on 120 single-core workloads and 11.4% on 75 SMT
workloads; the record now marks this as a focused author-version review, with
no extracted local source-text file.

Theme notes now connect locality to that cross-level cost, data layout to
PUSHtap's competing row-oriented CPU and column-oriented in-memory consumers,
and communication overlap to Concerto's abstract-only claim. The reading text
also distinguishes CENT's near-memory inference tradeoffs and leaves
unavailable implementation details explicitly unverified. The invented
four-by-four transfer model remains labeled original: at six column reads and
two row reads, the original layout costs 26 transfers and the conversion path
22; with four of each, they cost 20 and 28. The first strictly winning column
read count is six under the stated no-retention and conversion-cost
assumptions.

Learning/arithmetic and paper-source checks, structural and editorial checks,
and diff validation pass. Full browser regression passes at 390px and 1280px
for 161 anchors and 21 source pages. Manual inspection of the 390px theme 3
view found the heading, explanation, subtheme, and evidence card readable
without horizontal clipping. ASPLOS themes 4–8 and the remaining conference
routes and final source/teaching audit remain unfinished.

## ASPLOS whole-computation mapping theme review — 2026-09-22

Completed theme 4's first pass. The lesson now teaches that assigning the main
arithmetic to an accelerator is not the same as mapping the whole job: inputs,
temporary state, unsupported operations, communication, and output checks still
belong in the path. The reading distinguishes Plaid's local dataflow groups and
global links, Micro Blossom's CPU/FPGA division, CENT's memory-side inference
path, and the separate safety claim in the CXL.cache formal model. It keeps
workload claims bounded: CENT's reported limits are compute-heavy prefill and
Llama 2 through 32K context; the CXL proof is a two-device model, not a general
hardware or liveness guarantee.

The invented filter exercise checks both cost and whether the result is still
correct. The exact near-data route is `3 + 10f` ms against a 12 ms baseline,
with a tie at `f = 0.9`; the preliminary-filter route is `5 + 10f` ms, with a
tie at `f = 0.7`. The practice stages total 9 ms, but dropping any true match
still breaks exact filtering. These are teaching assumptions, not paper results.

Learning arithmetic/source-boundary checks, course structure, editorial triage,
and scoped diff validation pass. Full browser regression passes at 390px and
1280px for 161 anchor positions and all 21 source pages. Manual inspection of
the 390px theme 4 screenshot found the heading, prose, and evidence card readable
without horizontal clipping. ASPLOS themes 5–8 and the course-wide conference,
source, and teaching audit remain unfinished. A repository-wide `git diff
--check` remains noisy because of trailing whitespace in unrelated files;
scoped checks on this work pass.

## ASPLOS scheduling and coordination theme review — 2026-09-22

Completed theme 5's first pass. The lesson distinguishes balancing completion
time from assigning equal numbers of tasks, and separates mutual exclusion,
group barriers, and pipeline overlap. Source notes now tie request grouping to
CoServe's known expert routes in circuit-board inspection, communication and
compute overlap to FSMoE's MoE training system, and key-range locks to
RANGE-BLOCKS' abstract-level description. Limits are recorded: CoServe's
dynamic-routing/general-workload applicability is unproven, FSMoE's results
are from clusters up to 48 GPUs, and the local RANGE-BLOCKS record is abstract
only.

The invented two-worker example gives 15 ms for an unbalanced schedule, 11 ms
for balanced placement, and 16 ms when that placement first requires a 5 ms
data exchange. The pipeline examples finish in 12, 15, and 18 ms as per-piece
handling increases, under their stated independent-stage assumptions. Learning
checks cover these values and source boundaries. Course structure and editorial
triage pass; browser regression passes at 390px and 1280px for 161 anchors and
all 21 source pages. The mobile theme 5 screenshot was inspected; the heading,
body, and first subtheme card are readable without horizontal clipping. ASPLOS
themes 6–8 and the remaining conference, evidence, and course-wide audits are
still open.

## ASPLOS full-run resource accounting theme review — 2026-09-22

Completed theme 6's first pass. The lesson now separates power (a rate), energy
(accumulated use over time), capacity (what fits), service rate (what finishes),
and cost per accepted result. It ties each distinction to a different ASPLOS
example: the fine-grained DVFS paper's power/performance measurements, Coach's
guaranteed versus oversubscribed VM memory and contention controls, and
Past-Future's SLA-bounded goodput. CENT is used to contrast tokens per joule
with tokens per dollar and to show why phase mix matters; these different
systems are not presented as a direct ranking.

The DVFS paper record was upgraded from abstract-only to a focused review of
the author-hosted full PDF. For its GPT-3 row at a 2% performance-loss target,
the paper reports 250.04 W over 11.29 s at baseline and 236.14 W over 11.47 s
under DVFS. Multiplying the rounded values gives about 2,823 J versus 2,709 J,
an estimated 4.05% decrease in SoC energy; the table itself reports average
power and iteration time, not that derived energy metric. The record preserves
that distinction and notes that DVFS tuning is limited to the AICore.

The invented service example keeps the whole 10-second run's energy in the
numerator and counts only correct, on-time results in the denominator. The
third design ties A at 20/3 J per accepted result but returns 84 results, below
the 85-result eligibility threshold. The capacity example likewise distinguishes
20 requests fitting in memory from only five meeting a 50 ms deadline on one
serial worker. Learning/source-boundary checks, structure, and editorial triage
pass. Browser regression passes at 390px and 1280px for 161 anchors and all 21
source pages; manual inspection of the mobile theme 6 view found the heading,
explanation, and first evidence card readable without horizontal clipping.
ASPLOS themes 7–8 and the wider conference, source, and teaching audit remain
unfinished.

## ASPLOS scoped-evidence theme review — 2026-09-22

Theme 7 now teaches the scope of a correctness or security claim through four
distinct examples. The CXL cache-coherence proof checks SWMR in a two-device,
one-location model, not liveness or every possible configuration. AutoPRAC's
June 2026 preprint reports a bounded-model counterexample to MOAT's periodic
counter-reset policy; the course states the model/implementation gap and does
not present this as a demonstrated commercial-DRAM attack. SMaCk's threat
example names its unprivileged sibling-SMT attacker and treats performance
counters as a detector rather than a universal prevention guarantee. PMVerify's
reported 26 examples are separated into one robust, 12 violations, and 13
unknown; the unknown outcomes remain unresolved.

The original checkpoint and timing examples remain explicitly identified as
teaching constructions. Paper records now include a focused PMVerify PDF review
and an AutoPRAC follow-up note for MOAT. Theme 7 checks cover source mapping,
scope language, and the unresolved-result distinction. The generated course
build, learning checks, structural checks, editorial triage, scoped diff/JSON
checks, and responsive-browser regression pass. The browser covers 390px and
1280px, 161 anchors, and all 21 source pages. A 390px screenshot inspection
found the title, opening explanation, and first teaching card readable without
horizontal clipping. ASPLOS theme 8 and the wider source/course audits remain
unfinished.

## ASPLOS changing-conditions theme review — 2026-09-22

Completed the first full pass of ASPLOS theme 8. The lesson now defines the
whole request path from arrival through admission, waiting, execution, and
accepted delivery; compares results only under a fixed workload and service
promise; and measures reaction time separately from backlog-clearing time.
Source notes now connect those questions to Past-Future's SLA-qualified goodput
and short-window output-length assumption, PUSHtap's concurrent CPU/PIM HTAP
workload, and Coach's forecast/monitor/reassign cycle. Their metrics are not
presented as comparable rankings, and the invented queue values are kept
separate from paper results.

The queue calculation is checked explicitly: under the stated fluid model, the
original shift creates 100 waiting requests by the time the extra worker is
ready, then needs 2.5 more seconds to clear them. For a two-second shift, the
original worker clears the 40-request backlog by time four, before the worker
could start at time five. Learning, structural, editorial, and browser checks
pass; responsive regression covers 390px and 1280px, 161 anchors, and all 21
source pages. The mobile theme 8 screenshot is readable without horizontal
clipping. All eight ASPLOS themes now have a first reviewed course pass; the
cross-conference source, depth, and end-to-end learning audit remains open.

## Current full browser regression — 2026-09-22

Rebuilt the current source into `course.html` and ran the full Playwright/Chromium
regression using the already-installed local browser libraries. At 390px and
1280px, all 175 course anchor targets cleared the sticky navigation without
document-wide horizontal overflow. The request-latency control changed its total
from 10 ms to the 8 ms fixed-stage floor and 16 ms at the high end using Home/End;
its visible label and live explanation remained available, and its card fit both
viewports. Keyboard checks also passed for the skip link,
contents, lesson exercises, route exercises and tables, paper exercises, capstone
notes and rubric, and source-page return menus. All 26 paper walkthroughs and
21 exported source pages were visited at both widths. Mobile screenshots of the
opening page, contents, Pimba walkthrough, and exercises, plus desktop exercise
content, were visually inspected; the observed views kept headings, text, and
controls readable without horizontal clipping. This is a responsive browser
regression and limited visual spot-check, not a full accessibility or cross-browser
review, nor evidence that course content or conference coverage is complete.

## Dependency and pipeline lesson review — 2026-09-22

The lesson now makes the ideal pipeline rule explicit: the first item pays the
sum of stage times, then each additional independent item completes at the slowest
stage's interval. The checked examples give 10, 15, 20, and 55 ms for 1, 2, 3,
and 10 items under the 2/5/3 ms stage model; after reducing the middle stage to
2 ms, the ten-item total is 34 ms. The finite-buffer example still distinguishes
back-pressure from dropping or storing work when the input cannot be paused.

The paper connection now separates OSDI 2025 WLB-LLM's workload balancing from
ASPLOS 2025 FSMoE's scheduling of independent communication and computation.
WLB-LLM's reported comparisons name Plain-4D, Fixed-4D, and static sharding
baselines. FSMoE's reported ranges name its Tutel/PipeMoE and DeepSpeed-MoE/Tutel
comparison groups. The papers' results are explicitly not compared or combined,
and are not course reproductions. These source details were checked against the
local primary-PDF review records and linked author/publisher sources.

Arithmetic, course structure, all paper boundaries, editorial triage, and the
full Playwright regression pass. At 390px and 1280px, the browser checks 175
course targets and all 21 source pages; screenshots of the lesson at both widths
were visually inspected. These checks do not establish independent learning or
complete course-wide source review.

## Memory and storage lesson review — 2026-09-22

The memory lesson now makes peak live footprint concrete: an explicitly
invented training-step example sums 6 GB of weights, 4 GB of intermediate
values, 6 GB of gradients, and 8 GB of optimizer state to 24 GB when all are
needed together. It explains that reuse can lower the peak when values do not
overlap in time. The APOLLO (MLSys 2025) example describes lower-memory
optimizer state and shared update scales, while preserving the paper's scope:
28 GB of AdamW state in its cited single-batch LLaMA-7B example and about 3×
throughput on eight A100-80GB GPUs with four-times-larger batches are reported
results, not measurements reproduced here. The lesson also distinguishes
volatile DRAM from persistent storage and does not equate writing an SSD with a
durability guarantee.

`python3 scripts/check_course_learning.py` checks the new teaching/example and
boundary language alongside the cache model. The structural, paper-walkthrough,
editorial, table, science, conference-coverage, and resizing checks passed. The
full Chromium regression passed at 390px and 1280px, with 175 anchor positions,
no document-wide horizontal overflow, keyboard interaction checks, and all 22
exported source pages visited. This is a responsive regression and scoped
lesson pass, not independent paper reproduction, comprehensive accessibility
testing, or completion of the cross-conference source review.

## Skipping work: three meanings of sparsity — 2026-09-22

Revised the lesson's conference synthesis using the primary MLSys 2025 papers
SparseTransX, Radius, and TASD/TASDER. It now distinguishes naturally sparse
graph operations that are reorganized without dropping small values; gradient
entries omitted from inter-GPU communication with accumulated leftovers
periodically sent back; and irregular sparse calculations represented as
hardware-supported structured patterns, where more terms reduce approximation
error but add work. The Radius description preserves its limitation: under
AdamW, delayed gradient corrections do not recreate the dense update history.
Reported performance is bounded to each evaluation: SparseTransX's graph
training, Radius's GPT-2.0B run on 64 A100 GPUs with Slingshot 11, and TASD's
sparse ResNet-34 test on an RTX 3080. The prose warns that these are different
workloads and not a head-to-head comparison.

The lesson now defines sparsity, gives a plain example of a knowledge-graph
fact, and explains the gradient and AdamW references where they first appear.
The learning checker covers both existing arithmetic (storage break-even,
fixed overhead, worker imbalance, and error bound) and new paper-evidence
boundaries. Learning, structural, paper-walkthrough, editorial, table, science,
coverage, and resizing checks passed. The full browser regression passed at
390px and 1280px across 175 anchors, with all 27 generated source pages visited
and no document-wide horizontal overflow. These remain implementation and
editorial checks, not full accessibility testing, paper reproduction, or
completion of the overall source review.

## Precision lesson: number choice meets execution — 2026-09-22

Expanded the number-representation lesson with source-linked MLSys 2025
examples. QServe makes the mechanism concrete: W4A8KV4, conversion overhead,
and accompanying GPU execution changes. Its reported 1.2× maximum serving
throughput for Llama-3-8B on A100 is explicitly tied to the TensorRT-LLM
comparison. MiLo shows a different trade: 3-bit weights, small factored
correction matrices, and a custom GPU routine; its reported 1.2× latency result
is tied to its tested MoE models, batch size above one, device, and MARLIN
baseline. The prose states these are not head-to-head results. It also corrects
the QServe 20–90% statement to “runtime overhead associated with” dequantizing
weights or partial sums; the paper does not say this is that share of total
runtime. Terms such as activations and factored correction arrays are explained
in the lesson prose.

The primary MLSys 2025 papers, course-local paper records, and existing QServe
walkthrough were checked. The learning arithmetic/boundary checker, all 26
paper walkthrough checks, editorial, table, science, coverage, resizing, and
structural checks pass. The built site has 16 lessons, 46 concepts, 1,245
links, and 24 source pages. The final responsive run covered 175 anchors and
all 24 source pages at 390px and 1280px, with no document-wide horizontal
overflow. This does not substitute for the still-open claim-by-claim audit of
all conference routes or the Propel learner pilot.

## Compiler transformations and Relax — 2026-09-22

Reviewed the compiler lesson's explanation of semantics-preserving changes to
an execution plan. The lesson works through array-map fusion and memory traffic,
the rounding caveat in floating-point reassociation, tiling, and when
optimization preparation cost pays off across repeated runs. It now adds Relax
(ASPLOS 2025) as a concrete example: retaining symbolic size relationships such
as n and 4n can give transformations useful information across a model graph
and lower-level loops. The source is linked to the author-hosted conference
paper; the lesson bounds reported performance and deployment claims to the
paper's tested models and targets. Its local paper note remains explicitly
abstract-derived, so this change does not represent a full local paper audit.

Structural, learning, paper-walkthrough, editorial, table, science,
conference-coverage, and resizing checks passed. The full Chromium regression
passed at 390px and 1280px, including all 28 source pages, 175 course targets,
keyboard navigation, exercise interaction, and overflow checks. Homepage and
source-page screenshots were visually inspected. The build contains 16 lessons,
46 concepts, 1,253 links, and 26 walkthroughs. These checks establish behavior
in the tested browser conditions; they do not establish full accessibility,
independent learning, or completion of the course-wide source review and Propel
pilot.

## Distributed work and checkpoint recovery — 2026-09-22

Replaced the lesson's generic reference to NSDI and SC research with two
source-grounded examples that expose different recovery costs. Checkmate
(NSDI 2026) copies already-moving data-parallel gradients to a CPU shadow
cluster, which applies updates to a model copy. The lesson states the exact
delivery, network, and extra-compute requirements and confines the reported
throughput claim to the evaluated setup. LLMTailor is explicitly identified as
SC Workshops '25 / PDSW '25, not a main-track SC paper. It assembles selected
layers and optimizer state from partial checkpoints; the lesson warns that a
loadable state need not reproduce the original training result and cites the
lower reported benchmark scores in its filtered Qwen2.5-7B fine-tuning case.
The paper evidence is linked directly and to local adjudication notes.

The learning checker now guards these distinctions. Structural, paper,
editorial, table, science, conference coverage, resizing, and learning checks
passed. The complete Chromium regression passed at 390px and 1280px over 175
course targets and all 30 source pages. It now also opens the distributed-work
exercise by keyboard and checks for horizontal overflow at both sizes. The
lesson screenshot at 390px was visually inspected. This is an implementation
and scoped source review, not a full accessibility audit, paper reproduction,
or completion of the course-wide source review or Propel pilot.

## Correctness promises, tests, and proofs — 2026-09-22

Rewrote the lesson's opening and examples to avoid abstract wording and explain
the necessary terms where they first appear. It now connects an explicit system
rule to three distinct kinds of evidence: tested runs, proof under stated
assumptions, and a search that may leave cases undecided. PMVerify (ASPLOS 2025)
and PoWER (OSDI 2025) anchor the discussion in persistent-memory recovery. The
PMVerify result is stated as 12 violating cases, one case satisfying its rule,
and 13 undecided among 26 analyzed examples; the prose warns that undecided is
not a pass. PoWER is described as proving two example systems under its stated
storage and damage assumptions. These are bounded paper results, not a claim
that either approach covers every failure.

During the source-page browser pass, the newly exported PMVerify note caused a
real 390px overflow because it contained a bare long PDF URL. I turned that
address into a link and verified the specific page now measures 390px wide at a
390px viewport. I also clarified the local note: the focused author-PDF review
exists, but its PDF was not imported into the local extracted-text corpus.

The learning, structural, paper, editorial, table, science, route-coverage, and
resizing checks pass. Full Chromium passes at 390px and 1280px across 175 course
targets and all 32 source pages, including keyboard operation of the revised
correctness exercise and overflow checks. Its 390px screenshot was visually
reviewed. This remains a focused review, not independent reproduction, a full
accessibility audit, or completion of the course-wide source review and Propel
pilot.

## Physical circuits, energy, and capture timing — 2026-09-22

Rewrote the physical-design lesson to explain electrical work before naming
its terms. Added MIT sources for switching energy and setup/hold timing,
expanded the OpenROAD sequence in everyday language, and checked the new
120 J versus 124 J teaching calculation with exact arithmetic. The example
explicitly assumes its execution times. MIT's Design Tradeoffs transcript
occasionally labels expressions containing frequency as energy; the course
keeps joules per task separate from watts and does not copy that unit error.

The build, learning checks, and structural checks pass: 16 lessons, 46 concepts,
1,264 course links, 32 source pages, and 26 paper walkthroughs. A focused
Playwright check passed at 390px and 1280px for the physical-design anchor,
document width, both MIT links, and opening the exercise with Enter.
Screenshots are in `/tmp/physical-lesson-review-6cgkqi21`; the mobile opening
was visually inspected. The full course browser regression was not rerun for
this prose-only change. The preceding correctness entry records that wider
check on its earlier build.

## NSDI state and observation theme — 2026-09-22

Expanded the controller explanation, added UNUM and PolicyCache mechanism
comparisons from their official USENIX abstracts, and replaced the first
theme's three loosely related FastServe source notes. The prose defines
controller, state description, embedding, and flow in context. Its new probe
example charges 6 ms and saves 1 ms per subsequent decision: six repay the
cost and seven yield a saving under the stated assumptions.

Build, learning, editorial, and structural checks pass. The structural count
is 1,266 course links with the same 16 lessons and 32 source pages. A focused
Playwright check passed at 390px and 1280px for the first NSDI theme's anchor,
document width, all three replacement subtheme links, and keyboard opening
of the explained answer. Screenshots are in `/tmp/nsdi-state-review-244iz8m5`;
the mobile opening was visually inspected. This is a focused browser check;
the full regression was not rerun for this content change.

## NSDI recovery theme — 2026-09-22

Expanded the recovery explanation and added bounded Checkmate, Fractal, and
PILOT summaries from official USENIX abstracts. Replaced three FastServe
references with recovery sources. The text distinguishes maintaining state,
repeating dependent work, and inspecting recovery actions. Its original
reserve arithmetic and command sequence are labeled as teaching examples.

Build, learning, editorial, and structural checks pass, with 1,269 course links,
16 lessons, 46 concepts, 32 source pages, and 26 walkthroughs. A focused
Playwright check passed at 390px and 1280px for the recovery theme's anchor,
document width, three replacement subtheme links, and keyboard opening of
the answer. The mobile screenshot was visually inspected; screenshots are
in `/tmp/nsdi-recovery-review-0fv09a3x`. The full browser regression was not
rerun for this prose change. This review does not establish complete paper
coverage or completion of the course-wide source review.

## NSDI unusually slow requests — 2026-09-22

Expanded the fourth theme with HydraServe and BLADE mechanism explanations
supported by their official abstracts. The prose separates worker readiness,
network competition during startup, and waiting for a wireless transmission
turn. Two subtheme citations now point to the relevant papers. Reported
results remain bounded to their different tasks and evaluation settings.

Build, learning, editorial, and structural checks pass: 1,271 links, 16 lessons,
46 concepts, 32 source pages, and 26 walkthroughs. Focused Playwright checks
passed at 390px and 1280px for the theme anchor, document width, replacement
source links, and opening the answer with Enter. No new visual inspection or
full browser regression was performed for this prose change.

## NSDI measurement, replay, and input checks — 2026-09-22

Expanded the seventh theme using the official USENIX abstracts for μView,
MirrorNet, and CrossCheck. The explanations and three replacement subtheme
notes distinguish recording a useful event, reproducing relevant conditions,
and checking controller inputs. The finite deployment observation and separate
simulation evidence in CrossCheck remain explicitly separated.

Build, learning, editorial, and structural checks pass: 1,274 links, 16 lessons,
46 concepts, 32 source pages, and 26 walkthroughs. Focused Playwright checks
passed at 390px and 1280px for the theme anchor, document width, all three
replacement source links, and opening the answer with Enter. No full browser
regression or new screenshot inspection was performed for this prose change.

## NSDI work across hardware boundaries — 2026-09-22

Expanded the fifth theme with HybridMesh and FENIX examples supported by
their official abstracts. Replaced three generic FastServe citations with
sources about gateway work and switch/FPGA rate matching. Defined the key
device and interface terms in context. The original overload example and
the existing exceptional-request calculations passed exact arithmetic checks.

Build, learning, editorial, structural, and scoped whitespace checks pass.
The build has 1,276 links, 16 lessons, 46 concepts, 32 source pages, and 26
walkthroughs. No browser checks were rerun for this text-only change; earlier
entries record the browser checks on their respective versions.

## NSDI stored state and usable capacity — 2026-09-22

Expanded theme three using official SYMI and ZipLLM abstracts. The prose
distinguishes state placement, update authority, and representation, and
defines optimizer state, deduplication, exclusive OR, and lossless compression.
Three subtheme citations now match those explanations. The original 40 GB
versus 13 GB example is explicitly separate from ZipLLM's measurements.

Build, learning, editorial, structural, and scoped whitespace checks pass.
Exact storage arithmetic and XOR reconstruction for all byte pairs passed.
The build has 1,278 links with the same 16 lessons, 46 concepts, 32 source pages,
and 26 walkthroughs. No browser regression was rerun for this prose change.

## NSDI reduced messages and valid reuse — 2026-09-22

Expanded theme nine with KDC and Cortex mechanism summaries from official
abstracts. Replaced three generic source notes and explained how prior
knowledge, reconstruction, and reuse judgment affect the accepted result.
The text makes no universal accuracy claim and does not reproduce the
malformed numerical cache-hit-rate wording in Cortex's web abstract.

Build, learning, editorial, structural, and scoped whitespace checks pass.
The sensor-summary examples were checked directly: equal averages conceal
different alarm results; equal maxima and positions conceal different counts.
The build has 1,280 links, 16 lessons, 46 concepts, 32 source pages, and 26
walkthroughs. No browser regression was rerun for this text-only change.

## NSDI scheduling and accumulated browser regression — 2026-09-22

Expanded the scheduling theme with FastServe and Libra mechanism summaries
from their official abstracts. It explains token boundaries, retained state,
cross-worker dependencies, batches, and distinct timing targets. Two subtheme
notes now use Libra for the relevant dependency and batching claims.

Build, learning, editorial, structural, and scoped whitespace checks pass.
The full Chromium regression passed on the current build at 390px and 1280px:
keyboard entry, contents, 175 anchor positions, document overflow, exercise
interaction, all 32 source pages, and return menus. This covers the accumulated
NSDI edits in the preceding entries. Diagnostic screenshots are in
`/tmp/conference-course-browser-mgmyza7r`; no new visual inspection is claimed.
The current build contains 1,282 links, 16 lessons, 46 concepts, and 26 paper
walkthroughs. Browser success does not establish completion of the course's
source review or learner evaluation.

## NSDI reading sequence and evidence notice — 2026-09-22

Rewrote the introduction to connect all ten themes through a request's path.
Updated the route status and evidence notice to reflect the selected abstract
reviews and the remaining work. Fixed six directional references: evidence
notes appear after the examples in generated HTML, so references to summaries
"below" were misleading. The replacement references name the theme directly.

Build, learning, venue coverage, editorial, and scoped whitespace checks pass.
No links, interactions, or section IDs changed. The preceding full browser
regression predates this text revision; it was not repeated for this change.

## Early-lesson prerequisites — 2026-09-22

Expanded the numbers opening with two-bit patterns, repeated doubling to
eight bits, and the definition of a byte. Defined decimal GB and time units
in the memory lesson, explained training-state terms before their worked
example, and defined the basic network parts before the topology calculation.
Removed the memory paragraph's tank-and-pipe analogy in favor of direct
statements about amount, rate, and dependent reads.

Build, learning, structural, and scoped whitespace checks pass. The build
retains 16 lessons, 46 concepts, 1,282 links, 32 source pages, and 26 walkthroughs.
The lesson order was inspected directly from the content module. No browser
regression was rerun for these prose edits.

## Dependency lesson paper comparison — 2026-09-22

Separated the dense WLB-LLM/FSMoE comparison into connected paragraphs that
explain each mechanism before its measurements. Defined the terms needed by
this second lesson and clarified the distinction between layer measurements
and complete-model experiments. Existing numbers, baseline names, and source
links are retained. Corrected "reduce the worker" to name the waiting time.

Build, learning, structural, and scoped whitespace checks pass. The existing
wording assertion was updated for that correction; no new mirrored prose
tests were added. Counts remain 16 lessons, 46 concepts, 1,282 links, 32 source
pages, and 26 walkthroughs. Browser checks were not repeated for this edit.

## Opening and learner guidance — 2026-09-22

Rewrote the introduction around the question of why faster components may not
shorten a request. Orientation now tells readers to predict, calculate, and
change an assumption. The starting delay check uses one missed deadline per
hundred requests and asks whether that meets the service target. Updated the
existing introduction wording assertion after it failed on the revised text.

Build, learning, structural, and scoped whitespace checks pass, with unchanged
component and link counts. The focused orientation/capstone browser option
passed at 390px and 1280px: seven anchors, keyboard answers, note entry, rubric,
and overflow. Screenshots are in `/tmp/conference-course-browser-o1_jtzar`;
the mobile orientation opening was visually inspected. This option does not
run the full course browser regression.

## Final challenge explanation example — 2026-09-22

Added an invented example inside the self-review rubric showing a reported
12-to-8 ms change, its 1.5× ratio, the effect of 20 ms preparation, and a
separate proposed test. Exact arithmetic confirms the five-use tie and six-use
saving. The text states reusable preparation and unchanged per-request times
as assumptions and tells readers to locate the corresponding facts in a real
paper. The challenge introduction now states the expected output directly.

Build, learning, structural, and scoped whitespace checks pass, with unchanged
counts. The focused browser option passed at 390px and 1280px for seven anchors,
keyboard answers, note entry, rubric opening, and document overflow.
Screenshots are in `/tmp/conference-course-browser-k_jxwnum`; no new screenshot
inspection or full course browser regression is claimed.

## Glossary examples — 2026-09-22

Expanded energy, latency, throughput, false-positive, and percentile entries
with compact examples. The percentile example explicitly uses nearest rank;
the false-positive example distinguishes ordinary events from all alerts.
Verified the arithmetic and indexing directly. Build, learning, structural,
and scoped whitespace checks pass. Counts and anchors are unchanged. No
browser regression was repeated for these definition edits.

## ISCA representation and lookup cost — 2026-09-22

Expanded the first ISCA theme with lookup preparation, reuse, and validity.
The author summary supplies the bounded LUT Tensor Core connection; a local
evaluation note is now exported as a source page. The tiny multiplication
table and six-use tie/seven-use saving are original and checked directly.

Build, learning, editorial, structural, and scoped whitespace checks pass:
1,284 links, 33 source pages, 16 lessons, 46 concepts, and 26 walkthroughs.
Focused Chromium checks passed at 390px and 1280px for the ISCA exercise's
keyboard interaction, course and new source-page widths, and source return
links. No full browser regression or screenshot inspection was performed.

## ISCA near-memory execution — 2026-09-22

Added a bounded NMP-PaK explanation using the university publication record
and local evaluation review. The theme distinguishes remaining CPU work,
scratchpad space, software-only comparisons, and modeled accelerator results.
Two subtheme notes now use near-memory sources instead of the LUT paper.

Build, learning, editorial, structural, and scoped whitespace checks pass:
1,286 links, 34 source pages, 16 lessons, 46 concepts, and 26 walkthroughs.
The new evaluation-note page passed document-width and return-link checks
at 390px and 1280px. No full course browser regression was rerun.

## ISCA scheduling prose — 2026-09-22

Rewrote the scheduling introduction and subthemes around input arrival,
shared hardware, and storage. Added the RSN mechanism and evaluation limits;
replaced two unrelated LUT references. The teaching timeline is explicitly
separate from paper measurements. Learning, editorial, coverage, and structural
checks passed before the final source-list addition; the final build and
structural check were rerun. Focused keyboard and document-width checks passed
at 390px and 1280px before that source-list addition. No full browser regression
or visual inspection was performed in this pass.

## ISCA shared connections — 2026-09-22

Expanded the network theme with plain-language definitions, a source-backed
DeepSeek deployment/proposal distinction, and a qualified measured comparison.
Two unrelated LUT citations were replaced. Build, learning, editorial-triage,
structural, and scoped whitespace checks pass. Counts: 1,289 links and 35
source pages. Focused Chromium checks pass at 390px and 1280px for theme 4's
keyboard exercise, course width, and rendered source links. The RSN source-note
page also passed width and return-link checks at both sizes. These checks do
not replace a full browser regression or visual inspection.

## ISCA preparation and unsupported work — 2026-09-22

Rewrote theme 5 to define compiler and input shape, explain safe reuse, and
distinguish expressing a program from executing it and making it faster.
Added the HPVM-HDC author paper and a separate whole-program transfer example.
Build, learning, editorial triage, and structure checks pass (1,290 links,
35 source pages). The teaching arithmetic was checked directly. Focused
Chromium checks cover the rendered example, keyboard exercise, document width,
and paper link at 390px and 1280px; no full regression or visual inspection.

## ISCA required behavior and approximation — 2026-09-22

Expanded theme 6 with DX100's compiler restrictions and a bounded HyFlexPIM
connection. Defined aliasing, indirect access, and digital versus analog
calculation in the explanation. Replaced two unrelated source notes and
separated tested model quality from a proved ranking under assumed error bounds.
Build, learning, editorial triage, and structure checks pass (1,292 links,
35 source pages). Decimal arithmetic checks cover reversal, preservation, and
the tie boundary. Focused Chromium checks at 390px and 1280px cover rendered
text, keyboard exercise, document width, and DX100 links. No full browser
regression or visual inspection was performed.

## FCCM reported cycles: focused source and reading review

FCCM follow-up source example (2026-09-22): checked the added table-II cycle
comparison at 390px and 1280px. Both full paragraphs were visually inspected in
`/tmp/fccm-cycle-reading-e06he1it/` and wrap within the reading column. The
source table fragment exists in the retrieved manuscript HTML. Build, learning
arithmetic, and editorial-heuristic checks passed. This focused pass does not
establish full-course visual or source accuracy.

## Expanded final exercise: focused browser review

After adding the cross-conference mechanism comparison to the final exercise,
the focused browser check passed at 390px and 1280px. It checked seven anchors,
keyboard answer controls, entry into the note fields, the expandable rubric,
and document overflow. Output: `/tmp/conference-course-browser-7w0k3yyg/`.

Narrow-width element screenshots were also captured for the design-evidence
comparison and the expanded final exercise in
`/tmp/course-reading-review-_jhxj_0o/`. The comparison text and links wrap within
the column. The final-exercise overview shows all six fields and the expanded
guide, but its very tall image is too reduced to establish fine text readability.
The sticky navigation appears inside the stitched comparison capture; this
capture alone does not establish a scrolling obstruction. These focused checks
do not complete the systematic visual review or replace the full regression.

Follow-up: inspected four normal-size viewport captures in
`/tmp/course-guide-views-bapahqft/`: the cross-conference connection and the
worked explanation, each at 390px and 1280px. The sampled paragraphs wrap
readably, and the two target headings are below the fixed navigation. These
views establish readability for the visible text, not the entire expanded
guide. Added direct links from the connection paragraph to the named LUT Tensor
Core and TRRIP walkthroughs so readers can inspect the examples being compared.
Rebuilt the page and checked both links by clicking them in Chromium at 390px
and 1280px; both reached their unique target, with no document overflow.
Structural checks passed for 1,348 course links and 52 source pages; the learning
calculation checks and scoped whitespace check also passed.

## ISSCC measured-condition limits — 2026-09-22

Theme 4 now explains missing duration/activity combinations, names the
digest's tested models and dataset, and preserves the one-paper review limit.
Build, learning, structural, toy combination coverage, and scoped whitespace
checks pass (1,320 links, 52 source pages). Focused Chromium checks passed
at 390px and 1280px for text, keyboard exercise, and document width. No full
browser regression or visual inspection was performed.

## ISSCC peak versus task energy — 2026-09-22

Theme 3 now explains operation-count conventions and identifies the digest's
peak operating point and prior-accelerator comparison assumptions. Checked
the local primary measurement passage. Build, learning, structural, energy/
operation arithmetic, and scoped whitespace checks pass (1,320 links,
52 source pages). Focused Chromium checks passed at 390px and 1280px for
text, keyboard exercise, and document width. No full browser regression or
visual inspection was performed.

## ISSCC storage lifetime and changed work — 2026-09-22

Theme 2 now connects ConvFormer reuse to last-reader constraints, explains
fusion through a neighboring-input example, and separates pruning from exact
storage reuse. Build, learning, structural, live-storage/neighbor arithmetic,
and scoped whitespace checks pass (1,320 links, 52 source pages). Focused
Chromium checks passed at 390px and 1280px for text, keyboard exercise, and
document width. No full browser regression or visual inspection was performed.

## ISSCC workload stages — 2026-09-22

Theme 1 now explains the ConvFormer digest's distinct storage, transfer,
and arithmetic problems. Corrected the local review's attention-reordering
description and aligned subtheme notes with the timing examples. Build,
learning, structural, stage/overlap arithmetic, and scoped whitespace checks
pass (1,320 links, 52 source pages). Focused Chromium checks passed at 390px
and 1280px for text, keyboard exercise, and width. No full browser regression
or visual inspection was performed.

## VLSID evidence synthesis — 2026-09-22

Theme 4 now summarizes the three reviewed records' evidence stages and
unresolved checks in a compact table. Build, learning, structural, exact
additive-error arithmetic, and scoped whitespace checks pass (1,320 links,
52 source pages). Focused Chromium checks passed at 390px and 1280px for
all three table rows, keyboard exercise, and document width. The editorial
pass does not establish full proceedings coverage or resolve the energy
discrepancy. No full browser regression or visual inspection was performed.

## VLSID device selection and mixed evidence — 2026-09-22

Theme 3 and its local QuaLITi review now distinguish simulated model accuracy,
real queue observations, and extrapolated inference waits. Checked primary
setup and queue-analysis passages. Build, learning, structural, completion/
queue/interval arithmetic, and scoped whitespace checks pass (1,320 links,
52 source pages). Focused Chromium checks passed at 390px and 1280px for
keyboard exercise, corrected source evidence, and course/source widths.
No full browser regression or visual inspection was performed.

## VLSID conversion and energy accounting — 2026-09-22

Rechecked the TimeFloats walkthrough against the August 2024 arXiv preprint.
The source's Table I and IV-B prose report different component values, and
the course keeps the resulting arithmetic discrepancy visible rather than
choosing a preferred total. Added an editorial regression check for the
preprint scope, modeled-evidence boundary, and conflicting energy figures.
Build and the focused editorial assertions passed; no new browser capture was
needed because the rendered wording did not change.

## ISCA Oaken source review — 2026-09-22

Checked the final author-hosted paper's online/offline thresholds, 4-/5-bit
groups, fused dense/sparse encoding, memory configurations, simulator-based
evaluation, synthesis-based area, and named baselines. Added an editorial
regression check ensuring the walkthrough does not merge the A100, vLLM, and
QServe throughput denominators or the FP16, KVQuant, and KIVI accuracy
references. No reader-facing wording changed, so no new browser capture was
needed.

## ISCA LUT Tensor Core source review — 2026-09-22

Checked the manuscript's table-precompute fusion, symmetry transformation,
bit-serial lookup, elongated tile reuse, LMMA/compiler path, and separate
hardware/kernel/model evaluation stages. Added an editorial regression check
for the manuscript scope and modeled-evidence boundary. No reader-facing
wording changed, so no new browser capture was needed.

## MICRO TRRIP source review — 2026-09-22

Checked the compiler-to-OS-to-cache handoff, the meaning of hot code, the
Sniper model and benchmark boundary, the fixed simulated instruction count,
and the omitted wrong-path behavior. Added an editorial regression check for
the prediction-versus-reservation distinction and the SRRIP/geomean evidence
boundary. No reader-facing wording changed, so no new browser capture was
needed.

## MICRO Pimba source review — 2026-09-22

Checked the generalized state update, two-bank shared processing unit, MX8
with stochastic rounding, GPU/PIM work split, dependency bubbles, named
throughput baselines, and Ramulator2/RTL evaluation boundary. Added an
editorial regression check for the maximum-versus-average denominators and
the modeled-device limit. No reader-facing wording changed, so no new browser
capture was needed.

## MICRO route coverage notice — 2026-09-22

The route notice now distinguishes its two full walkthroughs from the wider
20-record source-backed synthesis and the 103 abstract/title-only records.
Added an editorial regression check for those counts and evidence labels.
Build, structural, learning, and editorial checks passed. The narrow 390px
browser regression passed all anchor, exercise, source-page, keyboard, and
overflow checks; its general route screenshots were not a complete visual
review of every route notice.

## ISCA route coverage notice — 2026-09-22

The route notice now distinguishes its two full walkthroughs from the 17
source-backed papers, 95 abstract-level records, and 23 records without source
text. Added an editorial regression check for those counts and evidence labels.
Build, structural, learning, and editorial checks passed. The narrow 390px
browser regression passed all anchor, exercise, source-page, keyboard, and
overflow checks; this was not a complete visual review of every route notice.

## HPCA route coverage notice — 2026-09-22

The route notice now identifies one full LEGO walkthrough within seven
source-backed reviews across 121 records, and explains that the 4/108/110
acquisition counts overlap rather than forming a partition. Added an editorial
regression check for the non-additive inventory and evidence labels. Build,
structural, learning, and editorial checks passed. The narrow 390px browser
regression passed all anchor, exercise, source-page, keyboard, and overflow
checks; this was not a complete visual review of every route notice.

## SC route coverage notice — 2026-09-22

The route notice now distinguishes one full cuSZ-Hi walkthrough from the 119
text-backed records and the 314 abstract/title-only records in the reconciled
433-record inventory. The three failed PDF acquisitions remain described as
part of the abstract count. Added an editorial regression check. Build,
structural, learning, and editorial checks passed. The narrow 390px browser
regression passed all anchor, exercise, source-page, keyboard, and overflow
checks; this was not a complete visual review of every route notice.

## DAC and DATE route coverage notices — 2026-09-22

DAC now identifies GSIM as one full walkthrough within 32 source-backed
records; DATE identifies CorrectBench as one within 15. Both notices name the
remaining discovery-level population and preserve the no-independent-
reproduction boundary. Added editorial regression checks. Build, structural,
learning, and editorial checks passed. A narrow 390px browser regression
passed all anchor, exercise, source-page, keyboard, and overflow checks; this
was not a complete visual review of every route notice.

Theme 2 now explains TimeFloats' five-stage calculation path, modeled
conversion variability, and unresolved component-energy discrepancy. Added
the discrepancy to the local evaluation review after checking IV-B.
Build, learning, structural, exact energy/reuse arithmetic, and scoped
whitespace checks pass (1,320 links, 52 source pages). Focused Chromium
checks passed at 390px and 1280px for the rendered warning, keyboard
exercise, and document width. No full regression or visual inspection.

## VLSID representation sensitivity — 2026-09-22

Theme 1 now explains the duration/tolerance tradeoff and control-memory bit
effects, retaining the local review's simulator and occurrence-rate limits.
Build, learning, structural, exact duration/bit arithmetic, and scoped
whitespace checks pass (1,320 links, 52 source pages). Focused Chromium
checks passed at 390px and 1280px for keyboard exercise, course/source width,
and source return links. No full browser regression or visual inspection.

## DATE complete-job comparisons — 2026-09-22

Theme 8 now connects acceptance rules, partial delivery, timeout exclusions,
and precision exceptions across DATE, with a new batch-deadline explanation.
Build, learning, structural, batch/fallback arithmetic, and scoped whitespace
checks pass (1,319 links, 51 source pages). Focused Chromium checks passed
at 390px and 1280px for text, keyboard exercise, and document width. All
eight DATE themes have received this editorial pass, not a full-paper or
whole-course audit. No full browser regression or visual inspection.

## DATE detection and response — 2026-09-22

Theme 7 now connects EILID's protected return-state checks and target limits
to RTL-Breaker's distinct generation-time threat. Checked local EILID method
text and bounded evaluation notes. Build, learning, structural, exhaustive
single/double-bit toy patterns, retry arithmetic, and scoped whitespace checks
pass (1,319 links, 51 source pages). Focused Chromium checks passed at 390px
and 1280px for text, keyboard exercise, and document width. No full browser
regression or visual inspection was performed.

## DATE separated design search — 2026-09-22

Theme 6 now explains the CGRA paper's schedule-first mapping and hardware
restriction, plus the completed-comparisons-only runtime average. Corrected
stage order in the local source review after reading the primary paper.
Build, learning, structural, exhaustive toy design combinations, and scoped
whitespace checks pass (1,319 links, 51 source pages). Focused Chromium
checks passed at 390px and 1280px for keyboard exercise, corrected source
text, and course/source width. No full browser regression or visual inspection.

## DATE selective precision — 2026-09-22

Theme 5 now explains Cocktail's context-chunk precision, retained FP16
output/remainder values, and selection costs, checked against local method
text and evaluation notes. Build, learning, structural, exact precision/storage/
fallback arithmetic, and scoped whitespace checks pass (1,319 links,
51 source pages). Focused Chromium checks passed at 390px and 1280px for
text, keyboard exercise, course/source width, and source return links.
No full browser regression or visual inspection was performed.

## DATE checking generated tests — 2026-09-22

Theme 4 now explains CorrectBench's bounded repair process and exact Eval2
agreement rule, checked against local methodology and evaluation passages.
Replaced stale counter notes with queue-order checks. Build, learning,
structural, permutation/agreement arithmetic, and scoped whitespace checks
pass (1,318 links, 50 source pages). Focused Chromium checks passed at 390px
and 1280px for text, keyboard exercise, and document width. No full browser
regression or visual inspection was performed.

## DATE shared-memory observations — 2026-09-22

Theme 3 now connects the timing model to MC3's covert communication,
distinguishes cooperating senders from victim inference, and states the
transfer-splitting and no-borrowing assumptions behind the fixed-slot model.
Build, learning, structural, service-timeline arithmetic, and scoped whitespace
checks pass (1,318 links, 50 source pages). Focused Chromium checks passed
at 390px and 1280px for text, keyboard exercise, and document width.
No full browser regression or visual inspection was performed.

## DATE manufacturing and variation — 2026-09-22

Theme 2 now connects manufacturing-aware selection and variation testing
to BOSON-1. Checked local benchmark, sampling, and comparison passages;
the invented feature-size example is explicitly not a process specification.
Build, learning, structural, exact timing/candidate arithmetic, and scoped
whitespace checks pass (1,318 links, 50 source pages). Focused Chromium
checks passed at 390px and 1280px for text, keyboard exercise, and document
width. No full browser regression or visual inspection was performed.

## DATE dependencies and logical rewriting — 2026-09-22

Theme 1 now connects execution dependencies to the SAT-sampling paper,
with an explained inverter relation and separate existence/validity/diversity
requirements. Checked the local transformation passage and evaluation review.
Build, learning, structural, truth-table, distinguishing-input arithmetic,
and scoped whitespace checks pass (1,318 links, 50 source pages). Focused
Chromium checks passed at 390px and 1280px for keyboard exercise, course/source
width, and return links. No full browser regression or visual inspection.

## DAC physical implementation evidence — 2026-09-22

Theme 8 now links WISEDRAM circuit simulation and KLiNQ's measured-input
and implementation evidence, keeping each quantity's evidence stage separate.
Build, learning, structural coverage, link checks, timing arithmetic, and
scoped whitespace checks pass (1,317 links, 49 source pages). Focused
Chromium checks passed at 390px and 1280px for the keyboard exercise,
course/source width, and source return links. Coverage counts do not prove
teaching quality or full-paper review. No full browser regression or visual
inspection was performed.

## DAC prediction and design acceptance — 2026-09-22

Theme 7 now explains equal errors with different acceptance consequences,
distinguishes average error from a verified bound, and links LMM-IR's value
and high-drop detection evaluation. Checked local paper passages and review
limits. Build, learning, structural, exact error/search-budget arithmetic,
and scoped whitespace checks pass (1,316 links, 48 source pages). Focused
Chromium checks passed at 390px and 1280px for rendered examples, keyboard
exercise, and document width. No full browser regression or visual inspection.

## DAC observer access — 2026-09-22

Theme 6 now connects its timing model to DeepPUFSCA's measurement access
and GNNVault's visible/protected information split. Checked local paper
passages and evaluation notes; no attack or defense was independently run.
Build, learning, structural, random-delay probability, and scoped whitespace
checks pass (1,316 links, 48 source pages). Focused Chromium checks passed
at 390px and 1280px for paper connections, exercise table, keyboard operation,
and document width. No full browser regression or visual inspection.

## DAC energy accounting — 2026-09-22

Theme 5 now defines power and energy, adds fixed-window idle accounting,
and connects the choices to local EdgeMM and HH-PIM evidence. Replaced
unrelated GSIM subtheme citations. Build, learning, structural, energy
arithmetic, and scoped whitespace checks pass (1,316 links, 48 source pages).
Focused Chromium checks passed at 390px and 1280px for the table, new text,
keyboard exercise, and document width. No full browser regression or visual
inspection was performed.

## DAC accumulated and interacting errors — 2026-09-22

Theme 4 now explains error amplification, shrinking errors, and interactions
between changes, with local CLADO/SQ-DM paper and review connections.
Replaced unrelated simulator/carry notes. Build, learning, structural,
exact-decimal example arithmetic, and scoped whitespace checks pass
(1,316 links, 48 source pages). Focused Chromium checks passed at 390px
and 1280px for rendered examples, keyboard exercise, and document width.
No full browser regression or visual inspection was performed.

## DAC stopping points and deadlines — 2026-09-22

Theme 3 now connects DARIS stage boundaries and recent-duration estimates
with Tropical's answer-start and continuing-answer requirements. Checked
local paper passages and replaced unrelated simulator citations. Build,
learning, structural, switching/deadline arithmetic, and scoped whitespace
checks pass (1,316 links, 48 source pages). Focused Chromium checks passed
at 390px and 1280px for rendered text, keyboard exercise, and document width.
No full browser regression or visual inspection was performed.

## DAC data reuse and placement — 2026-09-22

Theme 2 now explains cache competition through CaMDN and placement across
memory-compute modules through HH-PIM, with modeled evidence explicitly
distinguished from fabricated-chip measurements. Build, learning, structural,
reuse arithmetic, and scoped whitespace checks pass. Focused Chromium checks
passed at 390px and 1280px for the keyboard exercise, course/source widths,
and return links in both added source pages. This is not a full browser
regression or visual inspection.

## SC overlap, device changes, and worker count — 2026-09-22

Themes 4–6 now distinguish asynchronous submission from completed transfers,
buffer availability, acceptable numerical answers, complete-job timing, and
fixed versus growing problems. Replaced generic subtheme citations with
AGILE and FFTMatvec/QuaTrEx reviews. Checked local paper passages for SC
Workshops attribution, QuaTrEx's excluded input/output, and FFTMatvec's
communication-delay limit. Build, learning, and structural checks pass
(1,312 links, 45 source pages). Focused Chromium checks passed at 390px
and 1280px for themes 4–5 and their added source page in the preceding
pass; this pass checked theme 6 text, keyboard exercise, and document
width. Exact arithmetic checks passed for the worker and exchange examples.
These checks do not constitute a full browser regression or visual inspection.

## SC answer checks and recovery — 2026-09-22

Theme 7 now distinguishes a detected disagreement from a proven compiler
bug, and saved work from an acceptable answer. Checked local LLM4FP
limitations and LLMTailor evaluation passages; retained the latter's
SC Workshops status and selected-training-case limits. Build, learning,
structural, and retry/recovery arithmetic checks pass (1,313 links,
45 source pages). Focused Chromium checks passed at 390px and 1280px for
rendered paper connections, keyboard exercise, course/source width, and
source return links. No full browser regression or visual inspection.

## SC measurement and simulation checks — 2026-09-22

Theme 8 now connects its plain-language measurement examples to MT4G and
CGSim, with a new example showing that an exact average can conceal wrong
individual predictions. Checked local paper passages and evaluation notes;
neither system was independently rerun. Corrected theme 1's stale compression
prompt to match its concentration example. Build, learning, structural, and
exact example arithmetic checks pass (1,313 links, 45 source pages).
Focused Chromium checks passed at 390px and 1280px for theme 8 text,
keyboard exercise, and document width. No full browser regression or visual
inspection was performed.

## ISCA evidence and complete-job comparisons — 2026-09-22

Expanded themes 7 and 8 using the existing RSN, Oaken, and NMP-PaK evaluation
reviews. The prose distinguishes measured timing, estimated power, scenario
ranges, and preparation tied to one model or input. Added the conversion-only
case to complete the four-way teaching comparison. Three subtheme citations
now point to relevant evaluation notes. Build, learning, editorial triage,
structure, and direct arithmetic checks pass; counts remain 1,292 links and
35 source pages. Focused Chromium checks passed for both themes' keyboard
exercises and document width at 390px and 1280px. No full regression or visual
inspection was performed.

## HPCA memory execution — 2026-09-22

Expanded theme 1 with MVE's multidimensional instruction idea, plain-language
cache/vector definitions, and an original eight-position/four-row example.
Replaced the two LEGO-only source notes with relevant MVE references and
exported the local HPCA evaluation review. Build, learning, and structural
checks pass (1,295 links, 36 source pages). Focused Chromium checks pass at
390px and 1280px for the keyboard exercise, course/source-page width, and
source return links. No full browser regression or visual inspection was run.

## HPCA compact values and skipped work — 2026-09-22

Expanded theme 2 with VQ-LLM codebook placement and EXION reuse/compaction,
using their publication abstracts and the existing local evaluation review.
Replaced two unrelated LEGO citations. Added a four-worker example that
separates operation count, completion time, and redistribution cost. Build,
learning, structural, and direct arithmetic checks pass (1,297 links,
36 source pages). Focused Chromium checks pass at 390px and 1280px for keyboard
exercise, document width, and rendered source links. No full regression or
visual inspection was performed.

## HPCA parallel work — 2026-09-22

Expanded theme 3 with a row-dependency example and LEGO's generated connections,
memory arrangement, and intermediate registers. Defined dataflow in context
and retained the CPU-communication exclusion from the local evaluation review.
Build, learning, and structural checks pass (1,298 links, 36 source pages).
Focused Chromium checks passed at 390px and 1280px for the keyboard exercise,
document width, and rendered evidence boundary. No full browser regression or
visual inspection was performed in this pass.

## HPCA resource control — 2026-09-22

Expanded theme 4 with DynamoLLM's combined controls and defined controller,
instance, clock frequency, and request trace. Added a longer-request example
with unchanged arrivals but reduced completion capacity. Two unrelated LEGO
references were replaced. Build, learning, structural, direct arithmetic, and
scoped whitespace checks pass (1,299 links, 36 source pages). Focused Chromium
checks passed at 390px and 1280px for the keyboard exercise, document width,
and relevant source links. No full regression or visual inspection was run.

## HPCA preparation and fallback — 2026-09-22

Expanded theme 5 with early fallback selection and the distinction between
unsupported execution, unavailable optimization, and untested configurations.
Replaced generic LEGO citations with the relevant VQ-LLM/EXION evaluation
review. Build and learning checks pass; direct arithmetic checks cover the
620/540 ms alternatives and strict supported-request threshold. Focused Chromium
checks passed at 390px and 1280px for the rendered example, keyboard exercise,
and document width. Scoped whitespace checks pass. No full browser regression
or visual inspection was performed.

## HPCA transitions, acceptance, and changed conditions — 2026-09-22

Expanded themes 6–8 using the existing evaluation review: MVE cache writeback,
IRIS measured versus modeled energy, DynamoLLM delivery timing and hardware
scope, Choco-Q validity versus quality, and VQ-LLM profiling conditions.
Six generic LEGO citations were replaced. Build, learning, structural, and
scoped whitespace checks pass; counts remain 1,299 links and 36 source pages.
Focused Chromium checks passed at 390px and 1280px for all three keyboard
exercises and document width. No full regression or visual inspection was run.

## MICRO remembered state — 2026-09-22

Expanded theme 1 with TRRIP's compiler-supplied code-use labels and original
stale-reservation and occupied-fetch-record examples. Removed the misleading
ownership framing from the TRRIP subtheme and separated replacement prediction
from shared-value validity. Build, learning, and structural checks pass
(1,301 links, 37 source pages). Focused Chromium checks cover the keyboard
exercise, course/source width, and source return links at 390px and 1280px.
No full browser regression or visual inspection was performed.

## MICRO movement and partial results — 2026-09-22

Expanded theme 2 with Pimba's shared near-memory update units and numerical
representation changes. Added an original result-identity example; replaced
two mismatched TRRIP citations. Build, learning, and structural checks pass
(1,302 links, 37 source pages). Focused Chromium checks passed at 390px and
1280px for the keyboard exercise, document width, result labels, and source
links. No full browser regression or visual inspection was performed.

## MICRO number formats — 2026-09-22

Expanded theme 3 with an original shared-scale rounding example and a bounded
MX+ mechanism explanation. Replaced two unrelated cuSZ-Hi references. Defined
exponent/significand in context and separated quality, software timing, and
modeled hardware evidence. Build, learning, structure, and direct rounding/
offset arithmetic checks pass (1,303 links, 37 source pages). Focused Chromium
checks passed at 390px and 1280px for keyboard exercise, width, and rendered
rounding example. No full regression or visual inspection was run.

## MICRO scheduling costs and event detail — 2026-09-22

Expanded theme 4 using the local Task-LP and OmniSim evaluation review.
Distinguished placement from balancing, precomputed server groupings from
placement hardware, and event-level storage waits from average rates.
Replaced two unrelated TRRIP references and exported the review source page.
Build, learning, structural, and scoped whitespace checks pass (1,304 links,
38 source pages). Focused Chromium checks pass at 390px and 1280px for keyboard
exercise, course/source width, and return links. No full browser regression
or visual inspection was performed.

## MICRO checked specialization — 2026-09-22

Expanded theme 5 with partial fast-path execution plus remainder handling,
RISSP's application-specific instruction support, and the separation of timing
prediction from behavior verification. Two unrelated TRRIP citations were
replaced. Build, learning, structural, and direct arithmetic checks pass;
counts remain 1,304 links and 38 source pages. Focused Chromium checks passed
at 390px and 1280px for keyboard exercise, width, and rendered remainder text.
No full browser regression or visual inspection was performed.

## MICRO task requirements and source wrapping — 2026-09-22

Expanded theme 6 with bounded ρHammer and RTGS explanations, plus an original
frame-rate/position-error acceptance example. Replaced unrelated citations.
Build, learning, structural, acceptance arithmetic, and scoped whitespace
checks pass (1,306 links, 39 source pages). The browser check found a real
narrow-screen overflow in a long slash-separated tool name on the new source
page. Source paragraphs and list items now permit wrapping within long words;
all source pages were regenerated. Rechecks passed for all 39 source pages'
document widths and return links at 390px and 1280px, plus theme 6's keyboard
exercise and course width. No full navigation regression or visual inspection
was performed.

## MICRO physical costs and experimental conclusions — 2026-09-22

Expanded themes 7/8 with ReGate's modeled power-control evidence and the
commercial compute-in-SRAM study's separate optimizations and mixed
measured/simulated retrieval result. Added an original idle-energy break-even
example; replaced four generic citations. Build, learning, structure, arithmetic,
and scoped whitespace checks pass (1,307 links, 40 source pages). Focused
Chromium checks passed at 390px and 1280px for both keyboard exercises,
course/source width, and source return links. No full navigation regression
or visual inspection was performed.

## SC accepted scientific results — 2026-09-22

Expanded theme 1 with a weighted-concentration example and local InferA and
SimAI-Bench evidence. Distinguished task completion, scientific interpretation,
transport benchmarking, and full workflow timing. Build, learning, structural,
and concentration arithmetic checks pass (1,309 links, 42 source pages).
Focused Chromium checks passed at 390px and 1280px for the keyboard exercise,
course/new-source widths, and return links. No full regression or visual
inspection was performed.

## SC communication and placement — 2026-09-22

Expanded theme 2 with cMPI, LCI, and D-CHAG connections from local evaluation
reviews. Distinguished shared access, asynchronous communication, and memory
distribution while preserving remaining copies, readiness, and aggregation.
Replaced unrelated compression references and exported two source reviews.
Build, learning, and structural checks pass (1,311 links, 44 source pages).
Focused Chromium checks passed at 390px and 1280px for keyboard exercise,
course/source width, and return links. No full regression or visual inspection.

## Full regression after foundational edits — 2026-09-22

The complete browser script passed at 390px and 1280px after the memory,
queueing, pipeline, omission-error, compiler, timing, correctness, and privacy
changes. It covers homepage keyboard entry, contents, 175 anchor positions,
exercise controls, conference practices, 26 walkthroughs, and 52 source pages
with return menus. Artifacts: `/tmp/conference-course-browser-kbvnfx5m/`.
Visually inspected the narrow latency control, VLSID evidence table, and source
return menu. All three sampled views were readable. The regression checks do
not establish factual accuracy or a complete visual/accessibility review.

## Compiler overlap and physical timing examples — 2026-09-22

Reviewed the overlapping-storage example, reverse traversal, hold-time failure,
and delay repair at 390px and 1280px. Captures are in
`/tmp/course-compiler-timing-review-rjvj76bq/`. The new paragraphs and numerical
arrays wrap within the reading column at normal reading size. At both widths,
the compiler and physical-design exercise answers open with keyboard Enter;
the page has no horizontal overflow. This review covers the added examples,
not the entire two lessons or a full navigation regression.

## Memory lesson: independent reads and exercise — 2026-09-22

Inspected the new independent-read calculation, its limiting assumptions, and
the expanded cache exercise at 390px and 1280px. Captures are in
`/tmp/course-memory-review-2m64pzyy/`. The calculation and answer wrap within
the reading column; the exercise opens with Enter and displays a visible focus
outline. Automated checks found no document overflow. This sample covers those
paragraphs and the exercise, not every part of the memory lesson or course.
A separate full structural-check attempt ended with exit 143 before producing
a result; it is not recorded as a pass. The focused browser check completed.

Follow-up: the checker reparsed the course document for each source return
link. It now caches parsed documents by resolved path within a run, retaining
all existing assertions. A fresh full check passed for 1,352 course links and
52 source pages in 0.86 seconds. Instrumentation confirmed one read per HTML
file. An in-memory broken return-link test was rejected as expected; no fixture
files were changed. This resolves the interrupted structural verification, not
the separate full-browser or editorial review requirements.

## Opening lesson: elapsed time and completion rate — 2026-09-22

Replaced the brief latency/throughput assertion with a worked schedule of ten
independent workers. Arithmetic checks verify completion times 10–39 ms and
the corresponding one-worker and ten-worker rates. Inspected both new
paragraphs at 390px and 1280px in
`/tmp/course-opening-workers-0bxrn8_n/`; text wraps readably and automated width
checks passed. Clarified the following paragraph's reference to the earlier
four-stage example. This is a focused reading review, not a full regression.

## SC compression and downstream error — 2026-09-22

Expanded theme 3 with cuSZ-Hi mode/quality boundaries, TurboFNO's combined
operations, and an original subtraction example in which allowed input errors
reverse the result's sign. Corrected the subtheme note to match that example.
Build and learning checks pass. Exact decimal arithmetic verifies the sign
and error calculation. Focused Chromium checks passed at 390px and 1280px
for keyboard exercise, document width, and rendered error example. No full
regression or visual inspection was performed.

## Small-sample route coverage notices — 2026-09-22

Added learner-facing evidence boundaries for VLSID, ISSCC, FCCM, and ICCAD.
The notices now distinguish the full TimeFloats, ConvFormer, Banked Memories,
and RSizing walkthroughs from the much larger discovery-level record sets and
from externally inspected manuscripts that were not part of the local PDF
inventory. They also preserve the no-independent-reproduction boundary.
Build, structural, learning, and editorial checks pass. A narrow Chromium
regression passed at 390px: 175 anchor positions, exercises, source pages,
keyboard interactions, and overflow checks. The screenshot set is
`/tmp/conference-course-browser-a8qmvhn4/`. This is a scope-clarity change,
not a claim of proceedings-wide review or complete visual inspection.

## MLSys route coverage notice — 2026-09-22

Clarified that the route has four focused learner walkthroughs—FlashInfer,
QServe, SOLA, and Photon—rather than leaving the walkthrough count implicit.
The evidence notice reconciles the local synthesis's 61 extracted-source
records with the catalog's 56 full-text entries and five additional
text-bearing acquisition records, and states that source availability is not
independent reproduction. Added an editorial regression assertion. This is a
coverage-boundary improvement; broader MLSys paper walkthroughs and full
claim-level review remain unfinished.

## MiLo walkthrough — 2026-09-22

Added a fifth focused MLSys walkthrough for MiLo. It teaches the complete
chain from three-bit quantization through low-rank error correction, adaptive
rank selection, offline optimization, fused dequantization, and the measured
A100 comparison. It labels all hand calculations as original teaching models,
keeps quality, memory, and latency as separate claims, and states that the
course has not reproduced the experiments. Build, structural, learning, and
editorial checks pass. The narrow Chromium regression then passed at 390px
with 176 anchor positions, 27 walkthroughs, 52 source pages, keyboard checks,
and no horizontal overflow. Screenshots are in
`/tmp/conference-course-browser-ap4ncxnq/`. This remains an automated narrow
viewport check, not a complete human visual review.

## MiLo rebuild regression — 2026-09-22

After rebuilding with the corrected EXIST source link and the MiLo walkthrough,
the complete local checks still pass: 16 lessons, 52 concepts, 1,376 course
links, 27 walkthroughs, and 52 source pages. Chromium at 390px passed 176
anchor positions, keyboard entry, exercises, source-page return menus, and
overflow checks. Screenshots are in
`/tmp/conference-course-browser-bl62wbuu/`.

## Mirage walkthrough regression — 2026-09-22

Added a fifth focused OSDI walkthrough for Mirage. It follows the path from
multi-level GPU graphs to search pruning, equivalence checking, generated CUDA,
preparation break-even, and measured benchmark limits. The complete local
checks pass with 16 lessons, 52 concepts, 1,393 links, 28 walkthroughs, and 52
source pages. Chromium at 390px passed 177 anchor positions, exercises,
keyboard interactions, source-page return menus, and overflow checks.
Screenshots are in `/tmp/conference-course-browser-va_6wa8t/`.

## Tigon walkthrough regression — 2026-09-22

Added a sixth focused OSDI walkthrough for Tigon. It follows the CAT working
set from local and CXL memory through coherence, transaction, logging, and
emulated-pod evaluation limits. The complete local checks pass with 16 lessons,
52 concepts, 1,410 links, 29 walkthroughs, and 52 source pages. Chromium at
390px passed 178 anchor positions, exercises, keyboard interactions,
source-page return menus, and overflow checks. Screenshots are in
`/tmp/conference-course-browser-m7qcsoa3/`.

## HydraServe walkthrough regression — 2026-09-22

Added a third focused NSDI walkthrough for HydraServe. It follows a cold start
from model fetch and runtime setup through overlap, temporary pipeline workers,
placement, consolidation, and user-facing SLOs. The complete local checks pass
with 16 lessons, 52 concepts, 1,427 links, 30 walkthroughs, and 52 source
pages. Chromium at 390px passed 179 anchor positions, exercises, keyboard
interactions, source-page return menus, and overflow checks. Screenshots are in
`/tmp/conference-course-browser-gll52d0w/`.

## DynamoLLM walkthrough regression — 2026-09-22

Added a second focused HPCA walkthrough for DynamoLLM. It follows the
request-specific prefill/decode distinction through latency promises,
energy-performance profiles, hierarchical control, reconfiguration overhead,
and the paper's cluster-level evaluation boundary. The complete local checks
pass with 16 lessons, 52 concepts, 1,445 links, 31 walkthroughs, and 52 source
pages. Chromium at 390px passed 180 anchor positions, exercises, keyboard
interactions, source-page return menus, and overflow checks. Screenshots are in
`/tmp/conference-course-browser-oyru59ej/`.

## VQ-LLM walkthrough regression — 2026-09-22

Added a third focused HPCA walkthrough for VQ-LLM. It follows vector
quantization from codebook lookup through hot-entry placement, occupancy and
bank conflicts, codebook-centered dataflow, register fusion, adaptive kernel
generation, and end-to-end inference evidence. The complete local checks pass
with 16 lessons, 52 concepts, 1,461 links, 32 walkthroughs, and 52 source
pages. Chromium at 390px passed 181 anchor positions, exercises, keyboard
interactions, source-page return menus, and overflow checks. Screenshots are in
`/tmp/conference-course-browser-j626bpej/`.

## EXION walkthrough regression — 2026-09-22

Added a fourth focused HPCA walkthrough for EXION. It follows diffusion
inference from repeated denoising through safe reuse, eager prediction,
output-sparsity compaction, hardware utilization, output-quality checks, and
the simulator/RTL/GPU evidence boundary. The complete local checks pass with
16 lessons, 52 concepts, 1,480 links, 33 walkthroughs, and 52 source pages.
Chromium at 390px passed 182 anchor positions, exercises, keyboard
interactions, source-page return menus, and overflow checks. Screenshots are in
`/tmp/conference-course-browser-7lyrkeib/`.

## IRIS walkthrough regression — 2026-09-22

Added a fifth focused HPCA walkthrough for IRIS. It follows region saliency
from ISP byproducts through mixed-resolution capture, backend tokenization and
localization stopping, task-specific quality, and measured-versus-modeled
system evidence. The complete local checks pass with 16 lessons, 52 concepts,
1,501 links, 34 walkthroughs, and 52 source pages. Chromium at 390px passed
183 anchor positions, exercises, keyboard interactions, source-page return
menus, and overflow checks. Screenshots are in
`/tmp/conference-course-browser-ii35axmi/`.

## Choco-Q walkthrough regression — 2026-09-22

Added a sixth focused HPCA walkthrough for Choco-Q. It follows constrained
optimization from legal versus optimal outputs through commute-Hamiltonian
constraint preservation, circuit serialization, equivalent decomposition,
variable elimination, and NISQ-scale evaluation. The complete local checks
pass with 16 lessons, 52 concepts, 1,520 links, 35 walkthroughs, and 52 source
pages. Chromium at 390px passed 184 anchor positions, exercises, keyboard
interactions, source-page return menus, and overflow checks. Screenshots are in
`/tmp/conference-course-browser-q8ot3txq/`.

## MVE walkthrough regression — 2026-09-22

Added a seventh focused HPCA walkthrough for MVE. It follows multidimensional
logical registers from strided and random movement through dimension-level
masking, compiler scheduling, cache-mode transitions, and measured-versus-
modeled evidence. The complete local checks pass with 16 lessons, 52 concepts,
1,539 links, 36 walkthroughs, and 52 source pages. Chromium at 390px passed
185 anchor positions, exercises, keyboard interactions, source-page return
menus, and overflow checks. Screenshots are in
`/tmp/conference-course-browser-931h9xds/`.

## Teola walkthrough regression — 2026-09-22

Added a fifth focused ASPLOS walkthrough for Teola. It follows an LLM
application from retrieval, embedding, and tool work through primitive-level
graphs, parallelization, pipelining, topology-aware batching, and end-to-end
latency evidence. The complete local checks pass with 16 lessons, 52 concepts,
1,557 links, 37 walkthroughs, and 52 source pages. Chromium at 390px passed
186 anchor positions, exercises, keyboard interactions, source-page return
menus, and overflow checks. Screenshots are in
`/tmp/conference-course-browser-lt8dk1kz/`.

## CIPHERMATCH walkthrough regression — 2026-09-22

Added a sixth focused ASPLOS walkthrough for CIPHERMATCH. It follows encrypted
data from representation expansion through packed addition-only matching,
near-data bit-serial addition in NAND flash, and the distinction between real
CPU results and modeled flash results. The complete local checks pass with 16
lessons, 52 concepts, 1,570 links, 38 walkthroughs, and 52 source pages.
Chromium at 390px passed 187 anchor positions, exercises, keyboard interactions,
source-page return menus, and overflow checks. Screenshots are in
`/tmp/conference-course-browser-dtpz_l5o/`.

## vAttention walkthrough regression — 2026-09-22

Added a seventh focused ASPLOS walkthrough for vAttention. It follows KV-cache
growth from physical-memory fragmentation through PagedAttention’s mapping and
kernel costs, then explains vAttention’s separation of contiguous virtual
addresses from on-demand physical pages and its phase-specific evaluation.
The complete local checks pass with 16 lessons, 52 concepts, 1,583 links, 39
walkthroughs, and 52 source pages. Chromium at 390px passed 188 anchor
positions, exercises, keyboard interactions, source-page return menus, and
overflow checks.

## COMET walkthrough regression — 2026-09-22

Added an eighth focused ASPLOS walkthrough for COMET. It follows outlier-aware
mixed precision from model-quality risk through mixed-format layout, conversion,
SM scheduling, and the distinction between kernel and serving measurements.
The complete local checks pass with 16 lessons, 52 concepts, 1,596 links, 40
walkthroughs, and 52 source pages. Chromium at 390px passed 189 anchor
positions, exercises, keyboard interactions, source-page return menus, and
overflow checks. Screenshots are in
`/tmp/conference-course-browser-yxm4lrsp/`.

## Micro Blossom walkthrough regression — 2026-09-22

Added a ninth focused ASPLOS walkthrough for Micro Blossom. It follows exact
decoding from the correction-ready boundary through heterogeneous CPU/FPGA
partitioning, graph-local conflict handling, stream decoding, and prototype
evidence. The complete local checks pass with 16 lessons, 52 concepts, 1,609
links, 41 walkthroughs, and 52 source pages. Chromium at 390px passed 190
anchor positions, exercises, keyboard interactions, source-page return menus,
and overflow checks. Screenshots are in
`/tmp/conference-course-browser-z07twqh4/`.

## PipeLLM walkthrough regression — 2026-09-22

Added a tenth focused ASPLOS walkthrough for PipeLLM. It follows confidential
GPU movement through speculative encryption, ordered-IV validation, recovery,
asynchronous decryption, bandwidth limits, and end-to-end evidence. The
complete local checks pass with 16 lessons, 52 concepts, 1,622 links, 42
walkthroughs, and 52 source pages. Chromium at 390px passed 191 anchor
positions, exercises, keyboard interactions, source-page return menus, and
overflow checks. Screenshots are in
`/tmp/conference-course-browser-znh9oji3/`.

## PartIR walkthrough regression — 2026-09-22

Added an eleventh focused ASPLOS walkthrough for PartIR. It follows sharding
intent from model-independent tactics through incremental IR rewrites, explicit
collectives, and the distinction between communication-count, runtime, and
compiler-time evidence. The complete local checks pass with 16 lessons, 52
concepts, 1,635 links, 43 walkthroughs, and 52 source pages. Chromium at 390px
passed 192 anchor positions, exercises, keyboard interactions, source-page
return menus, and overflow checks. Screenshots are in
`/tmp/conference-course-browser-ckkvhjov/`.

## TAPAS walkthrough regression — 2026-09-22

Added a twelfth focused ASPLOS walkthrough for TAPAS. It follows LLM-serving
control from phase-specific performance, temperature, and power behavior through
placement, routing, reconfiguration, emergency handling, and cluster evidence.
The complete local checks pass with 16 lessons, 52 concepts, 1,648 links, 44
walkthroughs, and 52 source pages. Chromium at 390px passed 193 anchor
positions, exercises, keyboard interactions, source-page return menus, and
overflow checks. Screenshots are in
`/tmp/conference-course-browser-r26yft6z/`.

## PCcheck walkthrough regression — 2026-09-22

Added a thirteenth focused ASPLOS walkthrough for PCcheck. It follows training
reliability from checkpoint interval and recomputation through concurrent
snapshots, pipelined persistence, coherent recovery points, storage capacity,
and goodput evidence. The complete local checks pass with 16 lessons, 52
concepts, 1,661 links, 45 walkthroughs, and 52 source pages. Chromium at 390px
passed 194 anchor positions, exercises, keyboard interactions, source-page
return menus, and overflow checks.

## Mint walkthrough regression — 2026-09-22

Added a fifteenth focused ASPLOS walkthrough for Mint. It follows distributed
tracing from keep-or-discard sampling through common/variable representation,
agent-side reduction, query fidelity, and end-to-end overhead evidence. The
complete local checks pass with 16 lessons, 52 concepts, 1,687 links, 47
walkthroughs, and 52 source pages. Chromium at 390px passed 196 anchor
positions, exercises, keyboard interactions, source-page return menus, and
overflow checks. Screenshots are in
`/tmp/conference-course-browser-urz9l0nu/`.

## PowerMove walkthrough regression — 2026-09-22

Added a sixteenth focused ASPLOS walkthrough for PowerMove. It follows
neutral-atom compilation from gate order through qubit placement, movement,
storage/computation zones, collective movement, fidelity, and separate execution
and compiler evidence. The complete local checks pass with 16 lessons, 52
concepts, 1,700 links, 48 walkthroughs, and 52 source pages. Chromium at 390px
passed 197 anchor positions, exercises, keyboard interactions, source-page
return menus, and overflow checks. Screenshots are in
`/tmp/conference-course-browser-bt0ql0d4/`.

## PUSHtap walkthrough regression — 2026-09-22

Added a seventeenth focused ASPLOS walkthrough for PUSHtap. It follows one
physical layout from row-oriented transactions through column-oriented PIM
scans, compact placement, device balancing, main/delta updates, snapshot
visibility, controller scheduling, and the paper’s bounded HTAP evaluation.
The complete local checks pass with 16 lessons, 52 concepts, 1,716 links, 49
walkthroughs, and 52 source pages. Chromium at 390px passed 198 anchor
positions, exercises, keyboard interactions, source-page return menus, and
overflow checks. Screenshots are in
`/tmp/conference-course-browser-ut3wluzb/`.

## CoServe walkthrough regression — 2026-09-22

Added an eighteenth focused ASPLOS walkthrough for CoServe. It follows
predictable expert dependencies from request grouping through eviction,
CPU/GPU allocation, profiling, service metrics, and the paper’s bounded
manufacturing-workload evaluation. The complete local checks pass with 16
lessons, 52 concepts, 1,734 links, 50 walkthroughs, and 52 source pages.
Chromium at 390px passed 199 anchor positions, exercises, keyboard
interactions, source-page return menus, and overflow checks. Screenshots are in
`/tmp/conference-course-browser-qn3drsj5/`.

## Fine-grained DVFS walkthrough regression — 2026-09-22

Added a nineteenth focused ASPLOS walkthrough for fine-grained DVFS. It
follows operator-level frequency choice from a slowdown budget through power,
elapsed time, derived energy, platform limits, and the paper’s Ascend-NPU
evaluation. The complete local checks pass with 16 lessons, 52 concepts,
1,750 links, 51 walkthroughs, and 52 source pages. Chromium at 390px passed
200 anchor positions, exercises, keyboard interactions, source-page return
menus, and overflow checks. Screenshots are in
`/tmp/conference-course-browser-_wb6jiig/`.

## BTrace walkthrough regression — 2026-09-22

Added a twentieth focused ASPLOS walkthrough for BTrace. It follows mobile
tracing from per-core buffer loss through coordinated capacity, completeness
versus recording latency, safe resizing, retained history, and the paper’s
smartphone evaluation. The complete local checks pass with 16 lessons, 52
concepts, 1,766 links, 52 walkthroughs, and 52 source pages. Chromium at
390px passed 201 anchor positions, exercises, keyboard interactions,
source-page return menus, and overflow checks. Screenshots are in
`/tmp/conference-course-browser-ekojwtgp/`.

## FCCM source-boundary regression — 2026-09-22

Expanded the FCCM route’s evidence notice for High Throughput Matrix
Transposition on HBM-Enabled FPGAs. The official accepted-paper list, program,
and DOI are now linked, while the route explicitly marks the full paper as
uninspected and keeps its mechanism at reading-lead status. The complete local
checks pass with 16 lessons, 52 concepts, 1,768 links, 52 walkthroughs, and
52 source pages. Chromium at 390px passed 201 anchor positions, exercises,
keyboard interactions, source-page return menus, and overflow checks.
Screenshots are in `/tmp/conference-course-browser-vqb8qcvv/`.

## DATE SAT-sampling walkthrough regression — 2026-09-22

Added a twenty-first focused walkthrough for DATE: High-Throughput SAT
Sampling. It follows satisfying assignments from probabilistic GPU search
through validity checks, duplicate removal, unique-valid throughput, and the
separate question of sampling uniformity. The complete local checks pass with
16 lessons, 52 concepts, 1,782 links, 53 walkthroughs, and 52 source pages.
Chromium at 390px passed 202 anchor positions, exercises, keyboard
interactions, source-page return menus, and overflow checks. Screenshots are in
`/tmp/conference-course-browser-r1bj3q_v/`.

## VLSID pulse-bit walkthrough regression — 2026-09-22

Added a twenty-second focused walkthrough for VLSID: representation-sensitive
bit flips in quantum-control memory. It follows a changed bit from numerical
representation through pulse behavior and output-distribution distance, then
separates simulator evidence from physical fault rates, invalid-pulse
interpolation, and detector assumptions. The complete local checks pass with
16 lessons, 52 concepts, 1,794 links, 54 walkthroughs, and 52 source pages.
Chromium at 390px passed 203 anchor positions, exercises, keyboard
interactions, source-page return menus, and overflow checks. Screenshots are in
`/tmp/conference-course-browser-m55sye77/`.

## Cascade walkthrough regression — 2026-09-22

Added a fourteenth focused ASPLOS walkthrough for Cascade. It follows temporal
graph training from event dependencies and memory freshness through topology-aware
batching, stabilized-node handling, adaptive updates, and accuracy/performance
evidence. The complete local checks pass with 16 lessons, 52 concepts, 1,674
links, 46 walkthroughs, and 52 source pages. Chromium at 390px passed 195
anchor positions, exercises, keyboard interactions, source-page return menus,
and overflow checks. Screenshots are in
`/tmp/conference-course-browser-84h84m9l/`.

## DAC DARIS walkthrough regression — 2026-09-22

Added a twenty-third focused walkthrough for DAC: DARIS deadline-aware GPU
scheduling. It follows capacity limits, spatial and temporal sharing, staged
priority changes, recent execution-time estimates, proportional virtual
deadlines, and the boundary between soft scheduling evidence and hard timing
guarantees. The complete local checks pass with 16 lessons, 52 concepts, 1,806
links, 55 walkthroughs, and 52 source pages. Chromium at 390px passed 204
anchor positions, exercises, keyboard interactions, source-page return menus,
and overflow checks. Screenshots are in
`/tmp/conference-course-browser-0ysznmqy/`.

## DAC CaMDN walkthrough regression — 2026-09-22

Added a twenty-fourth focused walkthrough for DAC: CaMDN’s cache-aware
multi-tenant NPU execution. It follows reuse distance, explicit cache
ownership, candidate mappings, dynamic allocation, fallback behavior, and the
boundary between modeled results and fabricated-hardware evidence. The
complete local checks pass with 16 lessons, 52 concepts, 1,818 links, 56
walkthroughs, and 52 source pages. Chromium at 390px passed 205 anchor
positions, exercises, keyboard interactions, source-page return menus, and
overflow checks. Screenshots are in
`/tmp/conference-course-browser-ra2nx0hj/`.

## DAC Tropical walkthrough regression — 2026-09-22

Added a twenty-fifth focused walkthrough for DAC: Tropical’s SLO-aware
prefill/decode multiplexing. It follows TTFT and TPOT as separate promises,
the queue/interference tradeoff, slack budgeting, joint SLO attainment, and
the boundary between the paper’s serving measurements and a universal claim.
The complete local checks pass with 16 lessons, 52 concepts, 1,830 links, 57
walkthroughs, and 52 source pages. Chromium at 390px passed 206 anchor
positions, exercises, keyboard interactions, source-page return menus, and
overflow checks. Screenshots are in
`/tmp/conference-course-browser-tp13j0hi/`.

## Glossary expansion regression — 2026-09-22

Added seven learner-facing definitions for cache ownership, decode, prefill,
slack, TTFT, TPOT, and virtual deadlines. Each definition uses plain language,
names its boundary, and links to the relevant lesson. The complete local checks
pass with 16 lessons, 59 concepts, 1,844 links, 57 walkthroughs, and 52 source
pages. Chromium at 390px passed keyboard entry, contents, 206 anchor positions,
exercises, source-page return menus, and overflow checks. Screenshots are in
`/tmp/conference-course-browser-em2z2d3l/`.

## DAC prose tightening regression — 2026-09-22

Reworded the DAC route to replace broad claims with named quantities: signal
calculations, reusable cache copies, first-token delay, token-gap delay, and
coordination cost. The complete local checks pass with 16 lessons, 59 concepts,
1,844 links, 57 walkthroughs, and 52 source pages. Chromium at 390px passed
keyboard entry, contents, 206 anchor positions, exercises, source-page return
menus, and overflow checks. Screenshots are in
`/tmp/conference-course-browser-nubujyeo/`.

## Desktop regression after source/prose updates — 2026-09-22

The full Chromium regression was rerun at 1280px after the university-hosted
DVFS source replacement and DAC prose tightening. It passed 206 anchor
positions, exercises, keyboard interactions, 52 source pages and return menus,
and overflow checks. The matching narrow run passed at 390px. Screenshots are
in `/tmp/conference-course-browser-v5a8dbgj/`.

## DAC VersaSlot walkthrough regression — 2026-09-22

Added the 26th focused DAC walkthrough: VersaSlot’s FPGA sharing system. It
follows partial-reconfiguration contention, Big and Little slots, dependency-
safe overlap, dual-core scheduling, live migration, and migration break-even.
The complete local checks pass with 16 lessons, 59 concepts, 1,856 links, 58
walkthroughs, and 52 source pages. Chromium at 390px passed 207 anchor
positions, exercises, keyboard interactions, source-page return menus, and
overflow checks. Screenshots are in
`/tmp/conference-course-browser-hcqwnlko/`.

## Desktop regression after VersaSlot — 2026-09-22

The full Chromium regression was rerun at 1280px after the VersaSlot
walkthrough was added. The run passed 207 anchor positions, keyboard entry,
contents navigation, exercises, theme practices, source-page return menus,
and document-width checks. Screenshots are in
`/tmp/conference-course-browser-jrdwqunx/`. Together with the current 390px
run above, this establishes the automated local browser checks at both target
widths; it is not a substitute for a full visual and cross-browser review.
