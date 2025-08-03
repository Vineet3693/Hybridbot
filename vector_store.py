
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Tuple
import pickle
import streamlit as st
from config import EMBEDDING_MODEL, SIMILARITY_THRESHOLD

class VectorStore:
    def __init__(self, model_name: str = EMBEDDING_MODEL):
        try:
            self.model = SentenceTransformer(model_name)
        except Exception as e:
            st.error(f"Error loading embedding model: {e}")
            # Fallback to a smaller model
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        self.index = None
        self.texts = []
        self.embeddings = None
        self.dimension = None
    
    def add_texts(self, texts: List[str]):
        """Add texts to vector store"""
        if not texts:
            return
        
        # Filter out empty texts
        valid_texts = [text for text in texts if text.strip()]
        if not valid_texts:
            return
        
        self.texts.extend(valid_texts)
        
        # Generate embeddings with progress bar
        progress_bar = st.progress(0)
        st.info(f"Generating embeddings for {len(valid_texts)} text chunks...")
        
        try:
            new_embeddings = self.model.encode(valid_texts, show_progress_bar=False)
            progress_bar.progress(0.5)
            
            if self.embeddings is None:
                self.embeddings = new_embeddings
                self.dimension = new_embeddings.shape[1]
            else:
                self.embeddings = np.vstack([self.embeddings, new_embeddings])
            
            # Create/update FAISS index
            if self.index is None:
                self.index = faiss.IndexFlatIP(self.dimension)  # Inner product similarity
            
            # Normalize embeddings for cosine similarity
            embeddings_normalized = self.embeddings.copy()
            faiss.normalize_L2(embeddings_normalized)
            
            # Clear and rebuild index
            self.index.reset()
            self.index.add(embeddings_normalized.astype('float32'))
            
            progress_bar.progress(1.0)
            progress_bar.empty()
            
        except Exception as e:
            st.error(f"Error generating embeddings: {e}")
            progress_bar.empty()
    
    def search(self, query: str, k: int = 5) -> List[Tuple[str, float]]:
        """Search for similar texts"""
        if self.index is None or len(self.texts) == 0:
            return []
        
        try:
            # Encode query
            query_embedding = self.model.encode([query])
            faiss.normalize_L2(query_embedding)
            
            # Search
            scores, indices = self.index.search(query_embedding.astype('float32'), min(k, len(self.texts)))
            
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.texts) and score > SIMILARITY_THRESHOLD:
                    results.append((self.texts[idx], float(score)))
            
            return results
        except Exception as e:
            st.error(f"Search error: {e}")
            return []
    
    def get_stats(self) -> dict:
        """Get statistics about the vector store"""
        return {
            "total_texts": len(self.texts),
            "has_index": self.index is not None,
            "dimension": self.dimension,
            "model_name": self.model._modules['0'].auto_model.name_or_path if hasattr(self.model, '_modules') else "unknown"
        }
