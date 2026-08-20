"""Unit tests for the pure pieces — no API key, no network, no server.

Everything that touches Gemini is excluded on purpose. What is left is the logic that
actually decides whether retrieval works: how documents are split, and how similarity is
computed. Those are the parts worth protecting with tests.
"""

import numpy as np
import pytest

from app.chunking import Chunk, chunk_document, sliding_window, split_by_heading
from app.store import VectorStore, normalise


# --------------------------------------------------------------------------- chunking

def test_split_by_heading_keeps_text_before_the_first_heading():
    doc = "preamble text\n\n# First\nbody one\n\n## Second\nbody two"
    sections = split_by_heading(doc)

    assert [h for h, _ in sections] == ["(intro)", "First", "Second"]
    # Losing the top of a document is silent and easy to miss, so assert it explicitly.
    assert sections[0][1] == "preamble text"


def test_split_by_heading_handles_a_document_with_no_headings():
    assert split_by_heading("just prose") == [("(intro)", "just prose")]


def test_sliding_window_overlaps():
    # size 10, overlap 4 -> step 6, so windows start at 0, 6, 12 ...
    windows = sliding_window("abcdefghijklmnop", size=10, overlap=4)

    assert windows[0] == "abcdefghij"
    assert windows[1] == "ghijklmnop"
    # The overlap must actually appear in both windows, or an idea spanning the boundary
    # is lost from both.
    assert windows[0][-4:] == windows[1][:4]


def test_sliding_window_returns_short_text_untouched():
    assert sliding_window("short", size=100, overlap=10) == ["short"]


def test_sliding_window_rejects_overlap_greater_than_size():
    # step would be <= 0 and the loop would spin forever.
    with pytest.raises(ValueError):
        sliding_window("abcdef", size=4, overlap=4)


def test_chunk_document_prepends_the_heading_for_context():
    chunks = chunk_document("# Backoff\n0.5s then 1s then 2s", source="notes.md")

    assert len(chunks) == 1
    assert chunks[0].heading == "Backoff"
    assert chunks[0].source == "notes.md"
    # The heading is what makes an otherwise contextless fragment retrievable.
    assert chunks[0].text.startswith("Backoff")


# ------------------------------------------------------------------------------ store

def test_normalise_gives_every_row_unit_length():
    vectors = np.array([[3.0, 4.0], [1.0, 0.0]])
    lengths = np.linalg.norm(normalise(vectors), axis=1)

    assert np.allclose(lengths, 1.0)


def test_normalise_does_not_produce_nan_for_a_zero_vector():
    result = normalise(np.array([[0.0, 0.0]]))

    assert not np.isnan(result).any()


def _store() -> VectorStore:
    chunks = [
        Chunk("cats purr", "a.md", "Cats"),
        Chunk("dogs bark", "b.md", "Dogs"),
        Chunk("birds sing", "c.md", "Birds"),
    ]
    vectors = np.array([[1.0, 0.0], [0.0, 1.0], [-1.0, 0.0]])
    return VectorStore(chunks, vectors)


def test_search_returns_the_closest_chunk_first():
    hits = _store().search(np.array([0.9, 0.1]), k=3)

    assert hits[0][0].text == "cats purr"
    # Opposite direction, so cosine similarity should be about -1.
    assert hits[-1][0].text == "birds sing"
    assert hits[-1][1] < 0


def test_search_respects_k():
    assert len(_store().search(np.array([1.0, 0.0]), k=2)) == 2


def test_search_scores_are_cosine_similarities():
    hits = _store().search(np.array([1.0, 0.0]), k=1)

    # Identical direction -> similarity 1.
    assert hits[0][1] == pytest.approx(1.0, abs=1e-6)


def test_store_rejects_mismatched_chunks_and_vectors():
    with pytest.raises(ValueError):
        VectorStore([Chunk("one", "a.md", "A")], np.array([[1.0, 0.0], [0.0, 1.0]]))
