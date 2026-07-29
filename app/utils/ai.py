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


def merge_results(extracted_results):
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
