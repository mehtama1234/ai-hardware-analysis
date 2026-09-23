"""Shared homepage course entry; keep independent of corpus-generation scripts."""

COURSE_ENTRY = '''<!-- course-entry:start -->
<section id="course-entry" aria-labelledby="course-entry-title">
  <h2 id="course-entry-title">Learn how computer systems produce results</h2>
  <p>A guided course from work, waiting, and memory to coordination, physical limits, and correctness. Follow worked examples, try exercises with explained answers, then compare research across conferences.</p>
  <p>Start with basic arithmetic; technical terms are explained as they appear. You can read the lessons in order or follow a question through several conference routes.</p>
  <ul>
    <li><a href="course.html#course-orientation">Check what you know and choose a starting point</a> — five ungraded questions link to the relevant lessons.</li>
    <li><a href="course.html#s1">Start the first lesson</a> — follow one request from arrival to answer.</li>
    <li><a href="course.html#cross-conference-questions">Compare ideas across conferences</a> — trace waiting, representation, permissions, and evidence.</li>
    <li><a href="course.html#paper-walkthroughs">Work through a paper</a> — separate its mechanism and evidence from original teaching examples.</li>
    <li><a href="course.html#final-paper-challenge">Try the final paper challenge</a> — audit a paper beyond the guided examples.</li>
    <li><a href="course.html#conference-routes">Check conference coverage</a> — see what is drafted and what remains unfinished.</li>
  </ul>
  <p class="course-status">In development. Includes 2025 conference routes and NSDI 2026; paper coverage and source review are not complete. This tutorial has its own scope, distinct from the older narrative below.</p>
</section>
<!-- course-entry:end -->'''

COURSE_ENTRY_CSS = '''
/* course-entry:styles:start */
#course-entry{margin:28px 0;padding:24px;border:1px solid var(--teal);border-radius:10px;background:var(--g1)}
#course-entry h2{font-size:1.7rem;line-height:1.25;margin:0 0 16px;color:var(--ink)}
#course-entry p{margin:12px 0;color:var(--ink2)}
#course-entry ul{padding-left:22px;margin:14px 0}
#course-entry li{padding:6px 0;color:var(--ink2)}
#course-entry a{color:var(--teal);text-decoration:underline;overflow-wrap:anywhere}
#course-entry a:focus-visible{outline:3px solid var(--orange);outline-offset:4px}
#course-entry .course-status{font-family:var(--sans);font-size:.9rem;color:var(--ink2)}
/* course-entry:styles:end */
'''
