"""
Stage 2 of the pipeline: splitting documents into chunks.

⚠️ THIS IS THE FILE YOU CHANGE IN MILESTONE 3.

`split_documents` below is deliberately plain. It cuts every document into
fixed-size pieces with a fixed overlap and pays no attention to where sentences
or paragraphs end. It works, and it is not good.

On a corpus of short posts it may not cut anything at all: `campus_life` comes
out as 88 documents and 88 chunks, because almost nothing in it reaches 800
characters. That is the baseline, not a bug — Milestone 3 is where you decide
whether one post should stay one chunk.

Your job in Milestone 3 is to replace the *body* of `split_documents` with a
strategy that fits the documents you actually read in Milestone 1. Keep the
name and the shape of what it returns — the rest of the pipeline calls it, and
your README has to name the function that produced your chunks.

If you get stuck for 30 minutes, `fallback_split` is the original. Switch back
to it, write down what you saw, and move on. That's a real observation about
your pipeline, not giving up.
"""

from dataclasses import dataclass

import config
from ingest import Document


@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str        # which file it came from
    index: int         # which chunk within that file, starting at 0
    produced_by: str   # the function that made it — cite this in your README

    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    The starter's original chunker. Fixed-size character windows with overlap.

    Keep this function. Milestone 3's stop rule points back at it, and having
    something to compare your own strategy against is useful in unit 2.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    if overlap >= chunk_size:
        raise ValueError("overlap has to be smaller than chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        start = 0
        index = 0
        while start < len(doc.text):
            piece = doc.text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::fallback_split",
                    )
                )
                index += 1
            start += chunk_size - overlap

    return chunks


MIN_TAIL_CHARS = 40  # a trailing fragment shorter than this gets merged back


def split_documents(documents: list[Document]) -> list[Chunk]:
    """
    Split documents into chunks.

    Same fixed-size character windowing as `fallback_split`, just tuned:
    CHUNK_SIZE=300 / CHUNK_OVERLAP=50 instead of the generic 800/120. At
    800/120 nothing in this corpus ever split (every document is under 554
    characters); at 300/50, documents over ~300 characters actually split,
    which is the point of this milestone.

    One fix on top of the raw windowing: the last window in a document is
    often just a few leftover characters ("ail." from the tail of "email.").
    Tried tuning overlap to avoid this instead — across the whole corpus it
    never got the tiny-chunk count anywhere near zero, and raising overlap
    made mid-word cuts substantially worse (more boundaries per document,
    each one still just a raw character index). So instead: any trailing
    piece shorter than MIN_TAIL_CHARS gets merged onto the previous chunk of
    the same document rather than kept standalone.

    That merge is a no-op in disguise, not string surgery: since
    MIN_TAIL_CHARS (40) is smaller than CHUNK_OVERLAP (50), any piece short
    enough to trigger it is guaranteed to fall entirely inside the previous
    window's overlap region — "ail." isn't new content, it's literally the
    tail of "fail." that the previous chunk already ends with. So the merge
    checks for that containment and drops the fragment outright; it only
    falls back to concatenating if that guarantee doesn't hold (e.g. if
    someone changes MIN_TAIL_CHARS or CHUNK_OVERLAP later without checking
    this still holds).

    Known trade-off, taken deliberately rather than fixed: this windowing
    still slices on raw character position, so mid-word cuts inside a chunk
    (not just at the very end) still happen, and every chunk after the first
    one in a split document loses the source document's title line, since the
    title only ever appears at the very start of the text. A strategy that
    split on paragraph breaks and re-prepended the title to each piece would
    avoid both; this one doesn't.
    """
    chunks = fallback_split(documents)

    merged: list[Chunk] = []
    for chunk in chunks:
        if (
            merged
            and merged[-1].source == chunk.source
            and len(chunk.text) < MIN_TAIL_CHARS
        ):
            if chunk.text not in merged[-1].text:
                merged[-1].text = f"{merged[-1].text} {chunk.text}"
            # else: fully contained in the overlap region already — drop it
        else:
            merged.append(chunk)

    counts: dict[str, int] = {}
    for chunk in merged:
        chunk.index = counts.get(chunk.source, 0)
        counts[chunk.source] = chunk.index + 1
        chunk.produced_by = "chunker.py::split_documents"

    return merged


def describe(chunks: list[Chunk]) -> str:
    """A one-line summary, printed after indexing."""
    if not chunks:
        return "0 chunks"
    lengths = [len(c.text) for c in chunks]
    return (
        f"{len(chunks)} chunks, "
        f"{sum(lengths) // len(lengths)} characters on average "
        f"(shortest {min(lengths)}, longest {max(lengths)}), "
        f"produced by {chunks[0].produced_by}"
    )


if __name__ == "__main__":
    from ingest import load_documents

    chunks = split_documents(load_documents())
    print(describe(chunks))
