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
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |
| 4 |  |  |  |
| 5 |  |  |  |

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

## The Improvement

**What I changed:**

**Why I picked it:**

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->
