"""
RAG (Retrieval-Augmented Generation) Module
============================================
Handles PDF ingestion, chunking, embedding, and semantic retrieval
using a local ChromaDB vector store. No data leaves your machine.

Usage:
    from src import rag

    rag.index_pdf(file_bytes, "my_doc.pdf")   # index a PDF
    context = rag.retrieve_context(user_query) # get relevant excerpts
"""

import hashlib
import io

import chromadb
from pypdf import PdfReader

_DB_PATH = ".chroma_db"       # Persisted next to the project root (git-ignored)
_CHUNK_SIZE = 600             # Characters per chunk — sweet spot for LLM context windows
_CHUNK_OVERLAP = 100          # Overlap keeps context continuous across chunk boundaries
_MIN_CHUNK_LEN = 50           # Discard fragments shorter than this (headers, page numbers…)

_client = None
_collection = None


def _get_collection() -> chromadb.Collection:
    """Lazy-initializes and returns the persistent ChromaDB collection."""
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(path=_DB_PATH)
        # DefaultEmbeddingFunction uses a lightweight ONNX MiniLM model (~23 MB,
        # downloaded once on first use — still 100% local, no API calls).
        _collection = _client.get_or_create_collection(name="documents")
    return _collection


def _chunk_text(text: str) -> list[str]:
    """
    Splits text into overlapping fixed-size character chunks.
    Overlap ensures that sentences split across a boundary appear in
    at least one complete chunk.
    """
    chunks: list[str] = []
    step = _CHUNK_SIZE - _CHUNK_OVERLAP
    for i in range(0, len(text), step):
        chunk = text[i : i + _CHUNK_SIZE].strip()
        if len(chunk) >= _MIN_CHUNK_LEN:
            chunks.append(chunk)
    return chunks



def index_pdf(file_bytes: bytes, filename: str) -> int:
    """
    Parses, chunks, and upserts a PDF into the vector store.
    Re-uploading the same file is idempotent (same content → same IDs).

    Returns:
        The number of chunks indexed.
    """
    reader = PdfReader(io.BytesIO(file_bytes))
    collection = _get_collection()

    all_chunks: list[str] = []
    all_ids: list[str] = []
    all_metadatas: list[dict] = []

    for page_num, page in enumerate(reader.pages):
        page_text = page.extract_text() or ""
        for chunk_idx, chunk in enumerate(_chunk_text(page_text)):
            # Deterministic ID: same file + page + chunk position → same ID.
            # Using chunk_idx (not content prefix) prevents hash collisions on
            # pages with repetitive or short-period text.
            chunk_id = hashlib.md5(
                f"{filename}:{page_num}:{chunk_idx}".encode()
            ).hexdigest()
            all_chunks.append(chunk)
            all_ids.append(chunk_id)
            all_metadatas.append({"source": filename, "page": page_num + 1})

    if all_chunks:
        collection.upsert(
            documents=all_chunks,
            ids=all_ids,
            metadatas=all_metadatas,
        )

    return len(all_chunks)


def retrieve_context(query: str, n_results: int = 4) -> str:
    """
    Semantic search against indexed documents.

    Returns a formatted string of the top-k relevant excerpts, ready to
    be injected into the system prompt. Returns an empty string when no
    documents have been indexed.
    """
    collection = _get_collection()
    total = collection.count()
    if total == 0:
        return ""

    results = collection.query(
        query_texts=[query],
        n_results=min(n_results, total),
    )

    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]

    if not docs:
        return ""

    parts = [
        f"[{meta['source']} — p.{meta['page']}]\n{doc}"
        for doc, meta in zip(docs, metas)
    ]
    return "\n\n---\n\n".join(parts)


def clear_index() -> None:
    """Removes all indexed document chunks from the vector store."""
    collection = _get_collection()
    all_ids = collection.get()["ids"]
    if all_ids:
        collection.delete(ids=all_ids)


def document_count() -> int:
    """Returns the total number of indexed chunks (useful for UI status)."""
    return _get_collection().count()
