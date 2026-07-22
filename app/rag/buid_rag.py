from rag.ingestion import IngestionPipeline
from rag.embeddings import EmbeddingPipeline
from rag.vectorstore import VectorStore
from rag.retriever import RetriverPipeline
from rag.pipeline import RagPipeline
from rag.llm import get_llm
from pathlib import Path
import os


def build_vector_store(data_directory: str="data"):
    print("Building VectorStore...")

    # initialising components
    embedding_manager=EmbeddingPipeline()
    vector_store=VectorStore()

    # load all documents
    documents=IngestionPipeline.load_all_documents(data_directory)
    if not documents:
        print ("No documents found.")
        return

    # split into chunks
    chunks=IngestionPipeline.chunk_documents(documents)

    # generate embeddings
    chunk_texts=[doc.page_content for doc in chunks]
    embeddings=embedding_manager.generate_embeddings(texts=chunk_texts)

    # store in chromadb
    vector_store.add_data(documents=chunks, embeddings=embeddings)

    print(f"\nVector store built successfully")

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


def chat():
    """
    Simple CLI interface.
    """

    rag = initialize_rag_pipeline()

    print("=" * 60)
    print("RAG Chat")
    print("Type 'exit' to quit.")
    print("=" * 60)

    while True:

        query = input("\nYou: ")

        if query.lower() == "exit":
            break

        response = rag.query(query)

        print("\nAssistant:")
        print(response)


if __name__ == "__main__":

    DATA_DIR = "./data"

    # Build vector database once
    if not Path("./chroma-db").exists():
        build_vector_store(DATA_DIR)

    # Start chatting
    chat()