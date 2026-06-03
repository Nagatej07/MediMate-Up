"""
vector_store.py - Pinecone vector database interface
"""

from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from src.config import Config
from src.utils import setup_logger
import time
import hashlib

logger = setup_logger(__name__)

class VectorStoreManager:
    """
    Manages interactions with Pinecone Vector DB.
    """
    def __init__(self):
        self.pc = Pinecone(api_key=Config.PINECONE_API_KEY)
        self.index_name = Config.PINECONE_INDEX_NAME
        
        # Local embedding model (no API key needed)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.embedding_dim = 384  # dimension of the model's output

        self._ensure_index()
        self.index = self.pc.Index(self.index_name)

    def _ensure_index(self):
        """Creates the index if it doesn't exist."""
        if self.index_name not in self.pc.list_indexes().names():
            logger.info(f"Creating Pinecone index: {self.index_name}")
            try:
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.embedding_dim,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region=Config.PINECONE_ENV
                    )
                )
                time.sleep(5) # Wait for initialization
            except Exception as e:
                logger.error(f"Failed to create index: {e}")

    def add_texts(self, texts, metadata_list, namespace=None):
        """Add texts to Pinecone."""
        vectors = []
        for i, text in enumerate(texts):
            text_hash = hashlib.md5(text.encode()).hexdigest()
            vector_id = f"{namespace}_{text_hash}" if namespace else text_hash
            embedding = self.embedding_model.encode(text).tolist()
            meta = metadata_list[i].copy() if i < len(metadata_list) else {}
            meta["text"] = text
            vectors.append((vector_id, embedding, meta))

        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i+batch_size]
            self.index.upsert(vectors=batch, namespace=namespace)
        
        logger.info(f"Stored {len(vectors)} texts in namespace '{namespace}'")
        return True

    def add_prescription(self, prescription_id, text_chunks, metadata):
        """Store prescription chunks."""
        vectors = []
        for i, chunk in enumerate(text_chunks):
            vector_id = f"{prescription_id}_{i}"
            embedding = self.embedding_model.encode(chunk).tolist()
            chunk_metadata = metadata.copy()
            chunk_metadata["text"] = chunk
            chunk_metadata["chunk_id"] = i
            chunk_metadata["prescription_id"] = prescription_id
            vectors.append((vector_id, embedding, chunk_metadata))

        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i+batch_size]
            self.index.upsert(vectors=batch)
        
        logger.info(f"Stored {len(vectors)} chunks for prescription {prescription_id}")
        return True

    def search(self, query, prescription_id=None, namespace="prescriptions", top_k=5):
        """
        Search for relevant chunks from Pinecone
        """
        # Convert query to embedding
        query_embedding = self.embedding_model.encode(query).tolist()

        # Optional filter
        filter_dict = None
        if prescription_id:
            filter_dict = {"prescription_id": prescription_id}

        # Query Pinecone
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            namespace=namespace,
            filter=filter_dict
        )

        return results.matches