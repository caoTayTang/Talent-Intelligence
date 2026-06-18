from uuid import UUID

from sqlalchemy.orm import Session

from talent_core.db import SessionLocal
from talent_core.models import (
    DocumentChunk,
    DocumentChunkSource,
    DocumentOwnerType,
)


def replace_document_chunks(
    owner_type: DocumentOwnerType,
    owner_id: UUID,
    source: DocumentChunkSource,
    chunks: list[dict],
    embeddings: list[list[float]],
) -> None:
    """
    Replace all chunks for one owner/source pair.

    Use this when the worker reparses a JD or CV and wants the vector index to
    match the latest source text exactly.
    """
    if len(chunks) != len(embeddings):
        raise ValueError("chunks and embeddings must have the same length")

    db: Session = SessionLocal()
    try:
        db.query(DocumentChunk).filter(
            DocumentChunk.owner_type == owner_type,
            DocumentChunk.owner_id == owner_id,
            DocumentChunk.source == source,
        ).delete()

        for chunk, embedding in zip(chunks, embeddings):
            db.add(
                DocumentChunk(
                    owner_type=owner_type,
                    owner_id=owner_id,
                    source=source,
                    section=chunk.get("section"),
                    chunk_text=chunk["text"],
                    embedding=embedding,
                    metadata_json=chunk.get("metadata", {}),
                )
            )

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def search_similar_chunks(
    owner_type: DocumentOwnerType,
    owner_id: UUID,
    source: DocumentChunkSource,
    query_embedding: list[float],
    limit: int = 5,
) -> list[dict]:
    """
    Return nearest chunks for one owner/source pair using cosine distance.
    """
    db: Session = SessionLocal()
    try:
        rows = (
            db.query(
                DocumentChunk,
                DocumentChunk.embedding.cosine_distance(query_embedding).label(
                    "distance"
                ),
            )
            .filter(
                DocumentChunk.owner_type == owner_type,
                DocumentChunk.owner_id == owner_id,
                DocumentChunk.source == source,
            )
            .order_by("distance")
            .limit(limit)
            .all()
        )

        return [
            {
                "id": str(chunk.id),
                "owner_type": chunk.owner_type.value,
                "owner_id": str(chunk.owner_id),
                "source": chunk.source.value,
                "section": chunk.section,
                "text": chunk.chunk_text,
                "metadata": chunk.metadata_json,
                "similarity": 1 - float(distance),
            }
            for chunk, distance in rows
        ]
    finally:
        db.close()
