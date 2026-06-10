import logging
import os
import time
from typing import Any, Dict, List, Optional

from google import genai
from google.genai import types

from tools.rag_core import RAGCore
from tools.rag_parser import RAGParser

logger = logging.getLogger(__name__)

DEFAULT_EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIMENSION = 768
DEFAULT_BATCH_SIZE = 50
MAX_RETRIES = 8
RETRY_DELAY_SECONDS = 32.0


class CorpusIngestor:
    """
    One-shot corpus ingestion pipeline: parses staged PDFs into metadata-rich
    chunks, embeds them with the Gemini embedding model, and persists the
    vectors into the local ChromaDB collection for RAG retrieval.
    """

    def __init__(
        self,
        parser: Optional[RAGParser] = None,
        core: Optional[RAGCore] = None,
        embedding_model: str = DEFAULT_EMBEDDING_MODEL,
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> None:
        self.parser = parser or RAGParser()
        self.core = core or RAGCore()
        self.embedding_model = embedding_model
        self.batch_size = batch_size
        self._cached_client: Optional[genai.Client] = None

    def _client(self) -> genai.Client:
        if self._cached_client is None:
            api_key = os.environ.get("GEMINI_API_KEY", "dummy")
            self._cached_client = genai.Client(api_key=api_key)
        return self._cached_client

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embeds a batch of texts at 768 dims, retrying on rate-limit (429) errors."""
        if not texts:
            return []
        for attempt in range(MAX_RETRIES):
            try:
                response = self._client().models.embed_content(
                    model=self.embedding_model,
                    contents=texts,
                    config=types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIMENSION),
                )
                return [list(emb.values) for emb in response.embeddings]
            except Exception as e:
                if "429" in str(e) and attempt < MAX_RETRIES - 1:
                    logger.warning(f"Embedding rate-limited; waiting {RETRY_DELAY_SECONDS}s (try {attempt + 1}).")
                    time.sleep(RETRY_DELAY_SECONDS)
                    continue
                raise
        return []

    def _build_id(self, chunk: Dict[str, Any], index: int) -> str:
        meta = chunk["metadata"]
        return f"{meta['source_filename']}_p{meta['page_number']}_{index}"

    def ingest(self) -> int:
        """
        Executes the full parse -> embed -> persist flow.
        Returns the total number of vectors inserted into the collection.
        """
        chunks = self.parser.process_directory()
        if not chunks:
            logger.warning("No chunks parsed from corpus; nothing to ingest.")
            return 0

        inserted = 0
        for start in range(0, len(chunks), self.batch_size):
            batch = chunks[start : start + self.batch_size]
            texts = [c["text"] for c in batch]
            embeddings = self.embed_batch(texts)
            if not embeddings:
                logger.error("Embedding batch returned empty; skipping batch.")
                continue
            ids = [self._build_id(c, start + i) for i, c in enumerate(batch)]
            metadatas = [c["metadata"] for c in batch]
            self.core.insert_vectors(ids, embeddings, texts, metadatas)
            inserted += len(ids)
            logger.info(f"Ingested batch {start}-{start + len(batch)} ({inserted} total).")

        logger.info(f"Corpus ingestion finished. Total vectors persisted: {inserted}.")
        return inserted
