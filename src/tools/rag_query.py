import logging
from pathlib import Path
from typing import Any, Dict, List

from .rag_core import RAGCore

logger = logging.getLogger(__name__)

class RAGQuery:
    """
    Executes semantic search against the local vector database.
    Enforces a strict anti-hallucination similarity threshold (>= 0.72).
    """
    def __init__(
        self,
        core_instance: RAGCore | None = None,
        persist_directory: str | Path = "data/processed/chroma_db",
        similarity_threshold: float = 0.72,
        top_k: int = 5
    ):
        self.core = core_instance or RAGCore(persist_directory=persist_directory)
        self.similarity_threshold = similarity_threshold
        self.top_k = top_k

    def query(self, query_embeddings: List[List[float]]) -> List[Dict[str, Any]]:
        """
        Executes a query using pre-computed embeddings and applies the anti-hallucination gate.
        Returns a list of dictionaries containing text chunks and metadata.
        """
        if not query_embeddings:
            return []

        collection = self.core.get_collection()

        try:
            # Execute query. ChromaDB uses cosine distance (1 - cosine_similarity).
            # We will convert it back to similarity for the threshold check.
            results = collection.query(
                query_embeddings=query_embeddings,
                n_results=self.top_k,
                include=["documents", "metadatas", "distances"]
            )
        except Exception as e:
            logger.error(f"Error querying ChromaDB collection: {e}")
            return []

        filtered_results = []

        # Parse the nested results structure from ChromaDB
        if not results["documents"] or not results["documents"][0]:
            return filtered_results

        docs = results["documents"][0]
        metadatas = results["metadatas"][0] if results["metadatas"] else [{}] * len(docs)
        distances = results["distances"][0] if results["distances"] else [1.0] * len(docs)

        for doc, meta, distance in zip(docs, metadatas, distances):
            # Convert Cosine Distance to Cosine Similarity
            # ChromaDB cosine distance: d = 1.0 - cos_sim -> cos_sim = 1.0 - d
            similarity = 1.0 - distance

            if similarity >= self.similarity_threshold:
                filtered_results.append({
                    "text": doc,
                    "metadata": meta,
                    "similarity": similarity
                })
            else:
                logger.debug(f"Chunk rejected by anti-hallucination gate. Score: {similarity:.3f}")

        logger.info(
            f"Query returned {len(filtered_results)} chunks above the "
            f"{self.similarity_threshold} threshold."
        )
        return filtered_results
