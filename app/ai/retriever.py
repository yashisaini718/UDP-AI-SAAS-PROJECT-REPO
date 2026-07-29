from app.ai.vectorstore import  VectorStore
from app.ai.embeddings import EmbeddingPipeline
from typing import List, Any, Dict

class RetriverPipeline():
    

    def __init__(self, vector_store: VectorStore, embedding_manager: EmbeddingPipeline):
        self.vector_store = vector_store
        self.embedding_manager = embedding_manager

   
    def retrieve(self, query: str, top_k: int= 3, score_threshold: float= 0.0)->List[ Dict[str, Any]]:
        ''' Generates query embeddings and search for top-k results in the vector db based on
        the similarity score'''

        # returns a list of dictionaries where each dictionary represents one retrieved document (document chunk) 

        #generating query embedding
        query_embedding = self.embedding_manager.generate_embeddings([query])[0]

        # generate_embeddings take a list of string and gives a np array so the embedding of first query is at 
        # 0th index in the array 

        try:
            results = self.vector_store.collection.query(
                query_embeddings = [query_embedding.tolist()], # query_embedding has a np array
                n_results = top_k  
            )

            retrieved_doc = []

            # chromadb allows multi-query search hence a list of lists is recieved in results
            if results['documents'] and results['documents'][0]:
                ids = results['ids'][0]
                documents = results['documents'][0]
                metadatas = results['metadatas'][0]
                distances = results['distances'][0]
                
               
                for i, (doc_id, doc, meta_data, distance) in enumerate( zip( ids, documents, metadatas, distances)):
                    
                    # no need to calculate cosine similarity, chromadb automatically implements it
                    similarity_score = 1-distance

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

            return retrieved_doc # list of semantically retrieved result
        
        except Exception as e:
            print("Error: {e}")

            return []
        
    
    def create_sliding_windows(self, chunks, window_size= 3):
        ''' Processes the chunks window by window 
        Args:
        chunks: a tuple of (chunk_text, metadata)'''

        windows = [] # a list of all window(dict) of the form {context, metadata}

        for i in range(len(chunks)-window_size+1):

            batch = chunks[i : i+window_size]

            context = "\n\n".join(chunk_text for chunk_text, _ in batch)  
            # since the metadata is not needed to be used use _ in it's place

            # batch is of the form [[chunk_text, metadata], [chun_text, metadata], [chunk_text, metadata]]
            # so, batch[0][1] means metadata of first chunk

            metadata = {
                "start_chunk": batch[0][1]["chunk_index"],
                "end_chunk": batch[-1][1]["chunk_index"],
                "document_id": batch[0][1]["document_id"]
            }

            # add to list
            windows.append(
                {
                    "context": context,
                    "metadata": metadata
                }
            )
        
        return windows
    