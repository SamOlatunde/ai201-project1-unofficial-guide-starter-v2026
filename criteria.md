# Acceptance criteria — The Unofficial Guide

Five criteria that say what "working" means for this system, written in unit 1
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"Retrieval works"* is an opinion. *"For at
least 4 of my 5 test questions, the top results include a chunk containing the
answer"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter or looser one. A reason that says something about your corpus or your
pipeline earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## 1. Retrieved chunks contain the answer

For at least 4 of my 5 test questions, the retrieved chunks include one that
contains the answer.

**Why this target:**

Four of my five questions map to exactly one dedicated document with
distinctive topic vocabulary (dining dollars, grade appeals, meal plan
changes, counselling wait time), so a single close semantic match should be
enough. The laundry question is actually the *easiest* of the five, not the
hardest — the same "Tuesday or Wednesday morning" tip is repeated
near-verbatim across all seven housing `_laundry.txt` files, so there's no
single point of failure there. My money for the one miss is on the
grade-appeal question: I asked about appealing to "the department chair," but
`admin_grade_appeals.txt` only ever says "the department" and never uses the
word "chair" — the least shared vocabulary of my five questions.

---

## 2. Every answer names a source

Every answer the system produces names at least one source document.

**Why this target:**

This is a plumbing check, not a content check, so I'm setting it strict at 5
of 5. `GROUNDING_INSTRUCTION` in generate.py explicitly tells the model to
name the filename it used, and the gate has already filtered out anything
that didn't pass `THRESHOLD` before generation ever runs — so every answer
that reaches the model has real chunks with real source labels behind it. A
miss here would mean the citation instruction itself is broken, not that a
fact was wrong (that's what criterion 5 checks instead).

---

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate
stops it and the system returns "I don't have enough information about that" —
in at least 4 of 5 tries.

<!-- The five questions are the ones in `OUT_OF_SCOPE` at the bottom of
     `questions.py`, and `run_eval.py` puts them through the gate and writes
     what happened into your run log. Swap them for your own if you'd rather —
     just keep five of them, or the "4 of 5" above has nothing to be 4 of. -->

**Why this target:**
<!-- TODO once you've run Milestone 4: run `python app.py retrieve "..."` for
     all 5 QUESTIONS and all 5 OUT_OF_SCOPE questions, note the best distance
     each time, and describe what you actually saw — e.g. "in-corpus
     distances clustered under 0.4, OUT_OF_SCOPE clustered above 0.8, a clean
     gap with THRESHOLD=0.6 sitting in the middle" or "the gap wasn't clean,
     [question] landed at 0.63, right where OUT_OF_SCOPE questions also
     landed, so a miss there is expected." Don't fill this with a number you
     haven't actually measured. -->

---

## 4. Something about your chunks

At least 4 of 5 sampled chunks begin with the source document's own title
line.

**Why this target:**

Several groups of documents in my corpus have near-identical bodies — the
seven housing `_laundry.txt` files all give the same coin prices and the same
"Tuesday or Wednesday morning" tip, and the dining halls' `_followup.txt`
posts restate the same wait-time figures as their main entry. The title line
("Laundry in Old Brewhouse", "Re: Kestrel Commons") is often the only text
that says *which* building or hall a chunk is actually about. If a chunking
strategy split on paragraph breaks or a fixed character window without
preserving that first line, a chunk could read as generically true but be
silently unattributable — or worse, misattributed once retrieved next to a
different document's title.

---

## 5. Your choice

For all 5 in-corpus test questions, the fact stated in the answer is actually present in the document it names (checked by opening that file and finding it).



**Why this target:**

Criterion 2 only checks that *some* filename gets named — it can't catch a
hallucination, because `TOP_K=5` always hands the model five labeled
excerpts, and the model could name a real file that doesn't actually support
the claim it made. This criterion is the one that checks accuracy of
attribution, not just its presence.

<!-- FLAG: the target above says "all 5," but the laundry question doesn't
     have one right answer to attribute — all seven housing buildings' laundry
     files say the identical thing, so "the" correct source for that question
     is ambiguous by design, not a pipeline bug. If you want the target to
     survive contact with that question, either drop to "4 of 5" and name the
     laundry question as the expected exception, or reword the target to allow
     any one of the matching files to count as correct for that question. -->

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 2 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 1. Retrieved chunks contain the answer

         For at least 4 of my 5 test questions, the retrieved chunks include
         one that contains the answer.

         **Why this target:** ...

         > **Revised in unit 2:** For at least 4 of 5 questions, the top three
         > results contain the answer.
         >
         > **Why revised:** I couldn't judge "the chunks include one that
         > contains the answer" the same way twice — I scored two questions
         > differently on Monday than on Wednesday. The new version is
         > something I can actually check.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said 4 of 5 but got 2 of 5, so 2 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.

     The whole reason the originals stay visible is so someone can see what you
     said before you knew the answer.
     ───────────────────────────────────────────────────────────────────────── -->
