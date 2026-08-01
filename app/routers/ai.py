from fastapi import APIRouter, Depends, Request
from app.db.session import get_db
from app.services.rag_service import index_document, extract_opportunity, querydb
from app.core.security import get_current_user
from app.schemas.ai_query import QueryText
from sqlalchemy.ext.asyncio import AsyncSession


router=APIRouter(prefix="/ai", tags=['AI'])

''' Routes for indexing document(loading, 
chunking and generating embeddings), 
extracting opportunities and
providing user query'''

@router.post("/index-document")
async def indexdocument(
    document_id: str, 
    db: AsyncSession=Depends(get_db),
    current_user=Depends(get_current_user)
):

    total_chunks = await index_document(db=db,
        document_id=document_id
    )

    return {
        "message": "Document indexed successfully",
        "document_id": document_id,
        "chunks": total_chunks
    }


@router.post("/extract-opportunity")
async def extract(
    document_id: str, 
    request: Request,
    db: AsyncSession= Depends(get_db),
    current_user=Depends(get_current_user),
    
):
    rag_pipeline= request.app.state.rag
    created_count= await extract_opportunity(db=db, document_id=document_id, rag_pipeline=rag_pipeline)
    
    return {
        "message": "Opportunities extracted successfully",
        "document_id": document_id,
        "opportunities_created": created_count,
    }


@router.post("/query-vectordb")
async def query_vectordb(
    query: QueryText,
    request: Request,
    current_user=Depends(get_current_user)
):
    return querydb(rag= request.app.state.rag, query= query.query)
    