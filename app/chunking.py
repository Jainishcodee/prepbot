"""Turning documents into retrievable chunks.

Chunking is the decision that quietly determines whether a RAG system works. Embed a
whole document and its vector is an average of everything in it — too blurry to match a
specific question. Chunk too small and you strip away the context that made a passage
meaningful.

The approach here is two-stage, and the first stage is the interesting one:

1. **Split on structure first.** These are markdown notes, so headings already mark where
   one idea ends and the next begins. Splitting there means a chunk is usually a whole
   coherent section rather than an arbitrary window of characters.
2. **Only then split by size.** A section longer than the budget gets a sliding window
   with overlap, so an idea straddling a boundary survives in at least one chunk.
"""

import re
from dataclasses import dataclass

# A markdown ATX heading: one to six hashes, a space, then the title.
HEADING = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)


@dataclass
class Chunk:
    """One retrievable unit of text, plus where it came from.

    `source` and `heading` are carried through the whole pipeline so the final answer can
    cite them. A RAG answer you cannot trace back to a document is barely better than an
    ungrounded one.
    """

    text: str
    source: str
    heading: str


def split_by_heading(markdown: str) -> list[tuple[str, str]]:
    """Split a markdown document into (heading, body) sections.

    Text before the first heading is kept under the heading "(intro)" rather than dropped —
    losing the top of a document is an easy and invisible bug.
    """
    matches = list(HEADING.finditer(markdown))
    if not matches:
        return [("(intro)", markdown)]

    sections: list[tuple[str, str]] = []

    lead = markdown[: matches[0].start()].strip()
    if lead:
        sections.append(("(intro)", lead))

    for i, match in enumerate(matches):
        title = match.group(2).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(markdown)
        body = markdown[start:end].strip()
        if body:
            sections.append((title, body))

    return sections


def sliding_window(text: str, size: int, overlap: int) -> list[str]:
    """Cut `text` into windows of `size` characters that overlap by `overlap`.

    The overlap is the whole point: without it, a sentence split across a boundary is
    half-present in two chunks and fully present in neither, so neither one retrieves for
    a question about it.
    """
    if size < 1:
        raise ValueError("size must be at least 1")
    if overlap < 0:
        raise ValueError("overlap cannot be negative")
    if overlap >= size:
        # step would be <= 0 and the loop would never advance.
        raise ValueError("overlap must be smaller than size")

    if len(text) <= size:
        return [text]

    step = size - overlap
    windows = []
    for start in range(0, len(text), step):
        window = text[start : start + size]
        if window.strip():
            windows.append(window)
        if start + size >= len(text):
            break
    return windows


def chunk_document(
    markdown: str, source: str, size: int = 900, overlap: int = 150
) -> list[Chunk]:
    """Split one markdown document into chunks, preserving heading context.

    The heading is prepended to the chunk body before embedding. That matters more than it
    looks: a chunk reading "0.5s, 1s, 2s, 4s, capped at 8" is nearly meaningless on its
    own, but "Explain your backoff — 0.5s, 1s, 2s..." embeds close to a question about
    backoff.
    """
    chunks: list[Chunk] = []

    for heading, body in split_by_heading(markdown):
        for window in sliding_window(body, size, overlap):
            chunks.append(
                Chunk(
                    text=f"{heading}\n\n{window}".strip(),
                    source=source,
                    heading=heading,
                )
            )

    return chunks
