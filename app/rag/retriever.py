from vectorstore import  VectorStore
from embeddings import EmbeddingPipeline
from typing import List, Any, Dict

class RetriverPipeline():
    """ Retriever will generate query embeddings and search for top-k results in the vector db based on
    the similarity score """

    def __init__(self, vector_store: VectorStore, embedding_manager: EmbeddingPipeline):
        self.vector_store=vector_store
        self.embedding_manager=embedding_manager
    
   
    def retrieve(self, query: str, top_k: int=3, score_threshold: float=0.0)->List[Dict[str,Any]]:
        #retrieve() returns a list of dictionaries, 
        # where each dictionary represents one retrieved document (or document chunk) that matched the query.

        #generating query embedding
        query_embedding=self.embedding_manager.generate_embeddings([query])[0]
        # generate_embeddings take a list of string and gives a np array so the embedding of first query is at 
        # 0th index in the array

        try:
            results=self.vector_store.collection.query(
                query_embeddings=[query_embedding.tolist()], # query_embedding has a np array
                n_results=top_k  
            )
            retrieved_doc=[]
            if results['documents'] and results['documents'][0]:
                ids=results['ids'][0]
                documents=results['documents'][0]
                metadatas=results['metadatas'][0]
                distances=results['distances'][0]

                for i, (doc_id, doc, meta_data, distance) in enumerate(zip(ids, documents, metadatas, distances)):
                    similarity_score=1-distance
                    if similarity_score > score_threshold :
                        retrieved_doc.append({
                            'id': doc_id,
                            'content': doc,
                            'metadata': meta_data,
                            'distance': distance,
                            'similarity_score': similarity_score,
                            'rank': i+1
                        })
                print(f"Retrieved {len(retrieved_doc)} documents after filtering")
            else:
                print("No documents found")
            return retrieved_doc
        except Exception as e:
            print("Error: {e}")
            return []




