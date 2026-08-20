"""Verify the API key and model names before running a full ingest.

    python -m scripts.check_setup

Model identifiers change between provider releases, and a wrong one fails halfway through
embedding a few hundred chunks — after you have already waited. Ten seconds here is worth
it.
"""

import os
import sys

from dotenv import load_dotenv

load_dotenv()


def main() -> int:
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        print("FAIL  GEMINI_API_KEY is not set.")
        print("      Get a free key at https://aistudio.google.com/apikey")
        print("      Then:  copy .env.example .env   and paste it in.")
        return 1
    print(f"OK    GEMINI_API_KEY found ({key[:6]}...{key[-4:]})")

    from app import embeddings

    try:
        vector = embeddings.embed_query("smoke test")
        print(f"OK    {embeddings.EMBED_MODEL} -> {len(vector)} dimensions")
    except Exception as exc:
        print(f"FAIL  embedding model '{embeddings.EMBED_MODEL}' failed: {exc}")
        _suggest(embeddings, "embed")
        return 1

    try:
        reply = embeddings.generate("Reply with exactly: ready")
        print(f"OK    {embeddings.CHAT_MODEL} -> {reply!r}")
    except Exception as exc:
        print(f"FAIL  chat model '{embeddings.CHAT_MODEL}' failed: {exc}")
        _suggest(embeddings, "generate")
        return 1

    print("\nAll good. Next:  python -m scripts.ingest")
    return 0


def _suggest(embeddings, kind: str) -> None:
    """List models the key can actually see, so a rename is obvious."""
    try:
        names = [m.name for m in embeddings.client().models.list()]
        wanted = "embed" if kind == "embed" else "gemini"
        matches = [n for n in names if wanted in n.lower()][:10]
        if matches:
            print("      Models available to this key:")
            for n in matches:
                print(f"        {n}")
            print("      Set EMBED_MODEL / CHAT_MODEL in .env to one of these.")
    except Exception:
        pass


if __name__ == "__main__":
    sys.exit(main())
