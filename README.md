# PrepBot — a RAG chatbot over interview-preparation notes

Ask a question in plain English; get an answer drawn **only** from an indexed set of
markdown notes, with the source passages it used. If the notes do not cover it, it says
so instead of inventing something.

Python · FastAPI · Gemini (embeddings + generation) · NumPy vector store · pytest

---

## Why RAG, and not just a prompt

A language model only knows what was in its training data. It has never seen these notes,
its knowledge has a cutoff, and when it does not know something it tends to produce a
fluent guess rather than an admission — because it was trained to predict plausible text,
not true text.

Retrieval-Augmented Generation fixes that by changing what the model is asked to do.
Instead of "answer from memory", it becomes "answer from *this* text, which I am giving
you right now". The knowledge lives in a searchable index, not in the weights — so it can
be updated by re-running ingestion rather than retraining anything, and every answer can
point at the passage it came from.

## How it works

**Ingest — offline, once**

```
markdown files
  -> split on markdown headings          structure first, so a chunk is a whole idea
  -> sliding window with overlap         only for sections too long to fit
  -> embed each chunk (RETRIEVAL_DOCUMENT)
  -> normalise + save to index/
```

**Query — per request**

```
question
  -> embed (RETRIEVAL_QUERY)
  -> cosine similarity against every chunk -> top-k
  -> relevance gate: is the best match close enough?   -- no -> "That isn't in my notes."
  -> build a prompt: rules + retrieved context + question
  -> Gemini answers from that context
  -> answer + the sources it retrieved
```

## Four decisions worth explaining

**Chunk on headings before chunking on size.** Most tutorials slice documents into fixed
windows of N characters. That cuts through the middle of ideas. These are markdown notes,
so headings already mark the boundaries the author intended — splitting there first means
a chunk is usually a complete thought, and only oversized sections fall back to a sliding
window. The heading is also prepended to each chunk before embedding: `"0.5s, 1s, 2s,
capped at 8"` is nearly meaningless alone, but `"Explain your backoff — 0.5s, 1s..."`
sits close in vector space to a question about backoff.

**Overlap between windows.** Without it, an idea spanning a boundary ends up half in one
chunk and half in the next, and fully in neither — so neither one retrieves for a question
about it.

**A relevance gate before calling the model.** Top-k retrieval has no concept of "nothing
matched" — it always returns the *k* closest chunks, however far away they are. Ask this
bot about the weather and it will happily hand the model four irrelevant passages, which
is exactly the setup where a model invents a connection. So if the best similarity falls
below a floor, the model is never called: the answer is "That isn't in my notes." Cheaper,
faster, and more honest than hoping the prompt talks it out of hallucinating.

**Task-typed embeddings.** A document states facts; a question asks for them. They are
phrased differently, so embedding both the same way loses a little matching accuracy.
Gemini's embedding endpoint accepts a task type, so chunks are embedded as
`RETRIEVAL_DOCUMENT` and questions as `RETRIEVAL_QUERY`.

## Why a NumPy store rather than FAISS, Chroma or Pinecone

At a few hundred chunks, an exact dot product across the whole matrix is both faster and
simpler than an approximate-nearest-neighbour index — and writing it out makes the actual
mechanic of semantic search visible rather than hidden behind a library call. Because
every vector is normalised at write time, cosine similarity *is* the dot product, so the
entire search is one matrix-vector multiply.

The swap point is a single method, `VectorStore.search`. Somewhere around a hundred
thousand chunks, scanning everything stops being instant; at that point you replace that
one method with FAISS or Chroma locally, or Pinecone or pgvector as a service, and trade a
little recall for a large speed win. Nothing else in the codebase changes.

## Run it

```bash
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt

copy .env.example .env          # then paste a free key from
                                # https://aistudio.google.com/apikey

.venv\Scripts\python.exe -m scripts.check_setup   # verify key + model names
.venv\Scripts\python.exe -m scripts.ingest        # build the index
.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Then open <http://127.0.0.1:8000>. API docs at `/docs`.

```bash
.venv\Scripts\python.exe -m pytest -q
```

12 tests, no API key and no network needed — they cover the chunking and similarity
logic, which is what actually determines whether retrieval works.

## Layout

| File | Responsibility |
|---|---|
| `app/chunking.py` | Heading-aware splitting and sliding windows — pure, unit-tested |
| `app/store.py` | Vector store: normalise, cosine search, save/load — pure, unit-tested |
| `app/embeddings.py` | Gemini embeddings and generation; the only file that talks to an API |
| `app/rag.py` | Retrieve → relevance gate → prompt construction → answer |
| `app/main.py` | FastAPI routes and the chat UI |
| `scripts/ingest.py` | Build the index from `data/*.md` |
| `scripts/check_setup.py` | Verify the key and model names before a full ingest |

## Known limits

- **Dense retrieval only.** No keyword/BM25 leg, so exact tokens — an error code, a
  version number — can be missed where semantic similarity is weak. Hybrid search is the
  standard fix.
- **No reranking.** Retrieving ~50 candidates cheaply and reranking with a cross-encoder
  would improve precision at the top of the list.
- **No conversation memory.** Each question is independent, so follow-ups like "why?" have
  no antecedent. Fixing it properly means rewriting the follow-up into a standalone query
  before embedding it, not just appending history.
- **Fixed relevance floor.** The threshold is a constant tuned by hand; the right value
  varies with the embedding model and the corpus.
- **Ingestion is not incremental.** Editing one note means re-embedding all of them.
