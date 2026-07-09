"""Document ingestion: parse -> chunk -> embed -> store."""
from __future__ import annotations

import io
import logging

from pypdf import PdfReader

from .chunking import chunk_pages
from .config import settings
from .db import get_pool
from .embeddings import embed_texts

logger = logging.getLogger(__name__)


def _parse(filename: str, data: bytes) -> list[tuple[int | None, str]]:
    """Return a list of (page_number, text). Page is None for non-paginated files."""
    lower = filename.lower()
    if lower.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(data))
        pages: list[tuple[int | None, str]] = []
        for i, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                pages.append((i, text))
        return pages
    if lower.endswith((".txt", ".md", ".markdown")):
        # utf-8-sig strips a leading BOM if present.
        return [(None, data.decode("utf-8-sig", errors="ignore"))]
    raise ValueError(f"Unsupported file type: {filename}")


def ingest_document(filename: str, data: bytes, collection: str = "default") -> dict:
    """Ingest a single uploaded file into the given collection."""
    pages = _parse(filename, data)
    if not pages:
        raise ValueError("No extractable text found in document.")

    chunks = chunk_pages(
        pages,
        chunk_size=settings.chunk_size,
        overlap=settings.chunk_overlap,
        strategy="sentence",
    )
    if not chunks:
        raise ValueError("Document produced no chunks.")

    embeddings = embed_texts([c.content for c in chunks])

    pool = get_pool()
    with pool.connection() as conn:
        with conn.transaction():
            row = conn.execute(
                "INSERT INTO documents (filename, collection, num_chunks) "
                "VALUES (%s, %s, %s) RETURNING id",
                (filename, collection, len(chunks)),
            ).fetchone()
            document_id = row[0]

            with conn.cursor() as cur:
                cur.executemany(
                    "INSERT INTO chunks "
                    "(document_id, collection, chunk_index, page, content, embedding) "
                    "VALUES (%s, %s, %s, %s, %s, %s)",
                    [
                        (
                            document_id,
                            collection,
                            idx,
                            chunk.page,
                            chunk.content,
                            embeddings[idx],
                        )
                        for idx, chunk in enumerate(chunks)
                    ],
                )

    logger.info("Ingested %s (%d chunks) into '%s'", filename, len(chunks), collection)
    return {
        "document_id": str(document_id),
        "filename": filename,
        "collection": collection,
        "num_chunks": len(chunks),
    }


def list_documents() -> list[dict]:
    pool = get_pool()
    with pool.connection() as conn:
        rows = conn.execute(
            "SELECT id, filename, collection, num_chunks, created_at "
            "FROM documents ORDER BY created_at DESC"
        ).fetchall()
    return [
        {
            "id": str(r[0]),
            "filename": r[1],
            "collection": r[2],
            "num_chunks": r[3],
            "created_at": r[4],
        }
        for r in rows
    ]


def delete_document(document_id: str) -> bool:
    pool = get_pool()
    with pool.connection() as conn:
        result = conn.execute("DELETE FROM documents WHERE id = %s", (document_id,))
        return result.rowcount > 0
