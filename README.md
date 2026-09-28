# The Unofficial Guide

**Name:** Samuel Olatunde | **Corpus:** campus_life


# Unit 1

## What This Does

This is a retrieval-augmented Q&A system built on the `campus_life` corpus — eighty-eight short posts about student life at a university, covering dining halls, dorms, courses, and administrative rules that aren't written down anywhere official. It answers specific, factual questions a student would ask another student rather than look up themselves, like whether dining dollars roll over between semesters, how to appeal a grade, and when laundry rooms are least crowded. Because most of these documents pack their useful information into a single sentence, the system leans on retrieving a small number of tightly relevant chunks rather than large ones. See `questions.py` for the full set of test questions it's built to answer.

## Chunking Strategy

**Chunk size:** 300
**Overlap:** 50

Every document in this corpus is between 183 and 554 characters — a title
line, then one to three short paragraphs. At the starter's default of 800/120,
nothing ever splits: 88 documents in, 88 chunks out. That's not chunking, it's
just relabeling whole files, so I dropped the size until documents actually
started splitting.

I tried a few size/overlap pairs against a handful of representative
documents (shortest, longest, a couple of mid-length ones) and counted two
things: chunks that cut through the middle of a word, and chunks left over at
the end of a document that were basically nothing (a few leftover characters,
like `"ail."` off the tail of "email."). 300/50 gave the fewest mid-word cuts
of the sizes that still split the longer documents.

That didn't get rid of the tiny leftover chunks, though — across the whole
corpus, 16 of 161 chunks came out under 30 characters. My first instinct was
to fix that by raising the overlap, but sweeping overlap from 50 up to 200
made it *worse*: more overlap means more chunk boundaries per document, and
each boundary is still just a raw character index with no idea where a word
ends, so mid-word cuts went from 43 up to 137 while the tiny-chunk count
bounced around without ever approaching zero. Overlap controls how often a
cut happens, not where it lands, so it was never going to fix this.

The actual fix was in `split_documents`, not in the numbers: any trailing
piece under 40 characters gets merged into the previous chunk instead of kept
standalone. Since 40 is smaller than the 50-character overlap, that leftover
piece is guaranteed to already be inside the previous chunk's tail — `"ail."`
is literally the end of the `"fail."` the previous chunk already has — so the
merge checks for that containment and drops the fragment rather than
duplicating it. That took the whole corpus from 16 tiny chunks to 0, and
`admin_library_holds.txt` — one of the worst offenders — went from 2 chunks
(one of them just `"ail."`) to 1 clean 300-character chunk.

Known trade-off I kept rather than fixed: this is still raw character
windowing, so it pays no attention to sentence or paragraph structure, and any
document that does split loses its title line on every chunk after the first
— the title only ever appears at the very start of the raw text. A strategy
that split on paragraph breaks and re-prepended the title to each piece would
avoid both problems; I chose the simpler tuning-plus-tail-merge approach
instead of rewriting the splitting logic from scratch.

## Sample Chunks

<!-- Five chunks, pasted as text. Label each one and name the file it came from
     AND the function that produced it — the grader checks your code against
     what you claim here.

     `python app.py chunks -n 5` prints all three for you. Copy them straight
     across.

     Milestone 3. -->

**Chunk 1** — source: `admin_add_drop_deadline.txt#0` — produced by: `chunker.py::split_documents`

```
On the add/drop deadline

You can add a course through the end of the second week. Dropping is a longer window — through the end of week six — but a drop after week two shows as a W on your transcript. Nothing anywhere on the registrar's site says this plainly, and students find out from each other.
```

**Chunk 2** — source: `course_cs_210_exams.txt#0` — produced by: `chunker.py::split_documents`

```
CS 210 Data Structures — assessment

Two midterms and a final, all drawn from lecture material rather than the textbook. Midterms are curved, the final is not.

Do the labs even though they're only 10% — the exams reuse the lab problems.
```

**Chunk 3** — source: `course_stat_150_exams.txt#0` — produced by: `chunker.py::split_documents`

```
STAT 150 Applied Statistics — assessment

Three equally weighted midterms, no final. No curve, but the lowest midterm is dropped.

The dropped midterm makes the first one low-stakes; use it to learn the format.
```

**Chunk 4** — source: `dining_verrill_street_grill_followup.txt#0` — produced by: `chunker.py::split_documents`

```
Re: Verrill Street Grill

Adding to what people have said about Verrill Street Grill. The wait figure of up to 30 minutes on Friday evenings matches what I've seen. If you're trying to eat between classes, gobefore 11:45 and it's a different building entirely.

Also worth saying: one register, so t
```

**Chunk 5** — source: `housing_morrow_house_laundry.txt#1` — produced by: `chunker.py::split_documents`

```
Wednesday morning. Sunday after 6pm you will wait.
```

## Sample Answer

<!-- One complete question and answer, pasted as text, with the source line
     visible. Milestone 4. -->

**Question:** Can I upgrage my meal plan tier for free?

**Answer:** No, upgrading your meal plan tier bills you immediately. 

**Source:** admin_meal_plan_changes.txt

**Sources retrieved:** admin_meal_plan_changes.txt, dining_halden_hall.txt, dining_north_kitchen.txt, dining_the_atrium.txt, dining_the_ridgeway_cafe.txt


**My relevance cutoff:** I set my relevance cut off to 0.6 becuase my last question was 0.45 but the source asa still correct, at the same time I didn't want to place the score too high, so I think 0.6 is a reasonable cutoff, especially for harder question.

<!-- The number you set in config.py, and how you got there.

     You ran five questions your corpus covers and the five in OUT_OF_SCOPE
     that it clearly doesn't, and wrote down the best distance for each. What
     did those two groups look like? Where was the gap? Put the actual numbers
     here — the table below wants all ten rows.

     Milestone 4. -->
     

| Question | In corpus? | Best distance |
|---|---|---|
| Does my dining dollars roll over from spring to the following autumn sememsters? | Yes | 0.272 |
| Can I appeal my grade to the department chair? | Yes | 0.397 |
| When's the best time to do laundry in morrow house? | Yes | 0.310 |
| Can I upgrage my meal plan tier for free? | Yes | 0.383 |
| How long does it take to get my first session at the counseling centre? | Yes | 0.451 |
| What is the capital of Mongolia? | No | 0.825 |
| How do I change the oil in a diesel engine? | No | 0.908 |
| Who won the 1994 World Cup? | No | 0.869 |
| What is the recommended dosage of ibuprofen for a headache? | No | 0.782 |
| How do I write a for loop in Rust? | No | 0.893 |

## How I Used AI

<!-- Two specific moments. For each: what you asked for, what came back, and
     what you changed about it.

     "I asked Claude to write the chunking function from my notes. It ignored
     the overlap, so I added that myself" is the level of detail we're after.
     "I used AI to help me code" is not.

     Milestone 5. -->

**1.** I used it to explain concepts likechunking, and how to run certain functionality to save me the time of eye fishing in ``RUNNINg.md`` to find the exact commands.

**2.** I also used it for fast experiemnation and anaslsis, specifically, I instructed it to run different chunk_size/overlap splits to save me time analysising. I also used it to implement logic and fill in the readme from my conversations with it. 

**3.** In unit 2, I used AI to work through what contituted wrong or right answer for eeach questiion. I also relied heavier on AI to spot issues with my criterians (most of which I disagreed with) and  populate the readme afterthe had clarity on what I wated.
<!-- ── Stretch features ─────────────────────────────────────────────────────
     Doing one? Say so here BEFORE you start. A feature this README never
     claims earns nothing.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5 of 5 | 5 of 5 | 5 of 5 | MET |
| 2. Every answer names a source | 5 of 5 | 5 of 5 | 5 of 5 | 5 of 5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5 of 5 | 5 of 5 | 5 of 5 | MET |
| 4. Sampled chunks begin with the source document's title line | 4 of 5 | 4 of 5 | 4 of 5 | 4 of 5 | MET |
| 5. Named source actually contains the fact stated | 5 of 5 | 5 of 5 | 5 of 5 | 5 of 5 | MET |

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

**1. Retrieved chunk contains the answer** — produced by: `store.py::search` inside `run_eval.py::run_once`, run 1 of `results/run_2026-09-27_2306_before.md`

```
Question: Can I appeal my grade to the department chair?
Best distance: 0.3968 (passed the gate)
Sources retrieved: admin_add_drop_deadline.txt, admin_grade_appeals.txt, course_cs_210.txt, course_stat_150.txt, course_stat_150_exams.txt

A grade appeal must start with the instructor and be raised within fifteen days of the grade posting; it only goes to the department after that step. Skipping the instructor step will cause the appeal to be returned.

Source: admin_grade_appeals.txt
```

**2. Every answer names a source** — produced by: `generate.py::answer_from_chunks`, run 1 of `results/run_2026-09-27_2306_before.md`

```
No, upgrading your meal plan tier bills you immediately.

Source: admin_meal_plan_changes.txt
```

**3. Gate stops out-of-corpus questions** — produced by: `gate.py::check` inside `run_eval.py::check_out_of_scope`, `results/run_2026-09-27_2306_before.md`

```
| Out-of-scope question | Best distance | Gate |
|---|---|---|
| What is the capital of Mongolia? | 0.825 | refused |
| How do I change the oil in a diesel engine? | 0.908 | refused |
| Who won the 1994 World Cup? | 0.869 | refused |
| What is the recommended dosage of ibuprofen for a headache? | 0.782 | refused |
| How do I write a for loop in Rust? | 0.893 | refused |
```

**4. Sampled chunks begin with the source document's title line** — produced by: `chunker.py::split_documents` (see Sample Chunks above)

```
Chunk 2 — source: course_cs_210_exams.txt#0
CS 210 Data Structures — assessment

Two midterms and a final, all drawn from lecture material rather than the textbook. Midterms are curved, the final is not.
```
```
Chunk 5 — source: housing_morrow_house_laundry.txt#1  (the miss — continuation chunk, no title)
Wednesday morning. Sunday after 6pm you will wait.
```

**5. Named source actually contains the fact stated** — cross-checked against `corpora/campus_life/documents/admin_meal_plan_changes.txt`

```
System answer: No, upgrading your meal plan tier bills you immediately.
                                                    ↓ matches ↓
Source text:   You can change your meal plan tier once, in the first ten
               days of the semester. After that it's locked. Downgrading
               refunds the difference to your student account; upgrading
               bills you immediately.
```

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 | Retrieved chunk contains the answer | MET | All 15 answers (5 questions × 3 runs) stated a fact that only appears in one of their own retrieved sources — including the grade-appeal question I predicted would miss, since the retrieved chunk still had "the department" and the model reasoned around the missing word "chair." 5 of 5 held on all three runs, beating the 4-of-5 target. |
| 2 | Every answer names a source | MET | Every run output names its filename inline or on a `Source:` line — 5 of 5 on all three runs, matching the target exactly. |
| 3 | Gate stops out-of-corpus questions | MET | The deterministic out-of-scope pass refused 5 of 5, above the 4-of-5 target, with best distances (0.78–0.91) clearly separated from the in-corpus cluster (0.27–0.45). |
| 4 | Sampled chunks begin with the source document's title line | MET | 4 of my 5 pasted sample chunks open with the title line; the one that doesn't (`housing_morrow_house_laundry.txt#1`) is a continuation chunk, exactly the known trade-off I called out in the chunker write-up. Matches the 4-of-5 target exactly rather than beating it, so I'm calling it a real MET, not a lucky one. |
| 5 | Named source actually contains the fact stated | MET | I read all five cited source documents directly and checked each answer's claim against the actual text — every one matched verbatim or near-verbatim (e.g. `admin_meal_plan_changes.txt` literally says "upgrading bills you immediately"). 5 of 5 on all three runs. |

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->

I didn't miss anything — all five criteria came back MET across all three runs, so there's no per-question mechanism to trace through the five stages here.

That's a reason to be suspicious of the targets, not a reason to celebrate. Two of the five were set with room to spare rather than pinned to the actual risk:

- **Criterion 2 (every answer names a source, 5 of 5)** was never really at risk. `GROUNDING_INSTRUCTION` in `generate.py` tells the model to name its source on every call, and the gate (`gate.py::check`) already filters out any retrieval that didn't clear `THRESHOLD` before generation runs at all — so by construction, nothing reaches the model without a real, named chunk behind it. I called this a "plumbing check" in criteria.md before I had any results, and the results confirm it: this criterion tests whether the prompt instruction exists, not whether the system works. Tightening the number to 5 of 5 (already true) wouldn't fix that — it needs a different test, e.g. checking that the *named* source is the *correct* one, which is really what criterion 5 already covers. I'd retire criterion 2 as written and fold its intent into criterion 5.

- **Criterion 3 (gate stops out-of-corpus, 4 of 5)** was set before I had the distance data to justify it — criteria.md even left the "why this target" section as a TODO until Milestone 4. Now that I have it: in-corpus best distances clustered at 0.272–0.451, out-of-corpus at 0.782–0.908. That's not a narrow margin sitting near my 0.6 threshold; it's a clean, wide gap with nothing near the boundary on either side. A target of "4 of 5" was hedging against a risk (a borderline out-of-scope question landing just under threshold) that the actual gap shows doesn't exist for these five questions. I'd tighten this to **5 of 5** — the measured separation gives no reason to tolerate a single miss.

The one target I'd defend as correctly calibrated, not just met, is **criterion 4** (chunks begin with title line, 4 of 5): it landed exactly on the target rather than beating it, and the one miss (`housing_morrow_house_laundry.txt#1`) is the specific, known mechanism I predicted in the chunker write-up — a continuation chunk losing the title line that only appears once at the top of the raw document. That's a target that was actually pinned to a real, understood failure mode, which is what the other two should have been.

## The Improvement

**What I changed:**

Added `generate.py::source_is_grounded(answer, results) -> bool`. It extracts every filename-shaped string from the answer and checks that each one is actually in the set of sources that were retrieved for that question — not just that *some* filename-shaped text appears.

**Why I picked it:**

This directly fixes the criterion 2 diagnosis above: the old check ("does a filename appear in the answer") passes even if the model names a file that was never retrieved or invents one that doesn't exist, because nothing cross-checks the name against reality. `source_is_grounded` closes that gap.

**Did it help?**

Re-ran it against all 5 real answers from the "before" run (`results/run_2026-09-27_2306_before.md`) — all 5 still pass under the stricter check, so the original answers were genuinely grounded, not just passing a weak test by luck. The value of the fix isn't a different number here; it's that criterion 2 now actually catches a hallucinated or wrong-file citation if one ever shows up, which the old check structurally could not.

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5 of 5 | 5 of 5 | 5 of 5 | MET |
| 2. Every answer names a source | 5 of 5 | 5 of 5 | 5 of 5 | 5 of 5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5 of 5 | 5 of 5 | 5 of 5 | MET |
| 4. Sampled chunks begin with the source document's title line | 4 of 5 | 4 of 5 | 4 of 5 | 4 of 5 | MET |
| 5. Named source actually contains the fact stated | 5 of 5 | 5 of 5 | 5 of 5 | 5 of 5 | MET |

From `results/run_2026-09-27_2358_after.md`. Criterion 2's 5 of 5 here is under the new `source_is_grounded` check, not the old any-filename-shaped-text check — I ran all 15 new answers (including ones with markdown like `` `admin_grade_appeals.txt` `` and `**admin_meal_plan_changes.txt**`) through it directly and every named source matched one actually retrieved. Criterion 4 is unchanged because the fix didn't touch chunking, so it's the same deterministic 4 of 5 from the Sample Chunks section.

**Did it help?**

Plainly: it didn't change any number, and I don't think it was supposed to. The system's answers were already grounded before the fix — what I confirmed is that criterion 2 previously passed for a weak reason (any filename-shaped text counted) and now passes for the right reason (the named file is actually one that was retrieved). The fix is a strengthening of the test, not a repair of the system; nothing here contradicts that, since 15 of 15 new answers still cleared the stricter bar. If it had ever caught a hallucinated filename, that's when I'd have seen this table move — it just never had a broken answer to catch in these 15 calls.

## What's Still Broken

Nothing failed a target, but one gap is still real: criterion 5 (named source actually contains the fact stated) has no automated check — I verified it by reading the five corpus documents myself and eyeballing the match. `source_is_grounded` only proves the citation is a real, retrieved file; it doesn't prove the cited chunk actually contains the specific claim in the answer. A model could name a real, retrieved source and still misattribute or fabricate a detail from a *different* retrieved chunk, and today's check would call that "grounded." I stopped here because writing an automated fact-containment check (matching a claim back to specific chunk text) is a meaningfully bigger problem than filename validation, and out of scope for this pass.

## What I'd Do Differently

I'd retire criterion 2 as its own line item. Once `source_is_grounded` exists, "names a source" and "the source is real" are the same check, and the interesting question was always criterion 5's — does the named source actually back up the claim. I'd merge 2 and 5 into one criterion: "every answer names a source that was retrieved, and that source contains the stated fact," and spend the saved effort building the automated version of the fact-containment half instead of doing it by hand each run.
