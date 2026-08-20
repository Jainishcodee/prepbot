"""Gemini embeddings and generation.

Google's free tier covers both the embedding model and a fast chat model, so the whole
system runs on one API key and no local model download.

One detail worth knowing, because it is the kind of thing an interviewer follows up on:
Gemini's embedding endpoint takes a **task type**. Embedding a document and embedding a
question are not the same job — a document states facts, a question asks for them, and
they are phrased differently. Telling the model which side it is embedding produces
vectors that match each other better. Hence `RETRIEVAL_DOCUMENT` at ingest time and
`RETRIEVAL_QUERY` at query time.
"""

import os

import numpy as np
from google import genai
from google.genai import types

EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-004")
CHAT_MODEL = os.getenv("CHAT_MODEL", "gemini-2.0-flash")

# The embedding endpoint caps how many texts it will take per call.
BATCH_SIZE = 64

_client: genai.Client | None = None


def client() -> genai.Client:
    """One shared client, created on first use.

    Reading the key lazily rather than at import time means the tests and the chunking
    code can be imported without an API key present.
    """
    global _client
    if _client is None:
        key = os.getenv("GEMINI_API_KEY")
        if not key:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Get a free key at "
                "https://aistudio.google.com/apikey and put it in .env"
            )
        _client = genai.Client(api_key=key)
    return _client


def _embed(texts: list[str], task_type: str) -> np.ndarray:
    vectors: list[list[float]] = []

    for start in range(0, len(texts), BATCH_SIZE):
        batch = texts[start : start + BATCH_SIZE]
        response = client().models.embed_content(
            model=EMBED_MODEL,
            contents=batch,
            config=types.EmbedContentConfig(task_type=task_type),
        )
        vectors.extend(e.values for e in response.embeddings)

    return np.array(vectors, dtype=np.float32)


def embed_documents(texts: list[str]) -> np.ndarray:
    """Embed chunks for storage. Returns one row per input text."""
    return _embed(texts, "RETRIEVAL_DOCUMENT")


def embed_query(text: str) -> np.ndarray:
    """Embed a user question for search. Returns a single vector."""
    return _embed([text], "RETRIEVAL_QUERY")[0]


def generate(prompt: str) -> str:
    """Ask the chat model for an answer.

    Temperature 0.2, not the default. This is a retrieval-grounded question-answering
    task, so the goal is to restate supplied facts accurately — creative variety is
    exactly the wrong behaviour here, and lower temperature reduces the chance of the
    model embellishing beyond the context.
    """
    response = client().models.generate_content(
        model=CHAT_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.2),
    )
    return (response.text or "").strip()
