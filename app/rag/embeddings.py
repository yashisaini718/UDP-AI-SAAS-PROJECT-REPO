from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List

class EmbeddingPipeline():
    def __init__(self, model_name: str="all-MiniLM-L6-v2"):
        self.model_name=model_name
        self.model=None
        self._load_model()

    def _load_model(self):
        try:   
            print(f"Trying to load model: {self.model_name}")
            self.model=SentenceTransformer(self.model_name)
        except Exception as e:
            print(f"Error loading model: {e}")
            raise
    
    def generate_embeddings(self, texts: List[str])->np.ndarray:
        if not self.model:
            raise ValueError("Model not loaded")
        embeds=self.model.encode(texts,show_progress_bar=True)
        print(f"generated embeddings with shape: {embeds.shape}")
        return embeds


    
        