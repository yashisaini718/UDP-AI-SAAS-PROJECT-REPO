from app.ai.retriever import RetriverPipeline
from app.ai.embeddings import EmbeddingPipeline
from app.ai.vectorstore import VectorStore
from sqlalchemy import select
from app.models.documents import Document
from sqlalchemy.ext.asyncio import AsyncSession
from app.ai.llm import get_llm
from app.ai.rag import RagPipeline

async def get_document_by_id(db: AsyncSession, document_id: str):
    result=await db.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()

    if document is None:
        raise ValueError("Document not found")

    return document

def initialize_rag_pipeline():
    embedding_manager=EmbeddingPipeline()
    vector_store=VectorStore()

    retriever=RetriverPipeline(
        vector_store=vector_store, 
        embedding_manager=embedding_manager
    )
    llm=get_llm()
    rag_pipeline=RagPipeline(
        retriever=retriever,
        llm=llm
    )
    return rag_pipeline


def merge_and_reconcile(extracted_results):
    ''' it deduplicates the resulted opportunities'''
    merged = {}

    for result in extracted_results:

        data=result

        title = data.get("title")

        if not title:
            continue

        key = (data.get("title", "").strip().lower(),
            data.get("organization", "").strip().lower(),
            data.get("deadline")
        )

        if key not in merged:

            merged[key] = data

        else:

            existing = merged[key]

            for field, value in data.items():

                if (
                    existing.get(field) in [None, "", []]
                    and value not in [None, "", []]
                ):

                    existing[field] = value

    return list(merged.values())

import difflib

def merge_fragments(fragments: list[dict]) -> dict:
    ''' Rule-based merge for fragments already known to be the SAME
    opportunity (windowed extraction *within* one oversized anchor group).
    No LLM call — there's no cross-opportunity ambiguity here, just field
    completeness, so a plain union/first-non-null merge is enough. '''
    if not fragments:
        return {}

    merged = {}
    for frag in fragments:
        for key, value in frag.items():
            if key in ("required_documents", "action_items"):
                merged.setdefault(key, [])
                if isinstance(value, list):
                    for item in value:
                        if item not in merged[key]:
                            merged[key].append(item)
            elif key == "deadline":
                if value and (not merged.get("deadline") or value < merged["deadline"]):
                    merged["deadline"] = value
            else:
                if not merged.get(key) and value:
                    merged[key] = value
    return merged


def is_known_title(title: str, anchors: list[dict], threshold: float = 0.85) -> bool:
    ''' Cheap fuzzy check (no LLM call) — drops leftover-pass extractions that
    just re-describe an anchor already handled in the main pass, as a safety
    net in case grounding didn't fully prevent it. '''
    if not title:
        return False
    title_lower = title.lower()
    for anchor in anchors:
        anchor_title = (anchor.get("title") or "").lower()
        if anchor_title and difflib.SequenceMatcher(None, title_lower, anchor_title).ratio() >= threshold:
            return True
    return False