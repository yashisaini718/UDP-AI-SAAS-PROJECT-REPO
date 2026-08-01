from sqlalchemy.ext.asyncio import AsyncSession
from app.ai.ingestion import load_document, chunk_document
from app.ai.embeddings import EmbeddingPipeline
from app.ai.vectorstore import VectorStore
from app.ai.retriever import RetriverPipeline
from app.ai.rag import RagPipeline
from app.ai.llm import get_llm
from app.utils.ai import get_document_by_id, merge_and_reconcile, merge_fragments, is_known_title
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

MAX_GROUP_WORDS = 3000  # oversized-group cutoff before windowing within one opportunity

async def extract_opportunity(db: AsyncSession, document_id: str, rag_pipeline: RagPipeline):
    print("starting opportunity extraction")

    chunks = rag_pipeline.retriever.vector_store.get_document_chunks(document_id)
    if not chunks:
        return []

    outline = rag_pipeline.retriever.build_section_outline(chunks)
    print (outline)
    anchors = rag_pipeline.extract_outline(outline) if outline else []

    opportunities = []

    if anchors:
        grouped, leftover = rag_pipeline.retriever.group_chunks_by_anchor(chunks, anchors)

        # Primary path: one extraction per known opportunity
        for anchor_idx, anchor_chunks in grouped.items():
            if not anchor_chunks:
                continue

            anchor = anchors[anchor_idx]
            word_count = sum(len(text.split()) for text, _ in anchor_chunks)

            if word_count <= MAX_GROUP_WORDS:
                context = "\n\n".join(text for text, _ in anchor_chunks)
                result = rag_pipeline.extract_for_anchor(anchor, context)
                if result:
                    opportunities.append(result)
            else:
                # Case A: oversized group -- window within this one opportunity only
                windows = rag_pipeline.retriever.create_sliding_windows(anchor_chunks, window_size=3)
                fragments = [rag_pipeline.extract_for_anchor(anchor, w["context"]) for w in windows]
                merged = merge_fragments([f for f in fragments if f])
                if merged:
                    opportunities.append(merged)

        # Case B: catch-all for chunks the anchor pass missed entirely
        if leftover:
            windows = rag_pipeline.retriever.create_sliding_windows(leftover, window_size=3)
            leftover_extracted = []
            for window in windows:
                result = rag_pipeline.extract_window(
                    window["context"], known_anchors=anchors,
                    section_headings=window["metadata"]["section_headings"],
                )
                leftover_extracted.extend(result)

            leftover_extracted = [
                opp for opp in leftover_extracted if not is_known_title(opp.get("title"), anchors)
            ]

            if leftover_extracted:
                for cluster in rag_pipeline.retriever.cluster_opportunities(leftover_extracted):
                    reconciled = rag_pipeline.reconcile_cluster(cluster)
                    if reconciled:
                        opportunities.append(reconciled)
    else:
        # No anchors identified at all -- fall back to the pure windowed path
        windows = rag_pipeline.retriever.create_sliding_windows(chunks, window_size=3)
        extracted = []
        for window in windows:
            result = rag_pipeline.extract_window(
                window["context"], known_anchors=[], section_headings=window["metadata"]["section_headings"]
            )
            extracted.extend(result)
        opportunities = merge_and_reconcile(extracted, rag_pipeline.retriever, rag_pipeline)

    document = await get_document_by_id(db, document_id)
    created_count = 0
    for opportunity in opportunities:
        await save_opportunity(db=db, extracted_data=opportunity, document=document)
        created_count += 1
    await db.commit()
    return created_count

# async def extract_opportunity(db: AsyncSession, document_id: str):
#     vector_store=VectorStore()
#     embedding_manager=EmbeddingPipeline()

#     retriever=RetriverPipeline(
#         vector_store=vector_store, 
#         embedding_manager=embedding_manager
#     )
#     llm=get_llm()
#     rag_pipeline=RagPipeline(
#         retriever=retriever,
#         llm=llm
#     )

#     chunks = vector_store.get_document_chunks(document_id)

#     if not chunks:
#         return []

#     windows = retriever.create_sliding_windows(chunks,window_size=3)

#     print("Number of windows:", len(windows))

#     outline = retriever.build_section_outline(chunks)

#     anchors = rag_pipeline.extract_outline(outline) if outline else []

#     extracted = []

#     for window in windows:
#         result = rag_pipeline.extract_window(
#             window["context"], known_anchors=anchors, section_headings=window["metadata"]["section_headings"]
#         )   
#         # the extract_window function returns a list of parsed json
#         extracted.extend(result)

#     opportunities = merge_results(extracted)
#     # merge_result returns a list of opportunities 
#     # each opportunity a dictionary

#     document = await get_document_by_id(db, document_id)

#     created_count = 0

#     for opportunity in opportunities:
#         await save_opportunity(
#             db=db,
#             extracted_data=opportunity,
#             document=document,
#         )
#         created_count += 1

#     await db.commit()

#     return created_count

def querydb(rag, query: str):
    response = rag.query(query)
    return response