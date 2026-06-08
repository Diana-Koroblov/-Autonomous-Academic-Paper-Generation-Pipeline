import logging
from pathlib import Path
from typing import Any, Dict, List

import fitz  # PyMuPDF

logger = logging.getLogger(__name__)

class RAGParser:
    """
    Parses PDF documents from a specified directory, applying a strict 1000/100
    sliding-window chunking strategy and injecting structural metadata for the RAG engine.
    """
    def __init__(
        self, raw_dir: str | Path = "data/raw", chunk_size: int = 1000, chunk_overlap: int = 100
    ):
        self.raw_dir = Path(raw_dir)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str) -> List[str]:
        """
        Splits raw text into constrained chunks with a continuous overlapping boundary.
        """
        if not text:
            return []

        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = start + self.chunk_size
            chunks.append(text[start:end])
            if end >= text_len:
                break
            start = end - self.chunk_overlap

        return chunks

    def parse_pdf(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Extracts text from a single PDF and injects exact metadata per chunk.
        """
        parsed_data = []
        try:
            doc = fitz.open(file_path)
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()

                if not text.strip():
                    continue

                chunks = self.chunk_text(text)
                for chunk in chunks:
                    parsed_data.append({
                        "text": chunk,
                        "metadata": {
                            "source_filename": file_path.name,
                            "page_number": page_num + 1,
                        }
                    })
            doc.close()
            logger.info(f"Parsed {file_path.name}: {len(parsed_data)} chunks extracted.")
        except Exception as e:
            logger.error(f"Error parsing {file_path.name}: {e}")

        return parsed_data

    def process_directory(self) -> List[Dict[str, Any]]:
        """
        Iterates through the raw data directory and processes all staged PDFs.
        """
        all_chunks = []
        if not self.raw_dir.exists():
            logger.warning(f"Ingestion directory {self.raw_dir} does not exist.")
            return all_chunks

        for file_path in self.raw_dir.glob("*.pdf"):
            file_chunks = self.parse_pdf(file_path)
            all_chunks.extend(file_chunks)

        logger.info(f"Corpus ingestion complete. Total chunks extracted: {len(all_chunks)}")
        return all_chunks
