"""PrepBot — a RAG chatbot over interview-preparation notes.

Run it:  uvicorn app.main:app --reload
Then:    http://127.0.0.1:8000
Docs:    http://127.0.0.1:8000/docs
"""

from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.rag import answer_question
from app.store import VectorStore

load_dotenv()

INDEX_DIR = Path(__file__).resolve().parent.parent / "index"
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

# Loaded once at startup rather than per request — the index is a few megabytes and
# re-reading it on every question would dominate the response time.
state: dict = {"store": None}


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        state["store"] = VectorStore.load(INDEX_DIR)
        print(f"Loaded {len(state['store'])} chunks from {INDEX_DIR}")
    except FileNotFoundError as exc:
        # Start anyway so /health can report the problem, rather than crashing the
        # process with a stack trace that says nothing useful to a first-time user.
        print(f"WARNING: {exc}")
    yield


app = FastAPI(
    title="PrepBot",
    description="RAG over interview-prep notes: chunk, embed, retrieve, ground, answer.",
    lifespan=lifespan,
)


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    k: int = Field(default=4, ge=1, le=10)


class ChatResponse(BaseModel):
    answer: str
    sources: list[dict]
    grounded: bool


def get_store() -> VectorStore:
    store = state["store"]
    if store is None:
        raise HTTPException(
            503, "No index loaded. Run: python -m scripts.ingest"
        )
    return store


@app.get("/health")
def health() -> dict:
    store = state["store"]
    return {
        "status": "ok" if store else "no-index",
        "chunks": len(store) if store else 0,
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    result = answer_question(get_store(), request.question, k=request.k)
    return ChatResponse(
        answer=result.text, sources=result.sources, grounded=result.grounded
    )


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
