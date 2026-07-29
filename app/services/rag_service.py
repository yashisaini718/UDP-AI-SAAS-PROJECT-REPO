from sqlalchemy.ext.asyncio import AsyncSession
from app.ai.ingestion import load_document, chunk_document
from app.ai.embeddings import EmbeddingPipeline
from app.ai.vectorstore import VectorStore
from app.ai.retriever import RetriverPipeline
from app.ai.rag import RagPipeline
from app.ai.llm import get_llm
from app.utils.ai import get_document_by_id, merge_results
from app.services.opportunities import save_opportunity


async def index_document(db:AsyncSession, document_id: str):
    # get the document from postgres
    document=await get_document_by_id(db=db, document_id=document_id)
    file_path= document.file_path

    # load document
    pages= load_document(file_path=file_path, document_id=document_id)

    # create chunks
    chunks= chunk_document(pages=pages)

    print("Building VectorStore...")

    # initialising components
    embedding_manager=EmbeddingPipeline()
    vector_store=VectorStore()

    # generate embeddings
    chunk_texts=[doc.page_content for doc in chunks]
    embeddings=embedding_manager.generate_embeddings(texts=chunk_texts)

    # store in chromadb
    vector_store.add_data(chunks=chunks, embeddings=embeddings)

    print(f"\nVector store built successfully")

    return len(chunks)

async def extract_opportunity(db: AsyncSession, document_id: str):
    vector_store=VectorStore()
    embedding_manager=EmbeddingPipeline()

    retriever=RetriverPipeline(
        vector_store=vector_store, 
        embedding_manager=embedding_manager
    )
    llm=get_llm()
    rag_pipeline=RagPipeline(
        retriever=retriever,
        llm=llm
    )

    chunks = vector_store.get_document_chunks(document_id)

    if not chunks:
        return []

    windows = retriever.create_sliding_windows(chunks,window_size=3)

    print("Number of windows:", len(windows))

    extracted = []

    for window in windows:
        result = rag_pipeline.extract_window(
            window["context"]
        )   
        # the extract_window function returns a list of parsed json
        extracted.extend(result)

    opportunities = merge_results(extracted)
    # merge_result returns a list of opportunities 
    # each opportunity a dictionary

    document = await get_document_by_id(db, document_id)

    created_count = 0

    for opportunity in opportunities:
        await save_opportunity(
            db=db,
            extracted_data=opportunity,
            document=document,
        )
        created_count += 1

    await db.commit()

    return created_count

def querydb(rag, query: str):
    response = rag.query(query)
    return response