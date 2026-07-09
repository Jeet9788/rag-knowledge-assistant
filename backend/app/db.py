"""Database access: connection pool, schema bootstrap, and pgvector setup."""
from __future__ import annotations

import logging

import psycopg
from pgvector.psycopg import register_vector
from psycopg_pool import ConnectionPool

from .config import settings

logger = logging.getLogger(__name__)

_pool: ConnectionPool | None = None


def _ensure_extension() -> None:
    """Create the pgvector extension once, before the pool opens connections.

    Doing this here (rather than in the pool's per-connection configure) avoids a
    race where multiple connections try to CREATE EXTENSION concurrently.
    """
    with psycopg.connect(settings.database_url, autocommit=True) as conn:
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector")


def _configure(conn) -> None:
    # By now the vector type exists, so we can register its psycopg adapter.
    register_vector(conn)


def get_pool() -> ConnectionPool:
    global _pool
    if _pool is None:
        _ensure_extension()
        _pool = ConnectionPool(
            conninfo=settings.database_url,
            min_size=1,
            max_size=10,
            configure=_configure,
            open=True,
            kwargs={"autocommit": True},
        )
    return _pool


SCHEMA_SQL = """
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename TEXT NOT NULL,
    collection TEXT NOT NULL DEFAULT 'default',
    num_chunks INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    collection TEXT NOT NULL DEFAULT 'default',
    chunk_index INTEGER NOT NULL,
    page INTEGER,
    content TEXT NOT NULL,
    embedding VECTOR(%(dim)s) NOT NULL,
    tsv TSVECTOR GENERATED ALWAYS AS (to_tsvector('english', content)) STORED,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS chunks_collection_idx ON chunks (collection);
CREATE INDEX IF NOT EXISTS chunks_tsv_idx ON chunks USING GIN (tsv);
CREATE INDEX IF NOT EXISTS chunks_embedding_idx
    ON chunks USING hnsw (embedding vector_cosine_ops);
"""


def init_db() -> None:
    """Create the pgvector extension, tables, and indexes if they do not exist."""
    pool = get_pool()
    with pool.connection() as conn:
        conn.execute(SCHEMA_SQL % {"dim": settings.embedding_dim})
    logger.info("Database schema initialized (embedding_dim=%s)", settings.embedding_dim)


def close_db() -> None:
    global _pool
    if _pool is not None:
        _pool.close()
        _pool = None
