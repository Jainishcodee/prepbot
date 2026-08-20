"""Retrieval-augmented generation: the part that ties everything together.

Query flow:

    question
      -> embed_query()               question becomes a vector
      -> store.search(k)             cosine similarity picks the closest chunks
      -> relevance gate              if nothing is close enough, stop here
      -> build_prompt()              retrieved text becomes context in the prompt
      -> generate()                  model answers *from that context*
      -> answer + sources
"""

from dataclasses import dataclass

from app import embeddings
from app.chunking import Chunk
from app.store import VectorStore

# If even the best-matching chunk scores below this, the corpus almost certainly does not
# contain the answer.
#
# This gate is the single most useful safety feature here. Retrieval always returns
# *something* — top-k has no concept of "nothing matched" — so without a floor, an
# off-topic question retrieves the least-irrelevant chunks and the model dutifully
# invents an answer around them. Refusing to call the model at all is both cheaper and
# more honest than hoping the prompt talks it out of hallucinating.
MIN_SIMILARITY = 0.45

SYSTEM_RULES = """You are a study assistant answering from a set of interview-preparation notes.

Rules:
- Answer using ONLY the context below. Do not add facts from your own knowledge.
- If the context does not contain the answer, say exactly: "That isn't in my notes."
- Be concise and direct. Prefer the wording used in the notes.
- Do not mention "the context" or "the notes provided" in your answer; just answer.
"""


@dataclass
class Answer:
    text: str
    sources: list[dict]
    grounded: bool


def format_context(hits: list[tuple[Chunk, float]]) -> str:
    """Lay the retrieved chunks out as numbered blocks.

    Numbering them lets the model refer to a specific passage, and makes it obvious in
    the logs which chunk produced which claim when an answer looks wrong.
    """
    blocks = []
    for i, (chunk, score) in enumerate(hits, start=1):
        blocks.append(
            f"[{i}] source: {chunk.source} — {chunk.heading} (similarity {score:.2f})\n"
            f"{chunk.text}"
        )
    return "\n\n---\n\n".join(blocks)


def build_prompt(question: str, hits: list[tuple[Chunk, float]]) -> str:
    return (
        f"{SYSTEM_RULES}\n"
        f"=== CONTEXT ===\n{format_context(hits)}\n\n"
        f"=== QUESTION ===\n{question}\n\n"
        f"=== ANSWER ==="
    )


def answer_question(store: VectorStore, question: str, k: int = 4) -> Answer:
    question = question.strip()
    if not question:
        return Answer("Ask me something.", [], grounded=False)

    hits = store.search(embeddings.embed_query(question), k=k)

    if not hits or hits[0][1] < MIN_SIMILARITY:
        return Answer("That isn't in my notes.", [], grounded=False)

    text = embeddings.generate(build_prompt(question, hits))

    sources = [
        {"source": c.source, "heading": c.heading, "similarity": round(s, 3)}
        for c, s in hits
    ]
    return Answer(text or "That isn't in my notes.", sources, grounded=True)
