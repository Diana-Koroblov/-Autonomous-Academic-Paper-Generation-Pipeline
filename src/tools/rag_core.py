import logging
import os
from pathlib import Path

import chromadb
from chromadb.config import Settings

logger = logging.getLogger(__name__)

class RAGCore:
    """
    Manages local-first vector database persistence for RAG operations.
    Configured specifically for the Google Gemini gemini-embedding-001 model (768 dimensions).
    """
    def __init__(self, persist_directory: str | Path = "data/processed/chroma_db"):
        self.persist_directory = str(persist_directory)
        os.makedirs(self.persist_directory, exist_ok=True)

        # Initialize persistent ChromaDB client
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection_name = "academic_corpus"
        self.embedding_dimension = 768  # Native dimension for gemini-embedding-001

        logger.info(f"Initialized ChromaDB persistent client at {self.persist_directory}")

    def get_collection(self):
        """
        Retrieves or creates the main vector collection.
        Enforces cosine similarity space matching the architectural constraints.
        """
        try:
            collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            return collection
        except Exception as e:
            logger.error(f"Failed to access ChromaDB collection: {e}")
            raise

    def insert_vectors(
        self, ids: list[str], embeddings: list[list[float]], documents: list[str], metadatas: list[dict]
    ):
        """
        Inserts vectors into the collection, ensuring dimensional compliance to prevent pipeline crashes.
        """
        if not embeddings:
            return

        # Enforce dimension check for gemini-embedding-001
        if len(embeddings[0]) != self.embedding_dimension:
            raise ValueError(
                f"Embedding dimension mismatch. Expected {self.embedding_dimension}, got {len(embeddings[0])}"
            )

        collection = self.get_collection()
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        logger.info(f"Successfully inserted {len(ids)} vectors into {self.collection_name}.")
