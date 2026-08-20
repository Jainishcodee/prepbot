"""Build the vector index from the markdown notes in data/.

    python -m scripts.ingest

Ingestion is offline and runs once. Everything expensive — reading files, chunking,
calling the embedding API — happens here so that answering a question at runtime is just
one embed call plus a matrix multiply.
"""

import sys
from pathlib import Path

from dotenv import load_dotenv

from app import embeddings
from app.chunking import chunk_document
from app.store import VectorStore

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
INDEX_DIR = ROOT / "index"


def main() -> int:
    files = sorted(DATA_DIR.glob("**/*.md"))
    if not files:
        print(f"No .md files found in {DATA_DIR}")
        return 1

    chunks = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        found = chunk_document(text, source=path.name)
        chunks.extend(found)
        print(f"  {path.name:<28} {len(text):>7,} chars -> {len(found):>3} chunks")

    if not chunks:
        print("Every file was empty.")
        return 1

    print(f"\nEmbedding {len(chunks)} chunks with {embeddings.EMBED_MODEL} ...")
    vectors = embeddings.embed_documents([c.text for c in chunks])

    store = VectorStore(chunks, vectors)
    store.save(INDEX_DIR)

    print(f"Saved {len(store)} chunks ({vectors.shape[1]} dimensions) to {INDEX_DIR}")
    print("\nStart the server:  uvicorn app.main:app --reload")
    return 0


if __name__ == "__main__":
    sys.exit(main())
