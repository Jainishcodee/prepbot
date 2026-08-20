"""A minimal vector store: cosine similarity search over embeddings.

Deliberately hand-rolled rather than FAISS, Chroma or Pinecone. At this corpus size —
a few hundred chunks — an exact numpy dot product is both faster and simpler than an
approximate-nearest-neighbour index, and writing it out makes the actual mechanic of
"semantic search" visible instead of hidden behind a library call.

The swap point is `search()`. At a scale where scanning every vector stops being
instant (roughly a hundred thousand chunks and up), you replace that one method with an
ANN index — FAISS or Chroma locally, Pinecone or pgvector as a service — and trade a
little recall for a large speed win. Nothing else in this file has to change.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import numpy as np

from app.chunking import Chunk


def normalise(vectors: np.ndarray) -> np.ndarray:
    """Scale each row to unit length.

    Why: cosine similarity is the dot product divided by both magnitudes. If every vector
    already has magnitude 1, cosine similarity *is* the dot product — so the whole search
    becomes one matrix multiply. Normalising once at write time removes that division from
    every subsequent query.
    """
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    # Guard against a zero vector: dividing by zero would produce NaN and silently poison
    # every similarity score computed against it.
    norms[norms == 0] = 1e-12
    return vectors / norms


class VectorStore:
    """Chunks plus their embeddings, searchable by cosine similarity."""

    def __init__(self, chunks: list[Chunk], vectors: np.ndarray):
        if len(chunks) != vectors.shape[0]:
            raise ValueError(
                f"{len(chunks)} chunks but {vectors.shape[0]} vectors — these must match"
            )
        self.chunks = chunks
        self.vectors = normalise(vectors.astype(np.float32))

    def __len__(self) -> int:
        return len(self.chunks)

    def search(self, query_vector: np.ndarray, k: int = 4) -> list[tuple[Chunk, float]]:
        """Return the `k` chunks most similar to the query, best first.

        `k` is the classic RAG dial. Too low and the answer simply isn't in the context, so
        the model fills the gap by guessing. Too high and you bury the relevant passage in
        noise, burn tokens, and hit the "lost in the middle" effect where models attend
        less to the centre of a long context.
        """
        if len(self) == 0:
            return []

        query = normalise(query_vector.reshape(1, -1).astype(np.float32))[0]

        # One matrix-vector product scores every chunk at once. Because both sides are
        # unit length, each score is exactly the cosine similarity, in [-1, 1].
        scores = self.vectors @ query

        # argsort is ascending, so take the tail and reverse it. argpartition would be
        # faster asymptotically but is not worth the complexity at this size.
        top = np.argsort(scores)[-k:][::-1]
        return [(self.chunks[i], float(scores[i])) for i in top]

    def save(self, directory: str | Path) -> None:
        """Persist the index so ingestion runs once, not on every server start."""
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        np.save(path / "vectors.npy", self.vectors)
        (path / "chunks.json").write_text(
            json.dumps([asdict(c) for c in self.chunks], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @classmethod
    def load(cls, directory: str | Path) -> VectorStore:
        path = Path(directory)
        vectors_file = path / "vectors.npy"
        chunks_file = path / "chunks.json"

        if not vectors_file.exists() or not chunks_file.exists():
            raise FileNotFoundError(
                f"No index in {path}. Build one first: python -m scripts.ingest"
            )

        vectors = np.load(vectors_file)
        raw = json.loads(chunks_file.read_text(encoding="utf-8"))
        return cls([Chunk(**c) for c in raw], vectors)
