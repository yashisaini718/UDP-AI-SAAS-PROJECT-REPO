import chromadb
import numpy as np
import uuid
import os
from typing import List, Any

class VectorStore():
    
    def __init__(self, collection_name: str= "tickit", persist_directory= "./chroma-db"):
        self.collection_name = collection_name
        self.persist_directory = persist_directory

        self.client = None
        self.collection = None

        self._initialize_store()

    def _initialize_store(self):
        '''Incase the vector store is not available, creates one'''
        try:
            os.makedirs(self.persist_directory , exist_ok= True) # if exists do not create

            # attach the persistent client of chromadb
            self.client = chromadb.PersistentClient(path=self.persist_directory)

            # create collection in the vectordb
            self.collection = self.client.get_or_create_collection(
                name = self.collection_name,
                metadata = { "description" : "Document Embeddings for RAG" }
            )

            print(f"collection : {self.collection_name}")

        except Exception as e:
            print(f"Error initialising vector collection: {e}")

            raise

    def add_data(self, chunks: List[Any], embeddings: np.ndarray):
        ''' Adds the data to the chromadb
        Args:
        chunks: chunked documents
        embeddings: array of embeddings
        '''

        if len(chunks) != len(embeddings) :
            raise ValueError("No. of documents is not equal to no. of embeddings")
        
        #process data
        ids = []
        metadatas = []
        chunk_text = []
        embedding_list = []

        # store in vectorstore
        for i, (chunk, embedding) in enumerate( zip( chunks, embeddings)):
            chunk_id = f"chunk_{uuid.uuid4().hex[:6]}"
            ids.append(chunk_id)

            meta_data = dict(chunk.metadata)
            meta_data["chunk_id"] = chunk_id
            meta_data["chunk_index"] = i
            meta_data["content_length"] = len(chunk.page_content)
            metadatas.append(meta_data)

            chunk_text.append(chunk.page_content)
            embedding_list.append(embedding.tolist())

        try:
            self.collection.add(
                ids= ids,
                metadatas= metadatas,
                documents= chunk_text,
                embeddings= embedding_list
            )

            print(f"Successfully added {i+1} chunks into chromadb")

        except Exception as e:
            print("Error adding data to collection: {e}")

            raise

    def get_document_chunks(self, document_id: str):
        ''' Returns the chunks belonging to a particular document only
        Args:
        document_id: id of the document for which the chunks are needed
        '''
        try:
            results = self.collection.get(
                where= {"document_id": document_id},
                include=["documents", "metadatas"]
            )
            combined = list( zip( results["documents"], results["metadatas"]))

            combined.sort( key= lambda x: x[1]["chunk_index"])

            return combined

        except Exception as e:
            print(f"Error retrieving document chunks: {e}")

            raise
