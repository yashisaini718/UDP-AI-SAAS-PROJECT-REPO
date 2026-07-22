import chromadb
import numpy as np
import uuid
import os
from typing import List, Dict, Any

class VectorStore():
    def __init__(self, collection_name: str="tickit", persist_directory="./chroma-db"):
        self.collection_name=collection_name
        self.persist_directory=persist_directory
        self.client=None
        self.collection=None
        self._initialize_store()

    def _initialize_store(self):
        try:
            os.makedirs(self.persist_directory,exist_ok=True)
            self.client=chromadb.PersistentClient(path=self.persist_directory)
            self.collection=self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description":"Document Embeddings for RAG"}
            )
            print(f"collection : {self.collection_name}")
        except Exception as e:
            print(f"Error initialising vector collection: {e}")
            raise

    def add_data(self, documents: List[Any], embeddings: np.ndarray):
        if len(documents) != len(embeddings) :
            raise ValueError("No. of documents is not equal to no. of embeddings")
        
        #process data
        ids=[]
        metadatas=[]
        document_text=[]
        embedding_list=[]

        for i, (doc, embedding) in enumerate(zip(documents,embeddings)):
            doc_id=f"doc_{uuid.uuid4().hex[:6]}"
            ids.append(doc_id)

            meta_data=dict(doc.metadata)
            meta_data["doc_index"]=i
            meta_data["content_length"]=len(doc.page_content)
            metadatas.append(meta_data)

            document_text.append(doc.page_content)
            embedding_list.append(embedding.tolist())

            try:
                self.collection.add(
                    ids=ids,
                    metadatas=metadatas,
                    documents=document_text,
                    embeddings=embedding_list
                )
                print(f"Successfully added {i+1} documents into chromadb")
            except Exception as e:
                print("Error adding data to collection: {e}")
                raise
